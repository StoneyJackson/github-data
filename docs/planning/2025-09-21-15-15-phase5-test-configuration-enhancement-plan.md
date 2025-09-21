# Phase 5 Implementation Plan: Test Configuration Enhancement

**Date:** 2025-09-21  
**Scope:** Complete test configuration enhancement with markers, pytest configuration, and documentation  
**Prerequisites:** Phases 1-4 of test shared fixtures consolidation completed

## Executive Summary

This plan details Phase 5 of the test shared fixtures consolidation project, focusing on test configuration enhancement. With the fixture consolidation complete (Phases 1-4), this phase adds comprehensive test markers, pytest configuration, and documentation to create a robust test organization system.

## Phase 5 Objectives

### Primary Goals
1. **Test Categorization**: Implement comprehensive test markers for organized test execution
2. **Configuration Management**: Add pytest.ini configuration for consistent test behavior
3. **Marker Application**: Update all test files with appropriate markers
4. **Documentation**: Create fixture usage patterns and marker documentation

### Success Metrics
- All test files properly marked with category markers
- Pytest configuration enables selective test execution
- Test discovery and execution performance maintained
- Comprehensive documentation for developers

## Current State Assessment

### Existing Test Structure
Based on the completed phases, the current test structure includes:
- ✅ Consolidated shared fixtures in `tests/shared/fixtures.py`
- ✅ Enhanced mock utilities in `tests/shared/mocks.py`
- ✅ Data builders in `tests/shared/builders.py`
- ✅ Eliminated fixture duplication across test files
- ✅ Standardized import patterns

### Test File Inventory
**Integration Test Files:**
- `tests/test_integration.py` - Core integration tests
- `tests/test_sub_issues_integration.py` - Sub-issues workflow tests
- `tests/test_pr_integration.py` - Pull request workflow tests
- `tests/test_docker_compose_integration.py` - Docker Compose tests
- `tests/test_container_integration.py` - Container integration tests

**Unit Test Files:**
- `tests/test_conflict_strategies.py` - Conflict resolution unit tests
- `tests/test_*.py` (various unit test files)

## Implementation Plan

### Step 5.1: Design Test Marker Strategy

#### Core Test Categories
```python
# Performance-based markers
@pytest.mark.fast       # < 1 second per test
@pytest.mark.medium     # 1-10 seconds per test  
@pytest.mark.slow       # > 10 seconds per test

# Test type markers
@pytest.mark.unit       # Isolated component tests
@pytest.mark.integration # Component interaction tests
@pytest.mark.container # Full Docker workflow tests

# Feature area markers
@pytest.mark.labels     # Label management tests
@pytest.mark.issues     # Issue management tests
@pytest.mark.comments   # Comment management tests
@pytest.mark.sub_issues # Sub-issues workflow tests
@pytest.mark.pull_requests # PR workflow tests

# Infrastructure markers
@pytest.mark.github_api # GitHub API interaction tests
@pytest.mark.storage    # Storage service tests
@pytest.mark.backup_workflow # Backup operation tests
@pytest.mark.restore_workflow # Restore operation tests

# Special scenario markers
@pytest.mark.empty_repository # Empty repo scenario tests
@pytest.mark.large_dataset # Large data scenario tests
@pytest.mark.rate_limiting # Rate limiting tests
@pytest.mark.error_simulation # Error handling tests
```

#### Marker Combinations Strategy
```python
# Example combinations:
@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.labels
def test_label_validation():
    """Fast unit test for label validation."""
    pass

@pytest.mark.integration
@pytest.mark.medium
@pytest.mark.sub_issues
@pytest.mark.github_api
def test_sub_issues_backup_workflow():
    """Medium integration test for sub-issues backup."""
    pass

@pytest.mark.container
@pytest.mark.slow
@pytest.mark.backup_workflow
@pytest.mark.large_dataset
def test_full_repository_backup():
    """Slow container test for full repository backup."""
    pass
```

### Step 5.2: Create Enhanced conftest.py

#### File: `tests/conftest.py`
```python
"""Global test configuration and marker definitions."""

import pytest
from pathlib import Path

# Import shared fixtures for global availability
pytest_plugins = ["tests.shared.fixtures"]

def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    
    # Performance markers
    config.addinivalue_line(
        "markers", 
        "fast: marks tests as fast (< 1 second) - suitable for TDD cycles"
    )
    config.addinivalue_line(
        "markers", 
        "medium: marks tests as medium speed (1-10 seconds) - integration tests"
    )
    config.addinivalue_line(
        "markers", 
        "slow: marks tests as slow (> 10 seconds) - container/end-to-end tests"
    )
    
    # Test type markers
    config.addinivalue_line(
        "markers", 
        "unit: marks tests as unit tests - isolated component testing"
    )
    config.addinivalue_line(
        "markers", 
        "integration: marks tests as integration tests - component interactions"
    )
    config.addinivalue_line(
        "markers", 
        "container: marks tests as container tests - full Docker workflows"
    )
    
    # Feature area markers
    config.addinivalue_line(
        "markers", 
        "labels: marks tests related to label management functionality"
    )
    config.addinivalue_line(
        "markers", 
        "issues: marks tests related to issue management functionality"
    )
    config.addinivalue_line(
        "markers", 
        "comments: marks tests related to comment management functionality"
    )
    config.addinivalue_line(
        "markers", 
        "sub_issues: marks tests related to sub-issues workflow functionality"
    )
    config.addinivalue_line(
        "markers", 
        "pull_requests: marks tests related to pull request workflow functionality"
    )
    
    # Infrastructure markers
    config.addinivalue_line(
        "markers", 
        "github_api: marks tests that interact with GitHub API (real or mocked)"
    )
    config.addinivalue_line(
        "markers", 
        "storage: marks tests related to data storage and persistence"
    )
    config.addinivalue_line(
        "markers", 
        "backup_workflow: marks tests for backup operation workflows"
    )
    config.addinivalue_line(
        "markers", 
        "restore_workflow: marks tests for restore operation workflows"
    )
    
    # Special scenario markers
    config.addinivalue_line(
        "markers", 
        "empty_repository: marks tests using empty repository scenarios"
    )
    config.addinivalue_line(
        "markers", 
        "large_dataset: marks tests using large dataset scenarios"
    )
    config.addinivalue_line(
        "markers", 
        "rate_limiting: marks tests that verify rate limiting behavior"
    )
    config.addinivalue_line(
        "markers", 
        "error_simulation: marks tests that simulate error conditions"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add automatic markers based on test patterns."""
    
    for item in items:
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
        
        # Auto-mark by feature area based on filename
        if "sub_issues" in item.nodeid:
            item.add_marker(pytest.mark.sub_issues)
        elif "pr_" in item.nodeid or "pull_request" in item.nodeid:
            item.add_marker(pytest.mark.pull_requests)
        elif "conflict" in item.nodeid:
            item.add_marker(pytest.mark.labels)  # Conflicts typically with labels
        
        # Auto-mark GitHub API tests
        if hasattr(item, 'function') and item.function:
            if 'github' in str(item.function.__code__.co_names).lower():
                item.add_marker(pytest.mark.github_api)

def pytest_runtest_setup(item):
    """Setup hook for individual test execution."""
    # Skip slow tests in fast mode
    if item.config.getoption("--fast", default=False):
        if item.get_closest_marker("slow"):
            pytest.skip("Skipping slow test in fast mode")
    
    # Skip container tests if Docker not available
    if item.get_closest_marker("container"):
        try:
            import docker
            client = docker.from_env()
            client.ping()
        except Exception:
            pytest.skip("Docker not available for container tests")

def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--fast",
        action="store_true",
        default=False,
        help="Run only fast tests (skip slow and container tests)"
    )
    parser.addoption(
        "--unit-only",
        action="store_true", 
        default=False,
        help="Run only unit tests"
    )
    parser.addoption(
        "--integration-only",
        action="store_true",
        default=False, 
        help="Run only integration tests"
    )
    parser.addoption(
        "--container-only",
        action="store_true",
        default=False,
        help="Run only container tests"
    )
```

### Step 5.3: Create pytest.ini Configuration

#### File: `pytest.ini`
```ini
[tool:pytest]
# Test discovery configuration
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Marker configuration
markers =
    # Performance markers
    fast: Fast tests (< 1 second) - suitable for TDD cycles
    medium: Medium speed tests (1-10 seconds) - integration tests  
    slow: Slow tests (> 10 seconds) - container/end-to-end tests
    
    # Test type markers
    unit: Unit tests - isolated component testing
    integration: Integration tests - component interactions
    container: Container tests - full Docker workflows
    
    # Feature area markers
    labels: Label management functionality tests
    issues: Issue management functionality tests
    comments: Comment management functionality tests
    sub_issues: Sub-issues workflow functionality tests
    pull_requests: Pull request workflow functionality tests
    
    # Infrastructure markers
    github_api: GitHub API interaction tests (real or mocked)
    storage: Data storage and persistence tests
    backup_workflow: Backup operation workflow tests
    restore_workflow: Restore operation workflow tests
    
    # Special scenario markers
    empty_repository: Empty repository scenario tests
    large_dataset: Large dataset scenario tests
    rate_limiting: Rate limiting behavior tests
    error_simulation: Error condition simulation tests

# Output and behavior configuration
addopts = 
    --verbose
    --tb=short
    --strict-markers
    --strict-config
    --color=yes
    --durations=10
    
# Coverage configuration (when using --cov)
addopts = 
    --cov=src
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=80

# Minimum pytest version
minversion = 6.0

# Test timeout (for hanging tests)
timeout = 300

# Parallel execution configuration
addopts = -n auto

# Warnings configuration
filterwarnings =
    error
    ignore::UserWarning
    ignore::DeprecationWarning:pkg_resources.*
```

### Step 5.4: Update Test Files with Markers

#### Test File Marker Application Strategy

**For each test file, apply markers based on:**

1. **Automatic markers** (applied by conftest.py):
   - Performance markers based on file patterns
   - Test type markers based on file names
   - Feature area markers based on file names

2. **Manual markers** (applied to specific test methods):
   - Special scenario markers
   - Infrastructure markers
   - Custom combinations

#### Example: tests/test_sub_issues_integration.py
```python
import pytest
from tests.shared import (
    temp_data_dir,
    sample_sub_issues_data,
    complex_hierarchy_data,
    github_service_with_mock
)

class TestSubIssuesIntegration:
    """Integration tests for sub-issues workflow functionality."""
    
    @pytest.mark.backup_workflow
    @pytest.mark.github_api
    def test_backup_sub_issues_basic(self, github_service_with_mock, temp_data_dir):
        """Test basic sub-issues backup workflow."""
        # Test implementation
        pass
    
    @pytest.mark.restore_workflow
    @pytest.mark.storage
    def test_restore_sub_issues_hierarchy(self, temp_data_dir, complex_hierarchy_data):
        """Test restoration of complex sub-issues hierarchy."""
        # Test implementation
        pass
    
    @pytest.mark.large_dataset
    @pytest.mark.rate_limiting
    def test_backup_large_sub_issues_dataset(self, github_service_with_mock):
        """Test backup with large sub-issues dataset and rate limiting."""
        # Test implementation
        pass
    
    @pytest.mark.error_simulation
    @pytest.mark.github_api
    def test_backup_sub_issues_with_api_errors(self, github_service_with_mock):
        """Test sub-issues backup with simulated API errors."""
        # Test implementation
        pass
```

#### Example: tests/test_conflict_strategies.py
```python
import pytest
from tests.shared import temp_data_dir, sample_labels_data

class TestConflictStrategies:
    """Unit tests for conflict resolution strategies."""
    
    @pytest.mark.storage
    def test_label_conflict_skip_strategy(self, temp_data_dir, sample_labels_data):
        """Test skip strategy for label conflicts."""
        # Test implementation
        pass
    
    @pytest.mark.storage
    def test_label_conflict_overwrite_strategy(self, temp_data_dir, sample_labels_data):
        """Test overwrite strategy for label conflicts."""
        # Test implementation
        pass
    
    @pytest.mark.error_simulation
    def test_conflict_strategy_with_invalid_data(self, temp_data_dir):
        """Test conflict strategies with invalid data scenarios."""
        # Test implementation
        pass
```

### Step 5.5: Create Test Execution Scripts

#### File: `scripts/test-categories.py`
```python
#!/usr/bin/env python3
"""Test execution script for different test categories."""

import subprocess
import sys
import argparse
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        print(f"❌ {description} failed with exit code {result.returncode}")
        return False
    else:
        print(f"✅ {description} completed successfully")
        return True

def main():
    parser = argparse.ArgumentParser(description="Run categorized tests")
    parser.add_argument("--fast", action="store_true", help="Run only fast tests")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--container", action="store_true", help="Run only container tests")
    parser.add_argument("--feature", choices=["labels", "issues", "comments", "sub_issues", "pull_requests"], help="Run tests for specific feature")
    parser.add_argument("--coverage", action="store_true", help="Include coverage reporting")
    
    args = parser.parse_args()
    
    base_cmd = ["python", "-m", "pytest"]
    
    if args.coverage:
        base_cmd.extend(["--cov=src", "--cov-report=term-missing"])
    
    if args.fast:
        base_cmd.extend(["-m", "fast"])
        success = run_command(base_cmd, "Fast tests")
    elif args.unit:
        base_cmd.extend(["-m", "unit"])
        success = run_command(base_cmd, "Unit tests")
    elif args.integration:
        base_cmd.extend(["-m", "integration"])
        success = run_command(base_cmd, "Integration tests")
    elif args.container:
        base_cmd.extend(["-m", "container"])
        success = run_command(base_cmd, "Container tests")
    elif args.feature:
        base_cmd.extend(["-m", args.feature])
        success = run_command(base_cmd, f"{args.feature.title()} feature tests")
    else:
        # Run test categories in sequence
        categories = [
            (["fast"], "Fast tests (TDD cycle)"),
            (["medium", "and", "not", "container"], "Medium integration tests"),
            (["slow", "and", "not", "container"], "Slow integration tests"),
            (["container"], "Container tests"),
        ]
        
        all_success = True
        for markers, description in categories:
            cmd = base_cmd + ["-m", " ".join(markers)]
            success = run_command(cmd, description)
            all_success = all_success and success
        
        success = all_success
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

### Step 5.6: Update Makefile with Marker-Based Commands

#### Add to Makefile:
```makefile
# Test commands with markers
.PHONY: test-fast test-unit test-integration test-container test-by-feature

test-fast:  ## Run fast tests only (< 1 second)
	pdm run python -m pytest -m fast

test-unit:  ## Run unit tests only
	pdm run python -m pytest -m unit

test-integration:  ## Run integration tests only (excluding container tests)
	pdm run python -m pytest -m "integration and not container"

test-container:  ## Run container tests only
	pdm run python -m pytest -m container

test-by-feature:  ## Run tests for specific feature (usage: make test-by-feature FEATURE=labels)
	pdm run python -m pytest -m $(FEATURE)

# Combined test workflows
test-dev:  ## Development test workflow (fast + integration, no container)
	pdm run python -m pytest -m "fast or (integration and not container)"

test-ci:  ## CI test workflow (all tests with coverage)
	pdm run python -m pytest --cov=src --cov-report=term-missing --cov-report=html

# Test discovery and information
test-list-markers:  ## List all available test markers
	pdm run python -m pytest --markers

test-collect-only:  ## Show test collection without running tests
	pdm run python -m pytest --collect-only

test-by-markers:  ## Run tests by custom marker expression (usage: make test-by-markers MARKERS="fast and labels")
	pdm run python -m pytest -m "$(MARKERS)"
```

### Step 5.7: Create Documentation

#### File: `docs/testing-markers.md`
```markdown
# Test Markers and Configuration Guide

This document describes the comprehensive test marker system and configuration for the GitHub Data project.

## Test Marker Categories

### Performance Markers

- `@pytest.mark.fast` - Tests completing in < 1 second (suitable for TDD cycles)
- `@pytest.mark.medium` - Tests completing in 1-10 seconds (integration tests)
- `@pytest.mark.slow` - Tests completing in > 10 seconds (container/end-to-end tests)

### Test Type Markers

- `@pytest.mark.unit` - Isolated component tests with mocked dependencies
- `@pytest.mark.integration` - Tests verifying component interactions
- `@pytest.mark.container` - Full Docker workflow tests

### Feature Area Markers

- `@pytest.mark.labels` - Label management functionality
- `@pytest.mark.issues` - Issue management functionality
- `@pytest.mark.comments` - Comment management functionality
- `@pytest.mark.sub_issues` - Sub-issues workflow functionality
- `@pytest.mark.pull_requests` - Pull request workflow functionality

### Infrastructure Markers

- `@pytest.mark.github_api` - GitHub API interaction tests
- `@pytest.mark.storage` - Data storage and persistence tests
- `@pytest.mark.backup_workflow` - Backup operation tests
- `@pytest.mark.restore_workflow` - Restore operation tests

### Special Scenario Markers

- `@pytest.mark.empty_repository` - Empty repository scenario tests
- `@pytest.mark.large_dataset` - Large dataset scenario tests
- `@pytest.mark.rate_limiting` - Rate limiting behavior tests
- `@pytest.mark.error_simulation` - Error condition simulation tests

## Usage Examples

### Running Specific Test Categories

```bash
# Fast development cycle
make test-fast

# Unit tests only
make test-unit

# Integration tests (excluding containers)
make test-integration

# Container tests only
make test-container

# Feature-specific tests
make test-by-feature FEATURE=labels
make test-by-feature FEATURE=sub_issues

# Custom marker combinations
make test-by-markers MARKERS="fast and labels"
make test-by-markers MARKERS="integration and github_api"
```

### Test Development Workflow

1. **TDD Cycle**: Use `make test-fast` for rapid feedback
2. **Feature Development**: Use `make test-by-feature FEATURE=<area>`
3. **Integration Validation**: Use `make test-integration`
4. **Full Validation**: Use `make test` (includes container tests)

## Marker Application Guidelines

### Automatic Markers

The following markers are applied automatically based on test patterns:

- Container tests: Auto-marked with `container` and `slow`
- Integration tests: Auto-marked with `integration` and `medium`
- Other tests: Auto-marked with `unit` and `fast`
- Feature areas: Auto-marked based on filename patterns

### Manual Marker Application

Apply these markers manually to test methods:

```python
@pytest.mark.github_api
@pytest.mark.rate_limiting
def test_api_rate_limiting():
    """Test that requires manual marking for specific scenarios."""
    pass
```

## Best Practices

### Marker Combinations

Use multiple markers to categorize tests effectively:

```python
@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.labels
@pytest.mark.storage
def test_label_storage_unit():
    """Well-categorized unit test."""
    pass
```

### Performance Guidelines

- **Fast tests**: No I/O, minimal computation, mocked dependencies
- **Medium tests**: Limited I/O, component interactions, controlled datasets
- **Slow tests**: Full workflows, large datasets, container operations

### Marker Selection Strategy

Choose markers based on:
1. **Test execution time** (fast/medium/slow)
2. **Test scope** (unit/integration/container)  
3. **Feature area** (labels/issues/etc.)
4. **Infrastructure requirements** (github_api/storage/etc.)
5. **Special scenarios** (error_simulation/large_dataset/etc.)
```

#### File: `docs/fixture-usage-patterns.md`
```markdown
# Fixture Usage Patterns Guide

This document provides patterns and best practices for using the consolidated shared fixtures.

## Shared Fixture Overview

### Core Infrastructure Fixtures

- `temp_data_dir` - Temporary directory for test data
- `sample_github_data` - Comprehensive GitHub API sample data
- `github_service_mock` - Basic GitHub service mock
- `storage_service_mock` - Storage service mock

### Enhanced Mock Fixtures

- `mock_boundary_class` - Mock GitHubApiBoundary class for patching
- `mock_boundary` - Configured mock boundary instance
- `github_service_with_mock` - GitHub service with mocked boundary

### Specialized Data Fixtures

- `empty_repository_data` - Empty repository scenario data
- `sample_sub_issues_data` - Sub-issues hierarchical data
- `sample_pr_data` - Pull request workflow data
- `sample_labels_data` - Label management data
- `complex_hierarchy_data` - Complex sub-issue hierarchy data

## Usage Patterns

### Pattern 1: Basic Unit Test

```python
import pytest
from tests.shared import temp_data_dir, sample_labels_data

@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.labels
def test_label_validation(sample_labels_data):
    """Test label validation logic."""
    # Use sample_labels_data for test input
    pass
```

### Pattern 2: Service Integration Test

```python
import pytest
from tests.shared import github_service_with_mock, temp_data_dir

@pytest.mark.integration
@pytest.mark.medium
@pytest.mark.github_api
def test_service_integration(github_service_with_mock, temp_data_dir):
    """Test service integration with mocked boundary."""
    # Use pre-configured service and temp directory
    pass
```

### Pattern 3: Storage Workflow Test

```python
import pytest
from tests.shared import temp_data_dir, storage_service_mock, sample_github_data

@pytest.mark.integration
@pytest.mark.medium
@pytest.mark.storage
def test_storage_workflow(temp_data_dir, storage_service_mock, sample_github_data):
    """Test complete storage workflow."""
    # Use all three fixtures for comprehensive testing
    pass
```

### Pattern 4: Complex Scenario Test

```python
import pytest
from tests.shared import (
    temp_data_dir,
    complex_hierarchy_data,
    github_service_with_mock
)

@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.sub_issues
@pytest.mark.large_dataset
def test_complex_hierarchy_workflow(
    temp_data_dir, 
    complex_hierarchy_data, 
    github_service_with_mock
):
    """Test complex sub-issues hierarchy workflow."""
    # Use specialized data and services for complex scenarios
    pass
```

## Best Practices

### Fixture Selection Guidelines

1. **Start with minimal fixtures** - Use only what you need
2. **Prefer shared fixtures** - Avoid creating test-specific fixtures
3. **Combine appropriately** - Use multiple fixtures for complex scenarios
4. **Follow naming conventions** - Use descriptive fixture parameter names

### Import Organization

```python
# Preferred import style
from tests.shared import (
    temp_data_dir,
    sample_github_data,
    github_service_with_mock,
    storage_service_mock
)

# Avoid importing individual modules
# from tests.shared.fixtures import temp_data_dir  # Not preferred
```

### Fixture Scope Awareness

- Most fixtures use `function` scope for test isolation
- Use `session` or `module` scope fixtures sparingly
- Be aware of fixture cleanup behavior

## Common Patterns by Test Type

### Unit Tests
- Use data fixtures (`sample_*_data`)
- Minimal service mocking
- Focus on single component behavior

### Integration Tests  
- Use service fixtures (`*_service_mock`)
- Combine data and service fixtures
- Test component interactions

### Container Tests
- Use `temp_data_dir` for file operations
- Combine with service fixtures for end-to-end workflows
- Include cleanup verification
```

### Step 5.8: Validation and Testing

#### Validation Checklist
1. **Marker Discovery**: Verify all markers are properly registered
2. **Test Collection**: Ensure test discovery works with new configuration
3. **Selective Execution**: Test marker-based test execution
4. **Performance**: Verify test execution time categorization
5. **Documentation**: Validate documentation accuracy and completeness

#### Testing Commands
```bash
# Validate marker registration
pdm run python -m pytest --markers

# Test marker-based execution
pdm run python -m pytest -m fast --collect-only
pdm run python -m pytest -m "integration and not container" --collect-only

# Validate automatic marker application
pdm run python -m pytest --collect-only -q

# Test custom command line options
pdm run python -m pytest --fast --collect-only
pdm run python -m pytest --unit-only --collect-only
```

## Implementation Timeline

### Day 1: Configuration Setup
- [ ] Create enhanced `conftest.py` with all markers
- [ ] Create `pytest.ini` configuration
- [ ] Test marker registration and discovery
- [ ] Validate test collection works properly

### Day 2: Marker Application
- [ ] Apply markers to integration test files
- [ ] Apply markers to unit test files  
- [ ] Apply markers to container test files
- [ ] Test selective execution by markers

### Day 3: Scripts and Documentation
- [ ] Create test execution scripts
- [ ] Update Makefile with marker-based commands
- [ ] Create marker documentation
- [ ] Create fixture usage patterns documentation
- [ ] Final validation and testing

## Success Criteria

### Functional Requirements
- [ ] All test files have appropriate markers applied
- [ ] Marker-based test execution works correctly
- [ ] Test categorization is accurate (fast/medium/slow)
- [ ] Custom command line options function properly

### Quality Requirements
- [ ] No test discovery regressions
- [ ] Test execution performance maintained
- [ ] All tests continue to pass
- [ ] Documentation is comprehensive and accurate

### Integration Requirements
- [ ] Makefile commands work with new markers
- [ ] CI/CD pipeline compatibility maintained
- [ ] Development workflow is enhanced
- [ ] Future fixture additions are well-supported

## Risk Mitigation

### Potential Issues and Solutions

1. **Marker Conflicts**
   - Risk: Conflicting or duplicate markers
   - Solution: Systematic marker review and testing

2. **Performance Categorization Errors**
   - Risk: Tests marked with wrong performance category
   - Solution: Execution time validation and adjustment

3. **Test Discovery Issues**
   - Risk: Configuration changes breaking test discovery
   - Solution: Comprehensive test collection validation

4. **Documentation Drift**
   - Risk: Documentation becoming outdated
   - Solution: Include documentation updates in development workflow

## Follow-up Work

### Future Enhancements
1. **Marker Analytics**: Track marker usage and test execution patterns
2. **Dynamic Marker Assignment**: Auto-assign markers based on execution time
3. **Marker Validation**: Add pre-commit hooks to validate marker usage
4. **Enhanced Reporting**: Create marker-based test reports and dashboards

## Conclusion

Phase 5 completes the test configuration enhancement by providing comprehensive test markers, pytest configuration, and documentation. This creates a robust foundation for organized test execution and development workflows, building on the fixture consolidation work from Phases 1-4.

The implementation provides developers with powerful tools for selective test execution while maintaining the benefits of the consolidated shared fixture system.