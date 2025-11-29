#!/bin/bash
# Script to selectively test only packages with changes on the current branch
# Usage:
#   ./scripts/test-changed.sh           # Run all tests for changed packages
#   ./scripts/test-changed.sh --fast    # Run only fast tests for changed packages

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if --fast flag is provided
FAST_MODE=false
if [ "$1" == "--fast" ]; then
    FAST_MODE=true
fi

# Get the main branch name (usually 'main' or 'master')
MAIN_BRANCH=$(git remote show origin | grep 'HEAD branch' | cut -d' ' -f5)
if [ -z "$MAIN_BRANCH" ]; then
    MAIN_BRANCH="main"
fi

echo -e "${YELLOW}Detecting changes against branch: ${MAIN_BRANCH}${NC}"

# Get list of changed files on current branch
CHANGED_FILES=$(git diff --name-only ${MAIN_BRANCH}...HEAD)

if [ -z "$CHANGED_FILES" ]; then
    echo -e "${GREEN}No changes detected. Skipping tests.${NC}"
    exit 0
fi

echo -e "${YELLOW}Changed files:${NC}"
echo "$CHANGED_FILES"
echo ""

# Determine which packages have changes
PACKAGES_TO_TEST=""

# Check if core package has changes
if echo "$CHANGED_FILES" | grep -q "^packages/core/"; then
    echo -e "${YELLOW}Core package changed - testing ALL packages (all depend on core)${NC}"
    PACKAGES_TO_TEST="all"
fi

# If core didn't change, check individual packages
if [ "$PACKAGES_TO_TEST" != "all" ]; then
    # Check git-repo-tools
    if echo "$CHANGED_FILES" | grep -q "^packages/git-repo-tools/"; then
        PACKAGES_TO_TEST="$PACKAGES_TO_TEST git-repo-tools"
    fi

    # Check github-repo-manager
    if echo "$CHANGED_FILES" | grep -q "^packages/github-repo-manager/"; then
        PACKAGES_TO_TEST="$PACKAGES_TO_TEST github-repo-manager"
    fi

    # Check github-data-tools
    if echo "$CHANGED_FILES" | grep -q "^packages/github-data-tools/"; then
        PACKAGES_TO_TEST="$PACKAGES_TO_TEST github-data-tools"
    fi

    # Check kit-orchestrator
    if echo "$CHANGED_FILES" | grep -q "^packages/kit-orchestrator/"; then
        PACKAGES_TO_TEST="$PACKAGES_TO_TEST kit-orchestrator"
    fi
fi

# If no package-specific changes, check for root changes
if [ -z "$PACKAGES_TO_TEST" ]; then
    if echo "$CHANGED_FILES" | grep -q -E "(^pyproject.toml|^Makefile|^scripts/)"; then
        echo -e "${YELLOW}Root infrastructure changed - testing ALL packages${NC}"
        PACKAGES_TO_TEST="all"
    fi
fi

# Exit if no packages need testing
if [ -z "$PACKAGES_TO_TEST" ]; then
    echo -e "${GREEN}No package changes detected. Skipping tests.${NC}"
    exit 0
fi

# Run tests based on what changed
echo -e "${GREEN}Testing packages: $PACKAGES_TO_TEST${NC}"
echo ""

EXIT_CODE=0

if [ "$PACKAGES_TO_TEST" == "all" ]; then
    # Test everything
    echo -e "${YELLOW}Running tests for all packages...${NC}"
    if [ "$FAST_MODE" == "true" ]; then
        make test-fast || EXIT_CODE=$?
    else
        make test-all || EXIT_CODE=$?
    fi
else
    # Test specific packages
    for package in $PACKAGES_TO_TEST; do
        echo -e "${YELLOW}Testing $package...${NC}"

        case $package in
            git-repo-tools)
                if [ "$FAST_MODE" == "true" ]; then
                    pdm run pytest packages/git-repo-tools/tests -m "not container and not slow" || EXIT_CODE=$?
                else
                    make test-git || EXIT_CODE=$?
                fi
                ;;
            github-repo-manager)
                if [ "$FAST_MODE" == "true" ]; then
                    pdm run pytest packages/github-repo-manager/tests -m "not container and not slow" || EXIT_CODE=$?
                else
                    make test-github-manager || EXIT_CODE=$?
                fi
                ;;
            github-data-tools)
                if [ "$FAST_MODE" == "true" ]; then
                    pdm run pytest packages/github-data-tools/tests -m "not container and not slow" || EXIT_CODE=$?
                else
                    make test-github-data || EXIT_CODE=$?
                fi
                ;;
            kit-orchestrator)
                if [ "$FAST_MODE" == "true" ]; then
                    pdm run pytest packages/kit-orchestrator/tests -m "not container and not slow" || EXIT_CODE=$?
                else
                    make test-orchestrator || EXIT_CODE=$?
                fi
                ;;
        esac
    done
fi

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
else
    echo -e "${RED}Some tests failed. Exit code: $EXIT_CODE${NC}"
fi

exit $EXIT_CODE
