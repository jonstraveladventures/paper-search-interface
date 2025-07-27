#!/usr/bin/env python3
import pandas as pd

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

filtered = df[df['Author_Countries'].apply(has_selected_country)]
print(f"Found {len(filtered)} papers with Japan")

if len(filtered) > 0:
    print("Sample papers:")
    for i, (_, row) in enumerate(filtered.head(3).iterrows()):
        print(f"{i+1}. {row['Title']} - Countries: {row['Author_Countries']}")

# Test the exact filtering logic from web_interface.py
filtered_df = df.copy()
if selected_countries:
    filtered_df = filtered_df[filtered_df['Author_Countries'].apply(has_selected_country)]

print(f"Filtered result: {len(filtered_df)} papers") 