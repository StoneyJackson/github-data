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
                "pageInfo": {"hasNextPage": False, "endCursor": None},
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
        data_path="repository.issues",
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

    # Initialize paginator
    paginator = GraphQLPaginator(mock_client)

    # Execute pagination
    results = paginator.paginate_all(
        query=mock_query,
        variable_values={"owner": "test", "name": "repo"},
        data_path="repository.issues",
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
                "pageInfo": {"hasNextPage": False, "endCursor": None},
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
        post_processor=add_extra_field,
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
                "pageInfo": {"hasNextPage": False, "endCursor": None},
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
        data_path="repository.issues",
    )

    # Assertions
    assert len(results) == 0
    mock_client.execute.assert_called_once()


def test_deep_data_path():
    """Test pagination with a deeply nested data path."""
    # Mock GraphQL client
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

    # Initialize paginator
    paginator = GraphQLPaginator(mock_client)

    # Execute pagination
    results = paginator.paginate_all(
        query=mock_query,
        variable_values={"owner": "test", "name": "repo"},
        data_path="repository.pullRequest.comments",
    )

    # Assertions
    assert len(results) == 2
    assert results == [{"id": "comment1"}, {"id": "comment2"}]


def test_pagination_with_custom_page_size():
    """Test pagination with custom page size."""
    # Mock GraphQL client
    mock_client = Mock(spec=Client)
    mock_query = Mock()

    # Prepare mock results
    mock_result = {
        "repository": {
            "issues": {
                "nodes": [{"id": "1"}],
                "pageInfo": {"hasNextPage": False, "endCursor": None},
            }
        }
    }
    mock_client.execute.return_value = mock_result

    # Initialize paginator with custom page size
    paginator = GraphQLPaginator(mock_client, page_size=50)

    # Execute pagination
    results = paginator.paginate_all(
        query=mock_query,
        variable_values={"owner": "test", "name": "repo"},
        data_path="repository.issues",
    )

    # Verify the correct page size was used
    expected_call = mock_client.execute.call_args[1]["variable_values"]
    assert expected_call["first"] == 50
    assert len(results) == 1


def test_null_data_path():
    """Test pagination when data path resolves to null."""
    # Mock GraphQL client
    mock_client = Mock(spec=Client)
    mock_query = Mock()

    # Prepare mock results with null data
    mock_result = {"repository": {"issues": None}}
    mock_client.execute.return_value = mock_result

    # Initialize paginator
    paginator = GraphQLPaginator(mock_client)

    # Execute pagination - should handle null gracefully
    results = paginator.paginate_all(
        query=mock_query,
        variable_values={"owner": "test", "name": "repo"},
        data_path="repository.issues",
    )

    # Should return empty list when data is null
    assert len(results) == 0


def test_large_multi_page_pagination():
    """Test pagination across many pages to ensure cursor handling."""
    # Mock GraphQL client
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
                            "endCursor": f"cursor_{i}" if not is_last_page else None,
                        },
                    }
                }
            }
        )

    mock_client.execute.side_effect = mock_results

    # Initialize paginator
    paginator = GraphQLPaginator(mock_client)

    # Execute pagination
    results = paginator.paginate_all(
        query=mock_query,
        variable_values={"owner": "test", "name": "repo"},
        data_path="repository.issues",
    )

    # Assertions
    assert len(results) == 10  # 5 pages * 2 items each
    assert mock_client.execute.call_count == 5
    # Verify we got all the expected IDs
    expected_ids = [str(i) for i in range(1, 11)]
    actual_ids = [item["id"] for item in results]
    assert actual_ids == expected_ids
