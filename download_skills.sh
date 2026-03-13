#!/bin/bash
#
# OpenClaw Skills Downloader
# Downloads skills from category markdown files into corresponding folders
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMEOUT=120

# Counters
TOTAL_CATEGORIES=0
TOTAL_SKILLS=0
DOWNLOADED=0
FAILED=0
SKIPPED=0

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to extract skills from markdown file
parse_markdown() {
    local md_file="$1"
    local category_name="$2"
    local category_folder="$3"
    
    log_info "Parsing: $md_file"
    
    # Pattern to match skill entries:
    # - [skill-name](https://github.com/openclaw/skills/tree/main/skills/author/skill-name/SKILL.md)
    grep -E '^\s*-\s*\[[^\]]+\]\(https://github\.com/openclaw/skills/tree/main/skills/[^/]+/[^/]+/SKILL\.md\)' "$md_file" 2>/dev/null | while IFS= read -r line; do
        # Extract skill name and URL
        skill_name=$(echo "$line" | sed -n 's/.*\[\([^]]*\)\].*/\1/p')
        skill_url=$(echo "$line" | sed -n 's/.*(\([^)]*\)).*/\1/p')
        
        # Extract author and repo name from URL
        # URL format: https://github.com/openclaw/skills/tree/main/skills/author/skill-name/SKILL.md
        if [[ "$skill_url" =~ github\.com/openclaw/skills/tree/main/skills/([^/]+)/([^/]+) ]]; then
            author="${BASH_REMATCH[1]}"
            repo_name="${BASH_REMATCH[2]}"
            
            # Skip empty entries
            if [[ -z "$skill_name" || -z "$author" || -z "$repo_name" ]]; then
                continue
            fi
            
            # Create skill folder
            skill_folder="$category_folder/$skill_name"
            
            # Check if already exists
            if [[ -d "$skill_folder" ]]; then
                log_warning "SKIPPED: $skill_name (already exists)"
                ((SKIPPED++))
                continue
            fi
            
            # Create folder
            mkdir -p "$skill_folder"
            
            # Download the SKILL.md file directly
            raw_url="https://raw.githubusercontent.com/openclaw/skills/main/skills/$author/$repo_name/SKILL.md"
            
            log_info "Downloading: $skill_name"
            
            if curl -sL --max-time $TIMEOUT "$raw_url" -o "$skill_folder/SKILL.md" 2>/dev/null; then
                if [[ -s "$skill_folder/SKILL.md" ]]; then
                    log_success "Downloaded: $skill_name"
                    ((DOWNLOADED++))
                else
                    log_error "Empty file: $skill_name"
                    rm -f "$skill_folder/SKILL.md"
                    rmdir "$skill_folder" 2>/dev/null || true
                    ((FAILED++))
                fi
            else
                log_error "Failed to download: $skill_name"
                rmdir "$skill_folder" 2>/dev/null || true
                ((FAILED++))
            fi
        fi
    done
}

# Function to process a category
process_category() {
    local md_file="$1"
    local category_name
    category_name=$(basename "$md_file" .md)
    local category_folder="$SCRIPT_DIR/$category_name"
    
    log_info "========================================"
    log_info "Processing category: $category_name"
    log_info "========================================"
    
    # Create category folder
    mkdir -p "$category_folder"
    
    # Count skills in file
    local skill_count
    skill_count=$(grep -c -E '^\s*-\s*\[[^\]]+\]\(https://github\.com/openclaw/skills' "$md_file" 2>/dev/null || echo "0")
    log_info "Found $skill_count skills in $category_name"
    
    ((TOTAL_SKILLS += skill_count))
    
    # Parse and download
    parse_markdown "$md_file" "$category_name" "$category_folder"
}

# Main execution
main() {
    echo "========================================"
    echo "OpenClaw Skills Downloader"
    echo "========================================"
    echo "Started: $(date)"
    echo ""
    
    # Find all markdown files in categories directory
    log_info "Scanning for category markdown files..."
    
    local categories=()
    for md_file in "$SCRIPT_DIR"/*.md; do
        # Skip if not a file
        [[ -f "$md_file" ]] || continue
        
        # Skip special files
        local basename_file
        basename_file=$(basename "$md_file")
        [[ "$basename_file" == "AGENTS.md" ]] && continue
        [[ "$basename_file" == "README.md" ]] && continue
        
        categories+=("$md_file")
    done
    
    TOTAL_CATEGORIES=${#categories[@]}
    
    if [[ $TOTAL_CATEGORIES -eq 0 ]]; then
        log_error "No category markdown files found!"
        exit 1
    fi
    
    log_info "Found $TOTAL_CATEGORIES categories to process"
    echo ""
    
    # Process each category
    for md_file in "${categories[@]}"; do
        process_category "$md_file"
        echo ""
    done
    
    # Summary
    echo "========================================"
    echo "DOWNLOAD SUMMARY"
    echo "========================================"
    echo "Total categories: $TOTAL_CATEGORIES"
    echo "Total skills found: $TOTAL_SKILLS"
    echo "Successfully downloaded: $DOWNLOADED"
    echo "Skipped (already exist): $SKIPPED"
    echo "Failed: $FAILED"
    echo ""
    echo "Completed: $(date)"
    echo "========================================"
    
    # Return appropriate exit code
    if [[ $FAILED -gt 0 ]]; then
        exit 1
    else
        exit 0
    fi
}

# Run main function
main "$@"
