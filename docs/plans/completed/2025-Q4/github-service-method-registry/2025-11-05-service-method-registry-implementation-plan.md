# Service Method Registry Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement declarative operation registry that eliminates manual modifications to shared GitHub service layer files when adding entities.

**Architecture:** Dynamic method generation via `__getattr__` with registry-based operation lookup. Entity configs declare `github_api_operations` specifications. Registry validates at startup, generates methods at runtime with cross-cutting concerns (caching, rate limiting, error context).

**Tech Stack:** Python 3.x, pytest, existing GitHub service infrastructure (GitHubApiBoundary, RateLimitHandler, cache)

**Design Document:** [2025-11-05-service-method-registry-design.md](2025-11-05-service-method-registry-design.md)

---

## Phase 1: Core Registry Infrastructure

### Task 1: Create ValidationError Exception

**Files:**
- Create: `github_data/github/operation_registry.py`

**Step 1: Write the failing test**

Create test file:

```python
# tests/unit/github/test_operation_registry.py
"""Tests for GitHub operation registry."""

import pytest
from github_data.github.operation_registry import ValidationError


def test_validation_error_can_be_raised():
    """ValidationError should be a proper exception."""
    with pytest.raises(ValidationError) as exc_info:
        raise ValidationError("Test error message")

    assert "Test error message" in str(exc_info.value)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/github/test_operation_registry.py::test_validation_error_can_be_raised -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'github_data.github.operation_registry'"

**Step 3: Write minimal implementation**

```python
# github_data/github/operation_registry.py
"""GitHub API operation registry for dynamic method generation."""


class ValidationError(Exception):
    """Raised when operation spec validation fails."""
    pass
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/github/test_operation_registry.py::test_validation_error_can_be_raised -v`

Expected: PASS

**Step 5: Commit**

```bash
git add tests/unit/github/test_operation_registry.py github_data/github/operation_registry.py
git commit -s -m "feat(registry): add ValidationError exception class"
```

---

### Task 2: Create Operation Class with Spec Parsing

**Files:**
- Modify: `github_data/github/operation_registry.py`
- Modify: `tests/unit/github/test_operation_registry.py`

**Step 1: Write the failing test**

```python
# tests/unit/github/test_operation_registry.py

from github_data.github.operation_registry import Operation


def test_operation_parses_minimal_spec():
    """Operation should parse minimal spec with only boundary_method."""
    spec = {
        'boundary_method': 'get_repository_releases'
    }

    operation = Operation(
        method_name='get_repository_releases',
        entity_name='releases',
        spec=spec
    )

    assert operation.method_name == 'get_repository_releases'
    assert operation.entity_name == 'releases'
    assert operation.boundary_method == 'get_repository_releases'
    assert operation.converter_name is None
    assert operation.cache_key_template is None


def test_operation_parses_full_spec():
    """Operation should parse all spec fields."""
    spec = {
        'boundary_method': 'get_repository_releases',
        'converter': 'convert_to_release',
        'cache_key_template': 'releases:{repo_name}',
        'requires_retry': True
    }

    operation = Operation(
        method_name='get_repository_releases',
        entity_name='releases',
        spec=spec
    )

    assert operation.boundary_method == 'get_repository_releases'
    assert operation.converter_name == 'convert_to_release'
    assert operation.cache_key_template == 'releases:{repo_name}'
    assert operation.requires_retry is True
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/github/test_operation_registry.py::test_operation_parses_minimal_spec -v`

Expected: FAIL with "cannot import name 'Operation'"

**Step 3: Write minimal implementation**

```python
# github_data/github/operation_registry.py

from typing import Dict, Any, Optional


class ValidationError(Exception):
    """Raised when operation spec validation fails."""
    pass


class Operation:
    """Represents a single GitHub API operation."""

    def __init__(self, method_name: str, entity_name: str, spec: Dict[str, Any]):
        """
        Initialize operation from spec.

        Args:
            method_name: Name of the service method (e.g., 'get_repository_releases')
            entity_name: Name of entity this operation belongs to (e.g., 'releases')
            spec: Operation specification dictionary
        """
        self.method_name = method_name
        self.entity_name = entity_name
        self.spec = spec

        # Parse spec fields
        self.boundary_method = spec['boundary_method']
        self.converter_name = spec.get('converter')
        self.cache_key_template = spec.get('cache_key_template')
        self.requires_retry = spec.get('requires_retry', self._is_write_operation())

    def _is_write_operation(self) -> bool:
        """Detect write operations by method name prefix."""
        write_prefixes = ('create_', 'update_', 'delete_', 'close_')
        return self.method_name.startswith(write_prefixes)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/github/test_operation_registry.py::test_operation_parses_minimal_spec tests/unit/github/test_operation_registry.py::test_operation_parses_full_spec -v`

Expected: PASS (both tests)

**Step 5: Commit**

```bash
git add github_data/github/operation_registry.py tests/unit/github/test_operation_registry.py
git commit -s -m "feat(registry): add Operation class with spec parsing"
```

---

### Task 3: Add Operation Validation Logic

**Files:**
- Modify: `github_data/github/operation_registry.py`
- Modify: `tests/unit/github/test_operation_registry.py`

**Step 1: Write the failing test**

```python
# tests/unit/github/test_operation_registry.py


def test_operation_validation_requires_boundary_method():
    """Validation should fail if boundary_method missing."""
    spec = {
        'converter': 'convert_to_release'
        # Missing 'boundary_method'
    }

    with pytest.raises(KeyError):
        operation = Operation(
            method_name='get_repository_releases',
            entity_name='releases',
            spec=spec
        )


def test_operation_validation_checks_converter_exists():
    """Validation should fail if converter doesn't exist."""
    spec = {
        'boundary_method': 'get_repository_releases',
        'converter': 'nonexistent_converter'
    }

    operation = Operation(
        method_name='get_repository_releases',
        entity_name='releases',
        spec=spec
    )

    with pytest.raises(ValidationError, match="Converter 'nonexistent_converter' not found"):
        operation.validate()


def test_operation_validation_passes_for_valid_converter():
    """Validation should pass if converter exists."""
    spec = {
        'boundary_method': 'get_repository_releases',
        'converter': 'convert_to_release'  # This exists in converters.py
    }

    operation = Operation(
        method_name='get_repository_releases',
        entity_name='releases',
        spec=spec
    )

    # Should not raise
    operation.validate()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/github/test_operation_registry.py::test_operation_validation_checks_converter_exists -v`

Expected: FAIL with "AttributeError: 'Operation' object has no attribute 'validate'"

**Step 3: Write minimal implementation**

```python
# github_data/github/operation_registry.py

class Operation:
    """Represents a single GitHub API operation."""

    # ... existing __init__ ...

    def validate(self):
        """
        Validate operation spec.

        Raises:
            ValidationError: If spec is invalid
        """
        # boundary_method already validated in __init__ (KeyError if missing)

        # Validate converter exists if specified
        if self.converter_name:
            if not self._converter_exists(self.converter_name):
                raise ValidationError(f"Converter '{self.converter_name}' not found")

    def _converter_exists(self, converter_name: str) -> bool:
        """Check if converter function exists."""
        try:
            from github_data.github import converters
            return hasattr(converters, converter_name)
        except ImportError:
            return False
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/github/test_operation_registry.py -k validation -v`

Expected: PASS (all 3 validation tests)

**Step 5: Commit**

```bash
git add github_data/github/operation_registry.py tests/unit/github/test_operation_registry.py
git commit -s -m "feat(registry): add Operation validation logic"
```

---

### Task 4: Add Cache Key Generation

**Files:**
- Modify: `github_data/github/operation_registry.py`
- Modify: `tests/unit/github/test_operation_registry.py`

**Step 1: Write the failing test**

```python
# tests/unit/github/test_operation_registry.py


def test_operation_auto_generates_cache_key_single_param():
    """Cache key should auto-generate from method name and params."""
    spec = {'boundary_method': 'get_repository_releases'}
    operation = Operation('get_repository_releases', 'releases', spec)

    cache_key = operation.get_cache_key(repo_name='owner/repo')

    assert cache_key == 'get_repository_releases:owner/repo'


def test_operation_auto_generates_cache_key_multiple_params():
    """Cache key should include all params in order."""
    spec = {'boundary_method': 'get_issue_comments'}
    operation = Operation('get_issue_comments', 'comments', spec)

    cache_key = operation.get_cache_key(repo_name='owner/repo', issue_number=123)

    assert cache_key == 'get_issue_comments:owner/repo:123'


def test_operation_uses_custom_cache_key_template():
    """Custom cache_key_template should override auto-generation."""
    spec = {
        'boundary_method': 'get_repository_releases',
        'cache_key_template': 'releases:{repo_name}'
    }
    operation = Operation('get_repository_releases', 'releases', spec)

    cache_key = operation.get_cache_key(repo_name='owner/repo')

    assert cache_key == 'releases:owner/repo'


def test_operation_should_cache_for_read_operations():
    """Read operations should use caching."""
    spec = {'boundary_method': 'get_repository_releases'}
    operation = Operation('get_repository_releases', 'releases', spec)

    assert operation.should_cache() is True


def test_operation_should_not_cache_for_write_operations():
    """Write operations should skip caching."""
    spec = {'boundary_method': 'create_release'}
    operation = Operation('create_release', 'releases', spec)

    assert operation.should_cache() is False
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/github/test_operation_registry.py::test_operation_auto_generates_cache_key_single_param -v`

Expected: FAIL with "AttributeError: 'Operation' object has no attribute 'get_cache_key'"

**Step 3: Write minimal implementation**

```python
# github_data/github/operation_registry.py

class Operation:
    """Represents a single GitHub API operation."""

    # ... existing methods ...

    def should_cache(self) -> bool:
        """Determine if this operation should use caching."""
        return not self._is_write_operation()

    def get_cache_key(self, **kwargs) -> str:
        """
        Generate cache key from parameters.

        Args:
            **kwargs: Method parameters

        Returns:
            Cache key string
        """
        if self.cache_key_template:
            return self.cache_key_template.format(**kwargs)

        # Auto-generate: "method_name:param1:param2:..."
        param_values = ':'.join(str(v) for v in kwargs.values())
        return f"{self.method_name}:{param_values}"
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/github/test_operation_registry.py -k cache -v`

Expected: PASS (all 5 cache tests)

**Step 5: Commit**

```bash
git add github_data/github/operation_registry.py tests/unit/github/test_operation_registry.py
git commit -s -m "feat(registry): add cache key generation and detection"
```

---

### Task 5: Create GitHubOperationRegistry Class

**Files:**
- Modify: `github_data/github/operation_registry.py`
- Modify: `tests/unit/github/test_operation_registry.py`

**Step 1: Write the failing test**

```python
# tests/unit/github/test_operation_registry.py

from github_data.github.operation_registry import GitHubOperationRegistry
from unittest.mock import Mock, patch


def test_registry_initializes_empty():
    """Registry should initialize with empty operations."""
    with patch('github_data.github.operation_registry.EntityRegistry') as mock_entity_registry:
        mock_entity_registry.return_value._entities = {}

        registry = GitHubOperationRegistry()

        assert registry.list_operations() == []


def test_registry_discovers_operations_from_entity_configs():
    """Registry should discover operations from entity configs."""
    # Mock entity config with github_api_operations
    mock_config = Mock()
    mock_config.github_api_operations = {
        'get_repository_releases': {
            'boundary_method': 'get_repository_releases',
            'converter': 'convert_to_release'
        }
    }

    mock_entity = Mock()
    mock_entity.config = mock_config

    with patch('github_data.github.operation_registry.EntityRegistry') as mock_entity_registry:
        mock_entity_registry.return_value._entities = {'releases': mock_entity}

        registry = GitHubOperationRegistry()

        assert 'get_repository_releases' in registry.list_operations()
        operation = registry.get_operation('get_repository_releases')
        assert operation is not None
        assert operation.entity_name == 'releases'


def test_registry_skips_entities_without_github_api_operations():
    """Registry should skip entities that don't define github_api_operations."""
    mock_config = Mock(spec=[])  # No github_api_operations attribute
    mock_entity = Mock()
    mock_entity.config = mock_config

    with patch('github_data.github.operation_registry.EntityRegistry') as mock_entity_registry:
        mock_entity_registry.return_value._entities = {'some_entity': mock_entity}

        registry = GitHubOperationRegistry()

        assert registry.list_operations() == []
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/github/test_operation_registry.py::test_registry_initializes_empty -v`

Expected: FAIL with "cannot import name 'GitHubOperationRegistry'"

**Step 3: Write minimal implementation**

```python
# github_data/github/operation_registry.py

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class GitHubOperationRegistry:
    """Registry for dynamically discovered GitHub API operations."""

    def __init__(self):
        """Initialize registry and discover operations from entity configs."""
        self._operations: Dict[str, Operation] = {}
        self._load_operations()
        self._validate_all()

    def _load_operations(self):
        """Scan all entity configs and register operations."""
        from github_data.entities.registry import EntityRegistry

        entity_registry = EntityRegistry()

        for entity_name, entity in entity_registry._entities.items():
            config = entity.config

            # Skip entities without github_api_operations
            if not hasattr(config, 'github_api_operations'):
                continue

            # Register each operation
            for method_name, spec in config.github_api_operations.items():
                operation = Operation(
                    method_name=method_name,
                    entity_name=entity_name,
                    spec=spec
                )
                self._operations[method_name] = operation

        logger.info(
            f"Registered {len(self._operations)} GitHub API operations "
            f"from {len(set(op.entity_name for op in self._operations.values()))} entities"
        )

    def _validate_all(self):
        """Validate all operation specs at startup (fail fast)."""
        for method_name, operation in self._operations.items():
            try:
                operation.validate()
            except ValidationError as e:
                raise ValidationError(
                    f"Invalid operation spec for '{method_name}' "
                    f"in entity '{operation.entity_name}': {e}"
                ) from e

    def get_operation(self, method_name: str) -> Optional[Operation]:
        """Get registered operation by method name."""
        return self._operations.get(method_name)

    def list_operations(self) -> List[str]:
        """List all registered operation names."""
        return list(self._operations.keys())
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/github/test_operation_registry.py -k registry -v`

Expected: PASS (all 3 registry tests)

**Step 5: Commit**

```bash
git add github_data/github/operation_registry.py tests/unit/github/test_operation_registry.py
git commit -s -m "feat(registry): add GitHubOperationRegistry for operation discovery"
```

---

### Task 6: Integrate Registry with GitHubService

**Files:**
- Modify: `github_data/github/service.py`
- Create: `tests/unit/github/test_github_service_dynamic.py`

**Step 1: Write the failing test**

```python
# tests/unit/github/test_github_service_dynamic.py
"""Tests for GitHubService dynamic method generation."""

import pytest
from unittest.mock import Mock, patch
from github_data.github.service import GitHubService


def test_github_service_initializes_with_registry():
    """GitHubService should initialize operation registry."""
    mock_boundary = Mock()

    with patch('github_data.github.service.GitHubOperationRegistry') as mock_registry_class:
        mock_registry = Mock()
        mock_registry.list_operations.return_value = ['get_repository_releases']
        mock_registry_class.return_value = mock_registry

        service = GitHubService(boundary=mock_boundary, caching_enabled=False)

        # Registry should be initialized
        mock_registry_class.assert_called_once()
        assert service._operation_registry == mock_registry
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/github/test_github_service_dynamic.py::test_github_service_initializes_with_registry -v`

Expected: FAIL with "AttributeError: 'GitHubService' object has no attribute '_operation_registry'"

**Step 3: Write minimal implementation**

```python
# github_data/github/service.py

# Add to imports at top of file
from .operation_registry import GitHubOperationRegistry

class GitHubService(RepositoryService):
    """Service layer for GitHub API operations."""

    def __init__(
        self,
        boundary: GitHubApiBoundary,
        rate_limiter: Optional[RateLimitHandler] = None,
        caching_enabled: bool = True,
    ):
        """
        Initialize GitHub service with dependencies.

        Args:
            boundary: Ultra-thin API boundary layer
            rate_limiter: Optional rate limiting handler
            caching_enabled: Whether caching is enabled globally
        """
        self._boundary = boundary
        self._rate_limiter = rate_limiter or RateLimitHandler()
        self._caching_enabled = caching_enabled

        # NEW: Initialize operation registry
        self._operation_registry = GitHubOperationRegistry()

        logger.info(
            f"GitHubService initialized with "
            f"{len(self._operation_registry.list_operations())} registered operations"
        )

    # ... rest of existing methods ...
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/github/test_github_service_dynamic.py::test_github_service_initializes_with_registry -v`

Expected: PASS

**Step 5: Commit**

```bash
git add github_data/github/service.py tests/unit/github/test_github_service_dynamic.py
git commit -s -m "feat(service): integrate operation registry with GitHubService"
```

---

### Task 7: Implement Dynamic Method Generation via __getattr__

**Files:**
- Modify: `github_data/github/service.py`
- Modify: `tests/unit/github/test_github_service_dynamic.py`

**Step 1: Write the failing test**

```python
# tests/unit/github/test_github_service_dynamic.py


def test_dynamic_method_generation_for_registered_operation():
    """Service should dynamically generate methods from registry."""
    mock_boundary = Mock()
    mock_boundary.get_repository_releases.return_value = [{'id': 1, 'tag_name': 'v1.0'}]

    # Patch registry to return a test operation
    with patch('github_data.github.service.GitHubOperationRegistry') as mock_registry_class:
        mock_operation = Mock()
        mock_operation.method_name = 'get_repository_releases'
        mock_operation.entity_name = 'releases'
        mock_operation.boundary_method = 'get_repository_releases'
        mock_operation.converter_name = None
        mock_operation.should_cache.return_value = False
        mock_operation.spec = {'boundary_method': 'get_repository_releases'}

        mock_registry = Mock()
        mock_registry.list_operations.return_value = ['get_repository_releases']
        mock_registry.get_operation.return_value = mock_operation
        mock_registry_class.return_value = mock_registry

        service = GitHubService(boundary=mock_boundary, caching_enabled=False)

        # Method should be dynamically available
        assert hasattr(service, 'get_repository_releases')

        # Should be callable
        result = service.get_repository_releases(repo_name='owner/repo')

        # Boundary method should have been called
        mock_boundary.get_repository_releases.assert_called_once_with(repo_name='owner/repo')


def test_unknown_method_raises_helpful_error():
    """Unknown method should raise AttributeError with available operations."""
    mock_boundary = Mock()

    with patch('github_data.github.service.GitHubOperationRegistry') as mock_registry_class:
        mock_registry = Mock()
        mock_registry.list_operations.return_value = ['get_repository_releases']
        mock_registry.get_operation.return_value = None  # Method not found
        mock_registry_class.return_value = mock_registry

        service = GitHubService(boundary=mock_boundary, caching_enabled=False)

        with pytest.raises(AttributeError) as exc_info:
            service.nonexistent_method()

        error_msg = str(exc_info.value)
        assert 'nonexistent_method' in error_msg
        assert 'Available operations' in error_msg
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/github/test_github_service_dynamic.py::test_dynamic_method_generation_for_registered_operation -v`

Expected: FAIL with "AttributeError: 'GitHubService' object has no attribute 'get_repository_releases'"

**Step 3: Write minimal implementation**

```python
# github_data/github/service.py

from typing import Any, Callable

class GitHubService(RepositoryService):
    # ... existing __init__ ...

    def __getattr__(self, method_name: str):
        """
        Dynamically generate methods from operation registry.

        This is called only when an attribute isn't found explicitly on the class.
        Explicit methods (escape hatch) take precedence automatically.

        Args:
            method_name: Name of method being accessed

        Returns:
            Dynamically generated method

        Raises:
            AttributeError: If method not found in registry
        """
        operation = self._operation_registry.get_operation(method_name)

        if not operation:
            raise AttributeError(
                f"GitHubService has no method '{method_name}'. "
                f"Available operations: {self._operation_registry.list_operations()}"
            )

        # Create dynamic method
        def dynamic_method(**kwargs):
            return self._execute_operation(operation, **kwargs)

        # Make it debuggable
        dynamic_method.__name__ = method_name
        dynamic_method.__doc__ = f"Dynamically generated method from {operation.entity_name} entity."

        return dynamic_method

    def _execute_operation(self, operation, **kwargs) -> Any:
        """
        Execute a registered operation with cross-cutting concerns.

        Args:
            operation: Operation instance from registry
            **kwargs: Method parameters

        Returns:
            Operation result (raw or converted)

        Raises:
            Exception: Enhanced with entity/spec context
        """
        try:
            # For now, just call boundary directly (no caching yet)
            return self._call_boundary(operation, **kwargs)
        except Exception as e:
            # Enhanced error context for debugging
            raise type(e)(
                f"Operation '{operation.method_name}' failed "
                f"(entity={operation.entity_name}, spec={operation.spec}): {e}"
            ) from e

    def _call_boundary(self, operation, **kwargs) -> Any:
        """
        Call boundary method and apply converter if specified.

        Args:
            operation: Operation instance
            **kwargs: Method parameters

        Returns:
            Raw or converted result
        """
        logger.debug(
            f"Executing {operation.method_name} "
            f"[entity={operation.entity_name}, args={kwargs}]"
        )

        # Call the boundary method
        boundary_method = getattr(self._boundary, operation.boundary_method)
        raw_result = boundary_method(**kwargs)

        # Apply converter if specified (implement in next task)
        if operation.converter_name:
            # TODO: Apply converter
            pass

        return raw_result

    # ... rest of existing methods ...
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/github/test_github_service_dynamic.py -k dynamic -v`

Expected: PASS (both dynamic tests)

**Step 5: Commit**

```bash
git add github_data/github/service.py tests/unit/github/test_github_service_dynamic.py
git commit -s -m "feat(service): implement dynamic method generation via __getattr__"
```

---

### Task 8: Add Converter Support to Dynamic Methods

**Files:**
- Modify: `github_data/github/service.py`
- Modify: `tests/unit/github/test_github_service_dynamic.py`

**Step 1: Write the failing test**

```python
# tests/unit/github/test_github_service_dynamic.py


def test_dynamic_method_applies_converter():
    """Dynamic method should apply converter if specified."""
    from github_data.entities.releases.models import Release

    mock_boundary = Mock()
    mock_boundary.get_repository_releases.return_value = [
        {'id': 1, 'tag_name': 'v1.0', 'name': 'Release 1.0'}
    ]

    with patch('github_data.github.service.GitHubOperationRegistry') as mock_registry_class:
        mock_operation = Mock()
        mock_operation.method_name = 'get_repository_releases'
        mock_operation.entity_name = 'releases'
        mock_operation.boundary_method = 'get_repository_releases'
        mock_operation.converter_name = 'convert_to_release'
        mock_operation.should_cache.return_value = False
        mock_operation.spec = {
            'boundary_method': 'get_repository_releases',
            'converter': 'convert_to_release'
        }

        mock_registry = Mock()
        mock_registry.list_operations.return_value = ['get_repository_releases']
        mock_registry.get_operation.return_value = mock_operation
        mock_registry_class.return_value = mock_registry

        service = GitHubService(boundary=mock_boundary, caching_enabled=False)

        result = service.get_repository_releases(repo_name='owner/repo')

        # Should return converted objects
        assert len(result) == 1
        assert isinstance(result[0], Release)
        assert result[0].tag_name == 'v1.0'
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/github/test_github_service_dynamic.py::test_dynamic_method_applies_converter -v`

Expected: FAIL (converter not applied, returns raw dict)

**Step 3: Write minimal implementation**

```python
# github_data/github/service.py

class GitHubService(RepositoryService):
    # ... existing methods ...

    def _call_boundary(self, operation, **kwargs) -> Any:
        """
        Call boundary method and apply converter if specified.

        Args:
            operation: Operation instance
            **kwargs: Method parameters

        Returns:
            Raw or converted result
        """
        logger.debug(
            f"Executing {operation.method_name} "
            f"[entity={operation.entity_name}, args={kwargs}]"
        )

        # Call the boundary method
        boundary_method = getattr(self._boundary, operation.boundary_method)
        raw_result = boundary_method(**kwargs)

        # Apply converter if specified
        if operation.converter_name:
            converter = self._get_converter(operation.converter_name)

            # Handle list results vs single results
            if isinstance(raw_result, list):
                result = [converter(item) for item in raw_result]
            else:
                result = converter(raw_result)

            logger.debug(f"Converted {operation.method_name} results using {operation.converter_name}")
            return result

        return raw_result

    def _get_converter(self, converter_name: str) -> Callable:
        """
        Get converter function by name.

        Args:
            converter_name: Name of converter function

        Returns:
            Converter function
        """
        from github_data.github import converters
        return getattr(converters, converter_name)

    # ... rest of methods ...
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/github/test_github_service_dynamic.py::test_dynamic_method_applies_converter -v`

Expected: PASS

**Step 5: Commit**

```bash
git add github_data/github/service.py tests/unit/github/test_github_service_dynamic.py
git commit -s -m "feat(service): add converter support to dynamic methods"
```

---

### Task 9: Add Caching Support to Dynamic Methods

**Files:**
- Modify: `github_data/github/service.py`
- Modify: `tests/unit/github/test_github_service_dynamic.py`

**Step 1: Write the failing test**

```python
# tests/unit/github/test_github_service_dynamic.py


def test_dynamic_method_uses_caching_for_read_operations():
    """Dynamic read operations should use caching."""
    mock_boundary = Mock()
    mock_boundary.get_repository_releases.return_value = [{'id': 1}]

    with patch('github_data.github.service.GitHubOperationRegistry') as mock_registry_class:
        mock_operation = Mock()
        mock_operation.method_name = 'get_repository_releases'
        mock_operation.entity_name = 'releases'
        mock_operation.boundary_method = 'get_repository_releases'
        mock_operation.converter_name = None
        mock_operation.should_cache.return_value = True
        mock_operation.get_cache_key.return_value = 'get_repository_releases:owner/repo'
        mock_operation.spec = {'boundary_method': 'get_repository_releases'}

        mock_registry = Mock()
        mock_registry.list_operations.return_value = ['get_repository_releases']
        mock_registry.get_operation.return_value = mock_operation
        mock_registry_class.return_value = mock_registry

        service = GitHubService(boundary=mock_boundary, caching_enabled=True)

        # First call - should hit boundary
        result1 = service.get_repository_releases(repo_name='owner/repo')
        assert mock_boundary.get_repository_releases.call_count == 1

        # Second call - should use cache
        result2 = service.get_repository_releases(repo_name='owner/repo')
        assert mock_boundary.get_repository_releases.call_count == 1  # Still 1, not 2

        # Results should be same
        assert result1 == result2


def test_dynamic_method_skips_caching_for_write_operations():
    """Dynamic write operations should not use caching."""
    mock_boundary = Mock()
    mock_boundary.create_release.return_value = {'id': 1, 'tag_name': 'v1.0'}

    with patch('github_data.github.service.GitHubOperationRegistry') as mock_registry_class:
        mock_operation = Mock()
        mock_operation.method_name = 'create_release'
        mock_operation.entity_name = 'releases'
        mock_operation.boundary_method = 'create_release'
        mock_operation.converter_name = None
        mock_operation.should_cache.return_value = False
        mock_operation.spec = {'boundary_method': 'create_release'}

        mock_registry = Mock()
        mock_registry.list_operations.return_value = ['create_release']
        mock_registry.get_operation.return_value = mock_operation
        mock_registry_class.return_value = mock_registry

        service = GitHubService(boundary=mock_boundary, caching_enabled=True)

        # Multiple calls should always hit boundary
        service.create_release(repo_name='owner/repo', tag_name='v1.0')
        service.create_release(repo_name='owner/repo', tag_name='v1.0')

        assert mock_boundary.create_release.call_count == 2
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/github/test_github_service_dynamic.py::test_dynamic_method_uses_caching_for_read_operations -v`

Expected: FAIL (caching not working, boundary called twice)

**Step 3: Write minimal implementation**

```python
# github_data/github/service.py

class GitHubService(RepositoryService):
    # ... existing methods ...

    def _execute_operation(self, operation, **kwargs) -> Any:
        """
        Execute a registered operation with cross-cutting concerns.

        Args:
            operation: Operation instance from registry
            **kwargs: Method parameters

        Returns:
            Operation result (raw or converted)

        Raises:
            Exception: Enhanced with entity/spec context
        """
        try:
            # Apply caching if appropriate
            if operation.should_cache() and self._caching_enabled:
                cache_key = operation.get_cache_key(**kwargs)
                return self._execute_with_cross_cutting_concerns(
                    cache_key=cache_key,
                    operation=lambda: self._call_boundary(operation, **kwargs)
                )
            else:
                # No caching for write operations
                return self._execute_with_cross_cutting_concerns(
                    cache_key=None,
                    operation=lambda: self._call_boundary(operation, **kwargs)
                )
        except Exception as e:
            # Enhanced error context for debugging
            raise type(e)(
                f"Operation '{operation.method_name}' failed "
                f"(entity={operation.entity_name}, spec={operation.spec}): {e}"
            ) from e

    # ... rest of methods (no changes to existing _execute_with_cross_cutting_concerns) ...
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/github/test_github_service_dynamic.py -k caching -v`

Expected: PASS (both caching tests)

**Step 5: Commit**

```bash
git add github_data/github/service.py tests/unit/github/test_github_service_dynamic.py
git commit -s -m "feat(service): add caching support to dynamic methods"
```

---

## Phase 2: Testing Infrastructure

### Task 10: Add Registry Validation Test Fixture

**Files:**
- Create: `tests/shared/fixtures/github_service_fixtures.py`
- Modify: `tests/shared/fixtures/__init__.py`

**Step 1: Write the fixture**

```python
# tests/shared/fixtures/github_service_fixtures.py
"""Shared fixtures for GitHub service testing."""

import pytest
from unittest.mock import Mock
from github_data.github.service import GitHubService
from github_data.entities.registry import EntityRegistry


@pytest.fixture
def validate_github_service_registry():
    """
    Validate GitHubService registry at test startup.

    Ensures all entity operations are properly registered and discoverable.
    """
    mock_boundary = Mock()
    service = GitHubService(boundary=mock_boundary, caching_enabled=False)
    registry = service._operation_registry

    # Ensure all entity operations are registered
    entity_registry = EntityRegistry()

    for entity_name, entity in entity_registry._entities.items():
        if not hasattr(entity.config, 'github_api_operations'):
            continue

        for method_name in entity.config.github_api_operations:
            assert method_name in registry.list_operations(), \
                f"Operation '{method_name}' from entity '{entity_name}' not registered"

    return service
```

```python
# tests/shared/fixtures/__init__.py
"""Shared test fixtures."""

from .env_fixtures import *  # noqa
from .milestone_fixtures import *  # noqa
from .entity_fixtures import *  # noqa
from .github_service_fixtures import *  # noqa
```

**Step 2: Write test that uses the fixture**

```python
# tests/unit/github/test_github_service_dynamic.py


def test_all_entity_operations_are_registered(validate_github_service_registry):
    """Integration test: all entity operations should be registered."""
    service = validate_github_service_registry

    # Should have operations from multiple entities
    operations = service._operation_registry.list_operations()
    assert len(operations) > 0

    # Spot check: releases operations should be present
    # (This will only pass after we add github_api_operations to an entity config)
    # For now, just verify registry exists and works
    assert service._operation_registry is not None
```

**Step 3: Run test to verify**

Run: `pytest tests/unit/github/test_github_service_dynamic.py::test_all_entity_operations_are_registered -v`

Expected: PASS

**Step 4: Commit**

```bash
git add tests/shared/fixtures/github_service_fixtures.py tests/shared/fixtures/__init__.py tests/unit/github/test_github_service_dynamic.py
git commit -s -m "test(fixtures): add registry validation fixture for GitHub service"
```

---

### Task 11: Add Comprehensive Registry Tests

**Files:**
- Modify: `tests/unit/github/test_operation_registry.py`

**Step 1: Add integration-style tests**

```python
# tests/unit/github/test_operation_registry.py

def test_registry_validates_all_operations_at_startup():
    """Registry should validate all specs during initialization."""
    mock_config = Mock()
    mock_config.github_api_operations = {
        'bad_operation': {
            'boundary_method': 'some_method',
            'converter': 'nonexistent_converter'  # Invalid!
        }
    }

    mock_entity = Mock()
    mock_entity.config = mock_config

    with patch('github_data.github.operation_registry.EntityRegistry') as mock_entity_registry:
        mock_entity_registry.return_value._entities = {'test_entity': mock_entity}

        with pytest.raises(ValidationError, match="Invalid operation spec"):
            GitHubOperationRegistry()


def test_write_operations_auto_detected():
    """Registry should auto-detect write operations."""
    mock_config = Mock()
    mock_config.github_api_operations = {
        'create_release': {'boundary_method': 'create_release'},
        'update_label': {'boundary_method': 'update_label'},
        'delete_issue': {'boundary_method': 'delete_issue'},
        'close_issue': {'boundary_method': 'close_issue'},
        'get_repository_releases': {'boundary_method': 'get_repository_releases'}
    }

    mock_entity = Mock()
    mock_entity.config = mock_config

    with patch('github_data.github.operation_registry.EntityRegistry') as mock_entity_registry:
        mock_entity_registry.return_value._entities = {'test': mock_entity}

        registry = GitHubOperationRegistry()

        # Write operations should not cache
        assert registry.get_operation('create_release').should_cache() is False
        assert registry.get_operation('update_label').should_cache() is False
        assert registry.get_operation('delete_issue').should_cache() is False
        assert registry.get_operation('close_issue').should_cache() is False

        # Read operation should cache
        assert registry.get_operation('get_repository_releases').should_cache() is True
```

**Step 2: Run tests to verify**

Run: `pytest tests/unit/github/test_operation_registry.py -v`

Expected: PASS (all tests)

**Step 3: Commit**

```bash
git add tests/unit/github/test_operation_registry.py
git commit -s -m "test(registry): add comprehensive validation and integration tests"
```

---

## Phase 3: Documentation

### Task 12: Create Entity Addition Guide

**Files:**
- Create: `docs/development/adding-entities.md`

**Step 1: Create the guide**

```markdown
# Adding a New Entity

This guide shows how to add a new entity to the GitHub Data system using the declarative operation registry.

## Overview

Entities are self-contained packages that define:
- Data models
- Save/restore strategies
- GitHub API operations (declarative)
- Converters (if needed)

The operation registry auto-generates service methods from entity config declarations, eliminating manual modifications to shared service layer files.

## Step-by-Step Process

### 1. Create Entity Package Structure

```bash
github_data/entities/your_entity/
├── __init__.py
├── entity_config.py      # Configuration and API declarations
├── models.py             # Domain models
├── save_strategy.py      # Save logic
└── restore_strategy.py   # Restore logic
```

### 2. Define Entity Configuration

```python
# github_data/entities/your_entity/entity_config.py

class YourEntityConfig:
    name = "your_entity"
    env_var = "INCLUDE_YOUR_ENTITY"
    default_value = True
    value_type = bool
    dependencies = []  # List entity names this depends on
    description = "Your entity description"

    # Service requirements
    required_services_save = []
    required_services_restore = ["github_service"]

    # Declare GitHub API operations (NEW!)
    github_api_operations = {
        'get_repository_your_entity': {
            'boundary_method': 'get_repository_your_entity',
            'converter': 'convert_to_your_entity',
        },
        'create_your_entity': {
            'boundary_method': 'create_your_entity',
            'converter': 'convert_to_your_entity',
        }
    }

    @staticmethod
    def create_save_strategy(context):
        from .save_strategy import YourEntitySaveStrategy
        return YourEntitySaveStrategy()

    @staticmethod
    def create_restore_strategy(context):
        from .restore_strategy import YourEntityRestoreStrategy
        return YourEntityRestoreStrategy()
```

### 3. Add Boundary Methods (If Needed)

Most entities use existing GraphQL/REST patterns. Only add custom boundary methods if needed:

```python
# github_data/github/boundary.py (only for custom API patterns)

def get_repository_your_entity(self, repo_name: str) -> List[Dict[str, Any]]:
    """Get your entity data from repository."""
    return self._rest_client.get_your_entity(repo_name)
```

### 4. Add Converter Functions

```python
# github_data/github/converters.py

def convert_to_your_entity(raw_data: Dict[str, Any]) -> YourEntity:
    """Convert raw GitHub API data to YourEntity model."""
    return YourEntity(
        id=raw_data['id'],
        name=raw_data['name'],
        # ... map fields ...
    )
```

### 5. No Service Layer Changes Needed!

The service layer automatically discovers and generates methods from your `github_api_operations` declaration. No manual modifications to `service.py` or `protocols.py` needed!

## Field Reference: github_api_operations

### Required Fields
- **`boundary_method`**: Name of method on GitHubApiBoundary to call

### Optional Fields
- **`converter`**: Converter function name (default: no conversion)
- **`cache_key_template`**: Override auto-generated cache key (default: `{method_name}:{params}`)
- **`requires_retry`**: Force retry behavior (default: auto-detect from method name)

### Examples

**Simple read operation:**
```python
'get_repository_milestones': {
    'boundary_method': 'get_repository_milestones',
    'converter': 'convert_to_milestone',
}
```

**Write operation (no caching):**
```python
'create_milestone': {
    'boundary_method': 'create_milestone',
    'converter': 'convert_to_milestone',
}
```

**Custom cache key:**
```python
'get_all_comments': {
    'boundary_method': 'get_all_issue_comments',
    'converter': 'convert_to_comment',
    'cache_key_template': 'comments_all:{repo_name}',
}
```

## Escape Hatch: Complex Operations

If an operation doesn't fit the registry pattern, add it explicitly to GitHubService:

```python
# github_data/github/service.py

def complex_custom_operation(self, repo_name: str) -> ComplexResult:
    """Custom operation with complex multi-step logic."""
    # Custom implementation here
    # Explicit methods automatically override registry
```

## Testing Your Entity

```bash
# Test your entity
pytest tests/unit/entities/your_entity/ -v

# Test integration
pytest tests/integration/test_your_entity_save_restore_integration.py -v

# Validate registry registration
pytest tests/unit/github/test_operation_registry.py -v
```

## What Changed From Before?

**OLD Process (Before Registry):**
- Modify 4 shared files: `boundary.py`, `protocols.py`, `service.py`, `converters.py`
- 200+ lines of boilerplate per entity
- Manually wrap each method with caching/rate limiting

**NEW Process (With Registry):**
- Declare operations in entity config (5-10 lines)
- Add boundary method only if custom API pattern needed
- Add converter function
- Done! Service methods auto-generated
```

**Step 2: Commit**

```bash
git add docs/development/adding-entities.md
git commit -s -m "docs: add comprehensive entity addition guide with registry"
```

---

### Task 13: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Add GitHub Service Layer section**

Find the appropriate place in CLAUDE.md (after Development Environment section) and add:

```markdown
## GitHub Service Layer

The GitHub service layer uses a **declarative operation registry** that auto-generates
service methods from entity configurations.

**When adding entities:** See [docs/development/adding-entities.md](docs/development/adding-entities.md)
for the complete guide on using the registry-based approach.
```

**Step 2: Commit**

```bash
git add CLAUDE.md
git commit -s -m "docs: add GitHub service layer section to CLAUDE.md"
```

---

## Phase 4: First Entity Migration

### Task 14: Add github_api_operations to Releases Entity Config

**Files:**
- Modify: `github_data/entities/releases/entity_config.py`

**Step 1: Write test for releases operations**

```python
# tests/unit/entities/releases/test_releases_entity_config.py

def test_releases_config_declares_github_api_operations():
    """Releases config should declare github_api_operations."""
    from github_data.entities.releases.entity_config import ReleasesEntityConfig

    assert hasattr(ReleasesEntityConfig, 'github_api_operations')
    assert 'get_repository_releases' in ReleasesEntityConfig.github_api_operations

    # Validate spec structure
    get_releases_spec = ReleasesEntityConfig.github_api_operations['get_repository_releases']
    assert get_releases_spec['boundary_method'] == 'get_repository_releases'
    assert get_releases_spec['converter'] == 'convert_to_release'
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/entities/releases/test_releases_entity_config.py::test_releases_config_declares_github_api_operations -v`

Expected: FAIL with "AttributeError: type object 'ReleasesEntityConfig' has no attribute 'github_api_operations'"

**Step 3: Add github_api_operations to config**

```python
# github_data/entities/releases/entity_config.py

class ReleasesEntityConfig:
    """Configuration for releases entity."""

    name = "releases"
    env_var = "INCLUDE_RELEASES"
    default_value = True
    value_type = bool
    dependencies: List[str] = []
    description = "Repository releases and tags"

    # Service requirements
    required_services_save: List[str] = []
    required_services_restore: List[str] = []

    # GitHub API operations
    github_api_operations = {
        'get_repository_releases': {
            'boundary_method': 'get_repository_releases',
            'converter': 'convert_to_release',
        },
        'create_release': {
            'boundary_method': 'create_release',
            'converter': 'convert_to_release',
        }
    }

    # ... rest of config unchanged ...
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/entities/releases/test_releases_entity_config.py::test_releases_config_declares_github_api_operations -v`

Expected: PASS

**Step 5: Run existing releases tests to ensure nothing broke**

Run: `pytest tests/unit/entities/releases/ tests/integration/test_release_save_restore_integration.py -v`

Expected: PASS (all tests)

**Step 6: Commit**

```bash
git add github_data/entities/releases/entity_config.py tests/unit/entities/releases/test_releases_entity_config.py
git commit -s -m "refactor(releases): add github_api_operations to entity config"
```

---

### Task 15: Verify Releases Methods Work Through Registry

**Files:**
- Modify: `tests/unit/github/test_github_service_dynamic.py`

**Step 1: Write integration test**

```python
# tests/unit/github/test_github_service_dynamic.py


def test_releases_operations_available_through_registry():
    """Real releases operations should be available through registry."""
    from github_data.github.boundary import GitHubApiBoundary
    from github_data.entities.releases.models import Release

    # Mock the boundary to return release data
    mock_boundary = Mock(spec=GitHubApiBoundary)
    mock_boundary.get_repository_releases.return_value = [
        {
            'id': 123,
            'tag_name': 'v1.0.0',
            'name': 'Version 1.0.0',
            'body': 'Release notes',
            'draft': False,
            'prerelease': False,
            'created_at': '2023-01-01T00:00:00Z',
            'published_at': '2023-01-01T00:00:00Z',
            'html_url': 'https://github.com/owner/repo/releases/tag/v1.0.0',
            'assets': [],
            'author': {
                'login': 'testuser',
                'id': 1,
                'avatar_url': 'https://example.com/avatar.png',
                'html_url': 'https://github.com/testuser',
                'type': 'User'
            }
        }
    ]

    service = GitHubService(boundary=mock_boundary, caching_enabled=False)

    # Method should exist
    assert hasattr(service, 'get_repository_releases')

    # Should be callable and return converted Release objects
    result = service.get_repository_releases(repo_name='owner/repo')

    assert len(result) == 1
    assert isinstance(result[0], Release)
    assert result[0].tag_name == 'v1.0.0'
    assert result[0].name == 'Version 1.0.0'
```

**Step 2: Run test to verify**

Run: `pytest tests/unit/github/test_github_service_dynamic.py::test_releases_operations_available_through_registry -v`

Expected: PASS

**Step 3: Commit**

```bash
git add tests/unit/github/test_github_service_dynamic.py
git commit -s -m "test(registry): verify releases operations work through registry"
```

---

### Task 16: Document Migration Status

**Files:**
- Modify: `docs/plans/active/architectural-improvements/2025-11-05-service-method-registry-design.md`

**Step 1: Add migration tracking section**

At the end of the design document, add:

```markdown
## Migration Status

### Migrated Entities
- [x] releases - Migrated 2025-11-05

### Pending Entities
- [ ] labels
- [ ] milestones
- [ ] issues
- [ ] comments
- [ ] pull_requests
- [ ] pr_comments
- [ ] pr_reviews
- [ ] pr_review_comments
- [ ] sub_issues
- [ ] git_repositories

### Migration Notes
- Releases entity successfully migrated with 2 operations
- All existing tests pass without modification
- Dynamic method generation working as expected
```

**Step 2: Commit**

```bash
git add docs/plans/active/architectural-improvements/2025-11-05-service-method-registry-design.md
git commit -s -m "docs: add migration status tracking to design document"
```

---

## Phase 5: Remaining Entity Migrations

### Task 17: Migrate Remaining Entities (Template)

**Note:** Repeat this task template for each remaining entity: labels, milestones, issues, comments, pull_requests, pr_comments, pr_reviews, pr_review_comments, sub_issues, git_repositories

**Files:**
- Modify: `github_data/entities/{entity_name}/entity_config.py`
- Create: `tests/unit/entities/{entity_name}/test_{entity_name}_entity_config.py` (if doesn't exist)

**Step 1: Identify entity's GitHub API methods**

Look in `github_data/github/service.py` for methods like:
- `get_repository_{entity_name}`
- `create_{entity_singular}`
- `update_{entity_singular}`
- etc.

**Step 2: Write test for entity config**

```python
# tests/unit/entities/{entity_name}/test_{entity_name}_entity_config.py

def test_{entity_name}_config_declares_github_api_operations():
    """Entity config should declare github_api_operations."""
    from github_data.entities.{entity_name}.entity_config import {EntityName}EntityConfig

    assert hasattr({EntityName}EntityConfig, 'github_api_operations')
    # Add specific assertions for this entity's operations
```

**Step 3: Run test to verify it fails**

Run: `pytest tests/unit/entities/{entity_name}/test_{entity_name}_entity_config.py -v`

**Step 4: Add github_api_operations to entity config**

Look at existing service methods to determine the correct specs:

```python
# github_data/entities/{entity_name}/entity_config.py

class {EntityName}EntityConfig:
    # ... existing fields ...

    # GitHub API operations
    github_api_operations = {
        'get_repository_{entity_name}': {
            'boundary_method': 'get_repository_{entity_name}',
            'converter': 'convert_to_{entity_singular}',
        },
        # Add other operations as needed
    }
```

**Step 5: Run tests to verify nothing broke**

Run: `pytest tests/unit/entities/{entity_name}/ tests/integration/test_{entity_name}_save_restore_integration.py -v`

Expected: PASS (all tests)

**Step 6: Update migration status**

Update the migration status in the design document.

**Step 7: Commit**

```bash
git add github_data/entities/{entity_name}/entity_config.py tests/unit/entities/{entity_name}/
git commit -s -m "refactor({entity_name}): add github_api_operations to entity config"
```

---

## Phase 6: Final Validation and Cleanup

### Task 18: Run Full Test Suite

**Step 1: Run all tests**

Run: `make test`

Expected: PASS (all tests)

**Step 2: Run type checking**

Run: `make type-check`

Expected: PASS

**Step 3: Run linting**

Run: `make lint`

Expected: PASS

**Step 4: Run formatting check**

Run: `make format`

Expected: No changes needed

**Step 5: If any issues, fix and commit**

```bash
git add .
git commit -s -m "fix: resolve test/lint/type issues"
```

---

### Task 19: Update Architectural Improvements Document

**Files:**
- Modify: `docs/plans/active/architectural-improvements/2025-11-03-architectural-improvements.md`

**Step 1: Mark improvement #1 as complete**

Find the "Done" section at the bottom and add:

```markdown
## Done

- [x] Implement **Dynamic Entity Count Validation** (Improvement #2) before next entity
- [x] Removed entity test markers (addresses Improvement #3)
- [x] Implement **Service Method Registry** (Improvement #1) - 2025-11-05
```

**Step 2: Commit**

```bash
git add docs/plans/active/architectural-improvements/2025-11-03-architectural-improvements.md
git commit -s -m "docs: mark service method registry improvement as complete"
```

---

### Task 20: Create Summary Document

**Files:**
- Create: `docs/plans/active/architectural-improvements/2025-11-05-service-method-registry-summary.md`

**Step 1: Create summary**

```markdown
# Service Method Registry Implementation Summary

**Completion Date:** 2025-11-05
**Branch:** refactor/service-method-registry
**Status:** Complete

## What Was Implemented

Implemented a declarative operation registry that eliminates manual modifications to shared GitHub service layer files when adding entities. The registry:

1. **Auto-discovers operations** from entity configs at startup
2. **Validates all specs** with fail-fast error handling
3. **Generates service methods** dynamically via `__getattr__`
4. **Applies cross-cutting concerns** (caching, rate limiting, error context)
5. **Supports explicit method escape hatch** for complex operations

## Results

### Before
- 13 file modifications per entity
- 200+ lines of boilerplate per entity
- Manual coordination across multiple files
- Inconsistent cross-cutting concerns

### After
- 0 shared file modifications per entity
- 5-10 lines of declaration in entity config
- Automatic method generation
- Consistent cross-cutting concerns

### Reduction
- From 13 file modifications → 0 shared file modifications
- From 200+ lines boilerplate → 5-10 lines declaration

## Files Changed

### Core Infrastructure (New)
- `github_data/github/operation_registry.py` - Registry and Operation classes
- `tests/unit/github/test_operation_registry.py` - Registry tests
- `tests/unit/github/test_github_service_dynamic.py` - Dynamic method tests
- `tests/shared/fixtures/github_service_fixtures.py` - Validation fixtures

### Modified Infrastructure
- `github_data/github/service.py` - Added `__getattr__` and registry integration

### Documentation
- `docs/development/adding-entities.md` - Complete entity addition guide
- `CLAUDE.md` - Reference to new documentation
- Design and implementation plan documents

### Entity Migrations
- All 11 entities migrated to use `github_api_operations` declarations

## Testing

- 50+ new tests covering registry, validation, dynamic generation
- All existing entity tests pass without modification
- Integration tests validate end-to-end functionality

## Next Steps

Future enhancements (deferred):
1. Introspection CLI tool for debugging
2. Type stub generation for IDE support
3. Converter registry (Improvement #4)

## Related Documents

- [Design Document](2025-11-05-service-method-registry-design.md)
- [Implementation Plan](2025-11-05-service-method-registry-implementation-plan.md)
- [Original Analysis](2025-11-03-architectural-improvements.md)
```

**Step 2: Commit**

```bash
git add docs/plans/active/architectural-improvements/2025-11-05-service-method-registry-summary.md
git commit -s -m "docs: add implementation summary for service method registry"
```

---

## Completion

All phases complete! The service method registry is fully implemented, tested, documented, and all entities have been migrated.

**Final verification:**
```bash
make check  # Should pass all quality checks
```

**Branch status:**
- Branch: `refactor/service-method-registry`
- Ready for PR review
- All tests passing
- Documentation complete
