#!/usr/bin/env python3
"""
Extract country temporal data in Mathematica-compatible format.
Outputs: {{Country, {year1_count, year2_count, ...}}, ...}
Now includes ALL African countries with any papers.
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
        
        return african_df
        
    except FileNotFoundError:
        print("❌ Error: all_papers.csv not found. Please run combine_papers.py first.")
        return None

def extract_mathematica_format(df):
    """Extract data in Mathematica format - ALL countries with any papers"""
    
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
    
    # Create data for Mathematica format
    mathematica_data = []
    for country in all_countries_with_papers.index:
        country_counts = []
        for year in years:
            count = len(recent_df[(recent_df['Primary_Country'] == country) & (recent_df['Year'] == year)])
            country_counts.append(count)
        
        mathematica_data.append((country, country_counts))
    
    return mathematica_data, years

def check_south_sudan(df):
    """Check specifically for South Sudan papers"""
    
    print(f"\n🇸🇸 SOUTH SUDAN PAPERS ANALYSIS:")
    print("=" * 60)
    
    south_sudan_papers = []
    for _, row in df.iterrows():
        countries_str = str(row['Author_Countries']) if pd.notna(row['Author_Countries']) else ''
        countries = [c.strip() for c in countries_str.split(';') if c.strip()]
        
        if 'South Sudan' in countries:
            south_sudan_papers.append(row)
    
    if south_sudan_papers:
        print(f"Found {len(south_sudan_papers)} papers from South Sudan:")
        for paper in south_sudan_papers:
            print(f"  • {paper['Title']} ({paper['Year']}) - {paper['Conference']}")
    else:
        print("No papers found from South Sudan.")
    
    return south_sudan_papers

def display_mathematica_format(mathematica_data, years):
    """Display the data in Mathematica format"""
    
    print("📊 Mathematica-Compatible Format (ALL COUNTRIES):")
    print("=" * 60)
    print(f"Years: {years}")
    print()
    
    print("{{Country, {year_counts}}, ...}")
    print("-" * 60)
    
    for country, counts in mathematica_data:
        counts_str = ",".join(map(str, counts))
        print(f"{{{country}, {{{counts_str}}}}},")
    
    print()
    print("📈 Summary by country:")
    print("-" * 60)
    for country, counts in mathematica_data:
        total = sum(counts)
        print(f"{country}: {total} total papers")

def main():
    """Main function"""
    print("🎨 Extracting Country Temporal Data in Mathematica Format (ALL COUNTRIES)...")
    
    # Load data
    df = load_african_data()
    if df is None:
        return
    
    # Check for South Sudan specifically
    south_sudan_papers = check_south_sudan(df)
    
    # Extract data in Mathematica format
    mathematica_data, years = extract_mathematica_format(df)
    
    # Display the data
    display_mathematica_format(mathematica_data, years)
    
    print(f"\n✅ Data extraction complete!")
    print(f"📅 Years covered: {years[0]} - {years[-1]}")
    print(f"🌍 Total countries included: {len(mathematica_data)}")

if __name__ == "__main__":
    main() 