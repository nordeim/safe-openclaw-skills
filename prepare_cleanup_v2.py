import re
import os
from pathlib import Path

# 🛡️ Rigorous Deletion Strategy (Round 2)
# Any skill with ANY finding (HIGH, MEDIUM, LOW) is slated for removal.
REPORT_FILE = "SECURITY_AUDIT_REPORT.md"
OUTPUT_SCRIPT = "cleanup_skills_round2.sh"

def extract_all_not_safe():
    """
    Parses the SECURITY_AUDIT_REPORT.md to find all skills NOT marked as Safe.
    Looks for headers like: ### 🔴 `ai-and-llms/agent-sentinel` (HIGH)
    OR ### 🟡 `ai-and-llms/aap-passport` (MEDIUM)
    OR ### 🟢 `ai-and-llms/agent-rpg` (LOW)
    """
    suspicious_skills = set()
    
    if not os.path.exists(REPORT_FILE):
        print(f"❌ Error: {REPORT_FILE} not found.")
        return []

    # Regex to capture the skill path between backticks in the header
    # Matches: ### 🔴 `path/to/skill` (HIGH)
    # OR: ### 🟡 `path/to/skill` (MEDIUM)
    # OR: ### 🟢 `path/to/skill` (LOW)
    header_pattern = re.compile(r'###\s*(?:🔴|🟡|🟢)\s*`([^`]+)`\s*\((?:HIGH|MEDIUM|LOW)\)')

    with open(REPORT_FILE, "r") as f:
        for line in f:
            match = header_pattern.search(line)
            if match:
                skill_path = match.group(1).strip()
                # Verify the path exists before adding to set
                if os.path.isdir(skill_path):
                    suspicious_skills.add(skill_path)
    
    return sorted(list(suspicious_skills))

def create_cleanup_script(skills):
    """Generates a bash script to remove all identified folders."""
    with open(OUTPUT_SCRIPT, "w") as f:
        f.write("#!/bin/bash\n")
        f.write("# 🛡️ OpenClaw Skills Rigorous Cleanup (Round 2)\n")
        f.write(f"# Generated on: {os.popen('date').read()}\n")
        f.write(f"# Total non-safe skills to remove: {len(skills)}\n\n")
        
        for skill in skills:
            # Use quotes to handle any potential spaces in folder names
            f.write(f"rm -rf \"{skill}\"\n")
            
    # Make it executable
    os.chmod(OUTPUT_SCRIPT, 0o755)

def main():
    print("🔍 Extracting all skills with findings (HIGH, MEDIUM, LOW)...")
    skills = extract_all_not_safe()
    
    if not skills:
        print("✅ No non-safe skills found for deletion. All remaining skills are safe!")
        return

    print(f"🚀 Found {len(skills)} unique skill directories with findings.")
    create_cleanup_script(skills)
    print(f"✨ Cleanup script created: {OUTPUT_SCRIPT}")

if __name__ == "__main__":
    main()
