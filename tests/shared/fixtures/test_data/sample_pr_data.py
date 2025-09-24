"""Sample pull request data fixture for testing."""

import pytest


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
