#!/bin/bash

# Batch Manual Testing Script
# Tests multiple repositories from manual-test-repos.local.yml

set -e

CONFIG_FILE="manual-test-repos.local.yml"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: $CONFIG_FILE not found"
    echo "Copy manual-test-repos.yml to manual-test-repos.local.yml and customize it"
    exit 1
fi

if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable is required"
    exit 1
fi

echo "=== Batch Manual Testing ==="
echo "Reading repositories from $CONFIG_FILE"
echo

# Simple YAML parsing for repo names (basic approach)
REPOS=$(grep "repo:" "$CONFIG_FILE" | cut -d'"' -f2 | grep -v "owner/" || true)

if [ -z "$REPOS" ]; then
    echo "No repositories found in $CONFIG_FILE"
    echo "Make sure to customize the file with real repository names"
    exit 1
fi

OPERATION=${1:-save}
SUCCESS_COUNT=0
TOTAL_COUNT=0

for REPO in $REPOS; do
    if [[ "$REPO" == "your-username/your-repo" ]]; then
        echo "Skipping template repository: $REPO"
        continue
    fi
    
    echo "=== Testing repository: $REPO ==="
    TOTAL_COUNT=$((TOTAL_COUNT + 1))
    
    if ./scripts/manual-testing/test-repo.sh "$REPO" "$OPERATION"; then
        echo "✓ Success: $REPO"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "✗ Failed: $REPO"
    fi
    
    echo
done

echo "=== Batch Test Results ==="
echo "Successful: $SUCCESS_COUNT/$TOTAL_COUNT"
echo "Results saved to: ./manual-test-data/"