"""GitHub service with mocked boundary fixture for testing."""

import pytest


@pytest.fixture
def github_service_with_mock(mock_boundary):
    """GitHub service with mocked boundary for testing."""
    from github_data.github.rate_limiter import RateLimitHandler
    from github_data.github.service import GitHubService

    rate_limiter = RateLimitHandler(max_retries=2, base_delay=0.1)
    return GitHubService(mock_boundary, rate_limiter)
