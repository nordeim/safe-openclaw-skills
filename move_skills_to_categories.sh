#!/bin/bash
#
# OpenClaw Skills Organizer
# Moves skills from temp clone to category folders based on markdown listings
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMP_SKILLS_DIR="$SCRIPT_DIR/temp_cloned_skils_to_scan_before_select_relevant/skills"

# Counters
TOTAL_CATEGORIES=0
TOTAL_SKILLS_FOUND=0
SKILLS_MOVED=0
SKILLS_COPIED=0
SKILLS_SKIPPED=0
SKILLS_NOT_FOUND=0
SKILLS_CONFLICT=0

# Array to track moved skills for conflict detection
declare -A MOVED_SKILLS

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

log_debug() {
    echo -e "${CYAN}[DEBUG]${NC} $1"
}

# Function to sanitize folder name for filesystem
sanitize_name() {
    local name="$1"
    # Replace problematic characters
    name=$(echo "$name" | tr '[:upper:]' '[:lower:]')
    name=$(echo "$name" | sed 's/[^a-z0-9._-]/-/g')
    # Remove leading/trailing dashes
    name=$(echo "$name" | sed 's/^-//;s/-$//')
    echo "$name"
}

# Function to find unique name if conflict exists
find_unique_name() {
    local target_dir="$1"
    local base_name="$2"
    local author="$3"
    
    local final_name="$base_name"
    local counter=1
    
    # If name exists, try with author prefix
    if [[ -e "$target_dir/$final_name" ]]; then
        final_name="${base_name}-${author}"
        
        # If still exists, add counter
        while [[ -e "$target_dir/$final_name" ]]; do
            final_name="${base_name}-${author}-${counter}"
            ((counter++))
        done
    fi
    
    echo "$final_name"
}

# Function to parse markdown and move skills
process_category() {
    local md_file="$1"
    local category_name
    category_name=$(basename "$md_file" .md)
    local category_folder="$SCRIPT_DIR/$category_name"
    
    log_info "========================================"
    log_info "Processing: $category_name"
    log_info "========================================"
    
    # Create category folder
    mkdir -p "$category_folder"
    
    local category_skills=0
    local category_moved=0
    local category_not_found=0
    local category_conflict=0
    
    # Parse markdown for skills
    while IFS= read -r line; do
        # Skip empty lines and headers
        [[ -z "$line" ]] && continue
        [[ "$line" =~ ^# ]] && continue
        [[ "$line" =~ ^\[ ]] && continue
        
    # Extract skill info from markdown pattern:
    # - [skill-name](https://github.com/openclaw/skills/tree/main/skills/author/skill-name/SKILL.md)
    # Note: Bash regex doesn't support \s, use [[:space:]] instead
    if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*\[([^\]]+)\]\(https://github\.com/openclaw/skills/tree/main/skills/([^/]+)/([^/]+)/SKILL\.md ]]; then
            local skill_name="${BASH_REMATCH[1]}"
            local author="${BASH_REMATCH[2]}"
            local skill_repo="${BASH_REMATCH[3]}"
            
            ((TOTAL_SKILLS_FOUND++))
            ((category_skills++))
            
            # Sanitize skill name for folder
            local skill_folder_name
            skill_folder_name=$(sanitize_name "$skill_name")
            
            # Source folder in temp
            local source_folder="$TEMP_SKILLS_DIR/$author/$skill_repo"
            
            # Check if source exists
            if [[ ! -d "$source_folder" ]]; then
                log_error "NOT FOUND: $skill_name (author: $author, repo: $skill_repo)"
                ((SKILLS_NOT_FOUND++))
                ((category_not_found++))
                continue
            fi
            
            # Find unique target name
            local target_name
            target_name=$(find_unique_name "$category_folder" "$skill_folder_name" "$author")
            local target_path="$category_folder/$target_name"
            
            # Check if this exact skill (by author/repo) was already moved
            local skill_key="$author/$skill_repo"
            if [[ -n "${MOVED_SKILLS[$skill_key]}" ]]; then
                log_warning "SKIPPED (duplicate): $skill_name (already in ${MOVED_SKILLS[$skill_key]})"
                ((SKILLS_SKIPPED++))
                continue
            fi
            
            # Check if this is a rename
            if [[ "$target_name" != "$skill_folder_name" ]]; then
                log_info "RENAME: $skill_name -> $target_name (conflict resolved)"
                ((SKILLS_CONFLICT++))
                ((category_conflict++))
            fi
            
            # Copy the skill folder
            if cp -a "$source_folder" "$target_path"; then
                log_success "COPIED: $skill_name -> $category_name/$target_name"
                ((SKILLS_COPIED++))
                ((category_moved++))
                
                # Track this move
                MOVED_SKILLS["$skill_key"]="$category_name/$target_name"
            else
                log_error "FAILED: $skill_name (copy failed)"
                ((SKILLS_NOT_FOUND++))
                ((category_not_found++))
            fi
        fi
    done < "$md_file"
    
    log_info "Category stats: $category_skills skills, $category_moved copied, $category_not_found not found, $category_conflict renamed"
}

# Main execution
main() {
    echo "========================================"
    echo "OpenClaw Skills Organizer"
    echo "========================================"
    echo "Started: $(date)"
    echo "Source: $TEMP_SKILLS_DIR"
    echo ""
    
    # Check if temp directory exists
    if [[ ! -d "$TEMP_SKILLS_DIR" ]]; then
        log_error "Temp skills directory not found: $TEMP_SKILLS_DIR"
        exit 1
    fi
    
    # Count available skills
    local available_skills
    available_skills=$(find "$TEMP_SKILLS_DIR" -mindepth 2 -maxdepth 2 -type d | wc -l)
    log_info "Available skills in temp folder: $available_skills"
    echo ""
    
    # Find all markdown files
    local categories=()
    for md_file in "$SCRIPT_DIR"/*.md; do
        [[ -f "$md_file" ]] || continue
        
        local basename_file
        basename_file=$(basename "$md_file")
        
        # Skip special files
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
    echo "ORGANIZATION SUMMARY"
    echo "========================================"
    echo "Total categories processed: $TOTAL_CATEGORIES"
    echo "Total skills found in markdowns: $TOTAL_SKILLS_FOUND"
    echo "Successfully copied: $SKILLS_COPIED"
    echo "Skipped (duplicates): $SKILLS_SKIPPED"
    echo "Not found: $SKILLS_NOT_FOUND"
    echo "Renamed (conflicts): $SKILLS_CONFLICT"
    echo ""
    echo "Completed: $(date)"
    echo "========================================"
    
    # Return appropriate exit code
    if [[ $SKILLS_NOT_FOUND -gt 0 ]]; then
        log_warning "Some skills were not found in the temp directory"
        exit 0  # Don't fail, just warn
    else
        exit 0
    fi
}

# Run main function
main "$@"
