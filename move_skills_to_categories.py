#!/usr/bin/env python3
"""
OpenClaw Skills Organizer
Moves skills from temp clone to category folders based on markdown listings
"""

import re
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Configuration
SCRIPT_DIR = Path(__file__).parent
TEMP_SKILLS_DIR = (
    SCRIPT_DIR / "temp_cloned_skils_to_scan_before_select_relevant" / "skills"
)

# Counters
TOTAL_CATEGORIES = 0
TOTAL_SKILLS_FOUND = 0
SKILLS_COPIED = 0
SKILLS_SKIPPED = 0
SKILLS_NOT_FOUND = 0
SKILLS_CONFLICT = 0

# Track moved skills to avoid duplicates
MOVED_SKILLS = {}  # key: author/repo -> target path


def log_info(msg):
    print(f"\033[0;34m[INFO]\033[0m {msg}")


def log_success(msg):
    print(f"\033[0;32m[OK]\033[0m {msg}")


def log_warning(msg):
    print(f"\033[1;33m[WARN]\033[0m {msg}")


def log_error(msg):
    print(f"\033[0;31m[ERROR]\033[0m {msg}")


def sanitize_name(name):
    """Sanitize folder name for filesystem."""
    # Convert to lowercase
    name = name.lower()
    # Replace non-alphanumeric characters with dashes
    sanitized = re.sub(r"[^a-z0-9._-]", "-", name)
    # Remove leading/trailing dashes
    sanitized = sanitized.strip("-")
    return sanitized


def find_unique_name(target_dir, base_name, author):
    """Find unique name if conflict exists."""
    final_name = base_name
    counter = 1

    # If name exists, try with author prefix
    target_path = target_dir / final_name
    if target_path.exists():
        final_name = f"{base_name}-{author}"
        target_path = target_dir / final_name

        # If still exists, add counter
        while target_path.exists():
            final_name = f"{base_name}-{author}-{counter}"
            target_path = target_dir / final_name
            counter += 1

    return final_name


def parse_markdown(md_file):
    """Parse markdown file to extract skill entries."""
    skills = []

    # Pattern to match skill entries:
    # - [skill-name](https://github.com/openclaw/skills/tree/main/skills/author/skill-name/SKILL.md)
    pattern = r"^\s*-\s*\[([^\]]+)\]\(https://github\.com/openclaw/skills/tree/main/skills/([^/]+)/([^/]+)/SKILL\.md"

    try:
        with open(md_file, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("["):
                    continue

                match = re.match(pattern, line)
                if match:
                    skill_name = match.group(1).strip()
                    author = match.group(2).strip()
                    skill_repo = match.group(3).strip()

                    skills.append(
                        {
                            "name": skill_name,
                            "author": author,
                            "repo": skill_repo,
                            "line_num": line_num,
                        }
                    )
    except Exception as e:
        log_error(f"Error reading {md_file}: {e}")

    return skills


def process_category(md_file):
    """Process a single category markdown file."""
    global \
        TOTAL_SKILLS_FOUND, \
        SKILLS_COPIED, \
        SKILLS_SKIPPED, \
        SKILLS_NOT_FOUND, \
        SKILLS_CONFLICT

    category_name = md_file.stem
    category_folder = SCRIPT_DIR / category_name

    log_info("=" * 60)
    log_info(f"Processing: {category_name}")
    log_info("=" * 60)

    # Create category folder
    category_folder.mkdir(parents=True, exist_ok=True)

    # Parse markdown for skills
    skills = parse_markdown(md_file)

    if not skills:
        log_info(f"No skills found in {md_file.name}")
        return

    log_info(f"Found {len(skills)} skills in {category_name}")

    category_skills = 0
    category_copied = 0
    category_not_found = 0
    category_conflict = 0

    for skill_info in skills:
        skill_name = skill_info["name"]
        author = skill_info["author"]
        skill_repo = skill_info["repo"]

        TOTAL_SKILLS_FOUND += 1
        category_skills += 1

        # Sanitize skill name for folder
        skill_folder_name = sanitize_name(skill_name)

        # Source folder in temp
        source_folder = TEMP_SKILLS_DIR / author / skill_repo

        # Check if source exists
        if not source_folder.exists():
            log_error(f"NOT FOUND: {skill_name} (author: {author}, repo: {skill_repo})")
            SKILLS_NOT_FOUND += 1
            category_not_found += 1
            continue

        # Find unique target name
        target_name = find_unique_name(category_folder, skill_folder_name, author)
        target_path = category_folder / target_name

        # Check if this exact skill (by author/repo) was already moved
        skill_key = f"{author}/{skill_repo}"
        if skill_key in MOVED_SKILLS:
            log_warning(
                f"SKIPPED (duplicate): {skill_name} (already in {MOVED_SKILLS[skill_key]})"
            )
            SKILLS_SKIPPED += 1
            continue

        # Check if this is a rename
        if target_name != skill_folder_name:
            log_info(f"RENAME: {skill_name} -> {target_name} (conflict resolved)")
            SKILLS_CONFLICT += 1
            category_conflict += 1

        # Copy the skill folder
        try:
            shutil.copytree(source_folder, target_path, symlinks=True)
            log_success(f"COPIED: {skill_name} -> {category_name}/{target_name}")
            SKILLS_COPIED += 1
            category_copied += 1

            # Track this move
            MOVED_SKILLS[skill_key] = f"{category_name}/{target_name}"
        except Exception as e:
            log_error(f"FAILED: {skill_name} (copy failed: {e})")
            SKILLS_NOT_FOUND += 1
            category_not_found += 1

    log_info(
        f"Category stats: {category_skills} skills, {category_copied} copied, "
        f"{category_not_found} not found, {category_conflict} renamed"
    )


def main():
    """Main entry point."""
    global TOTAL_CATEGORIES

    print("=" * 60)
    print("OpenClaw Skills Organizer")
    print("=" * 60)
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Source: {TEMP_SKILLS_DIR}")
    print()

    # Check if temp directory exists
    if not TEMP_SKILLS_DIR.exists():
        log_error(f"Temp skills directory not found: {TEMP_SKILLS_DIR}")
        sys.exit(1)

    # Count available skills
    available_skills = len([d for d in TEMP_SKILLS_DIR.rglob("*") if d.is_dir()])
    log_info(f"Available skill directories in temp folder: {available_skills}")
    print()

    # Find all markdown files
    categories = []
    for md_file in SCRIPT_DIR.glob("*.md"):
        # Skip special files
        if md_file.name in ["AGENTS.md", "README.md"]:
            continue
        categories.append(md_file)

    TOTAL_CATEGORIES = len(categories)

    if TOTAL_CATEGORIES == 0:
        log_error("No category markdown files found!")
        sys.exit(1)

    log_info(f"Found {TOTAL_CATEGORIES} categories to process")
    print()

    # Process each category
    for md_file in sorted(categories):
        process_category(md_file)
        print()

    # Summary
    print("=" * 60)
    print("ORGANIZATION SUMMARY")
    print("=" * 60)
    print(f"Total categories processed: {TOTAL_CATEGORIES}")
    print(f"Total skills found in markdowns: {TOTAL_SKILLS_FOUND}")
    print(f"Successfully copied: {SKILLS_COPIED}")
    print(f"Skipped (duplicates): {SKILLS_SKIPPED}")
    print(f"Not found: {SKILLS_NOT_FOUND}")
    print(f"Renamed (conflicts): {SKILLS_CONFLICT}")
    print()
    print(f"Completed: {datetime.now().isoformat()}")
    print("=" * 60)

    # Save report
    import json

    report_file = SCRIPT_DIR / "organization_report.json"
    with open(report_file, "w") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_categories": TOTAL_CATEGORIES,
                    "total_skills_found": TOTAL_SKILLS_FOUND,
                    "skills_copied": SKILLS_COPIED,
                    "skills_skipped": SKILLS_SKIPPED,
                    "skills_not_found": SKILLS_NOT_FOUND,
                    "skills_renamed": SKILLS_CONFLICT,
                },
                "moved_skills": MOVED_SKILLS,
            },
            f,
            indent=2,
        )

    log_info(f"Report saved to: {report_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
