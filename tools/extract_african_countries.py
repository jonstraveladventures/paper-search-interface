#!/usr/bin/env python3
"""
Script to identify and list all African countries from the complete country list.
"""

# Define African countries (including all countries on the African continent)
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

def main():
    """Main function to identify African countries from the dataset"""
    
    # Read the unique countries from the file
    countries_file = 'unique_countries.txt'
    
    try:
        with open(countries_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract countries from the file
        lines = content.split('\n')
        all_countries = []
        in_country_list = False
        
        for line in lines:
            if 'All countries (alphabetically sorted):' in line:
                in_country_list = True
                continue
            elif '=== COUNTRY COUNTS ===' in line:
                break
            elif in_country_list and line.strip():
                # Extract country name from lines like "  1. Albania"
                if '. ' in line:
                    country = line.split('. ', 1)[1].strip()
                    all_countries.append(country)
        
        # Find African countries
        african_countries_found = []
        for country in all_countries:
            if country in AFRICAN_COUNTRIES:
                african_countries_found.append(country)
        
        # Sort alphabetically
        african_countries_found.sort()
        
        print("=== AFRICAN COUNTRIES FOUND IN THE DATASET ===")
        print(f"Total African countries found: {len(african_countries_found)}")
        print(f"Total countries in dataset: {len(all_countries)}")
        print(f"Percentage of African countries: {len(african_countries_found)/len(all_countries)*100:.1f}%")
        
        print(f"\nAfrican countries (alphabetically sorted):")
        for i, country in enumerate(african_countries_found, 1):
            print(f"{i:2d}. {country}")
        
        # Also show which African countries are NOT in the dataset
        african_countries_not_found = []
        for country in AFRICAN_COUNTRIES:
            if country not in all_countries:
                african_countries_not_found.append(country)
        
        if african_countries_not_found:
            print(f"\nAfrican countries NOT found in the dataset:")
            for i, country in enumerate(sorted(african_countries_not_found), 1):
                print(f"{i:2d}. {country}")
        
        # Save to file
        output_file = 'african_countries.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=== AFRICAN COUNTRIES FOUND IN THE DATASET ===\n")
            f.write(f"Total African countries found: {len(african_countries_found)}\n")
            f.write(f"Total countries in dataset: {len(all_countries)}\n")
            f.write(f"Percentage of African countries: {len(african_countries_found)/len(all_countries)*100:.1f}%\n\n")
            
            f.write("African countries (alphabetically sorted):\n")
            for i, country in enumerate(african_countries_found, 1):
                f.write(f"{i:2d}. {country}\n")
            
            if african_countries_not_found:
                f.write(f"\nAfrican countries NOT found in the dataset:\n")
                for i, country in enumerate(sorted(african_countries_not_found), 1):
                    f.write(f"{i:2d}. {country}\n")
        
        print(f"\nAfrican countries list saved to: {output_file}")
        
    except FileNotFoundError:
        print(f"Error: {countries_file} not found!")
        print("Please run extract_countries.py first to generate the countries list.")

if __name__ == "__main__":
    main() 