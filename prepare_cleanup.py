import re
import os
from pathlib import Path

# 🛡️ Deletion Strategy
REPORT_FILE = "SECURITY_AUDIT_REPORT.md"
OUTPUT_SCRIPT = "cleanup_skills.sh"

def extract_suspicious_skills():
    """
    Parses the SECURITY_AUDIT_REPORT.md to find all HIGH and MEDIUM risk skills.
    Looks for the pattern: | `category/skill` | 🔴 HIGH | or | `category/skill` | 🟡 MEDIUM |
    """
    suspicious_skills = set()
    
    if not os.path.exists(REPORT_FILE):
        print(f"❌ Error: {REPORT_FILE} not found.")
        return []

    # Regex to capture the skill path between backticks in the first column
    # Matches: | `path/to/skill` | 🔴 HIGH |  OR  | `path/to/skill` | 🟡 MEDIUM |
    pattern = re.compile(r'\|\s*`([^`]+)`\s*\|\s*(?:🔴\s*HIGH|🟡\s*MEDIUM)')

    with open(REPORT_FILE, "r") as f:
        for line in f:
            match = pattern.search(line)
            if match:
                skill_path = match.group(1).strip()
                # Verify the path exists before adding to set
                if os.path.isdir(skill_path):
                    suspicious_skills.add(skill_path)
    
    return sorted(list(suspicious_skills))

def create_cleanup_script(skills):
    """Generates a bash script to remove the identified folders."""
    with open(OUTPUT_SCRIPT, "w") as f:
        f.write("#!/bin/bash\n")
        f.write("# 🛡️ OpenClaw Skills Cleanup Script\n")
        f.write(f"# Generated on: {os.popen('date').read()}\n")
        f.write(f"# Total skills to remove: {len(skills)}\n\n")
        
        for skill in skills:
            # Use quotes to handle any potential spaces in folder names
            f.write(f"rm -rf \"{skill}\"\n")
            
    # Make it executable
    os.chmod(OUTPUT_SCRIPT, 0o755)

def main():
    print("🔍 Extracting suspicious skills from report...")
    skills = extract_suspicious_skills()
    
    if not skills:
        print("✅ No suspicious skills found for deletion.")
        return

    print(f"🚀 Found {len(skills)} unique suspicious/malicious skill directories.")
    create_cleanup_script(skills)
    print(f"✨ Cleanup script created: {OUTPUT_SCRIPT}")
    print("⚠️  Review the script before execution to ensure no safe skills are included.")

if __name__ == "__main__":
    main()
