# Use Cases Reorganization Plan: Operation-Based Structure

**Date:** 2025-09-18 13:45  
**Status:** Planning Phase  
**Impact:** Major refactoring of use cases directory structure  

## Current State Analysis

The current `src/use_cases/` structure has **10 directories** with scattered responsibilities:
- `collection/` - Data collection from GitHub API (6 files)
- `loading/` - Loading data from JSON files (6 files) 
- `persistence/` - Saving data to JSON files (6 files)
- `restoration/` - Restoring data to GitHub (6 files)
- `jobs/` - Job execution for restoration (5 files)
- `orchestration/` - High-level save/restore orchestration (2 files)
- `processing/` - Data processing and validation (2 files)
- `conflict_resolution/` - Conflict handling
- `validation/` - Data validation
- `sub_issue_management/` - Sub-issue specific logic

**Current Issues:**
- Related functionality is scattered across multiple directories
- Save and restore operations are not clearly separated
- Difficult to locate operation-specific code
- Complex import paths and dependencies
- Mixed responsibilities within directories

## Proposed Structure: Operation-Based Organization

### New Directory Structure
```
src/use_cases/
├── save/
│   ├── orchestration/
│   │   └── save_repository.py (moved from orchestration/)
│   ├── collection/
│   │   ├── collect_labels.py
│   │   ├── collect_issues.py
│   │   ├── collect_comments.py
│   │   ├── collect_pull_requests.py
│   │   ├── collect_pr_comments.py
│   │   └── collect_sub_issues.py
│   ├── processing/
│   │   ├── associate_sub_issues.py (moved from processing/)
│   │   └── validate_repository_access.py (shared logic)
│   └── persistence/
│       ├── save_labels.py
│       ├── save_issues.py
│       ├── save_comments.py
│       ├── save_pull_requests.py
│       ├── save_pr_comments.py
│       └── save_sub_issues.py
├── restore/
│   ├── orchestration/
│   │   └── restore_repository.py (moved from orchestration/)
│   ├── loading/
│   │   ├── load_labels.py
│   │   ├── load_issues.py
│   │   ├── load_comments.py
│   │   ├── load_pull_requests.py
│   │   ├── load_pr_comments.py
│   │   └── load_sub_issues.py
│   ├── validation/
│   │   └── validate_restore_data.py (moved from validation/)
│   ├── jobs/
│   │   ├── restore_labels_job.py
│   │   ├── restore_issues_job.py
│   │   ├── restore_comments_job.py
│   │   ├── restore_pull_requests_job.py
│   │   └── restore_sub_issues_job.py
│   ├── conflict_resolution/
│   │   └── [existing conflict resolution files]
│   ├── restoration/
│   │   ├── restore_labels.py
│   │   ├── restore_issues.py
│   │   ├── restore_comments.py
│   │   ├── restore_pull_requests.py
│   │   ├── restore_pr_comments.py
│   │   └── restore_sub_issues.py
│   └── sub_issue_management/
│       └── [existing sub-issue management files]
├── shared/
│   ├── processing/
│   │   └── validate_repository_access.py (shared between save/restore)
│   └── base/
│       └── [shared base classes and utilities]
└── requests.py (stays at root level)
```

## Migration Steps

### Phase 1: Create New Directory Structure
1. Create `src/use_cases/save/` directory with subdirectories:
   - `save/orchestration/`
   - `save/collection/`
   - `save/processing/`
   - `save/persistence/`
2. Create `src/use_cases/restore/` directory with subdirectories:
   - `restore/orchestration/`
   - `restore/loading/`
   - `restore/validation/`
   - `restore/jobs/`
   - `restore/conflict_resolution/`
   - `restore/restoration/`
   - `restore/sub_issue_management/`
3. Create `src/use_cases/shared/` directory with subdirectories:
   - `shared/processing/`
   - `shared/base/`

### Phase 2: Move Save-Related Files
1. Move `orchestration/save_repository.py` → `save/orchestration/save_repository.py`
2. Move all `collection/` files → `save/collection/`:
   - `collect_labels.py`
   - `collect_issues.py`
   - `collect_comments.py`
   - `collect_pull_requests.py`
   - `collect_pr_comments.py`
   - `collect_sub_issues.py`
3. Move all `persistence/` files → `save/persistence/`:
   - `save_labels.py`
   - `save_issues.py`
   - `save_comments.py`
   - `save_pull_requests.py`
   - `save_pr_comments.py`
   - `save_sub_issues.py`
4. Move save-specific processing files → `save/processing/`:
   - `associate_sub_issues.py` (from processing/)

### Phase 3: Move Restore-Related Files  
1. Move `orchestration/restore_repository.py` → `restore/orchestration/restore_repository.py`
2. Move all `loading/` files → `restore/loading/`:
   - `load_labels.py`
   - `load_issues.py`
   - `load_comments.py`
   - `load_pull_requests.py`
   - `load_pr_comments.py`
   - `load_sub_issues.py`
3. Move all `restoration/` files → `restore/restoration/`:
   - `restore_labels.py`
   - `restore_issues.py`
   - `restore_comments.py`
   - `restore_pull_requests.py`
   - `restore_pr_comments.py`
   - `restore_sub_issues.py`
4. Move all `jobs/` files → `restore/jobs/`:
   - `restore_labels_job.py`
   - `restore_issues_job.py`
   - `restore_comments_job.py`
   - `restore_pull_requests_job.py`
   - `restore_sub_issues_job.py`
5. Move entire directories:
   - `conflict_resolution/` → `restore/conflict_resolution/`
   - `validation/` → `restore/validation/`
   - `sub_issue_management/` → `restore/sub_issue_management/`

### Phase 4: Handle Shared Components
1. Move shared processing logic → `shared/processing/`:
   - `validate_repository_access.py` (used by both save and restore)
2. Identify and move shared base classes → `shared/base/`
3. Keep `requests.py` at root level as it's used by both operations

### Phase 5: Update Imports and Dependencies
1. Update all import statements throughout the codebase:
   - Search for imports from old paths
   - Replace with new operation-based paths
   - Example: `from ..collection.collect_labels` → `from ..save.collection.collect_labels`
2. Update `__init__.py` files in all directories:
   - Create new `__init__.py` files for new directories
   - Update existing ones to reflect new structure
3. Update test imports:
   - Search test files for use_cases imports
   - Update to match new structure

### Phase 6: Validation and Clean Up
1. Run comprehensive tests to ensure all imports work:
   - `make test-fast` - Unit and integration tests
   - `make type-check` - Type checking with mypy
   - `make lint` - Code quality checks
2. Remove empty original directories:
   - Delete old `collection/`, `loading/`, `persistence/`, `restoration/`, `jobs/`, `processing/`, `validation/`, `sub_issue_management/` directories
   - Keep `orchestration/` only if it has other shared files
3. Update documentation:
   - Update any architectural documentation
   - Update developer guides
   - Update import examples in docs

## Benefits

### Clear Separation of Concerns
- **Save Operations**: All save-related functionality grouped under `save/`
- **Restore Operations**: All restore-related functionality grouped under `restore/`
- **Shared Components**: Common utilities and base classes in `shared/`

### Improved Maintainability
- **Logical Grouping**: Related functionality is co-located
- **Easier Navigation**: Developers can quickly find operation-specific code
- **Reduced Cognitive Load**: Focus only on relevant operation when working

### Enhanced Scalability
- **Easy Extension**: Simple to add new save or restore features
- **Clear Patterns**: Consistent organization makes adding new entity types straightforward
- **Modular Design**: Each operation can evolve independently

### Better Developer Experience
- **Intuitive Structure**: Directory names clearly indicate purpose
- **Shorter Import Paths**: More direct imports within operations
- **Reduced Confusion**: No ambiguity about where functionality belongs

## Impact Assessment

### Files Affected
- **55 Python files** need to be moved across 10 directories
- **Import statements** across the entire codebase need updates
- **Test files** may need import path updates
- **__init__.py files** need creation/modification

### Risk Mitigation
- **Comprehensive Testing**: Run full test suite after each phase
- **Incremental Migration**: Move files in logical groups to minimize breakage
- **Import Verification**: Use IDE/tools to verify all imports resolve correctly
- **Rollback Plan**: Keep git commits granular for easy rollback if needed

### Compatibility
- **External APIs**: No changes to public interfaces
- **CI/CD**: Should continue working as module structure is preserved
- **Docker**: No impact on containerization
- **CLI**: No changes to command-line interface

## Success Criteria

1. **All tests pass** after migration completion
2. **No broken imports** - all import statements resolve correctly
3. **Type checking passes** - mypy reports no new errors
4. **Code quality maintained** - linting passes with same or better scores
5. **Documentation updated** - all references to old structure are corrected
6. **Developer workflow unaffected** - all make commands continue to work

## Timeline Estimate

- **Phase 1-2 (Save Operations)**: 2-3 hours
- **Phase 3 (Restore Operations)**: 3-4 hours  
- **Phase 4 (Shared Components)**: 1-2 hours
- **Phase 5 (Import Updates)**: 3-4 hours
- **Phase 6 (Validation/Cleanup)**: 1-2 hours

**Total Estimated Time**: 10-15 hours

## Dependencies

- No external dependencies required
- Requires careful coordination if multiple developers are working on use cases
- Should be done when no major feature development is in progress on use cases