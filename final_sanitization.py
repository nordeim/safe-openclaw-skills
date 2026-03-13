import os
import re
from pathlib import Path
from langdetect import detect, detect_langs, DetectorFactory

# 🛡️ Final Sanitization Strategy
# 1. Rename skill.md -> SKILL.md
# 2. Delete folders without valid SKILL.md (must have YAML header ---)
# 3. Delete folders with SKILL.md in non-English/non-Chinese languages.

# Ensure consistent results from langdetect
DetectorFactory.seed = 42

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

OUTPUT_SCRIPT = "cleanup_final_sanitization.sh"

def is_english_or_chinese(content):
    """Detects if content is English or Chinese (Simple/Traditional)."""
    # Remove YAML header and markdown formatting for cleaner detection
    clean_content = re.sub(r'---.*?---', '', content, flags=re.DOTALL)
    clean_content = re.sub(r'#|`|\*|_|\[|\]|\(|\)', '', clean_content)
    clean_content = clean_content.strip()

    if len(clean_content) < 10:
        # Heuristic for very short content: Check for Chinese characters
        if re.search(r'[\u4e00-\u9fff]', clean_content):
            return True
        # Check for Latin characters
        if re.search(r'[a-zA-Z]', clean_content):
            return True
        return False

    try:
        langs = detect_langs(clean_content)
        for l in langs:
            # en, zh-cn, zh-tw are allowed
            if l.lang in ['en', 'zh-cn', 'zh-tw']:
                return True
        return False
    except:
        # Fallback to regex check for safety
        if re.search(r'[\u4e00-\u9fff]', clean_content):
            return True
        if re.search(r'[a-zA-Z]', clean_content):
            return True
        return False

def has_valid_yaml_header(content):
    """Checks if content starts with a valid YAML header."""
    return content.strip().startswith('---') and '---' in content.strip()[3:1000]

def process_skills():
    to_delete = []
    renamed_count = 0
    
    for category in CATEGORY_DIRS:
        cat_path = Path(category)
        if not cat_path.is_dir():
            continue
            
        for skill_dir in cat_path.iterdir():
            if not skill_dir.is_dir():
                continue
            
            # 1. Standardize: rename skill.md to SKILL.md
            lower_skill = skill_dir / "skill.md"
            upper_skill = skill_dir / "SKILL.md"
            
            if lower_skill.exists() and not upper_skill.exists():
                lower_skill.rename(upper_skill)
                renamed_count += 1
            elif lower_skill.exists() and upper_skill.exists():
                lower_skill.unlink() # Keep the uppercase one

            # 2. Validation: check for SKILL.md
            if not upper_skill.exists():
                to_delete.append((str(skill_dir), "No SKILL.md"))
                continue
                
            try:
                content = upper_skill.read_text(encoding='utf-8')
            except Exception as e:
                to_delete.append((str(skill_dir), f"Read Error: {str(e)}"))
                continue
            
            # 3. Header Validation
            if not has_valid_yaml_header(content):
                to_delete.append((str(skill_dir), "Invalid YAML header"))
                continue
                
            # 4. Language Validation
            if not is_english_or_chinese(content):
                to_delete.append((str(skill_dir), "Non-English/Non-Chinese language detected"))
                continue
                
    return to_delete, renamed_count

def main():
    print("🔍 Meticulously scanning skills for standardization and language filtering...")
    to_delete, renamed_count = process_skills()
    
    print(f"✅ Standardization: Renamed {renamed_count} files to SKILL.md")
    print(f"🚀 Found {len(to_delete)} unique skill directories for final cleanup.")
    
    with open(OUTPUT_SCRIPT, "w") as f:
        f.write("#!/bin/bash\n")
        f.write("# 🛡️ OpenClaw Skills Final Sanitization Script\n")
        f.write(f"# Total non-compliant skills to remove: {len(to_delete)}\n\n")
        
        for skill_path, reason in to_delete:
            f.write(f"rm -rf \"{skill_path}\" # Reason: {reason}\n")
            
    os.chmod(OUTPUT_SCRIPT, 0o755)
    print(f"✨ Final cleanup script created: {OUTPUT_SCRIPT}")

if __name__ == "__main__":
    main()
