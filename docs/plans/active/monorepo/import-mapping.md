# Import Mapping - Monorepo Conversion

**Date**: 2025-11-24
**Purpose**: Map incorrect test imports to correct monorepo structure

## Investigation Summary

### Actual Module Structure

**Core Package** (`github_data_core`):
```
github_data_core/
├── entities/
│   ├── base.py
│   ├── registry.py          ← EntityRegistry IS HERE
│   └── strategy_context.py  ← StrategyContext IS HERE
├── operations/
│   ├── orchestrator_base.py
│   └── strategy_factory.py  ← StrategyFactory IS HERE
└── storage/
    ├── json_storage.py
    └── protocols.py
```

**Git-Repo-Tools Package** (`git_repo_tools`):
```
git_repo_tools/
├── entities/
│   ├── entity_config.py     ← GitRepositoryEntityConfig
│   ├── models.py            ← GitBackupFormat
│   ├── restore_strategy.py
│   └── save_strategy.py
└── git/
    └── service.py
```

**GitHub-Data-Tools Package** (`github_data_tools`):
```
github_data_tools/
├── entities/
│   ├── comments/
│   ├── issues/
│   ├── labels/
│   ├── milestones/
│   ├── pr_comments/
│   ├── pr_review_comments/
│   ├── pr_reviews/
│   ├── pull_requests/
│   ├── releases/
│   └── sub_issues/
├── github/
│   ├── boundary.py
│   ├── service.py
│   └── utils/
└── operations/
    ├── restore/
    │   └── orchestrator.py   ← StrategyBasedRestoreOrchestrator
    └── save/
        └── orchestrator.py   ← StrategyBasedSaveOrchestrator
```

## Import Mappings

### Core Infrastructure Imports

**EntityRegistry**:
- ❌ Wrong: `from github_data_tools.entities.registry import EntityRegistry`
- ❌ Wrong: `from git_repo_tools.entities.registry import EntityRegistry`
- ✅ Correct: `from github_data_core.entities.registry import EntityRegistry`

**StrategyContext**:
- ❌ Wrong: `from github_data_tools.entities.strategy_context import StrategyContext`
- ❌ Wrong: `from git_repo_tools.entities.strategy_context import StrategyContext`
- ✅ Correct: `from github_data_core.entities.strategy_context import StrategyContext`

**StrategyFactory**:
- ❌ Wrong: `from github_data_tools.operations.strategy_factory import StrategyFactory`
- ✅ Correct: `from github_data_core.operations.strategy_factory import StrategyFactory`

### Git-Repo-Tools Imports

**GitRepositoryEntityConfig**:
- ❌ Wrong: `from git_repo_tools.entities.git_repositories.entity_config import GitRepositoryEntityConfig`
- ✅ Correct: `from git_repo_tools.entities.entity_config import GitRepositoryEntityConfig`

**GitBackupFormat**:
- ❌ Wrong: `from git_repo_tools.entities.git_repositories.models import GitBackupFormat`
- ✅ Correct: `from git_repo_tools.entities.models import GitBackupFormat`

### GitHub-Data-Tools Imports

Entity-specific imports are correct - they DO have subdirectories:
- ✅ `from github_data_tools.entities.issues.entity_config import ...`
- ✅ `from github_data_tools.entities.labels.converters import ...`
- ✅ `from github_data_tools.entities.releases.models import ...`

## Fix Strategy

### Pattern 1: Core Infrastructure (applies to ALL packages' tests)
```bash
# Fix EntityRegistry imports
find packages/*/tests -name "*.py" -exec sed -i \
  's/from github_data_tools\.entities\.registry import/from github_data_core.entities.registry import/g' {} \;
find packages/*/tests -name "*.py" -exec sed -i \
  's/from git_repo_tools\.entities\.registry import/from github_data_core.entities.registry import/g' {} \;

# Fix StrategyContext imports
find packages/*/tests -name "*.py" -exec sed -i \
  's/from github_data_tools\.entities\.strategy_context import/from github_data_core.entities.strategy_context import/g' {} \;
find packages/*/tests -name "*.py" -exec sed -i \
  's/from git_repo_tools\.entities\.strategy_context import/from github_data_core.entities.strategy_context import/g' {} \;

# Fix StrategyFactory imports
find packages/*/tests -name "*.py" -exec sed -i \
  's/from github_data_tools\.operations\.strategy_factory import/from github_data_core.operations.strategy_factory import/g' {} \;
```

### Pattern 2: Git-Repo-Tools Specific
```bash
# Fix git_repositories submodule references
find packages/git-repo-tools/tests -name "*.py" -exec sed -i \
  's/from git_repo_tools\.entities\.git_repositories\./from git_repo_tools.entities./g' {} \;
```

### Pattern 3: Pydantic Dependency
```bash
# Add pydantic to core package
cd packages/core
pdm add --dev pydantic
cd ../..
pdm lock
pdm install --dev
```

## Expected Impact

### Pattern 1 Fixes:
- **13 integration tests** in github-data-tools (EntityRegistry, StrategyFactory imports)
- **50+ unit tests** in github-data-tools (StrategyContext, StrategyFactory imports)
- **3 unit tests** in git-repo-tools (StrategyContext imports)

### Pattern 2 Fixes:
- **3 unit tests** in git-repo-tools (git_repositories submodule)

### Pattern 3 Fixes:
- **1 unit test** in core (pydantic dependency)

**Total**: All 67 failing tests should be fixed by these three patterns.

## Verification Commands

```bash
# After fixes, verify each package
pdm run pytest packages/core/tests/ -m "not container" -v
pdm run pytest packages/git-repo-tools/tests/ -m "not container" -v
pdm run pytest packages/github-data-tools/tests/ -m "not container" -v

# Verify all together
pdm run pytest packages/ -m "not container and not slow" -v
```
