#!/usr/bin/env python3
"""
Flask web application for querying paper data with interactive filters.
"""

from flask import Flask, render_template, request, jsonify, make_response
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
        'Eritrea', 'Eswatini', 'Ethiopia', 'Gabon', 'Gambia', 'Ghana', 'Guinea', 'Guinea-Bissau',
        'Ivory Coast', 'Kenya', 'Lesotho', 'Liberia', 'Libya', 'Madagascar', 'Malawi',
        'Mali', 'Mauritania', 'Mauritius', 'Morocco', 'Mozambique', 'Namibia', 'Niger',
        'Nigeria', 'Rwanda', 'São Tomé and Príncipe', 'Senegal', 'Seychelles',
        'Sierra Leone', 'Somalia', 'South Africa', 'South Sudan', 'Sudan', 'Tanzania',
        'Togo', 'Tunisia', 'Uganda', 'Western Sahara', 'Zambia', 'Zimbabwe'
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
        'Finland', 'France', 'Germany', 'Gibraltar', 'Greece', 'Hungary', 'Iceland', 'Ireland',
        'Italy', 'Kosovo', 'Latvia', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Malta',
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
        'Australia', 'Fiji', 'French Polynesia', 'Kiribati', 'Marshall Islands', 'Micronesia', 'Nauru',
        'New Caledonia', 'New Zealand', 'Palau', 'Papua New Guinea', 'Samoa',
        'Solomon Islands', 'Tonga', 'Tuvalu', 'Vanuatu'
    ]
}

def get_unique_countries(df):
    """Get all unique countries from the dataset"""
    all_countries = []
    for countries_str in df['Author_Countries'].dropna():
        if countries_str and countries_str.strip():
            countries = [c.strip() for c in countries_str.split(',') if c.strip()]
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
                 selected_venues=None, year_min=None, year_max=None, include_rejected=False):
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
            
            countries = [c.strip() for c in countries_str.split(',') if c.strip()]
            
            # Handle name variations
            for country in countries:
                # Check exact match first
                if country in selected_countries:
                    return True
                # Handle variations
                if country == "Kingdom of Saudi Arabia" and "Saudi Arabia" in selected_countries:
                    return True
                if country == "State of Palestine" and "Palestine" in selected_countries:
                    return True
                if country == "Türkiye" and "Turkey" in selected_countries:
                    return True
            
            return False
        
        filtered_df = filtered_df[filtered_df['Author_Countries'].apply(has_selected_country)]
    
    # Filter by venues
    if selected_venues and 'Conference' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Conference'].isin(selected_venues)]
    
    # Filter by year range
    if year_min is not None and 'Year' in filtered_df.columns and not filtered_df.empty:
        filtered_df = filtered_df[filtered_df['Year'] >= year_min]
    if year_max is not None and 'Year' in filtered_df.columns and not filtered_df.empty:
        filtered_df = filtered_df[filtered_df['Year'] <= year_max]
    
    # Filter by status (exclude rejected/withdrawn papers by default)
    if not include_rejected and 'Status' in filtered_df.columns:
        # Define statuses to exclude (rejected, withdrawn, etc.)
        exclude_statuses = ['Reject', 'Withdraw', 'Desk Reject', 'Desk Rejected']
        
        # Filter out papers with excluded statuses
        filtered_df = filtered_df[~filtered_df['Status'].isin(exclude_statuses)]
    
    return filtered_df

def aggregate_counts_by_country(df, selected_countries=None):
    """Aggregate paper counts by country.

    Each paper contributes 1 count to every country listed in Author_Countries.
    Empty or missing countries are ignored unless explicitly included elsewhere.
    """
    if selected_countries is None:
        selected_countries = []
    selected_set = set(selected_countries)
    counts = {}
    if df.empty or 'Author_Countries' not in df.columns:
        return counts
    for countries_str in df['Author_Countries'].dropna():
        if not isinstance(countries_str, str) or not countries_str.strip():
            continue
        for country in [c.strip() for c in countries_str.split(',') if c.strip()]:
            # Only count countries that are selected (if any are provided)
            if selected_set and country not in selected_set:
                continue
            counts[country] = counts.get(country, 0) + 1
    return counts

@app.route('/')
def index():
    """Main page"""
    df = load_data()
    if df.empty:
        return "Error: Could not load data file"
    
    # Use all countries from the hardcoded continent lists instead of just those in the data
    all_countries = []
    for continent_countries in CONTINENTS.values():
        all_countries.extend(continent_countries)
    all_countries = sorted(all_countries)
    
    venues = get_unique_venues(df)
    venues_by_subfield = get_venues_by_subfield(df)
    year_min = int(df['Year'].min())
    year_max = int(df['Year'].max())
    
    response = make_response(render_template('index.html', 
                         countries=all_countries, 
                         venues=venues,
                         venues_by_subfield=venues_by_subfield,
                         continents=CONTINENTS,
                         year_min=year_min, 
                         year_max=year_max,
                         total_papers=len(df)))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/search')
def search():
    """API endpoint for searching papers"""
    df = load_data()
    if df.empty:
        return jsonify({'error': 'Could not load data'})
    
    # Debug: Print DataFrame info
    print(f"DataFrame shape: {df.shape}")
    print(f"DataFrame columns: {df.columns.tolist()}")
    
    # Get search parameters
    title_search = request.args.get('title', '')
    author_search = request.args.get('author', '')
    selected_countries = request.args.getlist('countries[]')
    selected_venues = request.args.getlist('venues[]')
    year_min = request.args.get('year_min', type=int)
    year_max = request.args.get('year_max', type=int)
    include_unknown = request.args.get('include_unknown', type=bool)
    include_rejected = request.args.get('include_rejected', type=bool)
    
    # Debug: Print search parameters
    print(f"Search params - title: '{title_search}', author: '{author_search}', countries: {selected_countries}, venues: {selected_venues}")
    
    # Filter papers
    filtered_df = filter_papers(df, title_search, author_search, selected_countries, 
                               selected_venues, year_min, year_max, include_rejected)
    
    # Handle unknown countries separately
    if include_unknown:
        # Add papers with missing country data
        unknown_papers = df[df['Author_Countries'].isna() | (df['Author_Countries'].astype(str).str.strip() == '')]
        filtered_df = pd.concat([filtered_df, unknown_papers]).drop_duplicates()
    
    # Limit results to prevent performance issues
    max_results = 1000
    total_count = len(filtered_df)
    
    if total_count > max_results:
        filtered_df = filtered_df.head(max_results)
        print(f"Limited results from {total_count} to {max_results}")
    
    # Convert to list of dictionaries for JSON response
    results = []
    try:
        for _, row in filtered_df.iterrows():
            results.append({
                'title': row['Title'] if pd.notna(row['Title']) else '',
                'authors': row['Authors'] if pd.notna(row['Authors']) else '',
                'conference': row['Conference'] if pd.notna(row['Conference']) else '',
                'year': int(row['Year']) if pd.notna(row['Year']) else 0,
                'subfield': row['Subfield'] if pd.notna(row['Subfield']) else '',
                'countries': row['Author_Countries'] if pd.notna(row['Author_Countries']) else '',
                'status': row['Status'] if pd.notna(row['Status']) else '',
                'track': row['Track'] if pd.notna(row['Track']) else '',
                'citations': int(row['Citations']) if pd.notna(row['Citations']) else 0
            })
        print(f"Successfully processed {len(results)} results for search")
    except Exception as e:
        print(f"Error processing results: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error processing results: {str(e)}'})
    
    return jsonify({
        'results': results,
        'total': total_count,
        'displayed': len(results),
        'limited': total_count > max_results
    })

@app.route('/map_data')
def map_data():
    """API endpoint to return aggregated counts by country for the current filters.

    Returns JSON: { counts: { countryName: count, ... }, max: maxCount, filtered_countries: [..] }
    """
    df = load_data()
    if df.empty:
        return jsonify({'error': 'Could not load data'})

    title_search = request.args.get('title', '')
    author_search = request.args.get('author', '')
    selected_countries = request.args.getlist('countries[]')
    selected_venues = request.args.getlist('venues[]')
    year_min = request.args.get('year_min', type=int)
    year_max = request.args.get('year_max', type=int)
    include_unknown = request.args.get('include_unknown', type=bool)
    include_rejected = request.args.get('include_rejected', type=bool)

    filtered_df = filter_papers(df, title_search, author_search, selected_countries,
                                selected_venues, year_min, year_max, include_rejected)

    counts = aggregate_counts_by_country(filtered_df, selected_countries)

    # Ensure selected countries appear even if zero
    if selected_countries:
        for c in selected_countries:
            counts.setdefault(c, 0)

    # Optionally include an 'Unknown' bucket
    if include_unknown:
        unknown_papers = filtered_df[filtered_df['Author_Countries'].isna() | (filtered_df['Author_Countries'].astype(str).str.strip() == '')]
        if not unknown_papers.empty:
            counts['Unknown'] = int(len(unknown_papers))

    max_count = max(counts.values()) if counts else 0
    return jsonify({'counts': counts, 'max': max_count, 'selected_only': bool(selected_countries)})

@app.route('/map')
def map_view():
    """Render the map view template. All filtering is passed via query params and fetched client-side."""
    response = make_response(render_template('map.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/export_csv')
def export_csv():
    """API endpoint for exporting search results to CSV"""
    df = load_data()
    if df.empty:
        return jsonify({'error': 'Could not load data'})
    
    # Get search parameters (same as search endpoint)
    title_search = request.args.get('title', '')
    author_search = request.args.get('author', '')
    selected_countries = request.args.getlist('countries[]')
    selected_venues = request.args.getlist('venues[]')
    year_min = request.args.get('year_min', type=int)
    year_max = request.args.get('year_max', type=int)
    include_unknown = request.args.get('include_unknown', type=bool)
    include_rejected = request.args.get('include_rejected', type=bool)
    
    # Filter papers
    filtered_df = filter_papers(df, title_search, author_search, selected_countries, 
                               selected_venues, year_min, year_max, include_rejected)
    
    # Handle unknown countries separately
    if include_unknown:
        # Add papers with missing country data
        unknown_papers = df[df['Author_Countries'].isna() | (df['Author_Countries'].astype(str).str.strip() == '')]
        filtered_df = pd.concat([filtered_df, unknown_papers]).drop_duplicates()
    
    if filtered_df.empty:
        return jsonify({'error': 'No results to export'})
    
    # Generate filename based on search criteria
    filename_parts = []
    if title_search:
        filename_parts.append(f"title_{title_search[:20]}")
    if author_search:
        filename_parts.append(f"author_{author_search}")
    if selected_countries:
        filename_parts.append(f"countries_{len(selected_countries)}")
    if selected_venues:
        filename_parts.append(f"venues_{len(selected_venues)}")
    if year_min or year_max:
        year_range = f"{year_min or 'all'}-{year_max or 'all'}"
        filename_parts.append(f"years_{year_range}")
    
    if not filename_parts:
        filename_parts.append("all_papers")
    
    filename = f"search_results_{'_'.join(filename_parts)}.csv"
    
    # Create CSV content
    csv_content = filtered_df.to_csv(index=False)
    
    # Create response with CSV file
    response = make_response(csv_content)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 