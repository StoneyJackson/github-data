"""Boundary with rate limiting fixture for testing."""

import pytest


@pytest.fixture
def boundary_with_rate_limiting():
    """Boundary mock that simulates rate limiting scenarios."""
    from unittest.mock import Mock

    boundary = Mock()

    # First call succeeds, subsequent calls hit rate limit
    def rate_limited_response():
        if not hasattr(rate_limited_response, "call_count"):
            rate_limited_response.call_count = 0
        rate_limited_response.call_count += 1

        if rate_limited_response.call_count == 1:
            return []
        else:
            raise Exception("Rate limit exceeded, retry after 60 seconds")

    boundary.get_repository_labels.side_effect = rate_limited_response
    boundary.get_repository_issues.side_effect = rate_limited_response
    boundary.get_all_issue_comments.side_effect = rate_limited_response
    boundary.get_repository_pull_requests.side_effect = rate_limited_response
    boundary.get_all_pull_request_comments.side_effect = rate_limited_response
    boundary.get_repository_sub_issues.side_effect = rate_limited_response

    return boundary
