# Test Framework Migration Plan

**Date**: 2025-09-21 01:51
**Task**: Migrate existing tests to new Advanced Testing Patterns framework
**Goal**: Reorganize test structure according to testing.md Advanced Testing Patterns section

## Current State Analysis

### Existing Test Structure
```
tests/
├── __init__.py
├── conftest.py
├── shared/                              ✅ Already migrated
│   ├── __init__.py
│   ├── fixtures.py                      ✅ Core and enhanced fixtures
│   ├── enhanced_fixtures.py             ✅ Advanced testing patterns
│   ├── mocks.py                         ✅ Mock utilities and factories
│   ├── builders.py                      ✅ Data builder patterns
│   └── helpers.py
├── integration/                         ✅ Partially migrated
│   ├── __init__.py
│   ├── test_issues_integration.py
│   ├── test_save_restore_workflows.py
│   ├── test_error_handling_integration.py
│   ├── test_labels_integration.py
│   └── test_file_operations.py
├── github/
│   └── utils/
│       ├── __init__.py
│       ├── test_graphql_paginator.py
│       └── test_data_enrichment.py
├── mocks/                               ✅ Already migrated
│   ├── __init__.py
│   ├── mock_github_service.py
│   └── mock_storage_service.py
└── [ROOT LEVEL TEST FILES - NEED MIGRATION]
    ├── test_main.py                     🔄 Needs migration to unit/
    ├── test_json_storage.py             🔄 Needs migration to unit/
    ├── test_rate_limit_handling.py      🔄 Needs migration to unit/
    ├── test_graphql_integration.py      🔄 Needs migration to integration/
    ├── test_metadata.py                 🔄 Needs migration to unit/
    ├── test_dependency_injection.py     🔄 Needs migration to unit/
    ├── test_integration.py              🔄 Needs migration to integration/
    ├── test_container_integration.py    🔄 Needs migration to container/
    ├── test_docker_compose_integration.py 🔄 Needs migration to container/
    ├── test_pr_integration.py           🔄 Needs migration to integration/
    ├── test_conflict_strategies.py      🔄 Needs migration to unit/
    └── test_sub_issues_integration.py   🔄 Needs migration to integration/
```

### Target Structure (per testing.md Advanced Testing Patterns)
```
tests/
├── unit/                         # Unit tests (fast, isolated) - NEW DIRECTORY
├── integration/                  # Integration tests (service interactions) - EXISTS
├── container/                    # Container integration tests - NEW DIRECTORY
└── shared/                       # Shared test infrastructure - EXISTS
    ├── fixtures.py               # Core and enhanced fixtures - EXISTS
    ├── enhanced_fixtures.py      # Advanced testing patterns - EXISTS
    ├── mocks.py                  # Mock utilities and factories - EXISTS
    └── builders.py               # Data builder patterns - EXISTS
```

## Migration Tasks

### Phase 1: Create Missing Directory Structure

1. **Create `tests/unit/` directory**
   - Create `tests/unit/__init__.py`
   - Add appropriate pytestmark configuration

2. **Create `tests/container/` directory**
   - Create `tests/container/__init__.py`
   - Add appropriate pytestmark configuration

### Phase 2: Migrate Unit Tests

**Tests to migrate to `tests/unit/`:**

1. **test_main.py** → `tests/unit/test_main_unit.py`
   - Currently: ✅ Has `pytestmark = [pytest.mark.unit]`
   - Action: Move and rename following naming convention

2. **test_json_storage.py** → `tests/unit/test_json_storage_unit.py`
   - Currently: ✅ Has `pytestmark = [pytest.mark.unit]`
   - Action: Move and rename

3. **test_rate_limit_handling.py** → `tests/unit/test_rate_limit_handling_unit.py`
   - Action: Analyze content and add unit markers if missing

4. **test_metadata.py** → `tests/unit/test_metadata_unit.py`
   - Action: Analyze content and add unit markers if missing

5. **test_dependency_injection.py** → `tests/unit/test_dependency_injection_unit.py`
   - Action: Analyze content and add unit markers if missing

6. **test_conflict_strategies.py** → `tests/unit/test_conflict_strategies_unit.py`
   - Action: Analyze content and add unit markers if missing

7. **tests/github/utils/test_graphql_paginator.py** → `tests/unit/test_graphql_paginator_unit.py`
   - Action: Move from nested structure and add unit markers

8. **tests/github/utils/test_data_enrichment.py** → `tests/unit/test_data_enrichment_unit.py`
   - Action: Move from nested structure and add unit markers

### Phase 3: Migrate Integration Tests

**Tests to migrate to `tests/integration/`:**

1. **test_integration.py** → `tests/integration/test_save_restore_integration.py`
   - Currently: ✅ Has `pytestmark = [pytest.mark.integration]`
   - Action: Move and rename with more descriptive name

2. **test_graphql_integration.py** → `tests/integration/test_graphql_integration.py`
   - Action: Move to integration directory and verify markers

3. **test_pr_integration.py** → `tests/integration/test_pr_integration.py`
   - Action: Move to integration directory and verify markers

4. **test_sub_issues_integration.py** → `tests/integration/test_sub_issues_integration.py`
   - Action: Move to integration directory and verify markers

### Phase 4: Migrate Container Tests

**Tests to migrate to `tests/container/`:**

1. **test_container_integration.py** → `tests/container/test_docker_container.py`
   - Currently: ✅ Has full container markers: `[pytest.mark.container, pytest.mark.integration, pytest.mark.slow]`
   - Action: Move and rename

2. **test_docker_compose_integration.py** → `tests/container/test_docker_compose_container.py`
   - Action: Move and add container markers if missing

### Phase 5: Update Import Paths and References

After moving files, update:

1. **Import statements** in test files that reference moved modules
2. **pytest.ini** test discovery paths if needed
3. **Makefile** test command paths if needed
4. **Documentation** references to test locations

### Phase 6: Clean Up Legacy Structure

1. **Remove empty directories:**
   - `tests/github/utils/` (after moving unit tests)
   - `tests/github/` (if empty)

2. **Update conftest.py** if it has path-specific configurations

## Implementation Steps

### Step 1: Analyze Current Marker Usage
For each file to be migrated, verify:
- Current pytest markers
- Test execution speed (fast/medium/slow)
- Dependencies (mocked vs real services)
- Fixture usage patterns

### Step 2: Create Directory Structure
```bash
mkdir -p tests/unit tests/container
touch tests/unit/__init__.py tests/container/__init__.py
```

### Step 3: Move and Rename Files
Follow naming convention:
- Unit tests: `test_<module>_unit.py`
- Integration tests: `test_<feature>_integration.py`
- Container tests: `test_<feature>_container.py`

### Step 4: Update Markers and Imports
Ensure each migrated file has:
- Appropriate pytestmark declarations
- Updated import paths for moved dependencies
- Consistent fixture usage

### Step 5: Validate Migration
Run test commands to ensure all tests still pass:
```bash
make test-unit          # Should find tests in tests/unit/
make test-integration   # Should find tests in tests/integration/
make test-container     # Should find tests in tests/container/
make test              # Should find all tests
```

## Marker Standardization

Ensure consistent marker usage per testing.md guidelines:

### Unit Tests (`tests/unit/`)
```python
pytestmark = [pytest.mark.unit, pytest.mark.fast]
```

### Integration Tests (`tests/integration/`)
```python
pytestmark = [pytest.mark.integration, pytest.mark.medium]
```

### Container Tests (`tests/container/`)
```python
pytestmark = [
    pytest.mark.container,
    pytest.mark.integration,
    pytest.mark.slow
]
```

## Benefits of Migration

1. **Clear Test Organization**: Tests organized by type and complexity
2. **Better Performance**: Can run fast unit tests separately from slow container tests
3. **Improved Developer Experience**: Clear separation allows targeted test execution
4. **Enhanced CI/CD**: Pipeline can run test categories in parallel
5. **Consistent Naming**: Following established naming conventions
6. **Better Fixture Usage**: Leverages enhanced fixture system from tests/shared/

## Risk Mitigation

1. **Backup current structure** before migration
2. **Migrate incrementally** - one category at a time
3. **Run full test suite** after each migration phase
4. **Update CI/CD pipeline** to use new structure
5. **Validate marker-based test selection** works correctly

## Success Criteria

- [ ] All tests moved to appropriate directories (unit/, integration/, container/)
- [ ] All tests follow new naming conventions
- [ ] All tests have appropriate pytest markers
- [ ] All test commands (`make test-unit`, `make test-integration`, etc.) work correctly
- [ ] No tests are lost or broken during migration
- [ ] Test execution performance is maintained or improved
- [ ] CI/CD pipeline works with new structure

## Timeline

**Estimated effort**: 4-6 hours
- Phase 1-2: 1 hour (directory creation + unit test migration)
- Phase 3-4: 2 hours (integration + container test migration)
- Phase 5-6: 1-2 hours (cleanup + validation)
- Testing and validation: 1 hour

This migration will bring the test suite into full compliance with the Advanced Testing Patterns framework described in testing.md.
