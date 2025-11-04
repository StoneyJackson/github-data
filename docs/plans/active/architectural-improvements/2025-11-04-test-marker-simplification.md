# Test Marker Simplification Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Eliminate entity-specific pytest markers, reducing maintenance burden while preserving performance and infrastructure markers.

**Architecture:** Remove entity markers from pytest.ini, clean test files, update conftest.py auto-marking, and update documentation. Entity selection shifts to file paths and `-k` flag filtering.

**Tech Stack:** pytest, Python decorators, grep for code search

**Design Document:** `docs/plans/active/architectural-improvements/2025-11-04-test-marker-simplification-design.md`

---

## Task 1: pytest.ini Cleanup - Remove Entity Markers

**Files:**
- Modify: `pytest.ini`

**Step 1: Read current pytest.ini**

Run: `cat pytest.ini`
Purpose: Understand current marker structure

**Step 2: Update pytest.ini to remove entity markers**

Edit `pytest.ini` to remove the following marker lines:

```ini
# Remove these lines (Feature area markers section):
    labels: Label management functionality tests
    issues: Issue management functionality tests
    comments: Comment management functionality tests
    include_issue_comments: Issue comments feature test (INCLUDE_ISSUE_COMMENTS)
    include_pull_request_comments: Pull request comments feature tests
    pr_comments: Pull request comment functionality tests
    sub_issues: Sub-issues workflow functionality tests
    pull_requests: Pull request workflow functionality tests
    git_repositories: Git repository backup/restore functionality tests
    milestones: Milestone management functionality tests
    milestone_relationships: Issue/PR milestone relationship tests
    milestone_integration: End-to-end milestone workflow tests
    milestone_config: INCLUDE_MILESTONES configuration tests
    releases: Release and tag management functionality tests
    release_integration: End-to-end release workflow tests
```

Keep all other markers (performance, test types, infrastructure, scenarios, fixtures, complexity).

Update the comment before the feature area section to remove reference to "Feature area markers".

**Step 3: Verify markers removed**

Run: `grep -E "(labels|issues|comments|milestones|releases|git_repositories|sub_issues|pull_requests|pr_comments|pr_review|milestone_|release_|include_issue|include_pull)" pytest.ini`
Expected: No matches (or only in comments explaining what was removed)

**Step 4: Verify pytest recognizes markers**

Run: `pytest --markers | head -30`
Expected: Should show performance, unit, integration, container markers but NOT entity markers

**Step 5: Commit**

```bash
git add pytest.ini
git commit -m "refactor: remove entity-specific pytest markers

Entity markers are redundant with file structure organization.
Entity selection now uses file paths and -k flag filtering.

Removed 14+ entity markers: labels, issues, comments, milestones,
releases, git_repositories, sub_issues, pull_requests, etc.

Kept 26 infrastructure/performance markers.

Related to architectural improvements #3.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 2: Find All Entity Marker Usage in Tests

**Files:**
- None (search only)

**Step 1: Search for entity marker decorators**

Run each grep command to find entity marker usage:

```bash
grep -r "@pytest.mark.labels" tests/
grep -r "@pytest.mark.issues" tests/
grep -r "@pytest.mark.comments" tests/
grep -r "@pytest.mark.milestones" tests/
grep -r "@pytest.mark.milestone_integration" tests/
grep -r "@pytest.mark.milestone_relationships" tests/
grep -r "@pytest.mark.releases" tests/
grep -r "@pytest.mark.release_integration" tests/
grep -r "@pytest.mark.git_repositories" tests/
grep -r "@pytest.mark.sub_issues" tests/
grep -r "@pytest.mark.pull_requests" tests/
grep -r "@pytest.mark.pr_comments" tests/
grep -r "@pytest.mark.pr_review" tests/
grep -r "@pytest.mark.include_issue_comments" tests/
grep -r "@pytest.mark.include_pull_request_comments" tests/
```

**Step 2: Document findings**

Create a temporary list of files that need updates. Save output for reference.

Expected: Likely find decorators in test files, especially integration tests.

**Step 3: Verify no false positives**

Check that grep results are actual decorator usage, not comments or strings.

---

## Task 3: Remove Entity Markers from Test Files (Batch 1 - Unit Tests)

**Files:**
- Modify: All files found in Task 2 under `tests/unit/`

**Step 1: Remove entity marker decorators from unit test files**

For each file found in Task 2 under `tests/unit/`:
- Open the file
- Remove `@pytest.mark.{entity}` decorators
- Keep all non-entity markers (`@pytest.mark.fast`, `@pytest.mark.unit`, etc.)

Example transformation:
```python
# BEFORE
@pytest.mark.releases
@pytest.mark.fast
def test_release_save():
    ...

# AFTER
@pytest.mark.fast
def test_release_save():
    ...
```

**Step 2: Verify no entity markers remain in unit tests**

Run: `grep -r "@pytest.mark.releases\|@pytest.mark.issues\|@pytest.mark.labels\|@pytest.mark.milestones\|@pytest.mark.comments" tests/unit/`
Expected: No matches

**Step 3: Run unit tests to verify no breakage**

Run: `make test-unit`
Expected: All tests pass

**Step 4: Commit**

```bash
git add tests/unit/
git commit -m "refactor: remove entity markers from unit tests

Remove entity-specific pytest marker decorators from unit tests.
Entity selection now uses file paths: tests/unit/entities/{entity}/

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 4: Remove Entity Markers from Test Files (Batch 2 - Integration Tests)

**Files:**
- Modify: All files found in Task 2 under `tests/integration/`

**Step 1: Remove entity marker decorators from integration test files**

For each file found in Task 2 under `tests/integration/`:
- Open the file
- Remove `@pytest.mark.{entity}` decorators
- Remove `@pytest.mark.{entity}_integration` decorators
- Keep all non-entity markers

**Step 2: Verify no entity markers remain in integration tests**

Run: `grep -r "@pytest.mark.releases\|@pytest.mark.release_integration\|@pytest.mark.milestone_integration\|@pytest.mark.issues\|@pytest.mark.labels" tests/integration/`
Expected: No matches

**Step 3: Run integration tests to verify no breakage**

Run: `make test-integration`
Expected: All tests pass

**Step 4: Commit**

```bash
git add tests/integration/
git commit -m "refactor: remove entity markers from integration tests

Remove entity-specific pytest marker decorators from integration tests.
Entity selection now uses: pytest tests/integration/ -k {entity}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 5: Update conftest.py Auto-Marking Logic

**Files:**
- Modify: `tests/conftest.py`

**Step 1: Read current conftest.py**

Run: `cat tests/conftest.py | grep -A 20 "def pytest_collection_modifyitems"`
Purpose: Review current auto-marking logic

**Step 2: Remove entity auto-marking from conftest.py**

Edit `tests/conftest.py`, find the `pytest_collection_modifyitems()` function.

Remove these lines:
```python
        # Auto-mark by feature area based on filename
        if "sub_issues" in item.nodeid:
            item.add_marker(pytest.mark.sub_issues)
        elif "pr_" in item.nodeid or "pull_request" in item.nodeid:
            item.add_marker(pytest.mark.pull_requests)
        elif "conflict" in item.nodeid:
            item.add_marker(pytest.mark.labels)  # Conflicts typically with labels
        elif "label" in item.nodeid:
            item.add_marker(pytest.mark.labels)
        elif "issue" in item.nodeid:
            item.add_marker(pytest.mark.issues)
        elif "comment" in item.nodeid:
            item.add_marker(pytest.mark.comments)
```

Keep these sections:
```python
        # Auto-mark container tests
        if "container" in item.nodeid or "docker" in item.nodeid:
            item.add_marker(pytest.mark.container)
            item.add_marker(pytest.mark.slow)

        # Auto-mark integration tests
        elif "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.medium)

        # Auto-mark unit tests (default for non-integration/container)
        else:
            item.add_marker(pytest.mark.unit)
            item.add_marker(pytest.mark.fast)

        # Auto-mark GitHub API tests
        if hasattr(item, "function") and item.function:
            if "github" in str(item.function.__code__.co_names).lower():
                item.add_marker(pytest.mark.github_api)
```

**Step 3: Verify entity auto-marking removed**

Run: `grep -E "(sub_issues|pull_requests|labels|issues|comments)" tests/conftest.py`
Expected: No matches in auto-marking section (only in comments/docs)

**Step 4: Run fast tests to verify auto-marking still works**

Run: `make test-fast`
Expected: All tests pass, performance markers still auto-applied

**Step 5: Commit**

```bash
git add tests/conftest.py
git commit -m "refactor: remove entity auto-marking from conftest.py

Remove entity-specific auto-marking logic from test collection.
Keep performance and test-type auto-marking (unit/integration/container).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 6: Verify Makefile Commands Still Work

**Files:**
- None (verification only)

**Step 1: Test make test-fast**

Run: `make test-fast`
Expected: Tests run, excluding slow/container tests

**Step 2: Test make test-unit**

Run: `make test-unit`
Expected: Only unit tests run

**Step 3: Test make test-integration**

Run: `make test-integration`
Expected: Integration tests run, excluding container tests

**Step 4: Test make check**

Run: `make check`
Expected: All quality checks pass

**Step 5: Document verification**

No changes needed to Makefile. All commands use performance/type markers which were kept.

---

## Task 7: Update docs/testing/README.md

**Files:**
- Modify: `docs/testing/README.md`

**Step 1: Read current testing README**

Run: `cat docs/testing/README.md | grep -A 20 "Running Tests"`
Purpose: Find sections that reference entity markers

**Step 2: Add section on entity-specific test selection**

Find the section on "Running Tests by Feature" or "Test Organization" and add:

```markdown
### Running Entity-Specific Tests

Tests are organized by entity in the file structure. Use file paths or pytest's `-k` flag to run entity-specific tests.

#### By File Path (Recommended)

```bash
# All release tests
pytest tests/unit/entities/releases/

# All milestone tests
pytest tests/unit/entities/milestones/

# Multiple entities
pytest tests/unit/entities/{releases,milestones}/

# Integration tests for specific entity
pytest tests/integration/test_release_save_restore_integration.py
```

#### By Keyword Filter

```bash
# All tests with "release" in path/name
pytest tests/ -k release

# Combine with performance markers
pytest tests/ -k release -m fast

# Integration tests for releases
pytest tests/integration/ -k release
```

#### Entity Test Selection: Before vs After

| Goal | OLD (removed) | NEW (use instead) |
|------|---------------|-------------------|
| All release tests | `pytest -m releases` | `pytest tests/ -k release` |
| Release unit tests | `pytest -m "releases and unit"` | `pytest tests/unit/entities/releases/` |
| Release integration | `pytest -m release_integration` | `pytest tests/integration/ -k release` |
| Multiple entities | `pytest -m "issues or milestones"` | `pytest tests/unit/entities/{issues,milestones}/` |
```

**Step 3: Remove entity marker references**

Search for and remove or update any references to:
- `pytest -m labels`
- `pytest -m issues`
- `pytest -m releases`
- Other entity-specific markers

Replace with path-based or `-k` examples.

**Step 4: Update marker list if present**

If there's a list of available markers, update it to reflect:
- Performance markers (fast/medium/slow)
- Test type markers (unit/integration/container)
- Infrastructure markers (github_api, storage, etc.)
- Remove entity markers

**Step 5: Commit**

```bash
git add docs/testing/README.md
git commit -m "docs: update testing guide for path-based entity selection

Replace entity marker examples with path-based test selection.
Add comprehensive guide for -k flag usage.
Document before/after comparison for migration.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 8: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Read current CLAUDE.md testing section**

Run: `grep -A 30 "Testing" CLAUDE.md`
Purpose: Find marker references

**Step 2: Update marker list**

Find the section listing pytest markers and update to reflect:

```markdown
### Test Markers

This project uses pytest markers for test organization:

**Performance markers (critical for TDD workflow)**:
- `fast`: Fast tests (< 1 second) - use `make test-fast` during development
- `medium`: Medium speed tests (1-10 seconds)
- `slow`: Slow tests (> 10 seconds) - container/end-to-end

**Test type markers**:
- `unit`: Unit tests - isolated component testing
- `integration`: Integration tests - component interactions
- `container`: Container tests - full Docker workflows

**Infrastructure markers** (cross-cutting concerns):
- `github_api`: GitHub API interaction tests
- `storage`: Data storage and persistence tests
- `save_workflow`, `restore_workflow`: Operation workflow tests
- `error_handling`: Error handling and resilience tests

**Entity-specific test selection** (no markers needed):
Use file paths or `-k` flag filtering:
- `pytest tests/unit/entities/releases/` - All release unit tests
- `pytest tests/ -k release` - All tests matching "release"
- `pytest tests/integration/ -k milestone` - Milestone integration tests
```

**Step 3: Update testing examples**

Replace any examples using entity markers with path-based examples.

**Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md with simplified marker guidance

Update marker documentation to reflect entity marker removal.
Add path-based test selection examples for entity filtering.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 9: Update CONTRIBUTING.md (If Needed)

**Files:**
- Modify: `CONTRIBUTING.md` (if it references entity markers)

**Step 1: Check if CONTRIBUTING.md references entity markers**

Run: `grep -i "pytest.mark" CONTRIBUTING.md`
Expected: May or may not find references

**Step 2: If references found, update them**

Replace entity marker references with path-based selection examples.

**Step 3: If no references found, skip**

If CONTRIBUTING.md doesn't reference entity markers, no changes needed.

**Step 4: Commit (if changes made)**

```bash
git add CONTRIBUTING.md
git commit -m "docs: update CONTRIBUTING.md marker references

Replace entity marker examples with path-based test selection.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 10: Check for Entity Generator

**Files:**
- None (search and conditional update)

**Step 1: Search for entity generator**

Run: `find . -type f -name "*generate*entity*" -o -name "*entity*template*" | grep -v node_modules | grep -v ".git"`
Expected: May find entity generation scripts or templates

**Step 2: If found, check for marker generation**

Run: `grep -r "pytest.mark" {files_found_in_step_1}`
Expected: May find marker generation in templates

**Step 3: If marker generation found, remove it**

Edit entity generator templates to remove marker generation.

**Step 4: Commit (if changes made)**

```bash
git add {files_modified}
git commit -m "refactor: remove marker generation from entity templates

Entity markers no longer needed - selection via file paths.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Step 5: If not found, document**

No entity generator found, no action needed.

---

## Task 11: Final Validation - Full Test Suite

**Files:**
- None (validation only)

**Step 1: Run complete test suite**

Run: `make check-all`
Expected: All tests pass, all quality checks pass

**Step 2: Verify pytest markers**

Run: `pytest --markers`
Expected:
- Shows ~26 markers (performance, infrastructure, scenarios, etc.)
- Does NOT show entity markers (releases, issues, labels, etc.)

**Step 3: Test entity selection with paths**

Run: `pytest tests/unit/entities/releases/ -v`
Expected: Runs only release unit tests

Run: `pytest tests/integration/ -k release -v`
Expected: Runs release integration tests

**Step 4: Test entity selection with -k flag**

Run: `pytest tests/ -k milestone -v`
Expected: Runs tests matching "milestone"

**Step 5: Test performance marker selection**

Run: `pytest -m fast -v | head -20`
Expected: Runs fast tests only

Run: `pytest -m "not slow" -v | head -20`
Expected: Runs tests excluding slow tests

**Step 6: Document validation results**

All test selection methods work as expected. Migration complete.

---

## Task 12: Final Commit and Summary

**Files:**
- None (documentation only)

**Step 1: Create summary of changes**

Document changes made:
- Removed 14+ entity markers from pytest.ini
- Cleaned entity marker decorators from all test files
- Updated conftest.py auto-marking logic
- Updated documentation (testing/README.md, CLAUDE.md, CONTRIBUTING.md)
- Verified all test commands still work

**Step 2: Verify clean working tree**

Run: `git status`
Expected: Clean working tree (all changes committed)

**Step 3: Review commit log**

Run: `git log --oneline -10`
Expected: See all commits from this migration

**Step 4: Success metrics achieved**

Before:
- 40+ markers in pytest.ini
- Manual updates required for new entities
- Entity markers in test files

After:
- ~26 markers in pytest.ini (35% reduction)
- Zero pytest.ini updates for new entities
- Clean test files with only infrastructure markers
- Path-based entity selection documented

---

## Rollback Plan

If issues arise during implementation:

**Rollback markers**:
```bash
git revert {commit_hash_task_1}
```

**Rollback test changes**:
```bash
git revert {commit_hash_task_3}
git revert {commit_hash_task_4}
```

**Rollback conftest changes**:
```bash
git revert {commit_hash_task_5}
```

**Full rollback**:
```bash
git log --oneline | grep "refactor.*marker"  # Find all marker commits
git revert {hash1} {hash2} {hash3}  # Revert in reverse order
```

---

## Success Criteria

- [ ] pytest.ini has ~26 markers (no entity markers)
- [ ] No `@pytest.mark.{entity}` decorators in test files
- [ ] conftest.py has no entity auto-marking logic
- [ ] `make test-fast` works
- [ ] `make test-unit` works
- [ ] `make test-integration` works
- [ ] `make check-all` passes
- [ ] `pytest tests/unit/entities/releases/` selects release tests
- [ ] `pytest tests/ -k release` selects release tests
- [ ] `pytest --markers` shows no entity markers
- [ ] Documentation updated (testing/README.md, CLAUDE.md)
- [ ] All commits include proper commit messages

---

## Notes

- **TDD not applicable**: This is a refactoring task, not new functionality
- **Frequent commits**: Each task is one commit
- **DRY**: Use grep/sed for bulk operations when possible
- **YAGNI**: Removing markers we don't need
- **Test after each change**: Verify tests still pass after each task
