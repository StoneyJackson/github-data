"""Performance testing fixtures for advanced testing patterns."""

import pytest


@pytest.fixture
def performance_monitoring_services(boundary_with_large_dataset, temp_data_dir):
    """Services configured for performance monitoring and timing tests."""
    from src.github.service import GitHubService
    from src.github.rate_limiter import RateLimitHandler
    from src.storage import create_storage_service
    import time

    # Create timing-aware boundary mock
    class TimingBoundaryWrapper:
        def __init__(self, boundary):
            self.boundary = boundary
            self.call_times = {}

        def __getattr__(self, name):
            original_method = getattr(self.boundary, name)

            def timed_method(*args, **kwargs):
                start_time = time.time()
                result = original_method(*args, **kwargs)
                end_time = time.time()

                if name not in self.call_times:
                    self.call_times[name] = []
                self.call_times[name].append(end_time - start_time)

                return result

            return timed_method

    # Wrap boundary with timing monitoring
    timing_boundary = TimingBoundaryWrapper(boundary_with_large_dataset)

    # Configure services
    rate_limiter = RateLimitHandler(max_retries=2, base_delay=0.1)
    github_service = GitHubService(timing_boundary, rate_limiter)
    storage_service = create_storage_service("json")
    storage_service._base_path = temp_data_dir

    return {
        "github": github_service,
        "storage": storage_service,
        "temp_dir": temp_data_dir,
        "timing_boundary": timing_boundary,
    }


@pytest.fixture
def rate_limiting_test_services(boundary_with_rate_limiting, temp_data_dir):
    """Services configured for rate limiting behavior testing."""
    from src.github.service import GitHubService
    from src.github.rate_limiter import RateLimitHandler
    from src.storage import create_storage_service

    # Configure rate limiter with specific settings for testing
    rate_limiter = RateLimitHandler(
        max_retries=2,
        base_delay=0.01,  # Fast retry for testing
        max_delay=0.05,  # Short max delay for testing
        jitter=False,  # Disable jitter for predictable testing
    )

    github_service = GitHubService(boundary_with_rate_limiting, rate_limiter)
    storage_service = create_storage_service("json")

    return {
        "github": github_service,
        "storage": storage_service,
        "temp_dir": temp_data_dir,
        "rate_limiter": rate_limiter,
    }
