"""Test data for mixed repository states scenarios."""

import pytest


@pytest.fixture
def existing_repository_data():
    """Sample data for repository with existing issues and labels."""
    return {
        "labels": [
            {
                "name": "bug",
                "color": "d73a4a",
                "description": "Bug report",
                "url": "https://api.github.com/repos/owner/repo/labels/bug",
                "id": 1001,
            }
        ],
        "issues": [
            {
                "id": 5001,
                "number": 50,
                "title": "Existing Issue",
                "body": "An existing issue",
                "state": "OPEN",
                "user": {
                    "login": "existing",
                    "id": 9001,
                    "avatar_url": "https://github.com/existing.png",
                    "html_url": "https://github.com/existing",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-01T10:00:00Z",
                "updated_at": "2023-01-01T16:00:00Z",
                "closed_at": None,
                "html_url": "https://github.com/owner/repo/issues/50",
                "comments": 0,
            }
        ],
        "comments": [],
        "pull_requests": [],
        "pr_comments": [],
        "pr_reviews": [],
        "pr_review_comments": [],
        "sub_issues": [],
    }
