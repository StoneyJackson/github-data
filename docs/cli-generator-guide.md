# Entity Generator Tool

## Overview

The entity generator (`src/tools/generate_entity.py`) is a CLI tool that automates the creation of new data entities for the GitHub Data project. It generates boilerplate code including entity configuration, data models, and save/restore strategies following the project's StrategyContext pattern.

**What it generates:**
- Entity configuration with auto-discovery support
- Data model classes (Pydantic models)
- Save strategy (fetching from GitHub, transforming, and saving to JSON)
- Restore strategy (reading JSON, validating, and restoring to GitHub)
- Package `__init__.py` for exports

**Benefits:**
- Ensures consistency across all entities
- Reduces boilerplate and copy-paste errors
- Enforces project patterns and conventions
- Provides guided prompts for entity requirements
- Supports service dependency declaration

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Usage Modes](#usage-modes)
3. [Entity Configuration](#entity-configuration)
4. [Generated Files](#generated-files)
5. [Implementation Guide](#implementation-guide)
6. [Extending with New Services](#extending-with-new-services)
7. [Testing Your Entity](#testing-your-entity)
8. [Examples](#examples)

---

## Quick Start

**Interactive mode** (recommended for first-time users):
```bash
python -m src.tools.generate_entity
```

The tool will prompt you for all required information:
- Entity name (snake_case, e.g., `comment_reactions`)
- Value type (`bool` for simple enable/disable, `set` for selective IDs)
- Default value (`true` or `false`)
- Dependencies (comma-separated entity names)
- Save services (services needed for save operation)
- Restore services (services needed for restore operation)
- Description (brief description of the entity)

---

## Usage Modes

### 1. Interactive Mode

Run without arguments for guided prompts:

```bash
python -m src.tools.generate_entity
```

**When to use:** First time creating entities, learning the system, or when you're unsure about service requirements.

### 2. Command-Line Arguments Mode

Provide all arguments upfront:

```bash
python -m src.tools.generate_entity \
    --name comment_reactions \
    --type bool \
    --default true \
    --deps issues,comments \
    --save-services github_service \
    --restore-services github_service,conflict_strategy \
    --description "Save and restore comment reactions"
```

**When to use:** Scripting, automation, or when you know all requirements upfront.

### 3. Hybrid Mode

Provide some arguments, get prompted for the rest:

```bash
python -m src.tools.generate_entity --name comment_reactions
```

**When to use:** Quick generation with prompts for complex decisions (like service dependencies).

### Additional Options

**Force overwrite** (use with caution):
```bash
python -m src.tools.generate_entity --name my_entity --force
```

This overwrites existing entity files without confirmation.

---

## Entity Configuration

### Entity Name

**Format:** `snake_case` (lowercase with underscores)

**Rules:**
- Must be lowercase
- Only alphanumeric characters and underscores
- Cannot start or end with underscore
- Example: `comment_reactions`, `issue_labels`, `pr_review_threads`

**Generated from name:**
- Environment variable: `INCLUDE_<UPPER_SNAKE>` (e.g., `INCLUDE_COMMENT_REACTIONS`)
- Class names: `<PascalCase>EntityConfig`, `<PascalCase>SaveStrategy`, `<PascalCase>RestoreStrategy`
- Directory: `src/entities/<snake_case>/`

### Value Type

**Options:**
- `bool` - Simple enable/disable flag
  - Example: `INCLUDE_LABELS=true` enables all labels
- `set` - Selective mode with ID filtering (future feature)
  - Example: `INCLUDE_LABELS=123,456` would enable only labels 123 and 456

**Current recommendation:** Use `bool` for all entities. The `set` type is reserved for future selective filtering features.

### Default Value

**Options:** `true` or `false`

**Guidelines:**
- Use `true` for core features (labels, issues, pull requests)
- Use `false` for optional/expensive features (git repositories, large attachments)

### Dependencies

**Format:** Comma-separated list of entity names (snake_case)

**Purpose:** Declares which entities must be processed before this one.

**Example:**
- `comments` depends on `issues` (comments belong to issues)
- `sub_issues` depends on `issues` (sub-issues reference parent issues)
- `pr_comments` depends on `pull_requests` (PR comments belong to PRs)

**Note:** The entity registry validates and enforces dependency order during operations.

### Service Requirements

Services are external dependencies your entity needs for save/restore operations.

**Available services:**

| Service | Description | When to Use |
|---------|-------------|-------------|
| `github_service` | GitHub API client (GraphQL/REST) | Fetching/creating GitHub resources (issues, PRs, labels) |
| `git_service` | Git repository operations | Cloning/restoring git repositories |
| `conflict_strategy` | Conflict resolution for restore | When restore might encounter conflicts (duplicate names, existing resources) |

**Declaring services:**
- `--save-services`: Services needed for save operation (typically `github_service`)
- `--restore-services`: Services needed for restore operation (typically `github_service,conflict_strategy`)

**Example:**
```bash
--save-services github_service \
--restore-services github_service,conflict_strategy
```

---

## Generated Files

The generator creates this structure:

```
src/entities/<entity_name>/
├── __init__.py                 # Package exports
├── entity_config.py            # Entity configuration and registration
├── models.py                   # Pydantic data models
├── save_strategy.py            # Save operation strategy
└── restore_strategy.py         # Restore operation strategy
```

### `entity_config.py`

Auto-discovered configuration class:

```python
class CommentReactionsEntityConfig:
    name = "comment_reactions"
    env_var = "INCLUDE_COMMENT_REACTIONS"
    default_value = True
    value_type = bool
    dependencies = ["issues", "comments"]
    description = "Save and restore comment reactions"

    required_services_save = ['github_service']
    required_services_restore = ['github_service', 'conflict_strategy']

    @staticmethod
    def create_save_strategy(context):
        # Extract services from context
        return CommentReactionsSaveStrategy(
            github_service=context.github_service,
            data_path=context.data_path,
            entity_config=context.entity_config
        )

    @staticmethod
    def create_restore_strategy(context):
        # Extract services from context
        return CommentReactionsRestoreStrategy(
            github_service=context.github_service,
            conflict_strategy=context.conflict_strategy,
            data_path=context.data_path,
            entity_config=context.entity_config
        )
```

**Key features:**
- Auto-discovered by `EntityRegistry` via naming convention (`*EntityConfig`)
- Factory methods for creating strategy instances with validated services
- Service requirements validated at runtime

### `models.py`

Pydantic models for data validation:

```python
from pydantic import BaseModel

class CommentReactions(BaseModel):
    """Model for comment reaction data."""

    comment_id: int
    reaction_type: str
    user_id: int
    created_at: str
```

**Customize:** Add fields specific to your entity's data structure.

### `save_strategy.py`

Strategy for saving data from GitHub:

```python
class CommentReactionsSaveStrategy(BaseSaveStrategy):
    """Save strategy for comment_reactions."""

    def __init__(self, github_service, data_path, entity_config):
        super().__init__(github_service, data_path, entity_config)

    def execute(self) -> None:
        """Execute save operation.

        TODO: Implement:
        1. Fetch data from GitHub using self.github_service
        2. Transform to model instances
        3. Validate data
        4. Save using self.save_to_json()
        """
        raise NotImplementedError("Implement execute() method")
```

**Your task:** Implement the `execute()` method (see Implementation Guide below).

### `restore_strategy.py`

Strategy for restoring data to GitHub:

```python
class CommentReactionsRestoreStrategy(BaseRestoreStrategy):
    """Restore strategy for comment_reactions."""

    def __init__(self, github_service, conflict_strategy, data_path, entity_config):
        super().__init__(github_service, data_path, entity_config)
        self.conflict_strategy = conflict_strategy

    def execute(self) -> None:
        """Execute restore operation.

        TODO: Implement:
        1. Load data from JSON using self.load_from_json()
        2. Validate data
        3. Check for conflicts
        4. Restore to GitHub using self.github_service
        """
        raise NotImplementedError("Implement execute() method")
```

**Your task:** Implement the `execute()` method (see Implementation Guide below).

---

## Implementation Guide

After generating your entity, follow these steps to complete the implementation:

### Step 1: Define Your Data Model

Edit `src/entities/<entity_name>/models.py`:

```python
from pydantic import BaseModel, Field
from typing import Optional

class CommentReactions(BaseModel):
    """Model for GitHub comment reaction data."""

    # GitHub fields
    comment_id: int = Field(..., description="ID of the comment")
    reaction_type: str = Field(..., description="Type of reaction (+1, -1, laugh, etc.)")
    user_login: str = Field(..., description="Username who reacted")
    created_at: str = Field(..., description="ISO 8601 timestamp")

    # Optional metadata
    node_id: Optional[str] = Field(None, description="GitHub GraphQL node ID")

    class Config:
        # Allow extra fields for forward compatibility
        extra = "allow"
```

**Tips:**
- Use Pydantic field validation for data integrity
- Add descriptions for documentation
- Consider using `Optional` for fields that might not exist
- Use `Config.extra = "allow"` for forward compatibility with GitHub API changes

### Step 2: Implement Save Strategy

Edit `src/entities/<entity_name>/save_strategy.py`:

```python
from typing import List
from .models import CommentReactions

class CommentReactionsSaveStrategy(BaseSaveStrategy):
    """Save strategy for comment reactions."""

    def execute(self) -> None:
        """Save comment reactions from GitHub to JSON."""
        print("Fetching comment reactions...")

        # 1. Fetch data from GitHub
        raw_reactions = self._fetch_reactions()

        # 2. Transform to models
        reactions = self._transform_to_models(raw_reactions)

        # 3. Validate (Pydantic handles this automatically)
        print(f"Found {len(reactions)} reactions")

        # 4. Save to JSON
        self.save_to_json(reactions, "comment_reactions.json")
        print("Comment reactions saved successfully")

    def _fetch_reactions(self) -> List[dict]:
        """Fetch reactions using GitHub service."""
        # Use self.github_service to fetch data
        # Example for GraphQL:
        query = '''
        query($owner: String!, $repo: String!) {
            repository(owner: $owner, name: $repo) {
                issues(first: 100) {
                    nodes {
                        comments(first: 100) {
                            nodes {
                                reactions(first: 100) {
                                    nodes {
                                        id
                                        content
                                        user { login }
                                        createdAt
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        '''

        # Execute query and extract data
        result = self.github_service.execute_graphql_query(query)
        # Extract and flatten reactions from result
        return self._extract_reactions(result)

    def _transform_to_models(self, raw_data: List[dict]) -> List[CommentReactions]:
        """Transform raw GitHub data to models."""
        reactions = []
        for item in raw_data:
            try:
                reaction = CommentReactions(
                    comment_id=item['comment_id'],
                    reaction_type=item['content'],
                    user_login=item['user']['login'],
                    created_at=item['createdAt'],
                    node_id=item['id']
                )
                reactions.append(reaction)
            except Exception as e:
                print(f"Warning: Failed to parse reaction: {e}")
                # Continue processing other reactions

        return reactions
```

**Key methods from `BaseSaveStrategy`:**
- `self.save_to_json(models, filename)` - Save list of Pydantic models to JSON
- `self.github_service` - GitHub API client
- `self.data_path` - Base directory for save files
- `self.entity_config` - Entity configuration

### Step 3: Implement Restore Strategy

Edit `src/entities/<entity_name>/restore_strategy.py`:

```python
from typing import List
from .models import CommentReactions

class CommentReactionsRestoreStrategy(BaseRestoreStrategy):
    """Restore strategy for comment reactions."""

    def execute(self) -> None:
        """Restore comment reactions from JSON to GitHub."""
        print("Loading comment reactions...")

        # 1. Load from JSON
        reactions = self.load_from_json(CommentReactions, "comment_reactions.json")

        if not reactions:
            print("No reactions to restore")
            return

        print(f"Restoring {len(reactions)} reactions...")

        # 2. Check for existing reactions (conflict detection)
        existing_reactions = self._fetch_existing_reactions()

        # 3. Resolve conflicts
        reactions_to_create = self._resolve_conflicts(reactions, existing_reactions)

        # 4. Create reactions in GitHub
        for reaction in reactions_to_create:
            self._create_reaction(reaction)

        print("Comment reactions restored successfully")

    def _fetch_existing_reactions(self) -> List[dict]:
        """Fetch existing reactions from target repository."""
        # Query GitHub for existing reactions
        # Return list of existing reaction data
        pass

    def _resolve_conflicts(
        self,
        reactions: List[CommentReactions],
        existing: List[dict]
    ) -> List[CommentReactions]:
        """Resolve conflicts using conflict strategy."""
        # Use self.conflict_strategy to handle conflicts
        # Example: skip, overwrite, or prompt user
        return [r for r in reactions if not self._reaction_exists(r, existing)]

    def _create_reaction(self, reaction: CommentReactions) -> None:
        """Create a reaction in GitHub."""
        # Use self.github_service to create reaction
        mutation = '''
        mutation($subjectId: ID!, $content: ReactionContent!) {
            addReaction(input: {subjectId: $subjectId, content: $content}) {
                reaction { id }
            }
        }
        '''

        variables = {
            'subjectId': reaction.node_id,
            'content': reaction.reaction_type.upper()
        }

        self.github_service.execute_graphql_mutation(mutation, variables)
```

**Key methods from `BaseRestoreStrategy`:**
- `self.load_from_json(ModelClass, filename)` - Load and parse JSON to Pydantic models
- `self.github_service` - GitHub API client
- `self.conflict_strategy` - Conflict resolution strategy
- `self.data_path` - Base directory for data files
- `self.entity_config` - Entity configuration

### Step 4: Test Your Entity

Create tests in `tests/entities/<entity_name>/`:

```bash
tests/entities/comment_reactions/
├── test_entity_config.py
├── test_save_strategy.py
├── test_restore_strategy.py
└── test_models.py
```

**Example test:**

```python
import pytest
from src.entities.comment_reactions.models import CommentReactions

def test_comment_reactions_model():
    """Test CommentReactions model validation."""
    reaction = CommentReactions(
        comment_id=123,
        reaction_type="THUMBS_UP",
        user_login="octocat",
        created_at="2024-01-01T00:00:00Z"
    )

    assert reaction.comment_id == 123
    assert reaction.reaction_type == "THUMBS_UP"

def test_save_strategy_execute(github_service_mock, tmp_path):
    """Test save strategy execution."""
    # Create mock GitHub service with test data
    # Create save strategy
    # Execute and verify JSON output
    pass
```

Run tests:
```bash
make test-fast  # Fast tests excluding containers
make test       # All tests with coverage
```

### Step 5: Manual Testing

Test the full workflow:

**Save test:**
```bash
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=your_token \
  -e GITHUB_REPO=owner/repo \
  -e INCLUDE_COMMENT_REACTIONS=true \
  -v $(pwd)/test-data:/data \
  github-data:latest
```

**Verify saved data:**
```bash
cat test-data/comment_reactions.json
```

**Restore test:**
```bash
docker run --rm \
  -e OPERATION=restore \
  -e GITHUB_TOKEN=your_token \
  -e GITHUB_REPO=target-owner/target-repo \
  -e INCLUDE_COMMENT_REACTIONS=true \
  -v $(pwd)/test-data:/data \
  github-data:latest
```

---

## Extending with New Services

To add a new service type (beyond `github_service`, `git_service`, `conflict_strategy`):

### Step 1: Update KNOWN_SERVICES

Edit `src/tools/generate_entity.py`:

```python
KNOWN_SERVICES: Dict[str, str] = {
    'github_service': 'GitHub API service for issues, PRs, labels, etc.',
    'git_service': 'Git repository service for cloning/restoring repositories',
    'conflict_strategy': 'Conflict resolution strategy for restoration',
    'notification_service': 'Service for sending notifications',  # NEW
}
```

### Step 2: Update Templates

If your service requires special imports or type hints, update the templates:

**`src/tools/templates/save_strategy_template.py.j2`:**

```jinja2
{% if 'notification_service' in save_services %}
from src.services.notification_service import NotificationService
{% endif %}

class {{ save_strategy_class }}(BaseSaveStrategy):
    def __init__(
        self,
        # ... other services ...
{%- if 'notification_service' in save_services %}
        notification_service: NotificationService,
{%- endif %}
        data_path: Path,
        entity_config: "EntityConfig"
    ):
```

### Step 3: Update StrategyContext

Edit `src/entities/strategy_context.py` to add the new service type:

```python
@dataclass
class StrategyContext:
    """Typed context for entity strategies."""

    entity_config: EntityConfig
    data_path: Path
    github_service: Optional[GitHubService] = None
    git_service: Optional[GitRepositoryService] = None
    conflict_strategy: Optional[ConflictResolutionStrategy] = None
    notification_service: Optional[NotificationService] = None  # NEW

    def validate_services(self, required: List[str]) -> None:
        """Validate all required services are present."""
        for service_name in required:
            if not hasattr(self, service_name):
                raise ValueError(f"Unknown service: {service_name}")
            if getattr(self, service_name) is None:
                raise ValueError(f"Required service not provided: {service_name}")
```

### Step 4: Update Service Provision

Update the code that creates `StrategyContext` instances to provide the new service:

```python
context = StrategyContext(
    entity_config=entity_config,
    data_path=data_path,
    github_service=github_service,
    git_service=git_service,
    conflict_strategy=conflict_strategy,
    notification_service=notification_service,  # NEW
)
```

### Step 5: Regenerate Templates

Regenerate the Jinja2 templates if you modified them:

```bash
python -m src.tools.generate_entity --name test_entity
```

Verify the generated code includes your new service properly.

---

## Testing Your Entity

### Unit Tests

Test individual components in isolation:

```python
# tests/entities/comment_reactions/test_models.py
def test_model_validation():
    """Test Pydantic model validation."""
    reaction = CommentReactions(
        comment_id=123,
        reaction_type="THUMBS_UP",
        user_login="octocat",
        created_at="2024-01-01T00:00:00Z"
    )
    assert reaction.comment_id == 123

# tests/entities/comment_reactions/test_entity_config.py
def test_entity_config():
    """Test entity configuration."""
    config = CommentReactionsEntityConfig()
    assert config.name == "comment_reactions"
    assert config.env_var == "INCLUDE_COMMENT_REACTIONS"
    assert "comments" in config.dependencies
```

### Integration Tests

Test strategy execution with mocked services:

```python
# tests/entities/comment_reactions/test_save_strategy.py
@pytest.mark.integration
def test_save_strategy_integration(github_service_mock, tmp_path):
    """Test save strategy with mocked GitHub service."""
    # Setup mock to return test data
    github_service_mock.execute_graphql_query.return_value = {...}

    # Create strategy
    config = CommentReactionsEntityConfig()
    strategy = CommentReactionsSaveStrategy(
        github_service=github_service_mock,
        data_path=tmp_path,
        entity_config=config
    )

    # Execute
    strategy.execute()

    # Verify JSON file created
    json_file = tmp_path / "comment_reactions.json"
    assert json_file.exists()

    # Verify contents
    data = json.loads(json_file.read_text())
    assert len(data) > 0
```

### Test Commands

```bash
# Fast unit tests (recommended for development)
make test-fast

# All tests including integration
make test

# Run specific test file
pdm run pytest tests/entities/comment_reactions/test_save_strategy.py -v

# Run with coverage
make test-with-test-coverage
```

### Container Tests

Test the full Docker workflow (slow, run less frequently):

```bash
make test-container
```

---

## Examples

### Example 1: Simple Entity (Labels)

**Generate:**
```bash
python -m src.tools.generate_entity \
    --name labels \
    --type bool \
    --default true \
    --deps "" \
    --save-services github_service \
    --restore-services github_service,conflict_strategy \
    --description "Save and restore repository labels"
```

**Implementation focus:**
- Simple GraphQL query for labels
- No complex dependencies
- Direct save/restore without transformations

### Example 2: Dependent Entity (Comments)

**Generate:**
```bash
python -m src.tools.generate_entity \
    --name comments \
    --type bool \
    --default true \
    --deps issues \
    --save-services github_service \
    --restore-services github_service,conflict_strategy \
    --description "Save and restore issue comments"
```

**Implementation focus:**
- Depends on `issues` entity (must process issues first)
- Maps comments to issue IDs
- Handles comment threads and nested replies

### Example 3: Complex Entity (Git Repositories)

**Generate:**
```bash
python -m src.tools.generate_entity \
    --name git_repositories \
    --type bool \
    --default false \
    --deps "" \
    --save-services github_service,git_service \
    --restore-services git_service \
    --description "Clone and restore full git repository history"
```

**Implementation focus:**
- Uses multiple services (`github_service` and `git_service`)
- Expensive operation (default `false`)
- Handles large binary data and git history
- Special restore logic (git operations instead of API calls)

### Example 4: Entity with Selective Mode (Future)

**Generate:**
```bash
python -m src.tools.generate_entity \
    --name pull_requests \
    --type set \
    --default true \
    --deps "" \
    --save-services github_service \
    --restore-services github_service,conflict_strategy \
    --description "Save and restore pull requests"
```

**Implementation notes:**
- `set` type supports selective filtering (e.g., `INCLUDE_PULL_REQUESTS=123,456`)
- Currently, `set` behaves like `bool` (all or nothing)
- Future enhancement: filter by PR numbers in save/restore

---

## Troubleshooting

### Entity Not Discovered

**Symptom:** Entity doesn't appear in operations

**Solution:**
1. Verify class name ends with `EntityConfig` in `entity_config.py`
2. Check entity directory is in `src/entities/`
3. Ensure `entity_config.py` exists and is not empty
4. Check logs for import errors: `logger.error(f"Failed to load entity from {entity_dir.name}: {e}")`

### Service Validation Fails

**Symptom:** `ValueError: Required service not provided: <service_name>`

**Solution:**
1. Verify service is in `KNOWN_SERVICES` dictionary
2. Check `StrategyContext` has the service attribute
3. Ensure service is passed when creating context
4. Verify service names match exactly (case-sensitive)

### Template Rendering Errors

**Symptom:** Generated code has syntax errors or missing imports

**Solution:**
1. Update Jinja2 templates in `src/tools/templates/`
2. Check template variable names match context dictionary
3. Test template rendering with sample data
4. Regenerate entity with `--force` to overwrite

### Dependency Cycle Detected

**Symptom:** `ValueError: Circular dependency detected`

**Solution:**
1. Review entity dependencies in `entity_config.py`
2. Ensure no circular references (A depends on B, B depends on A)
3. Consider refactoring to remove circular dependency
4. Entity registry will auto-detect and report cycles

---

## Best Practices

### Naming Conventions

- **Entity names:** `snake_case`, descriptive, plural (e.g., `pull_requests`, not `pr`)
- **Model classes:** Singular, descriptive (e.g., `PullRequest`, not `PR`)
- **Files:** Follow generated structure, don't rename

### Code Organization

- Keep models simple (data containers only, no business logic)
- Put complex logic in strategy methods, not `execute()`
- Use private methods (`_fetch_data()`) for clarity
- Add docstrings to all public methods

### Error Handling

- Validate data before saving/restoring
- Handle partial failures gracefully (log and continue)
- Provide clear error messages with context
- Use try/except for external API calls

### Performance

- Use GraphQL for efficient data fetching
- Batch API requests when possible
- Cache expensive operations
- Consider pagination for large datasets

### Testing

- Write tests before implementing (TDD)
- Use shared fixtures from `tests/shared/`
- Mock external services (GitHub API, git operations)
- Test edge cases (empty data, conflicts, API errors)

---

## Additional Resources

- **Entity Registry:** `src/entities/registry.py` - Auto-discovery implementation
- **Base Strategies:** `src/operations/save/base_save_strategy.py`, `src/operations/restore/base_restore_strategy.py`
- **StrategyContext:** `src/entities/strategy_context.py` - Service dependency injection
- **Testing Guide:** `docs/testing/README.md` - Comprehensive testing documentation
- **Contributing:** `CONTRIBUTING.md` - Code standards and workflow

---

## Summary

The entity generator automates boilerplate creation for GitHub Data entities:

1. **Generate** entity scaffold with `python -m src.tools.generate_entity`
2. **Define** data models in `models.py`
3. **Implement** save logic in `save_strategy.py`
4. **Implement** restore logic in `restore_strategy.py`
5. **Test** with unit/integration/container tests
6. **Document** entity-specific behavior and caveats

The entity is automatically discovered and integrated into save/restore operations via the entity registry.

For questions or issues, refer to the project documentation or create an issue in the repository.
