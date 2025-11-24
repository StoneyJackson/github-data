import pytest
import time
from unittest.mock import Mock
from gql import Client
from gql.transport.exceptions import TransportError

from github_data_tools.github.utils.graphql_paginator import GraphQLPaginator

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.github_api]


class TestGraphQLPaginatorBasicFunctionality:
    """Test basic GraphQL pagination functionality."""

    def test_single_page_pagination(self):
        """Test pagination with a single page of results."""
        # Arrange - Create mock client and query
        mock_client = Mock(spec=Client)
        mock_query = Mock()

        # Prepare mock results
        mock_result = {
            "repository": {
                "issues": {
                    "nodes": [{"id": "1"}, {"id": "2"}],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                }
            }
        }
        mock_client.execute.return_value = mock_result
        paginator = GraphQLPaginator(mock_client)

        # Act - Execute pagination
        results = paginator.paginate_all(
            query=mock_query,
            variable_values={"owner": "test", "name": "repo"},
            data_path="repository.issues",
        )

        # Assert - Verify results and mock calls
        assert len(results) == 2
        assert results == [{"id": "1"}, {"id": "2"}]
        mock_client.execute.assert_called_once()

    def test_multi_page_pagination(self):
        """Test pagination across multiple pages."""
        # Arrange - Create mock client with multi-page data
        mock_client = Mock(spec=Client)
        mock_query = Mock()

        # Prepare mock results for two pages
        mock_results = [
            {
                "repository": {
                    "issues": {
                        "nodes": [{"id": "1"}, {"id": "2"}],
                        "pageInfo": {"hasNextPage": True, "endCursor": "page1_cursor"},
                    }
                }
            },
            {
                "repository": {
                    "issues": {
                        "nodes": [{"id": "3"}, {"id": "4"}],
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                    }
                }
            },
        ]
        mock_client.execute.side_effect = mock_results
        paginator = GraphQLPaginator(mock_client)

        # Act - Execute pagination
        results = paginator.paginate_all(
            query=mock_query,
            variable_values={"owner": "test", "name": "repo"},
            data_path="repository.issues",
        )

        # Assert - Verify all pages were processed
        assert len(results) == 4
        assert results == [{"id": "1"}, {"id": "2"}, {"id": "3"}, {"id": "4"}]
        assert mock_client.execute.call_count == 2

    def test_post_processor(self):
        """Test pagination with a post-processing function."""
        # Arrange - Create mock with post-processor function
        mock_client = Mock(spec=Client)
        mock_query = Mock()

        mock_result = {
            "repository": {
                "issues": {
                    "nodes": [{"id": "1"}, {"id": "2"}],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                }
            }
        }
        mock_client.execute.return_value = mock_result

        # Post-processor function
        def add_extra_field(items):
            return [{"**extra": True, **item} for item in items]

        paginator = GraphQLPaginator(mock_client)

        # Act - Execute pagination with post-processor
        results = paginator.paginate_all(
            query=mock_query,
            variable_values={"owner": "test", "name": "repo"},
            data_path="repository.issues",
            post_processor=add_extra_field,
        )

        # Assert - Verify post-processing was applied
        assert len(results) == 2
        assert all("**extra" in item for item in results)

    def test_empty_result(self):
        """Test pagination with an empty result set."""
        # Arrange - Create mock with empty results
        mock_client = Mock(spec=Client)
        mock_query = Mock()

        mock_result = {
            "repository": {
                "issues": {
                    "nodes": [],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                }
            }
        }
        mock_client.execute.return_value = mock_result
        paginator = GraphQLPaginator(mock_client)

        # Act - Execute pagination on empty data
        results = paginator.paginate_all(
            query=mock_query,
            variable_values={"owner": "test", "name": "repo"},
            data_path="repository.issues",
        )

        # Assert - Verify empty results handling
        assert len(results) == 0
        mock_client.execute.assert_called_once()

    def test_deep_data_path(self):
        """Test pagination with a deeply nested data path."""
        # Arrange - Create mock with deeply nested data
        mock_client = Mock(spec=Client)
        mock_query = Mock()

        # Prepare mock results with deep nesting
        mock_result = {
            "repository": {
                "pullRequest": {
                    "comments": {
                        "nodes": [{"id": "comment1"}, {"id": "comment2"}],
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                    }
                }
            }
        }
        mock_client.execute.return_value = mock_result
        paginator = GraphQLPaginator(mock_client)

        # Act - Execute pagination with deep path
        results = paginator.paginate_all(
            query=mock_query,
            variable_values={"owner": "test", "name": "repo"},
            data_path="repository.pullRequest.comments",
        )

        # Assert - Verify deep path navigation works
        assert len(results) == 2
        assert results == [{"id": "comment1"}, {"id": "comment2"}]

    def test_pagination_with_custom_page_size(self):
        """Test pagination with custom page size."""
        # Arrange - Create paginator with custom page size
        mock_client = Mock(spec=Client)
        mock_query = Mock()

        mock_result = {
            "repository": {
                "issues": {
                    "nodes": [{"id": "1"}],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                }
            }
        }
        mock_client.execute.return_value = mock_result
        paginator = GraphQLPaginator(mock_client, page_size=50)

        # Act - Execute pagination
        results = paginator.paginate_all(
            query=mock_query,
            variable_values={"owner": "test", "name": "repo"},
            data_path="repository.issues",
        )

        # Assert - Verify custom page size was used
        expected_call = mock_client.execute.call_args[1]["variable_values"]
        assert expected_call["first"] == 50
        assert len(results) == 1

    def test_null_data_path(self):
        """Test pagination when data path resolves to null."""
        # Arrange - Create mock with null data path
        mock_client = Mock(spec=Client)
        mock_query = Mock()

        # Prepare mock results with null data
        mock_result = {"repository": {"issues": None}}
        mock_client.execute.return_value = mock_result
        paginator = GraphQLPaginator(mock_client)

        # Act - Execute pagination on null data path
        results = paginator.paginate_all(
            query=mock_query,
            variable_values={"owner": "test", "name": "repo"},
            data_path="repository.issues",
        )

        # Assert - Should return empty list when data is null
        assert len(results) == 0


class TestGraphQLPaginatorAdvancedScenarios:
    """Test advanced pagination scenarios and edge cases."""

    def test_large_multi_page_pagination(self):
        """Test pagination across many pages to ensure cursor handling."""
        # Arrange - Create mock with 5 pages of data
        mock_client = Mock(spec=Client)
        mock_query = Mock()

        # Prepare mock results for multiple pages
        mock_results = []
        for i in range(5):  # 5 pages
            is_last_page = i == 4
            mock_results.append(
                {
                    "repository": {
                        "issues": {
                            "nodes": [{"id": f"{i*2+1}"}, {"id": f"{i*2+2}"}],
                            "pageInfo": {
                                "hasNextPage": not is_last_page,
                                "endCursor": (
                                    f"cursor_{i}" if not is_last_page else None
                                ),
                            },
                        }
                    }
                }
            )

        mock_client.execute.side_effect = mock_results
        paginator = GraphQLPaginator(mock_client)

        # Act - Execute pagination across multiple pages
        results = paginator.paginate_all(
            query=mock_query,
            variable_values={"owner": "test", "name": "repo"},
            data_path="repository.issues",
        )

        # Assert - Verify all pages were processed correctly
        assert len(results) == 10  # 5 pages * 2 items each
        assert mock_client.execute.call_count == 5
        # Verify we got all the expected IDs
        expected_ids = [str(i) for i in range(1, 11)]
        actual_ids = [item["id"] for item in results]
        assert actual_ids == expected_ids

    @pytest.mark.enhanced_fixtures
    def test_pagination_with_github_data_builder(self, github_data_builder):
        """Test pagination using enhanced github_data_builder fixture."""
        # Arrange - Use data builder to create test data
        test_data = github_data_builder.reset().with_issues(5).build()

        mock_client = Mock(spec=Client)
        mock_query = Mock()

        # Convert test data to GraphQL response format
        mock_result = {
            "repository": {
                "issues": {
                    "nodes": test_data["issues"],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                }
            }
        }
        mock_client.execute.return_value = mock_result
        paginator = GraphQLPaginator(mock_client)

        # Act - Execute pagination
        results = paginator.paginate_all(
            query=mock_query,
            variable_values={"owner": "test", "name": "repo"},
            data_path="repository.issues",
        )

        # Assert - Verify results match built data
        assert len(results) == 5
        for result in results:
            assert "id" in result
            assert "title" in result
            assert "state" in result

    @pytest.mark.enhanced_fixtures
    def test_pagination_with_parametrized_data_factory(self, parametrized_data_factory):
        """Test pagination using parametrized_data_factory."""
        # Arrange - Create scenario data
        test_data = parametrized_data_factory("basic")

        mock_client = Mock(spec=Client)
        mock_query = Mock()

        # Convert test data to GraphQL response format
        mock_result = {
            "repository": {
                "issues": {
                    "nodes": test_data["issues"],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                }
            }
        }
        mock_client.execute.return_value = mock_result
        paginator = GraphQLPaginator(mock_client)

        # Act - Execute pagination
        results = paginator.paginate_all(
            query=mock_query,
            variable_values={"owner": "test", "name": "repo"},
            data_path="repository.issues",
        )

        # Assert - Verify parametrized data was processed
        assert len(results) == len(test_data["issues"])
        for result in results:
            assert "title" in result


@pytest.mark.github_api
@pytest.mark.error_simulation
class TestGraphQLPaginatorErrorHandling:
    """Test GraphQL paginator error handling and resilience."""

    def test_transport_error_during_pagination(self):
        """Test handling of transport errors during pagination."""
        mock_client = Mock(spec=Client)
        mock_query = Mock()

        # Simulate transport error
        mock_client.execute.side_effect = TransportError("Network timeout")

        paginator = GraphQLPaginator(mock_client)

        with pytest.raises(TransportError, match="Network timeout"):
            paginator.paginate_all(
                query=mock_query,
                variable_values={"owner": "test", "name": "repo"},
                data_path="repository.issues",
            )

    def test_malformed_response_structure(self):
        """Test handling of malformed GraphQL responses."""
        mock_client = Mock(spec=Client)
        mock_query = Mock()

        # Response missing expected structure
        malformed_response = {
            "repository": {
                "issues": {
                    "nodes": [{"id": "1"}],
                    # Missing pageInfo
                }
            }
        }
        mock_client.execute.return_value = malformed_response

        paginator = GraphQLPaginator(mock_client)

        with pytest.raises((KeyError, AttributeError)):
            paginator.paginate_all(
                query=mock_query,
                variable_values={"owner": "test", "name": "repo"},
                data_path="repository.issues",
            )


@pytest.mark.github_api
@pytest.mark.performance
class TestGraphQLPaginatorPerformance:
    """Test GraphQL paginator performance and timing."""

    def test_single_page_performance(self):
        """Test performance of single page pagination."""
        mock_client = Mock(spec=Client)
        mock_query = Mock()

        # Simulate response time
        def mock_execute(*_args, **_kwargs):
            time.sleep(0.01)  # Simulate 10ms response time
            return {
                "repository": {
                    "issues": {
                        "nodes": [{"id": str(i)} for i in range(100)],
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                    }
                }
            }

        mock_client.execute.side_effect = mock_execute
        paginator = GraphQLPaginator(mock_client)

        start_time = time.time()
        results = paginator.paginate_all(
            query=mock_query,
            variable_values={"owner": "test", "name": "repo"},
            data_path="repository.issues",
        )
        execution_time = time.time() - start_time

        assert len(results) == 100
        assert (
            execution_time < 0.5
        ), f"Single page took {execution_time:.3f}s, expected < 0.5s"
