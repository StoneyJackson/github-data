# MockBoundaryFactory Migration Troubleshooting Guide

**Date:** 2025-10-16  
**Purpose:** Troubleshooting guide for migrating from manual boundary mocks to MockBoundaryFactory  
**Status:** Complete after Phase 3.3 migration completion  

## Overview

This guide helps developers troubleshoot common issues when migrating tests from manual boundary mock patterns to the standardized MockBoundaryFactory system. Following the completion of the boundary mock migration plan, all tests should use factory patterns for GitHub API boundary mocking.

## Quick Migration Reference

### Before/After Pattern
```python
# ❌ BEFORE - Manual mock (avoid)
mock_boundary = Mock()
mock_boundary.get_repository_labels.return_value = []
mock_boundary.get_repository_issues.return_value = sample_data["issues"]
# ... 20+ more manual configurations

# ✅ AFTER - Factory pattern (use)
mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
# All protocol methods automatically configured ✅
```

## Common Migration Issues

### Issue 1: Import Errors

**Problem:**
```python
ImportError: cannot import name 'MockBoundaryFactory' from 'tests.shared.mocks'
```

**Solution:**
```python
# ✅ Correct import
from tests.shared.mocks.boundary_factory import MockBoundaryFactory

# ❌ Incorrect imports (avoid these)
from tests.shared.mocks import MockBoundaryFactory  # Wrong module
from tests.shared import MockBoundaryFactory        # Wrong path
```

### Issue 2: Test Failures After Migration

**Problem:**
Test fails with attribute errors or unexpected behavior after factory migration.

**Symptoms:**
```python
AttributeError: 'Mock' object has no attribute 'some_method'
AssertionError: Expected call to method X but it wasn't called
```

**Diagnosis Steps:**
1. **Verify Factory Usage:**
   ```python
   # ✅ Check you're using the factory
   mock_boundary = MockBoundaryFactory.create_auto_configured(sample_data)
   
   # ❌ Not using Mock() directly
   mock_boundary = Mock()  # This causes issues
   ```

2. **Validate Protocol Completeness:**
   ```python
   from tests.shared.mocks.protocol_validation import validate_boundary_mock
   
   def test_debug_boundary_mock():
       mock_boundary = MockBoundaryFactory.create_auto_configured(sample_data)
       is_complete = validate_boundary_mock(mock_boundary)
       assert is_complete, "Mock boundary is not protocol complete"
   ```

3. **Check Custom Configurations:**
   ```python
   # ✅ Preserve necessary custom behavior
   mock_boundary = MockBoundaryFactory.create_auto_configured(sample_data)
   mock_boundary.create_issue.side_effect = custom_side_effect  # Keep custom logic
   ```

**Solutions:**
- Replace `Mock()` with `MockBoundaryFactory.create_auto_configured()`
- Preserve any `side_effect` or custom `return_value` configurations
- Verify all test assertions still match expected factory behavior

### Issue 3: Protocol Completeness Failures

**Problem:**
```python
ValueError: Mock boundary missing methods: ['get_repository_pull_requests', 'create_pull_request_review']
```

**Cause:**
Using manual mock creation or incomplete factory configuration.

**Solution:**
```python
# ✅ Use auto-configured factory for completeness
mock_boundary = MockBoundaryFactory.create_auto_configured(sample_data)

# ✅ Or use protocol-complete factory with validation
mock_boundary = MockBoundaryFactory.create_protocol_complete(sample_data)

# ❌ Avoid manual mock creation
mock_boundary = Mock()  # Will be incomplete
```

### Issue 4: Sample Data Format Issues

**Problem:**
Test fails because sample data doesn't match expected format.

**Symptoms:**
```python
KeyError: 'pull_requests'
TypeError: 'NoneType' object is not iterable
```

**Solution:**
```python
# ✅ Use consistent sample data format
sample_data = {
    "labels": [...],
    "issues": [...],
    "comments": [...],
    "pull_requests": [...],
    "pr_comments": [...],
    "sub_issues": [...]
}

# ✅ Or use empty data for edge cases
mock_boundary = MockBoundaryFactory.create_auto_configured({})

# ✅ Or use existing sample data fixtures
def test_with_sample_data(sample_github_data):
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
```

### Issue 5: Custom Behavior Not Preserved

**Problem:**
Test expects specific custom mock behavior that's lost after migration.

**Example:**
```python
# ❌ BEFORE - Custom behavior lost
mock_boundary = Mock()
mock_boundary.create_label.side_effect = [success_response, Exception("Error")]

# Migration removes side_effect accidentally
mock_boundary = MockBoundaryFactory.create_auto_configured(sample_data)
# side_effect is gone! ❌
```

**Solution:**
```python
# ✅ AFTER - Preserve custom behavior
mock_boundary = MockBoundaryFactory.create_auto_configured(sample_data)
# Add custom behavior AFTER factory creation
mock_boundary.create_label.side_effect = [success_response, Exception("Error")]
```

### Issue 6: Performance Degradation

**Problem:**
Tests run slower after migration to factory patterns.

**Diagnosis:**
```python
# Check fixture scope and data size
@pytest.fixture(scope="session")  # Use appropriate scope
def sample_github_data():
    return {
        "labels": [...],      # Keep data realistic but not excessive
        "issues": [...],      # Avoid generating thousands of items
    }
```

**Solutions:**
- Use session-scoped fixtures for expensive data generation
- Keep sample data realistic but not excessively large
- Use `create_auto_configured({})` for tests that don't need data

### Issue 7: Fixture Conflicts

**Problem:**
Multiple fixtures try to configure the same mock boundary.

**Symptoms:**
```python
TypeError: Cannot configure already configured mock
Multiple fixture conflicts detected
```

**Solution:**
```python
# ✅ Use single factory configuration per test
def test_single_configuration(sample_github_data):
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
    # Only one factory call per test

# ❌ Avoid multiple factory configurations
def test_multiple_configurations():
    mock_boundary = MockBoundaryFactory.create_auto_configured(data1)
    mock_boundary = MockBoundaryFactory.create_auto_configured(data2)  # Conflict!
```

## Migration Step-by-Step Checklist

### Pre-Migration Analysis
- [ ] Identify all manual `Mock()` boundary creations
- [ ] List all manual `return_value` and `side_effect` configurations
- [ ] Note any custom test-specific behavior that must be preserved

### Migration Steps
1. **Update Imports:**
   ```python
   # Add this import
   from tests.shared.mocks.boundary_factory import MockBoundaryFactory
   
   # Remove if no longer needed
   from unittest.mock import Mock
   ```

2. **Replace Mock Creation:**
   ```python
   # ❌ Replace this
   mock_boundary = Mock()
   
   # ✅ With this
   mock_boundary = MockBoundaryFactory.create_auto_configured(sample_data)
   ```

3. **Remove Manual Configurations:**
   ```python
   # ❌ Delete these (factory handles automatically)
   mock_boundary.get_repository_labels.return_value = []
   mock_boundary.get_repository_issues.return_value = []
   mock_boundary.get_all_issue_comments.return_value = []
   # ... all other manual return_value assignments
   ```

4. **Preserve Custom Behavior:**
   ```python
   # ✅ Keep these AFTER factory creation
   mock_boundary.create_issue.side_effect = custom_side_effect
   mock_boundary.some_method.return_value = custom_response
   ```

### Post-Migration Validation
- [ ] Run tests to ensure they pass
- [ ] Verify protocol completeness using validation utilities
- [ ] Check that custom behavior is preserved
- [ ] Validate test performance is acceptable

## Error Message Decoder

### Common Error Messages and Solutions

**"Mock boundary missing methods"**
```python
# Solution: Use auto-configured factory
mock_boundary = MockBoundaryFactory.create_auto_configured(sample_data)
```

**"'Mock' object has no attribute 'create_auto_configured'"**
```python
# Solution: Fix import statement
from tests.shared.mocks.boundary_factory import MockBoundaryFactory
```

**"TypeError: 'NoneType' object is not iterable"**
```python
# Solution: Provide proper sample data format
sample_data = {"labels": [], "issues": [], "comments": []}
mock_boundary = MockBoundaryFactory.create_auto_configured(sample_data)
```

**"Cannot import name 'MockBoundaryFactory'"**
```python
# Solution: Check import path
from tests.shared.mocks.boundary_factory import MockBoundaryFactory
```

## Best Practices After Migration

### Do These ✅
```python
# ✅ Use factory for all boundary mocks
mock_boundary = MockBoundaryFactory.create_auto_configured(sample_data)

# ✅ Validate completeness in development
from tests.shared.mocks.protocol_validation import validate_boundary_mock
assert validate_boundary_mock(mock_boundary)

# ✅ Add custom behavior after factory creation
mock_boundary.create_issue.side_effect = Exception("API Error")

# ✅ Use appropriate factory method for scenario
mock_boundary = MockBoundaryFactory.create_for_restore()  # For restore tests
```

### Avoid These ❌
```python
# ❌ Don't use manual Mock() creation
mock_boundary = Mock()

# ❌ Don't manually configure protocol methods
mock_boundary.get_repository_labels.return_value = []

# ❌ Don't ignore protocol completeness
# Always ensure mocks are complete

# ❌ Don't create multiple factory configurations per test
mock_boundary = MockBoundaryFactory.create_auto_configured(data1)
mock_boundary = MockBoundaryFactory.create_auto_configured(data2)  # Conflict
```

## Advanced Troubleshooting

### Debug Protocol Completeness
```python
from tests.shared.mocks.protocol_validation import ProtocolValidator

def debug_mock_completeness(mock_boundary):
    """Debug helper for protocol completeness issues."""
    is_complete, missing, details = ProtocolValidator.validate_protocol_completeness(
        mock_boundary, GitHubApiBoundary
    )
    
    if not is_complete:
        print(f"❌ Protocol incomplete: {details['completeness_percentage']:.1f}%")
        print(f"Missing methods: {missing}")
        
        # Generate detailed report
        report = ProtocolValidator.generate_validation_report(
            mock_boundary, GitHubApiBoundary
        )
        print(report)
    else:
        print("✅ Mock boundary is protocol complete!")
```

### Test Migration Validation
```python
def validate_migration_success():
    """Validation script for post-migration testing."""
    
    # Test 1: Factory creates protocol-complete mocks
    mock_boundary = MockBoundaryFactory.create_auto_configured({})
    assert validate_boundary_mock(mock_boundary)
    
    # Test 2: Custom behavior works
    mock_boundary.create_issue.side_effect = Exception("Test error")
    with pytest.raises(Exception):
        mock_boundary.create_issue()
    
    # Test 3: Data integration works
    sample_data = {"labels": [{"name": "test"}]}
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_data)
    assert mock_boundary.get_repository_labels() == sample_data["labels"]
    
    print("✅ Migration validation successful!")
```

## Getting Help

### Documentation Resources
- [MockBoundaryFactory API Documentation](tests/shared/mocks/boundary_factory.py)
- [Protocol Validation Guide](tests/shared/mocks/protocol_validation.py)
- [Testing Guide - Boundary Mock Section](docs/testing.md#boundary-mock-standardization)
- [CONTRIBUTING.md - Mock Factory Guidelines](CONTRIBUTING.md#mock-boundary-factory-guidelines)

### Migration Support Resources
- **Migration Utilities:** `tests/shared/mocks/migration_utils.py` 
- **Sample Data Fixtures:** `tests/shared/fixtures.py`
- **Validation Tools:** `tests/shared/mocks/protocol_validation.py`

### Test Commands for Validation
```bash
# Run specific migrated test file
pdm run pytest tests/integration/test_pr_integration.py -v

# Run all integration tests to check for regressions
pdm run pytest tests/integration/ -v

# Run with coverage to ensure no functionality lost
pdm run pytest tests/integration/ --cov=src -v

# Run migration validation
pdm run pytest -k "boundary_factory" -v
```

## Migration History Reference

### Completed Migrations ✅
- **Phase 1:** `test_conflict_strategies_unit.py`, `test_labels_integration.py`
- **Phase 2:** `test_save_restore_integration.py`, `test_issues_integration.py`
- **Phase 3:** `test_pr_comments_save_integration.py`, `test_error_handling_integration.py`, `test_pr_integration.py`

### Migration Results
- **Total Manual Patterns Eliminated:** 913 patterns
- **Code Reduction:** 95%+ across all files
- **Protocol Completeness:** 100% across entire test suite
- **Test Regression:** Zero breaking changes

---

*This troubleshooting guide supports the boundary mock migration plan implementation. For additional help, refer to the main testing documentation and migration results documents.*