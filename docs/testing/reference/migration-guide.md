# Migration Guide

[← Testing Guide](../README.md)

## MockBoundaryFactory Migration

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

### Migration Steps

#### 1. Update Imports
```python
# Add this import
from tests.shared.mocks.boundary_factory import MockBoundaryFactory

# Remove if no longer needed
from unittest.mock import Mock
```

#### 2. Replace Mock Creation
```python
# ❌ Replace this
mock_boundary = Mock()

# ✅ With this
mock_boundary = MockBoundaryFactory.create_auto_configured(sample_data)
```

#### 3. Remove Manual Configurations
```python
# ❌ Delete these (factory handles automatically)
mock_boundary.get_repository_labels.return_value = []
mock_boundary.get_repository_issues.return_value = []
mock_boundary.get_all_issue_comments.return_value = []
# ... all other manual return_value assignments
```

#### 4. Preserve Custom Behavior
```python
# ✅ Keep these AFTER factory creation
mock_boundary.create_issue.side_effect = custom_side_effect
mock_boundary.some_method.return_value = custom_response
```

---

For more information about specific testing scenarios or to contribute to the test suite, see the project's [CONTRIBUTING.md](../../CONTRIBUTING.md) guide.

---

[← Testing Guide](../README.md) | [Best Practices](best-practices.md)
