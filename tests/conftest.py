"""Global test configuration and marker definitions."""

import pytest
import requests_cache
import os
import time

# Import shared fixtures for global availability
pytest_plugins = [
    "tests.shared.fixtures.enhanced.performance_fixtures",
    "tests.shared.fixtures.enhanced.data_builder_fixtures",
    "tests.shared.fixtures.enhanced.integration_fixtures",
    # Core Infrastructure Fixtures
    "tests.shared.fixtures.core.temp_data_dir",
    "tests.shared.fixtures.core.github_service_mock",
    "tests.shared.fixtures.core.storage_service_mock",
    "tests.shared.fixtures.core.mock_boundary_class",
    "tests.shared.fixtures.core.mock_boundary",
    "tests.shared.fixtures.core.github_service_with_mock",
    # Test Data Fixtures
    "tests.shared.fixtures.test_data.sample_github_data",
    "tests.shared.fixtures.test_data.empty_repository_data",
    "tests.shared.fixtures.test_data.sample_sub_issues_data",
    "tests.shared.fixtures.test_data.complex_hierarchy_data",
    "tests.shared.fixtures.test_data.sample_pr_data",
    "tests.shared.fixtures.test_data.sample_labels_data",
    "tests.shared.fixtures.test_data.chronological_comments_data",
    "tests.shared.fixtures.test_data.orphaned_sub_issues_data",
    "tests.shared.fixtures.test_data.mixed_states_data",
    # Boundary Mock Fixtures
    "tests.shared.fixtures.boundary_mocks.boundary_with_repository_data",
    "tests.shared.fixtures.boundary_mocks.boundary_with_empty_repository",
    "tests.shared.fixtures.boundary_mocks.boundary_with_large_dataset",
    "tests.shared.fixtures.boundary_mocks.boundary_with_pr_workflow_data",
    "tests.shared.fixtures.boundary_mocks.boundary_with_sub_issues_hierarchy",
    # Error Simulation Fixtures
    "tests.shared.fixtures.error_simulation.boundary_with_api_errors",
    "tests.shared.fixtures.error_simulation.boundary_with_partial_failures",
    "tests.shared.fixtures.error_simulation.boundary_with_rate_limiting",
    # Workflow Service Fixtures
    "tests.shared.fixtures.workflow_services.save_workflow_services",
    "tests.shared.fixtures.workflow_services.restore_workflow_services",
    "tests.shared.fixtures.workflow_services.sync_workflow_services",
    "tests.shared.fixtures.workflow_services.error_handling_workflow_services",
    # Support Fixtures
    "tests.shared.fixtures.support.boundary_factory",
    "tests.shared.fixtures.support.boundary_with_data",
    "tests.shared.fixtures.support.storage_service_for_temp_dir",
    # Configuration Fixtures
    "tests.shared.fixtures.env_fixtures",
    "tests.shared.fixtures.config_fixtures",
]

for i in pytest_plugins:
    pytest.register_assert_rewrite(i)

# Global test metrics collection
_test_metrics = {
    "fixture_usage": {},
    "test_durations": {},
    "memory_usage": {},
    "fixture_setup_times": {},
}


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add automatic markers based on test patterns."""

    for item in items:
        # Auto-mark container tests
        if "container" in item.nodeid or "docker" in item.nodeid:
            item.add_marker(pytest.mark.container)
            item.add_marker(pytest.mark.slow)

        # Auto-mark integration tests
        elif "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.medium)

        # Auto-mark unit tests (default for non-integration/container)
        else:
            item.add_marker(pytest.mark.unit)
            item.add_marker(pytest.mark.fast)

        # Auto-mark by feature area based on filename
        if "sub_issues" in item.nodeid:
            item.add_marker(pytest.mark.sub_issues)
        elif "pr_" in item.nodeid or "pull_request" in item.nodeid:
            item.add_marker(pytest.mark.pull_requests)
        elif "conflict" in item.nodeid:
            item.add_marker(pytest.mark.labels)  # Conflicts typically with labels
        elif "label" in item.nodeid:
            item.add_marker(pytest.mark.labels)
        elif "issue" in item.nodeid:
            item.add_marker(pytest.mark.issues)
        elif "comment" in item.nodeid:
            item.add_marker(pytest.mark.comments)

        # Auto-mark GitHub API tests
        if hasattr(item, "function") and item.function:
            if "github" in str(item.function.__code__.co_names).lower():
                item.add_marker(pytest.mark.github_api)


def pytest_runtest_setup(item):
    """Setup hook for individual test execution."""
    # Skip slow tests in fast mode
    if item.config.getoption("--fast", default=False):
        if item.get_closest_marker("slow"):
            pytest.skip("Skipping slow test in fast mode")

    # Skip container tests if Docker not available
    if item.get_closest_marker("container"):
        try:
            import docker

            client = docker.from_env()
            client.ping()
        except Exception:
            pytest.skip("Docker not available for container tests")

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
        "save_workflow_services",
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


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--fast",
        action="store_true",
        default=False,
        help="Run only fast tests (skip slow and container tests)",
    )
    parser.addoption(
        "--unit-only", action="store_true", default=False, help="Run only unit tests"
    )
    parser.addoption(
        "--integration-only",
        action="store_true",
        default=False,
        help="Run only integration tests",
    )
    parser.addoption(
        "--container-only",
        action="store_true",
        default=False,
        help="Run only container tests",
    )


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
