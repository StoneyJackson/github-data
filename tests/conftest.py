"""Test configuration and shared fixtures."""

import pytest
import requests_cache
import os
import time

# Import shared fixtures to make them available globally
pytest_plugins = ["tests.shared.fixtures"]

# Global test metrics collection
_test_metrics = {
    "fixture_usage": {},
    "test_durations": {},
    "memory_usage": {},
    "fixture_setup_times": {},
}


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    # Existing basic markers
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "container: Container tests")
    config.addinivalue_line("markers", "slow: Slow running tests")

    # Existing feature-specific markers
    config.addinivalue_line("markers", "labels: Label-related tests")
    config.addinivalue_line("markers", "issues: Issue-related tests")
    config.addinivalue_line("markers", "comments: Comment-related tests")
    config.addinivalue_line("markers", "errors: Error handling tests")

    # NEW: Enhanced fixture category markers
    config.addinivalue_line(
        "markers", "enhanced_fixtures: Tests using enhanced fixture patterns"
    )
    config.addinivalue_line(
        "markers", "data_builders: Tests using dynamic data builder fixtures"
    )
    config.addinivalue_line(
        "markers", "error_simulation: Tests using error simulation fixtures"
    )
    config.addinivalue_line(
        "markers", "workflow_services: Tests using workflow service fixtures"
    )
    config.addinivalue_line(
        "markers", "performance_fixtures: Tests using performance monitoring fixtures"
    )

    # NEW: Test complexity and performance markers
    config.addinivalue_line("markers", "fast: Fast running tests (< 100ms)")
    config.addinivalue_line("markers", "medium: Medium running tests (100ms - 1s)")
    config.addinivalue_line(
        "markers", "performance: Performance testing and benchmarking"
    )
    config.addinivalue_line("markers", "memory_intensive: Tests with high memory usage")

    # NEW: GitHub API scenario markers
    config.addinivalue_line(
        "markers", "empty_repository: Tests with empty repository scenarios"
    )
    config.addinivalue_line(
        "markers", "large_dataset: Tests with large dataset scenarios"
    )
    config.addinivalue_line(
        "markers", "rate_limiting: Tests involving rate limiting scenarios"
    )
    config.addinivalue_line("markers", "api_errors: Tests simulating GitHub API errors")

    # NEW: Workflow-specific markers
    config.addinivalue_line("markers", "backup_workflow: Backup workflow tests")
    config.addinivalue_line("markers", "restore_workflow: Restore workflow tests")
    config.addinivalue_line("markers", "sync_workflow: Sync workflow tests")
    config.addinivalue_line(
        "markers", "validation_workflow: Data validation workflow tests"
    )

    # NEW: Data complexity markers
    config.addinivalue_line("markers", "simple_data: Tests with simple data structures")
    config.addinivalue_line(
        "markers", "complex_hierarchy: Tests with complex hierarchical data"
    )
    config.addinivalue_line(
        "markers", "temporal_data: Tests with time-sensitive data patterns"
    )
    config.addinivalue_line(
        "markers", "mixed_states: Tests with mixed state data (open/closed, etc.)"
    )

    # Configure test execution settings
    verbose = not hasattr(config.option, "verbose") or config.option.verbose
    config.option.verbose = verbose


def pytest_runtest_setup(item):
    """Track test setup and fixture usage."""
    # Record fixture usage for this test
    fixtures_used = [
        fixture for fixture in item.fixturenames if not fixture.startswith("_")
    ]
    test_name = f"{item.nodeid}"

    _test_metrics["fixture_usage"][test_name] = fixtures_used

    # Track enhanced fixture usage specifically
    enhanced_fixtures = [
        "boundary_with_repository_data",
        "boundary_with_large_dataset",
        "backup_workflow_services",
        "github_data_builder",
        "performance_monitoring_services",
        "integration_test_environment",
    ]

    enhanced_used = [f for f in fixtures_used if f in enhanced_fixtures]
    if enhanced_used:
        # Add enhanced_fixtures marker if not already present
        has_marker = any(
            mark.name == "enhanced_fixtures" for mark in item.iter_markers()
        )
        if not has_marker:
            item.add_marker(pytest.mark.enhanced_fixtures)


def pytest_runtest_call(item):
    """Monitor test execution performance."""
    start_time = time.time()
    yield
    end_time = time.time()

    duration = end_time - start_time
    test_name = f"{item.nodeid}"
    _test_metrics["test_durations"][test_name] = duration

    # Auto-categorize by duration if not already marked
    timing_markers = ["fast", "medium", "slow"]
    has_timing_marker = any(mark.name in timing_markers for mark in item.iter_markers())

    if not has_timing_marker:
        if duration < 0.1:
            item.add_marker(pytest.mark.fast)
        elif 0.1 <= duration < 1.0:
            item.add_marker(pytest.mark.medium)
        elif duration >= 1.0:
            item.add_marker(pytest.mark.slow)


def pytest_sessionfinish(session, exitstatus):
    """Generate test metrics report after session completion."""
    if session.config.option.verbose >= 2:  # Only in very verbose mode
        print("\n" + "=" * 80)
        print("TEST METRICS SUMMARY")
        print("=" * 80)

        # Fixture usage summary
        fixture_counts = {}
        for test, fixtures in _test_metrics["fixture_usage"].items():
            for fixture in fixtures:
                fixture_counts[fixture] = fixture_counts.get(fixture, 0) + 1

        print("\nTop 10 Most Used Fixtures:")
        top_fixtures = sorted(fixture_counts.items(), key=lambda x: x[1], reverse=True)[
            :10
        ]
        for fixture, count in top_fixtures:
            print(f"  {fixture}: {count} tests")

        # Performance summary
        durations = list(_test_metrics["test_durations"].values())
        if durations:
            print("\nPerformance Summary:")
            print(f"  Total tests: {len(durations)}")
            fast_count = sum(1 for d in durations if d < 0.1)
            medium_count = sum(1 for d in durations if 0.1 <= d < 1.0)
            slow_count = sum(1 for d in durations if d >= 1.0)
            print(f"  Fast tests (< 100ms): {fast_count}")
            print(f"  Medium tests (100ms-1s): {medium_count}")
            print(f"  Slow tests (> 1s): {slow_count}")
            avg_duration = sum(durations) / len(durations)
            print(f"  Average duration: {avg_duration:.3f}s")

        print("=" * 80)


@pytest.fixture(autouse=True)
def cleanup_cache():
    """Clean up any global cache before and after each test."""
    # Clean up before test
    if requests_cache.is_installed():
        requests_cache.uninstall_cache()

    # Remove cache file if it exists
    cache_file = "github_api_cache.sqlite"
    if os.path.exists(cache_file):
        os.remove(cache_file)

    yield

    # Clean up after test
    if requests_cache.is_installed():
        requests_cache.uninstall_cache()

    # Remove cache file if it exists
    if os.path.exists(cache_file):
        os.remove(cache_file)


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment with proper isolation."""
    # Ensure clean environment for each test
    original_env = os.environ.copy()

    # Set test-specific environment variables
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "WARNING"  # Reduce log noise in tests

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture(scope="session")
def test_session_metrics():
    """Provide access to test session metrics for analysis."""
    return _test_metrics
