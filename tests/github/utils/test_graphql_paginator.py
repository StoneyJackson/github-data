from unittest.mock import Mock
from gql import Client

from src.github.utils.graphql_paginator import GraphQLPaginator


def test_single_page_pagination():
    """Test pagination with a single page of results."""
    # Mock GraphQL client
    mock_client = Mock(spec=Client)
    mock_query = Mock()

    # Prepare mock results
    mock_result = {
        "repository": {
            "issues": {
                "nodes": [{"id": "1"}, {"id": "2"}],
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": None
                }
            }
        }
    }
    mock_client.execute.return_value = mock_result

    # Initialize paginator
    paginator = GraphQLPaginator(mock_client)

    # Execute pagination
    results = paginator.paginate_all(
        query=mock_query,
        variable_values={"owner": "test", "name": "repo"},
        data_path="repository.issues"
    )

    # Assertions
    assert len(results) == 2
    assert results == [{"id": "1"}, {"id": "2"}]
    mock_client.execute.assert_called_once()


def test_multi_page_pagination():
    """Test pagination across multiple pages."""
    # Mock GraphQL client
    mock_client = Mock(spec=Client)
    mock_query = Mock()

    # Prepare mock results for two pages
    mock_results = [
        {
            "repository": {
                "issues": {
                    "nodes": [{"id": "1"}, {"id": "2"}],
                    "pageInfo": {
                        "hasNextPage": True,
                        "endCursor": "page1_cursor"
                    }
                }
            }
        },
        {
            "repository": {
                "issues": {
                    "nodes": [{"id": "3"}, {"id": "4"}],
                    "pageInfo": {
                        "hasNextPage": False,
                        "endCursor": None
                    }
                }
            }
        }
    ]
    mock_client.execute.side_effect = mock_results

    # Initialize paginator
    paginator = GraphQLPaginator(mock_client)

    # Execute pagination
    results = paginator.paginate_all(
        query=mock_query,
        variable_values={"owner": "test", "name": "repo"},
        data_path="repository.issues"
    )

    # Assertions
    assert len(results) == 4
    assert results == [{"id": "1"}, {"id": "2"}, {"id": "3"}, {"id": "4"}]
    assert mock_client.execute.call_count == 2


def test_post_processor():
    """Test pagination with a post-processing function."""
    # Mock GraphQL client
    mock_client = Mock(spec=Client)
    mock_query = Mock()

    # Prepare mock results
    mock_result = {
        "repository": {
            "issues": {
                "nodes": [{"id": "1"}, {"id": "2"}],
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": None
                }
            }
        }
    }
    mock_client.execute.return_value = mock_result

    # Post-processor function
    def add_extra_field(items):
        return [{"**extra": True, **item} for item in items]

    # Initialize paginator
    paginator = GraphQLPaginator(mock_client)

    # Execute pagination
    results = paginator.paginate_all(
        query=mock_query,
        variable_values={"owner": "test", "name": "repo"},
        data_path="repository.issues",
        post_processor=add_extra_field
    )

    # Assertions
    assert len(results) == 2
    assert all("**extra" in item for item in results)


def test_empty_result():
    """Test pagination with an empty result set."""
    # Mock GraphQL client
    mock_client = Mock(spec=Client)
    mock_query = Mock()

    # Prepare mock results
    mock_result = {
        "repository": {
            "issues": {
                "nodes": [],
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": None
                }
            }
        }
    }
    mock_client.execute.return_value = mock_result

    # Initialize paginator
    paginator = GraphQLPaginator(mock_client)

    # Execute pagination
    results = paginator.paginate_all(
        query=mock_query,
        variable_values={"owner": "test", "name": "repo"},
        data_path="repository.issues"
    )

    # Assertions
    assert len(results) == 0
    mock_client.execute.assert_called_once()
