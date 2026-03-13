import re
from pathlib import Path

def fix_naruto_skill():
    p = Path("web-and-frontend-development/naruto-multi-agent-cn/SKILL.md")
    if not p.exists(): return
    
    content = p.read_text(encoding='utf-8')
    match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match: return
    
    header_raw = match.group(0)
    new_header = header_raw
    
    # Translate keywords
    new_header = new_header.replace("多agent", "multi-agent")
    new_header = new_header.replace("火影忍者", "naruto")
    new_header = new_header.replace("木叶", "konoha")
    new_header = new_header.replace("角色扮演", "roleplay")
    new_header = new_header.replace("调度", "scheduler")
    
    # Translate description part
    new_header = new_header.replace("火影执务室", "Hokage Office")
    
    new_content = content.replace(header_raw, new_header)
    p.write_text(new_content, encoding='utf-8')
    print("✅ Fixed naruto-multi-agent-cn/SKILL.md")

if __name__ == "__main__":
    fix_naruto_skill()
