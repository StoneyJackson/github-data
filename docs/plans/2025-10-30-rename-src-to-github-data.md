# Rename src Package to github_data Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rename the top-level `src/` package to `github_data/` to align with Python best practices and project naming conventions.

**Architecture:** Use git mv to preserve file history, then automated search/replace for all 140 import references (82 in tests, 58 in source), followed by manual configuration updates.

**Tech Stack:** Git, sed, Python packaging (PDM), Docker

---

## Task 1: Establish Baseline

**Files:**
- Verify: all test files, source files

**Step 1: Run fast test suite to establish baseline**

Run: `make test-fast`

Expected: All tests pass (or document any existing failures)

**Step 2: Check for any uncommitted changes**

Run: `git status`

Expected: Clean working directory on branch `refactor/rename-src-to-github-data`

**Step 3: Document current state**

Run:
```bash
grep -r "from src\." --include="*.py" . | wc -l
grep -r "import src\." --include="*.py" . | wc -l
grep -r "^import src$" --include="*.py" . | wc -l
```

Expected: Count of import statements (should be ~140 total)

---

## Task 2: Rename Directory

**Files:**
- Rename: `src/` → `github_data/`

**Step 1: Execute git mv to preserve history**

Run: `git mv src github_data`

Expected: Directory renamed, git tracks as rename operation

**Step 2: Verify git status shows rename**

Run: `git status`

Expected:
```
renamed:    src/ -> github_data/
```

**Step 3: Commit the rename**

Run:
```bash
git commit -m "refactor: rename src directory to github_data

Rename top-level package from src/ to github_data/ to align with
Python packaging best practices. This preserves git history.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

Expected: Commit created successfully

---

## Task 3: Update Import Statements - Pattern 1

**Files:**
- Modify: All `*.py` files with pattern `from src.`

**Step 1: Update "from src." imports**

Run:
```bash
find . -name "*.py" -type f -exec sed -i 's/from src\./from github_data./g' {} +
```

Expected: All `from src.module` changed to `from github_data.module`

**Step 2: Verify changes with sample**

Run: `grep "from github_data\." tests/unit/test_main_registry.py | head -3`

Expected: See updated imports like `from github_data.entities.registry`

**Step 3: Check for remaining "from src." patterns**

Run: `grep -r "from src\." --include="*.py" . | wc -l`

Expected: 0 matches

---

## Task 4: Update Import Statements - Pattern 2

**Files:**
- Modify: All `*.py` files with pattern `import src.`

**Step 1: Update "import src." imports**

Run:
```bash
find . -name "*.py" -type f -exec sed -i 's/import src\./import github_data./g' {} +
```

Expected: All `import src.module` changed to `import github_data.module`

**Step 2: Check for remaining "import src." patterns**

Run: `grep -r "import src\." --include="*.py" . | wc -l`

Expected: 0 matches

---

## Task 5: Update Import Statements - Pattern 3

**Files:**
- Modify: All `*.py` files with pattern `import src` (standalone)

**Step 1: Update standalone "import src" statements**

Run:
```bash
find . -name "*.py" -type f -exec sed -i 's/^import src$/import github_data/g' {} +
```

Expected: Any standalone `import src` changed to `import github_data`

**Step 2: Check for remaining "import src" patterns**

Run: `grep -r "^import src$" --include="*.py" . | wc -l`

Expected: 0 matches

**Step 3: Commit import updates**

Run:
```bash
git add -A
git commit -m "refactor: update all Python imports from src to github_data

Update 140+ import statements across source and test files to reference
the renamed github_data package.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

Expected: Commit created successfully

---

## Task 6: Update pyproject.toml

**Files:**
- Modify: `pyproject.toml:48`

**Step 1: Update CLI entry point**

Change line 48 from:
```toml
github-data = "src.main:main"
```

To:
```toml
github-data = "github_data.main:main"
```

**Step 2: Verify the change**

Run: `grep "github_data.main:main" pyproject.toml`

Expected: Line shows `github-data = "github_data.main:main"`

**Step 3: Commit configuration update**

Run:
```bash
git add pyproject.toml
git commit -m "refactor: update pyproject.toml entry point to github_data

Update CLI entry point from src.main:main to github_data.main:main

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

Expected: Commit created successfully

---

## Task 7: Update Dockerfile

**Files:**
- Modify: `Dockerfile:21,33`

**Step 1: Update COPY directive**

Change line 21 from:
```dockerfile
COPY src/ ./src/
```

To:
```dockerfile
COPY github_data/ ./github_data/
```

**Step 2: Update CMD directive**

Change line 33 from:
```dockerfile
CMD ["pdm", "run", "python", "-m", "src.main"]
```

To:
```dockerfile
CMD ["pdm", "run", "python", "-m", "github_data.main"]
```

**Step 3: Verify both changes**

Run: `grep "github_data" Dockerfile`

Expected: See both `COPY github_data/` and `python -m github_data.main`

**Step 4: Commit Dockerfile update**

Run:
```bash
git add Dockerfile
git commit -m "refactor: update Dockerfile to use github_data package

Update COPY and CMD directives to reference renamed package

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

Expected: Commit created successfully

---

## Task 8: Comprehensive Verification

**Files:**
- Verify: All modified files

**Step 1: Search for any remaining "src" references**

Run:
```bash
grep -r "from src\." --include="*.py" .
grep -r "import src\." --include="*.py" .
grep -r "import src$" --include="*.py" .
```

Expected: No matches (empty output)

**Step 2: Check git status**

Run: `git status`

Expected: Clean working directory (all changes committed)

**Step 3: Review commit history**

Run: `git log --oneline -5`

Expected: See 4 new commits for rename, imports, pyproject.toml, and Dockerfile

---

## Task 9: Run Tests

**Files:**
- Verify: All test files

**Step 1: Run fast test suite**

Run: `make test-fast`

Expected: All tests pass

**Step 2: Run full test suite including container tests**

Run: `make test`

Expected: All tests pass with coverage report

**Step 3: Document any test failures**

If any tests fail:
- Document the failure
- Investigate if related to rename
- Fix if necessary

Expected: No failures related to package rename

---

## Task 10: Run Quality Checks

**Files:**
- Verify: All source files

**Step 1: Run linting**

Run: `make lint`

Expected: No linting errors

**Step 2: Run type checking**

Run: `make type-check`

Expected: No mypy errors

**Step 3: Run code formatting check**

Run: `make format`

Expected: No formatting changes needed

---

## Task 11: Build Docker Image

**Files:**
- Verify: `Dockerfile`, `github_data/`

**Step 1: Build Docker image**

Run: `make docker-build`

Expected: Image builds successfully with output:
```
Successfully built <image-id>
Successfully tagged github-data:latest
```

**Step 2: Verify image exists**

Run: `docker images github-data`

Expected: See the github-data:latest image listed

**Step 3: Test running the container (optional smoke test)**

Run:
```bash
docker run --rm github-data:latest --help
```

Expected: Help message displays without errors

---

## Task 12: Final Review and Documentation

**Files:**
- Review: All changed files
- Update: `docs/plans/2025-10-30-rename-src-to-github-data.md` (this file)

**Step 1: Review all commits on branch**

Run: `git log main..HEAD --oneline`

Expected: See all 4 commits for this refactor

**Step 2: Verify branch is ready for PR**

Run: `git diff main...HEAD --stat`

Expected: See summary of all changed files

**Step 3: Document completion**

Add to this plan:
```
## Completion Checklist

- [x] Directory renamed with git mv
- [x] All import statements updated
- [x] pyproject.toml entry point updated
- [x] Dockerfile updated
- [x] All tests passing
- [x] Quality checks passing
- [x] Docker image builds successfully
- [x] Ready for PR to main branch
```

---

## Verification Checklist

After all tasks complete, verify:

- [ ] `git grep "from src\."` returns nothing
- [ ] `git grep "import src\."` returns nothing
- [ ] `git grep "^import src$"` returns nothing
- [ ] `make test-fast` passes
- [ ] `make test` passes
- [ ] `make lint` passes
- [ ] `make type-check` passes
- [ ] `make docker-build` succeeds
- [ ] All commits follow conventional commits format
- [ ] Branch ready for PR or merge

---

## Rollback Procedure

If issues arise:

1. **Before final verification:** `git reset --hard <commit-before-changes>`
2. **After merge:** Revert the merge commit
3. **Nuclear option:** Delete branch and start over

---

## Next Steps After Completion

1. Push branch to remote: `git push -u origin refactor/rename-src-to-github-data`
2. Create pull request to main branch
3. Request code review
4. Merge after approval
5. Developers pull and refresh IDE indexes
