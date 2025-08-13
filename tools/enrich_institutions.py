#!/usr/bin/env python3
"""
Enrich institution names with city and geocoordinates without touching existing app logic.

This script:
  - Scans all unique values in the `Author_Institutions` column of a CSV (default: all_papers.csv)
  - Looks up each institution in ROR first, then OpenAlex as a fallback
  - Writes/updates a cache CSV at tools/institution_locations.csv

Run:
  python tools/enrich_institutions.py --input all_papers.csv --out tools/institution_locations.csv --max 200

Safe by default:
  - Respects an existing cache; only queries missing institutions
  - Rate-limited requests
  - No changes to web_interface or data files used by the running app
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd
import requests


ROR_SEARCH_URL = "https://api.ror.org/organizations"
OPENALEX_SEARCH_URL = "https://api.openalex.org/institutions"


def _split_institutions(value: str) -> List[str]:
    if not isinstance(value, str) or not value.strip():
        return []
    # Split on common delimiters; keep commas because many institution names contain commas.
    # We assume semicolons or pipes separate multiple entries most reliably.
    parts = re.split(r"[;|]\s*", value)
    cleaned: List[str] = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # Further split on " and " when both sides look like organization names
        subparts = [p]
        if re.search(r"\band\b", p, re.I):
            tmp = [seg.strip() for seg in re.split(r"\s+and\s+", p, flags=re.I) if seg.strip()]
            if len(tmp) >= 2:
                # If both sides have org keywords, accept split
                if all(re.search(r"\b(University|Institute|Research|College|Laborator|Center|Centre|CNRS|INRAE|RIKEN|Google Research|Microsoft Research)\b", seg, re.I) for seg in tmp):
                    subparts = tmp
        for sp in subparts:
            # De-duplicate trivial noise
            if sp.lower() in {"unknown", "n/a", "na", "none"}:
                continue
            cleaned.append(sp)
    return cleaned


def read_unique_institutions(csv_path: str, limit: Optional[int] = None) -> List[str]:
    df = pd.read_csv(csv_path, dtype=str, low_memory=False)
    if 'Author_Institutions' not in df.columns:
        raise SystemExit("Input CSV does not have column 'Author_Institutions'")
    unique: set[str] = set()
    for val in df['Author_Institutions'].dropna():
        for inst in _split_institutions(val):
            unique.add(inst)
            if limit and len(unique) >= limit:
                break
        if limit and len(unique) >= limit:
            break
    return sorted(unique)


@dataclass
class EnrichedInstitution:
    institution: str
    matched_name: str = ""
    city: str = ""
    country_code: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source: str = ""
    ror_id: str = ""
    openalex_id: str = ""
    score: float = 0.0


def load_cache(path: str) -> Dict[str, EnrichedInstitution]:
    if not os.path.exists(path):
        return {}
    cache: Dict[str, EnrichedInstitution] = {}
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cache[row['institution']] = EnrichedInstitution(
                    institution=row.get('institution', ''),
                    matched_name=row.get('matched_name', ''),
                    city=row.get('city', ''),
                    country_code=row.get('country_code', ''),
                    latitude=float(row['latitude']) if row.get('latitude') else None,
                    longitude=float(row['longitude']) if row.get('longitude') else None,
                    source=row.get('source', ''),
                    ror_id=row.get('ror_id', ''),
                    openalex_id=row.get('openalex_id', ''),
                    score=float(row['score']) if row.get('score') else 0.0,
                )
            except Exception:
                # Be robust to any legacy rows
                continue
    return cache


def save_cache(path: str, rows: Iterable[EnrichedInstitution]) -> None:
    # Ensure deterministic order
    rows = list(rows)
    fieldnames = [
        'institution', 'matched_name', 'city', 'country_code', 'latitude', 'longitude',
        'source', 'ror_id', 'openalex_id', 'score', 'updated_at',
    ]
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        now = datetime.utcnow().isoformat(timespec='seconds') + 'Z'
        for r in rows:
            writer.writerow({
                'institution': r.institution,
                'matched_name': r.matched_name,
                'city': r.city,
                'country_code': r.country_code,
                'latitude': r.latitude if r.latitude is not None else '',
                'longitude': r.longitude if r.longitude is not None else '',
                'source': r.source,
                'ror_id': r.ror_id,
                'openalex_id': r.openalex_id,
                'score': r.score,
                'updated_at': now,
            })


def query_ror(name: str, timeout: float = 15.0) -> Optional[EnrichedInstitution]:
    try:
        resp = requests.get(ROR_SEARCH_URL, params={'query': name}, timeout=timeout)
        if resp.status_code != 200:
            return None
        data = resp.json()
        items = data.get('items') or []
        if not items:
            return None
        best = items[0]
        matched_name = best.get('name') or ''
        score = float(best.get('score') or 0.0)
        ror_id = best.get('id') or ''
        # Choose first address that has at least a country
        city = ''
        country_code = ''
        lat = None
        lng = None
        addresses = best.get('addresses') or []
        if addresses:
            addr = addresses[0]
            city = addr.get('city') or (addr.get('geonames_city') or {}).get('city', '')
            country_code = (addr.get('country_code') or '').upper()
            lat = addr.get('lat') or addr.get('latitude')
            lng = addr.get('lng') or addr.get('longitude')
        return EnrichedInstitution(
            institution=name,
            matched_name=matched_name,
            city=city or '',
            country_code=country_code or '',
            latitude=float(lat) if lat is not None else None,
            longitude=float(lng) if lng is not None else None,
            source='ror',
            ror_id=ror_id,
            openalex_id='',
            score=score,
        )
    except Exception:
        return None


def query_openalex(name: str, timeout: float = 15.0) -> Optional[EnrichedInstitution]:
    try:
        resp = requests.get(OPENALEX_SEARCH_URL, params={'search': name, 'per-page': 1}, timeout=timeout)
        if resp.status_code != 200:
            return None
        data = resp.json()
        results = data.get('results') or []
        if not results:
            return None
        best = results[0]
        matched_name = best.get('display_name') or ''
        openalex_id = best.get('id') or ''
        country_code = (best.get('country_code') or '').upper()
        # geo can be None; some have 'latitude'/'longitude'
        geo = best.get('geo') or {}
        lat = geo.get('latitude')
        lng = geo.get('longitude')
        city = geo.get('city') or (best.get('display_name_international') or {}).get('en', '')
        return EnrichedInstitution(
            institution=name,
            matched_name=matched_name,
            city=city or '',
            country_code=country_code or '',
            latitude=float(lat) if lat is not None else None,
            longitude=float(lng) if lng is not None else None,
            source='openalex',
            ror_id='',
            openalex_id=openalex_id,
            score=0.0,
        )
    except Exception:
        return None


def enrich_institution(name: str) -> Optional[EnrichedInstitution]:
    # Try ROR first
    r = query_ror(name)
    if r and (r.city or (r.latitude is not None and r.longitude is not None)):
        return r
    # Fallback to OpenAlex
    r = query_openalex(name)
    if r:
        return r
    # If still no match, try a normalized/core organization name
    core = normalize_institution(name)
    if core and core != name:
        r = query_ror(core)
        if r and (r.city or (r.latitude is not None and r.longitude is not None)):
            return r
        r = query_openalex(core)
        if r:
            return r
    return None


ORG_KEYWORDS_RE = re.compile(r"\b(University|Institute|Research|College|Laborator|Center|Centre|CNRS|INRAE|RIKEN|Google Research|Microsoft Research)\b", re.I)

LEADING_UNITS_RE = re.compile(r"^(Department|Dept\.?|School|Faculty) of [^,]+,\s*", re.I)

def normalize_institution(raw: str) -> str:
    """Heuristically strip department/lab segments and return a core org name.

    Examples:
      - "Department of Computer Science, Stanford University" -> "Stanford University"
      - "Microsoft Research, Cambridge" -> "Microsoft Research"
      - "The University of Tokyo and RIKEN AIP" -> "The University of Tokyo" (prefers University)
      - "Kyoto University and RIKEN AIP" -> "Kyoto University"
    """
    if not isinstance(raw, str):
        return ""
    s = raw.strip()
    if not s:
        return s
    # Remove leading unit phrases like "Department of X, "
    s = LEADING_UNITS_RE.sub("", s)
    # Split on common joiners and commas to isolate org candidates
    parts = re.split(r"\s*(?:,| and | & |\+|;|\|)\s*", s)
    candidates: List[str] = [p.strip() for p in parts if p.strip()]
    if not candidates:
        return s
    # Filter candidates to those containing organization keywords
    orgs = [p for p in candidates if ORG_KEYWORDS_RE.search(p)]
    # Prefer ones containing 'University', then 'Institute', then others
    def rank(p: str) -> Tuple[int, int]:
        prio = 3
        if re.search(r"\bUniversity\b", p, re.I):
            prio = 0
        elif re.search(r"\bInstitute\b", p, re.I):
            prio = 1
        elif re.search(r"\bResearch|Laborator|Center|Centre\b", p, re.I):
            prio = 2
        # tie-breaker: longer is often more specific
        return (prio, -len(p))
    if orgs:
        orgs.sort(key=rank)
        return orgs[0]
    # Fallback: return the last segment (often the core org)
    return candidates[-1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich institution names with city and geocoordinates")
    parser.add_argument('--input', default='all_papers.csv', help='Path to CSV with Author_Institutions column')
    parser.add_argument('--out', default='tools/institution_locations.csv', help='Path to cache CSV to create/update')
    parser.add_argument('--max', type=int, default=None, help='Optional cap on number of unique institutions to process')
    parser.add_argument('--sleep', type=float, default=0.25, help='Delay between API requests (seconds)')
    parser.add_argument('--refresh-missing', action='store_true', help='Retry institutions present in cache without a source')
    args = parser.parse_args()

    cache = load_cache(args.out)
    print(f"Loaded {len(cache)} cached institutions")
    unique = read_unique_institutions(args.input, limit=args.max)
    print(f"Found {len(unique)} unique institutions to consider")

    updated: Dict[str, EnrichedInstitution] = dict(cache)
    to_process = [u for u in unique if (u not in cache) or (args.refresh_missing and not (cache[u].source or '').strip())]
    print(f"Will query {len(to_process)} institutions ({'including' if args.refresh_missing else 'only'} uncached/missing)")

    for idx, name in enumerate(to_process, start=1):
        enr = enrich_institution(name)
        if enr:
            updated[name] = enr
            print(f"[{idx}/{len(to_process)}] OK: {name} -> {enr.city or '?'} {enr.country_code}")
        else:
            # Keep an empty placeholder so we don't retry immediately next run
            updated[name] = EnrichedInstitution(institution=name, source='')
            print(f"[{idx}/{len(to_process)}] MISS: {name}")
        time.sleep(max(0.0, args.sleep))

    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
    save_cache(args.out, updated.values())
    print(f"Saved {len(updated)} rows to {args.out}")


if __name__ == '__main__':
    main()


