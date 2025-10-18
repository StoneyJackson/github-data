# GitHub Milestones Phase 1: Design and Implementation Plan

**Document Type:** Technical Design Document  
**Feature:** GitHub Milestones Support - Phase 1 Core Infrastructure  
**Date:** 2025-10-16  
**Status:** Ready for Implementation  
**Related PRD:** [2025-10-16-20-39-github-milestones-prd.md](./2025-10-16-20-39-github-milestones-prd.md)

## Overview

This document provides the detailed technical design and implementation plan for Phase 1 of GitHub Milestones support, focusing on core infrastructure following the established architectural patterns in the codebase.

## Architecture Analysis Summary

The implementation leverages existing architectural patterns:
- **Entity Models**: Pydantic BaseModel with type annotations and ConfigDict
- **Service Layer**: Protocol-based design with cross-cutting concerns (rate limiting, caching)
- **API Boundary**: Ultra-thin boundary layer delegating to GraphQL/REST clients
- **Storage**: JSON-based with type-safe operations via StorageService protocol
- **Configuration**: Dataclass with enhanced boolean parsing
- **Strategies**: Template method pattern for save/restore operations
- **Testing**: Marker-based organization with shared fixture system

## Phase 1 Deliverables

### 1. Milestone Entity Model
**File:** `src/entities/milestones/models.py`

```python
"""GitHub milestone entity model."""
from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, ConfigDict
from src.entities.users.models import GitHubUser


class Milestone(BaseModel):
    """GitHub milestone entity following established entity patterns."""
    
    id: Union[int, str]
    number: int
    title: str
    description: Optional[str] = None
    state: str  # "open" | "closed"
    creator: GitHubUser
    created_at: datetime
    updated_at: datetime
    due_on: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    open_issues: int = 0
    closed_issues: int = 0
    html_url: str

    model_config = ConfigDict(populate_by_name=True)
```

**File:** `src/entities/milestones/__init__.py`

```python
"""Milestone entity exports."""
from .models import Milestone

__all__ = ["Milestone"]
```

**Update:** `src/entities/__init__.py`

```python
# Add to existing exports
from .milestones import Milestone

__all__ = [
    # ... existing exports
    "Milestone",
]
```

### 2. Configuration Enhancement
**Update:** `src/config/settings.py`

```python
@dataclass
class ApplicationConfig:
    # ... existing fields
    include_milestones: bool

    @classmethod
    def from_environment(cls) -> "ApplicationConfig":
        return cls(
            # ... existing field mappings
            include_milestones=cls._parse_enhanced_bool_env(
                "INCLUDE_MILESTONES", default=True
            ),
        )

    def validate(self) -> None:
        """Enhanced validation with milestone warnings."""
        # ... existing validation logic
        
        # Add milestone-specific validation
        if isinstance(self.include_issues, bool) and not self.include_issues:
            if self.include_milestones:
                logging.warning(
                    "Milestones may have limited utility without issues enabled. "
                    "Consider setting INCLUDE_ISSUES=true for full milestone functionality."
                )
```

### 3. GitHub API Service Integration
**Update:** `src/github/protocols.py`

```python
@abstractmethod
def get_repository_milestones(self, repo_name: str) -> List[Dict[str, Any]]:
    """Get all milestones from the repository.
    
    Args:
        repo_name: The repository name in format 'owner/repo'
        
    Returns:
        List of milestone dictionaries from GitHub API
    """
    pass

@abstractmethod
def create_milestone(
    self, 
    repo_name: str, 
    title: str, 
    description: Optional[str] = None,
    due_on: Optional[str] = None,
    state: str = "open"
) -> Dict[str, Any]:
    """Create a new milestone in the repository.
    
    Args:
        repo_name: The repository name in format 'owner/repo'
        title: Milestone title
        description: Optional milestone description
        due_on: Optional due date in ISO format
        state: Milestone state ("open" or "closed")
        
    Returns:
        Created milestone dictionary from GitHub API
    """
    pass
```

**Update:** `src/github/service.py`

```python
def get_repository_milestones(self, repo_name: str) -> List[Dict[str, Any]]:
    """Get milestones via GraphQL with caching and rate limiting."""
    return self._execute_with_cross_cutting_concerns(
        cache_key=f"milestones:{repo_name}",
        operation=lambda: self._boundary.get_repository_milestones(repo_name),
        repo_name=repo_name,
    )

def create_milestone(
    self, 
    repo_name: str, 
    title: str, 
    description: Optional[str] = None,
    due_on: Optional[str] = None,
    state: str = "open"
) -> Dict[str, Any]:
    """Create milestone via REST API with cache invalidation."""
    result = self._execute_with_cross_cutting_concerns(
        cache_key=None,  # No caching for creation operations
        operation=lambda: self._boundary.create_milestone(
            repo_name, title, description, due_on, state
        ),
        repo_name=repo_name,
    )
    
    # Invalidate relevant caches
    self._cache.invalidate(f"milestones:{repo_name}")
    
    return result
```

### 4. GitHub API Boundary Implementation
**Update:** `src/github/boundary.py`

```python
def get_repository_milestones(self, repo_name: str) -> List[Dict[str, Any]]:
    """Get milestones via GraphQL with pagination."""
    try:
        return self._graphql_client.get_repository_milestones(repo_name)
    except Exception as e:
        logging.error(f"Failed to get milestones for {repo_name}: {e}")
        raise

def create_milestone(
    self, 
    repo_name: str, 
    title: str, 
    description: Optional[str] = None,
    due_on: Optional[str] = None,
    state: str = "open"
) -> Dict[str, Any]:
    """Create milestone via REST API."""
    try:
        return self._rest_client.create_milestone(
            repo_name, title, description, due_on, state
        )
    except Exception as e:
        logging.error(f"Failed to create milestone '{title}' for {repo_name}: {e}")
        raise
```

### 5. GraphQL Query Implementation
**File:** `src/github/queries/milestones.py`

```python
"""GraphQL queries for milestone operations."""

REPOSITORY_MILESTONES_QUERY = """
query getRepositoryMilestones($owner: String!, $name: String!, $after: String) {
  repository(owner: $owner, name: $name) {
    milestones(first: 100, after: $after) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        id
        number
        title
        description
        state
        creator {
          login
          id
          avatarUrl
          htmlUrl
          type
        }
        createdAt
        updatedAt
        dueOn
        closedAt
        issues {
          totalCount
        }
        pullRequests {
          totalCount
        }
        url
      }
    }
  }
}
"""

def build_milestones_query_variables(owner: str, name: str, after: str = None) -> dict:
    """Build variables for milestone GraphQL query."""
    variables = {
        "owner": owner,
        "name": name,
    }
    if after:
        variables["after"] = after
    
    return variables
```

**Update:** `src/github/graphql_client.py`

```python
def get_repository_milestones(self, repo_name: str) -> List[Dict[str, Any]]:
    """Get all repository milestones with pagination."""
    from .queries.milestones import REPOSITORY_MILESTONES_QUERY, build_milestones_query_variables
    
    owner, name = repo_name.split("/", 1)
    milestones = []
    after = None
    
    while True:
        variables = build_milestones_query_variables(owner, name, after)
        response = self.execute_query(REPOSITORY_MILESTONES_QUERY, variables)
        
        milestone_data = response["repository"]["milestones"]
        milestones.extend(milestone_data["nodes"])
        
        if not milestone_data["pageInfo"]["hasNextPage"]:
            break
            
        after = milestone_data["pageInfo"]["endCursor"]
    
    return milestones
```

### 6. REST Client Enhancement
**Update:** `src/github/rest_client.py`

```python
def create_milestone(
    self, 
    repo_name: str, 
    title: str, 
    description: Optional[str] = None,
    due_on: Optional[str] = None,
    state: str = "open"
) -> Dict[str, Any]:
    """Create a milestone using GitHub REST API."""
    url = f"{self.base_url}/repos/{repo_name}/milestones"
    
    payload = {
        "title": title,
        "state": state,
    }
    
    if description:
        payload["description"] = description
    if due_on:
        payload["due_on"] = due_on
    
    response = self._make_request("POST", url, json=payload)
    return response.json()
```

### 7. Data Conversion Functions
**Update:** `src/github/converters.py`

```python
def convert_to_milestone(raw_data: Dict[str, Any]) -> Milestone:
    """Convert raw GitHub API milestone data to Milestone model."""
    # Handle GraphQL vs REST API differences
    issues_count = raw_data.get("issues", {})
    if isinstance(issues_count, dict):
        # GraphQL format
        open_issues = issues_count.get("totalCount", 0)
        closed_issues = 0  # GraphQL doesn't provide this directly
    else:
        # REST API format
        open_issues = raw_data.get("open_issues", 0)
        closed_issues = raw_data.get("closed_issues", 0)
    
    return Milestone(
        id=raw_data["id"],
        number=raw_data["number"],
        title=raw_data["title"],
        description=raw_data.get("description"),
        state=raw_data["state"].lower(),
        creator=convert_to_user(raw_data["creator"]),
        created_at=_parse_datetime(raw_data.get("createdAt") or raw_data.get("created_at")),
        updated_at=_parse_datetime(raw_data.get("updatedAt") or raw_data.get("updated_at")),
        due_on=(_parse_datetime(raw_data.get("dueOn") or raw_data.get("due_on")) 
                if raw_data.get("dueOn") or raw_data.get("due_on") else None),
        closed_at=(_parse_datetime(raw_data.get("closedAt") or raw_data.get("closed_at")) 
                   if raw_data.get("closedAt") or raw_data.get("closed_at") else None),
        open_issues=open_issues,
        closed_issues=closed_issues,
        html_url=raw_data.get("url") or raw_data.get("html_url"),
    )
```

### 8. Milestone Save Strategy
**File:** `src/operations/save/strategies/milestones_strategy.py`

```python
"""Milestone save strategy implementation."""
from typing import Any, Dict, List
from src.operations.save.strategy import SaveEntityStrategy


class MilestonesSaveStrategy(SaveEntityStrategy):
    """Strategy for saving repository milestones."""
    
    def get_entity_name(self) -> str:
        """Return the entity name for file naming and logging."""
        return "milestones"
    
    def get_dependencies(self) -> List[str]:
        """Milestones have no dependencies."""
        return []
    
    def get_converter_name(self) -> str:
        """Return the converter function name."""
        return "convert_to_milestone"
    
    def get_service_method(self) -> str:
        """Return the service method name for data collection."""
        return "get_repository_milestones"
    
    def process_data(self, entities: List[Any], context: Dict[str, Any]) -> List[Any]:
        """Process milestone data - no special processing needed."""
        return entities
    
    def should_skip(self, config) -> bool:
        """Skip milestone operations if disabled in config."""
        return not getattr(config, 'include_milestones', True)
```

### 9. Milestone Restore Strategy
**File:** `src/operations/restore/strategies/milestones_strategy.py`

```python
"""Milestone restore strategy implementation."""
from typing import Any, Dict, List, Optional
from pathlib import Path
from src.operations.restore.strategy import RestoreEntityStrategy
from src.entities.milestones.models import Milestone


class MilestonesRestoreStrategy(RestoreEntityStrategy):
    """Strategy for restoring repository milestones."""
    
    def get_entity_name(self) -> str:
        """Return the entity name for file location and logging."""
        return "milestones"
    
    def get_dependencies(self) -> List[str]:
        """Milestones have no dependencies."""
        return []
    
    def load_data(self, data_path: str, storage_service) -> List[Milestone]:
        """Load milestone data from JSON storage."""
        milestone_file = Path(data_path) / f"{self.get_entity_name()}.json"
        
        if not milestone_file.exists():
            self.logger.info(f"No {self.get_entity_name()} file found at {milestone_file}")
            return []
        
        return storage_service.load_data(milestone_file, Milestone)
    
    def transform_for_creation(self, milestone: Milestone, context: Dict[str, Any]) -> Dict[str, Any]:
        """Transform milestone for creation via API."""
        creation_data = {
            "title": milestone.title,
            "state": milestone.state,
        }
        
        if milestone.description:
            creation_data["description"] = milestone.description
        
        if milestone.due_on:
            creation_data["due_on"] = milestone.due_on.isoformat()
        
        return creation_data
    
    def create_entity(self, entity_data: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create milestone via GitHub API."""
        repo_name = context["repo_name"]
        service = context["service"]
        
        try:
            return service.create_milestone(
                repo_name=repo_name,
                title=entity_data["title"],
                description=entity_data.get("description"),
                due_on=entity_data.get("due_on"),
                state=entity_data["state"]
            )
        except Exception as e:
            if "already exists" in str(e).lower():
                self.logger.warning(f"Milestone '{entity_data['title']}' already exists, skipping")
                return None
            raise
    
    def post_create_actions(self, original: Milestone, created: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Store milestone mapping for use by dependent entities."""
        if created:
            milestone_mapping = context.setdefault("milestone_mapping", {})
            milestone_mapping[original.number] = created["number"]
    
    def should_skip(self, config) -> bool:
        """Skip milestone operations if disabled in config."""
        return not getattr(config, 'include_milestones', True)
```

### 10. Strategy Factory Integration
**Update:** `src/operations/strategy_factory.py`

```python
# Import new strategies
from src.operations.save.strategies.milestones_strategy import MilestonesSaveStrategy
from src.operations.restore.strategies.milestones_strategy import MilestonesRestoreStrategy

class StrategyFactory:
    @staticmethod
    def create_save_strategies(config: ApplicationConfig) -> List[SaveEntityStrategy]:
        """Create save strategies in dependency order."""
        strategies = [LabelsSaveStrategy()]
        
        # Add milestone strategy before issues (dependency order)
        if config.include_milestones:
            strategies.append(MilestonesSaveStrategy())
        
        if config.include_issues:
            strategies.append(IssuesSaveStrategy())
        
        # ... rest of existing logic
        
        return strategies
    
    @staticmethod
    def create_restore_strategies(config: ApplicationConfig) -> List[RestoreEntityStrategy]:
        """Create restore strategies in dependency order."""
        strategies = [LabelsRestoreStrategy()]
        
        # Add milestone strategy before issues (dependency order)
        if config.include_milestones:
            strategies.append(MilestonesRestoreStrategy())
        
        if config.include_issues:
            strategies.append(IssuesRestoreStrategy())
        
        # ... rest of existing logic
        
        return strategies
```

## Implementation Order

### Step 1: Entity and Configuration (30 minutes)
1. Create milestone entity model: `src/entities/milestones/models.py`
2. Update entity exports: `src/entities/milestones/__init__.py` and `src/entities/__init__.py`
3. Update configuration: `src/config/settings.py`

### Step 2: API Client Infrastructure (45 minutes)
1. Add protocol methods: `src/github/protocols.py`
2. Create GraphQL queries: `src/github/queries/milestones.py`
3. Implement GraphQL client method: `src/github/graphql_client.py`
4. Implement REST client method: `src/github/rest_client.py`
5. Update API boundary: `src/github/boundary.py`
6. Update service layer: `src/github/service.py`

### Step 3: Data Conversion (15 minutes)
1. Add milestone converter: `src/github/converters.py`

### Step 4: Save/Restore Strategies (60 minutes)
1. Implement save strategy: `src/operations/save/strategies/milestones_strategy.py`
2. Implement restore strategy: `src/operations/restore/strategies/milestones_strategy.py`
3. Update strategy factory: `src/operations/strategy_factory.py`

### Step 5: Testing Infrastructure (60 minutes)
1. Add milestone marker to `pytest.ini`
2. Create milestone test fixtures using TestDataHelper patterns
3. Add ConfigBuilder milestone methods
4. Unit tests for milestone entity model using modern patterns
5. Unit tests for save/restore strategies with MockBoundaryFactory
6. Integration tests for API operations with protocol validation
7. Configuration tests for `INCLUDE_MILESTONES` with ConfigBuilder
8. Error handling tests using hybrid factory pattern

**Total Estimated Time: 3.5 hours**

## Testing Strategy

Following the comprehensive testing infrastructure outlined in `docs/testing.md`, all milestone tests will use the modern infrastructure pattern with ConfigBuilder, MockBoundaryFactory, and protocol validation.

### Test Organization and Markers

All milestone tests will follow the standardized marker system:

```python
# Base markers for unit tests
pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.milestones]

# Base markers for integration tests  
pytestmark = [pytest.mark.integration, pytest.mark.milestones]

# Additional infrastructure markers where applicable
@pytest.mark.enhanced_fixtures
@pytest.mark.workflow_services  
@pytest.mark.error_simulation
```

### Modern Infrastructure Test Patterns

#### Unit Tests Using Modern Pattern

```python
# tests/unit/entities/test_milestones.py
"""Unit tests for milestone entity model."""

import pytest
from tests.shared.builders.config_builder import ConfigBuilder
from tests.shared.mocks.boundary_factory import MockBoundaryFactory
from tests.shared.mocks.protocol_validation import assert_boundary_mock_complete
from src.entities.milestones.models import Milestone
from src.github.converters import convert_to_milestone

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.milestones]

class TestMilestoneModel:
    """Test milestone entity model."""
    
    def test_milestone_model_creation(self, sample_milestone_data):
        """Test milestone model instantiation and validation."""
        # Arrange
        milestone_data = sample_milestone_data["milestones"][0]
        
        # Act
        milestone = convert_to_milestone(milestone_data)
        
        # Assert
        assert isinstance(milestone, Milestone)
        assert milestone.title == "v1.0 Release"
        assert milestone.state == "open"
        assert milestone.number == 1
        
    def test_milestone_optional_fields(self):
        """Test milestone model with optional fields."""
        # Arrange - minimal milestone data
        minimal_data = {
            "id": 1001,
            "number": 1,
            "title": "Minimal Milestone",
            "state": "open",
            "creator": {
                "login": "testuser",
                "id": 123,
                "avatar_url": "https://example.com/avatar.png",
                "html_url": "https://github.com/testuser",
                "type": "User"
            },
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "html_url": "https://github.com/owner/repo/milestone/1",
        }
        
        # Act
        milestone = convert_to_milestone(minimal_data)
        
        # Assert
        assert milestone.description is None
        assert milestone.due_on is None
        assert milestone.closed_at is None

# tests/unit/operations/save/test_milestones_save_strategy.py
"""Unit tests for milestone save strategy."""

import pytest
from tests.shared.builders.config_builder import ConfigBuilder
from src.operations.save.strategies.milestones_strategy import MilestonesSaveStrategy

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.milestones]

class TestMilestonesSaveStrategy:
    """Test milestone save strategy."""
    
    def test_milestones_save_strategy_dependencies(self):
        """Test milestone save strategy has no dependencies."""
        # Arrange
        strategy = MilestonesSaveStrategy()
        
        # Act
        dependencies = strategy.get_dependencies()
        
        # Assert
        assert dependencies == []
        
    def test_milestones_save_strategy_skip_when_disabled(self):
        """Test milestone save strategy skips when INCLUDE_MILESTONES=false."""
        # Arrange
        config = ConfigBuilder().with_milestones_disabled().build()
        strategy = MilestonesSaveStrategy()
        
        # Act
        should_skip = strategy.should_skip(config)
        
        # Assert
        assert should_skip is True
        
    def test_milestones_save_strategy_enabled_by_default(self):
        """Test milestone save strategy enabled when INCLUDE_MILESTONES=true."""
        # Arrange
        config = ConfigBuilder().with_all_features().build()
        strategy = MilestonesSaveStrategy()
        
        # Act
        should_skip = strategy.should_skip(config)
        
        # Assert
        assert should_skip is False
```

#### Integration Tests Using Modern Pattern

```python
# tests/integration/test_milestones_workflow.py
"""Integration tests for milestone workflows."""

import pytest
from pathlib import Path
from tests.shared.builders.config_builder import ConfigBuilder
from tests.shared.mocks.boundary_factory import MockBoundaryFactory
from tests.shared.mocks.protocol_validation import assert_boundary_mock_complete
from src.operations.save.workflow import SaveWorkflow
from src.operations.restore.workflow import RestoreWorkflow

pytestmark = [pytest.mark.integration, pytest.mark.milestones]

class TestMilestoneWorkflows:
    """Integration tests for milestone save/restore workflows."""
    
    def test_milestone_save_restore_workflow(self, tmp_path, sample_github_data):
        """Test complete milestone save and restore workflow using modern pattern."""
        # ✅ Step 1: Configuration with fluent API (schema-resilient)
        config = (
            ConfigBuilder()
            .with_operation("save")
            .with_data_path(str(tmp_path))
            .with_milestone_features()
            .build()
        )
        
        # ✅ Step 2: Protocol-complete mock with validation
        mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
        assert_boundary_mock_complete(mock_boundary)
        
        # ✅ Step 3: Test save workflow
        save_workflow = SaveWorkflow()
        save_result = save_workflow.execute(config, mock_boundary)
        assert save_result.success
        
        # Verify milestone file was created
        milestone_file = Path(tmp_path) / "milestones.json"
        assert milestone_file.exists()
        
        # ✅ Step 4: Test restore workflow
        restore_config = (
            ConfigBuilder()
            .with_operation("restore")
            .with_data_path(str(tmp_path))
            .with_milestone_features()
            .build()
        )
        
        # Create restore-optimized mock boundary
        restore_mock = MockBoundaryFactory.create_for_restore(success_responses=True)
        assert_boundary_mock_complete(restore_mock)
        
        restore_workflow = RestoreWorkflow()
        restore_result = restore_workflow.execute(restore_config, restore_mock)
        assert restore_result.success
        
        # Verify milestone creation was called
        assert restore_mock.create_milestone.called

    def test_milestone_api_integration(self, sample_github_data):
        """Test milestone operations via GitHub API using modern pattern."""
        # ✅ Configuration with ConfigBuilder
        config = ConfigBuilder().with_milestone_features().build()
        
        # ✅ Protocol-complete mock with custom milestone responses
        mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
        assert_boundary_mock_complete(mock_boundary)
        
        # ✅ Add specific milestone API responses
        mock_boundary.create_milestone.return_value = {
            "id": 2001,
            "number": 10,
            "title": "API Test Milestone",
            "state": "open"
        }
        
        # Test API integration
        from src.github.service import GitHubService
        service = GitHubService(mock_boundary)
        
        result = service.create_milestone(
            "owner/repo", 
            "Test Milestone", 
            "Test Description"
        )
        
        assert result["title"] == "API Test Milestone"
        mock_boundary.create_milestone.assert_called_once()
```

#### Error Testing Using Hybrid Pattern

```python
# tests/integration/test_milestones_error_handling.py
"""Error handling tests for milestone operations."""

import pytest
import requests
from tests.shared.builders.config_builder import ConfigBuilder
from tests.shared.mocks.boundary_factory import MockBoundaryFactory
from tests.shared.mocks.protocol_validation import assert_boundary_mock_complete

pytestmark = [pytest.mark.integration, pytest.mark.milestones, pytest.mark.error_simulation]

class TestMilestoneErrorHandling:
    """Test milestone error handling scenarios."""
    
    def test_milestone_api_failure_handling(self, sample_github_data):
        """Test handling of GitHub API failures with hybrid pattern."""
        # ✅ Step 1: Start with protocol-complete boundary
        mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
        assert_boundary_mock_complete(mock_boundary)
        
        # ✅ Step 2: Add specific error simulation via side_effect
        mock_boundary.create_milestone.side_effect = [
            {"id": 100, "number": 1, "title": "Success", "state": "open"},  # First succeeds
            Exception("API rate limit exceeded"),                           # Second fails
        ]
        
        # ✅ Step 3: Test error handling logic
        config = ConfigBuilder().with_milestone_features().build()
        
        from src.github.service import GitHubService
        service = GitHubService(mock_boundary)
        
        # First call succeeds
        result1 = service.create_milestone("owner/repo", "Test 1")
        assert result1["title"] == "Success"
        
        # Second call fails
        with pytest.raises(Exception, match="API rate limit exceeded"):
            service.create_milestone("owner/repo", "Test 2")
        
        # ✅ Step 4: Verify error state and recovery
        assert mock_boundary.create_milestone.call_count == 2
        
    def test_milestone_network_timeout_handling(self, sample_github_data):
        """Test handling of network timeouts during milestone operations."""
        # ✅ Factory provides protocol completeness
        mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)
        assert_boundary_mock_complete(mock_boundary)
        
        # ✅ Custom timeout simulation
        mock_boundary.get_repository_milestones.side_effect = [
            sample_github_data["milestones"],                      # First succeeds
            requests.exceptions.Timeout("Request timed out"),      # Second times out
        ]
        
        config = ConfigBuilder().with_milestone_features().build()
        
        from src.github.service import GitHubService
        service = GitHubService(mock_boundary)
        
        # First call succeeds
        result1 = service.get_repository_milestones("owner/repo")
        assert len(result1) > 0
        
        # Second call times out
        with pytest.raises(requests.exceptions.Timeout):
            service.get_repository_milestones("owner/repo")
```

### Enhanced Test Fixtures

Following the shared fixture system patterns:

```python
# tests/shared/fixtures/milestones.py
"""Milestone-specific test fixtures following shared patterns."""

import pytest
from tests.shared.helpers import TestDataHelper

@pytest.fixture
def sample_milestone_data():
    """Sample milestone data integrated with existing test data patterns."""
    return {
        "id": 1001,
        "number": 1,
        "title": "v1.0 Release",
        "description": "First major release",
        "state": "open",
        "creator": TestDataHelper.create_test_user(),
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "due_on": "2023-12-31T23:59:59Z",
        "closed_at": None,
        "open_issues": 5,
        "closed_issues": 3,
        "html_url": "https://github.com/owner/repo/milestone/1",
    }

@pytest.fixture  
def milestone_entity(sample_milestone_data):
    """Milestone entity for testing using established converter patterns."""
    from src.github.converters import convert_to_milestone
    return convert_to_milestone(sample_milestone_data)

@pytest.fixture
def milestone_data_builder(github_data_builder):
    """Enhanced data builder for milestone scenarios."""
    return github_data_builder.with_milestones(count=3, with_due_dates=True)
```

### ConfigBuilder Enhancement

Add milestone-specific methods to ConfigBuilder:

```python
# tests/shared/builders/config_builder.py - Add these methods

def with_milestone_features(self):
    """Configure for milestone testing with related features."""
    return (self
            .with_include_milestones(True)
            .with_include_issues(True)  # Issues reference milestones
            .with_include_pull_requests(True))  # PRs reference milestones

def with_milestones_disabled(self):
    """Configure with milestones explicitly disabled."""
    return self.with_include_milestones(False)

def with_include_milestones(self, enabled: bool):
    """Set milestone inclusion flag."""
    self._config_data["include_milestones"] = enabled
    return self
```

### Test Execution Commands

Following the established testing patterns:

```bash
# Milestone-specific testing
make test-by-feature FEATURE=milestones           # All milestone tests
pdm run pytest -m "milestones and unit"          # Milestone unit tests
pdm run pytest -m "milestones and integration"   # Milestone integration tests
pdm run pytest -m "milestones and fast"          # Fast milestone tests

# Combined feature testing
pdm run pytest -m "milestones and github_api"    # Milestone API tests
pdm run pytest -m "milestones and error_simulation"  # Milestone error tests
```

## Quality Assurance

### Pre-commit Checklist
- [ ] All new code follows existing patterns
- [ ] Tests use modern infrastructure (ConfigBuilder + MockBoundaryFactory + protocol validation)
- [ ] Unit tests cover new functionality with proper markers (`@pytest.mark.unit`, `@pytest.mark.fast`, `@pytest.mark.milestones`)
- [ ] Integration tests validate API operations using MockBoundaryFactory.create_auto_configured()
- [ ] Configuration tests use ConfigBuilder patterns instead of manual ApplicationConfig construction
- [ ] Error handling tests use hybrid factory pattern (protocol-complete + custom error simulation)
- [ ] All boundary mocks use factory patterns and include protocol validation
- [ ] Type hints are complete and accurate
- [ ] Error handling follows established patterns
- [ ] Logging uses consistent format and levels
- [ ] Documentation strings follow project conventions
- [ ] Test fixtures follow shared fixture system patterns
- [ ] No manual Mock() creation for boundary objects

### Validation Commands
```bash
# Run milestone-specific tests using established patterns
make test-by-feature FEATURE=milestones      # All milestone tests
pdm run pytest -m "milestones and unit"      # Unit tests with markers
pdm run pytest -m "milestones and fast"      # Fast milestone tests

# Run all quality checks
make check

# Verify configuration handling with ConfigBuilder
python -c "
from tests.shared.builders.config_builder import ConfigBuilder
config = ConfigBuilder().with_milestone_features().build()
print(f'Milestones enabled: {config.include_milestones}')
"

# Verify MockBoundaryFactory protocol completeness
python -c "
from tests.shared.mocks.boundary_factory import MockBoundaryFactory
from tests.shared.mocks.protocol_validation import assert_boundary_mock_complete
mock = MockBoundaryFactory.create_auto_configured({})
assert_boundary_mock_complete(mock)
print('Protocol validation passed')
"
```

## Acceptance Criteria

### Functional Requirements
- [ ] Milestones can be saved to JSON storage via `OPERATION=save`
- [ ] Milestones can be restored from JSON storage via `OPERATION=restore`
- [ ] `INCLUDE_MILESTONES=true` (default) enables milestone operations
- [ ] `INCLUDE_MILESTONES=false` disables milestone operations with no impact on existing functionality
- [ ] API operations respect rate limiting and caching infrastructure
- [ ] Error handling provides meaningful messages and graceful degradation

### Technical Requirements
- [ ] Implementation follows existing architectural patterns exactly
- [ ] All tests use modern infrastructure (ConfigBuilder + MockBoundaryFactory + protocol validation)
- [ ] Tests pass with appropriate markers (`@pytest.mark.milestones`, `@pytest.mark.unit`, `@pytest.mark.fast`)
- [ ] ConfigBuilder includes milestone-specific methods (`with_milestone_features()`, `with_milestones_disabled()`)
- [ ] All boundary mocks use factory patterns with protocol completeness validation
- [ ] Error handling tests use hybrid factory pattern (protocol-complete + custom error simulation)
- [ ] Code quality passes all checks (`make check`)
- [ ] Type checking passes without errors
- [ ] Documentation is complete and accurate
- [ ] Integration with existing strategy factory works correctly
- [ ] Test fixtures follow shared fixture system patterns
- [ ] No manual Mock() creation for boundary objects

### Performance Requirements
- [ ] Milestone operations add minimal overhead to existing workflows
- [ ] GraphQL pagination handles large milestone datasets efficiently
- [ ] Caching reduces redundant API calls
- [ ] Rate limiting prevents API quota issues

## Future Considerations

### Phase 2 Preparation
- Milestone field in Issue and PullRequest entities will be added in Phase 2
- Context mapping (`milestone_mapping`) in restore strategy prepares for relationship restoration
- Service methods support both current and future milestone relationship needs

### Extension Points
- Additional GraphQL fields can be easily added to queries
- REST API client can be extended for milestone updates and deletion
- Strategy pattern allows for different conflict resolution approaches
- Configuration system can accommodate additional milestone-related settings

---

**Document Status:** Ready for Implementation  
**Next Steps:** Begin implementation following the step-by-step order outlined above  
**Estimated Completion:** 3.5 hours of focused development time