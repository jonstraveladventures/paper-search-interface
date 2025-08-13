#!/usr/bin/env python3
"""
Heuristically extract city (and country/state hints) from raw institution strings
and write a cache CSV without calling any external APIs.

Output: tools/institution_locations_heuristic.csv with columns:
  institution_raw, institution_core, city_guess, country_hint, source

Usage:
  python tools/extract_institution_cities.py --input all_papers.csv --out tools/institution_locations_heuristic.csv
"""
from __future__ import annotations

import argparse
import csv
import os
import re
from typing import Dict, Iterable, List, Optional

import pandas as pd
import unicodedata
import sys

# Reuse split/normalizer from enrichment script
sys.path.append('tools')
try:
    import enrich_institutions as ei
except Exception:  # fallback if import path issues
    ei = None


def _split_simple(value: str) -> List[str]:
    if not isinstance(value, str) or not value.strip():
        return []
    # Prefer the smarter splitter from enrich_institutions if available
    if ei and hasattr(ei, '_split_institutions'):
        try:
            return [p for p in ei._split_institutions(value) if p]
        except Exception:
            pass
    parts = re.split(r"[;|]\\s*", value)
    return [p.strip() for p in parts if p and p.strip()]


ORG_WORDS = set(w.lower() for w in [
    'university','institute','research','college','laboratory','laboratories','lab','school','faculty',
    'department','centre','center','cnrs','inrae','riken','aip','academy','national','inria','iit',
    'technion','politecnico','université','universidad','universita','universität','universite',
    'universidade','mit','ai','company','corp','inc','ltd','llc','hospital','clinic','medical','hospitality'
])

COUNTRY_WORDS = {
    # Common country tokens and abbreviations seen in affiliations
    'usa':'US','us':'US','united states':'US','u.s.':'US','u.s.a.':'US',
    'uk':'GB','united kingdom':'GB','england':'GB','scotland':'GB','wales':'GB','northern ireland':'GB',
    'germany':'DE','deutschland':'DE','france':'FR','china':'CN','people\'s republic of china':'CN',
    'pr china':'CN','hong kong':'HK','taiwan':'TW','japan':'JP','italy':'IT','spain':'ES','portugal':'PT',
    'canada':'CA','australia':'AU','switzerland':'CH','singapore':'SG','south korea':'KR','korea':'KR',
    'israel':'IL','india':'IN','brazil':'BR','mexico':'MX','netherlands':'NL','belgium':'BE','austria':'AT',
    'sweden':'SE','norway':'NO','denmark':'DK','finland':'FI','ireland':'IE','greece':'GR','poland':'PL',
}

CAP = re.compile(r'^[A-ZÀ-ÖØ-Ý][a-zA-ZÀ-ÖØ-öø-ÿ\-\']+$')

# City-states or city = country cases we should accept as cities too
CITY_STATES = { 'singapore', 'luxembourg', 'monaco', 'hong kong', 'macau', 'vatican city' }

# Capital cities by ISO code (subset sufficient for our data)
CAPITALS = {
    'US': 'Washington', 'GB': 'London', 'DE': 'Berlin', 'FR': 'Paris', 'IT': 'Rome', 'ES': 'Madrid',
    'PT': 'Lisbon', 'CA': 'Ottawa', 'AU': 'Canberra', 'CH': 'Bern', 'SG': 'Singapore', 'KR': 'Seoul',
    'IL': 'Jerusalem', 'IN': 'New Delhi', 'BR': 'Brasília', 'MX': 'Mexico City', 'NL': 'Amsterdam',
    'BE': 'Brussels', 'AT': 'Vienna', 'SE': 'Stockholm', 'NO': 'Oslo', 'DK': 'Copenhagen', 'FI': 'Helsinki',
    'IE': 'Dublin', 'GR': 'Athens', 'PL': 'Warsaw', 'CN': 'Beijing', 'TW': 'Taipei', 'JP': 'Tokyo'
}

# Hand-curated aliases for core institution names -> (city, country_hint)
ALIAS_CITY = {
    'MIT': ('Cambridge', 'US'),
    'Massachusetts Institute of Technology': ('Cambridge', 'US'),
    'Technion': ('Haifa', 'IL'),
    'EPFL': ('Lausanne', 'CH'),
    "Ecole Polytechnique Federale de Lausanne": ('Lausanne', 'CH'),
    "École Polytechnique Fédérale de Lausanne": ('Lausanne', 'CH'),
    'ETH Zurich': ('Zurich', 'CH'),
    'Carnegie Mellon University': ('Pittsburgh', 'US'),
    'Stanford University': ('Stanford', 'US'),
    'Columbia University': ('New York', 'US'),
    'Harvard': ('Cambridge', 'US'),
    'Harvard University': ('Cambridge', 'US'),
    'University of Pittsburgh': ('Pittsburgh', 'US'),
    'University of Wisconsin-Madison': ('Madison', 'US'),
    'The University of Texas at Austin': ('Austin', 'US'),
    'University of Texas at Austin': ('Austin', 'US'),
    'University of California San Diego': ('San Diego', 'US'),
    'UC San Diego': ('San Diego', 'US'),
    'University of California Irvine': ('Irvine', 'US'),
    'UC Irvine': ('Irvine', 'US'),
    'University of Waterloo': ('Waterloo', 'CA'),
    'California Institute of Technology': ('Pasadena', 'US'),
    'The Hebrew University of Jerusalem': ('Jerusalem', 'IL'),
    'University of Tokyo': ('Tokyo', 'JP'),
    'National University of Singapore': ('Singapore', 'SG'),
    'Texas A &M University': ('College Station', 'US'),
    'Texas A&M University': ('College Station', 'US'),
    'Max Planck Institute for Intelligent Systems': ('Tübingen', 'DE'),
    'RIKEN AIP': ('Tokyo', 'JP'),
    'Yahoo! Research': ('Sunnyvale', 'US'),
    'USC': ('Los Angeles', 'US'),
    'USC†': ('Los Angeles', 'US'),
    'University of Southern California': ('Los Angeles', 'US'),
    'Linköping University': ('Linköping', 'SE'),
    'Linkoping University': ('Linköping', 'SE'),
    'Link¨oping University': ('Linköping', 'SE'),
    'École normale supérieure': ('Paris', 'FR'),
    "Ecole normale superieure": ('Paris', 'FR'),
    "´Ecole normale supérieure": ('Paris', 'FR'),
    'Inria': ('Paris', 'FR'),
    'INRIA': ('Paris', 'FR'),
    'pitt.edu': ('Pittsburgh', 'US'),
    'tauex.tau.ac.il': ('Tel Aviv', 'IL'),
    'Tel Aviv University': ('Tel Aviv', 'IL'),
    'Korea University': ('Seoul', 'KR'),
    'CSIRO Data61': ('Sydney', 'AU'),
    'CSIRO’s Data61': ('Sydney', 'AU'),
    "CSIRO's Data61": ('Sydney', 'AU'),
    'iFLYTEK AI Research (Central China)': ('Hefei', 'CN'),
    'iFLYTEK': ('Hefei', 'CN'),
    'C3.AI': ('Redwood City', 'US'),
    'C3.ai': ('Redwood City', 'US'),
    'Deeproute.ai': ('Shenzhen', 'CN'),
    "University of L'Aquila": ("L'Aquila", 'IT'),
    'University of L’Aquila': ("L'Aquila", 'IT'),
    'A*STAR': ('Singapore', 'SG'),
    'Agency for Science, Technology and Research': ('Singapore', 'SG'),
    'Agency for Science Technology and Research': ('Singapore', 'SG'),
    'RIKEN': ('Tokyo', 'JP'),
    'eBay Inc.': ('San Jose', 'US'),
    'eBay': ('San Jose', 'US'),
    'Helm.ai': ('Palo Alto', 'US'),
    'National Taiwan University': ('Taipei', 'TW'),
    'University of Kassel': ('Kassel', 'DE'),
    "Queen's University": ('Kingston', 'CA'),
    'Queen’s University': ('Kingston', 'CA'),
    # New aliases from top-miss patterns
    'University of Washington': ('Seattle', 'US'),
    'CNRS': ('Paris', 'FR'),
    'University of T ¨ubingen': ('Tübingen', 'DE'),
    'University of Tübingen': ('Tübingen', 'DE'),
    'University of Tuebingen': ('Tübingen', 'DE'),
    'AITRICS': ('Seoul', 'KR'),
    'AITRICS2': ('Seoul', 'KR'),
    'University of Toronto': ('Toronto', 'CA'),
    'University of Toronto2': ('Toronto', 'CA'),
    "Chang’an University": ("Xi'an", 'CN'),
    "Chang'an University": ("Xi'an", 'CN'),
    'Grifﬁth University': ('Brisbane', 'AU'),
    'Griffith University': ('Brisbane', 'AU'),
    'University of St.Gallen': ('St. Gallen', 'CH'),
    'University of St. Gallen': ('St. Gallen', 'CH'),
    'University of Wrocław': ('Wrocław', 'PL'),
    'University of Wroclaw': ('Wrocław', 'PL'),
    'University of Warwick': ('Coventry', 'GB'),
    'PROWLER.io': ('Cambridge', 'GB'),
    'University of L ¨ubeck': ('Lübeck', 'DE'),
    'University of Luebeck': ('Lübeck', 'DE'),
    'Universität zu Lübeck': ('Lübeck', 'DE'),
    'InsightFace.ai': ('Shenzhen', 'CN'),
    # Batch 3 aliases
    'University of Sheffield': ('Sheffield', 'GB'),
    'University of Shefﬁeld': ('Sheffield', 'GB'),
    'Universite de Montreal': ('Montreal', 'CA'),
    'Université de Montréal': ('Montreal', 'CA'),
    'University of Copenhagen': ('Copenhagen', 'DK'),
    'USI': ('Lugano', 'CH'),
    'USI‡': ('Lugano', 'CH'),
    'Università della Svizzera italiana': ('Lugano', 'CH'),
    'Universita della Svizzera italiana': ('Lugano', 'CH'),
    'University of Amsterdam': ('Amsterdam', 'NL'),
    'Ant Group': ('Hangzhou', 'CN'),
    'antgroup': ('Hangzhou', 'CN'),
    'AntGroup': ('Hangzhou', 'CN'),
    'CAS': ('Beijing', 'CN'),
    'Chinese Academy of Sciences': ('Beijing', 'CN'),
    'University of Guelph': ('Guelph', 'CA'),
    'Renmin University of China': ('Beijing', 'CN'),
    'University of Edinburgh': ('Edinburgh', 'GB'),
    'University of Pennsylvania': ('Philadelphia', 'US'),
    'University of Michigan': ('Ann Arbor', 'US'),
    'University of Liverpool': ('Liverpool', 'GB'),
    'IIT Madras': ('Chennai', 'IN'),
    'Universit´e de Montr´eal': ('Montreal', 'CA'),
}


def norm_basic(s: str) -> str:
    s = ''.join(ch for ch in unicodedata.normalize('NFKD', s or '') if not unicodedata.combining(ch))
    s = s.lower()
    s = re.sub(r"[\u2013\u2014\u2019\u2018\u00B4\u02DC\u0308\u0301\u0300\u0302]", '', s)
    s = re.sub(r"[^a-z0-9+&@#\-\s]", '', s)
    s = re.sub(r"\s+", ' ', s).strip()
    return s

NOISE_NAMES = set(['inc', 'ltd', 'research', 'faculty'])

def is_noise_name(name: str) -> bool:
    n = norm_basic(name)
    if not n:
        return True
    if n in NOISE_NAMES:
        return True
    if re.fullmatch(r"\d+", n):
        return True
    if len(n) == 1:
        return True
    return False


def likely_city_segment(seg: str) -> bool:
    s = seg.strip()
    if not s or any(ch.isdigit() for ch in s):
        # allow tokens like postal code + city (e.g., '8092 Zürich'): strip leading digits and retry
        s = re.sub(r'^\s*\d+[\s,]*', '', s).strip()
        if not s:
            return False
    sl = s.lower()
    if sl in ORG_WORDS:
        return False
    if sl in COUNTRY_WORDS and sl not in CITY_STATES:
        return False
    # allow multi-word cities like New York, Los Angeles, Tel Aviv
    words = [w for w in re.split(r'\s+', s) if w]
    if len(words) <= 3 and all(CAP.match(w) for w in words):
        if not all(w.lower() in ORG_WORDS for w in words):
            return True
    return False


def extract_city(raw: str) -> str:
    # Split on commas and unicode dashes (–, —) as soft separators
    parts = [p.strip() for p in re.split(r'[ ,\u2013\u2014]+', raw) if p.strip()]
    # scan from end for a likely city token; join previous if it forms e.g. "New York"
    for i in range(len(parts) - 1, -1, -1):
        cand = parts[i]
        if likely_city_segment(cand):
            if i - 1 >= 0:
                prev = parts[i - 1]
                if likely_city_segment(prev) and len(prev.split()) <= 2:
                    return (prev + ' ' + cand).strip()
            return cand
    # Fallback: embedded city at end of organisation phrase
    s = raw.strip()
    if not s:
        return ''
    # Remove trailing country codes in parentheses or tokens like US/USA/UK
    s = re.sub(r"\((?:[^)]*)\)$", "", s).strip()
    s = re.sub(r"\b(US|USA|U\.S\.?A?\.?|UK|GB)\b$", "", s).strip()
    # Try patterns: 'University of <City>', 'Politecnico di <City>', 'at <City>' or final capitalised tokens (unicode friendly)
    m = re.search(r"(?:\b(?:di|de|of|at)\s+)?([A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ\-\']+(?:\s+[A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ\-\']+){0,2})\s*$", s)
    if m:
        cand = m.group(1).strip()
        # If hyphenated at the end, prefer last segment (e.g., Wisconsin-Madison -> Madison)
        if '-' in cand:
            cand = cand.split('-')[-1]
        words = cand.split()
        if 0 < len(words) <= 3 and all(CAP.match(w) for w in words):
            if not all(w.lower() in ORG_WORDS or w.lower() in COUNTRY_WORDS for w in words):
                return cand
    return ''


def apply_alias(core: str, raw: str, city: str, country_hint: str) -> tuple[str, str]:
    """Use alias mapping and simple cleanups to improve city/country.
    - Normalize 'California San Diego' -> 'San Diego', 'California Irvine' -> 'Irvine'
    - Map well-known cores to canonical city/country.
    """
    # Cleanup UC pattern leaking into city
    if city and city.startswith('California '):
        city = city.replace('California ', '').strip()
    # Normalize keys (strip diacritics/punctuation, lowercase) for robust alias matching
    def norm_key(s: str) -> str:
        s = ''.join(ch for ch in unicodedata.normalize('NFKD', s) if not unicodedata.combining(ch))
        s = s.lower()
        s = re.sub(r"[\u2013\u2014\u2019\u2018\u00B4\u02DC\u0308\u0301\u0300\u0302]", '', s)  # dashes/apostrophes/accents
        s = re.sub(r"[^a-z0-9+&@#\-\s]", '', s)  # drop most punctuation except basic tokens
        s = re.sub(r"\s+", ' ', s).strip()
        return s

    alias_norm = {norm_key(k): v for k, v in ALIAS_CITY.items()}

    # Strip trailing footnote-like tokens from core/raw (digits, daggers, single letters)
    def strip_footnotes(s: str) -> str:
        s = re.sub(r"[\s\u2020\u2021\u00A7\u00B6\u00B0\u00B9\u00B2\u00B3\*\^\+\-\d]+$", '', s).strip()
        return s
    core = strip_footnotes(core)
    raw = strip_footnotes(raw)

    # Direct alias by core name (exact or normalized)
    key = core.strip()
    if key in ALIAS_CITY:
        acity, cc = ALIAS_CITY[key]
        return acity, (country_hint or cc)
    nkey = norm_key(key)
    if nkey in alias_norm:
        acity, cc = alias_norm[nkey]
        return acity, (country_hint or cc)
    # Sometimes raw contains the alias string (check normalized containment)
    nraw = norm_key(raw)
    for nk, (acity, cc) in alias_norm.items():
        if nk in nraw:
            return acity, (country_hint or cc)
    # Country-only fallback: if core/raw equals a country, use its capital
    def country_code_for(text: str) -> str:
        t = norm_key(text)
        # exact match against COUNTRY_WORDS keys
        for k, code in COUNTRY_WORDS.items():
            if t == norm_key(k):
                return code
        return ''
    if not city:
        code = country_code_for(core) or country_code_for(raw)
        if code and code in CAPITALS:
            return CAPITALS[code], code
    return city, country_hint


def extract_country_hint(raw: str) -> str:
    text = raw.lower()
    # quick contains search for country words
    for k, code in COUNTRY_WORDS.items():
        if k in text:
            return code
    return ''


def main() -> None:
    parser = argparse.ArgumentParser(description='Heuristically extract city names from institutions (split + normalize)')
    parser.add_argument('--input', default='all_papers.csv', help='Path to CSV with Author_Institutions')
    parser.add_argument('--out', default='tools/institution_locations_heuristic.csv', help='Output CSV path')
    parser.add_argument('--log-every', type=int, default=10000, help='Progress print frequency')
    args = parser.parse_args()

    df = pd.read_csv(args.input, usecols=['Author_Institutions'], dtype=str, low_memory=False)
    # Build unique split set first
    split_uniques: List[str] = []
    seen_raw: set[str] = set()
    for val in df['Author_Institutions'].dropna().astype(str):
        for inst in _split_simple(val):
            if inst not in seen_raw:
                seen_raw.add(inst)
                split_uniques.append(inst)

    total = len(split_uniques)
    print(f'Total split entries: {total}')

    # Extract with progress
    rows: List[Dict[str, str]] = []
    for idx, inst in enumerate(split_uniques, start=1):
        core = inst
        if ei and hasattr(ei, 'normalize_institution'):
            try:
                core = ei.normalize_institution(inst) or inst
            except Exception:
                core = inst
        # Strip footnote markers and noise names early
        if is_noise_name(core):
            core = ''
        if is_noise_name(inst):
            inst = ''
        if not inst and not core:
            continue
        city = extract_city(inst)
        country_hint = extract_country_hint(inst)
        city, country_hint = apply_alias(core, inst, city, country_hint)
        rows.append({
            'institution_raw': inst,
            'institution_core': core,
            'city_guess': city,
            'country_hint': country_hint,
            'source': 'heuristic',
        })
        if args.log_every and idx % args.log_every == 0:
            remain = total - idx
            print(f'Processed {idx}/{total} (remaining {remain})')

    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
    with open(args.out, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['institution_raw','institution_core','city_guess','country_hint','source'])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    with_city = sum(1 for r in rows if r['city_guess'])
    print(f'Wrote {total} rows to {args.out}; with city guesses: {with_city} ({with_city*100.0/total:.1f}%)')


if __name__ == '__main__':
    main()


