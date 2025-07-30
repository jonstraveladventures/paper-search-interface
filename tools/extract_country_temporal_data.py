#!/usr/bin/env python3
"""
Extract and display the country temporal data used in the African AI research visualization.
This shows the breakdown of publications by African country and year (2015-2024).
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

def load_african_data():
    """Load and filter African papers data"""
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
        
        print(f"📊 Loaded {len(african_df)} African papers (up to 2024)")
        return african_df
        
    except FileNotFoundError:
        print("❌ Error: all_papers.csv not found. Please run combine_papers.py first.")
        return None

def extract_country_temporal_data(df):
    """Extract the country temporal data used in the visualization"""
    
    # Get the last 10 years
    current_year = 2024
    years = list(range(current_year - 9, current_year + 1))
    
    print(f"\n📅 Analyzing data for years: {years[0]} - {years[-1]}")
    
    # Extract primary country for each paper
    primary_countries = []
    for countries_str in df['Author_Countries']:
        countries = [c.strip() for c in str(countries_str).split(';') if c.strip()]
        # Filter for African countries only
        african_countries = [country for country in countries if country in AFRICAN_COUNTRIES]
        primary_countries.append(african_countries[0] if african_countries else 'Unknown')
    
    df_temp = df.copy()
    df_temp['Primary_Country'] = primary_countries
    
    # Filter to last 10 years and get top African countries
    recent_df = df_temp[df_temp['Year'].isin(years)]
    recent_df = recent_df[recent_df['Primary_Country'] != 'Unknown']  # Remove papers without African countries
    top_countries = recent_df['Primary_Country'].value_counts().head(15).index
    
    print(f"\n🏆 Top 15 African countries by total publications:")
    for i, country in enumerate(top_countries, 1):
        total = len(recent_df[recent_df['Primary_Country'] == country])
        print(f"   {i:2d}. {country}: {total} papers")
    
    # Create data for stacked bar chart
    country_data = {}
    for country in top_countries:
        country_data[country] = []
        for year in years:
            count = len(recent_df[(recent_df['Primary_Country'] == country) & (recent_df['Year'] == year)])
            country_data[country].append(count)
    
    return country_data, years, top_countries

def display_detailed_data(country_data, years, top_countries):
    """Display the detailed data in a formatted table"""
    
    print(f"\n" + "="*100)
    print("📊 DETAILED COUNTRY TEMPORAL DATA (2015-2024)")
    print("="*100)
    
    # Create header
    header = f"{'Country':<20}"
    for year in years:
        header += f"{year:>6}"
    header += f"{'Total':>8}"
    print(header)
    print("-" * 100)
    
    # Display data for each country
    for country in top_countries:
        row = f"{country:<20}"
        total = 0
        for year in years:
            count = country_data[country][years.index(year)]
            total += count
            row += f"{count:>6}"
        row += f"{total:>8}"
        print(row)
    
    print("-" * 100)
    
    # Display year totals
    year_totals = []
    for year in years:
        total = sum(country_data[country][years.index(year)] for country in top_countries)
        year_totals.append(total)
    
    row = f"{'YEAR TOTALS':<20}"
    for year, total in zip(years, year_totals):
        row += f"{total:>6}"
    row += f"{sum(year_totals):>8}"
    print(row)
    
    print("="*100)

def display_summary_statistics(country_data, years, top_countries):
    """Display summary statistics"""
    
    print(f"\n📈 SUMMARY STATISTICS:")
    print("-" * 50)
    
    # Total papers in the analysis
    total_papers = sum(sum(country_data[country]) for country in top_countries)
    print(f"Total papers analyzed: {total_papers}")
    
    # Countries with most recent activity (2024)
    recent_activity = []
    for country in top_countries:
        count_2024 = country_data[country][-1]  # Last year (2024)
        if count_2024 > 0:
            recent_activity.append((country, count_2024))
    
    recent_activity.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n🏆 Countries with publications in 2024:")
    for country, count in recent_activity[:10]:
        print(f"   • {country}: {count} papers")
    
    # Most consistent countries (papers every year)
    consistent_countries = []
    for country in top_countries:
        years_with_papers = sum(1 for count in country_data[country] if count > 0)
        if years_with_papers >= 5:  # At least 5 years with papers
            consistent_countries.append((country, years_with_papers))
    
    consistent_countries.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n📅 Most consistent countries (years with publications):")
    for country, years_count in consistent_countries[:10]:
        print(f"   • {country}: {years_count} years")

def main():
    """Main function to extract and display the data"""
    print("🎨 Extracting Country Temporal Data for African AI Research...")
    
    # Load data
    df = load_african_data()
    if df is None:
        return
    
    # Extract the data used in visualization
    country_data, years, top_countries = extract_country_temporal_data(df)
    
    # Display detailed data
    display_detailed_data(country_data, years, top_countries)
    
    # Display summary statistics
    display_summary_statistics(country_data, years, top_countries)
    
    print(f"\n✅ Data extraction complete!")
    print(f"📁 This data was used to generate: tools/img/african_country_temporal.png")

if __name__ == "__main__":
    main() 