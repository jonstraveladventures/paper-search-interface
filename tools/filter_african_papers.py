#!/usr/bin/env python3
"""
Script to filter the CSV file and create a new one containing only papers 
with African countries in the Author_Countries column.
"""

import pandas as pd
from pathlib import Path

# Define African countries (same as in extract_african_countries.py)
AFRICAN_COUNTRIES = {
    'Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cameroon', 
    'Cape Verde', 'Central African Republic', 'Chad', 'Comoros', 'Congo', 
    'Democratic Republic of the Congo', 'Djibouti', 'Egypt', 'Equatorial Guinea', 
    'Eritrea', 'Ethiopia', 'Gabon', 'Gambia', 'Ghana', 'Guinea', 'Guinea-Bissau', 
    'Ivory Coast', 'Kenya', 'Lesotho', 'Liberia', 'Libya', 'Madagascar', 'Malawi', 
    'Mali', 'Mauritania', 'Mauritius', 'Morocco', 'Mozambique', 'Namibia', 'Niger', 
    'Nigeria', 'Rwanda', 'São Tomé and Príncipe', 'Senegal', 'Seychelles', 
    'Sierra Leone', 'Somalia', 'South Africa', 'South Sudan', 'Sudan', 'Tanzania', 
    'Togo', 'Tunisia', 'Uganda', 'Zambia', 'Zimbabwe'
}

def has_african_country(countries_str):
    """Check if the countries string contains any African country"""
    if pd.isna(countries_str) or not countries_str.strip():
        return False
    
    # Split by semicolon and check each country
    countries = [c.strip() for c in countries_str.split(';') if c.strip()]
    for country in countries:
        if country in AFRICAN_COUNTRIES:
            return True
    return False

def main():
    """Main function to filter papers with African countries"""
    
    # Get the root directory (parent of tools folder)
    root_dir = Path(__file__).parent.parent
    
    # Define input and output CSV files
    input_csv = root_dir / 'all_papers.csv'
    output_csv = root_dir / 'african_papers.csv'
    
    if not input_csv.exists():
        print(f"Error: {input_csv} not found!")
        return
    
    print("Loading CSV file...")
    df = pd.read_csv(input_csv)
    
    print(f"Total papers in dataset: {len(df):,}")
    
    # Filter papers with African countries
    print("Filtering papers with African countries...")
    african_papers = df[df['Author_Countries'].apply(has_african_country)]
    
    # Filter out withdrawn, rejected, and desk rejected papers
    print("Removing withdrawn, rejected, and desk rejected papers...")
    excluded_statuses = ['Withdraw', 'Reject', 'Desk Reject']
    african_papers = african_papers[~african_papers['Status'].isin(excluded_statuses)]
    
    print(f"Papers after removing excluded statuses: {len(african_papers):,}")
    
    print(f"Papers with African countries: {len(african_papers):,}")
    print(f"Percentage of total papers: {len(african_papers)/len(df)*100:.2f}%")
    
    # Save filtered data
    african_papers.to_csv(output_csv, index=False)
    print(f"African papers saved to: {output_csv}")
    
    # Show statistics by African country
    print(f"\n=== PAPERS BY AFRICAN COUNTRY ===")
    african_country_counts = {}
    
    for _, row in african_papers.iterrows():
        countries_str = row['Author_Countries']
        if pd.notna(countries_str) and countries_str.strip():
            countries = [c.strip() for c in countries_str.split(';') if c.strip()]
            for country in countries:
                if country in AFRICAN_COUNTRIES:
                    african_country_counts[country] = african_country_counts.get(country, 0) + 1
    
    # Sort by count (descending)
    sorted_countries = sorted(african_country_counts.items(), key=lambda x: x[1], reverse=True)
    
    print("Papers by African country:")
    for country, count in sorted_countries:
        print(f"  {country}: {count:,} papers")
    
    # Show some sample papers
    print(f"\n=== SAMPLE AFRICAN PAPERS ===")
    print("First 5 papers with African countries:")
    for i, (_, row) in enumerate(african_papers.head(5).iterrows(), 1):
        print(f"{i}. Title: {row['Title'][:80]}...")
        print(f"   Conference: {row['Conference']} ({row['Year']})")
        print(f"   Countries: {row['Author_Countries']}")
        print(f"   Citations: {row['Citations']}")
        print()

if __name__ == "__main__":
    main() 