# Repository Creation Control Design

**Date**: 2025-11-22
**Status**: Approved
**Feature**: Control repository creation behavior during restore operations

## Overview

Add user control over what happens when the target repository doesn't exist during a restore operation. Users can choose to automatically create the repository (default) or fail with an error message.

## Motivation

Currently, the GitHub Data restore operation assumes the target repository exists. There's no explicit check or creation logic. This design adds:

1. **Explicit control**: Users decide whether missing repositories should be created or cause failure
2. **Repository visibility**: When creating repositories, users control whether they're public or private
3. **Fail-fast behavior**: Repository existence is checked before any entity restoration begins
4. **Future-ready**: Provides foundation for repository configuration preservation

## Design Principles

- **Fail fast**: Check repository existence at startup, before consuming API rate limit on entities
- **Restore-only**: These parameters only apply to restore operations, not save operations
- **Simple defaults**: Default behavior creates public repositories (most common use case)
- **Consistent patterns**: Reuse existing environment variable loading patterns from `main.py`
- **Clean separation**: Repository management separate from entity restoration logic

## Environment Variables

### CREATE_REPOSITORY_IF_MISSING

**Scope**: Restore operation only
**Type**: Boolean
**Default**: `true`
**Valid Values**: `true`, `false`, `yes`, `no`, `on`, `off`, `1`, `0` (case-insensitive)

**Behavior**:
- `true`: Automatically create repository if it doesn't exist
- `false`: Fail with clear error message if repository doesn't exist

**Usage Example**:
```bash
docker run --rm \
  -e OPERATION=restore \
  -e GITHUB_TOKEN=token \
  -e GITHUB_REPO=owner/repo \
  -e CREATE_REPOSITORY_IF_MISSING=false \
  -v $(pwd)/data:/data \
  github-data:latest
```

### REPOSITORY_VISIBILITY

**Scope**: Restore operation only (when CREATE_REPOSITORY_IF_MISSING=true)
**Type**: String (enum)
**Default**: `public`
**Valid Values**: `public`, `private` (case-insensitive)

**Behavior**:
- `public`: Create repository with public visibility
- `private`: Create repository with private visibility

**Usage Example**:
```bash
docker run --rm \
  -e OPERATION=restore \
  -e GITHUB_TOKEN=token \
  -e GITHUB_REPO=owner/repo \
  -e CREATE_REPOSITORY_IF_MISSING=true \
  -e REPOSITORY_VISIBILITY=private \
  -v $(pwd)/data:/data \
  github-data:latest
```

## Architecture

### Component Changes

```
┌─────────────────────────────────────────────────────────────┐
│ Main Entry Point (main.py)                                  │
├─────────────────────────────────────────────────────────────┤
│ 1. Load environment variables (including new params)        │
│ 2. Build services (GitHub, Storage, Git)                    │
│ 3. [NEW] Ensure repository exists (_ensure_repository_exists)│
│ 4. Build orchestrator                                        │
│ 5. Execute operation                                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ GitHub Service Layer (github/service.py)                    │
├─────────────────────────────────────────────────────────────┤
│ [NEW] create_repository(repo_name, private, description)    │
│ [NEW] get_repository_metadata(repo_name) → Dict or None     │
│                                                              │
│ - Wraps boundary with rate limiting, retry logic            │
│ - Returns None if repository not found (404)                │
│ - Raises exceptions for other errors                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ GitHub Boundary Layer (github/boundary.py)                  │
├─────────────────────────────────────────────────────────────┤
│ [NEW] create_repository(repo_name, private, description)    │
│ [NEW] get_repository_metadata(repo_name) → Dict             │
│                                                              │
│ - Ultra-thin PyGithub wrapper                               │
│ - Returns raw JSON data                                     │
│ - Handles user vs organization repository creation          │
└─────────────────────────────────────────────────────────────┘
```

### Execution Flow (Restore Operation)

```
┌─────────────────────────────────────────────────────────────┐
│ Start Restore Operation                                     │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ Load Environment Variables                                  │
│ - OPERATION=restore                                         │
│ - GITHUB_TOKEN, GITHUB_REPO, DATA_PATH                      │
│ - CREATE_REPOSITORY_IF_MISSING (restore only)               │
│ - REPOSITORY_VISIBILITY (restore only)                      │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ Build Services                                              │
│ - GitHub Service, Storage Service, Git Service             │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ [NEW] _ensure_repository_exists()                           │
├─────────────────────────────────────────────────────────────┤
│ 1. Check: Does repository exist?                            │
│    └─ Call: github_service.get_repository_metadata()        │
│                                                              │
│ 2. If exists: Continue                                      │
│                                                              │
│ 3. If not exists + CREATE_REPOSITORY_IF_MISSING=false:      │
│    └─ FAIL with error message                               │
│                                                              │
│ 4. If not exists + CREATE_REPOSITORY_IF_MISSING=true:       │
│    └─ Create repository with specified visibility           │
│    └─ Print confirmation message                            │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ Build Orchestrator & Execute                                │
│ - Repository guaranteed to exist at this point              │
│ - Proceed with normal entity restoration                    │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Details

### 1. GitHub API Boundary Layer

**File**: `github_data/github/boundary.py`

Add two new methods to `GitHubApiBoundary` class:

```python
def get_repository_metadata(self, repo_name: str) -> Dict[str, Any]:
    """Get repository metadata.

    Args:
        repo_name: Repository name in format "owner/repo"

    Returns:
        Raw JSON dictionary of repository metadata

    Raises:
        UnknownObjectException: If repository not found (404)
        GithubException: For other API errors
    """
    repo = self._github.get_repo(repo_name)
    return repo.raw_data

def create_repository(
    self,
    repo_name: str,
    private: bool = False,
    description: str = ""
) -> Dict[str, Any]:
    """Create a new repository.

    Args:
        repo_name: Repository name in format "owner/repo"
        private: Whether repository should be private
        description: Repository description

    Returns:
        Raw JSON dictionary of created repository

    Raises:
        GithubException: If repository creation fails
    """
    owner, repo = repo_name.split('/', 1)
    user = self._github.get_user()

    if user.login.lower() == owner.lower():
        # Create in user account
        created_repo = user.create_repo(
            name=repo,
            private=private,
            description=description
        )
    else:
        # Create in organization
        org = self._github.get_organization(owner)
        created_repo = org.create_repo(
            name=repo,
            private=private,
            description=description
        )

    return created_repo.raw_data
```

### 2. GitHub Service Layer

**File**: `github_data/github/service.py`

Add two new methods to `GitHubService` class:

```python
def get_repository_metadata(self, repo_name: str) -> Optional[Dict[str, Any]]:
    """Get repository metadata with rate limiting.

    Args:
        repo_name: Repository name in format "owner/repo"

    Returns:
        Dictionary containing repository metadata, or None if not found
    """
    from github import UnknownObjectException

    try:
        return cast(
            Dict[str, Any],
            self._execute_with_cross_cutting_concerns(
                cache_key=None,  # Don't cache metadata checks
                operation=lambda: self._boundary.get_repository_metadata(repo_name),
            ),
        )
    except UnknownObjectException:
        # Repository doesn't exist
        return None

def create_repository(
    self,
    repo_name: str,
    private: bool = False,
    description: str = ""
) -> Dict[str, Any]:
    """Create repository with rate limiting and retry logic.

    Args:
        repo_name: Repository name in format "owner/repo"
        private: Whether repository should be private
        description: Repository description

    Returns:
        Dictionary containing repository metadata
    """
    return cast(
        Dict[str, Any],
        self._execute_with_cross_cutting_concerns(
            cache_key=None,  # Don't cache repository creation
            operation=lambda: self._boundary.create_repository(
                repo_name, private, description
            ),
        ),
    )
```

### 3. GitHub Protocols

**File**: `github_data/github/protocols.py`

Add method signatures to `RepositoryService` protocol:

```python
def get_repository_metadata(self, repo_name: str) -> Optional[Dict[str, Any]]:
    """Get repository metadata.

    Args:
        repo_name: Repository name in format "owner/repo"

    Returns:
        Dictionary containing repository metadata, or None if not found
    """
    ...

def create_repository(
    self,
    repo_name: str,
    private: bool = False,
    description: str = ""
) -> Dict[str, Any]:
    """Create a new repository.

    Args:
        repo_name: Repository name in format "owner/repo"
        private: Whether repository should be private
        description: Repository description

    Returns:
        Dictionary containing repository metadata
    """
    ...
```

### 4. Main Entry Point

**File**: `github_data/main.py`

**Add instance variables to `Main` class**:
```python
self._create_repository_if_missing: bool = True
self._repository_visibility: str = "public"
```

**Add environment variable loaders**:
```python
def _load_create_repository_if_missing_from_environment(self) -> None:
    """Load CREATE_REPOSITORY_IF_MISSING setting (restore only)."""
    if self._operation != "restore":
        return

    value = os.getenv("CREATE_REPOSITORY_IF_MISSING", "true")
    try:
        from github_data.config.number_parser import NumberSpecificationParser
        self._create_repository_if_missing = NumberSpecificationParser.parse_boolean_value(value)
    except ValueError as e:
        exit(f"Error: Invalid CREATE_REPOSITORY_IF_MISSING value. {e}")

def _load_repository_visibility_from_environment(self) -> None:
    """Load REPOSITORY_VISIBILITY setting (restore only)."""
    if self._operation != "restore":
        return

    value = os.getenv("REPOSITORY_VISIBILITY", "public").lower()
    if value not in ["public", "private"]:
        exit(
            f"Error: Invalid REPOSITORY_VISIBILITY '{value}'. "
            f"Must be 'public' or 'private'."
        )
    self._repository_visibility = value
```

**Add repository existence checking**:
```python
def _ensure_repository_exists(self) -> None:
    """Ensure target repository exists, creating if necessary.

    Only runs for restore operations.
    Checks if repository exists and creates it if CREATE_REPOSITORY_IF_MISSING is true.
    """
    if self._operation != "restore":
        return

    # Check if repository exists
    metadata = self._github_service.get_repository_metadata(self._repo_name)

    if metadata is not None:
        # Repository exists, nothing to do
        return

    # Repository doesn't exist
    if not self._create_repository_if_missing:
        exit(
            f"Error: Repository '{self._repo_name}' does not exist. "
            f"Set CREATE_REPOSITORY_IF_MISSING=true to create it automatically."
        )

    # Create repository
    print(f"Repository '{self._repo_name}' does not exist. Creating...")
    private = (self._repository_visibility == "private")
    self._github_service.create_repository(
        self._repo_name,
        private=private,
        description=""
    )
    print(f"Created {'private' if private else 'public'} repository: {self._repo_name}")
```

**Update `main()` method**:
```python
def main(self) -> None:
    """Execute save or restore operation based on environment variables."""
    self._load_operation_from_environment()
    self._load_registry_from_environment()
    self._load_github_token_from_environment()
    self._load_github_repo_from_environment()
    self._load_data_path_from_environment()
    self._load_create_repository_if_missing_from_environment()  # NEW
    self._load_repository_visibility_from_environment()  # NEW
    self._build_github_service()
    self._build_storage_service()
    self._ensure_repository_exists()  # NEW
    self._build_git_service()
    self._build_orchestrator()
    self._execute_operation()
```

## Error Handling

### PyGithub Exception Handling

**Repository Not Found** (404):
- Exception: `github.UnknownObjectException`
- Handling: Return `None` from `get_repository_metadata()`
- User impact: Triggers repository creation logic or fails with helpful message

**Permission Denied** (403):
- Exception: `github.GithubException` with status 403
- Handling: Let exception propagate
- User impact: Clear error message about insufficient permissions

**Other API Errors**:
- Exception: `github.GithubException`
- Handling: Let exception propagate
- User impact: Error message with GitHub API details

### User-Facing Error Messages

**Repository doesn't exist, CREATE_REPOSITORY_IF_MISSING=false**:
```
Error: Repository 'owner/repo' does not exist. Set CREATE_REPOSITORY_IF_MISSING=true to create it automatically.
```

**Invalid CREATE_REPOSITORY_IF_MISSING value**:
```
Error: Invalid CREATE_REPOSITORY_IF_MISSING value. Invalid boolean value: 'maybe'. Valid values are: false, no, off, on, true, yes
```

**Invalid REPOSITORY_VISIBILITY value**:
```
Error: Invalid REPOSITORY_VISIBILITY 'internal'. Must be 'public' or 'private'.
```

## Testing Strategy

### Unit Tests

**File**: `tests/unit/github/test_boundary.py`
- Test `create_repository()` with user account
- Test `create_repository()` with organization
- Test `get_repository_metadata()` for existing repository
- Test `get_repository_metadata()` for non-existent repository (raises UnknownObjectException)

**File**: `tests/unit/github/test_service.py`
- Test `create_repository()` with rate limiting and retry
- Test `get_repository_metadata()` returns None for 404
- Test `get_repository_metadata()` propagates other exceptions

**File**: `tests/unit/test_main.py`
- Test `_load_create_repository_if_missing_from_environment()` with valid values
- Test `_load_create_repository_if_missing_from_environment()` with invalid values
- Test `_load_repository_visibility_from_environment()` with valid values
- Test `_load_repository_visibility_from_environment()` with invalid values
- Test `_ensure_repository_exists()` when repository exists
- Test `_ensure_repository_exists()` when repository doesn't exist and CREATE_REPOSITORY_IF_MISSING=true
- Test `_ensure_repository_exists()` when repository doesn't exist and CREATE_REPOSITORY_IF_MISSING=false
- Test that save operation skips loading these parameters

### Integration Tests

**File**: `tests/integration/test_repository_creation_integration.py`
- Test full restore flow with automatic repository creation
- Test full restore flow with repository creation disabled (should fail)
- Test repository visibility (public vs private)

### Test Scenarios

| Scenario | CREATE_REPOSITORY_IF_MISSING | REPOSITORY_VISIBILITY | Repository Exists | Expected Behavior |
|----------|------------------------------|----------------------|-------------------|-------------------|
| 1 | true | public | No | Creates public repository, proceeds with restore |
| 2 | true | private | No | Creates private repository, proceeds with restore |
| 3 | false | (ignored) | No | Fails with error message |
| 4 | true | public | Yes | Proceeds with restore (no creation) |
| 5 | false | (ignored) | Yes | Proceeds with restore (no creation) |
| 6 | (save op) | (save op) | Yes | Parameters ignored, proceeds with save |
| 7 | (save op) | (save op) | No | Parameters ignored, proceeds with save |

## Future Enhancements

### Repository Configuration Preservation (Future)

When implementing repository-level configuration preservation:

1. **Save Operation**: Capture repository settings (branch protection rules, webhooks, settings)
2. **Restore Operation**: Apply saved settings to created repository
3. **New parameter**: `APPLY_REPOSITORY_SETTINGS` (default: `false`)

This design provides the foundation for that feature by ensuring the repository exists before attempting to apply configuration.

### Validation Example (Future):
```python
def _ensure_repository_exists(self) -> None:
    # ... existing logic ...

    # Future: Apply repository settings if available
    if self._apply_repository_settings:
        self._apply_saved_repository_configuration()
```

## README Documentation Updates

Add to environment variables table in README.md:

```markdown
| `CREATE_REPOSITORY_IF_MISSING` | No | Create repository if it doesn't exist during restore (default: `true`) |
| `REPOSITORY_VISIBILITY` | No | Repository visibility when creating: `public` or `private` (default: `public`) |
```

Add new section after "Label Conflict Strategies":

```markdown
### Repository Creation Behavior

When restoring to a repository that doesn't exist, you can control the creation behavior:

- **`true`** (default): Automatically create the repository if it doesn't exist
- **`false`**: Fail with an error message if the repository doesn't exist

Control repository visibility when creating:
- **`public`** (default): Create publicly visible repository
- **`private`**: Create private repository

**Note**: These parameters only apply to restore operations and are ignored during save operations.
```

## Security Considerations

1. **Token Permissions**: Creating repositories requires appropriate GitHub token permissions
   - Personal access token needs `repo` scope
   - For organizations, token needs `repo` and appropriate org permissions

2. **Visibility Control**: Private repository creation is restricted by:
   - User account plan (free accounts have limited private repos)
   - Organization settings and permissions

3. **No Secrets in Logs**: Repository creation confirmation messages don't include sensitive data

## Compatibility

- **Backward Compatible**: Default behavior (CREATE_REPOSITORY_IF_MISSING=true) matches expected user intent
- **No Breaking Changes**: Existing restore operations continue to work without any changes
- **Save Operations Unaffected**: Save operations completely ignore these parameters

## Summary

This design adds repository creation control to the GitHub Data restore workflow by:

1. Adding two new environment variables for restore operations
2. Implementing repository existence checking before entity restoration
3. Providing user control over repository creation and visibility
4. Maintaining backward compatibility with existing workflows
5. Following existing code patterns and conventions
6. Establishing foundation for future repository configuration features
