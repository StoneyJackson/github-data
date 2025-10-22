"""Shared test fixtures for milestone testing.

Provides reusable milestone and strategy fixtures, sample milestone data builders,
milestone-enabled repository fixtures, issue/PR with milestone associations,
and mock GitHub API responses with milestones.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import json

from src.entities.milestones.models import Milestone
from src.operations.save.strategies.milestones_strategy import MilestonesSaveStrategy
from src.operations.restore.strategies.milestones_strategy import (
    MilestonesRestoreStrategy,
)
from src.github.service import GitHubService
from src.config.settings import ApplicationConfig


# Core Milestone Fixtures


@pytest.fixture
def sample_milestone_data():
    """Create comprehensive sample milestone data for testing."""
    return {
        "id": "M_kwDOABCDEF123",
        "number": 1,
        "title": "Version 1.0",
        "description": "First major release milestone",
        "state": "open",
        "creator_login": "testuser",
        "creator_id": "U_123456",
        "created_at": datetime(2023, 1, 1, tzinfo=timezone.utc),
        "updated_at": datetime(2023, 1, 2, tzinfo=timezone.utc),
        "due_on": datetime(2023, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
        "closed_at": None,
        "open_issues": 5,
        "closed_issues": 0,
        "url": "https://github.com/test-owner/test-repo/milestone/1",
    }


@pytest.fixture
def sample_closed_milestone_data():
    """Create sample closed milestone data for testing."""
    return {
        "id": "M_kwDOABCDEF456",
        "number": 2,
        "title": "Version 1.1",
        "description": "Bug fix release milestone",
        "state": "closed",
        "creator_login": "testuser",
        "creator_id": "U_123456",
        "created_at": datetime(2023, 2, 1, tzinfo=timezone.utc),
        "updated_at": datetime(2023, 2, 15, tzinfo=timezone.utc),
        "due_on": datetime(2023, 3, 31, tzinfo=timezone.utc),
        "closed_at": datetime(2023, 2, 15, tzinfo=timezone.utc),
        "open_issues": 0,
        "closed_issues": 8,
        "url": "https://github.com/test-owner/test-repo/milestone/2",
    }


@pytest.fixture
def sample_milestone(sample_milestone_data):
    """Create a sample Milestone entity for testing."""
    return Milestone(**sample_milestone_data)


@pytest.fixture
def sample_closed_milestone(sample_closed_milestone_data):
    """Create a sample closed Milestone entity for testing."""
    return Milestone(**sample_closed_milestone_data)


@pytest.fixture
def multiple_milestones(sample_milestone_data, sample_closed_milestone_data):
    """Create multiple milestone entities for comprehensive testing."""
    # Create additional milestone variations
    milestone_3_data = sample_milestone_data.copy()
    milestone_3_data.update(
        {
            "id": "M_kwDOABCDEF789",
            "number": 3,
            "title": "Version 2.0",
            "description": "Major feature release",
            "due_on": None,  # No due date
            "open_issues": 12,
            "closed_issues": 3,
        }
    )

    milestone_4_data = sample_milestone_data.copy()
    milestone_4_data.update(
        {
            "id": "M_kwDOABCDEF101",
            "number": 4,
            "title": "Hotfix Release",
            "description": None,  # No description
            "state": "closed",
            "closed_at": datetime(2023, 1, 15, tzinfo=timezone.utc),
            "open_issues": 0,
            "closed_issues": 2,
        }
    )

    return [
        Milestone(**sample_milestone_data),
        Milestone(**sample_closed_milestone_data),
        Milestone(**milestone_3_data),
        Milestone(**milestone_4_data),
    ]


# Data Builder Fixtures


class MilestoneDataBuilder:
    """Builder class for creating custom milestone data."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset to default values."""
        self._data = {
            "id": "M_kwDOBuilder001",
            "number": 1,
            "title": "Builder Milestone",
            "description": "Created by MilestoneDataBuilder",
            "state": "open",
            "creator_login": "builderuser",
            "creator_id": "U_builder",
            "created_at": datetime(2023, 1, 1, tzinfo=timezone.utc),
            "updated_at": datetime(2023, 1, 1, tzinfo=timezone.utc),
            "due_on": None,
            "closed_at": None,
            "open_issues": 0,
            "closed_issues": 0,
            "url": "https://github.com/builder/repo/milestone/1",
        }
        return self

    def with_id(self, milestone_id: str):
        """Set milestone ID."""
        self._data["id"] = milestone_id
        return self

    def with_number(self, number: int):
        """Set milestone number."""
        self._data["number"] = number
        return self

    def with_title(self, title: str):
        """Set milestone title."""
        self._data["title"] = title
        return self

    def with_description(self, description: Optional[str]):
        """Set milestone description."""
        self._data["description"] = description
        return self

    def with_state(self, state: str):
        """Set milestone state."""
        self._data["state"] = state
        if state == "closed" and self._data["closed_at"] is None:
            self._data["closed_at"] = self._data["updated_at"]
        elif state == "open":
            self._data["closed_at"] = None
        return self

    def with_creator(self, login: str, user_id: str):
        """Set milestone creator."""
        self._data["creator_login"] = login
        self._data["creator_id"] = user_id
        return self

    def with_dates(
        self,
        created_at: datetime,
        updated_at: Optional[datetime] = None,
        due_on: Optional[datetime] = None,
        closed_at: Optional[datetime] = None,
    ):
        """Set milestone dates."""
        self._data["created_at"] = created_at
        self._data["updated_at"] = updated_at or created_at
        self._data["due_on"] = due_on
        self._data["closed_at"] = closed_at
        return self

    def with_issue_counts(self, open_issues: int, closed_issues: int):
        """Set issue counts."""
        self._data["open_issues"] = open_issues
        self._data["closed_issues"] = closed_issues
        return self

    def with_url(self, url: str):
        """Set milestone URL."""
        self._data["url"] = url
        return self

    def build_data(self) -> Dict[str, Any]:
        """Build and return milestone data dictionary."""
        return self._data.copy()

    def build(self) -> Milestone:
        """Build and return Milestone entity."""
        return Milestone(**self._data)


@pytest.fixture
def milestone_builder():
    """Provide a MilestoneDataBuilder for creating custom milestone data."""
    return MilestoneDataBuilder()


@pytest.fixture
def bulk_milestone_builder():
    """Create a fixture for building multiple milestones."""

    def _build_milestones(count: int, prefix: str = "Bulk") -> List[Milestone]:
        """Build multiple milestones with variations."""
        milestones = []
        builder = MilestoneDataBuilder()

        for i in range(count):
            milestone = (
                builder.reset()
                .with_id(f"M_bulk_{prefix}_{i:03d}")
                .with_number(i + 1)
                .with_title(f"{prefix} Milestone {i + 1}")
                .with_description(f"Description for {prefix} milestone {i + 1}")
                .with_state("open" if i % 2 == 0 else "closed")
                .with_creator(f"user{i % 10}", f"U_{i:06d}")
                .with_dates(
                    created_at=datetime(2023, (i % 12) + 1, 1, tzinfo=timezone.utc),
                    updated_at=datetime(2023, (i % 12) + 1, 2, tzinfo=timezone.utc),
                    due_on=(
                        datetime(2023, (i % 12) + 1, 28, tzinfo=timezone.utc)
                        if i % 4 == 0
                        else None
                    ),
                )
                .with_issue_counts(i * 2, i)
                .with_url(f"https://github.com/bulk/repo/milestone/{i + 1}")
                .build()
            )
            milestones.append(milestone)

        return milestones

    return _build_milestones


# Mock Service Fixtures


@pytest.fixture
def mock_milestone_config():
    """Create a mock configuration with milestones enabled."""
    config = Mock(spec=ApplicationConfig)
    config.include_milestones = True
    config.repository_owner = "test-owner"
    config.repository_name = "test-repo"
    config.data_path = "/tmp/test-data"
    return config


@pytest.fixture
def mock_github_service():
    """Create a mock GitHub service with milestone methods."""
    service = Mock(spec=GitHubService)
    service.get_milestones = AsyncMock()
    service.create_milestone = AsyncMock()
    service.update_milestone = AsyncMock()
    service.close_milestone = AsyncMock()
    service.reopen_milestone = AsyncMock()
    return service


@pytest.fixture
def mock_storage_service():
    """Create a mock storage service for milestone operations."""
    storage = Mock()
    storage.write = Mock()
    storage.read = Mock()
    storage.file_exists = Mock()
    storage.ensure_directory = Mock()
    return storage


@pytest.fixture
def milestone_save_strategy():
    """Create a milestone save strategy."""
    return MilestonesSaveStrategy()


@pytest.fixture
def milestone_restore_strategy():
    """Create a milestone restore strategy."""
    return MilestonesRestoreStrategy()


# Repository and Context Fixtures


@pytest.fixture
def milestone_enabled_repository_context():
    """Create repository context with milestone functionality enabled."""
    return {
        "owner": "test-owner",
        "name": "test-repo",
        "include_milestones": True,
        "milestone_mapping": {},
        "created_milestones": [],
        "milestone_errors": [],
    }


@pytest.fixture
def milestone_mapping_context():
    """Create milestone mapping context for restore operations."""
    return {
        "original_to_new": {
            1: 10,  # Original milestone 1 maps to new milestone 10
            2: 11,  # Original milestone 2 maps to new milestone 11
            3: 12,  # Original milestone 3 maps to new milestone 12
        },
        "new_to_original": {10: 1, 11: 2, 12: 3},
        "title_mapping": {"Version 1.0": 10, "Version 1.1": 11, "Version 2.0": 12},
    }


# Issue and PR with Milestone Fixtures


@pytest.fixture
def issue_with_milestone_data():
    """Create sample issue data with milestone association."""
    return {
        "id": "I_kwDOIssue001",
        "number": 1,
        "title": "Test Issue with Milestone",
        "body": "This issue is associated with a milestone",
        "state": "open",
        "milestone": {"number": 1},
        "created_at": "2023-01-05T10:00:00Z",
        "updated_at": "2023-01-05T11:00:00Z",
        "author": {"login": "issueuser", "id": "U_issue123"},
        "labels": [],
        "url": "https://github.com/test-owner/test-repo/issues/1",
    }


@pytest.fixture
def pr_with_milestone_data():
    """Create sample PR data with milestone association."""
    return {
        "id": "PR_kwDOPR001",
        "number": 1,
        "title": "Test PR with Milestone",
        "body": "This PR is associated with a milestone",
        "state": "open",
        "milestone": {"number": 1},
        "created_at": "2023-01-06T10:00:00Z",
        "updated_at": "2023-01-06T11:00:00Z",
        "author": {"login": "pruser", "id": "U_pr123"},
        "labels": [],
        "head_ref_name": "feature-branch",
        "base_ref_name": "main",
        "merged": False,
        "merged_at": None,
        "mergeable": "MERGEABLE",
        "url": "https://github.com/test-owner/test-repo/pull/1",
    }


@pytest.fixture
def multiple_issues_with_milestones():
    """Create multiple issues with different milestone associations."""
    return [
        {
            "id": "I_kwDOIssue001",
            "number": 1,
            "title": "Issue for Milestone 1",
            "milestone": {"number": 1},
            "state": "open",
        },
        {
            "id": "I_kwDOIssue002",
            "number": 2,
            "title": "Issue for Milestone 2",
            "milestone": {"number": 2},
            "state": "closed",
        },
        {
            "id": "I_kwDOIssue003",
            "number": 3,
            "title": "Issue without Milestone",
            "milestone": None,
            "state": "open",
        },
    ]


@pytest.fixture
def multiple_prs_with_milestones():
    """Create multiple PRs with different milestone associations."""
    return [
        {
            "id": "PR_kwDOPR001",
            "number": 1,
            "title": "PR for Milestone 1",
            "milestone": {"number": 1},
            "state": "open",
        },
        {
            "id": "PR_kwDOPR002",
            "number": 2,
            "title": "PR for Milestone 2",
            "milestone": {"number": 2},
            "state": "merged",
        },
        {
            "id": "PR_kwDOPR003",
            "number": 3,
            "title": "PR without Milestone",
            "milestone": None,
            "state": "open",
        },
    ]


# GitHub API Mock Response Fixtures


@pytest.fixture
def mock_github_milestone_response():
    """Create mock GitHub API response for milestone data."""
    return {
        "id": "M_kwDOABCDEF123",
        "number": 1,
        "title": "Version 1.0",
        "description": "First major release",
        "state": "OPEN",
        "creator": {
            "login": "testuser",
            "id": "U_123456",
            "avatar_url": "https://github.com/images/testuser.jpg",
            "html_url": "https://github.com/testuser",
            "type": "User",
        },
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-02T00:00:00Z",
        "due_on": "2023-12-31T23:59:59Z",
        "closed_at": None,
        "issues": {"total_count": 5},
        "pull_requests": {"total_count": 2},
        "url": "https://github.com/test-owner/test-repo/milestone/1",
    }


@pytest.fixture
def mock_graphql_milestone_response():
    """Create mock GraphQL response for milestone data."""
    return {
        "repository": {
            "milestones": {
                "pageInfo": {"hasNextPage": False, "endCursor": None},
                "nodes": [
                    {
                        "id": "M_kwDOABCDEF123",
                        "number": 1,
                        "title": "Version 1.0",
                        "description": "First major release",
                        "state": "OPEN",
                        "creator": {
                            "login": "testuser",
                            "id": "U_123456",
                            "avatarUrl": "https://github.com/images/testuser.jpg",
                            "htmlUrl": "https://github.com/testuser",
                            "type": "User",
                        },
                        "createdAt": "2023-01-01T00:00:00Z",
                        "updatedAt": "2023-01-02T00:00:00Z",
                        "dueOn": "2023-12-31T23:59:59Z",
                        "closedAt": None,
                        "issues": {"totalCount": 5},
                        "pullRequests": {"totalCount": 2},
                        "url": "https://github.com/test-owner/test-repo/milestone/1",
                    }
                ],
            }
        }
    }


# File System and Data Fixtures


@pytest.fixture
def milestone_test_data_directory(tmp_path):
    """Create a temporary directory with milestone test data."""
    milestone_dir = tmp_path / "milestone_test_data"
    milestone_dir.mkdir()

    # Create sample milestone data file
    milestone_data = [
        {
            "id": "M_test_001",
            "number": 1,
            "title": "Test Milestone 1",
            "description": "First test milestone",
            "state": "open",
            "creator_login": "testuser",
            "creator_id": "U_test",
            "created_at": "2023-01-01T00:00:00+00:00",
            "updated_at": "2023-01-01T00:00:00+00:00",
            "due_on": None,
            "closed_at": None,
            "open_issues": 3,
            "closed_issues": 0,
            "url": "https://github.com/test/repo/milestone/1",
        }
    ]

    milestone_file = milestone_dir / "milestones.json"
    with open(milestone_file, "w") as f:
        json.dump(milestone_data, f, indent=2)

    return milestone_dir


@pytest.fixture
def complex_milestone_dataset():
    """Create a complex milestone dataset for comprehensive testing."""
    return {
        "milestones": [
            {
                "id": "M_complex_001",
                "number": 1,
                "title": "🚀 Version 1.0",
                "description": "First major release with emoji support",
                "state": "open",
                "creator_login": "lead_dev",
                "creator_id": "U_lead",
                "created_at": "2023-01-01T00:00:00+00:00",
                "updated_at": "2023-01-15T00:00:00+00:00",
                "due_on": "2023-06-30T23:59:59+00:00",
                "closed_at": None,
                "open_issues": 15,
                "closed_issues": 5,
                "url": "https://github.com/complex/repo/milestone/1",
            },
            {
                "id": "M_complex_002",
                "number": 2,
                "title": "Bug Fixes",
                "description": None,
                "state": "closed",
                "creator_login": "qa_lead",
                "creator_id": "U_qa",
                "created_at": "2023-02-01T00:00:00+00:00",
                "updated_at": "2023-02-28T00:00:00+00:00",
                "due_on": "2023-02-28T23:59:59+00:00",
                "closed_at": "2023-02-28T18:00:00+00:00",
                "open_issues": 0,
                "closed_issues": 12,
                "url": "https://github.com/complex/repo/milestone/2",
            },
        ],
        "issues": [
            {
                "id": "I_complex_001",
                "number": 1,
                "title": "Implement user authentication",
                "milestone": {"number": 1},
                "state": "open",
            },
            {
                "id": "I_complex_002",
                "number": 2,
                "title": "Fix login bug",
                "milestone": {"number": 2},
                "state": "closed",
            },
        ],
        "pull_requests": [
            {
                "id": "PR_complex_001",
                "number": 1,
                "title": "Add authentication system",
                "milestone": {"number": 1},
                "state": "open",
            }
        ],
    }


# Error Simulation Fixtures


@pytest.fixture
def milestone_error_scenarios():
    """Provide various error scenarios for milestone testing."""
    return {
        "api_errors": {
            "rate_limit": {"status": 403, "message": "API rate limit exceeded"},
            "unauthorized": {"status": 401, "message": "Bad credentials"},
            "not_found": {"status": 404, "message": "Repository not found"},
            "server_error": {"status": 500, "message": "Internal server error"},
            "conflict": {"status": 422, "message": "Milestone already exists"},
        },
        "data_errors": {
            "invalid_json": '{"invalid": json content}',
            "missing_fields": {"number": 1, "title": "Missing ID"},
            "wrong_types": {"id": 123, "number": "not_a_number", "title": None},
            "invalid_dates": {"created_at": "not_a_date", "updated_at": 12345},
        },
        "network_errors": {
            "timeout": "Request timeout",
            "connection_error": "Connection failed",
            "dns_error": "DNS resolution failed",
        },
    }


# Performance Testing Fixtures


@pytest.fixture
def large_milestone_dataset():
    """Create a large milestone dataset for performance testing."""

    def _create_dataset(size: int) -> List[Dict[str, Any]]:
        """Create a dataset of specified size."""
        dataset = []
        builder = MilestoneDataBuilder()

        for i in range(size):
            milestone_data = (
                builder.reset()
                .with_id(f"M_perf_{i:04d}")
                .with_number(i + 1)
                .with_title(f"Performance Test Milestone {i + 1}")
                .with_description(f"Performance test description {i + 1}" * 10)
                .with_state("open" if i % 3 != 0 else "closed")
                .with_creator(f"perfuser{i % 20}", f"U_perf_{i:06d}")
                .with_dates(
                    created_at=datetime(2023, (i % 12) + 1, 1, tzinfo=timezone.utc),
                    updated_at=datetime(2023, (i % 12) + 1, 2, tzinfo=timezone.utc),
                )
                .with_issue_counts(i % 50, i % 25)
                .build_data()
            )
            dataset.append(milestone_data)

        return dataset

    return _create_dataset


# Integration Test Fixtures


@pytest.fixture
def milestone_integration_context():
    """Provide context for milestone integration testing."""
    return {
        "test_repositories": [
            {"owner": "test-org", "name": "test-repo-1"},
            {"owner": "test-org", "name": "test-repo-2"},
        ],
        "test_milestones": [
            {"title": "Integration Test 1", "state": "open"},
            {"title": "Integration Test 2", "state": "closed"},
        ],
        "test_issues": [
            {"title": "Test Issue 1", "milestone_number": 1},
            {"title": "Test Issue 2", "milestone_number": 2},
        ],
        "test_prs": [
            {"title": "Test PR 1", "milestone_number": 1},
            {"title": "Test PR 2", "milestone_number": None},
        ],
    }
