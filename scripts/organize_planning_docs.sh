#!/bin/bash

# organize_planning_docs.sh
# Organizes docs/planning files older than 7 days into YYYY-MM directories

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PLANNING_DIR="$PROJECT_ROOT/docs/planning"

# Check if planning directory exists
if [[ ! -d "$PLANNING_DIR" ]]; then
    echo "Error: docs/planning directory not found at $PLANNING_DIR"
    exit 1
fi

# Calculate cutoff date (7 days ago)
CUTOFF_DATE=$(date -d "7 days ago" +%Y-%m-%d)
echo "Moving files older than $CUTOFF_DATE to monthly directories..."

# Find and process files older than 7 days
moved_count=0
for file in "$PLANNING_DIR"/*.{md,txt}; do
    # Skip if no files match the pattern
    [[ -f "$file" ]] || continue
    
    filename=$(basename "$file")
    
    # Extract date from filename (YYYY-MM-DD format)
    if [[ $filename =~ ^([0-9]{4})-([0-9]{2})-([0-9]{2}) ]]; then
        file_date="${BASH_REMATCH[1]}-${BASH_REMATCH[2]}-${BASH_REMATCH[3]}"
        year_month="${BASH_REMATCH[1]}-${BASH_REMATCH[2]}"
        
        # Check if file is older than cutoff date
        if [[ "$file_date" < "$CUTOFF_DATE" ]]; then
            # Create monthly directory if it doesn't exist
            monthly_dir="$PLANNING_DIR/$year_month"
            mkdir -p "$monthly_dir"
            
            # Move file
            echo "Moving $filename -> $year_month/"
            mv "$file" "$monthly_dir/"
            ((moved_count++))
        fi
    else
        echo "Warning: Skipping file with unexpected name format: $filename"
    fi
done

echo "Organization complete. Moved $moved_count files to monthly directories."

# Show summary
if [[ $moved_count -gt 0 ]]; then
    echo
    echo "Monthly directories created/updated:"
    find "$PLANNING_DIR" -type d -name "20*" | sort | while read dir; do
        dir_name=$(basename "$dir")
        file_count=$(find "$dir" -maxdepth 1 -type f | wc -l)
        echo "  $dir_name: $file_count files"
    done
    
    echo
    echo "Recent files remaining in main directory:"
    find "$PLANNING_DIR" -maxdepth 1 -type f -name "*.md" -o -name "*.txt" | wc -l | while read count; do
        echo "  $count files"
    done
fi