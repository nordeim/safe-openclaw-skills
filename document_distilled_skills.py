import os
import re
from pathlib import Path

# 🛡️ Category Documentation Strategy
# For each category, find all sub-folders with SKILL.md, extract name/desc, and write to category.md

CATEGORY_DIRS = [
    "ai-and-llms", "apple-apps-and-services", "browser-and-automation",
    "calendar-and-scheduling", "clawdbot-tools", "cli-utilities",
    "coding-agents-and-ides", "communication", "data-and-analytics",
    "devops-and-cloud", "gaming", "git-and-github", "health-and-fitness",
    "image-and-video-generation", "ios-and-macos-development", "marketing-and-sales",
    "media-and-streaming", "notes-and-pkm", "pdf-and-documents",
    "personal-development", "productivity-and-tasks", "search-and-research",
    "security-and-passwords", "self-hosted-and-automation", "shopping-and-e-commerce",
    "smart-home-and-iot", "speech-and-transcription", "transportation",
    "web-and-frontend-development"
]

def extract_metadata(skill_path):
    """Extracts name and description from SKILL.md YAML header."""
    try:
        content = skill_path.read_text(encoding='utf-8')
        match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match: return None, None
        
        header = match.group(1)
        name_match = re.search(r'^name:\s*["\']?(.*?)["\']?\s*$', header, re.MULTILINE)
        desc_match = re.search(r'^description:\s*["\']?(.*?)["\']?\s*$', header, re.MULTILINE)
        
        name = name_match.group(1) if name_match else skill_path.parent.name
        description = desc_match.group(1) if desc_match else "No description provided."
        
        # Clean up multi-line descriptions or quoted strings
        description = description.replace('"', '').replace("'", "").strip()
        
        return name, description
    except Exception:
        return None, None

def update_category_files():
    total_documented = 0
    
    for category in CATEGORY_DIRS:
        cat_path = Path(category)
        output_file = Path(f"{category}.md")
        
        if not cat_path.is_dir():
            continue
            
        skills_data = []
        for skill_dir in sorted(cat_path.iterdir()):
            if not skill_dir.is_dir():
                continue
            
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                name, desc = extract_metadata(skill_md)
                if name:
                    # Link to the directory relative to the categories root
                    link = f"./{category}/{skill_dir.name}/SKILL.md"
                    skills_data.append((name, desc, link))
        
        if not skills_data:
            if output_file.exists():
                # If category is empty now, we should still have a clean file stating so
                content = f"# 📁 {category.replace('-', ' ').title()}\n\nNo validated skills remain in this category after rigorous sanitization.\n"
                output_file.write_text(content, encoding='utf-8')
            continue

        # Generate professional Markdown content
        lines = [
            f"# 📁 {category.replace('-', ' ').title()}",
            f"\nThis list contains **{len(skills_data)}** high-quality, audited skills that passed the TrustSkill security and quality protocol.",
            "\n| Skill Name | Description | Link |",
            "| :--- | :--- | :--- |"
        ]
        
        for name, desc, link in skills_data:
            lines.append(f"| **{name}** | {desc} | [View Skill]({link}) |")
            
        output_file.write_text("\n".join(lines), encoding='utf-8')
        print(f"✅ Updated: {output_file} ({len(skills_data)} skills)")
        total_documented += len(skills_data)
        
    return total_documented

if __name__ == "__main__":
    count = update_category_files()
    print(f"\n🚀 Total skills documented across categories: {count}")
