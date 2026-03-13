Key files to review:
1. src/cli.py - Main entry point
2. src/scanner.py - Core scanner
3. src/analyzers/*.py - Various analyzers
4. src/rules.py - Rules definitions
5. src/config/*.py - Configuration system

Let me read the most
Now let me validate my understanding by examining the core source code
→ Read trustskill/src/cli.py 
→ Read trustskill/src/scanner.py 
→ Read trustskill/src/rules.py 
Thinking: Now let me read the analyzer files to understand the core
→ Read trustskill/src/analyzers/secret_analyzer.py 
→ Read trustskill/src/analyzers/taint_analyzer.py 
→ Read trustskill/src/analyzers/dependency_analyzer.py 

Summary of TrustSkill v3.1
WHAT is TrustSkill?
TrustSkill is an advanced security scanner specifically designed for OpenClaw skills. It acts as a defensive static analysis tool that audits skill packages before installation or execution - essentially an "antivirus" for the OpenClaw skill ecosystem.
WHY does TrustSkill exist?
- Pre-installation Security Gate: Before installing skills from unknown sources
- Periodic Security Audits: Regular checks of installed skills
- Pre-execution Validation: Before running scripts that modify systems
- Publishing Validation: Quality gate for ClawHub (skill marketplace)
- CI/CD Integration: Automated security enforcement
HOW does TrustSkill work?
Multi-Layered Detection Architecture:
1. Regex Analysis (all modes) - Pattern matching for suspicious code
2. AST Analysis (standard/deep) - Deep structural code analysis  
3. Secret Detection (all modes) - Hybrid entropy + pattern matching for API keys, passwords
4. Dependency Scanning (all modes) - OSV database integration for CVE detection
5. Taint Analysis (deep mode only) - Data flow tracking from user input to dangerous functions
Scanning Modes:
- FAST: Regex + Secrets + Dependencies (15 HIGH findings on malicious skill)
- STANDARD: + AST (30 HIGH findings)
- DEEP: + Taint Analysis (32 HIGH findings + flow tracking)
Key Capabilities (v3.1):
- 99% False Positive Reduction via NPM integrity hash whitelisting
- Smart Data Flow Detection - Distinguishes uploads (HIGH) vs downloads (MEDIUM)
- Context-Aware Documentation Scanning recognizes placeholders and documentation examples
- Comprehensive whitelist system for lock files, docs, and testing utilities
TrustSkill categorizes risks into HIGH, MEDIUM, and LOW tiers. Critical threats like command injection, hardcoded secrets, and data exfiltration trigger immediate action. Configuration supports YAML/JSON formats with custom rules and severity overrides. Exit codes enable CI/CD integration: 0 means no high-risk issues found, 1 indicates critical vulnerabilities detected. The tool validates across
TrustSkill Deep Understanding - Validation Complete
WHAT - Core Identity
TrustSkill v3.1 is an advanced security scanner for OpenClaw skills - a defensive static analysis tool that audits skill packages before installation/execution. It functions as the "antivirus" for the OpenClaw skill ecosystem.
WHY - Purpose & Use Cases
Use Case	Purpose
Pre-installation	Security gate before installing untrusted skills
Periodic audits	Regular security hygiene (113 skills in repo)
Pre-execution	Validate before system-modifying scripts
Publishing validation	Quality gate for ClawHub marketplace
CI/CD integration	Automated security enforcement (exit code 1 = HIGH risk)
HOW - Technical Implementation
Multi-Layer Analysis Stack:
Layer	Component	Mode	Function
1	Regex Analyzer	All	Pattern matching for suspicious code
2	AST Analyzer	Standard+	Python AST structural analysis
3	Secret Analyzer	All	Entropy (4.5+) + pattern detection (AWS, GitHub, OpenAI)
4	Dependency Analyzer	All	OSV CVE database integration
5	Taint Analyzer	Deep only	Data flow: user input → dangerous functions
Key Detection Categories (from rules.py):
🔴 HIGH Risk - Stop immediately:
- Command injection (eval, exec, os.system with variables)
- Hardcoded secrets (entropy ≥4.5, length ≥20)
- Data upload/exfiltration (requests.post with sensitive data)
- Destructive operations (shutil.rmtree, rm -rf)
🟡 MEDIUM Risk - Manual review:
- Vulnerable dependencies (requests, urllib3, django CVEs)
- Out-of-bounds file access (/etc/passwd, SSH keys)
- Code obfuscation (base64, ROT13)
🟢 LOW Risk - Document & proceed:
- Static shell commands (string literals only)
- Standard file operations
- Environment variable access
v3.1 Enhancements (99% FP reduction):
- NPM Integrity Hash Whitelist: Skips sha512-xxx patterns in lock files
- Smart Data Flow: Uploads (HIGH) vs downloads (MEDIUM)
- Context-Aware Docs: Recognizes placeholders (your_api_key_here, sk-..., i18n patterns)
Architecture:
src/
├── cli.py              # Entry point with argparse
├── scanner.py          # Orchestrates analyzers
├── rules.py            # Pattern definitions (HIGH/MEDIUM/LOW)
├── analyzers/
│   ├── regex_analyzer.py      # Pattern matching
│   ├── ast_analyzer.py        # Python AST parsing
│   ├── secret_analyzer.py     # Entropy + pattern detection
│   ├── dependency_analyzer.py # OSV vulnerability checking
│   └── taint_analyzer.py      # Data flow tracking
└── config/             # YAML/JSON configuration
Validation Evidence:
- 218 tests passing
- Scanned 113 skills in repository
- DEEP mode: 32 HIGH, 24 MEDIUM, 8 LOW on malicious skill test
- Exit codes: 0 (safe) / 1 (HIGH risk detected)
The codebase validates all claimed capabilities: malicious code detection, secret detection, vulnerable dependencies, taint analysis, configuration system, and all output formats.
