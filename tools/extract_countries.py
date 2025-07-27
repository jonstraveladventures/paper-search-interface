#!/usr/bin/env python3
"""
Script to extract all unique countries from the Author_Countries column in the CSV file.
"""

import pandas as pd
from pathlib import Path

def main():
    """Main function to extract and list all unique countries"""
    
    # Get the root directory (parent of tools folder)
    root_dir = Path(__file__).parent.parent
    
    # Define input CSV file
    csv_file = root_dir / 'all_papers.csv'
    
    if not csv_file.exists():
        print(f"Error: {csv_file} not found!")
        return
    
    print("Loading CSV file...")
    df = pd.read_csv(csv_file)
    
    print(f"Total papers: {len(df):,}")
    
    # Extract all countries from the Author_Countries column
    all_countries = []
    
    for countries_str in df['Author_Countries'].dropna():
        if countries_str and countries_str.strip():
            # Split by semicolon and clean each country
            countries = [c.strip() for c in countries_str.split(';') if c.strip()]
            all_countries.extend(countries)
    
    # Get unique countries and sort them
    unique_countries = sorted(set(all_countries))
    
    print(f"\n=== UNIQUE COUNTRIES ===")
    print(f"Total unique countries: {len(unique_countries)}")
    print("\nAll countries (alphabetically sorted):")
    
    for i, country in enumerate(unique_countries, 1):
        print(f"{i:3d}. {country}")
    
    # Also show country counts
    print(f"\n=== COUNTRY COUNTS ===")
    country_counts = pd.Series(all_countries).value_counts().sort_values(ascending=False)
    
    print("Countries by paper count:")
    for country, count in country_counts.items():
        print(f"  {country}: {count:,} papers")
    
    # Save to file
    output_file = root_dir / 'unique_countries.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=== UNIQUE COUNTRIES FROM AUTHOR_COUNTRIES COLUMN ===\n")
        f.write(f"Total unique countries: {len(unique_countries)}\n\n")
        f.write("All countries (alphabetically sorted):\n")
        for i, country in enumerate(unique_countries, 1):
            f.write(f"{i:3d}. {country}\n")
        
        f.write(f"\n=== COUNTRY COUNTS ===\n")
        f.write("Countries by paper count:\n")
        for country, count in country_counts.items():
            f.write(f"  {country}: {count:,} papers\n")
    
    print(f"\nCountry list saved to: {output_file}")

if __name__ == "__main__":
    main() 