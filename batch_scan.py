import os
import json
import subprocess
from pathlib import Path
import time

# ⚙️ Audit Configuration
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

TRUSTSKILL_CLI = "trustskill/src/cli.py"
AUDIT_CONFIG = "trustskill_audit.yaml"
VENV_PYTHON = "/opt/venv/bin/python3"

def find_skills():
    """Find all directories containing a SKILL.md file."""
    skills = []
    for category in CATEGORY_DIRS:
        cat_path = Path(category)
        if not cat_path.is_dir():
            continue
            
        for skill_dir in cat_path.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                skills.append(skill_dir)
    return skills

def run_scan(skill_path):
    """Run TrustSkill on a single skill directory."""
    try:
        cmd = [
            VENV_PYTHON, TRUSTSKILL_CLI, str(skill_path),
            "--mode", "deep",
            "--config", AUDIT_CONFIG,
            "--format", "json"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        # If exit code 1, it means HIGH risk found, but it's still valid JSON output usually
        try:
            return json.loads(e.stdout)
        except:
            return {"error": f"Failed to scan {skill_path}: {e.stderr}"}
    except Exception as e:
        return {"error": f"Exception scanning {skill_path}: {str(e)}"}

def generate_report(results):
    """Generate a comprehensive security audit report."""
    report = ["# 🛡️ OpenClaw Skills Security Audit Report", f"**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}", ""]
    
    # Summary Section
    total_skills = len(results)
    skills_with_high = 0
    skills_with_med = 0
    total_findings = 0
    
    for skill_name, data in results.items():
        if "error" in data: continue
        findings = data.get("findings", [])
        total_findings += len(findings)
        if any(f["level"] == "HIGH" for f in findings):
            skills_with_high += 1
        elif any(f["level"] == "MEDIUM" for f in findings):
            skills_with_med += 1
            
    report.append("## 📊 Executive Summary")
    report.append(f"- **Total Skills Scanned**: {total_skills}")
    report.append(f"- **Critical/High Risk Skills**: 🔴 {skills_with_high}")
    report.append(f"- **Medium Risk Skills**: 🟡 {skills_with_med}")
    report.append(f"- **Total Findings**: {total_findings}")
    report.append("")
    
    # Prompt Injection Focus
    report.append("## 🎯 Prompt Injection & Malicious Activity Focus")
    pi_findings = []
    for skill_name, data in results.items():
        if "error" in data: continue
        for f in data.get("findings", []):
            if f["category"] in ["prompt_injection_risk", "tainted_prompt_construction", "command_injection", "data_exfiltration", "openclaw_memory_leak"]:
                pi_findings.append((skill_name, f))
                
    if pi_findings:
        report.append("| Skill | Risk Level | Category | Description |")
        report.append("| :--- | :--- | :--- | :--- |")
        for skill_name, f in pi_findings:
            risk_icon = "🔴" if f["level"] == "HIGH" else "🟡"
            report.append(f"| `{skill_name}` | {risk_icon} {f['level']} | `{f['category']}` | {f['description']} |")
    else:
        report.append("No specific Prompt Injection or Malicious exfiltration patterns detected in this scan.")
    report.append("")
    
    # Detailed Breakdown
    report.append("## 📜 Detailed Skill Breakdown")
    for skill_name, data in sorted(results.items()):
        if "error" in data:
            report.append(f"### ❌ `{skill_name}` (Scan Error)")
            report.append(f"Error: {data['error']}")
            continue
            
        findings = data.get("findings", [])
        if not findings:
            report.append(f"### ✅ `{skill_name}` (Safe)")
            continue
            
        max_severity = "LOW"
        if any(f["level"] == "HIGH" for f in findings): max_severity = "HIGH"
        elif any(f["level"] == "MEDIUM" for f in findings): max_severity = "MEDIUM"
        
        icon = "🔴" if max_severity == "HIGH" else "🟡" if max_severity == "MEDIUM" else "🟢"
        report.append(f"### {icon} `{skill_name}` ({max_severity})")
        
        report.append("| Level | Category | Description | File:Line | Snippet |")
        report.append("| :--- | :--- | :--- | :--- | :--- |")
        for f in findings:
            report.append(f"| {f['level']} | `{f['category']}` | {f['description']} | `{f['file']}:{f['line']}` | `{f['snippet']}` |")
        report.append("")
        
    return "\n".join(report)

def main():
    print("🔍 Discovering skills...")
    skills = find_skills()
    print(f"✅ Found {len(skills)} skills.")
    
    results = {}
    for i, skill_path in enumerate(skills, 1):
        skill_name = f"{skill_path.parent.name}/{skill_path.name}"
        print(f"[{i}/{len(skills)}] Scanning: {skill_name}...", end="\r")
        results[skill_name] = run_scan(skill_path)
    
    print("\n✅ Scan complete. Generating report...")
    report_md = generate_report(results)
    
    with open("SECURITY_AUDIT_REPORT.md", "w") as f:
        f.write(report_md)
    print("🚀 Audit report generated: SECURITY_AUDIT_REPORT.md")

if __name__ == "__main__":
    main()
