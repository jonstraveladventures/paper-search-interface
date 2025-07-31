#!/usr/bin/env python3
"""
Convert Country Separators Script

This script converts the Author_Countries column in all_papers.csv from 
semicolon-separated to comma-separated format.

USAGE:
    python tools/convert_country_separators.py

AUTHOR: Jonathan Shock
DATE: 2025
"""

import pandas as pd
import os
from pathlib import Path

def convert_country_separators():
    """
    Convert semicolon-separated countries to comma-separated countries
    """
    print("🔄 Converting country separators from semicolons to commas...")
    
    # Load the data
    try:
        df = pd.read_csv('all_papers.csv')
        print(f"📊 Loaded {len(df)} papers")
    except FileNotFoundError:
        print("❌ Error: all_papers.csv not found in current directory")
        return False
    
    # Check if Author_Countries column exists
    if 'Author_Countries' not in df.columns:
        print("❌ Error: Author_Countries column not found")
        return False
    
    # Count papers with multiple countries (semicolon-separated)
    multi_country_papers = 0
    total_papers = len(df)
    
    for idx, countries_str in enumerate(df['Author_Countries']):
        if pd.notna(countries_str) and ';' in str(countries_str):
            multi_country_papers += 1
    
    print(f"📈 Papers with multiple countries (semicolon-separated): {multi_country_papers}")
    print(f"📈 Total papers: {total_papers}")
    
    # Convert semicolons to commas
    df['Author_Countries'] = df['Author_Countries'].astype(str).str.replace(';', ',')
    
    # Create backup
    backup_file = 'all_papers_backup.csv'
    print(f"💾 Creating backup: {backup_file}")
    df.to_csv(backup_file, index=False)
    
    # Save converted data
    print(f"💾 Saving converted data to all_papers.csv")
    df.to_csv('all_papers.csv', index=False)
    
    # Verify conversion
    multi_country_papers_after = 0
    for countries_str in df['Author_Countries']:
        if pd.notna(countries_str) and ',' in str(countries_str) and ';' not in str(countries_str):
            multi_country_papers_after += 1
    
    print(f"✅ Conversion complete!")
    print(f"📊 Papers with multiple countries (comma-separated): {multi_country_papers_after}")
    
    # Show sample of converted data
    print(f"\n📋 Sample of converted data:")
    sample_countries = df['Author_Countries'].dropna().head(5).tolist()
    for i, countries in enumerate(sample_countries, 1):
        print(f"   {i}. {countries}")
    
    return True

def main():
    """
    Main function
    """
    print("🔄 Country Separator Conversion Tool")
    print("=" * 40)
    
    # Check if all_papers.csv exists
    if not os.path.exists('all_papers.csv'):
        print("❌ Error: all_papers.csv not found in current directory")
        print("   Please run this script from the directory containing all_papers.csv")
        return
    
    # Perform conversion
    success = convert_country_separators()
    
    if success:
        print(f"\n✅ Successfully converted country separators!")
        print(f"📁 Backup saved as: all_papers_backup.csv")
        print(f"🔄 You can now restart your web interface to use comma-separated countries")
    else:
        print(f"\n❌ Conversion failed!")

if __name__ == "__main__":
    main() 