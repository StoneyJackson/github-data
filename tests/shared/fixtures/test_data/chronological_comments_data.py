"""Test data for chronological comment ordering scenarios."""

import pytest


@pytest.fixture
def chronological_comments_data():
    """Sample data with comments in reverse chronological order for testing sorting."""
    return {
        "labels": [
            {
                "name": "bug",
                "id": 1001,
                "color": "d73a4a",
                "description": "Something isn't working",
                "url": "https://api.github.com/repos/owner/repo/labels/bug",
            }
        ],
        "issues": [
            {
                "number": 1,
                "title": "Test issue",
                "id": 2001,
                "body": "Test issue body",
                "state": "open",
                "user": {
                    "login": "testuser",
                    "id": 1,
                    "avatar_url": "https://github.com/testuser.png",
                    "html_url": "https://github.com/testuser",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-10T10:00:00Z",
                "updated_at": "2023-01-10T10:00:00Z",
                "closed_at": None,
                "html_url": "https://github.com/owner/repo/issues/1",
                "comments": 3,
            }
        ],
        "comments": [
            # Comments in REVERSE chronological order (latest first)
            {
                "id": 4003,
                "body": "Third comment (latest)",
                "user": {
                    "login": "user3",
                    "id": 3003,
                    "avatar_url": "https://github.com/user3.png",
                    "html_url": "https://github.com/user3",
                },
                "created_at": "2023-01-10T14:00:00Z",  # Latest timestamp
                "updated_at": "2023-01-10T14:00:00Z",
                "html_url": "https://github.com/owner/repo/issues/1#issuecomment-4003",
                "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
            },
            {
                "id": 4002,
                "body": "Second comment (middle)",
                "user": {
                    "login": "user2",
                    "id": 3002,
                    "avatar_url": "https://github.com/user2.png",
                    "html_url": "https://github.com/user2",
                },
                "created_at": "2023-01-10T12:00:00Z",  # Middle timestamp
                "updated_at": "2023-01-10T12:00:00Z",
                "html_url": "https://github.com/owner/repo/issues/1#issuecomment-4002",
                "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
            },
            {
                "id": 4001,
                "body": "First comment (earliest)",
                "user": {
                    "login": "user1",
                    "id": 3001,
                    "avatar_url": "https://github.com/user1.png",
                    "html_url": "https://github.com/user1",
                },
                "created_at": "2023-01-10T11:00:00Z",  # Earliest timestamp
                "updated_at": "2023-01-10T11:00:00Z",
                "html_url": "https://github.com/owner/repo/issues/1#issuecomment-4001",
                "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
            },
        ],
        "pull_requests": [],
        "pr_comments": [],
        "pr_reviews": [],
        "pr_review_comments": [],
        "sub_issues": [],
    }