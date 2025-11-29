"""Integration tests for GraphQL milestone data integration.

Tests GraphQL query enhancement validation, milestone data conversion accuracy,
issue/PR GraphQL responses with milestones, and performance impact assessment.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from github_data_tools.github.graphql_client import GitHubGraphQLClient
from github_data_tools.github.queries.milestones import (
    REPOSITORY_MILESTONES_QUERY,
    build_milestones_query_variables,
)
from github_data_tools.github.queries.issues import REPOSITORY_ISSUES_QUERY
from github_data_tools.github.queries.pull_requests import (
    REPOSITORY_PULL_REQUESTS_QUERY,
)
from github_data_tools.github.converter_registry import get_converter


@pytest.mark.integration
class TestGraphQLMilestoneIntegration:
    """Test GraphQL milestone data integration."""

    @pytest.fixture
    def mock_graphql_client(self):
        """Create a mock GraphQL client."""
        client = Mock(spec=GitHubGraphQLClient)
        client.execute = AsyncMock()
        return client

    @pytest.fixture
    def sample_milestone_graphql_response(self):
        """Create sample milestone GraphQL response data."""
        return {
            "repository": {
                "milestones": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "nodes": [
                        {
                            "id": "M_kwDOABCDEF123",
                            "number": 1,
                            "title": "Version 1.0",
                            "description": "First major release",
                            "state": "OPEN",
                            "creator": {
                                "login": "testuser",
                                "id": "U_123456",
                                "avatarUrl": "https://github.com/images/testuser.jpg",
                                "htmlUrl": "https://github.com/testuser",
                                "type": "User",
                            },
                            "createdAt": "2023-01-01T00:00:00Z",
                            "updatedAt": "2023-01-02T00:00:00Z",
                            "dueOn": "2023-12-31T23:59:59Z",
                            "closedAt": None,
                            "issues": {"totalCount": 5},
                            "pullRequests": {"totalCount": 2},
                            "url": "https://github.com/owner/repo/milestone/1",
                        }
                    ],
                }
            }
        }

    @pytest.fixture
    def sample_issue_with_milestone_response(self):
        """Create sample issue GraphQL response with milestone data."""
        return {
            "repository": {
                "issues": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "nodes": [
                        {
                            "id": "I_kwDOABCDEF456",
                            "number": 1,
                            "title": "Test Issue",
                            "body": "This is a test issue",
                            "state": "OPEN",
                            "stateReason": None,
                            "url": "https://github.com/owner/repo/issues/1",
                            "createdAt": "2023-01-01T12:00:00Z",
                            "updatedAt": "2023-01-01T13:00:00Z",
                            "author": {
                                "login": "testuser",
                                "id": "U_123456",
                                "avatarUrl": "https://github.com/images/testuser.jpg",
                                "url": "https://github.com/testuser",
                            },
                            "labels": {"nodes": []},
                            "milestone": {
                                "id": "M_kwDOABCDEF123",
                                "number": 1,
                                "title": "Version 1.0",
                                "description": "First major release",
                                "state": "OPEN",
                                "createdAt": "2023-01-01T00:00:00Z",
                                "updatedAt": "2023-01-02T00:00:00Z",
                                "dueOn": "2023-12-31T23:59:59Z",
                                "closedAt": None,
                                "url": "https://github.com/owner/repo/milestone/1",
                            },
                        }
                    ],
                }
            }
        }

    @pytest.fixture
    def sample_pr_with_milestone_response(self):
        """Create sample PR GraphQL response with milestone data."""
        return {
            "repository": {
                "pullRequests": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "nodes": [
                        {
                            "id": "PR_kwDOABCDEF789",
                            "number": 1,
                            "title": "Test PR",
                            "body": "This is a test PR",
                            "state": "OPEN",
                            "url": "https://github.com/owner/repo/pull/1",
                            "createdAt": "2023-01-01T14:00:00Z",
                            "updatedAt": "2023-01-01T15:00:00Z",
                            "author": {
                                "login": "testuser",
                                "id": "U_123456",
                                "avatarUrl": "https://github.com/images/testuser.jpg",
                                "url": "https://github.com/testuser",
                            },
                            "labels": {"nodes": []},
                            "milestone": {
                                "id": "M_kwDOABCDEF123",
                                "number": 1,
                                "title": "Version 1.0",
                                "description": "First major release",
                                "state": "OPEN",
                                "createdAt": "2023-01-01T00:00:00Z",
                                "updatedAt": "2023-01-02T00:00:00Z",
                                "dueOn": "2023-12-31T23:59:59Z",
                                "closedAt": None,
                                "url": "https://github.com/owner/repo/milestone/1",
                            },
                            "headRefName": "feature-branch",
                            "baseRefName": "main",
                            "merged": False,
                            "mergedAt": None,
                            "mergeable": "MERGEABLE",
                        }
                    ],
                }
            }
        }

    @pytest.mark.asyncio
    async def test_milestone_graphql_query_structure(
        self, mock_graphql_client, sample_milestone_graphql_response
    ):
        """Test milestone GraphQL query structure and execution."""
        # Configure mock response
        mock_graphql_client.execute.return_value = sample_milestone_graphql_response

        # Execute query
        variables = build_milestones_query_variables("owner", "repo")
        result = await mock_graphql_client.execute(
            REPOSITORY_MILESTONES_QUERY, variables
        )

        # Verify query execution
        mock_graphql_client.execute.assert_called_once_with(
            REPOSITORY_MILESTONES_QUERY, variables
        )

        # Verify response structure
        assert "repository" in result
        assert "milestones" in result["repository"]
        assert "nodes" in result["repository"]["milestones"]
        assert "pageInfo" in result["repository"]["milestones"]

        # Verify milestone fields
        milestone_node = result["repository"]["milestones"]["nodes"][0]
        expected_fields = [
            "id",
            "number",
            "title",
            "description",
            "state",
            "creator",
            "createdAt",
            "updatedAt",
            "dueOn",
            "closedAt",
            "issues",
            "pullRequests",
            "url",
        ]
        for field in expected_fields:
            assert field in milestone_node

    @pytest.mark.asyncio
    async def test_milestone_data_conversion_accuracy(
        self, sample_milestone_graphql_response
    ):
        """Test accuracy of milestone data conversion from GraphQL response."""
        milestone_data = sample_milestone_graphql_response["repository"]["milestones"][
            "nodes"
        ][0]

        # Convert using the converter
        milestone = get_converter("convert_to_milestone")(milestone_data)

        # Verify conversion accuracy
        assert milestone.id == "M_kwDOABCDEF123"
        assert milestone.number == 1
        assert milestone.title == "Version 1.0"
        assert milestone.description == "First major release"
        assert milestone.state == "open"
        assert milestone.creator.login == "testuser"
        assert milestone.creator.id == "U_123456"
        assert milestone.created_at == datetime.fromisoformat(
            "2023-01-01T00:00:00+00:00"
        )
        assert milestone.updated_at == datetime.fromisoformat(
            "2023-01-02T00:00:00+00:00"
        )
        assert milestone.due_on == datetime.fromisoformat("2023-12-31T23:59:59+00:00")
        assert milestone.closed_at is None
        assert milestone.open_issues == 5
        assert milestone.closed_issues == 0  # Calculated field
        assert milestone.html_url == "https://github.com/owner/repo/milestone/1"

    @pytest.mark.asyncio
    async def test_issue_graphql_response_with_milestone(
        self, mock_graphql_client, sample_issue_with_milestone_response
    ):
        """Test issue GraphQL responses include milestone data."""
        # Configure mock response
        mock_graphql_client.execute.return_value = sample_issue_with_milestone_response

        # Execute query
        variables = {"owner": "owner", "name": "repo", "first": 100}
        result = await mock_graphql_client.execute(REPOSITORY_ISSUES_QUERY, variables)

        # Verify milestone data in issue response
        issue_node = result["repository"]["issues"]["nodes"][0]
        assert "milestone" in issue_node
        assert issue_node["milestone"] is not None

        # Verify milestone field completeness
        milestone_data = issue_node["milestone"]
        expected_milestone_fields = [
            "id",
            "number",
            "title",
            "description",
            "state",
            "createdAt",
            "updatedAt",
            "dueOn",
            "closedAt",
            "url",
        ]
        for field in expected_milestone_fields:
            assert field in milestone_data

        # Verify milestone data accuracy
        assert milestone_data["number"] == 1
        assert milestone_data["title"] == "Version 1.0"
        assert milestone_data["state"] == "OPEN"

    @pytest.mark.asyncio
    async def test_pr_graphql_response_with_milestone(
        self, mock_graphql_client, sample_pr_with_milestone_response
    ):
        """Test PR GraphQL responses include milestone data."""
        # Configure mock response
        mock_graphql_client.execute.return_value = sample_pr_with_milestone_response

        # Execute query
        variables = {"owner": "owner", "name": "repo", "first": 100}
        result = await mock_graphql_client.execute(
            REPOSITORY_PULL_REQUESTS_QUERY, variables
        )

        # Verify milestone data in PR response
        pr_node = result["repository"]["pullRequests"]["nodes"][0]
        assert "milestone" in pr_node
        assert pr_node["milestone"] is not None

        # Verify milestone field completeness
        milestone_data = pr_node["milestone"]
        expected_milestone_fields = [
            "id",
            "number",
            "title",
            "description",
            "state",
            "createdAt",
            "updatedAt",
            "dueOn",
            "closedAt",
            "url",
        ]
        for field in expected_milestone_fields:
            assert field in milestone_data

        # Verify milestone data accuracy
        assert milestone_data["number"] == 1
        assert milestone_data["title"] == "Version 1.0"
        assert milestone_data["state"] == "OPEN"

    def test_milestone_field_presence_validation(
        self, sample_milestone_graphql_response
    ):
        """Test validation of milestone field presence in GraphQL responses."""
        milestone_data = sample_milestone_graphql_response["repository"]["milestones"][
            "nodes"
        ][0]

        # Test all required fields are present
        required_fields = [
            "id",
            "number",
            "title",
            "state",
            "createdAt",
            "updatedAt",
            "url",
        ]
        for field in required_fields:
            assert (
                field in milestone_data
            ), f"Required field '{field}' missing from milestone data"

        # Test optional fields can be None
        milestone_data_with_none = milestone_data.copy()
        milestone_data_with_none["description"] = None
        milestone_data_with_none["dueOn"] = None
        milestone_data_with_none["closedAt"] = None

        # Should still convert successfully
        milestone = get_converter("convert_to_milestone")(milestone_data_with_none)
        assert milestone.description is None
        assert milestone.due_on is None
        assert milestone.closed_at is None

    def test_graphql_query_variable_building(self):
        """Test building GraphQL query variables for milestone queries."""
        # Test basic variables
        variables = build_milestones_query_variables("owner", "repo")
        expected = {"owner": "owner", "name": "repo"}
        assert variables == expected

        # Test with pagination
        variables_with_cursor = build_milestones_query_variables(
            "owner", "repo", "cursor123"
        )
        expected_with_cursor = {"owner": "owner", "name": "repo", "after": "cursor123"}
        assert variables_with_cursor == expected_with_cursor

    @pytest.mark.asyncio
    async def test_performance_impact_assessment(self, mock_graphql_client):
        """Test performance impact of milestone GraphQL enhancements."""
        # Create large dataset response
        large_response = {
            "repository": {
                "milestones": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "nodes": [],
                }
            }
        }

        # Generate 50 milestones for performance testing
        for i in range(50):
            milestone = {
                "id": f"M_kwDOABCDEF{i:03d}",
                "number": i + 1,
                "title": f"Milestone {i + 1}",
                "description": f"Description for milestone {i + 1}",
                "state": "OPEN" if i % 2 == 0 else "CLOSED",
                "creator": {
                    "login": "testuser",
                    "id": "U_123456",
                    "avatarUrl": "https://github.com/images/testuser.jpg",
                    "htmlUrl": "https://github.com/testuser",
                    "type": "User",
                },
                "createdAt": f"2023-{i//12 + 1:02d}-01T00:00:00Z",
                "updatedAt": f"2023-{i//12 + 1:02d}-02T00:00:00Z",
                "dueOn": f"2023-{i//12 + 1:02d}-28T23:59:59Z",
                "closedAt": (
                    f"2023-{i//12 + 1:02d}-15T12:00:00Z" if i % 2 == 1 else None
                ),
                "issues": {"totalCount": i * 2},
                "pullRequests": {"totalCount": i},
                "url": f"https://github.com/owner/repo/milestone/{i + 1}",
            }
            large_response["repository"]["milestones"]["nodes"].append(milestone)

        mock_graphql_client.execute.return_value = large_response

        # Measure conversion performance
        import time

        start_time = time.time()

        variables = build_milestones_query_variables("owner", "repo")
        result = await mock_graphql_client.execute(
            REPOSITORY_MILESTONES_QUERY, variables
        )

        # Convert all milestones
        milestones = []
        for milestone_data in result["repository"]["milestones"]["nodes"]:
            milestone = get_converter("convert_to_milestone")(milestone_data)
            milestones.append(milestone)

        end_time = time.time()
        conversion_time = end_time - start_time

        # Verify performance is acceptable (should be < 1 second for 50 milestones)
        assert (
            conversion_time < 1.0
        ), f"Conversion took too long: {conversion_time:.3f}s"
        assert len(milestones) == 50

        # Verify all conversions are accurate
        for i, milestone in enumerate(milestones):
            assert milestone.number == i + 1
            assert milestone.title == f"Milestone {i + 1}"
            assert milestone.state == ("open" if i % 2 == 0 else "closed")
