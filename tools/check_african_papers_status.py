#!/usr/bin/env python3
"""
African Papers Status Analysis Tool

This script analyzes whether the African papers analysis included rejected papers and shows the difference
between including all papers vs. only accepted papers. It provides a comparison of paper counts for
top African countries when rejected papers are included versus when only accepted papers are considered.

USAGE:
    python tools/check_african_papers_status.py

OUTPUT:
    - Comparison of paper counts between original analysis (including rejected) and accepted-only analysis
    - Breakdown of rejected papers by status
    - Summary statistics for both approaches

AUTHOR: Jonathan Shock
DATE: 2025
"""

import pandas as pd
from collections import Counter

# Define African countries
AFRICAN_COUNTRIES = {
    'Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cameroon', 
    'Cape Verde', 'Central African Republic', 'Chad', 'Comoros', 'Congo', 
    'Democratic Republic of the Congo', 'Djibouti', 'Egypt', 'Equatorial Guinea', 
    'Eritrea', 'Ethiopia', 'Gabon', 'Gambia', 'Ghana', 'Guinea', 'Guinea-Bissau', 
    'Ivory Coast', 'Kenya', 'Lesotho', 'Liberia', 'Libya', 'Madagascar', 'Malawi', 
    'Mali', 'Mauritania', 'Mauritius', 'Morocco', 'Mozambique', 'Namibia', 'Niger', 
    'Nigeria', 'Rwanda', 'Sao Tome and Principe', 'Senegal', 'Seychelles', 
    'Sierra Leone', 'Somalia', 'South Africa', 'South Sudan', 'Sudan', 'Swaziland', 
    'Tanzania', 'Togo', 'Tunisia', 'Uganda', 'Zambia', 'Zimbabwe'
}

def load_data():
    """
    Load the combined papers data from all_papers.csv
    
    Returns:
        pandas.DataFrame: The loaded data or None if file not found
    """
    try:
        df = pd.read_csv('all_papers.csv')
        print(f"📊 Loaded {len(df)} total papers")
        return df
    except FileNotFoundError:
        print("❌ Error: all_papers.csv not found. Please run combine_papers.py first.")
        return None

def analyze_african_papers_original(df):
    """
    Analyze African papers as done in the original analysis (including rejected papers)
    
    Args:
        df (pandas.DataFrame): The complete papers dataset
        
    Returns:
        pandas.DataFrame: Filtered African papers including rejected ones
    """
    
    print("🌍 ORIGINAL AFRICAN PAPERS ANALYSIS (INCLUDING REJECTED PAPERS):")
    print("=" * 70)
    
    # Filter for African papers only (as done in original analysis)
    african_papers = []
    for _, row in df.iterrows():
        countries_str = str(row['Author_Countries']) if pd.notna(row['Author_Countries']) else ''
        countries = [c.strip() for c in countries_str.split(';') if c.strip()]
        
        # Check if any author is from an African country
        if any(country in AFRICAN_COUNTRIES for country in countries):
            african_papers.append(row)
    
    african_df = pd.DataFrame(african_papers)
    
    # Filter to 2024 and earlier (as done in original analysis)
    african_df = african_df[african_df['Year'] <= 2024]
    
    print(f"📊 Total African papers: {len(african_df)}")
    
    # Check status breakdown
    if 'Status' in african_df.columns:
        status_counts = african_df['Status'].value_counts()
        
        print(f"\n📈 Status breakdown:")
        print("-" * 40)
        for status, count in status_counts.items():
            percentage = (count / len(african_df)) * 100
            print(f"{status}: {count} papers ({percentage:.1f}%)")
        
        # Check for rejected papers
        rejected_keywords = ['reject', 'rejected', 'desk reject', 'withdraw', 'withdrawn']
        rejected_papers = []
        
        for status in status_counts.index:
            if status and any(keyword in str(status).lower() for keyword in rejected_keywords):
                rejected_papers.append(status)
        
        if rejected_papers:
            print(f"\n❌ REJECTED PAPERS FOUND:")
            print("-" * 40)
            total_rejected = 0
            for status in rejected_papers:
                count = status_counts[status]
                total_rejected += count
                print(f"• {status}: {count} papers")
            print(f"Total rejected: {total_rejected} papers")
        else:
            print(f"\n✅ No rejected papers found")
    
    return african_df

def analyze_african_papers_accepted_only(df):
    """
    Analyze African papers with only accepted papers (excluding rejected/withdrawn)
    
    Args:
        df (pandas.DataFrame): The complete papers dataset
        
    Returns:
        pandas.DataFrame: Filtered African papers (accepted only)
    """
    
    print(f"\n🌍 AFRICAN PAPERS ANALYSIS (ACCEPTED PAPERS ONLY):")
    print("=" * 70)
    
    # Define rejected/withdrawn statuses to exclude
    rejected_statuses = [
        'Reject', 'Withdraw', 'Desk Reject', 
        'NeurIPS 2023 Conference Withdrawn Submission'
    ]
    
    # Filter out rejected papers first
    accepted_df = df[~df['Status'].isin(rejected_statuses)]
    
    # Filter for African papers only
    african_papers = []
    for _, row in accepted_df.iterrows():
        countries_str = str(row['Author_Countries']) if pd.notna(row['Author_Countries']) else ''
        countries = [c.strip() for c in countries_str.split(';') if c.strip()]
        
        # Check if any author is from an African country
        if any(country in AFRICAN_COUNTRIES for country in countries):
            african_papers.append(row)
    
    african_df = pd.DataFrame(african_papers)
    
    # Filter to 2024 and earlier
    african_df = african_df[african_df['Year'] <= 2024]
    
    print(f"📊 Total African papers (accepted only): {len(african_df)}")
    
    # Check status breakdown
    if 'Status' in african_df.columns:
        status_counts = african_df['Status'].value_counts()
        
        print(f"\n📈 Status breakdown (accepted papers):")
        print("-" * 40)
        for status, count in status_counts.items():
            percentage = (count / len(african_df)) * 100
            print(f"{status}: {count} papers ({percentage:.1f}%)")
    
    return african_df

def compare_country_counts(original_df, accepted_df):
    """
    Compare country counts between original and accepted-only analysis
    
    Args:
        original_df (pandas.DataFrame): African papers including rejected
        accepted_df (pandas.DataFrame): African papers (accepted only)
    """
    
    print(f"\n🌍 COUNTRY COMPARISON:")
    print("=" * 70)
    
    # Get country counts for original analysis
    original_countries = []
    for countries_str in original_df['Author_Countries'].dropna():
        countries = [c.strip() for c in str(countries_str).split(';') if c.strip()]
        original_countries.extend(countries)
    
    original_counts = Counter(original_countries)
    
    # Get country counts for accepted-only analysis
    accepted_countries = []
    for countries_str in accepted_df['Author_Countries'].dropna():
        countries = [c.strip() for c in str(countries_str).split(';') if c.strip()]
        accepted_countries.extend(countries)
    
    accepted_counts = Counter(accepted_countries)
    
    print(f"📊 Top 10 African countries comparison:")
    print("-" * 60)
    print(f"{'Country':<20} {'Original':<10} {'Accepted':<10} {'Difference':<10}")
    print("-" * 60)
    
    # Get top countries from original analysis
    top_countries = original_counts.most_common(10)
    
    for country, original_count in top_countries:
        accepted_count = accepted_counts.get(country, 0)
        difference = original_count - accepted_count
        print(f"{country:<20} {original_count:<10} {accepted_count:<10} {difference:<10}")

def main():
    """
    Main function to analyze African papers status and compare approaches
    """
    print("🔍 Checking African papers analysis for rejected papers...")
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Analyze original African papers (including rejected)
    original_african_df = analyze_african_papers_original(df)
    
    # Analyze African papers (accepted only)
    accepted_african_df = analyze_african_papers_accepted_only(df)
    
    # Compare country counts
    compare_country_counts(original_african_df, accepted_african_df)
    
    print(f"\n✅ Analysis complete!")

if __name__ == "__main__":
    main() 