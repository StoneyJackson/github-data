"""GitHub service mock fixture for testing."""

import pytest


@pytest.fixture
def github_service_mock():
    """Mock GitHub service for testing."""
    from unittest.mock import Mock

    service = Mock()
    
    # Mock the required service methods with proper data structure
    service.get_repository_labels.return_value = [
        {
            "name": "bug",
            "color": "d73a4a", 
            "description": "Bug reports",
            "url": "https://api.github.com/repos/owner/repo/labels/bug",
            "id": 101,
        }
    ]
    
    service.get_repository_issues.return_value = [
        {
            "id": 789,
            "number": 1,
            "title": "Test Issue",
            "body": "Test issue body",
            "state": "open",
            "user": {
                "login": "testuser",
                "id": 456,
                "avatar_url": "https://avatars.githubusercontent.com/u/456",
                "html_url": "https://github.com/testuser",
            },
            "assignees": [],
            "labels": [
                {
                    "name": "bug",
                    "color": "d73a4a",
                    "description": "Bug reports",
                    "url": "https://api.github.com/repos/owner/repo/labels/bug",
                    "id": 101,
                }
            ],
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "closed_at": None,
            "html_url": "https://github.com/owner/repo/issues/1",
            "comments": 1,
        }
    ]
    
    service.get_all_issue_comments.return_value = [
        {
            "id": 123,
            "body": "Test comment",
            "user": {
                "login": "testuser",
                "id": 456,
                "avatar_url": "https://avatars.githubusercontent.com/u/456",
                "html_url": "https://github.com/testuser",
            },
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "html_url": "https://github.com/owner/repo/issues/1#issuecomment-123",
            "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
        }
    ]
    
    return service
