#!/usr/bin/env python3
"""
Best-effort scraping of company domains (e.g., *.ai, *.com) to guess city locations.
Targets the residual missing entries in tools/institution_locations_merged_clean.csv
and writes tools/institution_locations_web.csv (institution, city, country_hint, source).

Approach:
- Only attempt names that look like domains (contain a TLD like .ai, .com, .io, .pl, .cn).
- Try https://{domain} and https://www.{domain}
- Parse for schema.org Organization addressLocality/addressCountry if present
- Heuristics: search for keywords (headquarters, address, contact) lines and extract a capitalized city
"""
from __future__ import annotations

import csv
import json
import re
import sys
from typing import Dict, Optional

import requests


TLD_RE = re.compile(r"\.(ai|com|io|pl|cn|co|org|net|de|fr|uk|ca|au|sg|jp)\b", re.I)


def looks_like_domain(name: str) -> Optional[str]:
    name = (name or '').strip()
    if TLD_RE.search(name):
        # try to extract domain token (e.g., 'Arya.ai' or 'arya.ai')
        m = re.search(r"([a-z0-9\-]+\.[a-z]{2,})(?:\b|$)", name, re.I)
        if m:
            return m.group(1).lower()
    return None


def fetch_url(url: str) -> Optional[str]:
    try:
        r = requests.get(url, timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code < 400 and r.text:
            return r.text
    except Exception:
        return None
    return None


def parse_schema_org(html: str) -> Dict[str, str]:
    # Find JSON-LD blocks
    out: Dict[str, str] = {}
    for m in re.finditer(r"<script[^>]*type=\"application/ld\+json\"[^>]*>(.*?)</script>", html, re.I | re.S):
        block = m.group(1).strip()
        try:
            data = json.loads(block)
        except Exception:
            continue
        nodes = data if isinstance(data, list) else [data]
        for node in nodes:
            if not isinstance(node, dict):
                continue
            addr = node.get('address') or {}
            if isinstance(addr, dict):
                city = (addr.get('addressLocality') or '').strip()
                country = (addr.get('addressCountry') or '').strip()
                if city:
                    out['city'] = city
                if country:
                    out['country'] = country
                if out:
                    return out
    return out


CITY_LINE_RE = re.compile(r"(headquarters|address|contact|located in|based in)[:\s\-]*([A-Z][A-Za-z\-']+(?:\s+[A-Z][A-Za-z\-']+){0,2})", re.I)


def parse_city_heuristic(text: str) -> Optional[str]:
    # Minify whitespace
    t = re.sub(r"\s+", ' ', text)
    for m in CITY_LINE_RE.finditer(t):
        city = m.group(2).strip()
        if city:
            return city
    return None


def try_scrape(domain: str) -> Dict[str, str]:
    urls = [f'https://{domain}', f'https://www.{domain}']
    html = None
    for u in urls:
        html = fetch_url(u)
        if html:
            break
    if not html:
        return {}
    data = parse_schema_org(html)
    if 'city' in data:
        return {'city': data.get('city',''), 'country_hint': data.get('country',''), 'source': f'web:{domain}'}
    # Heuristic
    city = parse_city_heuristic(html)
    if city:
        return {'city': city, 'country_hint': '', 'source': f'web:{domain}'}
    return {}


def main() -> None:
    merged = 'tools/institution_locations_merged_clean.csv'
    out = 'tools/institution_locations_web.csv'
    missing = []
    with open(merged, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if not r.get('city'):
                name = (r.get('institution_core') or r.get('institution_raw') or '').strip()
                if name:
                    missing.append(name)
    unique = []
    seen = set()
    for m in missing:
        if m not in seen:
            seen.add(m); unique.append(m)
    targets = []
    for u in unique:
        d = looks_like_domain(u)
        if d:
            targets.append((u, d))
    results = []
    for orig, domain in targets:
        info = try_scrape(domain)
        if info:
            results.append({'institution': orig, 'city': info['city'], 'country_hint': info.get('country_hint',''), 'source': info['source']})
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['institution','city','country_hint','source'])
        w.writeheader(); w.writerows(results)
    print('scraped', len(results), 'of', len(targets), 'domain-like entries')


if __name__ == '__main__':
    main()


