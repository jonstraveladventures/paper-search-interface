#!/usr/bin/env python3
"""
Update the CSV file with paper counts from our AI research analysis.
Replace the last column (currently population numbers) with paper counts.
"""

import pandas as pd
import csv

def load_paper_counts():
    """Load the paper counts from our analysis"""
    try:
        # Load the CSV we generated earlier
        df = pd.read_csv('global_country_papers_2015_2024.csv')
        
        # Create a dictionary mapping country names to paper counts
        paper_counts = {}
        for _, row in df.iterrows():
            paper_counts[row['Country']] = row['Papers']
        
        print(f"📊 Loaded paper counts for {len(paper_counts)} countries")
        return paper_counts
        
    except FileNotFoundError:
        print("❌ Error: global_country_papers_2015_2024.csv not found. Please run extract_global_country_data.py first.")
        return None

def update_csv_with_papers(input_file, output_file, paper_counts):
    """Update the CSV file with paper counts"""
    
    # Read the original CSV
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = list(reader)
    
    # Get the header
    header = rows[0]
    print(f"📋 Original header: {header}")
    
    # Update the header to reflect paper counts
    header[3] = 'Number of papers'
    
    # Process each row
    updated_rows = [header]
    countries_not_found = []
    
    for i, row in enumerate(rows[1:], 1):
        country_name = row[0]
        
        # Handle some country name variations
        country_mapping = {
            'Burma': 'Myanmar',
            'Cabo Verde': 'Cape Verde',
            'Congo, Dem Rep of the': 'Democratic Republic of the Congo',
            'Congo, Rep of the': 'Congo',
            'Czechia': 'Czech Republic',
            'Korea, North': 'North Korea',
            'Korea, South': 'South Korea',
            'Macedonia': 'North Macedonia',
            'Micronesia, Fed States of': 'Micronesia',
            'Solomon Is': 'Solomon Islands',
            'St Kitts & Nevis': 'Saint Kitts and Nevis',
            'St Lucia': 'Saint Lucia',
            'St Vincent & the Grenadines': 'Saint Vincent and the Grenadines',
            'Swaziland': 'Eswatini',
            'Türkiye': 'Turkey',
            'United Arab Emirates': 'UAE',
            'Vatican City': 'Holy See',
            'Western Sahara': 'Sahrawi Arab Democratic Republic'
        }
        
        # Check if we need to map the country name
        if country_name in country_mapping:
            lookup_name = country_mapping[country_name]
        else:
            lookup_name = country_name
        
        # Get paper count
        if lookup_name in paper_counts:
            paper_count = paper_counts[lookup_name]
        else:
            paper_count = 0
            countries_not_found.append(country_name)
        
        # Update the row with paper count
        updated_row = row[:3] + [paper_count]
        updated_rows.append(updated_row)
    
    # Write the updated CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(updated_rows)
    
    print(f"✅ Updated CSV saved to: {output_file}")
    
    if countries_not_found:
        print(f"\n⚠️  Countries not found in paper data ({len(countries_not_found)}):")
        for country in countries_not_found[:10]:  # Show first 10
            print(f"   • {country}")
        if len(countries_not_found) > 10:
            print(f"   ... and {len(countries_not_found) - 10} more")
    
    return updated_rows

def main():
    """Main function"""
    print("🔄 Updating CSV with paper counts...")
    
    # Load paper counts
    paper_counts = load_paper_counts()
    if paper_counts is None:
        return
    
    # Update the CSV
    input_file = '/Users/jonathanshock/Downloads/data.csv'
    output_file = '/Users/jonathanshock/Downloads/data_with_papers.csv'
    
    updated_rows = update_csv_with_papers(input_file, output_file, paper_counts)
    
    # Show some statistics
    total_papers = sum(row[3] for row in updated_rows[1:])  # Skip header
    countries_with_papers = sum(1 for row in updated_rows[1:] if row[3] > 0)
    
    print(f"\n📊 Summary:")
    print(f"   • Total countries: {len(updated_rows) - 1}")
    print(f"   • Countries with papers: {countries_with_papers}")
    print(f"   • Total papers: {total_papers}")
    
    print(f"\n✅ Process complete! Updated file: {output_file}")

if __name__ == "__main__":
    main() 