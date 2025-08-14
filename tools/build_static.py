#!/usr/bin/env python3
"""
Build script to generate static assets for GitHub Pages.

This script reads `all_papers.csv` and writes a minimized `docs/data.json`
with only the fields the web UI needs. The static site in `docs/` then loads
this JSON and performs all filtering client-side.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = PROJECT_ROOT / "all_papers.csv"
DOCS_DIR = PROJECT_ROOT / "docs"
JSON_OUT = DOCS_DIR / "data.json"


def load_dataframe(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing CSV file: {csv_path}")

    df = pd.read_csv(csv_path)

    # Ensure required columns exist; create if missing
    required_columns = [
        "Title",
        "Authors",
        "Conference",
        "Year",
        "Subfield",
        "Author_Institutions",
        "Author_Countries",
        "Status",
        "Track",
        "Citations",
    ]
    for col in required_columns:
        if col not in df.columns:
            df[col] = None

    # Keep only the necessary columns in a consistent order
    df = df[[
        "Title",
        "Authors",
        "Conference",
        "Year",
        "Subfield",
        "Author_Institutions",
        "Author_Countries",
        "Status",
        "Track",
        "Citations",
    ]].copy()

    # Normalize basic types
    # Year and Citations to integers where possible
    def safe_int(value):
        try:
            return int(value)
        except Exception:
            return None

    df["Year"] = df["Year"].apply(safe_int)
    df["Citations"] = df["Citations"].apply(safe_int)

    # Fill NaNs with empty strings for text fields
    for col in ["Title", "Authors", "Conference", "Subfield", "Author_Institutions", "Author_Countries", "Status", "Track"]:
        df[col] = df[col].fillna("")

    return df


def write_json(df: pd.DataFrame, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to list of dicts
    records = df.to_dict(orient="records")

    # Write pretty-printed JSON for readability; GitHub Pages will gzip
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, separators=(",", ":"))


def main() -> None:
    df = load_dataframe(CSV_PATH)
    write_json(df, JSON_OUT)
    print(f"Wrote {len(df)} records to {JSON_OUT}")


if __name__ == "__main__":
    main()


