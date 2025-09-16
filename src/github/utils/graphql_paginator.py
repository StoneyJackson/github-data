from typing import Dict, List, Any, Callable, Optional
from gql import Client


class GraphQLPaginator:
    """Generic GraphQL cursor-based pagination utility."""

    def __init__(self, gql_client: Client, page_size: int = 100):
        """
        Initialize paginator with GraphQL client.

        Args:
            gql_client: GraphQL client for executing queries
            page_size: Number of items to fetch per page, defaults to 100
        """
        self._gql_client = gql_client
        self._page_size = page_size

    def _resolve_data_path(
        self, result: Dict[str, Any], data_path: str
    ) -> Dict[str, Any]:
        """
        Resolve data path from nested dictionary.

        Args:
            result: GraphQL query result dictionary
            data_path: Dot-notation path to data

        Returns:
            Resolved data dictionary
        """
        current = result
        for key in data_path.split("."):
            current = current[key]
        return current

    def paginate_all(
        self,
        query: Any,
        variable_values: Dict[str, Any],
        data_path: str,
        post_processor: Optional[
            Callable[[List[Dict[str, Any]]], List[Dict[str, Any]]]
        ] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute paginated GraphQL query and return all results.

        Args:
            query: GraphQL query object (from gql)
            variable_values: Base variables for the query (without pagination params)
            data_path: Dot-notation path to paginated data (e.g., "repository.issues")
            post_processor: Optional function to process each page of results

        Returns:
            List of all items from all pages
        """
        all_items: List[Dict[str, Any]] = []
        cursor = None

        while True:
            # Create a copy of variable values to avoid modifying the original
            pagination_variables = variable_values.copy()
            pagination_variables.update({"first": self._page_size, "after": cursor})

            # Execute the query with pagination
            result = self._gql_client.execute(
                query, variable_values=pagination_variables
            )

            # Resolve the data path
            data = self._resolve_data_path(result, data_path)

            # Optional post-processing
            page_items = data["nodes"]
            if post_processor:
                page_items = post_processor(page_items)

            # Extend all items list
            all_items.extend(page_items)

            # Check for more pages
            if not data["pageInfo"]["hasNextPage"]:
                break

            # Update cursor for next iteration
            cursor = data["pageInfo"]["endCursor"]

        return all_items
