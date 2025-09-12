"""Tests for GraphQL integration functionality."""

import pytest
from unittest.mock import Mock, patch

from src.github.boundary import GitHubApiBoundary
from src.github.graphql_converters import (
    convert_graphql_labels_to_rest_format,
    convert_graphql_issues_to_rest_format,
    convert_graphql_comments_to_rest_format,
)


class TestGraphQLConverters:
    """Test GraphQL to REST format converters."""

    def test_convert_graphql_labels_to_rest_format(self):
        """Test converting GraphQL labels to REST format."""
        graphql_labels = [
            {
                "name": "bug",
                "color": "d73a4a",
                "description": "Something isn't working",
            },
            {"name": "enhancement", "color": "a2eeef", "description": "New feature"},
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
                        {"name": "bug", "color": "d73a4a", "description": "Bug label"}
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

    def test_convert_graphql_comments_to_rest_format(self):
        """Test converting GraphQL comments to REST format."""
        graphql_comments = [
            {
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

    @patch("src.github.boundary.Client")
    @patch("src.github.boundary.Github")
    def test_boundary_initialization_with_graphql(self, mock_github, mock_client):
        """Test that boundary properly initializes both REST and GraphQL clients."""
        mock_github_instance = Mock()
        mock_github.return_value = mock_github_instance

        mock_gql_client = Mock()
        mock_client.return_value = mock_gql_client

        boundary = GitHubApiBoundary("fake-token")

        assert boundary._github == mock_github_instance
        assert boundary._gql_client == mock_gql_client
        assert boundary._token == "fake-token"

    @patch("src.github.boundary.Client")
    @patch("src.github.boundary.Github")
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

    @patch("src.github.boundary.Client")
    @patch("src.github.boundary.Github")
    def test_get_repository_issues_graphql(self, mock_github, mock_client):
        """Test getting issues via GraphQL."""
        mock_gql_client = Mock()
        mock_client.return_value = mock_gql_client

        # Mock GraphQL response with pagination
        mock_gql_client.execute.return_value = {
            "repository": {
                "issues": {
                    "nodes": [
                        {
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
                    ],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                }
            }
        }

        boundary = GitHubApiBoundary("fake-token")
        result = boundary.get_repository_issues("owner/repo")

        # Should return REST-compatible format
        assert len(result) == 1
        assert result[0]["number"] == 1
        assert result[0]["title"] == "Test Issue"
        assert result[0]["state"] == "open"  # Converted to lowercase

    @patch("src.github.boundary.Github")
    def test_repo_name_parsing(self, mock_github):
        """Test repository name parsing."""
        boundary = GitHubApiBoundary("fake-token")

        owner, name = boundary._parse_repo_name("owner/repo")
        assert owner == "owner"
        assert name == "repo"

        with pytest.raises(
            ValueError, match="Repository name must be in 'owner/repo' format"
        ):
            boundary._parse_repo_name("invalid-repo-name")

    @patch("src.github.boundary.Client")
    @patch("src.github.boundary.Github")
    def test_graphql_client_creation_failure(self, mock_github, mock_client):
        """Test handling of GraphQL client creation failure."""
        # Mock client creation to raise an exception
        mock_client.side_effect = Exception("GraphQL client creation failed")

        with pytest.raises(Exception, match="GraphQL client creation failed"):
            GitHubApiBoundary("fake-token")
