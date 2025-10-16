# MockBoundaryFactory Patterns and Methods Guide

**Date:** 2025-10-16  
**Purpose:** Comprehensive guide to MockBoundaryFactory methods and usage patterns  
**Status:** Complete reference following Phase 3.3 migration  

## Overview

This guide provides comprehensive documentation for MockBoundaryFactory methods and patterns. Following the successful boundary mock migration plan, all GitHub API boundary mocking should use these factory patterns to ensure 100% protocol completeness and maintainability.

## Core Factory Methods

### `create_auto_configured(sample_data=None, validate_completeness=True)`

**Purpose:** Creates a fully automated mock boundary with 100% protocol coverage.

**Recommended Use:** ⭐ **PRIMARY METHOD** - Use for most test scenarios.

```python
from tests.shared.mocks.boundary_factory import MockBoundaryFactory

# ✅ Basic usage with sample data
mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)

# ✅ Empty repository scenario
mock_boundary = MockBoundaryFactory.create_auto_configured({})

# ✅ Custom data scenario
custom_data = {"labels": [{"name": "bug", "color": "red"}]}
mock_boundary = MockBoundaryFactory.create_auto_configured(custom_data)
```

**Features:**
- **Automatic Protocol Discovery:** Finds all protocol methods automatically
- **Intelligent Configuration:** Configures methods based on naming patterns
- **Data Integration:** Maps sample data to appropriate methods
- **Validation:** Optional protocol completeness validation
- **Future-Proof:** Automatically includes new protocol methods

**Method Behavior:**
- **GET methods:** Return sample data or empty lists
- **CREATE methods:** Return mock success responses
- **UPDATE methods:** Return mock updated responses
- **DELETE methods:** Return None
- **Rate limiting methods:** Return realistic rate limit data

### `create_protocol_complete(sample_data=None)`

**Purpose:** Creates protocol-complete mock with mandatory validation.

**Recommended Use:** When you need guaranteed protocol completeness with validation.

```python
# ✅ Protocol-complete with validation guarantee
mock_boundary = MockBoundaryFactory.create_protocol_complete(sample_github_data)

# Automatically validates completeness - raises error if incomplete
```

**Features:**
- **Mandatory Validation:** Always validates protocol completeness
- **Error on Incomplete:** Raises ValueError if any methods missing
- **Development Safety:** Catches protocol changes immediately
- **Documentation:** Provides detailed completeness reporting

### `create_for_restore(success_responses=True)`

**Purpose:** Creates mock boundary optimized for restore operation testing.

**Recommended Use:** For restore workflow tests requiring realistic API responses.

```python
# ✅ Restore workflow with success responses
mock_boundary = MockBoundaryFactory.create_for_restore(success_responses=True)

# ✅ Restore workflow with basic responses
mock_boundary = MockBoundaryFactory.create_for_restore(success_responses=False)
```

**Features:**
- **Empty Repository:** Configures empty repository state for conflict detection
- **Realistic Responses:** Detailed API response formats for restore operations
- **Success Configuration:** Optional detailed success response formatting
- **Restore-Specific:** Optimized for restore workflow patterns

**Detailed Responses Include:**
- Complete label creation responses with URLs and metadata
- Full issue creation responses with user data and timestamps
- Comment creation responses with relationship data

### `create_with_data(data_type="full", **kwargs)`

**Purpose:** Traditional factory method with data type selection.

**Recommended Use:** Legacy support and specific data type scenarios.

```python
# ✅ Full data configuration
mock_boundary = MockBoundaryFactory.create_with_data("full", sample_data=sample_github_data)

# ✅ Empty data configuration
mock_boundary = MockBoundaryFactory.create_with_data("empty")

# ✅ Labels-only configuration
mock_boundary = MockBoundaryFactory.create_with_data("labels_only", sample_data=sample_github_data)
```

**Data Types:**
- **"full":** Complete sample data configuration
- **"empty":** All methods return empty data
- **"labels_only":** Only labels have data, others empty

## Advanced Configuration Methods

### Protocol Validation Methods

```python
from tests.shared.mocks.boundary_factory import MockBoundaryFactory

# ✅ Validate protocol completeness
is_complete, missing_methods = MockBoundaryFactory.validate_protocol_completeness(mock_boundary)

# ✅ Get protocol methods list
protocol_methods = MockBoundaryFactory._get_protocol_methods()

# ✅ Get method signature information
signature = MockBoundaryFactory._get_method_signature("create_issue")
```

### Extension Methods

```python
# ✅ Add PR support to existing mock
MockBoundaryFactory.add_pr_support(mock_boundary, pr_data)

# ✅ Add sub-issues support to existing mock
MockBoundaryFactory.add_sub_issues_support(mock_boundary)
```

## Usage Patterns by Test Type

### Pattern 1: Basic Integration Test

**Scenario:** Standard integration test requiring realistic GitHub API responses.

```python
import pytest
from tests.shared.mocks.boundary_factory import MockBoundaryFactory

@pytest.mark.integration
def test_basic_save_workflow(sample_github_data, temp_data_dir):
    """Test basic save workflow with factory mock."""
    
    # ✅ Use auto-configured factory
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
    
    # Test logic uses complete protocol mock automatically
    # All GitHub API methods properly configured
    # Realistic data responses from sample_github_data
```

**Benefits:**
- **Protocol Complete:** All API methods automatically available
- **Realistic Data:** Uses actual sample data for responses
- **Low Maintenance:** No manual mock configuration required

### Pattern 2: Error Simulation Test

**Scenario:** Testing error handling and resilience with custom error behavior.

```python
@pytest.mark.error_simulation
def test_api_error_handling(sample_github_data):
    """Test API error handling with hybrid factory pattern."""
    
    # ✅ Step 1: Start with protocol-complete foundation
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
    
    # ✅ Step 2: Add specific error simulation
    mock_boundary.create_label.side_effect = [
        {"id": 100, "name": "success"},           # First call succeeds
        Exception("API rate limit exceeded"),     # Second call fails
        {"id": 101, "name": "recovery"}          # Third call succeeds
    ]
    
    # ✅ Step 3: All other methods remain functional
    assert mock_boundary.get_repository_labels() == sample_github_data["labels"]
    
    # Test error handling logic...
```

**Benefits:**
- **Hybrid Approach:** Protocol completeness + custom error simulation
- **Flexible Errors:** Complex error scenarios via side_effect
- **Realistic Foundation:** Base functionality remains realistic
- **Future-Proof:** New protocol methods included automatically

### Pattern 3: Restore Workflow Test

**Scenario:** Testing restore operations with realistic API creation responses.

```python
@pytest.mark.restore_workflow
def test_restore_workflow_success(temp_data_dir):
    """Test restore workflow with realistic API responses."""
    
    # ✅ Use restore-specific factory
    mock_boundary = MockBoundaryFactory.create_for_restore(success_responses=True)
    
    # ✅ Override specific creation responses if needed
    mock_boundary.create_issue.side_effect = [
        {"number": 101, "id": 999, "title": "Restored Issue 1"},
        {"number": 102, "id": 998, "title": "Restored Issue 2"}
    ]
    
    # Test restore logic with realistic API responses
    # Empty repository state for conflict detection
    # Detailed success responses for validation
```

**Benefits:**
- **Restore-Optimized:** Empty repository state and detailed responses
- **Realistic Creation:** Full API response format simulation
- **Conflict Detection:** Empty state enables proper conflict testing

### Pattern 4: Custom Data Integration

**Scenario:** Testing with specific custom data requirements.

```python
def test_custom_data_scenario():
    """Test with custom data while maintaining protocol completeness."""
    
    # ✅ Create custom data that extends sample data
    custom_data = {
        "labels": [
            {"name": "critical", "color": "ff0000", "description": "Critical issues"},
            {"name": "feature", "color": "00ff00", "description": "New features"}
        ],
        "issues": [
            {"number": 1, "title": "Custom Issue", "labels": ["critical"]}
        ],
        "comments": [],
        "pull_requests": []
    }
    
    # ✅ Use factory with custom data
    mock_boundary = MockBoundaryFactory.create_auto_configured(custom_data)
    
    # ✅ Verify custom data integration
    assert mock_boundary.get_repository_labels() == custom_data["labels"]
    assert len(mock_boundary.get_repository_issues()) == 1
    
    # Test custom scenario logic...
```

**Benefits:**
- **Custom Scenarios:** Tailored data for specific test requirements
- **Protocol Complete:** All methods still available even with custom data
- **Data Flexibility:** Mix custom and empty data as needed

### Pattern 5: Performance Testing

**Scenario:** Testing with large datasets for performance validation.

```python
@pytest.mark.performance
@pytest.mark.large_dataset
def test_large_dataset_performance():
    """Test performance with large dataset simulation."""
    
    # ✅ Generate large dataset
    large_data = {
        "labels": [{"name": f"label-{i}", "color": "ffffff"} for i in range(100)],
        "issues": [{"number": i, "title": f"Issue {i}"} for i in range(500)],
        "comments": [{"id": i, "body": f"Comment {i}"} for i in range(1000)]
    }
    
    # ✅ Use factory with large dataset
    mock_boundary = MockBoundaryFactory.create_auto_configured(large_data)
    
    # Test performance with large data volumes
    # All protocol methods still available
    # Realistic response patterns maintained
```

**Benefits:**
- **Scalable Testing:** Easy generation of large datasets
- **Performance Insights:** Realistic large-scale API response simulation
- **Protocol Maintained:** All methods remain available regardless of data size

## Error Patterns and Troubleshooting

### Common Error Simulation Patterns

#### Network and Connection Errors
```python
import requests

def test_network_error_handling(sample_github_data):
    """Test various network error scenarios."""
    
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
    
    # ✅ Connection errors
    mock_boundary.create_issue.side_effect = ConnectionError("Network unreachable")
    
    # ✅ Timeout errors
    mock_boundary.get_repository_labels.side_effect = requests.exceptions.Timeout("Request timeout")
    
    # ✅ HTTP errors
    mock_boundary.create_label.side_effect = requests.exceptions.HTTPError("500 Server Error")
```

#### API Rate Limiting
```python
def test_rate_limiting_scenarios(sample_github_data):
    """Test API rate limiting handling."""
    
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
    
    # ✅ Rate limit status configuration
    mock_boundary.get_rate_limit_status.return_value = {
        "remaining": 0,
        "reset": 3600,
        "limit": 5000
    }
    
    # ✅ Rate limit exception simulation
    mock_boundary.create_issue.side_effect = Exception("API rate limit exceeded. Try again after reset.")
```

#### Malformed Data Responses
```python
def test_malformed_data_handling():
    """Test handling of malformed API responses."""
    
    # ✅ Start with empty configuration
    mock_boundary = MockBoundaryFactory.create_auto_configured({})
    
    # ✅ Simulate malformed responses
    mock_boundary.get_repository_issues.return_value = [
        {"id": None, "title": "", "body": None},  # Missing required fields
        {"number": "invalid", "title": 123},      # Wrong data types
        {}                                        # Empty object
    ]
```

### Troubleshooting Anti-Patterns

#### ❌ Don't: Multiple Factory Configurations
```python
# ❌ AVOID: Multiple factory calls per test
def test_multiple_configurations():
    mock_boundary = MockBoundaryFactory.create_auto_configured(data1)
    mock_boundary = MockBoundaryFactory.create_auto_configured(data2)  # Conflict!
```

#### ❌ Don't: Manual Method Override
```python
# ❌ AVOID: Manual protocol method configuration
def test_manual_override():
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_data)
    mock_boundary.get_repository_labels = Mock(return_value=[])  # Breaks factory pattern
```

#### ❌ Don't: Ignore Protocol Completeness
```python
# ❌ AVOID: Skipping validation in development
def test_without_validation():
    mock_boundary = MockBoundaryFactory.create_auto_configured(
        sample_data, 
        validate_completeness=False  # Don't skip validation
    )
```

## Best Practices Summary

### ✅ Do These
1. **Use `create_auto_configured()` as primary method**
2. **Preserve custom behavior with `side_effect` after factory creation**
3. **Validate protocol completeness during development**
4. **Use sample data fixtures for consistent testing**
5. **Apply hybrid pattern for error testing**
6. **Choose appropriate factory method for test scenario**

### ❌ Avoid These
1. **Manual `Mock()` creation for boundary objects**
2. **Multiple factory configurations per test**
3. **Manual protocol method configuration**
4. **Ignoring protocol completeness validation**
5. **Hardcoded return values without sample data**
6. **Creating incomplete mocks**

## Migration Quick Reference

### Legacy to Factory Pattern
```python
# ❌ LEGACY PATTERN (avoid in new tests)
mock_boundary = Mock()
mock_boundary.get_repository_labels.return_value = []
mock_boundary.get_repository_issues.return_value = sample_data["issues"]
mock_boundary.create_issue.side_effect = Exception("API Error")
# Missing 25+ other protocol methods!

# ✅ FACTORY PATTERN (use for all tests)
mock_boundary = MockBoundaryFactory.create_auto_configured(sample_data)
# All 28+ protocol methods automatically configured ✅
mock_boundary.create_issue.side_effect = Exception("API Error")  # Preserve custom behavior
```

### Method Selection Guide
- **Standard Testing:** `create_auto_configured(sample_github_data)`
- **Empty Repository:** `create_auto_configured({})`
- **Restore Testing:** `create_for_restore(success_responses=True)`
- **Protocol Validation:** `create_protocol_complete(sample_github_data)`
- **Legacy Support:** `create_with_data("full", sample_data=sample_github_data)`

## Advanced Integration Examples

### Complex Workflow Testing
```python
@pytest.mark.integration
@pytest.mark.workflow_services
def test_complete_save_restore_cycle(sample_github_data, temp_data_dir):
    """Test complete save/restore cycle with factory mocks."""
    
    # ✅ Save phase - auto-configured with sample data
    save_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
    
    # ✅ Restore phase - restore-optimized configuration
    restore_boundary = MockBoundaryFactory.create_for_restore(success_responses=True)
    
    # Test complete workflow with both boundary configurations
    # Protocol completeness guaranteed for both phases
```

### Multi-Repository Testing
```python
def test_multi_repository_scenario():
    """Test scenario with multiple repository configurations."""
    
    # ✅ Repository 1 - Full data
    repo1_data = {"labels": [...], "issues": [...]}
    repo1_boundary = MockBoundaryFactory.create_auto_configured(repo1_data)
    
    # ✅ Repository 2 - Empty repository
    repo2_boundary = MockBoundaryFactory.create_auto_configured({})
    
    # Test cross-repository operations
    # Both boundaries are protocol-complete
```

---

*This guide provides comprehensive patterns and methods for MockBoundaryFactory usage. For troubleshooting specific migration issues, see [testing-migration-troubleshooting.md](testing-migration-troubleshooting.md). For general testing guidance, see [testing.md](testing.md).*