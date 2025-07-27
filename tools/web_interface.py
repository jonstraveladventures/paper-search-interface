#!/usr/bin/env python3
"""
Flask web application for querying paper data with interactive filters.
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
from pathlib import Path
import re

app = Flask(__name__)

# Load the data
def load_data():
    """Load the paper data"""
    root_dir = Path(__file__).parent.parent
    csv_file = root_dir / 'all_papers.csv'
    
    if csv_file.exists():
        df = pd.read_csv(csv_file)
        return df
    else:
        return pd.DataFrame()

# Define continents and their countries
CONTINENTS = {
    'Africa': [
        'Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cameroon',
        'Cape Verde', 'Central African Republic', 'Chad', 'Comoros', 'Congo',
        'Democratic Republic of the Congo', 'Djibouti', 'Egypt', 'Equatorial Guinea',
        'Eritrea', 'Ethiopia', 'Gabon', 'Gambia', 'Ghana', 'Guinea', 'Guinea-Bissau',
        'Ivory Coast', 'Kenya', 'Lesotho', 'Liberia', 'Libya', 'Madagascar', 'Malawi',
        'Mali', 'Mauritania', 'Mauritius', 'Morocco', 'Mozambique', 'Namibia', 'Niger',
        'Nigeria', 'Rwanda', 'São Tomé and Príncipe', 'Senegal', 'Seychelles',
        'Sierra Leone', 'Somalia', 'South Africa', 'South Sudan', 'Sudan', 'Tanzania',
        'Togo', 'Tunisia', 'Uganda', 'Zambia', 'Zimbabwe'
    ],
    'Asia': [
        'Afghanistan', 'Armenia', 'Azerbaijan', 'Bahrain', 'Bangladesh', 'Bhutan',
        'Brunei Darussalam', 'Cambodia', 'China', 'Cyprus', 'Georgia', 'India',
        'Indonesia', 'Iran', 'Iraq', 'Israel', 'Japan', 'Jordan', 'Kazakhstan',
        'Kuwait', 'Kyrgyzstan', 'Laos', 'Lebanon', 'Malaysia', 'Maldives', 'Mongolia',
        'Myanmar', 'Nepal', 'North Korea', 'Oman', 'Pakistan', 'Palestine',
        'Philippines', 'Qatar', 'Saudi Arabia', 'Singapore', 'South Korea', 'Sri Lanka',
        'Syria', 'Taiwan', 'Tajikistan', 'Thailand', 'Timor-Leste', 'Turkey',
        'Turkmenistan', 'United Arab Emirates', 'Uzbekistan', 'Vietnam', 'Yemen'
    ],
    'Europe': [
        'Albania', 'Andorra', 'Austria', 'Belarus', 'Belgium', 'Bosnia and Herzegovina',
        'Bulgaria', 'Croatia', 'Czech Republic', 'Czechia', 'Denmark', 'Estonia',
        'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland',
        'Italy', 'Latvia', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Malta',
        'Moldova', 'Monaco', 'Montenegro', 'Netherlands', 'North Macedonia', 'Norway',
        'Poland', 'Portugal', 'Romania', 'Russia', 'Russian Federation', 'San Marino',
        'Serbia', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland',
        'Ukraine', 'United Kingdom', 'Vatican City'
    ],
    'North America': [
        'Antigua and Barbuda', 'Bahamas', 'Barbados', 'Belize', 'Canada', 'Costa Rica',
        'Cuba', 'Dominica', 'Dominican Republic', 'El Salvador', 'Grenada',
        'Guatemala', 'Haiti', 'Honduras', 'Jamaica', 'Mexico', 'Nicaragua', 'Panama',
        'Puerto Rico', 'Saint Kitts and Nevis', 'Saint Lucia',
        'Saint Vincent and the Grenadines', 'Trinidad and Tobago', 'United States'
    ],
    'South America': [
        'Argentina', 'Bolivia', 'Brazil', 'Chile', 'Colombia', 'Ecuador', 'Guyana',
        'Paraguay', 'Peru', 'Suriname', 'Uruguay', 'Venezuela'
    ],
    'Oceania': [
        'Australia', 'Fiji', 'Kiribati', 'Marshall Islands', 'Micronesia', 'Nauru',
        'New Caledonia', 'New Zealand', 'Palau', 'Papua New Guinea', 'Samoa',
        'Solomon Islands', 'Tonga', 'Tuvalu', 'Vanuatu'
    ]
}

def get_unique_countries(df):
    """Get all unique countries from the dataset"""
    all_countries = []
    for countries_str in df['Author_Countries'].dropna():
        if countries_str and countries_str.strip():
            countries = [c.strip() for c in countries_str.split(';') if c.strip()]
            all_countries.extend(countries)
    return sorted(set(all_countries))

def get_unique_venues(df):
    """Get all unique venues from the dataset"""
    return sorted(df['Conference'].unique())

def get_subfield(conference_name):
    """Get subfield for a conference"""
    conference_name = conference_name.upper()
    if conference_name in ['NIPS', 'NEURIPS', 'ICLR', 'ICML', 'AAAI', 'IJCAI', 'AISTATS', 'CORL', 'ACML']:
        return 'Artificial Intelligence'
    elif conference_name in ['ACL', 'EMNLP', 'NAACL', 'COLING', 'ARR', 'COLM']:
        return 'Computational Linguistics'
    elif conference_name in ['SIGGRAPH', 'SIGGRAPHASIA', 'EUROGRAPHICS']:
        return 'Computer Graphics'
    elif conference_name in ['SITCOM']:
        return 'Computer Networks and Wireless Communication'
    elif conference_name in ['CVPR', 'ICCV', 'WACV', 'BMVC', '3DV']:
        return 'Computer Vision and Pattern Recognition'
    elif conference_name in ['KDD']:
        return 'Data Mining and Analysis'
    elif conference_name in ['WWW', 'SIGIR']:
        return 'Databases and Information Systems'
    elif conference_name in ['ACMMM']:
        return 'Multimedia'
    elif conference_name in ['ICRA', 'IROS', 'RSS']:
        return 'Robotics'
    else:
        return 'Other'

def get_venues_by_subfield(df):
    """Get venues grouped by subfield"""
    venues = get_unique_venues(df)
    venues_by_subfield = {}
    
    for venue in venues:
        subfield = get_subfield(venue)
        if subfield not in venues_by_subfield:
            venues_by_subfield[subfield] = []
        venues_by_subfield[subfield].append(venue)
    
    return venues_by_subfield

def filter_papers(df, title_search='', author_search='', selected_countries=None, 
                 selected_venues=None, year_min=None, year_max=None):
    """Filter papers based on search criteria"""
    if selected_countries is None:
        selected_countries = []
    if selected_venues is None:
        selected_venues = []
    
    filtered_df = df.copy()
    
    # Filter by title search
    if title_search:
        filtered_df = filtered_df[filtered_df['Title'].str.contains(title_search, case=False, na=False)]
    
    # Filter by author search
    if author_search:
        filtered_df = filtered_df[filtered_df['Authors'].str.contains(author_search, case=False, na=False)]
    
    # Filter by countries
    if selected_countries:
        def has_selected_country(countries_str):
            if pd.isna(countries_str) or not countries_str.strip():
                return False
            countries = [c.strip() for c in countries_str.split(';') if c.strip()]
            return any(country in countries for country in selected_countries)
        
        filtered_df = filtered_df[filtered_df['Author_Countries'].apply(has_selected_country)]
    
    # Filter by venues
    if selected_venues:
        filtered_df = filtered_df[filtered_df['Conference'].isin(selected_venues)]
    
    # Filter by year range
    if year_min is not None:
        filtered_df = filtered_df[filtered_df['Year'] >= year_min]
    if year_max is not None:
        filtered_df = filtered_df[filtered_df['Year'] <= year_max]
    
    return filtered_df

@app.route('/')
def index():
    """Main page"""
    df = load_data()
    if df.empty:
        return "Error: Could not load data file"
    
    countries = get_unique_countries(df)
    venues = get_unique_venues(df)
    venues_by_subfield = get_venues_by_subfield(df)
    year_min = int(df['Year'].min())
    year_max = int(df['Year'].max())
    
    return render_template('index.html', 
                         countries=countries, 
                         venues=venues,
                         venues_by_subfield=venues_by_subfield,
                         continents=CONTINENTS,
                         year_min=year_min, 
                         year_max=year_max,
                         total_papers=len(df))

@app.route('/search')
def search():
    """API endpoint for searching papers"""
    df = load_data()
    if df.empty:
        return jsonify({'error': 'Could not load data'})
    
    # Get search parameters
    title_search = request.args.get('title', '')
    author_search = request.args.get('author', '')
    selected_countries = request.args.getlist('countries[]')
    selected_venues = request.args.getlist('venues[]')
    year_min = request.args.get('year_min', type=int)
    year_max = request.args.get('year_max', type=int)
    
    # Filter papers
    filtered_df = filter_papers(df, title_search, author_search, selected_countries, 
                               selected_venues, year_min, year_max)
    
    # Convert to list of dictionaries for JSON response
    results = []
    for _, row in filtered_df.iterrows():
        results.append({
            'title': row['Title'],
            'authors': row['Authors'],
            'conference': row['Conference'],
            'year': int(row['Year']),
            'subfield': row['Subfield'],
            'countries': row['Author_Countries'],
            'status': row['Status'],
            'track': row['Track'],
            'citations': int(row['Citations']) if pd.notna(row['Citations']) else 0
        })
    
    return jsonify({
        'results': results,
        'total': len(results)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 