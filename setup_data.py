#!/usr/bin/env python3
"""
Data Setup Script for Paper Search Interface

This script helps users set up their data from Paper Copilot.
Users must obtain the data themselves from https://papercopilot.com
"""

import os
import sys

def check_data_exists():
    """Check if data files exist in the expected locations."""
    conference_dirs = [
        'aaai', 'acl', 'acml', 'acmmm', 'aistats', 'automl', 'coling', 'colm',
        'colt', 'corl', 'cvpr', 'eccv', 'emnlp', 'iccv', 'iclr', 'icml',
        'icra', 'ijcai', 'iros', 'kdd', 'naacl', 'nips', 'rss', 'siggraph',
        'siggraphasia', 'uai', 'wacv', 'www'
    ]
    
    found_dirs = []
    for conf_dir in conference_dirs:
        if os.path.exists(conf_dir) and os.path.isdir(conf_dir):
            json_files = [f for f in os.listdir(conf_dir) if f.endswith('.json')]
            if json_files:
                found_dirs.append((conf_dir, len(json_files)))
    
    return found_dirs

def main():
    print("=" * 60)
    print("PAPER SEARCH INTERFACE - DATA SETUP")
    print("=" * 60)
    print()
    
    # Check for existing data
    found_data = check_data_exists()
    
    if found_data:
        print("✅ Found existing data:")
        total_files = 0
        for conf_dir, file_count in found_data:
            print(f"   {conf_dir}/ - {file_count} JSON files")
            total_files += file_count
        print(f"\nTotal: {total_files} JSON files found")
        print()
        
        # Check if combined CSV exists
        if os.path.exists('all_papers.csv'):
            print("✅ Combined data file (all_papers.csv) exists")
            print("   You can now run: python run.py")
        else:
            print("⚠️  Combined data file not found")
            print("   Run: python tools/combine_papers.py")
    else:
        print("❌ No data files found")
        print()
        print("To set up your data:")
        print()
        print("Option A: Automatic Download (Recommended)")
        print("   Run: python download_data.py")
        print("   This will automatically download all data from Paper Copilot")
        print()
        print("Option B: Manual Download")
        print("   1. Visit https://papercopilot.com")
        print("   2. Download the paper data you want to analyze")
        print("   3. Place the JSON files in the appropriate conference folders")
        print("   4. Run: python tools/combine_papers.py")
        print("   5. Run: python run.py")
        print()
        print("Example folder structure:")
        print("   nips/")
        print("   ├── nips2020.json")
        print("   ├── nips2021.json")
        print("   └── ...")
        print("   icml/")
        print("   ├── icml2020.json")
        print("   └── ...")
    
    print()
    print("=" * 60)
    print("IMPORTANT: Data Usage Rights")
    print("=" * 60)
    print("• All data originates from Paper Copilot")
    print("• Users must comply with Paper Copilot's Terms and Conditions")
    print("• This tool is for personal, non-commercial use only")
    print("• See: https://papercopilot.com/policy/terms-and-conditions/")
    print("=" * 60)

if __name__ == "__main__":
    main() 