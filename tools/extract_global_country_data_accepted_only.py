#!/usr/bin/env python3
"""
Extract all countries in the world and their paper counts for AI-related fields (2015-2024).
Fields: AI, Computer Vision, Robotics, Computational Linguistics
FILTERED: Only accepted/published papers (removes rejected, withdrawn, desk rejected)
"""

import pandas as pd
from collections import Counter

def load_data():
    """Load the combined papers data"""
    try:
        df = pd.read_csv('all_papers.csv')
        print(f"📊 Loaded {len(df)} total papers")
        return df
    except FileNotFoundError:
        print("❌ Error: all_papers.csv not found. Please run combine_papers.py first.")
        return None

def filter_accepted_papers_only(df):
    """Filter to only include accepted/published papers"""
    
    # Define rejected/withdrawn statuses to exclude
    rejected_statuses = [
        'Reject', 'Withdraw', 'Desk Reject', 
        'NeurIPS 2023 Conference Withdrawn Submission'
    ]
    
    # Filter out rejected papers
    accepted_df = df[~df['Status'].isin(rejected_statuses)]
    
    print(f"🔍 Filtered out rejected/withdrawn papers:")
    print(f"   • Original papers: {len(df)}")
    print(f"   • After filtering: {len(accepted_df)}")
    print(f"   • Removed: {len(df) - len(accepted_df)} papers")
    
    # Show what was removed
    removed_papers = df[df['Status'].isin(rejected_statuses)]
    removed_counts = removed_papers['Status'].value_counts()
    print(f"\n📉 Removed papers by status:")
    for status, count in removed_counts.items():
        print(f"   • {status}: {count} papers")
    
    return accepted_df

def filter_ai_fields(df):
    """Filter for AI-related fields"""
    ai_fields = [
        'Artificial Intelligence',
        'Computer Vision and Pattern Recognition', 
        'Robotics',
        'Computational Linguistics'
    ]
    
    filtered_df = df[df['Subfield'].isin(ai_fields)]
    print(f"🔬 Filtered to {len(filtered_df)} papers in AI-related fields")
    
    # Show breakdown by subfield
    subfield_counts = filtered_df['Subfield'].value_counts()
    print("\n📈 Papers by subfield:")
    for subfield, count in subfield_counts.items():
        print(f"   • {subfield}: {count} papers")
    
    return filtered_df

def filter_temporal_period(df):
    """Filter to 2015-2024 period"""
    temporal_df = df[df['Year'].between(2015, 2024)]
    print(f"\n📅 Filtered to {len(temporal_df)} papers from 2015-2024")
    return temporal_df

def extract_all_countries(df):
    """Extract all countries from the dataset"""
    all_countries = []
    
    for countries_str in df['Author_Countries'].dropna():
        countries = [c.strip() for c in str(countries_str).split(';') if c.strip()]
        all_countries.extend(countries)
    
    # Count papers by country
    country_counts = Counter(all_countries)
    
    print(f"\n🌍 Found {len(country_counts)} unique countries")
    return country_counts

def display_top_countries(country_counts, top_n=50):
    """Display top countries by paper count"""
    print(f"\n🏆 TOP {top_n} COUNTRIES BY PAPER COUNT (ACCEPTED ONLY):")
    print("=" * 80)
    print(f"{'Rank':<6} {'Country':<30} {'Papers':<10} {'Percentage':<12}")
    print("-" * 80)
    
    total_papers = sum(country_counts.values())
    
    for i, (country, count) in enumerate(country_counts.most_common(top_n), 1):
        percentage = (count / total_papers) * 100
        print(f"{i:<6} {country:<30} {count:<10} {percentage:>8.1f}%")
    
    return total_papers

def display_all_countries(country_counts):
    """Display all countries with their paper counts"""
    print(f"\n🌍 ALL COUNTRIES WITH PAPERS (2015-2024, ACCEPTED ONLY):")
    print("=" * 80)
    print(f"{'Rank':<6} {'Country':<30} {'Papers':<10}")
    print("-" * 80)
    
    for i, (country, count) in enumerate(country_counts.most_common(), 1):
        print(f"{i:<6} {country:<30} {count:<10}")

def export_to_csv(country_counts, filename='global_country_papers_accepted_only_2015_2024.csv'):
    """Export country data to CSV"""
    data = []
    for country, count in country_counts.most_common():
        data.append({'Country': country, 'Papers': count})
    
    df_export = pd.DataFrame(data)
    df_export.to_csv(filename, index=False)
    print(f"\n💾 Exported data to: {filename}")

def analyze_regions(country_counts):
    """Analyze papers by region/continent"""
    print(f"\n🌍 REGIONAL ANALYSIS (ACCEPTED PAPERS ONLY):")
    print("=" * 50)
    
    # Define some major regions (simplified)
    regions = {
        'North America': ['United States', 'Canada'],
        'Europe': ['United Kingdom', 'Germany', 'France', 'Italy', 'Spain', 'Netherlands', 'Switzerland', 'Sweden', 'Norway', 'Denmark', 'Finland', 'Belgium', 'Austria', 'Poland', 'Czech Republic', 'Hungary', 'Portugal', 'Greece', 'Ireland', 'Luxembourg', 'Iceland'],
        'Asia': ['China', 'Japan', 'South Korea', 'India', 'Singapore', 'Taiwan', 'Hong Kong', 'Israel', 'Thailand', 'Malaysia', 'Vietnam', 'Indonesia', 'Philippines', 'Pakistan', 'Bangladesh', 'Sri Lanka', 'Nepal', 'Cambodia', 'Myanmar', 'Laos', 'Mongolia'],
        'Oceania': ['Australia', 'New Zealand'],
        'South America': ['Brazil', 'Argentina', 'Chile', 'Colombia', 'Peru', 'Uruguay', 'Venezuela', 'Ecuador', 'Bolivia', 'Paraguay'],
        'Africa': ['South Africa', 'Egypt', 'Algeria', 'Tunisia', 'Nigeria', 'Kenya', 'Morocco', 'Libya', 'Cameroon', 'Ethiopia', 'Ghana', 'Uganda', 'Burkina Faso', 'Rwanda', 'Mozambique', 'Benin', 'Tanzania', 'Madagascar', 'Sudan', 'Zambia'],
        'Middle East': ['Saudi Arabia', 'United Arab Emirates', 'Qatar', 'Kuwait', 'Bahrain', 'Oman', 'Jordan', 'Lebanon', 'Syria', 'Iraq', 'Iran', 'Turkey']
    }
    
    region_totals = {}
    for region, countries in regions.items():
        total = sum(country_counts.get(country, 0) for country in countries)
        region_totals[region] = total
    
    # Sort regions by total papers
    sorted_regions = sorted(region_totals.items(), key=lambda x: x[1], reverse=True)
    
    for region, total in sorted_regions:
        if total > 0:
            print(f"{region}: {total} papers")

def main():
    """Main function"""
    print("🌍 Extracting Global Country Data for AI Research (2015-2024, ACCEPTED PAPERS ONLY)...")
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Filter to accepted papers only
    accepted_df = filter_accepted_papers_only(df)
    
    # Filter for AI-related fields
    ai_df = filter_ai_fields(accepted_df)
    
    # Filter to temporal period
    temporal_df = filter_temporal_period(ai_df)
    
    # Extract all countries
    country_counts = extract_all_countries(temporal_df)
    
    # Display top countries
    total_papers = display_top_countries(country_counts, top_n=50)
    
    # Display all countries
    display_all_countries(country_counts)
    
    # Regional analysis
    analyze_regions(country_counts)
    
    # Export to CSV
    export_to_csv(country_counts)
    
    print(f"\n✅ Analysis complete!")
    print(f"📊 Total accepted papers analyzed: {total_papers}")
    print(f"🌍 Total countries: {len(country_counts)}")

if __name__ == "__main__":
    main() 