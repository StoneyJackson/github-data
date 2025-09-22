"""Common fixtures for GitHub Data tests."""

import tempfile
import pytest


@pytest.fixture
def temp_data_dir():
    """Create temporary directory for test data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_github_data():
    """Sample GitHub API JSON data that boundary would return."""
    return {
        "labels": [
            {
                "name": "bug",
                "color": "d73a4a",
                "description": "Something isn't working",
                "url": "https://api.github.com/repos/owner/repo/labels/bug",
                "id": 1001,
            },
            {
                "name": "enhancement",
                "color": "a2eeef",
                "description": "New feature or request",
                "url": "https://api.github.com/repos/owner/repo/labels/enhancement",
                "id": 1002,
            },
        ],
        "issues": [
            {
                "id": 2001,
                "number": 1,
                "title": "Fix authentication bug",
                "body": "Users cannot login with valid credentials",
                "state": "open",
                "user": {
                    "login": "alice",
                    "id": 3001,
                    "avatar_url": "https://github.com/alice.png",
                    "html_url": "https://github.com/alice",
                },
                "assignees": [],
                "labels": [
                    {
                        "name": "bug",
                        "color": "d73a4a",
                        "description": "Something isn't working",
                        "url": "https://api.github.com/repos/owner/repo/labels/bug",
                        "id": 1001,
                    }
                ],
                "created_at": "2023-01-15T10:30:00Z",
                "updated_at": "2023-01-15T14:20:00Z",
                "closed_at": None,
                "html_url": "https://github.com/owner/repo/issues/1",
                "comments": 2,
            },
            {
                "id": 2002,
                "number": 2,
                "title": "Add user dashboard",
                "body": None,
                "state": "closed",
                "user": {
                    "login": "bob",
                    "id": 3002,
                    "avatar_url": "https://github.com/bob.png",
                    "html_url": "https://github.com/bob",
                },
                "assignees": [
                    {
                        "login": "alice",
                        "id": 3001,
                        "avatar_url": "https://github.com/alice.png",
                        "html_url": "https://github.com/alice",
                    }
                ],
                "labels": [
                    {
                        "name": "enhancement",
                        "color": "a2eeef",
                        "description": "New feature or request",
                        "url": (
                            "https://api.github.com/repos/owner/repo/"
                            "labels/enhancement"
                        ),
                        "id": 1002,
                    }
                ],
                "created_at": "2023-01-10T09:00:00Z",
                "updated_at": "2023-01-12T16:45:00Z",
                "closed_at": "2023-01-12T16:45:00Z",
                "html_url": "https://github.com/owner/repo/issues/2",
                "comments": 0,
            },
        ],
        "comments": [
            {
                "id": 4001,
                "body": "I can reproduce this issue",
                "user": {
                    "login": "charlie",
                    "id": 3003,
                    "avatar_url": "https://github.com/charlie.png",
                    "html_url": "https://github.com/charlie",
                },
                "created_at": "2023-01-15T12:00:00Z",
                "updated_at": "2023-01-15T12:00:00Z",
                "html_url": (
                    "https://github.com/owner/repo/issues/1#issuecomment-4001"
                ),
                "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
            },
            {
                "id": 4002,
                "body": "Fixed in PR #3",
                "user": {
                    "login": "alice",
                    "id": 3001,
                    "avatar_url": "https://github.com/alice.png",
                    "html_url": "https://github.com/alice",
                },
                "created_at": "2023-01-15T14:00:00Z",
                "updated_at": "2023-01-15T14:00:00Z",
                "html_url": (
                    "https://github.com/owner/repo/issues/2#issuecomment-4002"
                ),
                "issue_url": "https://api.github.com/repos/owner/repo/issues/2",
            },
        ],
        "pull_requests": [
            {
                "id": 5001,
                "number": 3,
                "title": "Implement API rate limiting",
                "body": "This PR adds rate limiting to prevent API abuse",
                "state": "MERGED",
                "user": {
                    "login": "alice",
                    "id": 3001,
                    "avatar_url": "https://github.com/alice.png",
                    "html_url": "https://github.com/alice",
                },
                "assignees": [
                    {
                        "login": "bob",
                        "id": 3002,
                        "avatar_url": "https://github.com/bob.png",
                        "html_url": "https://github.com/bob",
                    }
                ],
                "labels": [
                    {
                        "name": "enhancement",
                        "color": "a2eeef",
                        "description": "New feature or request",
                        "url": (
                            "https://api.github.com/repos/owner/repo/"
                            "labels/enhancement"
                        ),
                        "id": 1002,
                    }
                ],
                "created_at": "2023-01-16T10:00:00Z",
                "updated_at": "2023-01-18T15:30:00Z",
                "closed_at": "2023-01-18T15:30:00Z",
                "merged_at": "2023-01-18T15:30:00Z",
                "merge_commit_sha": "abc123def456",
                "base_ref": "main",
                "head_ref": "feature/rate-limiting",
                "html_url": "https://github.com/owner/repo/pull/3",
                "comments": 1,
            },
            {
                "id": 5002,
                "number": 4,
                "title": "Fix security vulnerability",
                "body": "Address XSS vulnerability in user input",
                "state": "OPEN",
                "user": {
                    "login": "charlie",
                    "id": 3003,
                    "avatar_url": "https://github.com/charlie.png",
                    "html_url": "https://github.com/charlie",
                },
                "assignees": [],
                "labels": [
                    {
                        "name": "bug",
                        "color": "d73a4a",
                        "description": "Something isn't working",
                        "url": "https://api.github.com/repos/owner/repo/labels/bug",
                        "id": 1001,
                    }
                ],
                "created_at": "2023-01-17T14:00:00Z",
                "updated_at": "2023-01-17T16:45:00Z",
                "closed_at": None,
                "merged_at": None,
                "merge_commit_sha": None,
                "base_ref": "main",
                "head_ref": "fix/xss-vulnerability",
                "html_url": "https://github.com/owner/repo/pull/4",
                "comments": 2,
            },
        ],
        "pr_comments": [
            {
                "id": 6001,
                "body": "Great work on the rate limiting implementation!",
                "user": {
                    "login": "bob",
                    "id": 3002,
                    "avatar_url": "https://github.com/bob.png",
                    "html_url": "https://github.com/bob",
                },
                "created_at": "2023-01-18T14:00:00Z",
                "updated_at": "2023-01-18T14:00:00Z",
                "html_url": ("https://github.com/owner/repo/pull/3#issuecomment-6001"),
                "pull_request_url": "https://github.com/owner/repo/pull/3",
            },
            {
                "id": 6002,
                "body": "Need to add more tests for edge cases",
                "user": {
                    "login": "alice",
                    "id": 3001,
                    "avatar_url": "https://github.com/alice.png",
                    "html_url": "https://github.com/alice",
                },
                "created_at": "2023-01-17T15:30:00Z",
                "updated_at": "2023-01-17T15:30:00Z",
                "html_url": ("https://github.com/owner/repo/pull/4#issuecomment-6002"),
                "pull_request_url": "https://github.com/owner/repo/pull/4",
            },
            {
                "id": 6003,
                "body": "Updated the implementation to handle edge cases",
                "user": {
                    "login": "charlie",
                    "id": 3003,
                    "avatar_url": "https://github.com/charlie.png",
                    "html_url": "https://github.com/charlie",
                },
                "created_at": "2023-01-17T16:45:00Z",
                "updated_at": "2023-01-17T16:45:00Z",
                "html_url": ("https://github.com/owner/repo/pull/4#issuecomment-6003"),
                "pull_request_url": "https://github.com/owner/repo/pull/4",
            },
        ],
    }


@pytest.fixture
def github_service_mock():
    """Mock GitHub service for testing."""
    from unittest.mock import Mock
    from src.github import create_github_service

    service = create_github_service("fake_token")
    service.boundary = Mock()
    return service


@pytest.fixture
def storage_service_mock():
    """Mock storage service for testing."""
    from src.storage import create_storage_service

    return create_storage_service("json")


@pytest.fixture
def mock_boundary_class():
    """Mock GitHubApiBoundary class for patching."""
    from unittest.mock import patch

    with patch("src.github.service.GitHubApiBoundary") as mock:
        yield mock


@pytest.fixture
def mock_boundary():
    """Configured mock boundary instance with all required methods."""
    from unittest.mock import Mock

    boundary = Mock()

    # Configure all boundary methods with default empty responses
    boundary.get_repository_labels.return_value = []
    boundary.get_repository_issues.return_value = []
    boundary.get_all_issue_comments.return_value = []
    boundary.get_repository_pull_requests.return_value = []
    boundary.get_all_pull_request_comments.return_value = []
    boundary.get_repository_sub_issues.return_value = []

    return boundary


@pytest.fixture
def github_service_with_mock(mock_boundary):
    """GitHub service with mocked boundary for testing."""
    from src.github.rate_limiter import RateLimitHandler
    from src.github.service import GitHubService

    rate_limiter = RateLimitHandler(max_retries=2, base_delay=0.1)
    return GitHubService(mock_boundary, rate_limiter)


@pytest.fixture
def empty_repository_data():
    """Sample data for empty repository testing."""
    return {
        "labels": [],
        "issues": [],
        "comments": [],
        "pull_requests": [],
        "pr_comments": [],
        "sub_issues": [],
    }


@pytest.fixture
def sample_sub_issues_data():
    """Sample sub-issues data with hierarchical relationships."""
    return {
        "issues": [
            {
                "id": 3001,
                "number": 1,
                "title": "Parent Issue",
                "body": "Main issue with sub-issues",
                "state": "open",
                "user": {
                    "login": "alice",
                    "id": 3001,
                    "avatar_url": "https://github.com/alice.png",
                    "html_url": "https://github.com/alice",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-15T10:30:00Z",
                "updated_at": "2023-01-15T14:20:00Z",
                "closed_at": None,
                "html_url": "https://github.com/owner/repo/issues/1",
                "comments": 0,
            },
            {
                "id": 3002,
                "number": 2,
                "title": "Sub-issue 1",
                "body": "First sub-issue",
                "state": "open",
                "user": {
                    "login": "bob",
                    "id": 3002,
                    "avatar_url": "https://github.com/bob.png",
                    "html_url": "https://github.com/bob",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-16T09:00:00Z",
                "updated_at": "2023-01-16T09:00:00Z",
                "closed_at": None,
                "html_url": "https://github.com/owner/repo/issues/2",
                "comments": 0,
            },
            {
                "id": 3003,
                "number": 3,
                "title": "Sub-issue 2",
                "body": "Second sub-issue",
                "state": "closed",
                "user": {
                    "login": "charlie",
                    "id": 3003,
                    "avatar_url": "https://github.com/charlie.png",
                    "html_url": "https://github.com/charlie",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-17T10:00:00Z",
                "updated_at": "2023-01-18T15:30:00Z",
                "closed_at": "2023-01-18T15:30:00Z",
                "html_url": "https://github.com/owner/repo/issues/3",
                "comments": 0,
            },
        ],
        "sub_issues": [
            {
                "sub_issue_id": 3002,
                "sub_issue_number": 2,
                "parent_issue_id": 3001,
                "parent_issue_number": 1,
                "position": 1,
            },
            {
                "sub_issue_id": 3003,
                "sub_issue_number": 3,
                "parent_issue_id": 3001,
                "parent_issue_number": 1,
                "position": 2,
            },
        ],
        "comments": [],
        "labels": [],
        "pull_requests": [],
        "pr_comments": [],
    }


@pytest.fixture
def complex_hierarchy_data():
    """Complex multi-level sub-issue hierarchy data."""
    return {
        "issues": [
            {
                "id": 4001,
                "number": 1,
                "title": "Grandparent Issue",
                "body": "Top-level issue with complex hierarchy",
                "state": "open",
                "user": {
                    "login": "alice",
                    "id": 3001,
                    "avatar_url": "https://github.com/alice.png",
                    "html_url": "https://github.com/alice",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-15T10:30:00Z",
                "updated_at": "2023-01-15T14:20:00Z",
                "closed_at": None,
                "html_url": "https://github.com/owner/repo/issues/1",
                "comments": 0,
            },
            {
                "id": 4002,
                "number": 2,
                "title": "Parent Issue A",
                "body": "First parent under grandparent",
                "state": "open",
                "user": {
                    "login": "bob",
                    "id": 3002,
                    "avatar_url": "https://github.com/bob.png",
                    "html_url": "https://github.com/bob",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-16T09:00:00Z",
                "updated_at": "2023-01-16T09:00:00Z",
                "closed_at": None,
                "html_url": "https://github.com/owner/repo/issues/2",
                "comments": 0,
            },
            {
                "id": 4003,
                "number": 3,
                "title": "Parent Issue B",
                "body": "Second parent under grandparent",
                "state": "open",
                "user": {
                    "login": "charlie",
                    "id": 3003,
                    "avatar_url": "https://github.com/charlie.png",
                    "html_url": "https://github.com/charlie",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-17T10:00:00Z",
                "updated_at": "2023-01-17T10:00:00Z",
                "closed_at": None,
                "html_url": "https://github.com/owner/repo/issues/3",
                "comments": 0,
            },
            {
                "id": 4004,
                "number": 4,
                "title": "Child Issue A1",
                "body": "Child under Parent A",
                "state": "open",
                "user": {
                    "login": "alice",
                    "id": 3001,
                    "avatar_url": "https://github.com/alice.png",
                    "html_url": "https://github.com/alice",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-18T11:00:00Z",
                "updated_at": "2023-01-18T11:00:00Z",
                "closed_at": None,
                "html_url": "https://github.com/owner/repo/issues/4",
                "comments": 0,
            },
            {
                "id": 4005,
                "number": 5,
                "title": "Child Issue B1",
                "body": "Child under Parent B",
                "state": "closed",
                "user": {
                    "login": "bob",
                    "id": 3002,
                    "avatar_url": "https://github.com/bob.png",
                    "html_url": "https://github.com/bob",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-19T12:00:00Z",
                "updated_at": "2023-01-20T16:30:00Z",
                "closed_at": "2023-01-20T16:30:00Z",
                "html_url": "https://github.com/owner/repo/issues/5",
                "comments": 0,
            },
        ],
        "sub_issues": [
            # Grandparent -> Parent relationships
            {
                "sub_issue_id": 4002,
                "sub_issue_number": 2,
                "parent_issue_id": 4001,
                "parent_issue_number": 1,
                "position": 1,
            },
            {
                "sub_issue_id": 4003,
                "sub_issue_number": 3,
                "parent_issue_id": 4001,
                "parent_issue_number": 1,
                "position": 2,
            },
            # Parent -> Child relationships
            {
                "sub_issue_id": 4004,
                "sub_issue_number": 4,
                "parent_issue_id": 4002,
                "parent_issue_number": 2,
                "position": 1,
            },
            {
                "sub_issue_id": 4005,
                "sub_issue_number": 5,
                "parent_issue_id": 4003,
                "parent_issue_number": 3,
                "position": 1,
            },
        ],
        "comments": [],
        "labels": [],
        "pull_requests": [],
        "pr_comments": [],
    }


@pytest.fixture
def sample_pr_data():
    """Sample pull request data for PR testing."""
    return {
        "pull_requests": [
            {
                "id": 5001,
                "number": 1,
                "title": "Feature implementation",
                "body": "Implements new feature",
                "state": "OPEN",
                "user": {
                    "login": "alice",
                    "id": 3001,
                    "avatar_url": "https://github.com/alice.png",
                    "html_url": "https://github.com/alice",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-16T10:00:00Z",
                "updated_at": "2023-01-16T10:00:00Z",
                "closed_at": None,
                "merged_at": None,
                "merge_commit_sha": None,
                "base_ref": "main",
                "head_ref": "feature/new-implementation",
                "html_url": "https://github.com/owner/repo/pull/1",
                "comments": 1,
            },
            {
                "id": 5002,
                "number": 2,
                "title": "Bug fix for validation",
                "body": "Fixes validation issue in user input",
                "state": "MERGED",
                "user": {
                    "login": "bob",
                    "id": 3002,
                    "avatar_url": "https://github.com/bob.png",
                    "html_url": "https://github.com/bob",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-17T14:00:00Z",
                "updated_at": "2023-01-18T16:45:00Z",
                "closed_at": "2023-01-18T16:45:00Z",
                "merged_at": "2023-01-18T16:45:00Z",
                "merge_commit_sha": "def789abc012",
                "base_ref": "main",
                "head_ref": "fix/validation-bug",
                "html_url": "https://github.com/owner/repo/pull/2",
                "comments": 2,
            },
        ],
        "pr_comments": [
            {
                "id": 6001,
                "body": "Great implementation!",
                "user": {
                    "login": "charlie",
                    "id": 3003,
                    "avatar_url": "https://github.com/charlie.png",
                    "html_url": "https://github.com/charlie",
                },
                "created_at": "2023-01-16T12:00:00Z",
                "updated_at": "2023-01-16T12:00:00Z",
                "html_url": "https://github.com/owner/repo/pull/1#issuecomment-6001",
                "pull_request_url": "https://github.com/owner/repo/pull/1",
            },
            {
                "id": 6002,
                "body": "This fix looks good to me",
                "user": {
                    "login": "alice",
                    "id": 3001,
                    "avatar_url": "https://github.com/alice.png",
                    "html_url": "https://github.com/alice",
                },
                "created_at": "2023-01-18T15:30:00Z",
                "updated_at": "2023-01-18T15:30:00Z",
                "html_url": "https://github.com/owner/repo/pull/2#issuecomment-6002",
                "pull_request_url": "https://github.com/owner/repo/pull/2",
            },
            {
                "id": 6003,
                "body": "Approved and ready to merge",
                "user": {
                    "login": "charlie",
                    "id": 3003,
                    "avatar_url": "https://github.com/charlie.png",
                    "html_url": "https://github.com/charlie",
                },
                "created_at": "2023-01-18T16:00:00Z",
                "updated_at": "2023-01-18T16:00:00Z",
                "html_url": "https://github.com/owner/repo/pull/2#issuecomment-6003",
                "pull_request_url": "https://github.com/owner/repo/pull/2",
            },
        ],
        "labels": [],
        "issues": [],
        "comments": [],
        "sub_issues": [],
    }


@pytest.fixture
def sample_labels_data():
    """Sample label data for conflict testing."""
    return {
        "labels": [
            {
                "name": "enhancement",
                "color": "a2eeef",
                "description": "New feature or request",
                "id": 1001,
                "url": "https://api.github.com/repos/owner/repo/labels/enhancement",
            },
            {
                "name": "bug",
                "color": "d73a4a",
                "description": "Something isn't working",
                "id": 1002,
                "url": "https://api.github.com/repos/owner/repo/labels/bug",
            },
            {
                "name": "documentation",
                "color": "0075ca",
                "description": "Improvements or additions to documentation",
                "id": 1003,
                "url": "https://api.github.com/repos/owner/repo/labels/documentation",
            },
            {
                "name": "good first issue",
                "color": "7057ff",
                "description": "Good for newcomers",
                "id": 1004,
                "url": (
                    "https://api.github.com/repos/owner/repo/labels/"
                    "good%20first%20issue"
                ),
            },
        ],
        "issues": [],
        "comments": [],
        "pull_requests": [],
        "pr_comments": [],
        "sub_issues": [],
    }


@pytest.fixture
def boundary_factory():
    """Factory for creating configured boundary mocks."""
    from tests.shared.mocks import MockBoundaryFactory

    return MockBoundaryFactory


@pytest.fixture
def boundary_with_data(sample_github_data):
    """Boundary mock pre-configured with comprehensive sample data."""
    from tests.shared.mocks import MockBoundaryFactory

    return MockBoundaryFactory.create_with_data("full", sample_data=sample_github_data)


@pytest.fixture
def storage_service_for_temp_dir(temp_data_dir):
    """Storage service configured for temporary directory."""
    from src.storage import create_storage_service

    # Create storage service and set base path for testing
    storage_service = create_storage_service("json")
    storage_service._base_path = temp_data_dir  # Set internal path for testing
    return storage_service


# Enhanced Boundary Mock Fixtures


@pytest.fixture
def boundary_with_repository_data(sample_github_data):
    """Boundary mock configured with full repository data responses."""
    from unittest.mock import Mock

    boundary = Mock()

    # Configure with realistic repository responses
    boundary.get_repository_labels.return_value = sample_github_data["labels"]
    boundary.get_repository_issues.return_value = sample_github_data["issues"]
    boundary.get_all_issue_comments.return_value = sample_github_data["comments"]
    boundary.get_repository_pull_requests.return_value = sample_github_data[
        "pull_requests"
    ]
    boundary.get_all_pull_request_comments.return_value = sample_github_data[
        "pr_comments"
    ]
    boundary.get_repository_sub_issues.return_value = sample_github_data.get(
        "sub_issues", []
    )

    return boundary


@pytest.fixture
def boundary_with_empty_repository():
    """Boundary mock simulating empty repository responses."""
    from unittest.mock import Mock

    boundary = Mock()

    # Configure with empty responses for all endpoints
    boundary.get_repository_labels.return_value = []
    boundary.get_repository_issues.return_value = []
    boundary.get_all_issue_comments.return_value = []
    boundary.get_repository_pull_requests.return_value = []
    boundary.get_all_pull_request_comments.return_value = []
    boundary.get_repository_sub_issues.return_value = []

    return boundary


@pytest.fixture
def boundary_with_large_dataset():
    """Boundary mock simulating large dataset with pagination."""
    from unittest.mock import Mock

    boundary = Mock()

    # Generate large datasets for pagination testing
    large_issues = [
        {
            "id": 2000 + i,
            "number": i + 1,
            "title": f"Issue {i + 1}",
            "body": f"Description for issue {i + 1}",
            "state": "open" if i % 3 != 0 else "closed",
            "labels": [{"name": "bug" if i % 2 == 0 else "enhancement"}],
            "user": {"login": "testuser", "id": 1},
            "assignees": [],
            "created_at": f"2024-01-{(i % 28) + 1:02d}T00:00:00Z",
            "updated_at": f"2024-01-{(i % 28) + 1:02d}T00:00:00Z",
            "closed_at": None,
            "html_url": f"https://github.com/owner/repo/issues/{i + 1}",
            "comments": 0,
        }
        for i in range(250)  # Large dataset requiring pagination
    ]

    boundary.get_repository_issues.return_value = large_issues
    boundary.get_repository_labels.return_value = [
        {"name": "bug", "color": "d73a4a", "id": 1001},
        {"name": "enhancement", "color": "a2eeef", "id": 1002},
    ]
    boundary.get_all_issue_comments.return_value = []
    boundary.get_repository_pull_requests.return_value = []
    boundary.get_all_pull_request_comments.return_value = []
    boundary.get_repository_sub_issues.return_value = []

    return boundary


@pytest.fixture
def boundary_with_pr_workflow_data(sample_pr_data):
    """Boundary mock configured for pull request workflow testing."""
    from unittest.mock import Mock

    boundary = Mock()

    # Configure PR-specific responses
    boundary.get_repository_pull_requests.return_value = sample_pr_data["pull_requests"]
    boundary.get_all_pull_request_comments.return_value = sample_pr_data["pr_comments"]

    # Add PR branch information
    def get_pr_commits(pr_number):
        return [
            {
                "sha": f"abc123{pr_number}",
                "message": f"Commit for PR #{pr_number}",
                "author": {"login": "developer"},
            }
        ]

    boundary.get_pull_request_commits.side_effect = get_pr_commits

    # Empty responses for non-PR data
    boundary.get_repository_labels.return_value = []
    boundary.get_repository_issues.return_value = []
    boundary.get_all_issue_comments.return_value = []
    boundary.get_repository_sub_issues.return_value = []

    return boundary


@pytest.fixture
def boundary_with_sub_issues_hierarchy(sample_sub_issues_data, complex_hierarchy_data):
    """Boundary mock configured for hierarchical sub-issue testing."""
    from unittest.mock import Mock

    boundary = Mock()

    # Combine sample and complex hierarchy data
    all_issues = sample_sub_issues_data["issues"] + complex_hierarchy_data["issues"]
    all_sub_issues = (
        sample_sub_issues_data["sub_issues"] + complex_hierarchy_data["sub_issues"]
    )

    boundary.get_repository_issues.return_value = all_issues
    boundary.get_repository_sub_issues.return_value = all_sub_issues

    # Empty responses for other endpoints
    boundary.get_repository_labels.return_value = []
    boundary.get_all_issue_comments.return_value = []
    boundary.get_repository_pull_requests.return_value = []
    boundary.get_all_pull_request_comments.return_value = []

    return boundary


# Error Simulation Fixtures


@pytest.fixture
def boundary_with_api_errors():
    """Boundary mock that simulates various GitHub API errors."""
    from requests.exceptions import ConnectionError, Timeout
    from unittest.mock import Mock

    boundary = Mock()

    # Configure different types of errors for different endpoints
    boundary.get_repository_labels.side_effect = ConnectionError("Network error")
    boundary.get_repository_issues.side_effect = Timeout("Request timeout")
    boundary.get_all_issue_comments.side_effect = Exception("API Error")
    boundary.get_repository_pull_requests.side_effect = Exception("Rate limit exceeded")
    boundary.get_all_pull_request_comments.return_value = []
    boundary.get_repository_sub_issues.return_value = []

    return boundary


@pytest.fixture
def boundary_with_partial_failures():
    """Boundary mock that simulates partial API failures."""
    from requests.exceptions import ConnectionError, Timeout
    from unittest.mock import Mock

    boundary = Mock()

    # Some endpoints work, others fail
    boundary.get_repository_labels.return_value = [
        {"name": "bug", "color": "d73a4a", "id": 1001}
    ]
    boundary.get_repository_issues.side_effect = ConnectionError("Network error")
    boundary.get_all_issue_comments.return_value = []
    boundary.get_repository_pull_requests.return_value = []
    boundary.get_all_pull_request_comments.side_effect = Timeout("Request timeout")
    boundary.get_repository_sub_issues.return_value = []

    return boundary


@pytest.fixture
def boundary_with_rate_limiting():
    """Boundary mock that simulates rate limiting scenarios."""
    from unittest.mock import Mock

    boundary = Mock()

    # First call succeeds, subsequent calls hit rate limit
    def rate_limited_response():
        if not hasattr(rate_limited_response, "call_count"):
            rate_limited_response.call_count = 0
        rate_limited_response.call_count += 1

        if rate_limited_response.call_count == 1:
            return []
        else:
            raise Exception("Rate limit exceeded, retry after 60 seconds")

    boundary.get_repository_labels.side_effect = rate_limited_response
    boundary.get_repository_issues.side_effect = rate_limited_response
    boundary.get_all_issue_comments.side_effect = rate_limited_response
    boundary.get_repository_pull_requests.side_effect = rate_limited_response
    boundary.get_all_pull_request_comments.side_effect = rate_limited_response
    boundary.get_repository_sub_issues.side_effect = rate_limited_response

    return boundary


# Workflow-Specific Service Configurations


@pytest.fixture
def backup_workflow_services(boundary_with_repository_data, temp_data_dir):
    """Pre-configured services for backup workflow testing."""
    from src.github.service import GitHubService
    from src.github.rate_limiter import RateLimitHandler
    from src.storage import create_storage_service

    # Configure GitHub service with realistic rate limiting
    rate_limiter = RateLimitHandler(max_retries=3, base_delay=0.1)
    github_service = GitHubService(boundary_with_repository_data, rate_limiter)

    # Configure storage service for temp directory
    storage_service = create_storage_service("json")
    storage_service._base_path = temp_data_dir

    return {
        "github": github_service,
        "storage": storage_service,
        "temp_dir": temp_data_dir,
    }


@pytest.fixture
def restore_workflow_services(
    boundary_with_empty_repository, temp_data_dir, sample_github_data
):
    """Pre-configured services for restore workflow testing."""
    from src.github.service import GitHubService
    from src.github.rate_limiter import RateLimitHandler
    from src.storage import create_storage_service
    import json
    import os

    # Configure GitHub service for restore operations
    rate_limiter = RateLimitHandler(max_retries=3, base_delay=0.1)
    github_service = GitHubService(boundary_with_empty_repository, rate_limiter)

    # Configure storage service and pre-populate with sample data
    storage_service = create_storage_service("json")
    storage_service._base_path = temp_data_dir

    # Write sample data files for restore testing
    data_files = {
        "labels.json": sample_github_data["labels"],
        "issues.json": sample_github_data["issues"],
        "comments.json": sample_github_data["comments"],
        "pull_requests.json": sample_github_data["pull_requests"],
        "pr_comments.json": sample_github_data["pr_comments"],
    }

    for filename, data in data_files.items():
        file_path = os.path.join(temp_data_dir, filename)
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

    return {
        "github": github_service,
        "storage": storage_service,
        "temp_dir": temp_data_dir,
        "data_files": list(data_files.keys()),
    }


@pytest.fixture
def sync_workflow_services(boundary_with_repository_data, temp_data_dir):
    """Pre-configured services for sync workflow testing."""
    from src.github.service import GitHubService
    from src.github.rate_limiter import RateLimitHandler
    from src.storage import create_storage_service

    # Configure GitHub service with aggressive rate limiting for sync scenarios
    rate_limiter = RateLimitHandler(max_retries=5, base_delay=0.05)
    github_service = GitHubService(boundary_with_repository_data, rate_limiter)

    # Configure storage service
    storage_service = create_storage_service("json")
    storage_service._base_path = temp_data_dir

    return {
        "github": github_service,
        "storage": storage_service,
        "temp_dir": temp_data_dir,
    }


@pytest.fixture
def error_handling_workflow_services(boundary_with_partial_failures, temp_data_dir):
    """Pre-configured services for error handling workflow testing."""
    from src.github.service import GitHubService
    from src.github.rate_limiter import RateLimitHandler
    from src.storage import create_storage_service

    # Configure GitHub service with minimal retry for fast error testing
    rate_limiter = RateLimitHandler(max_retries=1, base_delay=0.01)
    github_service = GitHubService(boundary_with_partial_failures, rate_limiter)

    # Configure storage service
    storage_service = create_storage_service("json")
    storage_service._base_path = temp_data_dir

    return {
        "github": github_service,
        "storage": storage_service,
        "temp_dir": temp_data_dir,
    }
