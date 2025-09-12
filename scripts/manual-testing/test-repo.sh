#!/bin/bash

# Manual Repository Testing Script
# Usage: ./scripts/manual-testing/test-repo.sh <owner/repo> [operation]

set -e

REPO=${1:-}
OPERATION=${2:-save}

if [ -z "$REPO" ]; then
    echo "Usage: $0 <owner/repo> [save|restore]"
    echo "Example: $0 microsoft/vscode save"
    exit 1
fi

if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable is required"
    echo "Set it with: export GITHUB_TOKEN=your_token"
    exit 1
fi

echo "=== Manual Container Test ==="
echo "Repository: $REPO"
echo "Operation: $OPERATION" 
echo "Data Directory: ./manual-test-data/$REPO"
echo

# Create data directory
DATA_DIR="./manual-test-data/$REPO"
mkdir -p "$DATA_DIR"

# Build container if needed
echo "Building container..."
make docker-build

echo "Running container test for $REPO..."
docker run --rm \
    -v "$(pwd)/$DATA_DIR":/data \
    -e GITHUB_TOKEN="$GITHUB_TOKEN" \
    -e GITHUB_REPO="$REPO" \
    -e OPERATION="$OPERATION" \
    -e DATA_PATH="/data" \
    github-data

echo "=== Test Results ==="
echo "Data saved to: $DATA_DIR"
echo "Contents:"
ls -la "$DATA_DIR"

if [ "$OPERATION" = "save" ]; then
    echo
    echo "To test restore, run:"
    echo "$0 $REPO restore"
fi