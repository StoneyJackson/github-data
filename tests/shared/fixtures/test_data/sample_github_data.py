"""Sample GitHub API data fixture for testing."""

import pytest


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