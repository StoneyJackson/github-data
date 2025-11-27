# Remaining Test Fixes After Monorepo Conversion

**Date**: 2025-11-26
**Status**: In Progress
**Context**: Phase 10 Cleanup - Test failures after monorepo conversion

## Current Test Status

### Core Package
- ✅ **69/69 tests passing (100%)**
- All fixture errors fixed
- Created missing fixtures:
  - `storage_service_for_temp_dir` (registered in conftest.py)
  - `performance_monitoring_services` (registered in conftest.py)

### GitHub-Data-Tools Package
- **462/494 tests passing (93.5%)**
- **16 errors** (fixture-related)
- **16 failures** (assertion/logic issues)
- **54 container tests** deselected (Docker build issues)

## Errors Breakdown

### 1. Docker/Container Tests (11 errors)
**Issue**: Root Dockerfile references old `github_data/` directory
**Location**: `/workspaces/github-data/Dockerfile` line 21
**Error**: `"/github_data": not found` during Docker build

**Affected Tests**:
- `TestDockerRun::test_container_runs_with_environment_variables`
- `TestDockerRun::test_container_creates_data_directory_structure`
- `TestDockerRun::test_container_handles_missing_environment_variables`
- `TestDockerRun::test_container_python_path_configuration`
- `TestDockerRun::test_container_working_directory`
- And 6 more in `test_docker_container.py`

**Required Fix**:
1. Update root `Dockerfile` to use monorepo package structure
2. Update package-specific Dockerfiles in:
   - `packages/github-data-tools/Dockerfile`
   - `packages/git-repo-tools/Dockerfile`
   - `packages/kit-orchestrator/Dockerfile`
   - `packages/github-repo-manager/Dockerfile`
3. Update container tests to build from new structure

### 2. Missing Fixtures (5+ errors)
**Issue**: Tests reference fixtures that were never implemented

**Missing Fixtures**:
1. `github_data_builder` - Used in:
   - `test_graphql_paginator_unit.py::test_pagination_with_github_data_builder`
   - `test_graphql_paginator_unit.py::test_pagination_with_parametrized_data_factory`

2. Other fixture-related errors in:
   - `test_rate_limit_handling_unit.py::test_service_uses_rate_limiting_for_data_operations`
   - `test_rate_limit_handling_unit.py::test_service_rate_limiting_with_retry`

**Required Fix**:
1. Identify all missing fixtures
2. Determine if fixtures should be:
   - Implemented (if tests are valid)
   - Tests should be removed (if fixtures were never meant to exist)
   - Tests should be updated to use different fixtures

### 3. Test Failures (16 failures)
**Issue**: Logic/assertion failures unrelated to fixtures

**Required Fix**:
1. Run detailed failure analysis:
   ```bash
   pdm run pytest packages/github-data-tools/tests -m "not container" --tb=short -v | grep FAILED
   ```
2. Fix each failing test individually
3. Verify fixes don't break other tests

## Work Completed This Session

### ✅ Fixed Issues
1. **Entity Registry Discovery** - Updated ConverterRegistry to use new package structure
2. **Module Path References** - Fixed imports from `github_data` to `github_data_tools`/`github_data_core`
3. **Git Repository Entity** - Handled cross-package entity references
4. **Converter Location Tests** - Updated assertions for new package paths
5. **Core Package Fixtures** - Registered all required fixtures in conftest.py
6. **Test Failures** - Fixed all 4 test failures (0 failures now in github-data-tools)

### Test Progress
- **Before**: 421 passing, 4 failures, 11 errors
- **After Phase 1**: 491 passing, 0 failures, 32 errors
- **After Priority 1 Fixes**: 475 passing (non-container), 19 failures, 0 errors
- **Improvement**: All Priority 1 fixture errors resolved ✅

## Recommended Next Steps

### ✅ Priority 1: Fix Remaining Non-Container Errors (COMPLETED)

**Status**: All non-container fixture errors have been resolved.

**Fixtures Created**:
1. `all_entity_names` - Returns list of all entity names from EntityRegistry
2. `enabled_entity_names` - Returns list of enabled entity names
3. `validate_github_service_registry` - Provides GitHubService with validated registry
4. `github_data_builder` - Builder for creating test data with fluent interface
5. `parametrized_data_factory` - Factory for scenario-based test data
6. `integration_test_environment` - Test environment with test data
7. `rate_limiting_test_services` - Services for rate limiting tests
8. `performance_monitoring_services` - Services for performance monitoring
9. `temp_data_dir` - Temporary directory for test data

**Additional Fixes**:
- Fixed incorrect `RateLimitHandler` imports in workflow service fixtures
- Updated all workflow service fixtures to remove deprecated rate_limiter usage

**Result**: 0 fixture errors (down from 32 errors)

### Priority 2: Fix Test Failures (16 failures)
1. Get detailed failure list:
   ```bash
   pdm run pytest packages/github-data-tools/tests -m "not container" -v --tb=line | grep "FAILED"
   ```

2. Analyze common patterns in failures
3. Fix systematically by category

### Priority 3: Docker/Container Tests (11 errors)
This is lower priority as container tests are slow and typically excluded from regular test runs.

1. Update root Dockerfile for monorepo structure
2. Test Docker build manually
3. Update container test expectations
4. Re-enable container tests

## Success Criteria

### Minimum (Acceptable)
- ✅ Core package: 100% passing (ACHIEVED)
- ⏳ GitHub-data-tools: 95%+ passing (non-container tests)
- ⏳ Document all remaining issues

### Target (Ideal)
- ✅ Core package: 100% passing (ACHIEVED)
- ⏳ GitHub-data-tools: 100% passing (non-container tests)
- ⏳ Container tests: Documented path to fix

### Stretch (Future Work)
- ⏳ All packages: 100% passing including container tests
- ⏳ Docker builds working in monorepo structure
- ⏳ CI/CD updated for monorepo

## Notes

- Container tests (54 tests) are marked as `@pytest.mark.container` and excluded from fast test runs
- The `make test-fast` command excludes container tests by design
- Most development work can proceed with current test status
- Docker functionality will need attention before production deployment
