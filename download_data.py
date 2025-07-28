#!/usr/bin/env python3
"""
Data Download Script for Paper Search Interface

This script automatically downloads paper data from Paper Copilot
and organizes it into the correct folder structure.
"""

import os
import sys
import requests
import zipfile
import json
from pathlib import Path
from urllib.parse import urljoin

# Paper Copilot base URL
PAPER_COPILOT_BASE = "https://papercopilot.com"

# Conference folders and their expected files
CONFERENCES = {
    'aaai': ['aaai2021.json', 'aaai2022.json', 'aaai2023.json', 'aaai2024.json', 'aaai2025.json'],
    'acl': ['acl2021.json', 'acl2022.json', 'acl2023.json', 'acl2024.json'],
    'acml': ['acml2010.json', 'acml2011.json', 'acml2012.json', 'acml2013.json', 'acml2014.json', 
             'acml2015.json', 'acml2016.json', 'acml2017.json', 'acml2018.json', 'acml2019.json',
             'acml2020.json', 'acml2021.json', 'acml2022.json', 'acml2023.json', 'acml2024.json'],
    'acmmm': ['acmmm2024.json'],
    'aistats': ['aistats1995.json', 'aistats1997.json', 'aistats1999.json', 'aistats2001.json',
                'aistats2003.json', 'aistats2005.json', 'aistats2007.json', 'aistats2009.json',
                'aistats2010.json', 'aistats2011.json', 'aistats2012.json', 'aistats2013.json',
                'aistats2014.json', 'aistats2015.json', 'aistats2016.json', 'aistats2017.json',
                'aistats2018.json', 'aistats2019.json', 'aistats2020.json', 'aistats2021.json',
                'aistats2022.json', 'aistats2023.json', 'aistats2024.json', 'aistats2025.json'],
    'automl': ['automl2022.json', 'automl2023.json', 'automl2024.json'],
    'coling': ['coling2020.json', 'coling2022.json', 'coling2024.json', 'coling2025.json'],
    'colm': ['colm2024.json'],
    'colt': ['colt2011.json', 'colt2012.json', 'colt2013.json', 'colt2014.json', 'colt2015.json',
             'colt2016.json', 'colt2017.json', 'colt2018.json', 'colt2019.json', 'colt2020.json',
             'colt2021.json', 'colt2022.json', 'colt2023.json', 'colt2024.json'],
    'corl': ['corl2021.json', 'corl2022.json', 'corl2023.json', 'corl2024.json'],
    'cvpr': ['cvpr2013.json', 'cvpr2014.json', 'cvpr2015.json', 'cvpr2016.json', 'cvpr2017.json',
             'cvpr2018.json', 'cvpr2019.json', 'cvpr2020.json', 'cvpr2021.json', 'cvpr2022.json',
             'cvpr2023.json', 'cvpr2024.json', 'cvpr2025.json'],
    'eccv': ['eccv2018.json', 'eccv2020.json', 'eccv2022.json', 'eccv2024.json'],
    'emnlp': ['emnlp2021.json', 'emnlp2022.json', 'emnlp2023.json', 'emnlp2024.json'],
    'iccv': ['iccv2013.json', 'iccv2015.json', 'iccv2017.json', 'iccv2019.json', 'iccv2021.json',
             'iccv2023.json', 'iccv2025.json'],
    'iclr': ['iclr2013.json', 'iclr2014.json', 'iclr2017.json', 'iclr2018.json', 'iclr2019.json',
             'iclr2020.json', 'iclr2021.json', 'iclr2022.json', 'iclr2023.json', 'iclr2024.json',
             'iclr2025.json'],
    'icml': ['icml2013.json', 'icml2014.json', 'icml2015.json', 'icml2016.json', 'icml2017.json',
             'icml2018.json', 'icml2019.json', 'icml2020.json', 'icml2021.json', 'icml2022.json',
             'icml2023.json', 'icml2024.json', 'icml2025.json'],
    'icra': ['icra2000.json', 'icra2001.json', 'icra2002.json', 'icra2003.json', 'icra2004.json',
             'icra2005.json', 'icra2006.json', 'icra2007.json', 'icra2008.json', 'icra2009.json',
             'icra2010.json', 'icra2011.json', 'icra2012.json', 'icra2013.json', 'icra2014.json',
             'icra2015.json', 'icra2016.json', 'icra2017.json', 'icra2018.json', 'icra2019.json',
             'icra2020.json', 'icra2021.json', 'icra2022.json', 'icra2023.json', 'icra2024.json'],
    'ijcai': ['ijcai2020.json', 'ijcai2021.json', 'ijcai2022.json', 'ijcai2023.json', 'ijcai2024.json'],
    'iros': ['iros2000.json', 'iros2001.json', 'iros2002.json', 'iros2003.json', 'iros2004.json',
             'iros2005.json', 'iros2006.json', 'iros2007.json', 'iros2008.json', 'iros2009.json',
             'iros2010.json', 'iros2011.json', 'iros2012.json', 'iros2013.json', 'iros2014.json',
             'iros2015.json', 'iros2016.json', 'iros2017.json', 'iros2018.json', 'iros2019.json',
             'iros2020.json', 'iros2021.json', 'iros2022.json', 'iros2023.json', 'iros2024.json'],
    'kdd': ['kdd2023.json', 'kdd2024.json'],
    'naacl': ['naacl2021.json', 'naacl2022.json', 'naacl2024.json', 'naacl2025.json'],
    'nips': ['nips1987.json', 'nips1988.json', 'nips1989.json', 'nips1990.json', 'nips1991.json',
             'nips1992.json', 'nips1993.json', 'nips1994.json', 'nips1995.json', 'nips1996.json',
             'nips1997.json', 'nips1998.json', 'nips1999.json', 'nips2000.json', 'nips2001.json',
             'nips2002.json', 'nips2003.json', 'nips2004.json', 'nips2005.json', 'nips2006.json',
             'nips2007.json', 'nips2008.json', 'nips2009.json', 'nips2010.json', 'nips2011.json',
             'nips2012.json', 'nips2013.json', 'nips2014.json', 'nips2015.json', 'nips2016.json',
             'nips2017.json', 'nips2018.json', 'nips2019.json', 'nips2020.json', 'nips2021.json',
             'nips2022.json', 'nips2023.json', 'nips2024.json'],
    'rss': ['rss2005.json', 'rss2006.json', 'rss2007.json', 'rss2008.json', 'rss2009.json',
            'rss2010.json', 'rss2011.json', 'rss2012.json', 'rss2013.json', 'rss2014.json',
            'rss2015.json', 'rss2016.json', 'rss2017.json', 'rss2018.json', 'rss2019.json',
            'rss2020.json', 'rss2021.json', 'rss2022.json', 'rss2023.json', 'rss2024.json',
            'rss2025.json'],
    'siggraph': ['siggraph2010.json', 'siggraph2011.json', 'siggraph2012.json', 'siggraph2013.json',
                 'siggraph2014.json', 'siggraph2015.json', 'siggraph2016.json', 'siggraph2017.json',
                 'siggraph2018.json', 'siggraph2019.json', 'siggraph2020.json', 'siggraph2021.json',
                 'siggraph2022.json', 'siggraph2023.json', 'siggraph2024.json'],
    'siggraphasia': ['siggraphasia2018.json', 'siggraphasia2019.json', 'siggraphasia2020.json',
                     'siggraphasia2021.json', 'siggraphasia2022.json', 'siggraphasia2023.json',
                     'siggraphasia2024.json'],
    'uai': ['uai2019.json', 'uai2020.json', 'uai2021.json', 'uai2022.json', 'uai2023.json', 'uai2024.json'],
    'wacv': ['wacv2020.json', 'wacv2021.json', 'wacv2022.json', 'wacv2023.json', 'wacv2024.json', 'wacv2025.json'],
    'www': ['www2024.json']
}

def create_folder_structure():
    """Create the folder structure for conferences."""
    print("📁 Creating folder structure...")
    for conference in CONFERENCES.keys():
        Path(conference).mkdir(exist_ok=True)
    print("✅ Folder structure created")

def download_file(url, filepath):
    """Download a single file from Paper Copilot."""
    try:
        print(f"📥 Downloading {filepath}...")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Downloaded {filepath}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to download {filepath}: {e}")
        return False

def download_conference_data(conference, files):
    """Download all files for a specific conference."""
    print(f"\n🎯 Downloading {conference.upper()} data...")
    success_count = 0
    
    for filename in files:
        # Construct the URL for Paper Copilot
        url = f"{PAPER_COPILOT_BASE}/data/{conference}/{filename}"
        filepath = Path(conference) / filename
        
        if download_file(url, filepath):
            success_count += 1
    
    print(f"📊 {conference.upper()}: {success_count}/{len(files)} files downloaded")
    return success_count, len(files)

def download_all_data():
    """Download all conference data."""
    print("🚀 Starting data download from Paper Copilot...")
    print("=" * 60)
    
    create_folder_structure()
    
    total_success = 0
    total_files = 0
    
    for conference, files in CONFERENCES.items():
        success, total = download_conference_data(conference, files)
        total_success += success
        total_files += total
    
    print("\n" + "=" * 60)
    print(f"📊 DOWNLOAD SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully downloaded: {total_success}/{total_files} files")
    print(f"📁 Conferences: {len(CONFERENCES)}")
    print(f"📄 Total files: {total_files}")
    
    if total_success > 0:
        print(f"\n🎉 Data download completed!")
        print(f"💡 Next steps:")
        print(f"   1. Run: python tools/combine_papers.py")
        print(f"   2. Run: python run.py")
        print(f"   3. Open: http://localhost:5001")
    else:
        print(f"\n⚠️  No files were downloaded successfully.")
        print(f"💡 Please check your internet connection and try again.")

def check_existing_data():
    """Check what data already exists."""
    print("🔍 Checking existing data...")
    existing_data = {}
    
    for conference, files in CONFERENCES.items():
        existing_files = []
        for filename in files:
            if Path(conference) / filename:
                existing_files.append(filename)
        if existing_files:
            existing_data[conference] = existing_files
    
    if existing_data:
        print("📁 Found existing data:")
        for conference, files in existing_data.items():
            print(f"   {conference}/ - {len(files)} files")
        
        response = input("\n❓ Some data already exists. Download again? (y/N): ")
        if response.lower() != 'y':
            print("⏭️  Skipping download. Using existing data.")
            return False
    
    return True

def main():
    """Main function."""
    print("=" * 60)
    print("PAPER SEARCH INTERFACE - DATA DOWNLOADER")
    print("=" * 60)
    print()
    print("⚠️  IMPORTANT: Data Usage Rights")
    print("• All data originates from Paper Copilot")
    print("• Users must comply with Paper Copilot's Terms and Conditions")
    print("• This tool is for personal, non-commercial use only")
    print("• See: https://papercopilot.com/policy/terms-and-conditions/")
    print()
    
    # Check if user wants to proceed
    response = input("❓ Do you agree to the terms and want to download data? (y/N): ")
    if response.lower() != 'y':
        print("⏭️  Download cancelled.")
        return
    
    # Check existing data
    if not check_existing_data():
        return
    
    # Download data
    download_all_data()

if __name__ == "__main__":
    main() 