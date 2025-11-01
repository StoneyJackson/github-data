# Best Practices

[← Testing Guide](../README.md)

## Test Quality Standards

### 1. Test Readability
- Clear test names describing scenarios
- Appropriate fixture usage for test complexity
- Comprehensive test documentation

### 2. Test Maintainability
- Consistent marker usage across similar tests
- Proper fixture selection for test needs
- Regular cleanup of unused fixtures

### 3. Test Reliability
- Proper test isolation with fixture scopes
- Consistent test data patterns
- Reliable error simulation patterns

### 4. Configuration Standards ⭐ **MANDATORY**
- **ALWAYS use EntityRegistry.from_environment()** for test configuration
- **ALWAYS use monkeypatch** for setting environment variables - prevents leaks
- **Use string values** for boolean environment variables (`"true"`, `"false"`)
- **Convert paths to strings** with `str(path)` before setting env vars
- **Set all required variables** (GITHUB_TOKEN, GITHUB_REPO, DATA_PATH, OPERATION)

### 5. Boundary Mock Standards ⭐ **CRITICAL**
- **Never use manual Mock() creation** for boundary objects - protocol incomplete and brittle
- **Always start with factory methods** that guarantee protocol completeness
- **Use MockBoundaryFactory.create_auto_configured()** - ensures 100% protocol completeness
- **Validate mock completeness** with `assert_boundary_mock_complete()` - catches gaps immediately
- **Use hybrid factory pattern for error testing** - combine protocol completeness with custom error simulation

### 6. Error Testing Standards ⭐ **ENHANCED**
- **Use hybrid factory + custom override pattern** for error simulation
- **Start with protocol-complete boundary** via `MockBoundaryFactory.create_auto_configured()`
- **Add custom error behavior** using `side_effect` and `return_value` overrides after factory creation
- **Test configuration errors** with EntityRegistry and environment variables
- **Test error recovery mechanisms** and graceful degradation
- **Use error markers** (`@pytest.mark.error_simulation`) for test organization
- **Cover multiple error scenarios** (timeouts, rate limits, malformed data, connection failures, config errors)

### 7. Modern Infrastructure Standards ⭐ **RECOMMENDED**
- **Use EntityRegistry** for integration tests requiring services
- **Use MockBoundaryFactory** for protocol-complete mocks
- **Leverage existing sample data fixtures** for consistent, realistic test scenarios
- **Use GitHubDataBuilder** for dynamic test data generation when needed
- **Use environment variable mapping** for container tests
- **Follow migration guide** when updating legacy tests to current patterns

## General Testing

1. **AAA Pattern**: Arrange, Act, Assert
2. **Descriptive Names**: Test names should describe expected behavior
3. **Single Responsibility**: One test should test one thing
4. **Independent Tests**: Tests should not depend on each other
5. **Fast Feedback**: Keep unit tests fast (< 1 second)

## Mock Usage

### Standard Mock Usage with Factory Pattern ⭐ **RECOMMENDED**

```python
from tests.shared.mocks.boundary_factory import MockBoundaryFactory

# ✅ Mock external dependencies with protocol completeness
@patch('src.github.service.GitHubApiBoundary')
def test_with_mocked_github(mock_boundary_class, sample_github_data):
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
    mock_boundary_class.return_value = mock_boundary
    # All protocol methods automatically configured ✅
```

## Container Testing

1. **Resource Cleanup**: Always clean up Docker resources
2. **Timeout Handling**: Set appropriate timeouts for slow operations
3. **Error Scenarios**: Test both success and failure cases
4. **Resource Limits**: Test with constrained resources
5. **Image Size**: Validate reasonable image sizes

## Data Management

1. **Temporary Files**: Use `tempfile` for test data
2. **Test Isolation**: Don't share data between tests
3. **Cleanup**: Clean up test resources after use
4. **Realistic Data**: Use realistic test data that matches production

---

[← Testing Guide](../README.md) | [Writing Tests](../writing-tests.md)
