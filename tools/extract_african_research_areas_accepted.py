#!/usr/bin/env python3
"""
African Research Areas Analysis Tool (Accepted Papers Only)

This script extracts the research area breakdown for African papers with only accepted papers.
It provides the correct numbers for generating pie charts and other visualizations that
represent published research rather than including rejected/withdrawn papers.

USAGE:
    python tools/extract_african_research_areas_accepted.py

OUTPUT:
    - Research area breakdown for accepted African papers only
    - Mathematica-compatible code for pie chart generation
    - Percentage breakdown by research area

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

def analyze_research_areas(df):
    """
    Analyze research areas for African papers
    
    Args:
        df (pandas.DataFrame): African papers dataset
        
    Returns:
        pandas.Series: Count of papers by research area
    """
    
    print(f"\n🔬 RESEARCH AREA BREAKDOWN (ACCEPTED PAPERS ONLY):")
    print("=" * 60)
    
    # Count papers by subfield
    subfield_counts = df['Subfield'].value_counts()
    
    print(f"📈 Papers by research area:")
    print("-" * 40)
    for subfield, count in subfield_counts.items():
        percentage = (count / len(df)) * 100
        print(f"• {subfield}: {count} papers ({percentage:.1f}%)")
    
    return subfield_counts

def generate_mathematica_code(subfield_counts):
    """
    Generate Mathematica code for the pie chart
    
    Args:
        subfield_counts (pandas.Series): Count of papers by research area
        
    Returns:
        str: Mathematica code for pie chart generation
    """
    
    print(f"\n🎨 MATHEMATICA CODE:")
    print("=" * 60)
    
    # Create the association for Mathematica
    mathematica_assoc = []
    for subfield, count in subfield_counts.items():
        # Clean up subfield name for display
        if subfield == 'Computer Vision and Pattern Recognition':
            display_name = 'Computer Vision'
        else:
            display_name = subfield
        
        mathematica_assoc.append(f'Style["{display_name} ({count} papers)", 14, Bold] -> {count}')
    
    # Generate the full Mathematica code
    mathematica_code = f"""PieChart[<|{', '.join(mathematica_assoc)}|>, 
 ChartLabels -> Callout[Automatic], ImageSize -> 700, 
 ChartStyle -> "DarkRainbow", ImagePadding -> {{{80, 80}, {{60, 60}}}}
Export["piechart.png", %]"""
    
    print(mathematica_code)
    
    return mathematica_code

def main():
    """
    Main function to extract African research areas for accepted papers only
    """
    print("🔬 Extracting African research areas (accepted papers only)...")
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Filter to accepted African papers
    african_df = filter_accepted_african_papers(df)
    
    # Analyze research areas
    subfield_counts = analyze_research_areas(african_df)
    
    # Generate Mathematica code
    mathematica_code = generate_mathematica_code(subfield_counts)
    
    print(f"\n✅ Analysis complete!")
    print(f"📊 Total accepted African papers: {len(african_df)}")

if __name__ == "__main__":
    main() 