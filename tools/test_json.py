#!/usr/bin/env python3
import pandas as pd
import json

# Load data
df = pd.read_csv('../all_papers.csv')
print(f"Total papers: {len(df)}")

# Test Japan search
selected_countries = ['Japan']

def has_selected_country(countries_str):
    if pd.isna(countries_str) or not countries_str.strip():
        return False
    countries = [c.strip() for c in countries_str.split(';') if c.strip()]
    return any(country in countries for country in selected_countries)

filtered_df = df[df['Author_Countries'].apply(has_selected_country)]
print(f"Found {len(filtered_df)} papers with Japan")

# Test JSON conversion (same as web interface)
results = []
try:
    for _, row in filtered_df.head(5).iterrows():  # Just test first 5
        result = {
            'title': row['Title'],
            'authors': row['Authors'],
            'conference': row['Conference'],
            'year': int(row['Year']),
            'subfield': row['Subfield'],
            'countries': row['Author_Countries'],
            'status': row['Status'],
            'track': row['Track'],
            'citations': int(row['Citations']) if pd.notna(row['Citations']) else 0
        }
        results.append(result)
        print(f"Processed paper: {result['title'][:50]}...")
except Exception as e:
    print(f"Error processing results: {e}")
    import traceback
    traceback.print_exc()

# Test JSON serialization
try:
    json_data = {
        'results': results,
        'total': len(filtered_df)
    }
    json_str = json.dumps(json_data, ensure_ascii=False)
    print(f"JSON serialization successful, length: {len(json_str)}")
except Exception as e:
    print(f"JSON serialization error: {e}")
    import traceback
    traceback.print_exc() 