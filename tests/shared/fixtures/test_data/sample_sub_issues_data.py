"""Sample sub-issues data fixture for testing."""

import pytest


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