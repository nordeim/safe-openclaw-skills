import os
import re
from pathlib import Path

# 🛡️ Expanded Prohibited Chinese Keywords
CHINESE_KEYWORDS = [
    r"加密", r"虚拟货币", r"数字货币", r"数字资产", # crypto/virtual/digital currency
    r"挖矿", r"矿机", r"算力", r"矿场",             # mining
    r"支付", r"付款", r"缴费", r"结算",             # payment/payments
    r"比特", r"比特币", r"BTC",                    # bitcoin
    r"以太", r"以太坊", r"ETH",                    # ethereum
    r"稳定币", r"USDT", r"USDC",                  # stablecoin
    r"货币", r"代币", r"Token",                   # currency/token
    r"去中心化", r"金融", r"DeFi", r"理财",         # DeFi/finance/wealth mgt
    r"空投", r"Airdrop",                          # airdrops
    r"钱包", r"Wallet",                           # wallet
    r"区块链", r"链上", r"公链",                   # blockchain/on-chain
    r"索拉纳", r"Solana",                         # Solana
    r"合约", r"智能合约",                         # contract/smart contract
    r"投机", r"炒作",                             # speculation/hype
    r"银行", r"转账", r"汇款"                      # bank/transfer/remittance
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
    # Use ignore case for mixed English/Chinese terms
    pattern = re.compile("|".join(CHINESE_KEYWORDS), re.IGNORECASE)
    
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
    print("🔍 Meticulously scanning with EXPANDED Chinese prohibited keywords...")
    scam_skills = find_chinese_scams()
    
    print(f"🚀 Found {len(scam_skills)} unique skill directories containing prohibited terms.")
    
    with open("cleanup_chinese_scams_v2.sh", "w") as f:
        f.write("#!/bin/bash\n")
        f.write("# 🛡️ OpenClaw Skills Chinese Keyword Cleanup (Expanded)\n")
        f.write(f"# Total folders to remove: {len(scam_skills)}\n\n")
        
        for skill_path, term in scam_skills:
            f.write(f"rm -rf \"{skill_path}\" # Reason: Found prohibited term '{term}'\n")
            
    os.chmod("cleanup_chinese_scams_v2.sh", 0o755)
    print("✨ Cleanup script created: cleanup_chinese_scams_v2.sh")

if __name__ == "__main__":
    main()
