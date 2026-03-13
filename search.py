#!/usr/bin/env python3
"""
🔍 Safe OpenClaw Skills - Omni-Search Utility
A high-speed CLI tool to discover audited, high-quality skills.
"""

import os
import re
import sys
import argparse
from pathlib import Path

# Professional ANSI Colors
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

def get_categories():
    """Returns a list of all category directories."""
    # Exclude internal/config directories
    exclude = {'.git', '.ruff_cache', 'trustskill', '__pycache__'}
    return [d for d in os.listdir('.') if os.path.isdir(d) and d not in exclude]

def extract_metadata(skill_path):
    """Parses the YAML header of a SKILL.md file."""
    try:
        content = skill_path.read_text(encoding='utf-8')
        match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match: return None
        
        header = match.group(1)
        meta = {}
        for key in ['name', 'version', 'description', 'author', 'keywords']:
            val_match = re.search(rf'^{key}:\s*["\']?(.*?)["\']?\s*$', header, re.MULTILINE)
            meta[key] = val_match.group(1).strip() if val_match else ""
        return meta
    except Exception:
        return None

def perform_search(query, category=None):
    """Searches skills for the given query."""
    results = []
    categories = [category] if category else get_categories()
    
    query = query.lower()
    
    for cat in categories:
        cat_path = Path(cat)
        if not cat_path.is_dir(): continue
        
        for skill_dir in cat_path.iterdir():
            if not skill_dir.is_dir(): continue
            
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists(): continue
            
            meta = extract_metadata(skill_md)
            if not meta: continue
            
            # Search in Name, Description, and Keywords
            search_blob = f"{meta['name']} {meta['description']} {meta['keywords']}".lower()
            if query in search_blob:
                results.append({
                    'category': cat,
                    'path': str(skill_dir),
                    'meta': meta
                })
                
    return results

def main():
    parser = argparse.ArgumentParser(description="Search the Safe OpenClaw Skills repository.")
    parser.add_argument("query", help="Keyword to search for (e.g., 'image', 'git', 'weather')")
    parser.add_argument("-c", "--category", help="Filter search by category")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show full metadata snippets")
    
    args = parser.parse_args()
    
    print(f"\n{BOLD}🔍 Searching for '{args.query}'...{RESET}")
    results = perform_search(args.query, args.category)
    
    if not results:
        print(f"{RED}No skills found matching your query.{RESET}")
        return

    print(f"{GREEN}✨ Found {len(results)} high-quality skills:{RESET}\n")
    
    # Sort by category then name
    results.sort(key=lambda x: (x['category'], x['meta']['name']))
    
    current_cat = ""
    for r in results:
        if r['category'] != current_cat:
            current_cat = r['category']
            print(f"{BOLD}{BLUE}[ {current_cat.upper().replace('-', ' ')} ]{RESET}")
        
        name = r['meta']['name'] or Path(r['path']).name
        print(f"  {BOLD}• {name}{RESET}")
        print(f"    {YELLOW}↳ Path:{RESET} {r['path']}")
        
        if args.verbose:
            desc = r['meta']['description']
            if len(desc) > 100: desc = desc[:97] + "..."
            print(f"    {YELLOW}↳ Desc:{RESET} {desc}")
        print()

if __name__ == "__main__":
    main()
