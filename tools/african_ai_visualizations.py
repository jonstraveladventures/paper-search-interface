#!/usr/bin/env python3
"""
African AI-related Research Visualizations

This script creates comprehensive visualizations for AI-related research coming out of Africa,
providing insights into research trends, collaborations, and impact.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter, defaultdict
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

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
    """Load and prepare African papers data"""
    df = pd.read_csv('african_papers.csv')
    # Filter to include only papers up to 2024
    df = df[df['Year'] <= 2024]
    print(f"📊 Loaded {len(df)} African papers (up to 2024)")
    return df

def create_publication_trends(df):
    """Create publication trends over time"""
    plt.figure(figsize=(12, 6))
    
    # Count papers by year
    year_counts = df['Year'].value_counts().sort_index()
    
    # Create the plot
    plt.plot(year_counts.index, year_counts.values, marker='o', linewidth=3, markersize=8)
    plt.fill_between(year_counts.index, year_counts.values, alpha=0.3)
    
    plt.title('African AI-related Research: Publication Trends Over Time (1995-2024)', fontsize=16, fontweight='bold')
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Number of Papers', fontsize=12)
    plt.grid(True, alpha=0.3)
    

    
    plt.tight_layout()
    plt.savefig('tools/img/african_publication_trends.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_research_areas(df):
    """Create research areas/subfields visualization"""
    plt.figure(figsize=(14, 12))
    
    # Count papers by subfield
    subfield_counts = df['Subfield'].value_counts()
    
    # Create pie chart
    colors = plt.cm.Set3(np.linspace(0, 1, len(subfield_counts)))
    wedges, texts, autotexts = plt.pie(subfield_counts.values, 
                                       labels=subfield_counts.index,
                                       autopct='%1.1f%%',
                                       colors=colors,
                                       startangle=90,
                                       textprops={'fontsize': 18})
    
    # Make percentage labels bold
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(16)
    
    plt.title('African AI-related Research: Distribution by Research Area (2024 and earlier)', 
              fontsize=24, fontweight='bold', pad=20)
    
    # Add legend with counts
    legend_labels = [f'{area}: {count} papers' for area, count in subfield_counts.items()]
    legend = plt.legend(wedges, legend_labels, title="Research Areas", 
                       loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=16, title_fontsize=18)
    legend.get_title().set_fontweight('bold')
    
    plt.tight_layout()
    plt.savefig('tools/img/african_research_areas.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_conference_analysis(df):
    """Create conference/venue analysis"""
    plt.figure(figsize=(12, 8))
    
    # Count papers by conference
    conference_counts = df['Conference'].value_counts().head(15)
    
    # Create bar chart
    colors = plt.cm.viridis(np.linspace(0, 1, len(conference_counts)))
    bars = plt.bar(range(len(conference_counts)), conference_counts.values, color=colors)
    
    plt.xticks(range(len(conference_counts)), conference_counts.index, rotation=45, ha='right', fontsize=10)
    plt.ylabel('Number of Papers', fontsize=12)
    plt.title('African AI-related Research: Top Conferences/Journals (1995-2024)', fontsize=16, fontweight='bold')
    
    # Add value labels
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig('tools/img/african_conferences.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_country_analysis(df):
    """Create country-wise analysis"""
    plt.figure(figsize=(16, 10))
    
    # Extract countries from Author_Countries column
    all_countries = []
    for countries_str in df['Author_Countries'].dropna():
        countries = [c.strip() for c in str(countries_str).split(';') if c.strip()]
        all_countries.extend(countries)
    
    # Filter for African countries only
    african_countries = [country for country in all_countries if country in AFRICAN_COUNTRIES]
    
    # Count papers by country
    country_counts = Counter(african_countries)
    top_countries = dict(sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:15])
    
    # Create horizontal bar chart
    colors = plt.cm.RdYlBu_r(np.linspace(0, 1, len(top_countries)))
    bars = plt.barh(range(len(top_countries)), list(top_countries.values()), color=colors)
    
    plt.yticks(range(len(top_countries)), list(top_countries.keys()), fontsize=18)
    plt.xlabel('Number of Papers', fontsize=20, fontweight='bold')
    plt.title('African AI-related Research: Papers by African Country', fontsize=24, fontweight='bold', pad=20)
    
    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                f'{width}', ha='left', va='center', fontweight='bold', fontsize=16)
    
    plt.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    plt.savefig('tools/img/african_countries.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_country_temporal_analysis(df):
    """Create stacked bar chart showing publications by country over the last 10 years"""
    plt.figure(figsize=(18, 12))

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

    # Filter to last 10 years and get top African countries
    recent_df = df_temp[df_temp['Year'].isin(years)]
    recent_df = recent_df[recent_df['Primary_Country'] != 'Unknown']  # Remove papers without African countries
    top_countries = recent_df['Primary_Country'].value_counts().head(15).index

    # Create data for stacked bar chart
    country_data = {}
    for country in top_countries:
        country_data[country] = []
        for year in years:
            count = len(recent_df[(recent_df['Primary_Country'] == country) & (recent_df['Year'] == year)])
            country_data[country].append(count)

    # Create stacked bar chart
    x = np.arange(len(top_countries))
    width = 0.8

    # Create a more appealing color palette - red to blue to green progression
    colors = plt.cm.RdYlBu_r(np.linspace(0.1, 0.9, len(years)))

    # Plot stacked bars
    bottom = np.zeros(len(top_countries))
    for i, year in enumerate(years):
        values = [country_data[country][i] for country in top_countries]
        plt.bar(x, values, width, bottom=bottom, label=str(year), color=colors[i], alpha=0.9, edgecolor='white', linewidth=0.5)
        bottom += values

    # Customize the plot with better styling
    plt.xlabel('Country', fontsize=16, fontweight='bold')
    plt.ylabel('Number of Publications', fontsize=16, fontweight='bold')
    plt.title('African AI-related Research: Publications by African Country (Last 10 Years)', 
              fontsize=20, fontweight='bold', pad=20)
    plt.xticks(x, top_countries, rotation=45, ha='right', fontsize=14)

    # Add legend with better styling
    legend = plt.legend(title='Year', bbox_to_anchor=(1.02, 1), loc='upper left', 
                       fontsize=12, title_fontsize=14, frameon=True, 
                       fancybox=True, shadow=True)
    legend.get_title().set_fontweight('bold')

    # Add value labels on bars with better styling
    for i, country in enumerate(top_countries):
        total = sum(country_data[country])
        if total > 0:  # Only add labels for countries with publications
            plt.text(i, total + 0.3, str(total), ha='center', va='bottom', 
                    fontweight='bold', fontsize=12, color='darkred')

    # Add grid with better styling
    plt.grid(True, alpha=0.4, axis='y', linestyle='--', linewidth=0.8)
    
    # Set background color and improve overall appearance
    plt.gca().set_facecolor('#f8f9fa')
    plt.gcf().set_facecolor('white')
    
    # Adjust layout to prevent cutoff
    plt.tight_layout()
    plt.subplots_adjust(right=0.85)  # Make room for legend
    
    plt.savefig('tools/img/african_country_temporal.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.show()

def create_research_evolution(df):
    """Create research evolution analysis"""
    plt.figure(figsize=(16, 8))
    
    # Create subplots
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
    
    # Plot 1: Research areas over time
    pivot_subfield = df.groupby(['Year', 'Subfield']).size().unstack(fill_value=0)
    pivot_subfield.plot(kind='line', marker='o', ax=ax1)
    ax1.set_title('Research Areas Evolution Over Time', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('Number of Papers', fontsize=12)
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Conference trends over time
    top_conferences = df['Conference'].value_counts().head(8).index
    pivot_conf = df[df['Conference'].isin(top_conferences)].groupby(['Year', 'Conference']).size().unstack(fill_value=0)
    pivot_conf.plot(kind='line', marker='s', ax=ax2)
    ax2.set_title('Conference Participation Over Time', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Year', fontsize=12)
    ax2.set_ylabel('Number of Papers', fontsize=12)
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Country participation over time
    # Extract primary country for each paper
    primary_countries = []
    for countries_str in df['Author_Countries']:
        countries = [c.strip() for c in str(countries_str).split(';') if c.strip()]
        # Filter for African countries only
        african_countries = [country for country in countries if country in AFRICAN_COUNTRIES]
        primary_countries.append(african_countries[0] if african_countries else 'Unknown')
    
    df_temp = df.copy()
    df_temp['Primary_Country'] = primary_countries
    
    # Filter for African countries only
    df_temp = df_temp[df_temp['Primary_Country'] != 'Unknown']
    top_countries = df_temp['Primary_Country'].value_counts().head(8).index
    pivot_country = df_temp[df_temp['Primary_Country'].isin(top_countries)].groupby(['Year', 'Primary_Country']).size().unstack(fill_value=0)
    pivot_country.plot(kind='line', marker='^', ax=ax3)
    ax3.set_title('African Country Participation Over Time', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Year', fontsize=12)
    ax3.set_ylabel('Number of Papers', fontsize=12)
    ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax3.grid(True, alpha=0.3)
    
    plt.suptitle('African AI-related Research: Evolution Analysis', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('tools/img/african_evolution.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_summary_statistics(df):
    """Create summary statistics dashboard"""
    print("\n" + "="*60)
    print("AFRICAN AI-RELATED RESEARCH: SUMMARY STATISTICS")
    print("="*60)
    
    # Basic statistics
    print(f"\n📊 Total Papers: {len(df)}")
    print(f"📅 Year Range: {df['Year'].min()} - {df['Year'].max()}")
    # Count African countries represented
    all_countries = set([c.strip() for countries in df['Author_Countries'].dropna() for c in str(countries).split(';') if c.strip()])
    african_countries_represented = len(all_countries.intersection(AFRICAN_COUNTRIES))
    print(f"🌍 African Countries Represented: {african_countries_represented}")
    print(f"🎯 Research Areas: {len(df['Subfield'].unique())}")
    print(f"🏛️ Conferences/Journals: {len(df['Conference'].unique())}")
    
    # Top statistics
    print(f"\n🏆 TOP RESEARCH AREAS:")
    for area, count in df['Subfield'].value_counts().head(5).items():
        print(f"   • {area}: {count} papers")
    
    print(f"\n🏆 TOP AFRICAN COUNTRIES:")
    all_countries = []
    for countries_str in df['Author_Countries'].dropna():
        countries = [c.strip() for c in str(countries_str).split(';') if c.strip()]
        all_countries.extend(countries)
    
    # Filter for African countries only
    african_countries = [country for country in all_countries if country in AFRICAN_COUNTRIES]
    
    for country, count in Counter(african_countries).most_common(5):
        print(f"   • {country}: {count} papers")
    
    print(f"\n🏆 TOP CONFERENCES:")
    for conf, count in df['Conference'].value_counts().head(5).items():
        print(f"   • {conf}: {count} papers")
    
    # Citation statistics
    cited_papers = df[df['Citations'] > 0]
    print(f"\n📈 CITATION STATISTICS:")
    print(f"   • Papers with citations: {len(cited_papers)} ({len(cited_papers)/len(df)*100:.1f}%)")
    print(f"   • Total citations: {df['Citations'].sum()}")
    print(f"   • Average citations (cited papers): {cited_papers['Citations'].mean():.1f}")
    print(f"   • Median citations (cited papers): {cited_papers['Citations'].median():.1f}")
    
    # Recent trends
    recent_papers = df[df['Year'] >= 2020]
    print(f"\n📈 RECENT TRENDS (2020-2024):")
    print(f"   • Papers since 2020: {len(recent_papers)} ({len(recent_papers)/len(df)*100:.1f}%)")
    print(f"   • Growth rate: {len(recent_papers)/5:.1f} papers/year")
    
    print("\n" + "="*60)

def main():
    """Main function to generate all visualizations"""
    print("🎨 Creating African AI-related Research Visualizations...")
    
    # Load data
    df = load_african_data()
    
    # Create output directory if it doesn't exist
    import os
    os.makedirs('tools/img', exist_ok=True)
    
    # Generate all visualizations
    print("\n📈 Generating publication trends...")
    create_publication_trends(df)
    
    print("\n🔬 Generating research areas analysis...")
    create_research_areas(df)
    
    print("\n🏛️ Generating conference analysis...")
    create_conference_analysis(df)
    
    print("\n🌍 Generating country analysis...")
    create_country_analysis(df)
    
    print("\n📈 Generating country temporal analysis...")
    create_country_temporal_analysis(df)

    
    print("\n📈 Generating research evolution...")
    create_research_evolution(df)
    
    print("\n📋 Generating summary statistics...")
    create_summary_statistics(df)
    
    print("\n✅ All visualizations completed!")
    print("📁 Images saved in: tools/img/")
    print("\nGenerated files:")
    print("   • african_publication_trends.png")
    print("   • african_research_areas.png")
    print("   • african_conferences.png")
    print("   • african_countries.png")
    print("   • african_country_temporal.png")
    print("   • african_evolution.png")

if __name__ == "__main__":
    main() 