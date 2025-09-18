"""
Tests for metadata formatting functionality.

Tests the metadata formatting utilities that preserve original
author and timestamp information in restored issues and comments.
"""

import pytest
from datetime import datetime

from src.github.metadata import (
    add_issue_metadata_footer,
    add_comment_metadata_footer,
    _format_datetime,
)
from src.entities import Issue, Comment, GitHubUser


class TestMetadataFormatting:
    """Test metadata formatting functions."""

    @pytest.fixture
    def sample_user(self):
        """Create a sample GitHub user."""
        return GitHubUser(
            login="alice",
            id=3001,
            avatar_url="https://github.com/alice.png",
            html_url="https://github.com/alice",
        )

    @pytest.fixture
    def sample_issue_with_body(self, sample_user):
        """Create a sample issue with body text."""
        return Issue(
            id=1001,
            number=1,
            title="Sample issue",
            body="This is the original issue body.",
            state="open",
            user=sample_user,
            created_at=datetime(2023, 1, 15, 10, 30, 0),
            updated_at=datetime(2023, 1, 15, 14, 20, 0),
            html_url="https://github.com/owner/repo/issues/1",
            comments_count=0,
        )

    @pytest.fixture
    def sample_issue_without_body(self, sample_user):
        """Create a sample issue without body text."""
        return Issue(
            id=1002,
            number=2,
            title="Issue without body",
            body=None,
            state="open",
            user=sample_user,
            created_at=datetime(2023, 1, 15, 10, 30, 0),
            updated_at=datetime(2023, 1, 15, 10, 30, 0),
            html_url="https://github.com/owner/repo/issues/2",
            comments_count=0,
        )

    @pytest.fixture
    def sample_closed_issue(self, sample_user):
        """Create a sample closed issue."""
        return Issue(
            id=1003,
            number=3,
            title="Closed issue",
            body="This issue was closed.",
            state="closed",
            user=sample_user,
            created_at=datetime(2023, 1, 15, 10, 30, 0),
            updated_at=datetime(2023, 1, 15, 14, 20, 0),
            closed_at=datetime(2023, 1, 15, 16, 45, 0),
            html_url="https://github.com/owner/repo/issues/3",
            comments_count=0,
        )

    @pytest.fixture
    def sample_comment(self, sample_user):
        """Create a sample comment."""
        return Comment(
            id=4001,
            body="This is a comment body.",
            user=sample_user,
            created_at=datetime(2023, 1, 15, 12, 0, 0),
            updated_at=datetime(2023, 1, 15, 13, 30, 0),
            html_url="https://github.com/owner/repo/issues/1#issuecomment-4001",
            issue_url="https://api.github.com/repos/owner/repo/issues/1",
        )

    def test_add_issue_metadata_footer_with_body(self, sample_issue_with_body):
        """Test adding metadata footer to issue with existing body."""
        result = add_issue_metadata_footer(sample_issue_with_body)

        assert "This is the original issue body." in result
        assert "---" in result
        assert "*Originally created by @alice on 2023-01-15 10:30:00 UTC*" in result
        assert "*Last updated on 2023-01-15 14:20:00 UTC*" in result

        # Check that original body comes before metadata
        lines = result.split("\n")
        original_body_line = next(
            i for i, line in enumerate(lines) if "original issue body" in line
        )
        metadata_start_line = next(i for i, line in enumerate(lines) if line == "---")
        assert original_body_line < metadata_start_line

    def test_add_issue_metadata_footer_without_body(self, sample_issue_without_body):
        """Test adding metadata footer to issue without existing body."""
        result = add_issue_metadata_footer(sample_issue_without_body)

        assert result.startswith("---")
        assert "*Originally created by @alice on 2023-01-15 10:30:00 UTC*" in result
        # Should not show update time when same as creation time
        assert "*Last updated on" not in result

    def test_add_issue_metadata_footer_closed_issue(self, sample_closed_issue):
        """Test adding metadata footer to closed issue."""
        result = add_issue_metadata_footer(sample_closed_issue)

        assert "*Originally created by @alice on 2023-01-15 10:30:00 UTC*" in result
        assert "*Last updated on 2023-01-15 14:20:00 UTC*" in result
        assert "*Closed on 2023-01-15 16:45:00 UTC*" in result

    def test_add_comment_metadata_footer(self, sample_comment):
        """Test adding metadata footer to comment."""
        result = add_comment_metadata_footer(sample_comment)

        assert "This is a comment body." in result
        assert "---" in result
        assert "*Originally posted by @alice on 2023-01-15 12:00:00 UTC*" in result
        assert "*Last updated on 2023-01-15 13:30:00 UTC*" in result

        # Check that original body comes before metadata
        lines = result.split("\n")
        original_body_line = next(
            i for i, line in enumerate(lines) if "comment body" in line
        )
        metadata_start_line = next(i for i, line in enumerate(lines) if line == "---")
        assert original_body_line < metadata_start_line

    def test_format_datetime(self):
        """Test datetime formatting."""
        dt = datetime(2023, 1, 15, 10, 30, 45)
        result = _format_datetime(dt)
        assert result == "2023-01-15 10:30:45 UTC"

    def test_issue_same_created_updated_time(self, sample_user):
        """Test issue with same creation and update time."""
        issue = Issue(
            id=1004,
            number=4,
            title="Same times",
            body="Test body",
            state="open",
            user=sample_user,
            created_at=datetime(2023, 1, 15, 10, 30, 0),
            updated_at=datetime(2023, 1, 15, 10, 30, 0),
            html_url="https://github.com/owner/repo/issues/4",
            comments_count=0,
        )

        result = add_issue_metadata_footer(issue)
        assert "*Originally created by @alice on 2023-01-15 10:30:00 UTC*" in result
        assert "*Last updated on" not in result

    def test_comment_same_created_updated_time(self, sample_user):
        """Test comment with same creation and update time."""
        comment = Comment(
            id=4002,
            body="Test comment",
            user=sample_user,
            created_at=datetime(2023, 1, 15, 12, 0, 0),
            updated_at=datetime(2023, 1, 15, 12, 0, 0),
            html_url="https://github.com/owner/repo/issues/1#issuecomment-4002",
            issue_url="https://api.github.com/repos/owner/repo/issues/1",
        )

        result = add_comment_metadata_footer(comment)
        assert "*Originally posted by @alice on 2023-01-15 12:00:00 UTC*" in result
        assert "*Last updated on" not in result


class TestMetadataIntegration:
    """Test metadata integration with restore operations."""

    def test_restore_creates_issues_and_comments_successfully(self, tmp_path):
        """Test that restore operations work with our new metadata functionality."""
        from unittest.mock import MagicMock
        from src.operations.restore import restore_repository_data_with_services
        from src.storage import create_storage_service
        import json

        # Create test data directory
        data_dir = tmp_path / "test_data"
        data_dir.mkdir()

        # Create minimal test data files
        issues_data = [
            {
                "id": 1001,
                "number": 1,
                "title": "Test issue with metadata",
                "body": "Original issue content",
                "state": "open",
                "user": {
                    "login": "original_author",
                    "id": 123,
                    "avatar_url": "https://github.com/original_author.png",
                    "html_url": "https://github.com/original_author",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-15T10:30:00Z",
                "updated_at": "2023-01-15T14:20:00Z",
                "closed_at": None,
                "html_url": "https://github.com/owner/repo/issues/1",
                "comments": 0,
            }
        ]

        comments_data = [
            {
                "id": 4001,
                "body": "Original comment content",
                "user": {
                    "login": "comment_author",
                    "id": 456,
                    "avatar_url": "https://github.com/comment_author.png",
                    "html_url": "https://github.com/comment_author",
                },
                "created_at": "2023-01-15T12:00:00Z",
                "updated_at": "2023-01-15T13:30:00Z",
                "html_url": "https://github.com/owner/repo/issues/1#issuecomment-4001",
                "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
            }
        ]

        # Write test files
        with open(data_dir / "labels.json", "w") as f:
            json.dump([], f)
        with open(data_dir / "issues.json", "w") as f:
            json.dump(issues_data, f)
        with open(data_dir / "comments.json", "w") as f:
            json.dump(comments_data, f)

        # Create a mock GitHubService to capture what gets sent to API
        mock_client = MagicMock()
        mock_client.get_repository_labels.return_value = []

        # Set up return values for issue creation
        mock_client.create_issue.return_value = {
            "number": 10,
            "title": "Test issue with metadata",
        }

        # Set up return values for comment creation
        mock_client.create_issue_comment.return_value = MagicMock()

        # Run restore with metadata enabled (default)
        storage_service = create_storage_service("json")
        restore_repository_data_with_services(
            mock_client, storage_service, "owner/repo", str(data_dir)
        )

        # Verify issue was created
        assert mock_client.create_issue.call_count == 1

        # Verify comment was created
        assert mock_client.create_issue_comment.call_count == 1

    def test_metadata_functionality_works_end_to_end(self):
        """Test that our metadata functions produce the expected output."""
        from datetime import datetime
        from src.entities import Issue, Comment, GitHubUser
        from src.github.metadata import (
            add_issue_metadata_footer,
            add_comment_metadata_footer,
        )

        # Create test data
        user = GitHubUser(
            login="testuser",
            id=123,
            avatar_url="https://github.com/testuser.png",
            html_url="https://github.com/testuser",
        )

        issue = Issue(
            id=1001,
            number=1,
            title="Test Issue",
            body="Original issue body",
            state="open",
            user=user,
            created_at=datetime(2023, 1, 15, 10, 30, 0),
            updated_at=datetime(2023, 1, 15, 14, 20, 0),
            html_url="https://github.com/owner/repo/issues/1",
            comments_count=0,
        )

        comment = Comment(
            id=4001,
            body="Original comment body",
            user=user,
            created_at=datetime(2023, 1, 15, 12, 0, 0),
            updated_at=datetime(2023, 1, 15, 13, 30, 0),
            html_url="https://github.com/owner/repo/issues/1#issuecomment-4001",
            issue_url="https://api.github.com/repos/owner/repo/issues/1",
        )

        # Test issue metadata
        issue_with_metadata = add_issue_metadata_footer(issue)
        assert "Original issue body" in issue_with_metadata
        assert (
            "*Originally created by @testuser on 2023-01-15 10:30:00 UTC*"
            in issue_with_metadata
        )
        assert "*Last updated on 2023-01-15 14:20:00 UTC*" in issue_with_metadata

        # Test comment metadata
        comment_with_metadata = add_comment_metadata_footer(comment)
        assert "Original comment body" in comment_with_metadata
        assert (
            "*Originally posted by @testuser on 2023-01-15 12:00:00 UTC*"
            in comment_with_metadata
        )
        assert "*Last updated on 2023-01-15 13:30:00 UTC*" in comment_with_metadata
