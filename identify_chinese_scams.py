import os
import re
from pathlib import Path

# 🛡️ Prohibited Chinese Keywords (Equivalents of the English List)
CHINESE_KEYWORDS = [
    r"加密",          # crypto
    r"挖矿", r"算力",   # mining
    r"支付", r"付款",   # payment/payments
    r"比特币",         # bitcoin
    r"以太坊",         # ethereum
    r"稳定币",         # stablecoin
    r"货币", r"代币",   # currency/token
    r"去中心化", r"金融", # DeFi/decentralized
    r"空投",          # airdrops
    r"钱包",          # wallet
    r"区块链", r"链上",  # blockchain/on-chain
    r"索拉纳"          # Solana
]

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

def find_chinese_scams():
    to_delete = []
    
    # Compile regex for efficiency
    pattern = re.compile("|".join(CHINESE_KEYWORDS))
    
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
                match = pattern.search(content)
                if match:
                    to_delete.append((str(skill_dir), match.group(0)))
            except Exception:
                continue
                
    return to_delete

def main():
    print("🔍 Meticulously scanning for Chinese equivalents of prohibited keywords...")
    scam_skills = find_chinese_scams()
    
    print(f"🚀 Found {len(scam_skills)} unique skill directories containing prohibited Chinese terms.")
    
    with open("cleanup_chinese_scams.sh", "w") as f:
        f.write("#!/bin/bash\n")
        f.write("# 🛡️ OpenClaw Skills Chinese Keyword Cleanup\n")
        f.write(f"# Total folders to remove: {len(scam_skills)}\n\n")
        
        for skill_path, term in scam_skills:
            f.write(f"rm -rf \"{skill_path}\" # Reason: Found prohibited term '{term}'\n")
            
    os.chmod("cleanup_chinese_scams.sh", 0o755)
    print("✨ Cleanup script created: cleanup_chinese_scams.sh")

if __name__ == "__main__":
    main()
