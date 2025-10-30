# Design: Rename src Package to github_data

**Date:** 2025-10-30
**Status:** Approved
**Branch:** `refactor/rename-src-to-github-data`

## Overview

Rename the top-level Python package from `src/` to `github_data/` to follow Python best practices where the package name aligns with the project name (already defined as "github-data" in pyproject.toml).

## Motivation

The generic `src/` directory name is acceptable but doesn't follow the Python community convention of naming packages to match project identity. Using `github_data/` provides:
- Better alignment with the project name "github-data"
- Clearer intent when the package is imported
- Standard Python packaging practice

## Current State

- **Package location:** `src/` directory with subdirectories (entities, operations, github, git, storage, tools, utils, config)
- **Import references:** 140 total (82 in tests, 58 in source files)
- **Entry point:** `pyproject.toml` line 48 defines `github-data = "src.main:main"`
- **Docker references:** Dockerfile lines 21 and 33

## Design Approach

### Selected Strategy: Git mv + Automated Search/Replace

Use `git mv` to preserve file history, then automated find/replace for all imports. This approach:
- Preserves complete git history (blame, log --follow)
- Handles all 140 import updates consistently
- Minimizes manual error potential
- Fast execution

### Four-Phase Workflow

#### Phase 1: Branch Creation
Create feature branch: `refactor/rename-src-to-github-data`

#### Phase 2: Physical Rename
```bash
git mv src github_data
```

Git will track this as a rename operation, preserving history.

#### Phase 3: Import Statement Updates

Target patterns:
- `from src.` → `from github_data.`
- `import src.` → `import github_data.`
- `import src` → `import github_data`

Automated replacement:
```bash
find . -name "*.py" -type f -exec sed -i 's/from src\./from github_data./g' {} +
find . -name "*.py" -type f -exec sed -i 's/import src\./import github_data./g' {} +
find . -name "*.py" -type f -exec sed -i 's/import src$/import github_data/g' {} +
```

#### Phase 4: Configuration Updates

**pyproject.toml** (line 48):
```toml
# Before
github-data = "src.main:main"

# After
github-data = "github_data.main:main"
```

**Dockerfile**:
```dockerfile
# Line 21: Before
COPY src/ ./src/

# Line 21: After
COPY github_data/ ./github_data/

# Line 33: Before
CMD ["pdm", "run", "python", "-m", "src.main"]

# Line 33: After
CMD ["pdm", "run", "python", "-m", "github_data.main"]
```

## Verification Strategy

Run comprehensive validation in order:

1. **Grep verification**: Confirm no remaining `src` imports
2. **PDM lock**: `pdm lock` (verify lock file consistency)
3. **Fast tests**: `make test-fast` (non-container tests)
4. **Linting**: `make lint`
5. **Type checking**: `make type-check`
6. **Full test suite**: `make test` (including container tests)
7. **Docker build**: `make docker-build`

All checks must pass before considering the refactor complete.

## Error Handling

### Potential Issues

| Issue | Mitigation |
|-------|-----------|
| Missed imports | Verify with grep after sed commands |
| Cached bytecode | Git handles `__pycache__` (gitignored) automatically |
| IDE configurations | Not version-controlled; developers refresh after pull |

### Rollback Plan

- **Before merge:** `git reset --hard` or abandon branch
- **After merge:** Revert the merge commit

## Success Criteria

- All 140 import references updated correctly
- All tests pass (unit, integration, container)
- Docker image builds successfully
- No linting or type-checking errors
- Git history preserved for all files

## Impact Analysis

### Developer Impact
- Minimal: One-time pull of the branch and IDE refresh
- No API or behavior changes

### CI/CD Impact
- None: Branch-based workflow isolates changes until merge

### Deployment Impact
- Docker image name unchanged
- Container behavior unchanged (internal package name only)

## Timeline

Estimated implementation: 30 minutes
- Branch setup: 2 minutes
- Rename + updates: 10 minutes
- Verification: 15 minutes
- Documentation: 3 minutes
