#!/bin/bash

# Analyze Manual Test Results
# Shows summary of backup/restore data for manual verification

set -e

DATA_DIR="./manual-test-data"

if [ ! -d "$DATA_DIR" ]; then
    echo "No manual test data found at $DATA_DIR"
    echo "Run manual tests first using test-repo.sh or batch-test.sh"
    exit 1
fi

echo "=== Manual Test Results Analysis ==="
echo

for repo_dir in "$DATA_DIR"/*; do
    if [ ! -d "$repo_dir" ]; then
        continue
    fi
    
    repo_name=$(basename "$repo_dir")
    echo "Repository: $repo_name"
    echo "Directory: $repo_dir"
    
    # Check for expected files
    if [ -f "$repo_dir/issues.json" ]; then
        issue_count=$(jq length "$repo_dir/issues.json" 2>/dev/null || echo "N/A")
        echo "  Issues: $issue_count"
    else
        echo "  Issues: No issues.json found"
    fi
    
    if [ -f "$repo_dir/labels.json" ]; then
        label_count=$(jq length "$repo_dir/labels.json" 2>/dev/null || echo "N/A")
        echo "  Labels: $label_count"
    else
        echo "  Labels: No labels.json found"
    fi
    
    if [ -f "$repo_dir/metadata.json" ]; then
        echo "  Metadata: Found"
        if command -v jq >/dev/null 2>&1; then
            echo "    $(jq -r '.timestamp // "No timestamp"' "$repo_dir/metadata.json")"
            echo "    $(jq -r '.repository // "No repo info"' "$repo_dir/metadata.json")"
        fi
    else
        echo "  Metadata: Not found"
    fi
    
    echo "  Files:"
    ls -la "$repo_dir" | sed 's/^/    /'
    echo
done

echo "=== Summary ==="
total_repos=$(find "$DATA_DIR" -mindepth 1 -maxdepth 1 -type d | wc -l)
echo "Total repositories tested: $total_repos"
echo "Data location: $DATA_DIR"