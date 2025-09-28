# Phase 2 Implementation Plan: INCLUDE_ISSUE_COMMENTS Feature

**Date:** 2025-09-28  
**Status:** Implementation Plan  
**Author:** Claude Code  
**Related:** [2025-09-28-15-36-design-improvements-for-include-issue-comments.md](2025-09-28-15-36-design-improvements-for-include-issue-comments.md), [2025-09-28-16-00-phase1-implementation-plan.md](2025-09-28-16-00-phase1-implementation-plan.md)

## Overview

This document outlines the detailed implementation plan for Phase 2, which implements the `INCLUDE_ISSUE_COMMENTS` environment variable feature using the configuration foundation established in Phase 1.

## Phase 2 Objectives

Implement the `INCLUDE_ISSUE_COMMENTS` feature to allow users to control whether issue comments are included in backup and restore operations:

1. **Full Configuration Integration** - Update main module to pass configuration to operations
2. **Legacy Parameter Removal** - Remove manual comment strategy registration
3. **Testing Implementation** - Comprehensive tests for the new feature
4. **Documentation Updates** - Update user-facing documentation

**Estimated Effort:** 3-4 hours  
**Development Approach:** Test-Driven Development (TDD)  
**Quality Standards:** Clean Code principles with Step-Down Rule

## Current State Analysis

### Phase 1 Achievements
✅ **Configuration Module**: `ApplicationConfig` class with `include_issue_comments` field  
✅ **Strategy Factory**: Conditional registration of `CommentsSaveStrategy` and `CommentsRestoreStrategy`  
✅ **Configuration Parsing**: Boolean environment variable parsing for `INCLUDE_ISSUE_COMMENTS`  
✅ **Basic Integration**: Save/restore orchestrators use strategy factory  

### Current Limitations
⚠️ **Mixed Approach**: Main module still uses legacy function signatures  
⚠️ **Parameter Passing**: Comments strategy controlled by both config and manual registration  
⚠️ **Testing Gaps**: No end-to-end tests for the environment variable  
⚠️ **Documentation**: Feature not documented for users  

## Detailed Implementation Tasks

### Task 1: Complete Configuration Integration (1-1.5 hours)

#### 1.1 Update Main Module Function Signatures
**File:** `src/main.py`

Current issue: The main module creates a temporary config but still uses legacy parameters:

```python
# Current problematic approach in _perform_save_operation
save_repository_data_with_strategy_pattern(
    github_service,
    storage_service,
    config.github_repo,
    config.data_path,
    include_git_repo=config.include_git_repo,  # Mixed approach
    git_service=git_service,
)
```

**Solution:** Update both save and restore operations to pass configuration:

```python
def _perform_save_operation(config: ApplicationConfig) -> None:
    """Execute save operation to backup GitHub repository data."""
    _print_save_operation_start()
    
    github_service = _create_github_service(config)
    storage_service = _create_storage_service()
    git_service = _create_git_service_if_needed(config)
    
    _execute_save_with_config(
        config, github_service, storage_service, git_service
    )


def _print_save_operation_start() -> None:
    """Print start message for save operation."""
    print("Saving GitHub data...")


def _create_github_service(config: ApplicationConfig):
    """Create GitHub service with token from configuration."""
    from .github import create_github_service
    return create_github_service(config.github_token)


def _create_storage_service():
    """Create JSON storage service."""
    from .storage import create_storage_service
    return create_storage_service("json")


def _create_git_service_if_needed(config: ApplicationConfig):
    """Create git service if git repository backup is enabled."""
    return (
        _create_git_repository_service(config) 
        if config.include_git_repo 
        else None
    )


def _execute_save_with_config(
    config: ApplicationConfig,
    github_service,
    storage_service, 
    git_service
) -> None:
    """Execute save operation using configuration-based approach."""
    from .operations.save import save_repository_data_with_config
    
    save_repository_data_with_config(
        config,
        github_service,
        storage_service,
        config.github_repo,
        config.data_path,
        include_prs=False,  # Future: make configurable
        include_sub_issues=False,  # Future: make configurable
        git_service=git_service,
    )


def _perform_restore_operation(config: ApplicationConfig) -> None:
    """Execute restore operation to restore GitHub repository data."""
    _print_restore_operation_start()
    
    github_service = _create_github_service(config)
    storage_service = _create_storage_service()
    git_service = _create_git_service_if_needed(config)
    
    _execute_restore_with_config(
        config, github_service, storage_service, git_service
    )


def _print_restore_operation_start() -> None:
    """Print start message for restore operation."""
    print("Restoring GitHub data...")


def _execute_restore_with_config(
    config: ApplicationConfig,
    github_service,
    storage_service,
    git_service
) -> None:
    """Execute restore operation using configuration-based approach."""
    from .operations.restore.restore import restore_repository_data_with_config
    
    restore_repository_data_with_config(
        config,
        github_service,
        storage_service,
        config.github_repo,
        config.data_path,
        include_original_metadata=True,
        include_prs=False,  # Future: make configurable
        include_sub_issues=False,  # Future: make configurable
        git_service=git_service,
    )
```

#### 1.2 Create Config-Based Restore Function
**File:** `src/operations/restore/restore.py` (new function)

```python
def restore_repository_data_with_config(
    config: ApplicationConfig,
    github_service: RepositoryService,
    storage_service: StorageService,
    repo_name: str,
    data_path: str,
    include_original_metadata: bool = True,
    include_prs: bool = False,
    include_sub_issues: bool = False,
    git_service: Optional[GitRepositoryService] = None,
    data_types: Optional[List[str]] = None,
) -> None:
    """Restore using strategy pattern approach with configuration."""
    
    from .orchestrator import StrategyBasedRestoreOrchestrator
    
    # Create orchestrator with configuration
    orchestrator = StrategyBasedRestoreOrchestrator(
        config, github_service, storage_service
    )
    
    # Add additional strategies not yet in the factory
    if include_prs:
        from .strategies.pull_requests_strategy import PullRequestsRestoreStrategy
        from .strategies.pr_comments_strategy import PullRequestCommentsRestoreStrategy
        
        orchestrator.register_strategy(PullRequestsRestoreStrategy(include_original_metadata))
        orchestrator.register_strategy(PullRequestCommentsRestoreStrategy(include_original_metadata))
    
    if include_sub_issues:
        from .strategies.sub_issues_strategy import SubIssuesRestoreStrategy
        orchestrator.register_strategy(SubIssuesRestoreStrategy(include_original_metadata))
    
    if config.include_git_repo and git_service:
        from .strategies.git_repository_strategy import GitRepositoryRestoreStrategy
        orchestrator.register_strategy(GitRepositoryRestoreStrategy(git_service))
    
    # Determine entities to restore
    if data_types is None:
        requested_entities = StrategyFactory.get_enabled_entities(config)
        
        # Add additional entities based on parameters (future: make these config-driven)
        if include_prs:
            requested_entities.extend(["pull_requests", "pr_comments"])
        if include_sub_issues:
            requested_entities.append("sub_issues")
        if config.include_git_repo:
            requested_entities.append("git_repository")
    else:
        requested_entities = data_types
    
    # Execute restore with configured entities
    orchestrator.execute_restore(repo_name, data_path, requested_entities)
```

#### 1.3 Update Restore Module Exports
**File:** `src/operations/restore/__init__.py`

```python
"""Restore operations module."""

from .restore import (
    restore_repository_data_with_strategy_pattern,
    restore_repository_data_with_config,  # Add new export
)

__all__ = [
    "restore_repository_data_with_strategy_pattern",
    "restore_repository_data_with_config",
]
```

### Task 2: Remove Legacy Manual Registration (0.5 hours)

#### 2.1 Clean Up Save Operation
**File:** `src/operations/save/save.py`

The current approach has redundant registration. Update to rely fully on strategy factory:

```python
def save_repository_data_with_config(
    config: ApplicationConfig,
    github_service: RepositoryService,
    storage_service: StorageService,
    repo_name: str,
    output_path: str,
    include_prs: bool = True,
    include_sub_issues: bool = True,
    git_service: Optional[GitRepositoryService] = None,
    data_types: Optional[List[str]] = None,
) -> None:
    """Save using strategy pattern approach with configuration."""

    # Create orchestrator with configuration - strategies auto-registered via factory
    from .orchestrator import StrategyBasedSaveOrchestrator

    orchestrator = StrategyBasedSaveOrchestrator(
        config, github_service, storage_service
    )

    # Only register strategies NOT handled by the factory yet
    # NOTE: In future phases, these will also move to the factory
    if include_prs:
        from .strategies.pull_requests_strategy import PullRequestsSaveStrategy
        from .strategies.pr_comments_strategy import PullRequestCommentsSaveStrategy

        orchestrator.register_strategy(PullRequestsSaveStrategy())
        orchestrator.register_strategy(PullRequestCommentsSaveStrategy())

    if include_sub_issues:
        from .strategies.sub_issues_strategy import SubIssuesSaveStrategy
        orchestrator.register_strategy(SubIssuesSaveStrategy())

    if config.include_git_repo and git_service:
        from .strategies.git_repository_strategy import GitRepositoryStrategy
        orchestrator.register_strategy(GitRepositoryStrategy(git_service))

    # Determine entities to save based on configuration
    if data_types is None:
        # Use factory to get config-based entities
        requested_entities = StrategyFactory.get_enabled_entities(config)
        
        # Add entities for strategies not yet in factory (future: move to config)
        if include_prs:
            requested_entities.extend(["pull_requests", "pr_comments"])
        if include_sub_issues:
            requested_entities.append("sub_issues")
        if config.include_git_repo:
            requested_entities.append("git_repository")
    else:
        requested_entities = data_types

    # Execute save with determined entities
    orchestrator.execute_save(repo_name, output_path, requested_entities)
```

#### 2.2 Verify Orchestrator Strategy Registration
**File:** `src/operations/save/orchestrator.py` (verify implementation)

Ensure the orchestrator properly uses the strategy factory in its constructor:

```python
class StrategyBasedSaveOrchestrator:
    def __init__(
        self, 
        config: ApplicationConfig,
        github_service: RepositoryService, 
        file_service: StorageService
    ):
        self._config = config
        self._github_service = github_service
        self._file_service = file_service
        self._strategies = {}
        
        # Auto-register strategies from factory
        factory_strategies = StrategyFactory.create_save_strategies(config)
        for strategy in factory_strategies:
            self.register_strategy(strategy)
```

### Task 3: Comprehensive Testing (1-1.5 hours)

**Testing Approach:** Multi-layered testing strategy with pytest markers

#### 3.1 Environment Variable Integration Tests
**File:** `tests/integration/test_include_issue_comments_feature.py`  
**Markers:** `@pytest.mark.integration`, `@pytest.mark.medium`, `@pytest.mark.include_issue_comments`

```python
import pytest
import os
from unittest.mock import patch, MagicMock
from src.main import main
from src.config.settings import ApplicationConfig
from tests.shared import temp_data_dir, sample_github_data

# Test markers for organization and selective execution
pytestmark = [
    pytest.mark.integration,
    pytest.mark.medium,
    pytest.mark.include_issue_comments
]


class TestIncludeIssueCommentsFeature:
    """Integration tests for INCLUDE_ISSUE_COMMENTS environment variable."""
    
    def test_save_with_comments_enabled_by_default(self, temp_data_dir, mock_github_service):
        """Test that comments are included by default in save operations."""
        env_vars = {
            'OPERATION': 'save',
            'GITHUB_TOKEN': 'test-token',
            'GITHUB_REPO': 'owner/repo',
            'DATA_PATH': str(temp_data_dir),
            # INCLUDE_ISSUE_COMMENTS not set - should default to True
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('src.github.create_github_service', return_value=mock_github_service):
                with patch('src.storage.create_storage_service') as mock_storage:
                    with patch('src.operations.save.save.save_repository_data_with_config') as mock_save:
                        main()
                        
                        # Verify save was called with config that includes comments
                        mock_save.assert_called_once()
                        config = mock_save.call_args[0][0]  # First argument is config
                        assert config.include_issue_comments is True
    
    def test_save_with_comments_explicitly_enabled(self, temp_data_dir, mock_github_service):
        """Test save operation with INCLUDE_ISSUE_COMMENTS=true."""
        env_vars = {
            'OPERATION': 'save',
            'GITHUB_TOKEN': 'test-token',
            'GITHUB_REPO': 'owner/repo',
            'DATA_PATH': str(temp_data_dir),
            'INCLUDE_ISSUE_COMMENTS': 'true',
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('src.github.create_github_service', return_value=mock_github_service):
                with patch('src.storage.create_storage_service'):
                    with patch('src.operations.save.save.save_repository_data_with_config') as mock_save:
                        main()
                        
                        config = mock_save.call_args[0][0]
                        assert config.include_issue_comments is True
    
    def test_save_with_comments_disabled(self, temp_data_dir, mock_github_service):
        """Test save operation with INCLUDE_ISSUE_COMMENTS=false."""
        env_vars = {
            'OPERATION': 'save',
            'GITHUB_TOKEN': 'test-token',
            'GITHUB_REPO': 'owner/repo',
            'DATA_PATH': str(temp_data_dir),
            'INCLUDE_ISSUE_COMMENTS': 'false',
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('src.github.create_github_service', return_value=mock_github_service):
                with patch('src.storage.create_storage_service'):
                    with patch('src.operations.save.save.save_repository_data_with_config') as mock_save:
                        main()
                        
                        config = mock_save.call_args[0][0]
                        assert config.include_issue_comments is False
    
    def test_restore_with_comments_disabled(self, temp_data_dir, mock_github_service):
        """Test restore operation with INCLUDE_ISSUE_COMMENTS=false."""
        env_vars = {
            'OPERATION': 'restore',
            'GITHUB_TOKEN': 'test-token',
            'GITHUB_REPO': 'owner/repo',
            'DATA_PATH': str(temp_data_dir),
            'INCLUDE_ISSUE_COMMENTS': 'false',
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('src.github.create_github_service', return_value=mock_github_service):
                with patch('src.storage.create_storage_service'):
                    with patch('src.operations.restore.restore.restore_repository_data_with_config') as mock_restore:
                        main()
                        
                        config = mock_restore.call_args[0][0]
                        assert config.include_issue_comments is False
    
    def test_boolean_parsing_edge_cases(self):
        """Test various boolean value formats for INCLUDE_ISSUE_COMMENTS."""
        test_cases = [
            ('true', True),
            ('True', True),
            ('TRUE', True),
            ('1', True),
            ('yes', True),
            ('YES', True),
            ('on', True),
            ('ON', True),
            ('false', False),
            ('False', False),
            ('FALSE', False),
            ('0', False),
            ('no', False),
            ('NO', False),
            ('off', False),
            ('OFF', False),
            ('invalid', False),  # Invalid values default to False
            ('', False),  # Empty string defaults to False
        ]
        
        base_env = {
            'OPERATION': 'save',
            'GITHUB_TOKEN': 'test-token',
            'GITHUB_REPO': 'owner/repo',
            'DATA_PATH': '/tmp/test',
        }
        
        for value, expected in test_cases:
            env_vars = {**base_env, 'INCLUDE_ISSUE_COMMENTS': value}
            
            with patch.dict(os.environ, env_vars, clear=True):
                config = ApplicationConfig.from_environment()
                assert config.include_issue_comments == expected, f"Failed for value: '{value}'"


# Use shared fixtures from tests.shared instead of local fixtures
# This follows project convention for fixture reuse
```

#### 3.2 Strategy Factory Integration Tests
**File:** `tests/integration/test_strategy_factory_integration.py`  
**Markers:** `@pytest.mark.integration`, `@pytest.mark.medium`, `@pytest.mark.strategy_factory`

```python
import pytest
from src.operations.strategy_factory import StrategyFactory
from src.operations.save.orchestrator import StrategyBasedSaveOrchestrator
from src.operations.restore.orchestrator import StrategyBasedRestoreOrchestrator
from tests.shared import (
    base_config,
    config_with_comments_disabled,
    mock_github_service,
    mock_storage_service
)

# Test markers for organization and selective execution
pytestmark = [
    pytest.mark.integration,
    pytest.mark.medium,
    pytest.mark.strategy_factory
]


class TestStrategyFactoryIntegration:
    """Test integration between strategy factory and orchestrators."""
    
    def test_save_orchestrator_auto_registers_comments_strategy(
        self, base_config, mock_github_service, mock_storage_service
    ):
        """Test that save orchestrator automatically includes comments strategy when enabled."""
        base_config.include_issue_comments = True
        
        orchestrator = StrategyBasedSaveOrchestrator(
            base_config, mock_github_service, mock_storage_service
        )
        
        # Verify comments strategy is registered
        strategy_names = [type(s).__name__ for s in orchestrator._strategies.values()]
        assert 'CommentsSaveStrategy' in strategy_names
        assert 'LabelsSaveStrategy' in strategy_names
        assert 'IssuesSaveStrategy' in strategy_names
    
    def test_save_orchestrator_excludes_comments_strategy_when_disabled(
        self, config_with_comments_disabled, mock_github_service, mock_storage_service
    ):
        """Test that save orchestrator excludes comments strategy when disabled."""
        orchestrator = StrategyBasedSaveOrchestrator(
            config_with_comments_disabled, mock_github_service, mock_storage_service
        )
        
        # Verify comments strategy is NOT registered
        strategy_names = [type(s).__name__ for s in orchestrator._strategies.values()]
        assert 'CommentsSaveStrategy' not in strategy_names
        assert 'LabelsSaveStrategy' in strategy_names
        assert 'IssuesSaveStrategy' in strategy_names
    
    def test_restore_orchestrator_respects_config(
        self, base_config, mock_github_service, mock_storage_service
    ):
        """Test that restore orchestrator respects configuration."""
        base_config.include_issue_comments = False
        
        orchestrator = StrategyBasedRestoreOrchestrator(
            base_config, mock_github_service, mock_storage_service
        )
        
        strategy_names = [type(s).__name__ for s in orchestrator._strategies.values()]
        assert 'CommentsRestoreStrategy' not in strategy_names
    
    def test_entity_list_matches_registered_strategies(
        self, base_config, mock_github_service, mock_storage_service
    ):
        """Test that entity list from factory matches what orchestrator registers."""
        base_config.include_issue_comments = True
        
        # Get entities from factory
        expected_entities = StrategyFactory.get_enabled_entities(base_config)
        
        # Create orchestrator and get its strategy entities
        orchestrator = StrategyBasedSaveOrchestrator(
            base_config, mock_github_service, mock_storage_service
        )
        
        registered_entities = [strategy.entity_name for strategy in orchestrator._strategies.values()]
        
        # Core entities should match
        for entity in expected_entities:
            assert entity in registered_entities
```

#### 3.3 End-to-End Feature Tests
**File:** `tests/integration/test_comments_feature_end_to_end.py`  
**Markers:** `@pytest.mark.integration`, `@pytest.mark.slow`, `@pytest.mark.end_to_end`

```python
import pytest
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.main import main
from tests.shared import temp_data_dir, sample_github_data

# Test markers for organization and selective execution
pytestmark = [
    pytest.mark.integration,
    pytest.mark.slow,
    pytest.mark.end_to_end,
    pytest.mark.include_issue_comments
]


class TestCommentsFeatureEndToEnd:
    """End-to-end tests for the INCLUDE_ISSUE_COMMENTS feature."""
    
    def test_save_and_restore_cycle_with_comments_enabled(
        self, temp_data_dir, sample_repo_data_with_comments
    ):
        """Test complete save/restore cycle with comments enabled."""
        data_path = Path(temp_data_dir) / "backup"
        data_path.mkdir()
        
        # Mock environment for save operation
        save_env = {
            'OPERATION': 'save',
            'GITHUB_TOKEN': 'test-token',
            'GITHUB_REPO': 'owner/repo',
            'DATA_PATH': str(data_path),
            'INCLUDE_ISSUE_COMMENTS': 'true',
        }
        
        with patch.dict(os.environ, save_env, clear=True):
            with patch('src.github.create_github_service') as mock_github:
                mock_github.return_value = sample_repo_data_with_comments
                
                # Execute save operation
                main()
                
                # Verify comments were saved
                comments_file = data_path / "comments.json"
                assert comments_file.exists()
                
                with open(comments_file) as f:
                    comments_data = json.load(f)
                assert len(comments_data) > 0
        
        # Mock environment for restore operation
        restore_env = {
            'OPERATION': 'restore',
            'GITHUB_TOKEN': 'test-token',
            'GITHUB_REPO': 'owner/repo-new',
            'DATA_PATH': str(data_path),
            'INCLUDE_ISSUE_COMMENTS': 'true',
        }
        
        with patch.dict(os.environ, restore_env, clear=True):
            with patch('src.github.create_github_service') as mock_github:
                mock_restore_service = MagicMock()
                mock_github.return_value = mock_restore_service
                
                # Execute restore operation
                main()
                
                # Verify comments restoration was attempted
                assert mock_restore_service.create_issue_comment.called
    
    def test_save_excludes_comments_when_disabled(
        self, temp_data_dir, sample_repo_data_with_comments
    ):
        """Test that save operation excludes comments when disabled."""
        data_path = Path(temp_data_dir) / "backup"
        data_path.mkdir()
        
        env_vars = {
            'OPERATION': 'save',
            'GITHUB_TOKEN': 'test-token',
            'GITHUB_REPO': 'owner/repo',
            'DATA_PATH': str(data_path),
            'INCLUDE_ISSUE_COMMENTS': 'false',
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('src.github.create_github_service') as mock_github:
                mock_github.return_value = sample_repo_data_with_comments
                
                main()
                
                # Verify comments were NOT saved
                comments_file = data_path / "comments.json"
                assert not comments_file.exists()
                
                # But other files should exist
                issues_file = data_path / "issues.json"
                labels_file = data_path / "labels.json"
                assert issues_file.exists()
                assert labels_file.exists()


@pytest.fixture
def sample_repo_data_with_comments():
    """Mock GitHub service with sample repository data including comments."""
    mock_service = MagicMock()
    
    # Configure mock responses
    mock_service.get_repository_labels.return_value = [
        {"name": "bug", "color": "d73a4a", "description": "Bug reports"}
    ]
    
    mock_service.get_repository_issues.return_value = [
        {
            "number": 1,
            "title": "Test Issue",
            "body": "Test issue body",
            "state": "open",
            "labels": [{"name": "bug"}]
        }
    ]
    
    mock_service.get_issue_comments.return_value = [
        {
            "id": 123,
            "body": "Test comment",
            "user": {"login": "testuser"},
            "created_at": "2023-01-01T00:00:00Z"
        }
    ]
    
    return mock_service
```

### Task 4: Documentation and User Experience (0.5 hours)

#### 4.1 Update Environment Variable Documentation
**File:** `CLAUDE.md` (section update)

Add documentation for the new environment variable:

```markdown
## Environment Variables

The following environment variables control the GitHub Data operations:

### Required Variables
- `OPERATION`: Operation to perform (`save` or `restore`)
- `GITHUB_TOKEN`: Personal access token for GitHub API
- `GITHUB_REPO`: Repository in format `owner/repo`

### Optional Variables
- `DATA_PATH`: Path for data storage (default: `/data`)
- `LABEL_CONFLICT_STRATEGY`: Strategy for label conflicts (default: `fail-if-existing`)
- `INCLUDE_GIT_REPO`: Include git repository backup (default: `true`)
- `INCLUDE_ISSUE_COMMENTS`: Include issue comments in backup/restore (default: `true`)  <!-- NEW -->
- `GIT_AUTH_METHOD`: Git authentication method (default: `token`)

### Boolean Environment Variables

Boolean environment variables accept the following values:
- **True values**: `true`, `True`, `TRUE`, `1`, `yes`, `YES`, `on`, `ON`
- **False values**: `false`, `False`, `FALSE`, `0`, `no`, `NO`, `off`, `OFF`, or any other value

### Examples

```bash
# Save repository data including issue comments (default behavior)
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=your_token \
  -e GITHUB_REPO=owner/repo \
  -e DATA_PATH=/data \
  -v $(pwd)/backup:/data \
  github-data

# Save repository data excluding issue comments
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=your_token \
  -e GITHUB_REPO=owner/repo \
  -e DATA_PATH=/data \
  -e INCLUDE_ISSUE_COMMENTS=false \
  -v $(pwd)/backup:/data \
  github-data

# Restore repository data excluding issue comments
docker run --rm \
  -e OPERATION=restore \
  -e GITHUB_TOKEN=your_token \
  -e GITHUB_REPO=owner/new-repo \
  -e DATA_PATH=/data \
  -e INCLUDE_ISSUE_COMMENTS=false \
  -v $(pwd)/backup:/data \
  github-data
```
```

#### 4.2 Update Main Module Information Output
**File:** `src/main.py` (update `_print_operation_info`)

```python
def _print_operation_info(config: ApplicationConfig) -> None:
    """Print information about the operation being performed."""
    print(f"GitHub Data - {config.operation.capitalize()} operation")
    print(f"Repository: {config.github_repo}")
    print(f"Data path: {config.data_path}")
    
    # Feature status information
    features = []
    if config.include_git_repo:
        features.append("Git repository backup")
    if config.include_issue_comments:
        features.append("Issue comments")
    else:
        print("Issue comments: excluded")
    
    if features:
        print(f"Enabled features: {', '.join(features)}")
```

## Implementation Sequence

**Development Approach:** Test-Driven Development (TDD) with Clean Code principles

### Step 1: TDD Setup and Configuration Integration (Day 1, 1-1.5 hours)
1. **Write failing tests first** for configuration integration
2. Update main module to use config-based functions (following Step-Down Rule)
3. Create `restore_repository_data_with_config` function (small, single responsibility)
4. Update module exports
5. **Verify tests pass** and refactor for clean code

### Step 2: TDD Legacy Code Cleanup (Day 1, 0.5 hours)
1. **Write tests** for strategy registration behavior
2. Remove redundant manual strategy registration
3. Verify orchestrators use strategy factory correctly
4. **Run tests** to ensure no regressions

### Step 3: TDD Comprehensive Testing (Day 2, 1-1.5 hours)
1. **Create failing integration tests** using shared fixtures
2. Implement environment variable integration tests with proper markers
3. Create strategy factory integration tests
4. Create end-to-end feature tests with appropriate performance markers
5. **Verify test coverage** and ensure quality standards

### Step 4: Documentation and Quality (Day 2, 0.5 hours)
1. Update `CLAUDE.md` with environment variable documentation
2. Update operation info output (descriptive function names)
3. Add clear usage examples
4. **Run final quality checks**: `make check-all`

## Testing Strategy

**Testing Philosophy:** Multi-layered testing with TDD approach following project standards

### Test Categories Required

#### Unit Tests (`@pytest.mark.unit`, `@pytest.mark.fast`)
- Configuration parsing edge cases ✅ (from Phase 1)
- Strategy factory conditional logic ✅ (from Phase 1) 
- Boolean environment variable parsing ✅ (from Phase 1)
- **Speed:** < 1 second each, ideal for TDD cycles

#### Integration Tests (`@pytest.mark.integration`, `@pytest.mark.medium`) (NEW)
- Main module configuration integration
- Environment variable end-to-end flow
- Strategy factory and orchestrator integration
- Save/restore operation configuration passing
- **Speed:** 1-10 seconds each, moderate execution time

#### End-to-End Tests (`@pytest.mark.integration`, `@pytest.mark.slow`) (NEW)
- Complete save/restore cycle with comments enabled
- Complete save/restore cycle with comments disabled
- File system verification (comments.json presence/absence)
- Mixed feature scenarios
- **Speed:** 10+ seconds each, comprehensive validation

### Testing Markers

**Feature Markers:**
- `@pytest.mark.include_issue_comments` - All tests related to this feature
- `@pytest.mark.strategy_factory` - Strategy factory integration tests
- `@pytest.mark.end_to_end` - Complete workflow tests

**Performance Markers:**
- `@pytest.mark.fast` - Fast tests for TDD cycles
- `@pytest.mark.medium` - Medium-speed integration tests
- `@pytest.mark.slow` - Comprehensive validation tests

### Test Commands

**Development cycle testing (TDD approach):**
```bash
# Fast feedback during development
make test-fast-only                              # Fast tests only (< 1 second)
make test-by-markers MARKERS="include_issue_comments and fast"  # Fast feature tests

# Feature-specific testing
make test-by-feature FEATURE=include_issue_comments  # All feature tests
make test-by-markers MARKERS="integration and include_issue_comments"  # Integration tests
```

**Integration testing:**
```bash
# Run new integration tests with markers
make test-by-markers MARKERS="integration and include_issue_comments"
make test-by-markers MARKERS="strategy_factory"
make test-by-markers MARKERS="end_to_end and include_issue_comments"
```

**Complete validation:**
```bash
# Run all tests to verify no regressions
make test-fast      # Fast development cycle (excludes container tests)
make test           # All tests including container tests
make check          # Fast quality checks
make check-all      # Complete quality validation
```

## Success Criteria

Phase 2 is complete when:

1. **Environment Variable Works**
   - `INCLUDE_ISSUE_COMMENTS=false` excludes comments from save operations
   - `INCLUDE_ISSUE_COMMENTS=true` includes comments in save operations
   - Default behavior includes comments (backward compatibility)
   - Restore operations respect the same setting

2. **File System Behavior**
   - Comments disabled: no `comments.json` file created during save
   - Comments enabled: `comments.json` file created during save
   - Restore reads configuration and skips comment restoration when disabled

3. **Configuration Integration**
   - Main module passes configuration objects to operations
   - No manual strategy registration for core entities
   - Strategy factory fully controls core strategy registration

4. **Tests Pass**
   - All new integration tests pass
   - All new end-to-end tests pass
   - No regressions in existing functionality
   - Test coverage maintains or improves

5. **User Experience**
   - Clear documentation for the new environment variable
   - Operation output shows feature status
   - Intuitive boolean value parsing

## Risk Mitigation

### Potential Issues
1. **Backward Compatibility** - Ensure default behavior unchanged
2. **Test Coverage** - Comprehensive testing of the new feature
3. **Documentation** - Clear user guidance for the new feature
4. **Performance** - No performance impact from configuration changes

### Mitigation Strategies
1. **Default True**: `INCLUDE_ISSUE_COMMENTS` defaults to `true` for backward compatibility
2. **Comprehensive Test Suite**: Integration and end-to-end tests cover all scenarios
3. **Clear Examples**: Documentation includes practical usage examples
4. **Performance Testing**: Verify no performance regression in benchmarks

## Future Considerations

### Ready for Phase 3
After Phase 2 completion, the following will be possible:

1. **Similar Features**: Easy to add `INCLUDE_PR_COMMENTS`, `INCLUDE_SUB_ISSUES`, etc.
2. **Enhanced Orchestrators**: Move PR and sub-issue strategies to factory
3. **Metadata Tracking**: Track which features were used in save operations
4. **Advanced Configuration**: Multi-repository configurations and profiles

### Technical Debt Addressed
- ✅ Removes mixed parameter/configuration approach
- ✅ Eliminates manual strategy registration for core entities
- ✅ Establishes pattern for future configuration-driven features
- ✅ Provides comprehensive test coverage for configuration scenarios

## Dependencies

### External Dependencies
- No new external dependencies required
- Uses existing pytest framework for new tests

### Internal Dependencies
- ✅ Phase 1 configuration module (`ApplicationConfig`)
- ✅ Phase 1 strategy factory (`StrategyFactory`)
- ✅ Existing save/restore orchestrators
- ✅ Existing comment strategies

## Rollback Plan

If issues arise during implementation:

1. **Configuration Issues**: Revert main module to use legacy function signatures temporarily
2. **Strategy Issues**: Revert to manual strategy registration while debugging factory
3. **Test Failures**: Address specific test failures without rolling back entire feature
4. **Performance Issues**: Profile and optimize configuration parsing if needed

The modular approach allows for partial rollbacks without affecting the overall system architecture.

## Validation Checklist

Before considering Phase 2 complete:

**Feature Functionality:**
- [ ] Environment variable `INCLUDE_ISSUE_COMMENTS=false` prevents comment file creation
- [ ] Environment variable `INCLUDE_ISSUE_COMMENTS=true` enables comment file creation  
- [ ] Default behavior (no env var set) includes comments (backward compatibility)
- [ ] Restore operations respect the configuration setting

**Testing and Quality:**
- [ ] All existing tests continue to pass: `make test`
- [ ] New tests use shared fixtures and proper markers
- [ ] Fast tests support TDD development: `make test-fast-only`
- [ ] Integration tests cover feature thoroughly: `make test-by-feature FEATURE=include_issue_comments`
- [ ] End-to-end tests verify complete workflows
- [ ] Test coverage maintains or improves overall percentage

**Code Quality:**
- [ ] Functions follow Clean Code principles (Step-Down Rule, single responsibility)
- [ ] Function names are descriptive and intention-revealing
- [ ] No performance regression measured
- [ ] `make check` passes all quality checks (format, lint, type-check, test-fast)
- [ ] `make check-all` passes including container tests

**Documentation and UX:**
- [ ] Documentation is updated with clear examples
- [ ] Operation output shows feature status clearly
- [ ] Examples follow project conventions

## Next Steps

After Phase 2 completion:

1. **Phase 3**: Enhanced orchestrators and metadata tracking
2. **Future Features**: `INCLUDE_PR_COMMENTS`, `INCLUDE_SUB_ISSUES`, `INCLUDE_PRS`
3. **Configuration Profiles**: Support for multiple repository configurations
4. **Advanced Filtering**: Fine-grained control over what data is saved/restored