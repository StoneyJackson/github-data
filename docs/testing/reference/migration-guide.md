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

## Migrating from ConfigBuilder/ConfigFactory to EntityRegistry

### Background

The `ConfigBuilder` and `ConfigFactory` classes were removed when `ApplicationConfig` was deprecated. Tests now use `EntityRegistry.from_environment()` with environment variables.

**When this change happened:** Removal documented in `tests/shared/builders/__init__.py`

### Migration Overview

**Old Pattern (REMOVED):**
```python
from tests.shared.builders import ConfigFactory, ConfigBuilder

# ConfigFactory pattern
config = ConfigFactory.create_save_config(
    github_token="token",
    github_repo="owner/repo",
    data_path=temp_data_dir
)

# ConfigBuilder pattern
config = (
    ConfigBuilder()
    .with_github_token("token")
    .with_github_repo("owner/repo")
    .with_data_path(temp_data_dir)
    .build()
)
```

**New Pattern (CURRENT):**
```python
from github_data.core.registry import EntityRegistry

def test_example(temp_data_dir, monkeypatch):
    # Set environment variables
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_REPO", "owner/repo")
    monkeypatch.setenv("DATA_PATH", str(temp_data_dir))
    monkeypatch.setenv("OPERATION", "save")

    # Create registry from environment
    registry = EntityRegistry.from_environment()
```

### Step-by-Step Migration

#### Step 1: Add monkeypatch fixture

**Before:**
```python
def test_something(temp_data_dir):
    config = ConfigFactory.create_save_config(...)
```

**After:**
```python
def test_something(temp_data_dir, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "...")
```

#### Step 2: Replace config creation with environment setup

**Before:**
```python
config = ConfigFactory.create_save_config(
    github_token="test_token",
    github_repo="owner/repo",
    data_path=temp_data_dir,
    include_issues=True,
    include_pull_requests=False
)
```

**After:**
```python
monkeypatch.setenv("GITHUB_TOKEN", "test_token")
monkeypatch.setenv("GITHUB_REPO", "owner/repo")
monkeypatch.setenv("DATA_PATH", str(temp_data_dir))
monkeypatch.setenv("OPERATION", "save")
monkeypatch.setenv("INCLUDE_ISSUES", "true")
monkeypatch.setenv("INCLUDE_PULL_REQUESTS", "false")
```

#### Step 3: Create EntityRegistry

**Before:**
```python
# Config was passed to services manually
service = SomeService(config)
```

**After:**
```python
# Registry creates and manages services
registry = EntityRegistry.from_environment()
service = registry.some_service
```

### Common Migration Scenarios

#### Scenario 1: Simple save test

**Before:**
```python
def test_label_save(temp_data_dir):
    config = ConfigFactory.create_save_config(
        github_token="token",
        github_repo="owner/repo",
        data_path=temp_data_dir
    )
    saver = LabelSaver(config)
    result = saver.save()
```

**After:**
```python
def test_label_save(temp_data_dir, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_REPO", "owner/repo")
    monkeypatch.setenv("DATA_PATH", str(temp_data_dir))
    monkeypatch.setenv("OPERATION", "save")

    registry = EntityRegistry.from_environment()
    saver = registry.create_label_saver()
    result = saver.save()
```

#### Scenario 2: Complex configuration

**Before:**
```python
def test_with_options(temp_data_dir):
    config = (
        ConfigBuilder()
        .with_github_token("token")
        .with_github_repo("owner/repo")
        .with_data_path(temp_data_dir)
        .with_include_issues(True)
        .with_include_pull_requests(False)
        .with_include_comments(True)
        .build()
    )
```

**After:**
```python
def test_with_options(temp_data_dir, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_REPO", "owner/repo")
    monkeypatch.setenv("DATA_PATH", str(temp_data_dir))
    monkeypatch.setenv("OPERATION", "save")
    monkeypatch.setenv("INCLUDE_ISSUES", "true")
    monkeypatch.setenv("INCLUDE_PULL_REQUESTS", "false")
    monkeypatch.setenv("INCLUDE_ISSUE_COMMENTS", "true")

    registry = EntityRegistry.from_environment()
```

#### Scenario 3: Restore operation

**Before:**
```python
def test_restore(temp_data_dir):
    config = ConfigFactory.create_restore_config(
        github_token="token",
        github_repo="owner/repo",
        data_path=temp_data_dir
    )
```

**After:**
```python
def test_restore(temp_data_dir, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_REPO", "owner/repo")
    monkeypatch.setenv("DATA_PATH", str(temp_data_dir))
    monkeypatch.setenv("OPERATION", "restore")  # Key difference

    registry = EntityRegistry.from_environment()
```

### Environment Variable Reference

| ConfigBuilder/ConfigFactory Parameter | Environment Variable | Value Format |
|--------------------------------------|---------------------|--------------|
| `github_token` | `GITHUB_TOKEN` | String |
| `github_repo` | `GITHUB_REPO` | `"owner/repo"` |
| `data_path` | `DATA_PATH` | `str(path)` |
| `operation` (save/restore) | `OPERATION` | `"save"` or `"restore"` |
| `include_issues` | `INCLUDE_ISSUES` | `"true"` or `"false"` |
| `include_pull_requests` | `INCLUDE_PULL_REQUESTS` | `"true"` or `"false"` |
| `include_issue_comments` | `INCLUDE_ISSUE_COMMENTS` | `"true"` or `"false"` |
| `include_pull_request_comments` | `INCLUDE_PULL_REQUEST_COMMENTS` | `"true"` or `"false"` |
| `include_sub_issues` | `INCLUDE_SUB_ISSUES` | `"true"` or `"false"` |

### Troubleshooting

#### Issue: "ConfigFactory not found"

**Error:**
```python
ImportError: cannot import name 'ConfigFactory' from 'tests.shared.builders'
```

**Solution:** Update test to use EntityRegistry pattern (see migration steps above)

#### Issue: "ConfigBuilder not found"

**Error:**
```python
ImportError: cannot import name 'ConfigBuilder' from 'tests.shared.builders'
```

**Solution:** Update test to use EntityRegistry pattern (see migration steps above)

#### Issue: Missing environment variables

**Error:**
```python
ValueError: GITHUB_TOKEN environment variable not set
```

**Solution:** Ensure all required environment variables are set with `monkeypatch.setenv()`

#### Issue: Wrong value type for boolean variables

**Error:**
```python
ValueError: Invalid boolean value for INCLUDE_ISSUES
```

**Solution:** Use string values `"true"` or `"false"` (lowercase), not Python booleans

### Migration Checklist

When migrating a test from ConfigBuilder/ConfigFactory:

- [ ] Add `monkeypatch` parameter to test function signature
- [ ] Replace `ConfigFactory.create_*_config()` with environment variable setup
- [ ] Replace `ConfigBuilder()` with environment variable setup
- [ ] Convert all boolean parameters to `"true"`/`"false"` strings
- [ ] Convert paths to strings with `str(path)`
- [ ] Replace config passing with `EntityRegistry.from_environment()`
- [ ] Update service creation to use registry methods
- [ ] Run test to verify it passes
- [ ] Remove old imports (`ConfigFactory`, `ConfigBuilder`)
- [ ] Commit with descriptive message

---

For more information about specific testing scenarios or to contribute to the test suite, see the project's [CONTRIBUTING.md](../../CONTRIBUTING.md) guide.

---

[← Testing Guide](../README.md) | [Best Practices](best-practices.md)
