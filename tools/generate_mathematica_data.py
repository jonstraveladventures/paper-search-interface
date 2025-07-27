#!/usr/bin/env python3
"""
Script to generate Mathematica-compatible data for African countries and collaborations.
"""

import pandas as pd
from pathlib import Path
from collections import defaultdict

# Define African countries with their GeoPositions (latitude, longitude)
AFRICAN_COUNTRIES_GEO = {
    'South Africa': (-30.5595, 22.9375),
    'Egypt': (26.8206, 30.8025),
    'Algeria': (28.0339, 1.6596),
    'Tunisia': (33.8869, 9.5375),
    'Nigeria': (9.0820, 8.6753),
    'Morocco': (31.7917, -7.0926),
    'Kenya': (-0.0236, 37.9062),
    'Cameroon': (7.3697, 12.3547),
    'Libya': (26.3351, 17.2283),
    'Ghana': (7.9465, -1.0232),
    'Ethiopia': (9.1450, 40.4897),
    'Rwanda': (-1.9403, 29.8739),
    'Uganda': (1.3733, 32.2903),
    'Zambia': (-13.1339, 27.8493),
    'Namibia': (-22.9576, 18.4904),
    'Madagascar': (-18.7669, 46.8691),
    'Tanzania': (-6.3690, 34.8888),
    'Burkina Faso': (12.2383, -1.5616),
    'Malawi': (-13.2543, 34.3015),
    'Togo': (8.6195, 0.8248),
    'Mali': (17.5707, -3.9962),
    'Senegal': (14.4974, -14.4524),
    'Sudan': (12.8628, 30.2176),
    'Benin': (9.3077, 2.3158),
    'Mozambique': (-18.6657, 35.5296),
    'Djibouti': (11.8251, 42.5903),
    'Mauritius': (-20.3484, 57.5522)
}

def extract_african_countries(countries_str):
    """Extract African countries from a countries string"""
    if pd.isna(countries_str) or not countries_str.strip():
        return []
    
    countries = [c.strip() for c in countries_str.split(';') if c.strip()]
    african_countries = [c for c in countries if c in AFRICAN_COUNTRIES_GEO]
    return african_countries

def main():
    """Main function to generate Mathematica data"""
    
    # Get the root directory (parent of tools folder)
    root_dir = Path(__file__).parent.parent
    
    # Define input CSV file
    csv_file = root_dir / 'african_papers.csv'
    
    if not csv_file.exists():
        print(f"Error: {csv_file} not found!")
        return
    
    print("Loading African papers CSV...")
    df = pd.read_csv(csv_file)
    
    print(f"Total African papers: {len(df):,}")
    
    # Count papers by African country
    country_counts = defaultdict(int)
    collaborations = defaultdict(int)
    
    for _, row in df.iterrows():
        african_countries = extract_african_countries(row['Author_Countries'])
        
        # Count individual countries
        for country in african_countries:
            country_counts[country] += 1
        
        # Count collaborations (pairs of African countries)
        if len(african_countries) >= 2:
            for i in range(len(african_countries)):
                for j in range(i + 1, len(african_countries)):
                    country1, country2 = sorted([african_countries[i], african_countries[j]])
                    collaborations[(country1, country2)] += 1
    
    # Generate countriesData for Mathematica
    print("\n=== COUNTRIES DATA FOR MATHEMATICA ===")
    print("countriesData = {")
    
    countries_data = []
    for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True):
        if country in AFRICAN_COUNTRIES_GEO:
            lat, lon = AFRICAN_COUNTRIES_GEO[country]
            countries_data.append((country, count, lat, lon))
            print(f'    {{"{country}", {count}, GeoPosition[{{{lat}, {lon}}}]}},')
    
    print("};")
    
    # Generate collaborationsData for Mathematica
    print("\n=== COLLABORATIONS DATA FOR MATHEMATICA ===")
    print("collaborationsData = {")
    
    collaborations_list = []
    for (country1, country2), count in sorted(collaborations.items(), key=lambda x: x[1], reverse=True):
        collaborations_list.append((country1, country2, count))
        print(f'    {{"{country1}", "{country2}", {count}}},')
    
    print("};")
    
    # Save to file
    output_file = root_dir / 'mathematica_data.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("(* African Countries Data for Mathematica *)\n\n")
        f.write("(* Step 1: Define countries data with paper counts and geolocations *)\n")
        f.write("countriesData = {\n")
        
        for country, count, lat, lon in countries_data:
            f.write(f'    {{"{country}", {count}, GeoPosition[{{{lat}, {lon}}}]}},\n')
        
        f.write("};\n\n")
        f.write("(* Step 2: Define collaboration data using country names *)\n")
        f.write("collaborationsData = {\n")
        
        for country1, country2, count in collaborations_list:
            f.write(f'    {{"{country1}", "{country2}", {count}}},\n')
        
        f.write("};\n\n")
        
        # Add summary statistics
        f.write("(* Summary Statistics *)\n")
        f.write(f"(* Total African countries with papers: {len(countries_data)} *)\n")
        f.write(f"(* Total papers: {sum(country_counts.values())} *)\n")
        f.write(f"(* Total collaborations: {len(collaborations_list)} *)\n")
        f.write(f"(* Total collaboration instances: {sum(collaborations.values())} *)\n")
    
    print(f"\nMathematica data saved to: {output_file}")
    
    # Print summary
    print(f"\n=== SUMMARY ===")
    print(f"Total African countries with papers: {len(countries_data)}")
    print(f"Total papers: {sum(country_counts.values())}")
    print(f"Total collaborations: {len(collaborations_list)}")
    print(f"Total collaboration instances: {sum(collaborations.values())}")
    
    # Show top collaborations
    print(f"\n=== TOP COLLABORATIONS ===")
    for country1, country2, count in collaborations_list[:10]:
        print(f"  {country1} - {country2}: {count} papers")

if __name__ == "__main__":
    main() 