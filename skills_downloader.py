#!/usr/bin/env python3
"""
OpenClaw Skills Downloader & Security Scanner
Pulls skills from category markdown files into corresponding folders
"""

import re
import os
import subprocess
import sys
import json
from pathlib import Path
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from datetime import datetime

# Configuration
CATEGORIES_DIR = Path(__file__).parent
MAX_WORKERS = 8
TIMEOUT = 120  # seconds for git clone

# Thread-safe printing
print_lock = threading.Lock()


def safe_print(msg):
    with print_lock:
        print(msg, flush=True)


def parse_markdown_for_skills(md_file_path: Path) -> list:
    """
    Parse markdown file to extract skill names and GitHub URLs.

    Pattern: - [skill-name](https://github.com/openclaw/skills/tree/main/skills/author/skill-name/SKILL.md)
    """
    skills = []

    if not md_file_path.exists():
        safe_print(f"  ❌ File not found: {md_file_path}")
        return skills

    # Pattern to match skill entries
    # Format: - [name](url) - description or - [name](url)
    pattern = r"^\s*-\s*\[([^\]]+)\]\(([^\)]+)\)(?:\s*-\s*(.+))?$"

    try:
        with open(md_file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("["):
                    continue

                match = re.match(pattern, line)
                if match:
                    skill_name = match.group(1).strip()
                    skill_url = match.group(2).strip()
                    description = match.group(3).strip() if match.group(3) else ""

                    # Convert tree URL to raw repo URL for cloning
                    if "github.com/openclaw/skills/tree/main/skills/" in skill_url:
                        # Extract author and skill name from URL
                        # URL format: https://github.com/openclaw/skills/tree/main/skills/author/skill-name/SKILL.md
                        parts = skill_url.split("/skills/tree/main/skills/")
                        if len(parts) == 2:
                            repo_path = parts[1].replace("/SKILL.md", "")
                            # Construct clone URL
                            clone_url = f"https://github.com/openclaw/skills.git"
                            skills.append(
                                {
                                    "name": skill_name,
                                    "clone_url": clone_url,
                                    "sub_path": f"skills/{repo_path}",
                                    "description": description,
                                    "line_num": line_num,
                                }
                            )
    except Exception as e:
        safe_print(f"  ❌ Error reading {md_file_path}: {e}")

    return skills


def clone_skill(skill_info: dict, category_folder: Path) -> dict:
    """
    Clone a skill repository into the category folder using sparse checkout.

    Args:
        skill_info: Dictionary with skill details
        category_folder: Path to the category folder

    Returns:
        Result dictionary with status and details
    """
    skill_name = skill_info["name"]
    sub_path = skill_info["sub_path"]
    clone_url = skill_info["clone_url"]

    # Create skill folder path
    skill_folder = category_folder / skill_name

    result = {
        "name": skill_name,
        "sub_path": sub_path,
        "target_folder": str(skill_folder),
        "status": "pending",
        "error": None,
    }

    try:
        # Check if already exists
        if skill_folder.exists():
            result["status"] = "skipped"
            result["error"] = "Already exists"
            return result

        # Create parent directory
        skill_folder.parent.mkdir(parents=True, exist_ok=True)

        # Clone using sparse checkout to get only the specific skill
        # This is more efficient than cloning the entire repo
        temp_clone = skill_folder.with_suffix(".temp")

        # Clone with --depth 1 --filter=blob:none for efficiency
        clone_cmd = [
            "git",
            "clone",
            "--depth",
            "1",
            "--filter=blob:none",
            "--sparse",
            clone_url,
            str(temp_clone),
        ]

        subprocess.run(clone_cmd, capture_output=True, text=True, timeout=TIMEOUT)

        if not temp_clone.exists():
            result["status"] = "failed"
            result["error"] = "Clone failed - temp folder not created"
            return result

        # Initialize sparse checkout and checkout the specific path
        subprocess.run(
            ["git", "-C", str(temp_clone), "sparse-checkout", "set", sub_path],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Pull the specific path
        subprocess.run(
            ["git", "-C", str(temp_clone), "checkout"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Move the skill folder to destination
        source_folder = temp_clone / sub_path
        if source_folder.exists():
            # If the source exists, move it
            skill_folder.mkdir(parents=True, exist_ok=True)

            # Move contents
            for item in source_folder.iterdir():
                dest = skill_folder / item.name
                if not dest.exists():
                    subprocess.run(["mv", str(item), str(dest)], capture_output=True)

            result["status"] = "success"
        else:
            result["status"] = "failed"
            result["error"] = f"Source path not found: {source_folder}"

        # Cleanup temp clone
        if temp_clone.exists():
            subprocess.run(["rm", "-rf", str(temp_clone)], capture_output=True)

    except subprocess.TimeoutExpired:
        result["status"] = "failed"
        result["error"] = f"Timeout after {TIMEOUT}s"
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)

    return result


def download_category_skills(
    category_name: str, category_folder: Path, md_file: Path
) -> dict:
    """Download all skills for a category."""
    safe_print(f"\n📁 Processing category: {category_name}")
    safe_print(f"   Markdown: {md_file.name}")
    safe_print(f"   Target folder: {category_folder}")

    # Parse markdown for skills
    skills = parse_markdown_for_skills(md_file)

    if not skills:
        safe_print(f"   ℹ️  No skills found in {md_file.name}")
        return {
            "category": category_name,
            "total_skills": 0,
            "downloaded": 0,
            "failed": 0,
            "skipped": 0,
            "errors": [],
        }

    safe_print(f"   📊 Found {len(skills)} skills")

    # Create category folder
    category_folder.mkdir(parents=True, exist_ok=True)

    results = []
    downloaded = 0
    failed = 0
    skipped = 0
    errors = []

    # Download skills in parallel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_skill = {
            executor.submit(clone_skill, skill, category_folder): skill
            for skill in skills
        }

        for future in as_completed(future_to_skill):
            result = future.result()
            results.append(result)

            skill_name = result["name"]
            status = result["status"]

            if status == "success":
                downloaded += 1
                safe_print(f"   ✅ {skill_name}")
            elif status == "skipped":
                skipped += 1
                safe_print(f"   ⏭️  {skill_name} (already exists)")
            else:
                failed += 1
                errors.append(f"{skill_name}: {result['error']}")
                safe_print(f"   ❌ {skill_name}: {result['error']}")

    return {
        "category": category_name,
        "total_skills": len(skills),
        "downloaded": downloaded,
        "failed": failed,
        "skipped": skipped,
        "errors": errors,
    }


def get_category_mapping() -> dict:
    """Get mapping of markdown files to category folder names."""
    mapping = {}

    for md_file in CATEGORIES_DIR.glob("*.md"):
        # Skip special files
        if md_file.name in ["AGENTS.md", "README.md"]:
            continue

        # Convert filename to folder name
        # e.g., ai-and-llms.md -> ai-and-llms
        folder_name = md_file.stem
        mapping[folder_name] = md_file

    return mapping


def main():
    """Main entry point."""
    safe_print("=" * 70)
    safe_print("🔧 OpenClaw Skills Downloader")
    safe_print("=" * 70)
    safe_print(f"Started: {datetime.now().isoformat()}")
    safe_print(f"Categories directory: {CATEGORIES_DIR}")
    safe_print("")

    # Get category mapping
    categories = get_category_mapping()

    if not categories:
        safe_print("❌ No category markdown files found!")
        sys.exit(1)

    safe_print(f"Found {len(categories)} categories to process:")
    for name, md_file in sorted(categories.items()):
        safe_print(f"  • {name} -> {md_file.name}")

    # Process each category
    all_results = []
    total_downloaded = 0
    total_failed = 0
    total_skipped = 0

    for category_name, md_file in sorted(categories.items()):
        category_folder = CATEGORIES_DIR / category_name
        result = download_category_skills(category_name, category_folder, md_file)
        all_results.append(result)

        total_downloaded += result["downloaded"]
        total_failed += result["failed"]
        total_skipped += result["skipped"]

    # Summary
    safe_print("\n" + "=" * 70)
    safe_print("📊 DOWNLOAD SUMMARY")
    safe_print("=" * 70)
    safe_print(f"Total categories processed: {len(categories)}")
    safe_print(f"Total skills downloaded: {total_downloaded}")
    safe_print(f"Total skills skipped (already exist): {total_skipped}")
    safe_print(f"Total failures: {total_failed}")
    safe_print(f"Completed: {datetime.now().isoformat()}")

    # Detailed breakdown
    safe_print("\n📋 Category Breakdown:")
    for result in all_results:
        if result["total_skills"] > 0:
            safe_print(
                f"  • {result['category']}: {result['downloaded']} downloaded, "
                f"{result['skipped']} skipped, {result['failed']} failed"
            )

    # Save report
    report_file = CATEGORIES_DIR / "download_report.json"
    with open(report_file, "w") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_categories": len(categories),
                    "total_downloaded": total_downloaded,
                    "total_failed": total_failed,
                    "total_skipped": total_skipped,
                },
                "details": all_results,
            },
            f,
            indent=2,
        )

    safe_print(f"\n📝 Report saved to: {report_file}")

    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
