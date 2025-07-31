#!/usr/bin/env python3
"""
CSV Export Tool for African Papers Data (Accepted Papers Only)

This script creates CSV files for African papers data with only accepted papers. It generates two main files:
1. Temporal data by country and year (2015-2024)
2. Research areas data for pie chart generation

USAGE:
    python tools/create_csv_exports.py

OUTPUT FILES:
    - african_country_temporal_2015_2024_accepted.csv: Country-year breakdown
    - african_research_areas_accepted.csv: Research area breakdown

AUTHOR: Jonathan Shock
DATE: 2025
"""

import pandas as pd
import csv

# Define African countries
AFRICAN_COUNTRIES = {
    'Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cameroon', 
    'Cape Verde', 'Central African Republic', 'Chad', 'Comoros', 'Congo', 
    'Democratic Republic of the Congo', 'Djibouti', 'Egypt', 'Equatorial Guinea', 
    'Eritrea', 'Eswatini', 'Ethiopia', 'Gabon', 'Gambia', 'Ghana', 'Guinea', 'Guinea-Bissau', 
    'Ivory Coast', 'Kenya', 'Lesotho', 'Liberia', 'Libya', 'Madagascar', 'Malawi', 
    'Mali', 'Mauritania', 'Mauritius', 'Morocco', 'Mozambique', 'Namibia', 'Niger', 
    'Nigeria', 'Rwanda', 'Sao Tome and Principe', 'Senegal', 'Seychelles', 
    'Sierra Leone', 'Somalia', 'South Africa', 'South Sudan', 'Sudan', 
    'Tanzania', 'Togo', 'Tunisia', 'Uganda', 'Western Sahara', 'Zambia', 'Zimbabwe'
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

def filter_accepted_african_papers(df):
    """
    Filter to only accepted African papers (excluding rejected/withdrawn)
    
    Args:
        df (pandas.DataFrame): The complete papers dataset
        
    Returns:
        pandas.DataFrame: Filtered African papers (accepted only)
    """
    
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
    
    return african_df

def create_temporal_csv(df):
    """
    Create CSV file with temporal data by country and year
    
    Args:
        df (pandas.DataFrame): African papers dataset
        
    Returns:
        pandas.DataFrame: The created temporal CSV data
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
    
    # Filter to last 10 years and get ALL African countries with any papers
    recent_df = df_temp[df_temp['Year'].isin(years)]
    recent_df = recent_df[recent_df['Primary_Country'] != 'Unknown']  # Remove papers without African countries
    
    # Get ALL countries that have any papers in the temporal period
    all_countries_with_papers = recent_df['Primary_Country'].value_counts()
    
    # Create data for CSV
    csv_data = []
    for country in all_countries_with_papers.index:
        row = {'Country': country}
        total_papers = 0
        
        for year in years:
            count = len(recent_df[(recent_df['Primary_Country'] == country) & (recent_df['Year'] == year)])
            row[str(year)] = count
            total_papers += count
        
        row['Total'] = total_papers
        csv_data.append(row)
    
    # Create DataFrame and sort by total papers
    df_csv = pd.DataFrame(csv_data)
    df_csv = df_csv.sort_values('Total', ascending=False)
    
    # Save to CSV
    filename = 'african_country_temporal_2015_2024_accepted.csv'
    df_csv.to_csv(filename, index=False)
    
    print(f"💾 Temporal data saved to: {filename}")
    print(f"📊 Countries included: {len(df_csv)}")
    
    return df_csv

def create_research_areas_csv(df):
    """
    Create CSV file with research areas data for pie chart
    
    Args:
        df (pandas.DataFrame): African papers dataset
        
    Returns:
        pandas.DataFrame: The created research areas CSV data
    """
    
    # Count papers by subfield
    subfield_counts = df['Subfield'].value_counts()
    
    # Create data for CSV
    csv_data = []
    total_papers = len(df)
    
    for subfield, count in subfield_counts.items():
        percentage = (count / total_papers) * 100
        
        # Clean up subfield name for display
        if subfield == 'Computer Vision and Pattern Recognition':
            display_name = 'Computer Vision'
        else:
            display_name = subfield
        
        csv_data.append({
            'Research_Area': display_name,
            'Papers': count,
            'Percentage': round(percentage, 1)
        })
    
    # Create DataFrame
    df_csv = pd.DataFrame(csv_data)
    
    # Save to CSV
    filename = 'african_research_areas_accepted.csv'
    df_csv.to_csv(filename, index=False)
    
    print(f"💾 Research areas data saved to: {filename}")
    print(f"📊 Research areas included: {len(df_csv)}")
    
    return df_csv

def display_summary(df_temporal, df_research):
    """
    Display summary of the created CSV files
    
    Args:
        df_temporal (pandas.DataFrame): Temporal CSV data
        df_research (pandas.DataFrame): Research areas CSV data
    """
    
    print(f"\n📋 CSV FILES CREATED:")
    print("=" * 50)
    
    print(f"\n1. Temporal Data (african_country_temporal_2015_2024_accepted.csv):")
    print("-" * 60)
    print(f"   • Countries: {len(df_temporal)}")
    print(f"   • Years: 2015-2024")
    print(f"   • Total papers: {df_temporal['Total'].sum()}")
    print(f"   • Top 5 countries:")
    for i, row in df_temporal.head().iterrows():
        print(f"     {i+1}. {row['Country']}: {row['Total']} papers")
    
    print(f"\n2. Research Areas (african_research_areas_accepted.csv):")
    print("-" * 60)
    print(f"   • Research areas: {len(df_research)}")
    print(f"   • Total papers: {df_research['Papers'].sum()}")
    print(f"   • Breakdown:")
    for _, row in df_research.iterrows():
        print(f"     • {row['Research_Area']}: {row['Papers']} papers ({row['Percentage']}%)")

def main():
    """
    Main function to create CSV files for African papers data
    """
    print("📊 Creating CSV files for African papers data (accepted papers only)...")
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Filter to accepted African papers
    african_df = filter_accepted_african_papers(df)
    
    # Create temporal CSV
    df_temporal = create_temporal_csv(african_df)
    
    # Create research areas CSV
    df_research = create_research_areas_csv(african_df)
    
    # Display summary
    display_summary(df_temporal, df_research)
    
    print(f"\n✅ CSV files created successfully!")
    print(f"📁 Files saved in current directory")

if __name__ == "__main__":
    main() 