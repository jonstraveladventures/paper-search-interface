#!/usr/bin/env python3
"""
Demo script showing how to use the Paper Search Interface programmatically
"""

import pandas as pd
import sys
from pathlib import Path

# Add the tools directory to the Python path
tools_dir = Path(__file__).parent / "tools"
sys.path.insert(0, str(tools_dir))

from web_interface import load_data, filter_papers

def demo_search():
    """Demonstrate various search capabilities"""
    
    print("🔍 Paper Search Interface Demo")
    print("=" * 50)
    
    # Load the data
    print("📚 Loading data...")
    df = load_data()
    print(f"✅ Loaded {len(df):,} papers")
    
    # Demo 1: Search by author
    print("\n1️⃣  Searching for papers by 'Marivate'...")
    marivate_papers = filter_papers(df, author_search='Marivate')
    print(f"   Found {len(marivate_papers)} papers by Marivate")
    for _, paper in marivate_papers.head(3).iterrows():
        print(f"   - {paper['Title']} ({paper['Conference']} {paper['Year']})")
    
    print("\n💡 To find papers by any author, use: python tools/find_name_papers.py [name]")
    
    # Demo 2: Search by title keywords
    print("\n2️⃣  Searching for papers with 'reinforcement learning' in title...")
    rl_papers = filter_papers(df, title_search='reinforcement learning')
    print(f"   Found {len(rl_papers)} papers with 'reinforcement learning' in title")
    for _, paper in rl_papers.head(3).iterrows():
        print(f"   - {paper['Title']} ({paper['Conference']} {paper['Year']})")
    
    # Demo 3: Filter by African countries
    print("\n3️⃣  Searching for papers with African country affiliations...")
    african_countries = ['South Africa', 'Nigeria', 'Kenya', 'Egypt', 'Ghana']
    african_papers = filter_papers(df, selected_countries=african_countries)
    print(f"   Found {len(african_papers)} papers with African country affiliations")
    for _, paper in african_papers.head(3).iterrows():
        print(f"   - {paper['Title']} ({paper['Conference']} {paper['Year']})")
    
    # Demo 4: Filter by venue
    print("\n4️⃣  Searching for papers from NIPS conference...")
    nips_papers = filter_papers(df, selected_venues=['NIPS'])
    print(f"   Found {len(nips_papers)} papers from NIPS")
    
    # Demo 5: Filter by year range
    print("\n5️⃣  Searching for recent papers (2020-2024)...")
    recent_papers = filter_papers(df, year_min=2020, year_max=2024)
    print(f"   Found {len(recent_papers):,} papers from 2020-2024")
    
    # Demo 6: Combined search
    print("\n6️⃣  Combined search: Recent AI papers with 'transformer' in title...")
    combined_papers = filter_papers(
        df, 
        title_search='transformer',
        selected_venues=['NIPS', 'ICLR', 'ICML'],
        year_min=2020,
        year_max=2024
    )
    print(f"   Found {len(combined_papers)} recent AI papers with 'transformer' in title")
    for _, paper in combined_papers.head(3).iterrows():
        print(f"   - {paper['Title']} ({paper['Conference']} {paper['Year']})")
    
    print("\n🎉 Demo complete!")
    print("💡 Try the web interface for interactive searching:")
    print("   python run.py")

if __name__ == "__main__":
    demo_search() 