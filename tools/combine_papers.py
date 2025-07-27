#!/usr/bin/env python3
"""
Script to combine all paper data from JSON files across all conference folders
into a single CSV file with standardized columns.
"""

import json
import csv
import os
import glob
from pathlib import Path

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

def get_subfield(conference_name):
    """Determine subfield based on conference name"""
    conference_name = conference_name.upper()
    
    # Artificial Intelligence
    if conference_name in ['NIPS', 'NEURIPS', 'ICLR', 'ICML', 'AAAI', 'IJCAI', 'AISTATS', 'CORL', 'ACML']:
        return 'Artificial Intelligence'
    
    # Computational Linguistics
    elif conference_name in ['ACL', 'EMNLP', 'NAACL', 'COLING', 'ARR', 'COLM']:
        return 'Computational Linguistics'
    
    # Computer Graphics
    elif conference_name in ['SIGGRAPH', 'SIGGRAPHASIA', 'EUROGRAPHICS']:
        return 'Computer Graphics'
    
    # Computer networks and wireless communication
    elif conference_name in ['SITCOM']:
        return 'Computer Networks and Wireless Communication'
    
    # Computer vision and pattern recognition
    elif conference_name in ['CVPR', 'ICCV', 'WACV', 'BMVC', '3DV']:
        return 'Computer Vision and Pattern Recognition'
    
    # Data mining and analysis
    elif conference_name in ['KDD']:
        return 'Data Mining and Analysis'
    
    # Databases and information systems
    elif conference_name in ['WWW', 'SIGIR']:
        return 'Databases and Information Systems'
    
    # Multimedia
    elif conference_name in ['ACMMM']:
        return 'Multimedia'
    
    # Robotics
    elif conference_name in ['ICRA', 'IROS', 'RSS']:
        return 'Robotics'
    
    # Default case
    else:
        return 'Other'

def clean_text(text):
    """Clean and normalize text fields"""
    if not text:
        return ""
    # Remove extra whitespace and normalize
    return " ".join(text.split())

def process_paper(paper, conference_name, year):
    """Process a single paper entry and extract required fields"""
    
    # Title
    title = clean_text(paper.get('title', ''))
    
    # Year
    paper_year = year
    
    # Conference/Journal name
    conference = conference_name
    
    # Subfield
    subfield = get_subfield(conference_name)
    
    # Authors
    authors = clean_text(paper.get('author', ''))
    
    # Author institutions
    institutions = clean_text(paper.get('aff', ''))
    
    # Author countries
    countries = clean_text(paper.get('aff_country_unique', ''))
    
    # Status
    status = clean_text(paper.get('status', ''))
    
    # Track
    track = clean_text(paper.get('track', ''))
    
    # Citations
    citations = paper.get('gs_citation', 0)
    if citations == -1:  # Some files use -1 for unknown citations
        citations = 0
    
    return {
        'Title': title,
        'Year': paper_year,
        'Conference': conference,
        'Subfield': subfield,
        'Authors': authors,
        'Author_Institutions': institutions,
        'Author_Countries': countries,
        'Status': status,
        'Track': track,
        'Citations': citations
    }

def main():
    """Main function to process all JSON files and create CSV"""
    
    # Get the root directory (parent of tools folder)
    root_dir = Path(__file__).parent.parent
    
    # Define output CSV file
    output_file = root_dir / 'all_papers.csv'
    
    # CSV headers
    headers = [
        'Title', 'Year', 'Conference', 'Subfield', 'Authors', 'Author_Institutions',
        'Author_Countries', 'Status', 'Track', 'Citations'
    ]
    
    total_papers = 0
    processed_files = 0
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        
        # Process each conference folder
        for folder_path in root_dir.iterdir():
            if folder_path.is_dir() and folder_path.name != 'tools':
                conference_name = extract_conference_name(folder_path)
                print(f"Processing {conference_name}...")
                
                # Find all JSON files in the folder
                json_files = list(folder_path.glob('*.json'))
                
                for json_file in json_files:
                    year = extract_year_from_filename(json_file.name)
                    if not year:
                        print(f"Warning: Could not extract year from {json_file.name}")
                        continue
                    
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            papers = json.load(f)
                        
                        if not isinstance(papers, list):
                            print(f"Warning: {json_file} does not contain a list of papers")
                            continue
                        
                        for paper in papers:
                            if isinstance(paper, dict):
                                processed_paper = process_paper(paper, conference_name, year)
                                writer.writerow(processed_paper)
                                total_papers += 1
                        
                        processed_files += 1
                        
                    except json.JSONDecodeError as e:
                        print(f"Error reading {json_file}: {e}")
                    except Exception as e:
                        print(f"Error processing {json_file}: {e}")
    
    print(f"\nProcessing complete!")
    print(f"Processed {processed_files} files")
    print(f"Total papers: {total_papers}")
    print(f"Output file: {output_file}")

if __name__ == "__main__":
    main() 