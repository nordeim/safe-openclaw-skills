# 🍊 Safe OpenClaw Skills

[![Audit Passed](https://img.shields.io/badge/Audit-Passed-brightgreen.svg)](https://github.com/nordeim/safe-openclaw-skills/blob/main/OPENCLAW_SKILLS_SANITIZATION_REPORT.md)
[![Skills Count](https://img.shields.io/badge/Skills-~1000-orange.svg)](./)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Sanitized](https://img.shields.io/badge/Sanitized-EN/ZH-blueviolet.svg)](./)

> **The Elite, Hardened Ecosystem of OpenClaw Skills.**  
> Meticulously audited, sanitized, and distilled from over 6,700 candidates into a core of ~1,000 high-quality, verified skills.

---

## 🎯 WHAT is this?

This repository is a **curated and hardened distribution** of OpenClaw skills. It is the result of a massive security operation to identify and eliminate high-risk vulnerabilities, prompt injection vectors, and scam-related content from the OpenClaw ecosystem.

Every skill in this repository has passed through the **TrustSkill v3.1** multi-layered security engine, ensuring it is safe for installation and execution in sensitive environments.

---

## 🛡️ WHY does it exist?

Standard skill repositories are often filled with unvetted code. During our audit of the original 6,718 skills, we discovered and purged:
- **🔴 1,301 High-Risk Vulnerabilities**: Including command injection and data exfiltration.
- **🟡 1,775 Medium-Risk Findings**: Including insecure credential handling and obfuscated code.
- **📉 3,000+ "Distortion" Skills**: Purged all content related to crypto, mining, DeFi, and unauthorized payment processing.
- **🌍 Language Sanitization**: Only **English and Chinese** skills remain, ensuring 100% human-auditability.

This repo exists to provide a **Zero-Finding** baseline for OpenClaw users who value security and professional engineering standards.

---

## ⚙️ HOW to use it?

### 1. 🔍 Fast Omni-Search
Use our built-in search utility to discover relevant skills across all categories.

```bash
# Search by keyword (e.g., 'image')
python3 search.py "image"

# Search within a specific category with verbose output
python3 search.py "git" -c "git-and-github" -v
```

### 2. 📂 Browse Categories
Explore the distilled collections by category. Each category file contains a verified list of skills with deep-links to their implementation.

| Category | Skills Count | Link |
| :--- | :---: | :--- |
| **Coding Agents & IDEs** | 234 | [Browse](./coding-agents-and-ides.md) |
| **Web & Frontend Dev** | 138 | [Browse](./web-and-frontend-development.md) |
| **Browser & Automation** | 80 | [Browse](./browser-and-automation.md) |
| **AI & LLMs** | 44 | [Browse](./ai-and-llms.md) |
| **DevOps & Cloud** | 44 | [Browse](./devops-and-cloud.md) |
| **Search & Research** | 56 | [Browse](./search-and-research.md) |
| **Communication** | 20 | [Browse](./communication.md) |
| **Security & Passwords** | 9 | [Browse](./security-and-passwords.md) |

*(See all 29 categories in the sidebar)*

---

## 🛠️ The Sanitization Protocol

We applied a **Meticulous Engineering Approach** to ensure repository integrity:
1.  **TrustSkill v3.1 Deep Scan**: AST analysis and Taint Analysis (Source-to-Sink tracking).
2.  **Linguistic Filtering**: Automated language detection to remove non-EN/ZH scripts.
3.  **Metadata Standardization**: Renamed all files to `SKILL.md` and enforced strict English YAML headers.
4.  **Keyword Purge**: Rigorous regex-based removal of scam-adjacent terminology (Crypto, DeFi, Payments).

For the full technical breakdown, see the [**Sanitization & Security Protocol Report**](./OPENCLAW_SKILLS_SANITIZATION_REPORT.md).

---

## 📜 License & Governance

- **MIT License**: All original scripts and documentation are licensed under MIT.
- **Security First**: This is a defensive fork focused on system integrity.
- **Audit Methodology**: Powered by the **TrustSkill v3.1** engine.

---

**Built with Precision by Gemini CLI - Senior Frontend Architect & Security Partner.**
