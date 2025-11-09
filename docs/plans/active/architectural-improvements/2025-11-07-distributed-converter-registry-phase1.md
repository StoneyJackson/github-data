# Distributed Converter Registry Phase 1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the ConverterRegistry infrastructure with fail-fast validation and backward compatibility, without disrupting existing functionality.

**Architecture:** Create a ConverterRegistry class that eagerly loads converters from entity configs at startup, validates all declarations, and falls back to the monolithic converters.py for backward compatibility during migration. Follows the same pattern as GitHubOperationRegistry.

**Tech Stack:** Python 3, importlib for dynamic loading, difflib for typo suggestions, pytest for testing

---

## Prerequisites

**Files to review:**
- `github_data/github/operation_registry.py` - Parallel registry pattern
- `github_data/entities/registry.py` - Entity discovery mechanism
- `github_data/github/converters.py` - Current monolithic converter file
- Design document: `docs/plans/active/architectural-improvements/2025-11-07-distributed-converter-registry-design.md`

---

## Task 1: Create ConverterRegistry Exception Classes

**Files:**
- Create: `github_data/github/converter_registry.py`

**Step 1: Write failing test for ConverterNotFoundError**

Create test file:

```bash
touch tests/unit/github/test_converter_registry.py
```

```python
# tests/unit/github/test_converter_registry.py
"""Unit tests for ConverterRegistry."""
import pytest


def test_converter_not_found_error_is_exception():
    """ConverterNotFoundError should be an Exception subclass."""
    from github_data.github.converter_registry import ConverterNotFoundError

    error = ConverterNotFoundError("test message")
    assert isinstance(error, Exception)
    assert str(error) == "test message"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/github/test_converter_registry.py::test_converter_not_found_error_is_exception -v`

Expected: `FAIL` with `ModuleNotFoundError: No module named 'github_data.github.converter_registry'`

**Step 3: Create converter_registry.py with exception classes**

```python
# github_data/github/converter_registry.py
"""
Converter Registry for distributed entity converters.

Provides centralized discovery, loading, and validation of converter functions
declared in entity configurations.
"""
import logging

logger = logging.getLogger(__name__)


class ConverterNotFoundError(Exception):
    """Raised when a converter is not found in the registry."""
    pass


class ValidationError(Exception):
    """Raised when converter configuration is invalid."""
    pass
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/github/test_converter_registry.py::test_converter_not_found_error_is_exception -v`

Expected: `PASS`

**Step 5: Add test for ValidationError**

```python
# tests/unit/github/test_converter_registry.py
def test_validation_error_is_exception():
    """ValidationError should be an Exception subclass."""
    from github_data.github.converter_registry import ValidationError

    error = ValidationError("invalid config")
    assert isinstance(error, Exception)
    assert str(error) == "invalid config"
```

**Step 6: Run ValidationError test**

Run: `pytest tests/unit/github/test_converter_registry.py::test_validation_error_is_exception -v`

Expected: `PASS`

**Step 7: Commit exception classes**

```bash
git add github_data/github/converter_registry.py tests/unit/github/test_converter_registry.py
git commit -s -m "feat(converters): add ConverterRegistry exception classes

Add ConverterNotFoundError and ValidationError for converter registry.
Foundation for distributed converter registry pattern.

Related to distributed-converter-registry-design Phase 1.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 2: Create ConverterRegistry Class Structure

**Files:**
- Modify: `github_data/github/converter_registry.py`
- Modify: `tests/unit/github/test_converter_registry.py`

**Step 1: Write failing test for ConverterRegistry instantiation**

```python
# tests/unit/github/test_converter_registry.py
def test_converter_registry_instantiates():
    """ConverterRegistry should instantiate successfully."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    assert registry is not None
    assert hasattr(registry, '_converters')
    assert hasattr(registry, '_converter_metadata')
    assert isinstance(registry._converters, dict)
    assert isinstance(registry._converter_metadata, dict)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/github/test_converter_registry.py::test_converter_registry_instantiates -v`

Expected: `FAIL` with `ImportError: cannot import name 'ConverterRegistry'`

**Step 3: Implement ConverterRegistry class structure**

```python
# github_data/github/converter_registry.py
# Add after exception classes

from typing import Dict, Callable, Any


class ConverterRegistry:
    """
    Registry for entity data converters with eager loading.

    Scans all entity configs at initialization, imports converter modules,
    and validates all declarations. Provides fail-fast startup validation
    to catch configuration errors before any operations run.
    """

    def __init__(self):
        """Initialize registry with eager loading and validation."""
        self._converters: Dict[str, Callable] = {}
        self._converter_metadata: Dict[str, Dict[str, Any]] = {}
        # Eager loading and validation will be implemented in next tasks

        logger.info(
            f"ConverterRegistry initialized with {len(self._converters)} converters"
        )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/github/test_converter_registry.py::test_converter_registry_instantiates -v`

Expected: `PASS`

**Step 5: Commit registry class structure**

```bash
git add github_data/github/converter_registry.py tests/unit/github/test_converter_registry.py
git commit -s -m "feat(converters): add ConverterRegistry class structure

Add ConverterRegistry class with internal storage for converters and
metadata. Eager loading and validation to be implemented next.

Related to distributed-converter-registry-design Phase 1.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 3: Implement get() Method with Helpful Errors

**Files:**
- Modify: `github_data/github/converter_registry.py`
- Modify: `tests/unit/github/test_converter_registry.py`

**Step 1: Write failing test for get() method**

```python
# tests/unit/github/test_converter_registry.py
def test_get_returns_registered_converter():
    """get() should return registered converter function."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    # Manually register a test converter
    def test_converter(data):
        return "converted"

    registry._converters['test_converter'] = test_converter

    result = registry.get('test_converter')
    assert result is test_converter
    assert callable(result)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/github/test_converter_registry.py::test_get_returns_registered_converter -v`

Expected: `FAIL` with `AttributeError: 'ConverterRegistry' object has no attribute 'get'`

**Step 3: Implement get() method**

```python
# github_data/github/converter_registry.py
# Add to ConverterRegistry class

import difflib


class ConverterRegistry:
    # ... existing code ...

    def get(self, name: str) -> Callable:
        """
        Get converter by name.

        Args:
            name: Converter function name (e.g., 'convert_to_release')

        Returns:
            Converter function

        Raises:
            ConverterNotFoundError: If converter not registered
        """
        if name not in self._converters:
            # Provide helpful error with suggestions for typos
            similar = difflib.get_close_matches(name, self._converters.keys())
            msg = f"Converter '{name}' not found"
            if similar:
                msg += f". Did you mean: {', '.join(similar)}?"
            raise ConverterNotFoundError(msg)

        return self._converters[name]
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/github/test_converter_registry.py::test_get_returns_registered_converter -v`

Expected: `PASS`

**Step 5: Write test for not found error**

```python
# tests/unit/github/test_converter_registry.py
def test_get_raises_not_found_for_missing_converter():
    """get() should raise ConverterNotFoundError for unregistered converter."""
    from github_data.github.converter_registry import (
        ConverterRegistry,
        ConverterNotFoundError
    )

    registry = ConverterRegistry()

    with pytest.raises(ConverterNotFoundError) as exc_info:
        registry.get('nonexistent_converter')

    assert "nonexistent_converter" in str(exc_info.value)
    assert "not found" in str(exc_info.value)
```

**Step 6: Run not found test**

Run: `pytest tests/unit/github/test_converter_registry.py::test_get_raises_not_found_for_missing_converter -v`

Expected: `PASS`

**Step 7: Write test for typo suggestions**

```python
# tests/unit/github/test_converter_registry.py
def test_get_suggests_similar_names_for_typos():
    """get() should suggest similar converter names for typos."""
    from github_data.github.converter_registry import (
        ConverterRegistry,
        ConverterNotFoundError
    )

    registry = ConverterRegistry()
    registry._converters['convert_to_label'] = lambda x: x
    registry._converters['convert_to_release'] = lambda x: x

    with pytest.raises(ConverterNotFoundError) as exc_info:
        # Typo: "lable" instead of "label"
        registry.get('convert_to_lable')

    error_msg = str(exc_info.value)
    assert "Did you mean" in error_msg
    assert "convert_to_label" in error_msg
```

**Step 8: Run typo suggestion test**

Run: `pytest tests/unit/github/test_converter_registry.py::test_get_suggests_similar_names_for_typos -v`

Expected: `PASS`

**Step 9: Commit get() method**

```bash
git add github_data/github/converter_registry.py tests/unit/github/test_converter_registry.py
git commit -s -m "feat(converters): implement ConverterRegistry.get() with helpful errors

Add get() method that retrieves converters by name and provides helpful
error messages with typo suggestions using difflib.

Related to distributed-converter-registry-design Phase 1.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 4: Implement list_converters() Method

**Files:**
- Modify: `github_data/github/converter_registry.py`
- Modify: `tests/unit/github/test_converter_registry.py`

**Step 1: Write failing test for list_converters()**

```python
# tests/unit/github/test_converter_registry.py
def test_list_converters_returns_all_names():
    """list_converters() should return all registered converter names."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()
    registry._converters['converter_a'] = lambda x: x
    registry._converters['converter_b'] = lambda x: x
    registry._converters['converter_c'] = lambda x: x

    names = registry.list_converters()

    assert isinstance(names, list)
    assert 'converter_a' in names
    assert 'converter_b' in names
    assert 'converter_c' in names
    assert len(names) == 3
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/github/test_converter_registry.py::test_list_converters_returns_all_names -v`

Expected: `FAIL` with `AttributeError: 'ConverterRegistry' object has no attribute 'list_converters'`

**Step 3: Implement list_converters() method**

```python
# github_data/github/converter_registry.py
# Add to ConverterRegistry class

def list_converters(self) -> list[str]:
    """List all registered converter names."""
    return list(self._converters.keys())
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/github/test_converter_registry.py::test_list_converters_returns_all_names -v`

Expected: `PASS`

**Step 5: Write test for empty registry**

```python
# tests/unit/github/test_converter_registry.py
def test_list_converters_returns_empty_for_new_registry():
    """list_converters() should return empty list for new registry."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    names = registry.list_converters()

    assert isinstance(names, list)
    assert len(names) == 0
```

**Step 6: Run empty test**

Run: `pytest tests/unit/github/test_converter_registry.py::test_list_converters_returns_empty_for_new_registry -v`

Expected: `PASS`

**Step 7: Commit list_converters() method**

```bash
git add github_data/github/converter_registry.py tests/unit/github/test_converter_registry.py
git commit -s -m "feat(converters): implement ConverterRegistry.list_converters()

Add method to list all registered converter names for introspection
and debugging.

Related to distributed-converter-registry-design Phase 1.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 5: Implement _load_legacy_converters() for Backward Compatibility

**Files:**
- Modify: `github_data/github/converter_registry.py`
- Modify: `tests/unit/github/test_converter_registry.py`

**Step 1: Write failing test for legacy converter loading**

```python
# tests/unit/github/test_converter_registry.py
def test_load_legacy_converters_imports_from_converters_module():
    """_load_legacy_converters() should import convert_to_* functions."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()
    registry._load_legacy_converters()

    # Should have loaded some converters from github_data.github.converters
    converters = registry.list_converters()

    # Check for known converters from the monolithic file
    assert 'convert_to_label' in converters
    assert 'convert_to_issue' in converters
    assert 'convert_to_release' in converters
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/github/test_converter_registry.py::test_load_legacy_converters_imports_from_converters_module -v`

Expected: `FAIL` with `AttributeError: 'ConverterRegistry' object has no attribute '_load_legacy_converters'`

**Step 3: Implement _load_legacy_converters() method**

```python
# github_data/github/converter_registry.py
# Add to ConverterRegistry class

def _load_legacy_converters(self):
    """
    Load converters from monolithic converters.py for backward compatibility.

    During migration, this provides fallback for converters not yet moved
    to entity packages. Distributed converters take precedence.
    """
    try:
        from github_data.github import converters as legacy_module

        # Find all convert_to_* functions
        for name in dir(legacy_module):
            if name.startswith('convert_to_') and callable(getattr(legacy_module, name)):
                # Only register if not already loaded from entity package
                if name not in self._converters:
                    self._converters[name] = getattr(legacy_module, name)
                    self._converter_metadata[name] = {
                        'entity': 'legacy',
                        'module': 'github_data.github.converters',
                        'target_model': None,
                    }
                    logger.debug(f"Loaded legacy converter '{name}'")
    except ImportError:
        # converters.py may not exist after complete migration
        logger.debug("No legacy converters module found (this is OK after migration)")
        pass
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/github/test_converter_registry.py::test_load_legacy_converters_imports_from_converters_module -v`

Expected: `PASS`

**Step 5: Write test for distributed overrides legacy**

```python
# tests/unit/github/test_converter_registry.py
def test_distributed_converters_override_legacy():
    """Distributed converters should take precedence over legacy ones."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    # Pre-register a distributed converter
    def distributed_converter(data):
        return "distributed"

    registry._converters['convert_to_test'] = distributed_converter
    registry._converter_metadata['convert_to_test'] = {
        'entity': 'test_entity',
        'module': 'github_data.entities.test.converters',
        'target_model': 'Test',
    }

    # Load legacy converters (which won't override)
    registry._load_legacy_converters()

    # Should still have the distributed version
    result = registry.get('convert_to_test')
    assert result is distributed_converter
    assert registry._converter_metadata['convert_to_test']['entity'] == 'test_entity'
```

**Step 6: Run distributed override test**

Run: `pytest tests/unit/github/test_converter_registry.py::test_distributed_converters_override_legacy -v`

Expected: `PASS`

**Step 7: Write test for graceful missing module handling**

```python
# tests/unit/github/test_converter_registry.py
from unittest.mock import patch


def test_load_legacy_converters_handles_missing_module():
    """_load_legacy_converters() should handle missing converters.py gracefully."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    # Mock ImportError when importing converters module
    with patch('github_data.github.converter_registry.importlib.import_module') as mock_import:
        mock_import.side_effect = ImportError("No module named 'converters'")

        # Should not raise, just log and continue
        registry._load_legacy_converters()

    # Registry should still be usable
    assert isinstance(registry.list_converters(), list)
```

**Step 8: Update implementation to use importlib**

```python
# github_data/github/converter_registry.py
# Update imports at top of file
import importlib

# Update _load_legacy_converters() to use explicit import
def _load_legacy_converters(self):
    """
    Load converters from monolithic converters.py for backward compatibility.

    During migration, this provides fallback for converters not yet moved
    to entity packages. Distributed converters take precedence.
    """
    try:
        legacy_module = importlib.import_module('github_data.github.converters')

        # Find all convert_to_* functions
        for name in dir(legacy_module):
            if name.startswith('convert_to_') and callable(getattr(legacy_module, name)):
                # Only register if not already loaded from entity package
                if name not in self._converters:
                    self._converters[name] = getattr(legacy_module, name)
                    self._converter_metadata[name] = {
                        'entity': 'legacy',
                        'module': 'github_data.github.converters',
                        'target_model': None,
                    }
                    logger.debug(f"Loaded legacy converter '{name}'")
    except ImportError:
        # converters.py may not exist after complete migration
        logger.debug("No legacy converters module found (this is OK after migration)")
        pass
```

**Step 9: Run missing module test**

Run: `pytest tests/unit/github/test_converter_registry.py::test_load_legacy_converters_handles_missing_module -v`

Expected: `PASS`

**Step 10: Commit legacy converter loading**

```bash
git add github_data/github/converter_registry.py tests/unit/github/test_converter_registry.py
git commit -s -m "feat(converters): implement legacy converter loading for backward compatibility

Add _load_legacy_converters() to import converters from monolithic
converters.py during migration. Distributed converters take precedence.
Handles missing module gracefully for post-migration scenario.

Related to distributed-converter-registry-design Phase 1.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 6: Implement _load_converter() for Entity Converters

**Files:**
- Modify: `github_data/github/converter_registry.py`
- Modify: `tests/unit/github/test_converter_registry.py`

**Step 1: Write failing test for _load_converter()**

```python
# tests/unit/github/test_converter_registry.py
def test_load_converter_imports_from_spec():
    """_load_converter() should import converter from module spec."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    spec = {
        'module': 'github_data.entities.labels.converters',
        'function': 'convert_to_label',
        'target_model': 'Label',
    }

    registry._load_converter('convert_to_label', spec, 'labels')

    # Should have loaded the converter
    assert 'convert_to_label' in registry.list_converters()
    converter = registry.get('convert_to_label')
    assert callable(converter)

    # Should have metadata
    metadata = registry._converter_metadata['convert_to_label']
    assert metadata['entity'] == 'labels'
    assert metadata['module'] == 'github_data.entities.labels.converters'
    assert metadata['target_model'] == 'Label'
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/github/test_converter_registry.py::test_load_converter_imports_from_spec -v`

Expected: `FAIL` with `AttributeError: 'ConverterRegistry' object has no attribute '_load_converter'`

**Step 3: Implement _load_converter() method**

```python
# github_data/github/converter_registry.py
# Add to ConverterRegistry class

def _load_converter(self, name: str, spec: Dict[str, Any], entity_name: str):
    """Load a single converter from spec."""
    module_path = spec['module']
    function_name = spec['function']

    try:
        # Eagerly import the module
        module = importlib.import_module(module_path)
        converter_func = getattr(module, function_name)

        # Check for naming collisions
        if name in self._converters:
            existing_meta = self._converter_metadata[name]
            raise ValidationError(
                f"Converter naming collision: '{name}' declared by both "
                f"'{existing_meta['entity']}' and '{entity_name}'"
            )

        # Register converter
        self._converters[name] = converter_func
        self._converter_metadata[name] = {
            'entity': entity_name,
            'module': module_path,
            'target_model': spec.get('target_model'),
        }

        logger.debug(f"Loaded converter '{name}' from {entity_name}")

    except (ImportError, AttributeError) as e:
        raise ValidationError(
            f"Failed to load converter '{name}' from entity '{entity_name}': {e}"
        ) from e
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/github/test_converter_registry.py::test_load_converter_imports_from_spec -v`

Expected: `PASS` (uses actual labels converter from codebase)

**Step 5: Write test for naming collision detection**

```python
# tests/unit/github/test_converter_registry.py
def test_load_converter_detects_naming_collisions():
    """_load_converter() should detect when two entities declare same name."""
    from github_data.github.converter_registry import (
        ConverterRegistry,
        ValidationError
    )

    registry = ConverterRegistry()

    # Load first converter
    spec = {
        'module': 'github_data.entities.labels.converters',
        'function': 'convert_to_label',
        'target_model': 'Label',
    }
    registry._load_converter('convert_to_label', spec, 'labels')

    # Try to load duplicate from different entity
    duplicate_spec = {
        'module': 'github_data.entities.issues.converters',
        'function': 'convert_to_label',  # Different module, same function
        'target_model': 'Label',
    }

    with pytest.raises(ValidationError) as exc_info:
        registry._load_converter('convert_to_label', duplicate_spec, 'issues')

    error_msg = str(exc_info.value)
    assert "naming collision" in error_msg.lower()
    assert "labels" in error_msg
    assert "issues" in error_msg
```

**Step 6: Run collision detection test**

Run: `pytest tests/unit/github/test_converter_registry.py::test_load_converter_detects_naming_collisions -v`

Expected: `PASS`

**Step 7: Write test for import error handling**

```python
# tests/unit/github/test_converter_registry.py
def test_load_converter_raises_validation_error_for_bad_module():
    """_load_converter() should raise ValidationError for missing module."""
    from github_data.github.converter_registry import (
        ConverterRegistry,
        ValidationError
    )

    registry = ConverterRegistry()

    spec = {
        'module': 'nonexistent.module.path',
        'function': 'convert_to_something',
        'target_model': 'Something',
    }

    with pytest.raises(ValidationError) as exc_info:
        registry._load_converter('convert_to_something', spec, 'test_entity')

    error_msg = str(exc_info.value)
    assert "Failed to load converter" in error_msg
    assert "test_entity" in error_msg
```

**Step 8: Run import error test**

Run: `pytest tests/unit/github/test_converter_registry.py::test_load_converter_raises_validation_error_for_bad_module -v`

Expected: `PASS`

**Step 9: Write test for missing function handling**

```python
# tests/unit/github/test_converter_registry.py
def test_load_converter_raises_validation_error_for_bad_function():
    """_load_converter() should raise ValidationError for missing function."""
    from github_data.github.converter_registry import (
        ConverterRegistry,
        ValidationError
    )

    registry = ConverterRegistry()

    spec = {
        'module': 'github_data.entities.labels.converters',  # Module exists
        'function': 'nonexistent_function',  # Function doesn't
        'target_model': 'Something',
    }

    with pytest.raises(ValidationError) as exc_info:
        registry._load_converter('bad_converter', spec, 'test_entity')

    error_msg = str(exc_info.value)
    assert "Failed to load converter" in error_msg
```

**Step 10: Run missing function test**

Run: `pytest tests/unit/github/test_converter_registry.py::test_load_converter_raises_validation_error_for_bad_function -v`

Expected: `PASS`

**Step 11: Commit _load_converter() method**

```bash
git add github_data/github/converter_registry.py tests/unit/github/test_converter_registry.py
git commit -s -m "feat(converters): implement _load_converter() for entity converters

Add method to load individual converters from entity config specs.
Includes naming collision detection and comprehensive error handling
for missing modules or functions.

Related to distributed-converter-registry-design Phase 1.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 7: Implement _load_all_converters() Entity Discovery

**Files:**
- Modify: `github_data/github/converter_registry.py`
- Modify: `tests/unit/github/test_converter_registry.py`

**Step 1: Write failing test for _load_all_converters()**

```python
# tests/unit/github/test_converter_registry.py
def test_load_all_converters_discovers_entity_converters():
    """_load_all_converters() should scan EntityRegistry and load converters."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()
    registry._load_all_converters()

    # Should have loaded converters from entity configs
    converters = registry.list_converters()

    # Check for converters from entities that have converter configs
    # (We'll add these in Phase 2, but legacy ones should load)
    assert len(converters) > 0

    # Should have legacy converters at minimum
    assert any(name.startswith('convert_to_') for name in converters)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/github/test_converter_registry.py::test_load_all_converters_discovers_entity_converters -v`

Expected: `FAIL` with `AttributeError: 'ConverterRegistry' object has no attribute '_load_all_converters'`

**Step 3: Implement _load_all_converters() method**

```python
# github_data/github/converter_registry.py
# Add to ConverterRegistry class

def _load_all_converters(self):
    """Scan EntityRegistry and eagerly import all declared converters."""
    from github_data.entities.registry import EntityRegistry

    entity_registry = EntityRegistry()

    for entity_name, entity in entity_registry._entities.items():
        config = entity.config

        # Skip entities without converter declarations
        if not hasattr(config, "converters"):
            logger.debug(f"Entity '{entity_name}' has no converters declared")
            continue

        # Import and register each converter
        for converter_name, spec in config.converters.items():
            self._load_converter(converter_name, spec, entity_name)

    # Load legacy converters from monolithic file (backward compatibility)
    self._load_legacy_converters()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/github/test_converter_registry.py::test_load_all_converters_discovers_entity_converters -v`

Expected: `PASS`

**Step 5: Write test for entity without converters**

```python
# tests/unit/github/test_converter_registry.py
from unittest.mock import Mock


def test_load_all_converters_skips_entities_without_converters():
    """_load_all_converters() should skip entities with no converter config."""
    from github_data.github.converter_registry import ConverterRegistry
    from github_data.entities.registry import EntityRegistry

    registry = ConverterRegistry()
    entity_registry = EntityRegistry()

    # Count entities without converters
    entities_without_converters = sum(
        1 for entity in entity_registry._entities.values()
        if not hasattr(entity.config, 'converters')
    )

    # Should handle gracefully (no errors)
    registry._load_all_converters()

    # Should still have some converters loaded (legacy ones)
    assert len(registry.list_converters()) > 0
```

**Step 6: Run skip entities test**

Run: `pytest tests/unit/github/test_converter_registry.py::test_load_all_converters_skips_entities_without_converters -v`

Expected: `PASS`

**Step 7: Update __init__ to call _load_all_converters()**

```python
# github_data/github/converter_registry.py
# Update ConverterRegistry.__init__()

def __init__(self):
    """Initialize registry with eager loading and validation."""
    self._converters: Dict[str, Callable] = {}
    self._converter_metadata: Dict[str, Dict[str, Any]] = {}
    self._load_all_converters()  # Eager loading
    # Validation will be added in next task

    logger.info(
        f"ConverterRegistry initialized with {len(self._converters)} converters"
    )
```

**Step 8: Write integration test for initialization**

```python
# tests/unit/github/test_converter_registry.py
def test_registry_initialization_loads_all_converters():
    """Registry should load all converters on instantiation."""
    from github_data.github.converter_registry import ConverterRegistry

    # Simply instantiating should load everything
    registry = ConverterRegistry()

    # Should have loaded legacy converters
    converters = registry.list_converters()
    assert len(converters) > 0

    # Should have common converters from legacy file
    assert 'convert_to_label' in converters
    assert 'convert_to_issue' in converters
    assert 'convert_to_milestone' in converters
```

**Step 9: Run initialization test**

Run: `pytest tests/unit/github/test_converter_registry.py::test_registry_initialization_loads_all_converters -v`

Expected: `PASS`

**Step 10: Commit _load_all_converters() implementation**

```bash
git add github_data/github/converter_registry.py tests/unit/github/test_converter_registry.py
git commit -s -m "feat(converters): implement _load_all_converters() entity discovery

Add method to scan EntityRegistry and load all declared converters.
Integrates with __init__() for eager loading at instantiation.
Gracefully handles entities without converter declarations.

Related to distributed-converter-registry-design Phase 1.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 8: Implement _validate_all() Fail-Fast Validation

**Files:**
- Modify: `github_data/github/converter_registry.py`
- Modify: `tests/unit/github/test_converter_registry.py`

**Step 1: Write failing test for callable validation**

```python
# tests/unit/github/test_converter_registry.py
def test_validate_all_checks_converters_are_callable():
    """_validate_all() should verify all converters are callable."""
    from github_data.github.converter_registry import (
        ConverterRegistry,
        ValidationError
    )

    registry = ConverterRegistry()

    # Add a non-callable "converter"
    registry._converters['bad_converter'] = "not a function"
    registry._converter_metadata['bad_converter'] = {
        'entity': 'test',
        'module': 'test.module',
        'target_model': None,
    }

    with pytest.raises(ValidationError) as exc_info:
        registry._validate_all()

    error_msg = str(exc_info.value)
    assert "not callable" in error_msg.lower()
    assert "bad_converter" in error_msg
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/github/test_converter_registry.py::test_validate_all_checks_converters_are_callable -v`

Expected: `FAIL` with `AttributeError: 'ConverterRegistry' object has no attribute '_validate_all'`

**Step 3: Implement _validate_all() method - Part 1 (callable check)**

```python
# github_data/github/converter_registry.py
# Add to ConverterRegistry class

def _validate_all(self):
    """Comprehensive validation at startup (fail-fast)."""
    # 1. Validate all converters are callable
    for name, func in self._converters.items():
        if not callable(func):
            meta = self._converter_metadata[name]
            raise ValidationError(
                f"Converter '{name}' from entity '{meta['entity']}' is not callable"
            )

    # Cross-validation with operations will be added next
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/github/test_converter_registry.py::test_validate_all_checks_converters_are_callable -v`

Expected: `PASS`

**Step 5: Write test for cross-validation with operations**

```python
# tests/unit/github/test_converter_registry.py
def test_validate_all_checks_operation_converter_references():
    """_validate_all() should verify operations reference valid converters."""
    from github_data.github.converter_registry import (
        ConverterRegistry,
        ValidationError
    )
    from github_data.github.operation_registry import GitHubOperationRegistry

    # First, create a working registry
    registry = ConverterRegistry()

    # Get an operation that references a converter
    op_registry = GitHubOperationRegistry()
    operations = op_registry.list_operations()

    # Find an operation with a converter
    op_with_converter = None
    for op_name in operations:
        op = op_registry.get_operation(op_name)
        if op.converter_name:
            op_with_converter = op
            break

    # If we found an operation with a converter, it should be valid
    if op_with_converter:
        # Should not raise - converter should exist
        registry._validate_all()

        # Now test invalid case - remove the converter
        converter_name = op_with_converter.converter_name
        if converter_name in registry._converters:
            del registry._converters[converter_name]

            with pytest.raises(ValidationError) as exc_info:
                registry._validate_all()

            error_msg = str(exc_info.value)
            assert "references unknown converter" in error_msg.lower()
```

**Step 6: Run cross-validation test**

Run: `pytest tests/unit/github/test_converter_registry.py::test_validate_all_checks_operation_converter_references -v`

Expected: `FAIL` - cross-validation not implemented yet

**Step 7: Implement cross-validation in _validate_all()**

```python
# github_data/github/converter_registry.py
# Update _validate_all() method

def _validate_all(self):
    """Comprehensive validation at startup (fail-fast)."""
    # 1. Validate all converters are callable
    for name, func in self._converters.items():
        if not callable(func):
            meta = self._converter_metadata[name]
            raise ValidationError(
                f"Converter '{name}' from entity '{meta['entity']}' is not callable"
            )

    # 2. Cross-validate: operations reference valid converters
    from github_data.github.operation_registry import GitHubOperationRegistry

    operation_registry = GitHubOperationRegistry()
    for op_name in operation_registry.list_operations():
        operation = operation_registry.get_operation(op_name)
        if operation.converter_name:
            if operation.converter_name not in self._converters:
                raise ValidationError(
                    f"Operation '{op_name}' from entity '{operation.entity_name}' "
                    f"references unknown converter '{operation.converter_name}'"
                )
```

**Step 8: Run cross-validation test again**

Run: `pytest tests/unit/github/test_converter_registry.py::test_validate_all_checks_operation_converter_references -v`

Expected: `PASS`

**Step 9: Update __init__ to call _validate_all()**

```python
# github_data/github/converter_registry.py
# Update ConverterRegistry.__init__()

def __init__(self):
    """Initialize registry with eager loading and validation."""
    self._converters: Dict[str, Callable] = {}
    self._converter_metadata: Dict[str, Dict[str, Any]] = {}
    self._load_all_converters()  # Eager loading
    self._validate_all()          # Fail-fast validation

    logger.info(
        f"ConverterRegistry initialized with {len(self._converters)} converters"
    )
```

**Step 10: Write test for full initialization validation**

```python
# tests/unit/github/test_converter_registry.py
def test_registry_validates_on_initialization():
    """Registry should run full validation on instantiation."""
    from github_data.github.converter_registry import ConverterRegistry

    # Should not raise - all converters and operations should be valid
    registry = ConverterRegistry()

    # Should have converters
    assert len(registry.list_converters()) > 0

    # All should be callable
    for name in registry.list_converters():
        converter = registry.get(name)
        assert callable(converter)
```

**Step 11: Run full initialization test**

Run: `pytest tests/unit/github/test_converter_registry.py::test_registry_validates_on_initialization -v`

Expected: `PASS`

**Step 12: Commit _validate_all() implementation**

```bash
git add github_data/github/converter_registry.py tests/unit/github/test_converter_registry.py
git commit -s -m "feat(converters): implement _validate_all() fail-fast validation

Add comprehensive validation at startup:
- Verifies all converters are callable
- Cross-validates operations reference valid converters
Integrates with __init__() to fail fast on configuration errors.

Related to distributed-converter-registry-design Phase 1.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 9: Implement get_converter() Module-Level Function

**Files:**
- Modify: `github_data/github/converter_registry.py`
- Modify: `tests/unit/github/test_converter_registry.py`

**Step 1: Write failing test for get_converter() function**

```python
# tests/unit/github/test_converter_registry.py
def test_get_converter_function_returns_converter():
    """get_converter() module function should return converter from singleton."""
    from github_data.github.converter_registry import get_converter

    # Should work without explicitly creating registry
    converter = get_converter('convert_to_label')

    assert callable(converter)
    assert converter is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/github/test_converter_registry.py::test_get_converter_function_returns_converter -v`

Expected: `FAIL` with `ImportError: cannot import name 'get_converter'`

**Step 3: Implement get_converter() module function with singleton**

```python
# github_data/github/converter_registry.py
# Add after ConverterRegistry class definition

# Module-level singleton instance
_registry_instance = None


def get_converter(name: str) -> Callable:
    """
    Get converter by name from the global registry.

    This is a convenience function for use within converter implementations
    that need to call other converters.

    Args:
        name: Converter function name

    Returns:
        Converter function
    """
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ConverterRegistry()
    return _registry_instance.get(name)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/github/test_converter_registry.py::test_get_converter_function_returns_converter -v`

Expected: `PASS`

**Step 5: Write test for singleton behavior**

```python
# tests/unit/github/test_converter_registry.py
def test_get_converter_uses_singleton_registry():
    """get_converter() should reuse the same registry instance."""
    from github_data.github import converter_registry

    # Reset singleton for clean test
    converter_registry._registry_instance = None

    # First call creates registry
    converter1 = converter_registry.get_converter('convert_to_label')
    registry1 = converter_registry._registry_instance

    # Second call reuses same registry
    converter2 = converter_registry.get_converter('convert_to_issue')
    registry2 = converter_registry._registry_instance

    # Should be same registry instance
    assert registry1 is registry2

    # Both converters should work
    assert callable(converter1)
    assert callable(converter2)
```

**Step 6: Run singleton test**

Run: `pytest tests/unit/github/test_converter_registry.py::test_get_converter_uses_singleton_registry -v`

Expected: `PASS`

**Step 7: Write test for converter not found**

```python
# tests/unit/github/test_converter_registry.py
def test_get_converter_raises_for_unknown_converter():
    """get_converter() should raise ConverterNotFoundError for invalid name."""
    from github_data.github.converter_registry import (
        get_converter,
        ConverterNotFoundError
    )

    with pytest.raises(ConverterNotFoundError):
        get_converter('nonexistent_converter')
```

**Step 8: Run not found test**

Run: `pytest tests/unit/github/test_converter_registry.py::test_get_converter_raises_for_unknown_converter -v`

Expected: `PASS`

**Step 9: Commit get_converter() function**

```bash
git add github_data/github/converter_registry.py tests/unit/github/test_converter_registry.py
git commit -s -m "feat(converters): add get_converter() module-level function

Add convenience function with singleton pattern for easy converter access
from anywhere in codebase. Enables loose coupling between converters.

Related to distributed-converter-registry-design Phase 1.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 10: Run Full Test Suite and Validate

**Files:**
- All test files

**Step 1: Run all converter registry tests**

Run: `pytest tests/unit/github/test_converter_registry.py -v`

Expected: All tests `PASS`

**Step 2: Run full unit test suite**

Run: `make test-unit`

Expected: All tests `PASS` (no regressions)

**Step 3: Run fast test suite**

Run: `make test-fast`

Expected: All tests `PASS` (no integration regressions)

**Step 4: Check code quality**

Run: `make check`

Expected: No linting, formatting, or type errors

**Step 5: Review test coverage for converter_registry.py**

Run: `pytest tests/unit/github/test_converter_registry.py --cov=github_data.github.converter_registry --cov-report=term-missing`

Expected: Coverage > 90% for new module

**Step 6: Document any remaining work**

Create summary of Phase 1 completion and Phase 2 readiness:

```bash
echo "Phase 1 Complete - Review needed for:
- Test coverage: Check if additional edge cases needed
- Integration: Verify works with existing GitHubService
- Documentation: Update architecture docs
- Phase 2 prep: Ready for entity migration
" > /tmp/phase1_review.txt
cat /tmp/phase1_review.txt
```

**Step 7: Final commit for Phase 1**

```bash
git add tests/unit/github/test_converter_registry.py
git commit -s -m "test(converters): add comprehensive ConverterRegistry test suite

Add full unit test coverage for ConverterRegistry including:
- Exception classes
- Registry initialization and loading
- Converter retrieval with error handling
- Legacy converter backward compatibility
- Entity converter loading from specs
- Fail-fast validation
- Singleton pattern for get_converter()

Phase 1 framework complete and validated.

Related to distributed-converter-registry-design Phase 1.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 11: Create Integration Test File

**Files:**
- Create: `tests/integration/github/test_distributed_converters.py`

**Step 1: Create integration test file structure**

```bash
mkdir -p tests/integration/github
touch tests/integration/github/test_distributed_converters.py
```

**Step 2: Write integration test for end-to-end converter loading**

```python
# tests/integration/github/test_distributed_converters.py
"""Integration tests for distributed converter registry system."""
import pytest


@pytest.mark.integration
def test_converter_registry_integrates_with_existing_system():
    """ConverterRegistry should work with existing converter functions."""
    from github_data.github.converter_registry import ConverterRegistry
    from github_data.entities.labels.models import Label

    registry = ConverterRegistry()

    # Get existing converter
    convert_to_label = registry.get('convert_to_label')

    # Test with realistic data
    raw_label = {
        "id": 123456,
        "name": "bug",
        "color": "d73a4a",
        "description": "Something isn't working",
        "default": True
    }

    label = convert_to_label(raw_label)

    assert isinstance(label, Label)
    assert label.id == 123456
    assert label.name == "bug"
    assert label.color == "d73a4a"


@pytest.mark.integration
def test_all_legacy_converters_load_successfully():
    """All converters from monolithic file should load without errors."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()
    converters = registry.list_converters()

    # Should have multiple converters
    assert len(converters) > 5

    # Check for known converters
    expected_converters = [
        'convert_to_label',
        'convert_to_issue',
        'convert_to_milestone',
        'convert_to_release',
    ]

    for converter_name in expected_converters:
        assert converter_name in converters, f"Missing converter: {converter_name}"

        # Should be callable
        converter = registry.get(converter_name)
        assert callable(converter)


@pytest.mark.integration
def test_operation_registry_compatibility():
    """ConverterRegistry should work seamlessly with GitHubOperationRegistry."""
    from github_data.github.converter_registry import ConverterRegistry
    from github_data.github.operation_registry import GitHubOperationRegistry

    converter_registry = ConverterRegistry()
    operation_registry = GitHubOperationRegistry()

    # Every operation with a converter should reference a valid one
    for op_name in operation_registry.list_operations():
        operation = operation_registry.get_operation(op_name)

        if operation.converter_name:
            # Should not raise ConverterNotFoundError
            converter = converter_registry.get(operation.converter_name)
            assert callable(converter)


@pytest.mark.integration
def test_converter_metadata_is_complete():
    """All converters should have complete metadata."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    for converter_name in registry.list_converters():
        metadata = registry._converter_metadata[converter_name]

        # Should have required fields
        assert 'entity' in metadata
        assert 'module' in metadata
        assert 'target_model' in metadata  # May be None for legacy

        # Should have valid values
        assert isinstance(metadata['entity'], str)
        assert len(metadata['entity']) > 0
        assert isinstance(metadata['module'], str)
        assert len(metadata['module']) > 0
```

**Step 3: Run integration tests**

Run: `pytest tests/integration/github/test_distributed_converters.py -v`

Expected: All tests `PASS`

**Step 4: Commit integration tests**

```bash
git add tests/integration/github/test_distributed_converters.py
git commit -s -m "test(converters): add integration tests for distributed converter system

Add integration tests validating:
- End-to-end converter loading and execution
- All legacy converters load successfully
- Compatibility with GitHubOperationRegistry
- Complete metadata for all converters

Related to distributed-converter-registry-design Phase 1.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 12: Update Documentation

**Files:**
- Create: `docs/architecture/converter-registry.md`
- Modify: `docs/development/adding-entities.md`

**Step 1: Create architecture documentation**

```bash
mkdir -p docs/architecture
touch docs/architecture/converter-registry.md
```

```markdown
# Converter Registry Architecture

## Overview

The Converter Registry provides centralized discovery, loading, and validation of converter functions that transform raw GitHub API data into domain models. It follows the same pattern as the GitHubOperationRegistry for consistency.

## Design Pattern

The registry uses **eager loading** with **fail-fast validation**:

1. **Startup**: All converters imported and validated immediately
2. **Runtime**: Fast lookup with zero import overhead
3. **Errors**: Configuration problems caught before any operations run

## Core Components

### ConverterRegistry Class

Located in `github_data/github/converter_registry.py`.

**Responsibilities:**
- Discover converter declarations from entity configs
- Eagerly import all converter modules at startup
- Validate all converters are callable
- Cross-validate operations reference valid converters
- Provide fast converter lookup by name

**Key Methods:**
- `get(name)`: Retrieve converter by name (raises helpful errors)
- `list_converters()`: List all registered converter names
- Internal loading and validation methods

### Module-Level get_converter() Function

Convenience function using singleton pattern:

```python
from github_data.github.converter_registry import get_converter

def convert_to_issue(raw_data):
    # Use registry for nested conversions
    labels = [get_converter('convert_to_label')(l) for l in raw_data['labels']]
    user = get_converter('convert_to_user')(raw_data['user'])
    ...
```

**Benefits:**
- No direct imports between converters
- Loose coupling
- Easy to mock in tests

## Converter Discovery

### Phase 1: Legacy Converters (Current)

Registry loads from monolithic `github_data/github/converters.py`:
- Finds all `convert_to_*` functions
- Registers as 'legacy' entity
- Provides backward compatibility during migration

### Phase 2+: Distributed Converters (Future)

Entities will declare converters in config:

```python
# github_data/entities/releases/entity_config.py
class ReleasesEntityConfig:
    converters = {
        'convert_to_release': {
            'module': 'github_data.entities.releases.converters',
            'function': 'convert_to_release',
            'target_model': 'Release',
        },
    }
```

Registry will:
1. Scan EntityRegistry
2. Find entities with `converters` dict
3. Import each module and function
4. Register with metadata
5. Fall back to legacy for unmigrated converters

## Validation

### Startup Validation

All validation happens in `__init__()` before registry is ready:

1. **Converter existence**: Module and function must exist
2. **Callable check**: All converters must be callable
3. **Naming collisions**: No duplicate converter names
4. **Cross-validation**: Operations reference valid converters

**Result**: Application won't start with invalid configuration.

### Error Messages

Registry provides helpful errors:

```python
# Typo in converter name
>>> get_converter('convert_to_lable')
ConverterNotFoundError: Converter 'convert_to_lable' not found.
Did you mean: convert_to_label?

# Naming collision
>>> # Two entities declare 'convert_to_duplicate'
ValidationError: Converter naming collision: 'convert_to_duplicate'
declared by both 'entity_a' and 'entity_b'
```

## Usage Patterns

### Using Converters in Service Layer

```python
from github_data.github.converter_registry import get_converter

class GitHubService:
    def get_labels(self, repo):
        raw_data = self.boundary.fetch_labels(repo)
        converter = get_converter('convert_to_label')
        return [converter(item) for item in raw_data]
```

### Converters Calling Other Converters

```python
# github_data/entities/issues/converters.py
from github_data.github.converter_registry import get_converter

def convert_to_issue(raw_data):
    return Issue(
        labels=[get_converter('convert_to_label')(l) for l in raw_data['labels']],
        user=get_converter('convert_to_user')(raw_data['user']),
        milestone=get_converter('convert_to_milestone')(raw_data['milestone']),
    )
```

## Testing

### Unit Tests

Location: `tests/unit/github/test_converter_registry.py`

Tests cover:
- Registry initialization and loading
- Converter retrieval with error handling
- Legacy converter fallback
- Validation logic
- Singleton pattern

### Integration Tests

Location: `tests/integration/github/test_distributed_converters.py`

Tests cover:
- End-to-end converter execution
- Compatibility with GitHubOperationRegistry
- All converters load successfully
- Complete metadata

### Testing Converters

```python
def test_my_converter():
    from github_data.github.converter_registry import get_converter

    converter = get_converter('convert_to_myentity')
    raw_data = {...}

    result = converter(raw_data)

    assert isinstance(result, MyEntity)
```

## Migration Strategy

### Current State (Phase 1 Complete)

- ConverterRegistry infrastructure built
- Loads all converters from legacy `converters.py`
- Full validation and error handling
- Ready for entity migration

### Future Migration (Phase 2+)

Entities will be migrated one at a time:
1. Create `entities/{entity}/converters.py`
2. Add `converters` dict to entity config
3. Move converter functions
4. Test and validate
5. Repeat for next entity

**Backward compatibility**: Registry falls back to legacy file during migration.

## Design Benefits

1. **Zero shared file modifications**: Add entities without touching converters.py
2. **Clear ownership**: Each entity declares its converters
3. **Better organization**: Converters colocated with models
4. **Eliminates circular imports**: Registry provides indirection
5. **Fail-fast validation**: Errors caught at startup
6. **Consistent patterns**: Matches GitHubOperationRegistry
7. **Self-documenting**: Entity configs show all capabilities

## References

- Design: `docs/plans/active/architectural-improvements/2025-11-07-distributed-converter-registry-design.md`
- Implementation: `github_data/github/converter_registry.py`
- Tests: `tests/unit/github/test_converter_registry.py`
- Integration: `tests/integration/github/test_distributed_converters.py`
```

**Step 2: Write architecture doc to file**

Run: `write the architecture doc to docs/architecture/converter-registry.md`

**Step 3: Update entity addition guide**

Read current guide:

Run: `head -100 docs/development/adding-entities.md`

**Step 4: Add converter section to entity guide**

```markdown
# Add this section after existing entity configuration section

## Converter Configuration (Phase 2+)

When Phase 2 of the distributed converter registry is implemented, entities will
declare their converters explicitly in the entity config.

### Declaring Converters

```python
# github_data/entities/myentity/entity_config.py
class MyEntityConfig:
    name = "myentity"

    # Declare all converters this entity provides
    converters = {
        'convert_to_myentity': {
            'module': 'github_data.entities.myentity.converters',
            'function': 'convert_to_myentity',
            'target_model': 'MyEntity',
        },
    }

    # Reference converters in operations
    github_api_operations = {
        "get_repository_myentity": {
            "boundary_method": "get_repository_myentity",
            "converter": "convert_to_myentity",  # Must match declared converter
        },
    }
```

### Creating Converter Module

Create `github_data/entities/myentity/converters.py`:

```python
"""Converters for myentity."""
from typing import Dict, Any
from .models import MyEntity
from github_data.github.converter_registry import get_converter


def convert_to_myentity(raw_data: Dict[str, Any]) -> MyEntity:
    """
    Convert raw GitHub API data to MyEntity model.

    Args:
        raw_data: Raw data from GitHub API

    Returns:
        MyEntity domain model
    """
    # Use registry for nested conversions (loose coupling)
    user = get_converter('convert_to_user')(raw_data['user'])

    return MyEntity(
        id=raw_data["id"],
        user=user,
        # ... other fields
    )
```

**Important**: Always use `get_converter()` for nested conversions rather than
direct imports. This maintains loose coupling and enables testing.

### Converter Testing

Add tests in `tests/unit/entities/myentity/test_converters.py`:

```python
"""Unit tests for myentity converters."""
import pytest


def test_convert_to_myentity():
    """convert_to_myentity should transform raw data correctly."""
    from github_data.github.converter_registry import get_converter
    from github_data.entities.myentity.models import MyEntity

    converter = get_converter('convert_to_myentity')

    raw_data = {
        "id": 123,
        "user": {...},
        # ... test data
    }

    result = converter(raw_data)

    assert isinstance(result, MyEntity)
    assert result.id == 123
```

### Current State (Phase 1)

In Phase 1, the converter registry infrastructure is built but entities have
not yet been migrated. Converters still live in the monolithic
`github_data/github/converters.py` file.

The registry automatically loads all `convert_to_*` functions from that file
for backward compatibility.

**Action Required**: None yet. Continue using existing converters until Phase 2
migration begins.
```

**Step 5: Commit documentation**

```bash
git add docs/architecture/converter-registry.md docs/development/adding-entities.md
git commit -s -m "docs(converters): add converter registry architecture documentation

Add comprehensive architecture documentation for converter registry:
- Design patterns and rationale
- Component descriptions
- Usage patterns
- Testing strategies
- Migration guidance

Update entity addition guide with converter configuration section
for future Phase 2 migration.

Related to distributed-converter-registry-design Phase 1.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 13: Final Validation and Phase 1 Completion

**Files:**
- All project files

**Step 1: Run complete test suite**

Run: `make test`

Expected: All tests `PASS` including source code coverage

**Step 2: Run quality checks**

Run: `make check-all`

Expected: All quality checks `PASS` (linting, formatting, type checking, tests)

**Step 3: Verify no regressions in existing functionality**

Run specific entity tests to ensure nothing broke:

```bash
pytest tests/unit/entities/labels/ -v
pytest tests/unit/entities/issues/ -v
pytest tests/unit/entities/releases/ -v
```

Expected: All existing tests still `PASS`

**Step 4: Test converter registry imports**

Verify the module can be imported and used:

```bash
python -c "
from github_data.github.converter_registry import ConverterRegistry, get_converter
registry = ConverterRegistry()
print(f'Loaded {len(registry.list_converters())} converters')
converter = get_converter('convert_to_label')
print(f'Retrieved converter: {converter.__name__}')
print('✓ All imports and basic usage working')
"
```

Expected: Output showing converters loaded successfully

**Step 5: Review test coverage**

Run: `pytest tests/unit/github/test_converter_registry.py tests/integration/github/test_distributed_converters.py --cov=github_data.github.converter_registry --cov-report=term-missing --cov-report=html`

Expected: Coverage > 90%

Review HTML report in `htmlcov/index.html` for any gaps.

**Step 6: Create Phase 1 completion summary**

```bash
cat > docs/plans/2025-11-07-phase1-completion-summary.md << 'EOF'
# Phase 1 Completion Summary

**Date**: 2025-11-07
**Status**: Complete
**Related**: distributed-converter-registry-design.md

## Completed Tasks

### Infrastructure
- ✅ Created `ConverterRegistry` class with eager loading
- ✅ Implemented backward compatibility with legacy `converters.py`
- ✅ Added `get_converter()` module-level function with singleton pattern
- ✅ Implemented fail-fast validation at startup

### Testing
- ✅ Comprehensive unit tests for all registry functionality
- ✅ Integration tests for system compatibility
- ✅ Test coverage > 90%
- ✅ All existing tests pass (no regressions)

### Documentation
- ✅ Architecture documentation created
- ✅ Entity addition guide updated
- ✅ Code well-commented with docstrings

## Validation Results

**Test Results**:
- Unit tests: PASS
- Integration tests: PASS
- Container tests: PASS
- Code coverage: > 90%

**Quality Checks**:
- Linting (flake8): PASS
- Formatting (black): PASS
- Type checking (mypy): PASS

**Backward Compatibility**:
- All existing converters load successfully
- No changes required to existing code
- GitHubOperationRegistry integration validated

## Phase 1 Success Criteria

- [x] ConverterRegistry infrastructure complete
- [x] Backward compatibility maintained
- [x] Fail-fast validation implemented
- [x] All existing tests pass
- [x] Comprehensive test coverage
- [x] Documentation complete

## Ready for Phase 2

The framework is now ready for incremental entity migration. Phase 2 can begin
with a pilot entity (recommend: labels or releases) to validate the migration
pattern before proceeding with remaining entities.

## Files Created

- `github_data/github/converter_registry.py` - Registry implementation
- `tests/unit/github/test_converter_registry.py` - Unit tests
- `tests/integration/github/test_distributed_converters.py` - Integration tests
- `docs/architecture/converter-registry.md` - Architecture documentation

## Files Modified

- `docs/development/adding-entities.md` - Added converter configuration section

## Next Steps (Phase 2)

1. Choose pilot entity for migration
2. Create entity converter module
3. Add converter declarations to entity config
4. Test and validate
5. Document lessons learned
6. Proceed with remaining entities
EOF
```

**Step 7: Review summary**

Run: `cat docs/plans/2025-11-07-phase1-completion-summary.md`

**Step 8: Final commit**

```bash
git add docs/plans/2025-11-07-phase1-completion-summary.md
git commit -s -m "docs(converters): add Phase 1 completion summary

Phase 1 of distributed converter registry is complete:
- ConverterRegistry infrastructure built and tested
- Backward compatibility with legacy converters.py maintained
- Fail-fast validation at startup implemented
- Comprehensive test coverage and documentation
- All existing tests pass (zero regressions)
- Ready for Phase 2 entity migration

Related to distributed-converter-registry-design Phase 1.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Step 9: Push all changes**

Run: `git log --oneline -13`

Review commits, then:

Run: `git push origin main`

Expected: All commits pushed successfully

---

## Phase 1 Complete!

The Converter Registry infrastructure is now fully implemented, tested, documented, and ready for Phase 2 entity migration.

### What Was Built

1. **ConverterRegistry** class with eager loading and fail-fast validation
2. **Backward compatibility** with existing monolithic converters.py
3. **Module-level get_converter()** function with singleton pattern
4. **Comprehensive test suite** (unit + integration)
5. **Complete documentation** (architecture + entity guide)

### Validation

- ✅ All tests pass (unit, integration, container)
- ✅ Code quality checks pass (lint, format, type)
- ✅ Zero regressions in existing functionality
- ✅ Test coverage > 90%

### Ready for Phase 2

Can now begin migrating entities one at a time to distributed converter pattern.
