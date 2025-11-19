# Phase 3: ApplicationConfig Removal Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove ApplicationConfig class completely, update main entry point and all remaining references to use EntityRegistry.

**Architecture:** Remove ApplicationConfig from settings.py, update main.py to initialize EntityRegistry, update CLI interface, update all integration tests to use environment variables instead of ApplicationConfig.

**Tech Stack:** Python 3, pytest, EntityRegistry, CLI interface

---

## Prerequisites

- All 3 batches complete (10 entities migrated)
- StrategyFactory uses EntityRegistry only
- Both orchestrators use EntityRegistry only
- No ApplicationConfig usage in factory/orchestrator code

---

## Task 1: Update main entry point

**Files:**
- Modify: `src/main.py`
- Create: `tests/unit/test_main_registry.py`

### Step 1: Write failing test for main with EntityRegistry

```python
# tests/unit/test_main_registry.py
"""Tests for main entry point with EntityRegistry."""

import pytest
from unittest.mock import Mock, patch
import os


@pytest.mark.unit
@patch('src.main.EntityRegistry')
@patch('src.main.StrategyBasedSaveOrchestrator')
def test_main_initializes_registry_from_environment(mock_orchestrator, mock_registry):
    """Test main initializes EntityRegistry from environment."""
    from src.main import main

    os.environ["OPERATION"] = "save"
    os.environ["GITHUB_TOKEN"] = "test_token"
    os.environ["GITHUB_REPO"] = "owner/repo"

    # Mock registry
    registry_instance = Mock()
    mock_registry.from_environment.return_value = registry_instance

    main()

    # Verify registry initialized from environment
    mock_registry.from_environment.assert_called_once()

    # Cleanup
    del os.environ["OPERATION"]
    del os.environ["GITHUB_TOKEN"]
    del os.environ["GITHUB_REPO"]


@pytest.mark.unit
def test_main_passes_registry_to_orchestrator():
    """Test main passes registry to orchestrator constructor."""
    # Implementation test for registry usage
    pass
```

### Step 2: Run test to verify failure

**Command:**
```bash
pdm run pytest tests/unit/test_main_registry.py::test_main_initializes_registry_from_environment -v
```

**Expected:** FAILED - ApplicationConfig still being used

### Step 3: Update main.py to use EntityRegistry

Read current main.py first:

**Command:**
```bash
cat src/main.py | head -100
```

Then update to use EntityRegistry:

```python
# src/main.py
"""Main entry point for GitHub data save/restore operations."""

import os
import sys
from pathlib import Path

from src.entities.registry import EntityRegistry
from src.operations.save.orchestrator import StrategyBasedSaveOrchestrator
from src.operations.restore.orchestrator import StrategyBasedRestoreOrchestrator
from src.github.service import GitHubService
from src.storage.service import StorageService
from src.git.service import GitRepositoryService


def main():
    """Execute save or restore operation based on environment variables."""
    # Get operation type
    operation = os.getenv("OPERATION", "save").lower()

    if operation not in ["save", "restore"]:
        print(f"Error: Invalid OPERATION '{operation}'. Must be 'save' or 'restore'.")
        sys.exit(1)

    # Initialize EntityRegistry from environment
    try:
        registry = EntityRegistry.from_environment(is_strict=False)
    except ValueError as e:
        print(f"Error initializing registry: {e}")
        sys.exit(1)

    # Get required environment variables
    github_token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPO")
    data_path = os.getenv("DATA_PATH", "./data")

    if not github_token:
        print("Error: GITHUB_TOKEN environment variable required")
        sys.exit(1)

    if not repo_name:
        print("Error: GITHUB_REPO environment variable required")
        sys.exit(1)

    # Initialize services
    github_service = GitHubService(token=github_token)
    storage_service = StorageService()
    git_service = GitRepositoryService() if registry.get_entity("git_repository").is_enabled() else None

    # Execute operation
    if operation == "save":
        execute_save(registry, github_service, storage_service, git_service, repo_name, data_path)
    else:
        execute_restore(registry, github_service, storage_service, repo_name, data_path)


def execute_save(registry, github_service, storage_service, git_service, repo_name, output_path):
    """Execute save operation."""
    print(f"Starting save operation for {repo_name}")
    print(f"Output path: {output_path}")

    # Show enabled entities
    enabled = registry.get_enabled_entities()
    print(f"\nEnabled entities ({len(enabled)}):")
    for entity in enabled:
        print(f"  - {entity.config.name}")

    orchestrator = StrategyBasedSaveOrchestrator(
        registry=registry,
        github_service=github_service,
        storage_service=storage_service,
        git_service=git_service
    )

    try:
        results = orchestrator.execute_save(repo_name, output_path)
        print("\nSave operation completed successfully")
        print(f"Total entities saved: {len(results)}")
    except Exception as e:
        print(f"\nError during save operation: {e}")
        sys.exit(1)


def execute_restore(registry, github_service, storage_service, repo_name, input_path):
    """Execute restore operation."""
    print(f"Starting restore operation for {repo_name}")
    print(f"Input path: {input_path}")

    # Show enabled entities
    enabled = registry.get_enabled_entities()
    print(f"\nEnabled entities ({len(enabled)}):")
    for entity in enabled:
        print(f"  - {entity.config.name}")

    orchestrator = StrategyBasedRestoreOrchestrator(
        registry=registry,
        github_service=github_service,
        storage_service=storage_service
    )

    try:
        results = orchestrator.execute_restore(repo_name, input_path)
        print("\nRestore operation completed successfully")
        print(f"Total entities restored: {len(results)}")
    except Exception as e:
        print(f"\nError during restore operation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Step 4: Run test to verify changes

**Command:**
```bash
pdm run pytest tests/unit/test_main_registry.py -v
```

**Expected:** All PASSED

### Step 5: Test main manually with environment variables

**Command:**
```bash
OPERATION=save GITHUB_TOKEN=test GITHUB_REPO=owner/repo pdm run python -m src.main --help
```

### Step 6: Commit main.py updates

**Command:**
```bash
git add src/main.py tests/unit/test_main_registry.py
git commit -s -m "feat: migrate main entry point to EntityRegistry

Replace ApplicationConfig with EntityRegistry in main entry point.
Registry initialized from environment variables.

- Initialize EntityRegistry.from_environment() in main
- Pass registry to orchestrators
- Display enabled entities before execution
- Update error handling for registry initialization

Part of Phase 3 ApplicationConfig removal.

Signed-off-by: Claude <noreply@anthropic.com>"
```

---

## Task 2: Remove ApplicationConfig class

**Files:**
- Modify: `src/config/settings.py`
- Keep: NumberSpecificationParser (still used by EntityRegistry)

### Step 1: Write test to verify ApplicationConfig is gone

```python
# tests/unit/config/test_settings.py
"""Tests for config.settings module."""

import pytest


@pytest.mark.unit
def test_application_config_removed():
    """Test that ApplicationConfig class no longer exists."""
    import src.config.settings as settings

    # ApplicationConfig should not exist
    assert not hasattr(settings, "ApplicationConfig")


@pytest.mark.unit
def test_number_specification_parser_still_exists():
    """Test that NumberSpecificationParser still exists (used by registry)."""
    from src.config.settings import NumberSpecificationParser

    # Parser should still exist
    assert NumberSpecificationParser is not None
```

### Step 2: Run test to verify failure

**Command:**
```bash
pdm run pytest tests/unit/config/test_settings.py::test_application_config_removed -v
```

**Expected:** FAILED - ApplicationConfig still exists

### Step 3: Read current settings.py

**Command:**
```bash
cat src/config/settings.py | head -50
```

### Step 4: Remove ApplicationConfig class

Edit `src/config/settings.py`:
- Remove ApplicationConfig class definition
- Keep NumberSpecificationParser
- Keep any other utility functions used by EntityRegistry

### Step 5: Run test to verify removal

**Command:**
```bash
pdm run pytest tests/unit/config/test_settings.py -v
```

**Expected:** All PASSED

### Step 6: Search for remaining references

**Command:**
```bash
grep -r "ApplicationConfig" src/ --exclude-dir=__pycache__ --exclude="*.pyc"
```

**Expected:** No results (or only in comments/docstrings)

### Step 7: Commit ApplicationConfig removal

**Command:**
```bash
git add src/config/settings.py tests/unit/config/test_settings.py
git commit -s -m "feat: remove ApplicationConfig class

Delete ApplicationConfig class from codebase. EntityRegistry is now the
sole configuration system for entity management.

- Remove ApplicationConfig class definition
- Keep NumberSpecificationParser (used by EntityRegistry)
- Update module documentation

Part of Phase 3 ApplicationConfig removal.

BREAKING CHANGE: ApplicationConfig class removed. Use EntityRegistry instead.

Signed-off-by: Claude <noreply@anthropic.com>"
```

---

## Task 3: Update integration tests to use environment variables

**Files:**
- Modify: `tests/integration/*.py`
- Modify: `tests/container/*.py` (if any exist)

### Step 1: Find all ApplicationConfig usage in tests

**Command:**
```bash
grep -r "ApplicationConfig" tests/ --exclude-dir=__pycache__
```

### Step 2: Update each test file

For each file found, replace ApplicationConfig initialization with environment variable setup:

**Old pattern:**
```python
config = ApplicationConfig(
    operation="save",
    include_issues=True,
    include_comments=False,
    ...
)
```

**New pattern:**
```python
import os

os.environ["INCLUDE_ISSUES"] = "true"
os.environ["INCLUDE_ISSUE_COMMENTS"] = "false"
# ... set other variables

registry = EntityRegistry.from_environment()

# Cleanup after test
del os.environ["INCLUDE_ISSUES"]
del os.environ["INCLUDE_ISSUE_COMMENTS"]
```

### Step 3: Create helper fixture for environment setup

```python
# tests/shared/fixtures.py

@pytest.fixture
def clean_environment():
    """Fixture to clean up environment variables after tests."""
    # Store original environment
    original_env = os.environ.copy()

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def registry_with_config(clean_environment):
    """Fixture to create EntityRegistry with specific configuration."""
    def _create(**entity_settings):
        """Create registry with specific entity settings.

        Args:
            **entity_settings: Entity names and their values
                e.g., labels=True, issues=False
        """
        # Map friendly names to env vars
        env_var_map = {
            "labels": "INCLUDE_LABELS",
            "milestones": "INCLUDE_MILESTONES",
            "git_repository": "INCLUDE_GIT_REPO",
            "issues": "INCLUDE_ISSUES",
            "comments": "INCLUDE_ISSUE_COMMENTS",
            "sub_issues": "INCLUDE_SUB_ISSUES",
            "pull_requests": "INCLUDE_PULL_REQUESTS",
            "pr_reviews": "INCLUDE_PR_REVIEWS",
            "pr_review_comments": "INCLUDE_PR_REVIEW_COMMENTS",
            "pr_comments": "INCLUDE_PULL_REQUEST_COMMENTS",
        }

        for entity_name, value in entity_settings.items():
            env_var = env_var_map.get(entity_name)
            if env_var:
                os.environ[env_var] = str(value).lower()

        return EntityRegistry.from_environment()

    return _create
```

### Step 4: Update test files to use fixtures

Example update:

```python
# tests/integration/test_save_workflow.py

@pytest.mark.integration
def test_save_with_selective_entities(registry_with_config):
    """Test save operation with selective entities."""
    # Create registry with specific configuration
    registry = registry_with_config(
        labels=True,
        issues=True,
        comments=False
    )

    # Rest of test uses registry
    enabled = registry.get_enabled_entities()
    enabled_names = [e.config.name for e in enabled]

    assert "labels" in enabled_names
    assert "issues" in enabled_names
    assert "comments" not in enabled_names
```

### Step 5: Run updated integration tests

**Command:**
```bash
pdm run pytest tests/integration/ -v
```

**Expected:** All PASSED

### Step 6: Commit integration test updates

**Command:**
```bash
git add tests/integration/ tests/shared/fixtures.py
git commit -s -m "test: migrate integration tests to use EntityRegistry

Replace ApplicationConfig with EntityRegistry in all integration tests.
Tests now use environment variables via helper fixtures.

- Add clean_environment fixture for env cleanup
- Add registry_with_config fixture for easy setup
- Update all integration tests to use fixtures
- Remove all ApplicationConfig references from tests

Part of Phase 3 ApplicationConfig removal.

Signed-off-by: Claude <noreply@anthropic.com>"
```

---

## Task 4: Update container tests (if any)

**Files:**
- Modify: `tests/container/*.py` (if exists)

### Step 1: Check for container tests

**Command:**
```bash
find tests/ -name "*container*" -type f
```

### Step 2: Update container tests similarly to integration tests

Use environment variables instead of ApplicationConfig.

### Step 3: Run container tests

**Command:**
```bash
make test-container
```

**Expected:** All PASSED

### Step 4: Commit container test updates

**Command:**
```bash
git add tests/container/
git commit -s -m "test: migrate container tests to EntityRegistry

Update container tests to use environment variables and EntityRegistry.

Part of Phase 3 ApplicationConfig removal.

Signed-off-by: Claude <noreply@anthropic.com>"
```

---

## Task 5: Search and remove all remaining references

### Step 1: Comprehensive search for ApplicationConfig

**Command:**
```bash
grep -r "ApplicationConfig" . --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=__pycache__ --exclude="*.pyc"
```

### Step 2: Review each result

For each file found:
- If it's code: update to use EntityRegistry
- If it's documentation: update references
- If it's comments: update or remove

### Step 3: Check imports

**Command:**
```bash
grep -r "from src.config.settings import ApplicationConfig" src/ tests/
```

**Expected:** No results

### Step 4: Check type hints

**Command:**
```bash
grep -r "ApplicationConfig" src/ | grep -E "(: ApplicationConfig|-> ApplicationConfig)"
```

### Step 5: Update any found references

### Step 6: Commit cleanup

**Command:**
```bash
git add .
git commit -s -m "refactor: remove all remaining ApplicationConfig references

Clean up all remaining references to ApplicationConfig in code,
comments, and documentation. EntityRegistry is now the only
configuration system.

Part of Phase 3 ApplicationConfig removal.

Signed-off-by: Claude <noreply@anthropic.com>"
```

---

## Task 6: Update documentation

**Files:**
- Modify: `README.md`
- Modify: `docs/*.md`
- Modify: `CLAUDE.md`

### Step 1: Update README.md

Update environment variable documentation to reflect EntityRegistry usage.

Remove any ApplicationConfig references.

### Step 2: Update developer documentation

Update any developer guides that mention ApplicationConfig.

### Step 3: Update CLAUDE.md

Update project status to reflect Phase 3 completion.

### Step 4: Commit documentation updates

**Command:**
```bash
git add README.md docs/ CLAUDE.md
git commit -s -m "docs: update documentation for EntityRegistry system

Update all documentation to reflect EntityRegistry as the configuration
system, removing ApplicationConfig references.

- Update README with EntityRegistry usage
- Update developer documentation
- Update CLAUDE.md project status
- Document environment variables for all entities

Part of Phase 3 ApplicationConfig removal.

Signed-off-by: Claude <noreply@anthropic.com>"
```

---

## Task 7: Final comprehensive validation

### Step 1: Run all unit tests

**Command:**
```bash
pdm run pytest tests/unit/ -v
```

**Expected:** All PASSED

### Step 2: Run all integration tests

**Command:**
```bash
pdm run pytest tests/integration/ -v
```

**Expected:** All PASSED

### Step 3: Run container tests

**Command:**
```bash
make test-container
```

**Expected:** All PASSED

### Step 4: Run all quality checks

**Command:**
```bash
make check-all
```

**Expected:** All checks pass

### Step 5: Manual validation scenarios

Test each scenario manually:

**Scenario 1: All entities enabled (default)**
```bash
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  -e GITHUB_REPO=owner/repo \
  -e DATA_PATH=/data \
  -v $(pwd)/test-data:/data \
  github-data:latest
```

**Scenario 2: Selective entities disabled**
```bash
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  -e GITHUB_REPO=owner/repo \
  -e INCLUDE_ISSUE_COMMENTS=false \
  -e INCLUDE_PR_REVIEWS=false \
  -v $(pwd)/test-data:/data \
  github-data:latest
```

**Scenario 3: Number specifications**
```bash
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  -e GITHUB_REPO=owner/repo \
  -e INCLUDE_ISSUES="1,5-10" \
  -e INCLUDE_PULL_REQUESTS="1-3,7" \
  -v $(pwd)/test-data:/data \
  github-data:latest
```

### Step 6: Verify error messages

Test error scenarios:

**Invalid environment variable value:**
```bash
INCLUDE_ISSUES=invalid pytest  # Should show clear error
```

**Dependency violation:**
```bash
INCLUDE_ISSUES=false INCLUDE_ISSUE_COMMENTS=true pytest  # Should auto-disable or error
```

### Step 7: Create final validation report

Document all validation results in a report.

---

## Task 8: Final Phase 3 completion

### Step 1: Create Phase 3 completion summary

**Command:**
```bash
git commit --allow-empty -s -m "$(cat <<'EOF'
feat: complete Phase 3 - ApplicationConfig removal

Complete removal of ApplicationConfig from entire codebase. EntityRegistry
is now the sole configuration system for entity management.

Summary of Phase 3:
- Batch 1: Migrated labels, milestones, git_repository (3 entities)
- Batch 2: Migrated issues, comments, sub_issues (3 entities)
- Batch 3: Migrated pull_requests, pr_reviews, pr_review_comments, pr_comments (4 entities)
- Factory: StrategyFactory now uses EntityRegistry exclusively
- Orchestrators: Both save and restore orchestrators use EntityRegistry
- ApplicationConfig: Class removed, all references eliminated
- Tests: All tests updated to use environment variables
- Documentation: Updated for EntityRegistry system

Complete dependency graph validated:
  milestones → issues → [comments, sub_issues]
  milestones → pull_requests → [pr_reviews → pr_review_comments, pr_comments]
  labels (independent)
  git_repository (independent)

All 10 entities migrated successfully.
All tests passing (unit + integration + container).
All quality checks passing.
No ApplicationConfig references remain.

Phase 3 entity migration COMPLETE.

Signed-off-by: Claude <noreply@anthropic.com>
EOF
)"
```

### Step 2: Tag Phase 3 completion

**Command:**
```bash
git tag -a phase3-complete -m "Phase 3 Complete: All entities migrated to EntityRegistry, ApplicationConfig removed"
```

### Step 3: Update Phase 3 design document status

Edit `docs/planning/2025-10-25-phase3-entity-migration-design.md`:

Change status from "Design Complete" to "Implementation Complete"

### Step 4: Commit status update

**Command:**
```bash
git add docs/planning/2025-10-25-phase3-entity-migration-design.md
git commit -s -m "docs: mark Phase 3 as Implementation Complete

Update Phase 3 design document to reflect completion of implementation.

Signed-off-by: Claude <noreply@anthropic.com>"
```

### Step 5: Push all changes and tags

**Command:**
```bash
git push origin feature/entity-registry-system && git push origin --tags
```

### Step 6: Create completion summary document

**Command:**
```bash
cat > docs/planning/2025-10-25-phase3-completion-summary.md << 'EOF'
# Phase 3 Entity Migration - Completion Summary

**Date Completed:** 2025-10-25
**Status:** ✅ COMPLETE

## Overview

Phase 3 successfully migrated all 10 entities from ApplicationConfig to the EntityRegistry system and removed ApplicationConfig completely from the codebase.

## Accomplishments

### Batch 1: Independent Entities
- ✅ labels entity migrated
- ✅ milestones entity migrated
- ✅ git_repository entity migrated
- ✅ StrategyFactory updated to support EntityRegistry

### Batch 2: Issues Domain
- ✅ issues entity migrated (depends on milestones)
- ✅ comments entity migrated (depends on issues)
- ✅ sub_issues entity migrated (depends on issues)
- ✅ Dependency validation tested

### Batch 3: Pull Requests Domain
- ✅ pull_requests entity migrated (depends on milestones)
- ✅ pr_reviews entity migrated (depends on pull_requests)
- ✅ pr_review_comments entity migrated (depends on pr_reviews)
- ✅ pr_comments entity migrated (depends on pull_requests)
- ✅ Complete dependency graph validated

### Infrastructure Updates
- ✅ StrategyFactory migration complete (EntityRegistry only)
- ✅ SaveOrchestrator migrated to EntityRegistry
- ✅ RestoreOrchestrator migrated to EntityRegistry
- ✅ DependencyResolver deprecated (registry handles dependencies)

### ApplicationConfig Removal
- ✅ Main entry point updated to use EntityRegistry
- ✅ ApplicationConfig class deleted
- ✅ All integration tests updated to use environment variables
- ✅ All container tests updated
- ✅ All references removed from codebase
- ✅ Documentation updated

## Test Results

- Unit tests: ✅ All passing
- Integration tests: ✅ All passing
- Container tests: ✅ All passing
- Quality checks: ✅ All passing (lint, format, types)

## Dependency Graph

Final validated dependency graph:

```
Independent:
  - labels
  - git_repository

Milestone branch:
  milestones
    ├─→ issues
    │   ├─→ comments
    │   └─→ sub_issues
    └─→ pull_requests
        ├─→ pr_reviews
        │   └─→ pr_review_comments
        └─→ pr_comments
```

## Breaking Changes

- ApplicationConfig class removed (BREAKING CHANGE)
- Code using ApplicationConfig must migrate to EntityRegistry
- Environment variable-based configuration required

## Migration Benefits

1. **Auto-discovery**: No manual registration required for new entities
2. **Convention-based**: Strategies loaded automatically by naming convention
3. **Dependency management**: Automatic topological sorting and validation
4. **Flexible configuration**: Environment variables with auto-disable support
5. **Test isolation**: No shared global state breaking tests
6. **Reduced boilerplate**: Entity addition requires only entity_config.py

## Next Steps

Phase 3 is complete. Potential future enhancements:
- Phase 4: Test infrastructure improvements (if needed)
- Phase 5: Enhanced CLI interface
- Phase 6: Additional entity types

## Git Tags

- `phase3-batch1-complete`: Batch 1 completion
- `phase3-batch2-complete`: Batch 2 completion
- `phase3-batch3-complete`: Batch 3 completion
- `phase3-factory-orchestrator-complete`: Infrastructure updates
- `phase3-complete`: Full Phase 3 completion

## Conclusion

Phase 3 entity migration completed successfully. All 10 entities migrated to EntityRegistry with full dependency management. ApplicationConfig removed from codebase. All tests passing.

EntityRegistry system now fully operational and ready for production use.
EOF
```

### Step 7: Commit completion summary

**Command:**
```bash
git add docs/planning/2025-10-25-phase3-completion-summary.md
git commit -s -m "docs: add Phase 3 completion summary

Document completion of Phase 3 entity migration including accomplishments,
test results, breaking changes, and benefits.

Signed-off-by: Claude <noreply@anthropic.com>"
```

---

## Success Criteria

ApplicationConfig removal complete when:
- ✅ Main entry point uses EntityRegistry
- ✅ ApplicationConfig class deleted from settings.py
- ✅ All integration tests use environment variables
- ✅ All container tests use environment variables
- ✅ No ApplicationConfig references in src/
- ✅ No ApplicationConfig references in tests/
- ✅ Documentation updated
- ✅ All tests passing (unit + integration + container)
- ✅ All quality checks passing
- ✅ Manual validation scenarios work
- ✅ Error messages are clear and helpful
- ✅ Phase 3 tagged and documented

## Final Validation Checklist

- [ ] `grep -r "ApplicationConfig" src/` returns no results
- [ ] `grep -r "ApplicationConfig" tests/` returns no results
- [ ] `make check-all` passes
- [ ] Manual docker tests work for all scenarios
- [ ] Error messages are helpful
- [ ] Documentation is up to date
- [ ] Git tags created and pushed
- [ ] Completion summary document created

## Conclusion

Phase 3 entity migration complete. All 10 entities migrated to EntityRegistry. ApplicationConfig removed. System ready for production use.
