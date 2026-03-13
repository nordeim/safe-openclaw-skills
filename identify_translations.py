import os
import re
import yaml
from pathlib import Path

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

def contains_non_english(text):
    """Simple check for Chinese characters or other non-Latin scripts."""
    if not text: return False
    # Check for Chinese characters
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def find_skills_needing_translation():
    needs_translation = []
    
    for category in CATEGORY_DIRS:
        cat_path = Path(category)
        if not cat_path.is_dir():
            continue
            
        for skill_dir in cat_path.iterdir():
            if not skill_dir.is_dir():
                continue
            
            upper_skill = skill_dir / "SKILL.md"
            if not upper_skill.exists():
                continue
                
            try:
                content = upper_skill.read_text(encoding='utf-8')
                match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                if match:
                    header_raw = match.group(1)
                    if contains_non_english(header_raw):
                        needs_translation.append(str(upper_skill))
            except Exception:
                continue
                
    return needs_translation

if __name__ == "__main__":
    skills = find_skills_needing_translation()
    print(f"FOUND_SKILLS:{len(skills)}")
    for s in skills:
        print(s)
