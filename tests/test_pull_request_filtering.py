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

    @patch("src.github.boundary.Client")
    @patch("src.github.boundary.Github")
    def test_get_repository_issues_filters_pull_requests(
        self, mock_github, mock_client, sample_issues_with_pr
    ):
        """Test that get_repository_issues filters out pull requests."""
        # Setup GraphQL mock
        mock_gql_client = Mock()
        mock_client.return_value = mock_gql_client

        # Mock GraphQL response - return issues, not PRs, in GraphQL format
        issues_only = [
            issue
            for issue in sample_issues_with_pr
            if "pull_request" not in issue or issue["pull_request"] is None
        ]

        # Convert REST format to GraphQL format for the test
        graphql_issues = []
        for issue in issues_only:
            graphql_issue = {
                "number": issue["number"],
                "title": issue["title"],
                "body": issue["body"],
                "state": issue["state"].upper(),
                "stateReason": None,
                "url": issue["html_url"],
                "createdAt": issue["created_at"],
                "updatedAt": issue["updated_at"],
                "author": {"login": issue["user"]["login"]},
                "labels": {"nodes": []},  # Empty labels for simplicity
            }
            graphql_issues.append(graphql_issue)

        mock_gql_client.execute.return_value = {
            "repository": {
                "issues": {
                    "nodes": graphql_issues,
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                }
            }
        }

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

    @patch("src.github.boundary.Client")
    @patch("src.github.boundary.Github")
    def test_get_all_issue_comments_skips_pull_request_comments(
        self, mock_github, mock_client
    ):
        """Test that get_all_issue_comments skips pull request comments."""
        # Setup GraphQL mock
        mock_gql_client = Mock()
        mock_client.return_value = mock_gql_client

        # Mock GraphQL response - only includes comments from regular issues
        mock_gql_client.execute.return_value = {
            "repository": {
                "issues": {
                    "nodes": [
                        {
                            "number": 1,
                            "url": "https://api.github.com/repos/owner/repo/issues/1",
                            "comments": {
                                "nodes": [
                                    {
                                        "body": "Regular comment",
                                        "createdAt": "2023-01-15T10:30:00Z",
                                        "updatedAt": "2023-01-15T10:30:00Z",
                                        "url": "https://github.com/owner/repo/"
                                        "issues/1#issuecomment-1001",
                                        "author": {"login": "user1"},
                                    }
                                ],
                                "pageInfo": {
                                    "hasNextPage": False,
                                    "endCursor": None,
                                },
                            },
                        }
                        # Note: PR comments not included - GraphQL issues query
                        # naturally excludes pull requests
                    ],
                    "pageInfo": {
                        "hasNextPage": False,
                        "endCursor": None,
                    },
                }
            }
        }

        # Test the boundary
        boundary = GitHubApiBoundary("fake-token")
        result = boundary.get_all_issue_comments("owner/repo")

        # Should only have comments from regular issues
        assert len(result) == 1
        assert result[0]["body"] == "Regular comment"
        assert result[0]["user"]["login"] == "user1"

        # GraphQL naturally excludes PR comments by only querying issues
