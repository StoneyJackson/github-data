# ConfigFactory Extension Implementation Plan

**Date:** 2025-10-23  
**Based on:** Analysis document `2025-10-22-23-06-config-factory-analysis.md`  
**Scope:** Complete redesign and extension of `tests/shared/builders/config_factory.py`

## Implementation Overview

This plan implements a comprehensive ConfigFactory extension to eliminate code duplication across 50+ test files and provide standardized configuration patterns for all testing scenarios.

**Key Decision: No backwards compatibility maintained** - All existing factory methods will be updated to use new patterns for consistency.

## Phase 1: Core Infrastructure Extensions

### 1.1 Environment Variable Factory Methods

**Target:** Eliminate 50+ instances of manual environment setup

```python
class ConfigFactory:
    @staticmethod
    def create_base_env_dict(**overrides) -> Dict[str, str]:
        """Create base environment variables dict for testing."""
        base = {
            "OPERATION": "save",
            "GITHUB_TOKEN": "test-token",
            "GITHUB_REPO": "owner/repo", 
            "DATA_PATH": "/tmp/test",
            "INCLUDE_GIT_REPO": "false",
            "INCLUDE_LABELS": "true",
            "INCLUDE_ISSUES": "true",
            "INCLUDE_ISSUE_COMMENTS": "true",
            "INCLUDE_PULL_REQUESTS": "false",
            "INCLUDE_PULL_REQUEST_COMMENTS": "false",
            "INCLUDE_SUB_ISSUES": "false",
            "INCLUDE_MILESTONES": "false"
        }
        base.update(overrides)
        return base
    
    @staticmethod
    def create_save_env_dict(**overrides) -> Dict[str, str]:
        """Create environment variables for save operations."""
        return ConfigFactory.create_base_env_dict(
            OPERATION="save",
            **overrides
        )
    
    @staticmethod
    def create_restore_env_dict(**overrides) -> Dict[str, str]:
        """Create environment variables for restore operations."""
        return ConfigFactory.create_base_env_dict(
            OPERATION="restore",
            **overrides
        )
    
    @staticmethod
    def create_container_env_dict(**overrides) -> Dict[str, str]:
        """Create environment variables for container tests."""
        return ConfigFactory.create_base_env_dict(
            DATA_PATH="/data",
            **overrides
        )
    
    @staticmethod
    def create_validation_env_dict(field: str, value: str, **overrides) -> Dict[str, str]:
        """Create environment variables for field validation testing."""
        env_dict = ConfigFactory.create_base_env_dict(**overrides)
        env_dict[field] = value
        return env_dict
```

### 1.2 Mock Configuration Factory Methods

**Target:** Standardize mock creation across milestone and feature tests

```python
@staticmethod
def create_mock_config(**overrides) -> Mock:
    """Create a mock ApplicationConfig with realistic defaults."""
    mock_config = Mock(spec=ApplicationConfig)
    
    # Set realistic defaults
    mock_config.operation = "save"
    mock_config.github_token = "test-token"
    mock_config.repository_owner = "test-owner"
    mock_config.repository_name = "test-repo"
    mock_config.data_path = Path("/tmp/test")
    mock_config.include_git_repo = False
    mock_config.include_labels = True
    mock_config.include_issues = True
    mock_config.include_issue_comments = True
    mock_config.include_pull_requests = False
    mock_config.include_pull_request_comments = False
    mock_config.include_sub_issues = False
    mock_config.include_milestones = False
    
    # Apply overrides
    for key, value in overrides.items():
        setattr(mock_config, key, value)
    
    return mock_config

@staticmethod
def create_milestone_mock_config(**overrides) -> Mock:
    """Create a mock config specifically for milestone testing."""
    return ConfigFactory.create_mock_config(
        include_milestones=True,
        **overrides
    )

@staticmethod
def create_pr_mock_config(**overrides) -> Mock:
    """Create a mock config for pull request testing."""
    return ConfigFactory.create_mock_config(
        include_pull_requests=True,
        include_pull_request_comments=True,
        **overrides
    )
```

## Phase 2: Scenario-Specific Factory Methods

### 2.1 Dependency Validation Factories

**Target:** Common test patterns for feature dependencies

```python
@staticmethod
def create_dependency_validation_config(
    feature: str, enabled: bool, dependency_enabled: bool, **overrides
) -> ApplicationConfig:
    """Create config for testing feature dependency validation.
    
    Args:
        feature: Feature to test (e.g., 'pull_request_comments')
        enabled: Whether the feature should be enabled
        dependency_enabled: Whether the dependency should be enabled
    """
    feature_map = {
        'pull_request_comments': ('INCLUDE_PULL_REQUEST_COMMENTS', 'INCLUDE_PULL_REQUESTS'),
        'sub_issues': ('INCLUDE_SUB_ISSUES', 'INCLUDE_ISSUES'),
    }
    
    if feature not in feature_map:
        raise ValueError(f"Unknown feature: {feature}")
    
    feature_var, dependency_var = feature_map[feature]
    
    env_dict = ConfigFactory.create_base_env_dict(
        **{feature_var: str(enabled).lower()},
        **{dependency_var: str(dependency_enabled).lower()},
        **overrides
    )
    
    with patch.dict("os.environ", env_dict, clear=True):
        return ApplicationConfig.from_environment()

@staticmethod
def create_boolean_parsing_config(field: str, value: str, **overrides) -> ApplicationConfig:
    """Create config for testing boolean field parsing with various formats."""
    env_dict = ConfigFactory.create_validation_env_dict(field, value, **overrides)
    
    with patch.dict("os.environ", env_dict, clear=True):
        return ApplicationConfig.from_environment()

@staticmethod
def create_error_scenario_config(invalid_field: str, invalid_value: str, **overrides) -> ApplicationConfig:
    """Create config with invalid values for error testing."""
    env_dict = ConfigFactory.create_validation_env_dict(invalid_field, invalid_value, **overrides)
    
    with patch.dict("os.environ", env_dict, clear=True):
        return ApplicationConfig.from_environment()
```

### 2.2 Feature-Specific Factory Methods

**Target:** Replace existing methods with consistent patterns

```python
@staticmethod
def create_milestone_config(**overrides) -> ApplicationConfig:
    """Create configuration for milestone testing."""
    env_dict = ConfigFactory.create_base_env_dict(
        INCLUDE_MILESTONES="true",
        **overrides
    )
    
    with patch.dict("os.environ", env_dict, clear=True):
        return ApplicationConfig.from_environment()

@staticmethod
def create_git_only_config(**overrides) -> ApplicationConfig:
    """Create configuration for git repository testing only."""
    env_dict = ConfigFactory.create_base_env_dict(
        INCLUDE_GIT_REPO="true",
        INCLUDE_LABELS="false",
        INCLUDE_ISSUES="false", 
        INCLUDE_ISSUE_COMMENTS="false",
        INCLUDE_PULL_REQUESTS="false",
        INCLUDE_PULL_REQUEST_COMMENTS="false",
        INCLUDE_SUB_ISSUES="false",
        INCLUDE_MILESTONES="false",
        **overrides
    )
    
    with patch.dict("os.environ", env_dict, clear=True):
        return ApplicationConfig.from_environment()

@staticmethod
def create_comments_disabled_config(**overrides) -> ApplicationConfig:
    """Create configuration with all comment features disabled."""
    env_dict = ConfigFactory.create_base_env_dict(
        INCLUDE_ISSUE_COMMENTS="false",
        INCLUDE_PULL_REQUEST_COMMENTS="false",
        **overrides
    )
    
    with patch.dict("os.environ", env_dict, clear=True):
        return ApplicationConfig.from_environment()
```

## Phase 3: Update Existing Factory Methods

### 3.1 Standardize Existing Methods

**Breaking Change:** All existing methods updated to use new patterns

```python
@staticmethod
def create_save_config(**overrides) -> ApplicationConfig:
    """Create save operation configuration."""
    env_dict = ConfigFactory.create_save_env_dict(**overrides)
    
    with patch.dict("os.environ", env_dict, clear=True):
        return ApplicationConfig.from_environment()

@staticmethod
def create_restore_config(**overrides) -> ApplicationConfig:
    """Create restore operation configuration."""
    env_dict = ConfigFactory.create_restore_env_dict(**overrides)
    
    with patch.dict("os.environ", env_dict, clear=True):
        return ApplicationConfig.from_environment()

@staticmethod
def create_minimal_config(**overrides) -> ApplicationConfig:
    """Create minimal features configuration for unit tests."""
    env_dict = ConfigFactory.create_base_env_dict(
        INCLUDE_LABELS="false",
        INCLUDE_ISSUES="false",
        INCLUDE_ISSUE_COMMENTS="false",
        **overrides
    )
    
    with patch.dict("os.environ", env_dict, clear=True):
        return ApplicationConfig.from_environment()

@staticmethod
def create_full_config(**overrides) -> ApplicationConfig:
    """Create configuration with all features enabled."""
    env_dict = ConfigFactory.create_base_env_dict(
        INCLUDE_GIT_REPO="true",
        INCLUDE_LABELS="true",
        INCLUDE_ISSUES="true",
        INCLUDE_ISSUE_COMMENTS="true",
        INCLUDE_PULL_REQUESTS="true",
        INCLUDE_PULL_REQUEST_COMMENTS="true",
        INCLUDE_SUB_ISSUES="true",
        INCLUDE_MILESTONES="true",
        **overrides
    )
    
    with patch.dict("os.environ", env_dict, clear=True):
        return ApplicationConfig.from_environment()

@staticmethod
def create_pr_config(**overrides) -> ApplicationConfig:
    """Create configuration with pull request features enabled."""
    env_dict = ConfigFactory.create_base_env_dict(
        INCLUDE_PULL_REQUESTS="true",
        INCLUDE_PULL_REQUEST_COMMENTS="true",
        **overrides
    )
    
    with patch.dict("os.environ", env_dict, clear=True):
        return ApplicationConfig.from_environment()

@staticmethod
def create_issues_only_config(**overrides) -> ApplicationConfig:
    """Create configuration for issues and comments only."""
    env_dict = ConfigFactory.create_base_env_dict(
        INCLUDE_LABELS="false",
        INCLUDE_PULL_REQUESTS="false",
        INCLUDE_PULL_REQUEST_COMMENTS="false",
        INCLUDE_SUB_ISSUES="false",
        INCLUDE_MILESTONES="false",
        **overrides
    )
    
    with patch.dict("os.environ", env_dict, clear=True):
        return ApplicationConfig.from_environment()

@staticmethod
def create_labels_only_config(**overrides) -> ApplicationConfig:
    """Create configuration for labels only."""
    env_dict = ConfigFactory.create_base_env_dict(
        INCLUDE_ISSUES="false",
        INCLUDE_ISSUE_COMMENTS="false",
        INCLUDE_PULL_REQUESTS="false",
        INCLUDE_PULL_REQUEST_COMMENTS="false",
        INCLUDE_SUB_ISSUES="false",
        INCLUDE_MILESTONES="false",
        **overrides
    )
    
    with patch.dict("os.environ", env_dict, clear=True):
        return ApplicationConfig.from_environment()
```

## Phase 4: Test File Migration Strategy

### 4.1 High-Priority Migration Targets

**Files with highest duplication:**

1. **`tests/unit/config/test_settings.py`** - 10+ manual setups
2. **`tests/container/test_docker_container.py`** - Verbose container environment setup
3. **`tests/integration/test_*_feature.py`** files - Repetitive patterns
4. **Milestone test files** - Manual mock creation

### 4.2 Migration Pattern Examples

**Before (current pattern):**
```python
base_env_vars = {
    "OPERATION": "save",
    "GITHUB_TOKEN": "test-token",
    "GITHUB_REPO": "owner/repo",
    "DATA_PATH": "/tmp/test",
    "INCLUDE_PULL_REQUESTS": "false",
    "INCLUDE_PULL_REQUEST_COMMENTS": "true",
}
with patch.dict("os.environ", base_env_vars, clear=True):
    config = ApplicationConfig.from_environment()
```

**After (new pattern):**
```python
config = ConfigFactory.create_dependency_validation_config(
    feature="pull_request_comments",
    enabled=True,
    dependency_enabled=False
)
```

### 4.3 Systematic Migration Process

1. **Update ConfigFactory first** with all new methods
2. **Migrate high-impact files** (10+ manual setups each)
3. **Update integration tests** to use container environment methods
4. **Migrate remaining files** in dependency order
5. **Remove obsolete environment setup code**

## Phase 5: Documentation and Validation

### 5.1 Update Fixture Documentation

Update `tests/shared/fixtures/config_fixtures.py` documentation to reference new ConfigFactory methods.

### 5.2 Add Usage Examples

Create comprehensive usage examples in ConfigFactory docstrings:

```python
class ConfigFactory:
    """Factory for creating ApplicationConfig instances for testing.
    
    Usage Examples:
    
    # Basic configurations
    save_config = ConfigFactory.create_save_config()
    restore_config = ConfigFactory.create_restore_config()
    
    # Feature-specific configurations
    pr_config = ConfigFactory.create_pr_config()
    milestone_config = ConfigFactory.create_milestone_config()
    
    # Dependency validation testing
    invalid_config = ConfigFactory.create_dependency_validation_config(
        feature="pull_request_comments",
        enabled=True,
        dependency_enabled=False
    )
    
    # Environment variable generation
    env_dict = ConfigFactory.create_container_env_dict(
        DATA_PATH="/custom/path"
    )
    
    # Mock configurations
    mock_config = ConfigFactory.create_milestone_mock_config(
        repository_owner="custom-owner"
    )
    """
```

### 5.3 Validation Testing

Create comprehensive tests for new ConfigFactory methods:

```python
class TestConfigFactoryExtensions:
    def test_environment_variable_factories(self):
        """Test all environment variable factory methods."""
        
    def test_mock_configuration_factories(self):
        """Test all mock configuration factory methods."""
        
    def test_scenario_specific_factories(self):
        """Test dependency validation and error scenario factories."""
        
    def test_feature_specific_factories(self):
        """Test all feature-specific factory methods."""
        
    def test_backwards_compatibility_breaking_changes(self):
        """Verify existing methods use new patterns consistently."""
```

## Implementation Priority and Timeline

### Week 1: Core Infrastructure
- Implement Phase 1 (environment variable and mock factories)
- Update existing factory methods (Phase 3)
- Create validation tests

### Week 2: Scenario Methods
- Implement Phase 2 (scenario-specific factories)
- Add comprehensive documentation
- Begin high-priority file migrations

### Week 3: Mass Migration
- Migrate all 50+ target test files
- Update fixture documentation
- Run full test suite validation

### Week 4: Cleanup and Optimization
- Remove obsolete code patterns
- Optimize factory method performance
- Final documentation review

## Expected Impact Metrics

**Code Reduction:**
- **50+ files** with reduced boilerplate (20-30% size reduction each)
- **200+ instances** of manual environment setup eliminated
- **15+ mock creation patterns** standardized

**Developer Experience:**
- **Faster test writing** - One method call vs. 10+ lines of setup
- **Clearer test intent** - Method names describe scenario
- **Consistent patterns** - All tests follow same configuration approach
- **Easier maintenance** - Changes in one place affect all tests

**Maintainability:**
- **Centralized configuration logic** - Single source of truth
- **Version-safe updates** - Configuration changes automatically propagate
- **Reduced test fragility** - Standardized setup reduces test breaks

This implementation plan provides a complete roadmap for transforming the test suite's configuration patterns, eliminating massive code duplication, and establishing a robust foundation for future testing needs.