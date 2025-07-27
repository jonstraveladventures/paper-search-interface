#!/usr/bin/env python3
"""
Script to find all papers with authors whose surname is "Shock" across all JSON files.
"""

import json
import os
import glob
from pathlib import Path
import re

def extract_year_from_filename(filename):
    """Extract year from filename like 'aistats1997.json' -> 1997"""
    basename = os.path.basename(filename)
    # Remove .json extension
    name_without_ext = basename.replace('.json', '')
    # Extract year (last 4 digits)
    for i in range(len(name_without_ext) - 3):
        potential_year = name_without_ext[i:i+4]
        if potential_year.isdigit() and 1900 <= int(potential_year) <= 2030:
            return int(potential_year)
    return None

def extract_conference_name(folder_path):
    """Extract conference name from folder path"""
    folder_name = os.path.basename(folder_path)
    return folder_name.upper()

def has_shock_author(authors_str):
    """Check if any author has surname 'Shock'"""
    if not authors_str or not authors_str.strip():
        return False
    
    # Split authors by semicolon or comma
    authors = re.split(r'[;,]\s*', authors_str)
    
    for author in authors:
        author = author.strip()
        if not author:
            continue
        
        # Split by spaces and check if any part is "Shock"
        name_parts = author.split()
        for part in name_parts:
            if part.lower() == 'shock':
                return True
    
    return False

def main():
    """Main function to search for Shock papers"""
    
    # Get the root directory (parent of tools folder)
    root_dir = Path(__file__).parent.parent
    
    shock_papers = []
    total_files_processed = 0
    
    print("Searching for papers with authors named 'Shock'...")
    
    # Process each conference folder
    for folder_path in root_dir.iterdir():
        if folder_path.is_dir() and folder_path.name != 'tools':
            conference_name = extract_conference_name(folder_path)
            
            # Find all JSON files in the folder
            json_files = list(folder_path.glob('*.json'))
            
            for json_file in json_files:
                year = extract_year_from_filename(json_file.name)
                if not year:
                    continue
                
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        papers = json.load(f)
                    
                    if not isinstance(papers, list):
                        continue
                    
                    for paper in papers:
                        if isinstance(paper, dict):
                            authors = paper.get('author', '')
                            if has_shock_author(authors):
                                shock_papers.append({
                                    'title': paper.get('title', ''),
                                    'authors': authors,
                                    'conference': conference_name,
                                    'year': year,
                                    'file': json_file.name,
                                    'status': paper.get('status', ''),
                                    'track': paper.get('track', ''),
                                    'citations': paper.get('gs_citation', 0)
                                })
                    
                    total_files_processed += 1
                    
                except json.JSONDecodeError as e:
                    print(f"Error reading {json_file}: {e}")
                except Exception as e:
                    print(f"Error processing {json_file}: {e}")
    
    # Print results
    print(f"\n=== SEARCH RESULTS ===")
    print(f"Total files processed: {total_files_processed}")
    print(f"Papers with 'Shock' authors found: {len(shock_papers)}")
    
    if shock_papers:
        print(f"\n=== PAPERS WITH 'SHOCK' AUTHORS ===")
        for i, paper in enumerate(shock_papers, 1):
            print(f"\n{i}. Title: {paper['title']}")
            print(f"   Authors: {paper['authors']}")
            print(f"   Conference: {paper['conference']} ({paper['year']})")
            print(f"   Status: {paper['status']}")
            print(f"   Track: {paper['track']}")
            print(f"   Citations: {paper['citations']}")
            print(f"   File: {paper['file']}")
        
        # Save to CSV
        import csv
        output_file = root_dir / 'shock_papers.csv'
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Title', 'Authors', 'Conference', 'Year', 'Status', 'Track', 'Citations', 'File']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for paper in shock_papers:
                writer.writerow({
                    'Title': paper['title'],
                    'Authors': paper['authors'],
                    'Conference': paper['conference'],
                    'Year': paper['year'],
                    'Status': paper['status'],
                    'Track': paper['track'],
                    'Citations': paper['citations'],
                    'File': paper['file']
                })
        
        print(f"\nResults saved to: {output_file}")
        
        # Show summary by conference
        print(f"\n=== SUMMARY BY CONFERENCE ===")
        conference_counts = {}
        for paper in shock_papers:
            conf = paper['conference']
            conference_counts[conf] = conference_counts.get(conf, 0) + 1
        
        for conf, count in sorted(conference_counts.items()):
            print(f"  {conf}: {count} papers")
        
        # Show summary by year
        print(f"\n=== SUMMARY BY YEAR ===")
        year_counts = {}
        for paper in shock_papers:
            year = paper['year']
            year_counts[year] = year_counts.get(year, 0) + 1
        
        for year in sorted(year_counts.keys()):
            print(f"  {year}: {year_counts[year]} papers")
    
    else:
        print("No papers with authors named 'Shock' were found.")

if __name__ == "__main__":
    main() 