#!/usr/bin/env python3
"""
Sudan and African Countries Data Analysis Tool

This script specifically checks for papers from Sudan and other African countries that might not be
included in the top 15 countries analysis. It helps identify countries that might be missing from
temporal analysis and provides a comprehensive view of all African countries with papers.

USAGE:
    python tools/check_sudan_data.py

OUTPUT:
    - List of all African countries with papers
    - Specific analysis of Sudan papers
    - Countries that might be missing from temporal analysis
    - Complete breakdown of African research presence

AUTHOR: Jonathan Shock
DATE: 2025
"""

import pandas as pd

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

def load_african_data():
    """
    Load and filter African papers data
    
    Returns:
        pandas.DataFrame: Filtered African papers data or None if file not found
    """
    try:
        # Load the combined data
        df = pd.read_csv('all_papers.csv')
        
        # Filter for African papers only
        african_papers = []
        for _, row in df.iterrows():
            countries_str = str(row['Author_Countries']) if pd.notna(row['Author_Countries']) else ''
            countries = [c.strip() for c in countries_str.split(';') if c.strip()]
            
            # Check if any author is from an African country
            if any(country in AFRICAN_COUNTRIES for country in countries):
                african_papers.append(row)
        
        african_df = pd.DataFrame(african_papers)
        
        # Filter to 2024 and earlier
        african_df = african_df[african_df['Year'] <= 2024]
        
        return african_df
        
    except FileNotFoundError:
        print("❌ Error: all_papers.csv not found. Please run combine_papers.py first.")
        return None

def check_all_african_countries(df):
    """
    Check all African countries for papers
    
    Args:
        df (pandas.DataFrame): African papers dataset
        
    Returns:
        pandas.Series: Count of papers by African country
    """
    
    # Extract all countries from Author_Countries column
    all_countries = []
    for countries_str in df['Author_Countries'].dropna():
        countries = [c.strip() for c in str(countries_str).split(';') if c.strip()]
        all_countries.extend(countries)
    
    # Filter for African countries only
    african_countries_found = [country for country in all_countries if country in AFRICAN_COUNTRIES]
    
    # Count papers by country
    country_counts = pd.Series(african_countries_found).value_counts()
    
    print("🌍 ALL AFRICAN COUNTRIES WITH PAPERS:")
    print("=" * 60)
    
    for country, count in country_counts.items():
        print(f"{country}: {count} papers")
    
    return country_counts

def check_sudan_specifically(df):
    """
    Check specifically for Sudan papers
    
    Args:
        df (pandas.DataFrame): African papers dataset
        
    Returns:
        list: List of Sudan papers
    """
    
    print(f"\n🇸🇩 SUDAN PAPERS ANALYSIS:")
    print("=" * 60)
    
    sudan_papers = []
    for _, row in df.iterrows():
        countries_str = str(row['Author_Countries']) if pd.notna(row['Author_Countries']) else ''
        countries = [c.strip() for c in countries_str.split(';') if c.strip()]
        
        if 'Sudan' in countries:
            sudan_papers.append(row)
    
    if sudan_papers:
        print(f"Found {len(sudan_papers)} papers from Sudan:")
        for paper in sudan_papers:
            print(f"  • {paper['Title']} ({paper['Year']}) - {paper['Conference']}")
    else:
        print("No papers found from Sudan.")
    
    return sudan_papers

def check_temporal_analysis_missing(df):
    """
    Check what countries might be missing from the temporal analysis
    
    Args:
        df (pandas.DataFrame): African papers dataset
        
    Returns:
        pandas.Series: Count of papers by country in temporal period
    """
    
    # Get the last 10 years
    current_year = 2024
    years = list(range(current_year - 9, current_year + 1))
    
    # Extract primary country for each paper
    primary_countries = []
    for countries_str in df['Author_Countries']:
        countries = [c.strip() for c in str(countries_str).split(';') if c.strip()]
        # Filter for African countries only
        african_countries = [country for country in countries if country in AFRICAN_COUNTRIES]
        primary_countries.append(african_countries[0] if african_countries else 'Unknown')
    
    df_temp = df.copy()
    df_temp['Primary_Country'] = primary_countries
    
    # Filter to last 10 years
    recent_df = df_temp[df_temp['Year'].isin(years)]
    recent_df = recent_df[recent_df['Primary_Country'] != 'Unknown']
    
    # Get all countries in the temporal period
    all_countries_temporal = recent_df['Primary_Country'].value_counts()
    
    print(f"\n📊 ALL COUNTRIES IN TEMPORAL ANALYSIS (2015-2024):")
    print("=" * 60)
    
    for country, count in all_countries_temporal.items():
        print(f"{country}: {count} papers")
    
    return all_countries_temporal

def main():
    """
    Main function to analyze Sudan and African countries data
    """
    print("🔍 Checking for Sudan and other African countries...")
    
    # Load data
    df = load_african_data()
    if df is None:
        return
    
    # Check all African countries
    country_counts = check_all_african_countries(df)
    
    # Check Sudan specifically
    sudan_papers = check_sudan_specifically(df)
    
    # Check temporal analysis
    temporal_countries = check_temporal_analysis_missing(df)
    
    print(f"\n✅ Analysis complete!")

if __name__ == "__main__":
    main() 