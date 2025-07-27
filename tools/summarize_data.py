#!/usr/bin/env python3
"""
Script to provide summary statistics about the combined papers CSV file.
"""

import pandas as pd
import os
from pathlib import Path

def main():
    """Main function to analyze the CSV data"""
    
    # Get the root directory (parent of tools folder)
    root_dir = Path(__file__).parent.parent
    
    # Define input CSV file
    csv_file = root_dir / 'all_papers.csv'
    
    if not csv_file.exists():
        print(f"Error: {csv_file} not found!")
        return
    
    print("Loading CSV file...")
    df = pd.read_csv(csv_file)
    
    print(f"\n=== SUMMARY STATISTICS ===")
    print(f"Total papers: {len(df):,}")
    print(f"File size: {csv_file.stat().st_size / (1024*1024):.1f} MB")
    
    print(f"\n=== CONFERENCES ===")
    conference_counts = df['Conference'].value_counts()
    print(f"Number of unique conferences: {len(conference_counts)}")
    print("\nTop 10 conferences by paper count:")
    for conf, count in conference_counts.head(10).items():
        print(f"  {conf}: {count:,} papers")
    
    print(f"\n=== YEARS ===")
    year_counts = df['Year'].value_counts().sort_index()
    print(f"Year range: {year_counts.index.min()} - {year_counts.index.max()}")
    print(f"Number of years: {len(year_counts)}")
    print("\nPapers per year:")
    for year, count in year_counts.items():
        print(f"  {year}: {count:,} papers")
    
    print(f"\n=== CITATIONS ===")
    citations = df['Citations']
    print(f"Total citations: {citations.sum():,}")
    print(f"Average citations per paper: {citations.mean():.2f}")
    print(f"Median citations per paper: {citations.median():.2f}")
    print(f"Max citations: {citations.max():,}")
    print(f"Papers with 0 citations: {(citations == 0).sum():,} ({(citations == 0).mean()*100:.1f}%)")
    
    print(f"\n=== STATUS ===")
    status_counts = df['Status'].value_counts()
    print("Paper status distribution:")
    for status, count in status_counts.items():
        print(f"  {status}: {count:,} papers ({count/len(df)*100:.1f}%)")
    
    print(f"\n=== SUBFIELDS ===")
    subfield_counts = df['Subfield'].value_counts()
    print("Subfield distribution:")
    for subfield, count in subfield_counts.items():
        print(f"  {subfield}: {count:,} papers ({count/len(df)*100:.1f}%)")
    
    print(f"\n=== TRACKS ===")
    track_counts = df['Track'].value_counts()
    print("Track distribution:")
    for track, count in track_counts.head(10).items():
        print(f"  {track}: {count:,} papers")
    
    print(f"\n=== COUNTRIES ===")
    # Split countries and count
    all_countries = []
    for countries_str in df['Author_Countries'].dropna():
        if countries_str:
            countries = [c.strip() for c in countries_str.split(';') if c.strip()]
            all_countries.extend(countries)
    
    country_counts = pd.Series(all_countries).value_counts()
    print(f"Number of unique countries: {len(country_counts)}")
    print("\nTop 10 countries by paper count:")
    for country, count in country_counts.head(10).items():
        print(f"  {country}: {count:,} papers")

if __name__ == "__main__":
    main() 