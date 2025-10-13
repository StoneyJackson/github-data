"""Test data for orphaned sub-issues scenarios."""

import pytest


@pytest.fixture
def orphaned_sub_issues_data():
    """Sample data with orphaned sub-issues (parent missing)."""
    return {
        "labels": [],
        "issues": [
            {
                "id": 3002,
                "number": 2,
                "title": "Orphaned Sub-issue",
                "body": "This sub-issue has no parent",
                "state": "OPEN",
                "user": {
                    "login": "orphan",
                    "id": 9999,
                    "avatar_url": "https://github.com/orphan.png",
                    "html_url": "https://github.com/orphan",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-11T10:00:00Z",
                "updated_at": "2023-01-16T16:00:00Z",
                "closed_at": None,
                "html_url": "https://github.com/owner/repo/issues/2",
                "comments": 0,
            }
        ],
        "comments": [],
        "pull_requests": [],
        "pr_comments": [],
        "pr_reviews": [],
        "pr_review_comments": [],
        "sub_issues": [
            {
                "sub_issue_id": 3002,
                "sub_issue_number": 2,
                "parent_issue_id": 9999,  # Parent doesn't exist
                "parent_issue_number": 999,
                "position": 1,
            }
        ],
    }


@pytest.fixture
def regular_issue_data():
    """Sample data with a regular issue (no sub-issues)."""
    return {
        "labels": [],
        "issues": [
            {
                "id": 4001,
                "number": 1,
                "title": "Regular Issue",
                "body": "Just a regular issue",
                "state": "OPEN",
                "user": {
                    "login": "regular",
                    "id": 4001,
                    "avatar_url": "https://github.com/regular.png",
                    "html_url": "https://github.com/regular",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-10T10:00:00Z",
                "updated_at": "2023-01-15T16:00:00Z",
                "closed_at": None,
                "html_url": "https://github.com/owner/repo/issues/1",
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