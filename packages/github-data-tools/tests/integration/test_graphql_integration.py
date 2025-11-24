"""Tests for GraphQL integration functionality."""

import pytest
from unittest.mock import Mock, patch

from github_data.github.boundary import GitHubApiBoundary
from github_data.github.graphql_converters import (
    convert_graphql_labels_to_rest_format,
    convert_graphql_issues_to_rest_format,
    convert_graphql_comments_to_rest_format,
    convert_graphql_pull_requests_to_rest_format,
)
from github_data.entities.issues.converters import convert_to_issue
from github_data.entities.pull_requests.converters import convert_to_pull_request

pytestmark = [pytest.mark.integration, pytest.mark.medium]


class TestGraphQLConverters:
    """Test GraphQL to REST format converters."""

    def test_convert_graphql_labels_to_rest_format(self):
        """Test converting GraphQL labels to REST format."""
        graphql_labels = [
            {
                "id": "MDU6TGFiZWwxMjM0NTY3ODk=",
                "name": "bug",
                "color": "d73a4a",
                "description": "Something isn't working",
            },
            {
                "id": "MDU6TGFiZWwxMjM0NTY3ODA=",
                "name": "enhancement",
                "color": "a2eeef",
                "description": "New feature",
            },
        ]

        result = convert_graphql_labels_to_rest_format(graphql_labels)

        assert len(result) == 2
        assert result[0]["name"] == "bug"
        assert result[0]["color"] == "d73a4a"
        assert result[0]["description"] == "Something isn't working"
        assert "url" in result[0]
        assert "default" in result[0]

    def test_convert_graphql_issues_to_rest_format(self):
        """Test converting GraphQL issues to REST format."""
        graphql_issues = [
            {
                "id": "MDU6SXNzdWUxMjM0NTY3ODk=",
                "number": 1,
                "title": "Test Issue",
                "body": "Test body",
                "state": "OPEN",
                "stateReason": None,
                "url": "https://github.com/owner/repo/issues/1",
                "createdAt": "2023-01-15T10:30:00Z",
                "updatedAt": "2023-01-15T14:20:00Z",
                "author": {"login": "testuser"},
                "labels": {
                    "nodes": [
                        {
                            "id": "MDU6TGFiZWwxMjM0NTY3ODk=",
                            "name": "bug",
                            "color": "d73a4a",
                            "description": "Bug label",
                        }
                    ]
                },
            }
        ]

        result = convert_graphql_issues_to_rest_format(graphql_issues, "owner/repo")

        assert len(result) == 1
        issue = result[0]
        assert issue["number"] == 1
        assert issue["title"] == "Test Issue"
        assert issue["state"] == "open"  # Converted to lowercase
        assert issue["user"]["login"] == "testuser"
        assert len(issue["labels"]) == 1
        assert issue["labels"][0]["name"] == "bug"

    def test_convert_graphql_issues_with_milestone_to_entity(self):
        """Test GraphQL issues with milestones convert to Issue entities.

        This tests the full conversion pipeline:
        GraphQL -> REST format -> Issue entity.
        Regression test for bug where milestone was double-converted
        causing AttributeError.
        """
        graphql_issues = [
            {
                "id": "MDU6SXNzdWUxMjM0NTY3ODk=",
                "number": 1,
                "title": "Test Issue with Milestone",
                "body": "Test body",
                "state": "OPEN",
                "stateReason": None,
                "url": "https://github.com/owner/repo/issues/1",
                "createdAt": "2023-01-15T10:30:00Z",
                "updatedAt": "2023-01-15T14:20:00Z",
                "author": {
                    "login": "testuser",
                    "id": "MDQ6VXNlcjEyMzQ1Njc4OQ==",
                    "avatarUrl": "https://avatars.githubusercontent.com/u/123?v=4",
                    "url": "https://github.com/testuser",
                },
                "labels": {"nodes": []},
                "milestone": {
                    "id": "MDk6TWlsZXN0b25lMTIzNDU2Nzg5",
                    "number": 1,
                    "title": "v1.0",
                    "description": "First release",
                    "state": "OPEN",
                    "createdAt": "2023-01-01T00:00:00Z",
                    "updatedAt": "2023-01-01T00:00:00Z",
                    "dueOn": None,
                    "closedAt": None,
                    "url": "https://github.com/owner/repo/milestone/1",
                    "creator": {
                        "login": "creator",
                        "id": "MDQ6VXNlcjk4NzY1NDMyMQ==",
                        "avatarUrl": "https://avatars.githubusercontent.com/u/987?v=4",
                        "url": "https://github.com/creator",
                    },
                    "issues": {"totalCount": 5},
                },
            }
        ]

        # Convert from GraphQL to REST format
        rest_issues = convert_graphql_issues_to_rest_format(
            graphql_issues, "owner/repo"
        )

        # This should not raise AttributeError:
        # 'Milestone' object has no attribute 'get'
        issue = convert_to_issue(rest_issues[0])

        assert issue.number == 1
        assert issue.title == "Test Issue with Milestone"
        assert issue.milestone is not None
        assert issue.milestone.number == 1
        assert issue.milestone.title == "v1.0"

    def test_convert_graphql_pull_requests_with_milestone_to_entity(self):
        """Test GraphQL PRs with milestones convert to PullRequest entities.

        This tests the full conversion pipeline:
        GraphQL -> REST format -> PullRequest entity.
        Regression test for bug where milestone was double-converted
        causing AttributeError.
        """
        graphql_prs = [
            {
                "id": "MDExOlB1bGxSZXF1ZXN0MTIzNDU2Nzg5",
                "number": 1,
                "title": "Test PR with Milestone",
                "body": "Test PR body",
                "state": "OPEN",
                "url": "https://github.com/owner/repo/pull/1",
                "createdAt": "2023-01-15T10:30:00Z",
                "updatedAt": "2023-01-15T14:20:00Z",
                "closedAt": None,
                "mergedAt": None,
                "mergeCommit": None,
                "baseRef": {"name": "main"},
                "headRef": {"name": "feature"},
                "author": {
                    "login": "testuser",
                    "id": "MDQ6VXNlcjEyMzQ1Njc4OQ==",
                    "avatarUrl": "https://avatars.githubusercontent.com/u/123?v=4",
                    "url": "https://github.com/testuser",
                },
                "assignees": {"nodes": []},
                "labels": {"nodes": []},
                "comments": {"totalCount": 0},
                "milestone": {
                    "id": "MDk6TWlsZXN0b25lMTIzNDU2Nzg5",
                    "number": 1,
                    "title": "v1.0",
                    "description": "First release",
                    "state": "OPEN",
                    "createdAt": "2023-01-01T00:00:00Z",
                    "updatedAt": "2023-01-01T00:00:00Z",
                    "dueOn": None,
                    "closedAt": None,
                    "url": "https://github.com/owner/repo/milestone/1",
                    "creator": {
                        "login": "creator",
                        "id": "MDQ6VXNlcjk4NzY1NDMyMQ==",
                        "avatarUrl": "https://avatars.githubusercontent.com/u/987?v=4",
                        "url": "https://github.com/creator",
                    },
                    "issues": {"totalCount": 5},
                },
            }
        ]

        # Convert from GraphQL to REST format
        rest_prs = convert_graphql_pull_requests_to_rest_format(
            graphql_prs, "owner/repo"
        )

        # This should not raise AttributeError:
        # 'Milestone' object has no attribute 'get'
        pr = convert_to_pull_request(rest_prs[0])

        assert pr.number == 1
        assert pr.title == "Test PR with Milestone"
        assert pr.milestone is not None
        assert pr.milestone.number == 1
        assert pr.milestone.title == "v1.0"

    def test_convert_graphql_comments_to_rest_format(self):
        """Test converting GraphQL comments to REST format."""
        graphql_comments = [
            {
                "id": "MDEyOklzc3VlQ29tbWVudDEyMw==",
                "body": "Test comment",
                "createdAt": "2023-01-15T10:30:00Z",
                "updatedAt": "2023-01-15T14:20:00Z",
                "url": "https://github.com/owner/repo/issues/1#issuecomment-123",
                "author": {"login": "testuser"},
                "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
            }
        ]

        result = convert_graphql_comments_to_rest_format(graphql_comments)

        assert len(result) == 1
        comment = result[0]
        assert comment["body"] == "Test comment"
        assert comment["user"]["login"] == "testuser"
        assert (
            comment["issue_url"] == "https://api.github.com/repos/owner/repo/issues/1"
        )


class TestGraphQLBoundaryIntegration:
    """Test GitHubApiBoundary with GraphQL functionality."""

    @patch("github_data.github.graphql_client.Client")
    @patch("github_data.github.boundary.Github")
    def test_boundary_initialization_with_graphql(self, mock_github, mock_client):
        """Test that boundary properly initializes both REST and GraphQL clients."""
        mock_github_instance = Mock()
        mock_github.return_value = mock_github_instance

        mock_gql_client = Mock()
        mock_client.return_value = mock_gql_client

        boundary = GitHubApiBoundary("fake-token")

        assert boundary._github == mock_github_instance
        assert hasattr(boundary, "_graphql_client")
        assert boundary._token == "fake-token"

    @patch("github_data.github.graphql_client.Client")
    @patch("github_data.github.boundary.Github")
    def test_get_repository_labels_graphql(self, mock_github, mock_client):
        """Test getting labels via GraphQL."""
        mock_gql_client = Mock()
        mock_client.return_value = mock_gql_client

        # Mock GraphQL response
        mock_gql_client.execute.return_value = {
            "repository": {
                "labels": {
                    "nodes": [
                        {
                            "id": "MDU6TGFiZWwxMjM0NTY3ODk=",
                            "name": "bug",
                            "color": "d73a4a",
                            "description": "Something isn't working",
                        }
                    ]
                }
            }
        }

        boundary = GitHubApiBoundary("fake-token")
        result = boundary.get_repository_labels("owner/repo")

        # Should return REST-compatible format
        assert len(result) == 1
        assert result[0]["name"] == "bug"
        assert result[0]["color"] == "d73a4a"
        assert "url" in result[0]

    @patch("github_data.github.graphql_client.GraphQLPaginator")
    @patch("github_data.github.graphql_client.Client")
    @patch("github_data.github.boundary.Github")
    def test_get_repository_issues_graphql(
        self, mock_github, mock_client, mock_paginator
    ):
        """Test getting issues via GraphQL."""
        mock_gql_client = Mock()
        mock_client.return_value = mock_gql_client

        mock_paginator_instance = Mock()
        mock_paginator.return_value = mock_paginator_instance

        # Mock paginated response
        mock_paginator_instance.paginate_all.return_value = [
            {
                "id": "MDU6SXNzdWUxMjM0NTY3ODk=",
                "number": 1,
                "title": "Test Issue",
                "body": "Test body",
                "state": "OPEN",
                "stateReason": None,
                "url": "https://github.com/owner/repo/issues/1",
                "createdAt": "2023-01-15T10:30:00Z",
                "updatedAt": "2023-01-15T14:20:00Z",
                "author": {"login": "testuser"},
                "labels": {"nodes": []},
            }
        ]

        boundary = GitHubApiBoundary("fake-token")
        result = boundary.get_repository_issues("owner/repo")

        # Should return REST-compatible format
        assert len(result) == 1
        assert result[0]["number"] == 1
        assert result[0]["title"] == "Test Issue"
        assert result[0]["state"] == "open"  # Converted to lowercase

    @patch("github_data.github.boundary.Github")
    def test_repo_name_parsing(self, mock_github):
        """Test repository name parsing."""
        boundary = GitHubApiBoundary("fake-token")

        owner, name = boundary._rest_client._parse_repo_name("owner/repo")
        assert owner == "owner"
        assert name == "repo"

        with pytest.raises(
            ValueError, match="Repository name must be in 'owner/repo' format"
        ):
            boundary._rest_client._parse_repo_name("invalid-repo-name")

    @patch("github_data.github.graphql_client.Client")
    @patch("github_data.github.boundary.Github")
    def test_graphql_client_creation_failure(self, mock_github, mock_client):
        """Test handling of GraphQL client creation failure."""
        # Mock client creation to raise an exception
        mock_client.side_effect = Exception("GraphQL client creation failed")

        with pytest.raises(Exception, match="GraphQL client creation failed"):
            GitHubApiBoundary("fake-token")
