import os
import re
from pathlib import Path

# Manual translation mapping for the 15 identified skills to ensure precision
TRANSLATIONS = {
    "ai-and-llms/agent-linguo-xiwan/SKILL.md": {
        "description": "Multilingual translation and language analysis agent.",
        "author": "Xiwan"
    },
    "ai-and-llms/agent-linguo/SKILL.md": {
        "description": "Multilingual translation and language analysis agent.",
        "author": "Xiwan"
    },
    "coding-agents-and-ides/cloudflare-r2/SKILL.md": {
        "description": "Cloudflare R2 storage management skill.",
        "author": "Xiaoyaner"
    },
    "coding-agents-and-ides/cloudflare-r2-xiaoyaner0201/SKILL.md": {
        "description": "Cloudflare R2 storage management skill.",
        "author": "Xiaoyaner"
    },
    "data-and-analytics/douban-sync-skill/SKILL.md": {
        "description": "Synchronize Douban movie and book collections.",
        "author": "OpenClaw Contributor"
    },
    "devops-and-cloud/12306/SKILL.md": {
        "description": "China Railway 12306 ticket inquiry and management.",
        "author": "OpenClaw Contributor"
    },
    "git-and-github/searching-assistant/SKILL.md": {
        "description": "Intelligent searching assistant for Git and GitHub repositories.",
        "author": "OpenClaw Contributor"
    },
    "notes-and-pkm/flomo-notes/SKILL.md": {
        "description": "Sync and manage flomo notes directly from OpenClaw.",
        "author": "OpenClaw Contributor"
    },
    "transportation/daai-xianzun-persona/SKILL.md": {
        "description": "Fang Yuan (Great Love Immortal Venerable) persona simulation.",
        "author": "OpenClaw Contributor"
    },
    "web-and-frontend-development/doubao-image-gen/SKILL.md": {
        "description": "Generate images using Doubao AI models.",
        "author": "OpenClaw Contributor"
    },
    "web-and-frontend-development/minimax-video/SKILL.md": {
        "description": "Video generation and processing using MiniMax models.",
        "author": "OpenClaw Contributor"
    },
    "web-and-frontend-development/zhipu-embeddings-v2/SKILL.md": {
        "description": "Zhipu AI text embedding generation (v2).",
        "author": "OpenClaw Contributor"
    },
    "web-and-frontend-development/zhipu-search/SKILL.md": {
        "description": "Intelligent web search using Zhipu AI Search API.",
        "author": "OpenClaw Contributor"
    },
    "web-and-frontend-development/minimax-tts-v2/SKILL.md": {
        "description": "Text-to-speech synthesis using MiniMax voice models (v2).",
        "author": "OpenClaw Contributor"
    },
    "web-and-frontend-development/naruto-multi-agent-cn/SKILL.md": {
        "description": "Multi-agent simulation of Naruto universe (Chinese language support).",
        "author": "OpenClaw Contributor"
    }
}

def translate_headers():
    for skill_path, tdata in TRANSLATIONS.items():
        p = Path(skill_path)
        if not p.exists(): continue
        
        content = p.read_text(encoding='utf-8')
        # Extract YAML header
        match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match: continue
        
        header_raw = match.group(0)
        new_header = header_raw
        
        # Simple replacement for specific non-English values
        # We replace the values while keeping the keys
        if "description" in tdata:
            # Matches description: "value" or description: value
            new_header = re.sub(r'description:\s*["\']?.*["\']?', f'description: "{tdata["description"]}"', new_header)
        if "author" in tdata:
            new_header = re.sub(r'author:\s*["\']?.*["\']?', f'author: "{tdata["author"]}"', new_header)

        # Update the file
        new_content = content.replace(header_raw, new_header)
        p.write_text(new_content, encoding='utf-8')
        print(f"✅ Translated: {skill_path}")

if __name__ == "__main__":
    translate_headers()
