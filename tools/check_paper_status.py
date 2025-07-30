#!/usr/bin/env python3
"""
Paper Status Analysis Tool

This script analyzes the paper statuses in the dataset to understand what types of papers are included.
It checks for rejected, withdrawn, accepted, and other status types to help understand the data quality
and completeness.

USAGE:
    python tools/check_paper_status.py

OUTPUT:
    - Breakdown of all paper statuses in the dataset
    - Analysis of rejected/withdrawn papers
    - Analysis of accepted/published papers
    - Specific analysis for AI-related fields (2015-2024)

AUTHOR: Jonathan Shock
DATE: 2025
"""

import pandas as pd

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

def analyze_paper_statuses(df):
    """
    Analyze the paper statuses in the dataset
    
    Args:
        df (pandas.DataFrame): The complete papers dataset
    """
    
    print("📋 PAPER STATUS ANALYSIS:")
    print("=" * 60)
    
    # Check if Status column exists
    if 'Status' not in df.columns:
        print("❌ No 'Status' column found in the dataset")
        return
    
    # Get unique statuses
    status_counts = df['Status'].value_counts()
    
    print(f"📊 Total papers: {len(df)}")
    print(f"🔍 Unique statuses: {len(status_counts)}")
    print()
    
    print("📈 Status breakdown:")
    print("-" * 40)
    for status, count in status_counts.items():
        percentage = (count / len(df)) * 100
        print(f"{status}: {count} papers ({percentage:.1f}%)")
    
    # Check for rejected papers
    rejected_keywords = ['reject', 'rejected', 'desk reject', 'withdraw', 'withdrawn']
    rejected_papers = []
    
    for status in status_counts.index:
        if status and any(keyword in str(status).lower() for keyword in rejected_keywords):
            rejected_papers.append(status)
    
    if rejected_papers:
        print(f"\n❌ REJECTED PAPERS FOUND:")
        print("-" * 40)
        for status in rejected_papers:
            count = status_counts[status]
            print(f"• {status}: {count} papers")
    else:
        print(f"\n✅ No rejected papers found in the dataset")
    
    # Check for accepted/published papers
    accepted_keywords = ['accept', 'accepted', 'published', 'presented']
    accepted_papers = []
    
    for status in status_counts.index:
        if status and any(keyword in str(status).lower() for keyword in accepted_keywords):
            accepted_papers.append(status)
    
    if accepted_papers:
        print(f"\n✅ ACCEPTED PAPERS FOUND:")
        print("-" * 40)
        for status in accepted_papers:
            count = status_counts[status]
            print(f"• {status}: {count} papers")
    
    # Check for unknown/missing status
    unknown_status = df['Status'].isna().sum()
    if unknown_status > 0:
        print(f"\n❓ UNKNOWN STATUS:")
        print("-" * 40)
        print(f"• Papers with missing status: {unknown_status}")

def analyze_ai_fields_status(df):
    """
    Analyze statuses specifically for AI-related fields (2015-2024)
    
    Args:
        df (pandas.DataFrame): The complete papers dataset
    """
    
    ai_fields = [
        'Artificial Intelligence',
        'Computer Vision and Pattern Recognition', 
        'Robotics',
        'Computational Linguistics'
    ]
    
    print(f"\n🔬 AI FIELDS STATUS ANALYSIS (2015-2024):")
    print("=" * 60)
    
    # Filter for AI fields and temporal period
    ai_df = df[df['Subfield'].isin(ai_fields)]
    temporal_df = ai_df[ai_df['Year'].between(2015, 2024)]
    
    print(f"📊 AI papers (2015-2024): {len(temporal_df)}")
    
    if 'Status' in temporal_df.columns:
        status_counts = temporal_df['Status'].value_counts()
        
        print(f"\n📈 Status breakdown for AI papers:")
        print("-" * 40)
        for status, count in status_counts.items():
            percentage = (count / len(temporal_df)) * 100
            print(f"{status}: {count} papers ({percentage:.1f}%)")
        
        # Check for rejected papers in AI fields
        rejected_keywords = ['reject', 'rejected', 'desk reject', 'withdraw', 'withdrawn']
        rejected_ai_papers = []
        
        for status in status_counts.index:
            if status and any(keyword in str(status).lower() for keyword in rejected_keywords):
                rejected_ai_papers.append(status)
        
        if rejected_ai_papers:
            print(f"\n❌ REJECTED AI PAPERS:")
            print("-" * 40)
            for status in rejected_ai_papers:
                count = status_counts[status]
                print(f"• {status}: {count} papers")
        else:
            print(f"\n✅ No rejected papers found in AI fields")

def main():
    """
    Main function to analyze paper statuses in the dataset
    """
    print("🔍 Checking paper statuses in the dataset...")
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Analyze all paper statuses
    analyze_paper_statuses(df)
    
    # Analyze AI fields specifically
    analyze_ai_fields_status(df)
    
    print(f"\n✅ Analysis complete!")

if __name__ == "__main__":
    main() 