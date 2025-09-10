"""Tests for pull request filtering functionality."""

from unittest.mock import Mock, patch
import pytest

from src.github.boundary import GitHubApiBoundary

pytestmark = [pytest.mark.integration]


class TestPullRequestFiltering:
    """Test that pull requests are properly filtered out from issues."""

    @pytest.fixture
    def sample_issues_with_pr(self):
        """Sample GitHub API data with mixed issues and pull requests."""
        return [
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
                "labels": [],
                "created_at": "2023-01-15T10:30:00Z",
                "updated_at": "2023-01-15T14:20:00Z",
                "closed_at": None,
                "html_url": "https://github.com/owner/repo/issues/1",
                "comments": 0,
            },
            {
                "id": 2002,
                "number": 2,
                "title": "Add authentication feature",
                "body": "This PR adds authentication",
                "state": "open",
                "user": {
                    "login": "bob",
                    "id": 3002,
                    "avatar_url": "https://github.com/bob.png",
                    "html_url": "https://github.com/bob",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-16T10:30:00Z",
                "updated_at": "2023-01-16T14:20:00Z",
                "closed_at": None,
                "html_url": "https://github.com/owner/repo/pull/2",
                "comments": 0,
                "pull_request": {
                    "url": "https://api.github.com/repos/owner/repo/pulls/2",
                    "html_url": "https://github.com/owner/repo/pull/2",
                    "diff_url": "https://github.com/owner/repo/pull/2.diff",
                    "patch_url": "https://github.com/owner/repo/pull/2.patch",
                },
            },
            {
                "id": 2003,
                "number": 3,
                "title": "Another regular issue",
                "body": "This is a regular issue",
                "state": "closed",
                "user": {
                    "login": "charlie",
                    "id": 3003,
                    "avatar_url": "https://github.com/charlie.png",
                    "html_url": "https://github.com/charlie",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-17T10:30:00Z",
                "updated_at": "2023-01-17T14:20:00Z",
                "closed_at": "2023-01-17T14:20:00Z",
                "html_url": "https://github.com/owner/repo/issues/3",
                "comments": 1,
            },
        ]

    def test_filter_out_pull_requests_method(self, sample_issues_with_pr):
        """Test the _filter_out_pull_requests method directly."""
        boundary = GitHubApiBoundary("fake-token")
        filtered_issues = boundary._filter_out_pull_requests(sample_issues_with_pr)

        assert len(filtered_issues) == 2
        assert filtered_issues[0]["number"] == 1
        assert filtered_issues[1]["number"] == 3

        # Ensure no pull request made it through
        for issue in filtered_issues:
            assert "pull_request" not in issue or issue["pull_request"] is None

    @patch("src.github.boundary.Github")
    def test_get_repository_issues_filters_pull_requests(
        self, mock_github, sample_issues_with_pr
    ):
        """Test that get_repository_issues filters out pull requests."""
        # Setup mock
        mock_repo = Mock()
        mock_github.return_value.get_repo.return_value = mock_repo

        # Create mock issue objects with _rawData
        mock_issues = []
        for issue_data in sample_issues_with_pr:
            mock_issue = Mock()
            mock_issue._rawData = issue_data
            mock_issues.append(mock_issue)

        mock_repo.get_issues.return_value = mock_issues

        # Test the boundary
        boundary = GitHubApiBoundary("fake-token")
        result = boundary.get_repository_issues("owner/repo")

        # Should only return 2 issues (filtering out the pull request)
        assert len(result) == 2
        assert result[0]["number"] == 1
        assert result[1]["number"] == 3

        # Verify none of the returned items are pull requests
        for issue in result:
            assert "pull_request" not in issue or issue["pull_request"] is None

    @patch("src.github.boundary.Github")
    def test_get_all_issue_comments_skips_pull_request_comments(self, mock_github):
        """Test that get_all_issue_comments skips pull request comments."""
        # Setup mock repo
        mock_repo = Mock()
        mock_github.return_value.get_repo.return_value = mock_repo

        # Create mock issues: one regular issue, one pull request
        mock_regular_issue = Mock()
        mock_regular_issue._rawData = {"id": 1, "number": 1, "comments": 1}

        mock_pr_issue = Mock()
        mock_pr_issue._rawData = {
            "id": 2,
            "number": 2,
            "comments": 1,
            "pull_request": {"url": "https://api.github.com/repos/owner/repo/pulls/2"},
        }

        mock_repo.get_issues.return_value = [mock_regular_issue, mock_pr_issue]

        # Setup mock comments for the regular issue
        mock_comment = Mock()
        mock_comment._rawData = {
            "id": 1001,
            "body": "Regular comment",
            "user": {"login": "user1"},
            "created_at": "2023-01-15T10:30:00Z",
            "updated_at": "2023-01-15T10:30:00Z",
            "html_url": "https://github.com/owner/repo/issues/1#issuecomment-1001",
            "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
        }

        mock_regular_issue.get_comments.return_value = [mock_comment]
        mock_pr_issue.get_comments.return_value = [
            mock_comment
        ]  # This should not be called

        # Test the boundary
        boundary = GitHubApiBoundary("fake-token")
        result = boundary.get_all_issue_comments("owner/repo")

        # Should only have comments from regular issues
        assert len(result) == 1
        assert result[0]["id"] == 1001

        # Verify PR comments were not retrieved
        mock_regular_issue.get_comments.assert_called_once()
        mock_pr_issue.get_comments.assert_not_called()
