#!/usr/bin/env python3
"""
Master pipeline script that:
1. Runs all scrappers to collect newsletter and scientific repository data
2. Formats all collected data to a standardized structure
3. Runs ODS analysis on all formatted data
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

# Configuration
SCRAPER_DIR = Path(__file__).parent
DOCUMENTS_DIR = SCRAPER_DIR / "documents"

# Ensure documents directory exists
DOCUMENTS_DIR.mkdir(exist_ok=True)

def run_command(command, description):
    """Run a shell command and report progress"""
    print(f"\n{'='*60}")
    print(f"Starting: {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(command, shell=True, cwd=SCRAPER_DIR)
        if result.returncode == 0:
            print(f" {description} completed successfully")
            return True
        else:
            print(f" {description} failed with return code {result.returncode}")
            return False
    except Exception as e:
        print(f" Error running {description}: {e}")
        return False

def main():
    """Run the complete pipeline"""
    print("\n" + "="*60)
    print("STARTING COMPLETE DATA PIPELINE")
    print("="*60)
    print(f"Start time: {datetime.now().isoformat()}")
    
    steps = [
        ("py scraper_cursos_links.py", "Cursos Links Scraper"),
        ("py scraper_cursos_texto.py", "Cursos Content Scraper"),
        ("py scraper_newsletter_all.py", "Newsletter Links Scraper"),
        ("py scraper_newsletter_each.py", "Newsletter Content Scraper"),
        ("py scraper_repo_cientifico.py", "Scientific Repository Scraper"),
        ("py ./apis/scopus_api_scraper.py", "Scopus API Scraper"),
        ("py format_documents.py", "Document Formatter"),
        ("py eliminate_files.py", "File Eliminator"),
        ("py analyze_ods.py", "ODS Analysis"),
    ]
    
    results = []
    for command, description in steps:
        success = run_command(command, description)
        results.append((description, success))
        if not success:
            print(f"\n Warning: {description} failed, but continuing with pipeline...")
    
    # Print summary
    print("\n" + "="*60)
    print("PIPELINE SUMMARY")
    print("="*60)
    for description, success in results:
        status = " PASSED" if success else " FAILED"
        print(f"{status}: {description}")
    
    print(f"\nEnd time: {datetime.now().isoformat()}")
    
    all_passed = all(success for _, success in results)
    if all_passed:
        print("\n ALL STEPS COMPLETED SUCCESSFULLY!")
        return 0
    else:
        print("\n SOME STEPS FAILED - Review logs above")
        return 1

if __name__ == "__main__":
    sys.exit(main())


