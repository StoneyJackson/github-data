# Repository Creation Control Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add user control over repository creation behavior during restore operations with CREATE_REPOSITORY_IF_MISSING and REPOSITORY_VISIBILITY parameters.

**Architecture:** Fail-fast approach that checks repository existence before entity restoration begins. Add repository creation methods to GitHub API layers (boundary, service, protocol). Add environment variable loaders to main.py following existing patterns. Reuse NumberSpecificationParser for boolean parsing.

**Tech Stack:** Python 3.12, PyGithub, pytest, existing GitHub Data architecture (boundary/service/protocol layers)

---

## Task 1: Add Repository Metadata Method to GitHub Boundary Layer

**Files:**
- Modify: `github_data/github/boundary.py`
- Test: `tests/unit/github/test_boundary.py`

**Step 1: Write the failing test**

Create test in `tests/unit/github/test_boundary.py`:

```python
def test_get_repository_metadata_returns_raw_data(self):
    """Test get_repository_metadata returns raw repository data."""
    # Mock PyGithub repository object
    mock_repo = MagicMock()
    mock_repo.raw_data = {
        "id": 12345,
        "name": "test-repo",
        "full_name": "owner/test-repo",
        "private": False
    }

    self.mock_github.get_repo.return_value = mock_repo

    result = self.boundary.get_repository_metadata("owner/test-repo")

    assert result == mock_repo.raw_data
    self.mock_github.get_repo.assert_called_once_with("owner/test-repo")

def test_get_repository_metadata_raises_on_not_found(self):
    """Test get_repository_metadata raises UnknownObjectException for 404."""
    from github import UnknownObjectException

    self.mock_github.get_repo.side_effect = UnknownObjectException(
        status=404,
        data={"message": "Not Found"}
    )

    with pytest.raises(UnknownObjectException):
        self.boundary.get_repository_metadata("owner/nonexistent")
```

**Step 2: Run test to verify it fails**

Run: `make test-unit`
Expected: FAIL with "AttributeError: 'GitHubApiBoundary' object has no attribute 'get_repository_metadata'"

**Step 3: Write minimal implementation**

In `github_data/github/boundary.py`, add method to `GitHubApiBoundary` class:

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
```

**Step 4: Run test to verify it passes**

Run: `make test-unit`
Expected: PASS

**Step 5: Commit**

```bash
git add github_data/github/boundary.py tests/unit/github/test_boundary.py
git commit -s -m "feat(boundary): add get_repository_metadata method

Add method to retrieve repository metadata from GitHub API.
Returns raw JSON data or raises UnknownObjectException for 404.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 2: Add Repository Creation Method to GitHub Boundary Layer

**Files:**
- Modify: `github_data/github/boundary.py`
- Test: `tests/unit/github/test_boundary.py`

**Step 1: Write the failing tests**

Add to `tests/unit/github/test_boundary.py`:

```python
def test_create_repository_in_user_account(self):
    """Test create_repository creates repo in user account."""
    mock_user = MagicMock()
    mock_user.login = "testuser"
    mock_created_repo = MagicMock()
    mock_created_repo.raw_data = {
        "id": 67890,
        "name": "new-repo",
        "full_name": "testuser/new-repo",
        "private": False
    }

    self.mock_github.get_user.return_value = mock_user
    mock_user.create_repo.return_value = mock_created_repo

    result = self.boundary.create_repository(
        "testuser/new-repo",
        private=False,
        description="Test repository"
    )

    assert result == mock_created_repo.raw_data
    mock_user.create_repo.assert_called_once_with(
        name="new-repo",
        private=False,
        description="Test repository"
    )

def test_create_repository_in_organization(self):
    """Test create_repository creates repo in organization."""
    mock_user = MagicMock()
    mock_user.login = "testuser"
    mock_org = MagicMock()
    mock_created_repo = MagicMock()
    mock_created_repo.raw_data = {
        "id": 67890,
        "name": "new-repo",
        "full_name": "testorg/new-repo",
        "private": True
    }

    self.mock_github.get_user.return_value = mock_user
    self.mock_github.get_organization.return_value = mock_org
    mock_org.create_repo.return_value = mock_created_repo

    result = self.boundary.create_repository(
        "testorg/new-repo",
        private=True,
        description="Test org repo"
    )

    assert result == mock_created_repo.raw_data
    self.mock_github.get_organization.assert_called_once_with("testorg")
    mock_org.create_repo.assert_called_once_with(
        name="new-repo",
        private=True,
        description="Test org repo"
    )
```

**Step 2: Run tests to verify they fail**

Run: `make test-unit`
Expected: FAIL with "AttributeError: 'GitHubApiBoundary' object has no attribute 'create_repository'"

**Step 3: Write minimal implementation**

In `github_data/github/boundary.py`, add method to `GitHubApiBoundary` class:

```python
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

**Step 4: Run tests to verify they pass**

Run: `make test-unit`
Expected: PASS

**Step 5: Commit**

```bash
git add github_data/github/boundary.py tests/unit/github/test_boundary.py
git commit -s -m "feat(boundary): add create_repository method

Add method to create repositories in user accounts or organizations.
Handles owner detection and delegates to appropriate PyGithub API.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 3: Add Repository Methods to GitHub Service Layer

**Files:**
- Modify: `github_data/github/service.py`
- Test: `tests/unit/github/test_service.py`

**Step 1: Write the failing tests**

Add to `tests/unit/github/test_service.py`:

```python
def test_get_repository_metadata_returns_data_when_exists(self):
    """Test get_repository_metadata returns data for existing repository."""
    expected_data = {"id": 123, "name": "repo", "full_name": "owner/repo"}
    self.mock_boundary.get_repository_metadata.return_value = expected_data

    result = self.service.get_repository_metadata("owner/repo")

    assert result == expected_data
    self.mock_boundary.get_repository_metadata.assert_called_once_with("owner/repo")

def test_get_repository_metadata_returns_none_on_404(self):
    """Test get_repository_metadata returns None when repository not found."""
    from github import UnknownObjectException

    self.mock_boundary.get_repository_metadata.side_effect = UnknownObjectException(
        status=404,
        data={"message": "Not Found"}
    )

    result = self.service.get_repository_metadata("owner/nonexistent")

    assert result is None

def test_get_repository_metadata_propagates_other_exceptions(self):
    """Test get_repository_metadata propagates non-404 exceptions."""
    from github import GithubException

    self.mock_boundary.get_repository_metadata.side_effect = GithubException(
        status=403,
        data={"message": "Forbidden"}
    )

    with pytest.raises(GithubException):
        self.service.get_repository_metadata("owner/repo")

def test_create_repository_calls_boundary(self):
    """Test create_repository delegates to boundary layer."""
    expected_data = {"id": 456, "name": "new-repo", "private": True}
    self.mock_boundary.create_repository.return_value = expected_data

    result = self.service.create_repository(
        "owner/new-repo",
        private=True,
        description="Test repo"
    )

    assert result == expected_data
    self.mock_boundary.create_repository.assert_called_once_with(
        "owner/new-repo",
        private=True,
        description="Test repo"
    )
```

**Step 2: Run tests to verify they fail**

Run: `make test-unit`
Expected: FAIL with "AttributeError: 'GitHubService' object has no attribute 'get_repository_metadata'"

**Step 3: Write minimal implementation**

In `github_data/github/service.py`, add methods to `GitHubService` class:

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

**Step 4: Run tests to verify they pass**

Run: `make test-unit`
Expected: PASS

**Step 5: Commit**

```bash
git add github_data/github/service.py tests/unit/github/test_service.py
git commit -s -m "feat(service): add repository metadata and creation methods

Add get_repository_metadata that returns None for 404 errors.
Add create_repository with rate limiting and retry logic.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 4: Add Repository Methods to GitHub Protocol

**Files:**
- Modify: `github_data/github/protocols.py`

**Step 1: Add protocol method signatures**

In `github_data/github/protocols.py`, add to `RepositoryService` protocol:

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

**Step 2: Run type check to verify**

Run: `make type-check`
Expected: PASS (no type errors)

**Step 3: Commit**

```bash
git add github_data/github/protocols.py
git commit -s -m "feat(protocols): add repository creation protocol methods

Add get_repository_metadata and create_repository to RepositoryService
protocol for type safety.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 5: Add Environment Variable Loading to Main

**Files:**
- Modify: `github_data/main.py`
- Test: `tests/unit/test_main.py`

**Step 1: Write the failing tests**

Create/modify `tests/unit/test_main.py`:

```python
def test_load_create_repository_if_missing_default(self):
    """Test CREATE_REPOSITORY_IF_MISSING defaults to true."""
    with patch.dict(os.environ, {"OPERATION": "restore"}, clear=True):
        main = Main()
        main._operation = "restore"
        main._load_create_repository_if_missing_from_environment()

        assert main._create_repository_if_missing is True

def test_load_create_repository_if_missing_true_values(self):
    """Test CREATE_REPOSITORY_IF_MISSING accepts true values."""
    for value in ["true", "True", "TRUE", "yes", "on", "1"]:
        with patch.dict(os.environ, {"OPERATION": "restore", "CREATE_REPOSITORY_IF_MISSING": value}):
            main = Main()
            main._operation = "restore"
            main._load_create_repository_if_missing_from_environment()

            assert main._create_repository_if_missing is True, f"Failed for value: {value}"

def test_load_create_repository_if_missing_false_values(self):
    """Test CREATE_REPOSITORY_IF_MISSING accepts false values."""
    for value in ["false", "False", "FALSE", "no", "off", "0"]:
        with patch.dict(os.environ, {"OPERATION": "restore", "CREATE_REPOSITORY_IF_MISSING": value}):
            main = Main()
            main._operation = "restore"
            main._load_create_repository_if_missing_from_environment()

            assert main._create_repository_if_missing is False, f"Failed for value: {value}"

def test_load_create_repository_if_missing_invalid_value_exits(self):
    """Test CREATE_REPOSITORY_IF_MISSING exits on invalid value."""
    with patch.dict(os.environ, {"OPERATION": "restore", "CREATE_REPOSITORY_IF_MISSING": "maybe"}):
        main = Main()
        main._operation = "restore"

        with pytest.raises(SystemExit):
            main._load_create_repository_if_missing_from_environment()

def test_load_create_repository_if_missing_skipped_for_save(self):
    """Test CREATE_REPOSITORY_IF_MISSING not loaded for save operation."""
    with patch.dict(os.environ, {"OPERATION": "save", "CREATE_REPOSITORY_IF_MISSING": "false"}):
        main = Main()
        main._operation = "save"
        main._create_repository_if_missing = True  # Set to default
        main._load_create_repository_if_missing_from_environment()

        # Should remain at default since save operation skips loading
        assert main._create_repository_if_missing is True

def test_load_repository_visibility_default(self):
    """Test REPOSITORY_VISIBILITY defaults to public."""
    with patch.dict(os.environ, {"OPERATION": "restore"}, clear=True):
        main = Main()
        main._operation = "restore"
        main._load_repository_visibility_from_environment()

        assert main._repository_visibility == "public"

def test_load_repository_visibility_valid_values(self):
    """Test REPOSITORY_VISIBILITY accepts public and private."""
    for value in ["public", "Public", "PUBLIC"]:
        with patch.dict(os.environ, {"OPERATION": "restore", "REPOSITORY_VISIBILITY": value}):
            main = Main()
            main._operation = "restore"
            main._load_repository_visibility_from_environment()

            assert main._repository_visibility == "public", f"Failed for value: {value}"

    for value in ["private", "Private", "PRIVATE"]:
        with patch.dict(os.environ, {"OPERATION": "restore", "REPOSITORY_VISIBILITY": value}):
            main = Main()
            main._operation = "restore"
            main._load_repository_visibility_from_environment()

            assert main._repository_visibility == "private", f"Failed for value: {value}"

def test_load_repository_visibility_invalid_value_exits(self):
    """Test REPOSITORY_VISIBILITY exits on invalid value."""
    with patch.dict(os.environ, {"OPERATION": "restore", "REPOSITORY_VISIBILITY": "internal"}):
        main = Main()
        main._operation = "restore"

        with pytest.raises(SystemExit):
            main._load_repository_visibility_from_environment()

def test_load_repository_visibility_skipped_for_save(self):
    """Test REPOSITORY_VISIBILITY not loaded for save operation."""
    with patch.dict(os.environ, {"OPERATION": "save", "REPOSITORY_VISIBILITY": "private"}):
        main = Main()
        main._operation = "save"
        main._repository_visibility = "public"  # Set to default
        main._load_repository_visibility_from_environment()

        # Should remain at default since save operation skips loading
        assert main._repository_visibility == "public"
```

**Step 2: Run tests to verify they fail**

Run: `make test-unit`
Expected: FAIL with "AttributeError: 'Main' object has no attribute '_load_create_repository_if_missing_from_environment'"

**Step 3: Add instance variables to Main class**

In `github_data/main.py`, add to `Main.__init__()`:

```python
self._create_repository_if_missing: bool = True
self._repository_visibility: str = "public"
```

**Step 4: Write environment variable loader methods**

In `github_data/main.py`, add methods to `Main` class:

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

**Step 5: Run tests to verify they pass**

Run: `make test-unit`
Expected: PASS

**Step 6: Commit**

```bash
git add github_data/main.py tests/unit/test_main.py
git commit -s -m "feat(main): add environment variable loaders for repository creation

Add _load_create_repository_if_missing_from_environment method.
Add _load_repository_visibility_from_environment method.
Both methods only load for restore operations.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 6: Add Repository Existence Check to Main

**Files:**
- Modify: `github_data/main.py`
- Test: `tests/unit/test_main.py`

**Step 1: Write the failing tests**

Add to `tests/unit/test_main.py`:

```python
def test_ensure_repository_exists_when_repo_exists(self):
    """Test _ensure_repository_exists does nothing when repo exists."""
    with patch.dict(os.environ, {"OPERATION": "restore"}):
        main = Main()
        main._operation = "restore"
        main._repo_name = "owner/repo"
        main._github_service = MagicMock()
        main._github_service.get_repository_metadata.return_value = {"id": 123}

        # Should not raise
        main._ensure_repository_exists()

        main._github_service.get_repository_metadata.assert_called_once_with("owner/repo")
        main._github_service.create_repository.assert_not_called()

def test_ensure_repository_exists_creates_when_missing_and_flag_true(self):
    """Test _ensure_repository_exists creates repo when missing and flag is true."""
    with patch.dict(os.environ, {"OPERATION": "restore"}):
        main = Main()
        main._operation = "restore"
        main._repo_name = "owner/repo"
        main._create_repository_if_missing = True
        main._repository_visibility = "public"
        main._github_service = MagicMock()
        main._github_service.get_repository_metadata.return_value = None

        with patch('builtins.print'):
            main._ensure_repository_exists()

        main._github_service.create_repository.assert_called_once_with(
            "owner/repo",
            private=False,
            description=""
        )

def test_ensure_repository_exists_creates_private_when_visibility_private(self):
    """Test _ensure_repository_exists creates private repo when visibility is private."""
    with patch.dict(os.environ, {"OPERATION": "restore"}):
        main = Main()
        main._operation = "restore"
        main._repo_name = "owner/repo"
        main._create_repository_if_missing = True
        main._repository_visibility = "private"
        main._github_service = MagicMock()
        main._github_service.get_repository_metadata.return_value = None

        with patch('builtins.print'):
            main._ensure_repository_exists()

        main._github_service.create_repository.assert_called_once_with(
            "owner/repo",
            private=True,
            description=""
        )

def test_ensure_repository_exists_fails_when_missing_and_flag_false(self):
    """Test _ensure_repository_exists exits when repo missing and flag is false."""
    with patch.dict(os.environ, {"OPERATION": "restore"}):
        main = Main()
        main._operation = "restore"
        main._repo_name = "owner/repo"
        main._create_repository_if_missing = False
        main._github_service = MagicMock()
        main._github_service.get_repository_metadata.return_value = None

        with pytest.raises(SystemExit):
            main._ensure_repository_exists()

def test_ensure_repository_exists_skipped_for_save(self):
    """Test _ensure_repository_exists does nothing for save operation."""
    with patch.dict(os.environ, {"OPERATION": "save"}):
        main = Main()
        main._operation = "save"
        main._github_service = MagicMock()

        main._ensure_repository_exists()

        main._github_service.get_repository_metadata.assert_not_called()
```

**Step 2: Run tests to verify they fail**

Run: `make test-unit`
Expected: FAIL with "AttributeError: 'Main' object has no attribute '_ensure_repository_exists'"

**Step 3: Write minimal implementation**

In `github_data/main.py`, add method to `Main` class:

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

**Step 4: Run tests to verify they pass**

Run: `make test-unit`
Expected: PASS

**Step 5: Commit**

```bash
git add github_data/main.py tests/unit/test_main.py
git commit -s -m "feat(main): add repository existence check and creation

Add _ensure_repository_exists method that checks if repository exists
and creates it if CREATE_REPOSITORY_IF_MISSING is true.
Only runs for restore operations.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 7: Integrate Repository Check into Main Execution Flow

**Files:**
- Modify: `github_data/main.py`
- Test: `tests/unit/test_main.py`

**Step 1: Write the failing test**

Add to `tests/unit/test_main.py`:

```python
def test_main_calls_ensure_repository_exists_for_restore(self):
    """Test main() calls _ensure_repository_exists for restore operation."""
    with patch.dict(os.environ, {
        "OPERATION": "restore",
        "GITHUB_TOKEN": "token",
        "GITHUB_REPO": "owner/repo",
        "DATA_PATH": "/data"
    }):
        with patch.object(Main, '_ensure_repository_exists') as mock_ensure:
            with patch.object(Main, '_execute_operation'):
                with patch.object(Main, '_build_github_service'):
                    with patch.object(Main, '_build_storage_service'):
                        with patch.object(Main, '_build_git_service'):
                            with patch.object(Main, '_build_orchestrator'):
                                main = Main()
                                main.main()

        mock_ensure.assert_called_once()

def test_main_execution_order(self):
    """Test main() calls methods in correct order."""
    with patch.dict(os.environ, {
        "OPERATION": "restore",
        "GITHUB_TOKEN": "token",
        "GITHUB_REPO": "owner/repo"
    }):
        main = Main()
        calls = []

        # Patch all methods to track call order
        with patch.object(main, '_load_operation_from_environment', side_effect=lambda: calls.append('load_op')):
            with patch.object(main, '_load_registry_from_environment', side_effect=lambda: calls.append('load_registry')):
                with patch.object(main, '_load_github_token_from_environment', side_effect=lambda: calls.append('load_token')):
                    with patch.object(main, '_load_github_repo_from_environment', side_effect=lambda: calls.append('load_repo')):
                        with patch.object(main, '_load_data_path_from_environment', side_effect=lambda: calls.append('load_path')):
                            with patch.object(main, '_load_create_repository_if_missing_from_environment', side_effect=lambda: calls.append('load_create_flag')):
                                with patch.object(main, '_load_repository_visibility_from_environment', side_effect=lambda: calls.append('load_visibility')):
                                    with patch.object(main, '_build_github_service', side_effect=lambda: calls.append('build_github')):
                                        with patch.object(main, '_build_storage_service', side_effect=lambda: calls.append('build_storage')):
                                            with patch.object(main, '_ensure_repository_exists', side_effect=lambda: calls.append('ensure_repo')):
                                                with patch.object(main, '_build_git_service', side_effect=lambda: calls.append('build_git')):
                                                    with patch.object(main, '_build_orchestrator', side_effect=lambda: calls.append('build_orch')):
                                                        with patch.object(main, '_execute_operation', side_effect=lambda: calls.append('execute')):
                                                            main.main()

        expected = [
            'load_op', 'load_registry', 'load_token', 'load_repo', 'load_path',
            'load_create_flag', 'load_visibility',
            'build_github', 'build_storage', 'ensure_repo', 'build_git',
            'build_orch', 'execute'
        ]
        assert calls == expected
```

**Step 2: Run test to verify it fails**

Run: `make test-unit`
Expected: FAIL because _ensure_repository_exists is not called in main()

**Step 3: Update main() method**

In `github_data/main.py`, modify the `main()` method:

```python
def main(self) -> None:
    """Execute save or restore operation based on environment variables."""
    self._load_operation_from_environment()
    self._load_registry_from_environment()
    self._load_github_token_from_environment()
    self._load_github_repo_from_environment()
    self._load_data_path_from_environment()
    self._load_create_repository_if_missing_from_environment()
    self._load_repository_visibility_from_environment()
    self._build_github_service()
    self._build_storage_service()
    self._ensure_repository_exists()
    self._build_git_service()
    self._build_orchestrator()
    self._execute_operation()
```

**Step 4: Run tests to verify they pass**

Run: `make test-unit`
Expected: PASS

**Step 5: Run full test suite**

Run: `make test-fast`
Expected: PASS

**Step 6: Commit**

```bash
git add github_data/main.py tests/unit/test_main.py
git commit -s -m "feat(main): integrate repository existence check into execution flow

Call _ensure_repository_exists after building services but before
building orchestrator. Ensures repository exists before any entity
restoration begins.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 8: Update README Documentation

**Files:**
- Modify: `README.md`

**Step 1: Add environment variables to table**

In `README.md`, add to the environment variables table (around line 76):

```markdown
| `CREATE_REPOSITORY_IF_MISSING` | No | Create repository if it doesn't exist during restore (default: `true`) |
| `REPOSITORY_VISIBILITY` | No | Repository visibility when creating: `public` or `private` (default: `public`) |
```

**Step 2: Add new section after Label Conflict Strategies**

After the "Label Conflict Strategies" section (around line 87), add:

```markdown
### Repository Creation Behavior

When restoring to a repository that doesn't exist, you can control the creation behavior:

- **`true`** (default): Automatically create the repository if it doesn't exist
- **`false`**: Fail with an error message if the repository doesn't exist

Control repository visibility when creating:
- **`public`** (default): Create publicly visible repository
- **`private`**: Create private repository

**Example - Create private repository if missing:**
```bash
docker run --rm \
  -e OPERATION=restore \
  -e GITHUB_TOKEN=your_token_here \
  -e GITHUB_REPO=owner/repository \
  -e CREATE_REPOSITORY_IF_MISSING=true \
  -e REPOSITORY_VISIBILITY=private \
  -v "${PWD}:/data" \
  ghcr.io/stoneyjackson/github-data:latest
```

**Example - Fail if repository doesn't exist:**
```bash
docker run --rm \
  -e OPERATION=restore \
  -e GITHUB_TOKEN=your_token_here \
  -e GITHUB_REPO=owner/repository \
  -e CREATE_REPOSITORY_IF_MISSING=false \
  -v "${PWD}:/data" \
  ghcr.io/stoneyjackson/github-data:latest
```

**Note**: These parameters only apply to restore operations and are ignored during save operations.
```

**Step 3: Update Boolean Environment Variables section**

Update the Boolean Environment Variables section to include new variables in the list (around line 90):

```markdown
Boolean environment variables (`INCLUDE_GIT_REPO`, `INCLUDE_LABELS`, `INCLUDE_MILESTONES`, `INCLUDE_ISSUES`, `INCLUDE_ISSUE_COMMENTS`, `INCLUDE_PULL_REQUESTS`, `INCLUDE_PULL_REQUEST_COMMENTS`, `INCLUDE_PR_REVIEWS`, `INCLUDE_PR_REVIEW_COMMENTS`, `INCLUDE_SUB_ISSUES`, `INCLUDE_RELEASES`, `INCLUDE_RELEASE_ASSETS`, `CREATE_REPOSITORY_IF_MISSING`) accept the following values:
```

**Step 4: Commit**

```bash
git add README.md
git commit -s -m "docs(readme): document repository creation control parameters

Add CREATE_REPOSITORY_IF_MISSING and REPOSITORY_VISIBILITY to
environment variables documentation. Include usage examples.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 9: Run Full Quality Checks

**Step 1: Run all quality checks**

Run: `make check`
Expected: All checks pass (format, lint, type-check, test-fast)

**Step 2: If any checks fail, fix them**

Fix formatting:
```bash
make format
```

Fix linting issues as needed.

Fix type errors as needed.

**Step 3: Run checks again**

Run: `make check`
Expected: PASS

**Step 4: Commit any fixes**

```bash
git add -A
git commit -s -m "style: fix formatting and linting issues

Apply black formatting and fix any linting violations.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 10: Create Integration Test (Optional but Recommended)

**Files:**
- Create: `tests/integration/test_repository_creation_integration.py`

**Step 1: Write integration test**

Create `tests/integration/test_repository_creation_integration.py`:

```python
"""Integration tests for repository creation during restore."""

import pytest
import os
from unittest.mock import patch, MagicMock
from github_data.main import Main


@pytest.mark.integration
class TestRepositoryCreationIntegration:
    """Integration tests for repository creation control."""

    def test_restore_creates_repository_when_missing(self):
        """Test full restore flow creates repository when missing."""
        with patch.dict(os.environ, {
            "OPERATION": "restore",
            "GITHUB_TOKEN": "test-token",
            "GITHUB_REPO": "owner/test-repo",
            "DATA_PATH": "/tmp/test-data",
            "CREATE_REPOSITORY_IF_MISSING": "true",
            "REPOSITORY_VISIBILITY": "public"
        }):
            main = Main()

            # Mock GitHub service
            main._github_service = MagicMock()
            main._github_service.get_repository_metadata.return_value = None

            # Mock other services
            main._storage_service = MagicMock()
            main._git_service = None
            main._orchestrator = MagicMock()
            main._orchestrator.execute.return_value = []

            # Should create repository
            with patch('builtins.print'):
                main._ensure_repository_exists()

            main._github_service.create_repository.assert_called_once_with(
                "owner/test-repo",
                private=False,
                description=""
            )

    def test_restore_fails_when_repository_missing_and_flag_false(self):
        """Test restore fails when repository missing and CREATE_REPOSITORY_IF_MISSING is false."""
        with patch.dict(os.environ, {
            "OPERATION": "restore",
            "GITHUB_TOKEN": "test-token",
            "GITHUB_REPO": "owner/test-repo",
            "DATA_PATH": "/tmp/test-data",
            "CREATE_REPOSITORY_IF_MISSING": "false"
        }):
            main = Main()

            # Mock GitHub service
            main._github_service = MagicMock()
            main._github_service.get_repository_metadata.return_value = None

            # Should exit with error
            with pytest.raises(SystemExit):
                main._ensure_repository_exists()

    def test_restore_proceeds_when_repository_exists(self):
        """Test restore proceeds normally when repository exists."""
        with patch.dict(os.environ, {
            "OPERATION": "restore",
            "GITHUB_TOKEN": "test-token",
            "GITHUB_REPO": "owner/test-repo",
            "DATA_PATH": "/tmp/test-data"
        }):
            main = Main()

            # Mock GitHub service - repository exists
            main._github_service = MagicMock()
            main._github_service.get_repository_metadata.return_value = {"id": 123}

            # Should not create repository
            main._ensure_repository_exists()

            main._github_service.create_repository.assert_not_called()
```

**Step 2: Run integration test**

Run: `pytest tests/integration/test_repository_creation_integration.py -v`
Expected: PASS

**Step 3: Commit**

```bash
git add tests/integration/test_repository_creation_integration.py
git commit -s -m "test(integration): add repository creation integration tests

Add integration tests for full restore flow with repository creation.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Final Verification

**Step 1: Run complete test suite**

Run: `make check-all`
Expected: All tests pass including container tests

**Step 2: Verify git log**

Run: `git log --oneline -15`
Expected: See all commits from this implementation

**Step 3: Review changes**

Run: `git diff main`
Expected: Review all changes made

---

## Summary

This implementation adds repository creation control to GitHub Data restore operations:

- ✅ New GitHub API methods (boundary, service, protocol layers)
- ✅ Environment variable loading (CREATE_REPOSITORY_IF_MISSING, REPOSITORY_VISIBILITY)
- ✅ Pre-flight repository existence check
- ✅ Automatic repository creation with visibility control
- ✅ Comprehensive unit and integration tests
- ✅ Updated README documentation
- ✅ Follows TDD, DRY, YAGNI principles
- ✅ Frequent commits with clear messages

**Total Files Modified**: 6
**Total Files Created**: 2 (integration test + design doc)
**Total Commits**: ~10

**Next Steps**: Ready for code review and merge to main branch.
