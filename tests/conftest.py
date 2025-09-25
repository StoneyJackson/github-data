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
    "tests.shared.fixtures.workflow_services.backup_workflow_services",
    "tests.shared.fixtures.workflow_services.restore_workflow_services",
    "tests.shared.fixtures.workflow_services.sync_workflow_services",
    "tests.shared.fixtures.workflow_services.error_handling_workflow_services",
    # Support Fixtures
    "tests.shared.fixtures.support.boundary_factory",
    "tests.shared.fixtures.support.boundary_with_data",
    "tests.shared.fixtures.support.storage_service_for_temp_dir",
]

# Global test metrics collection
_test_metrics = {
    "fixture_usage": {},
    "test_durations": {},
    "memory_usage": {},
    "fixture_setup_times": {},
}


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""

    # Performance markers
    config.addinivalue_line(
        "markers", "fast: marks tests as fast (< 1 second) - suitable for TDD cycles"
    )
    config.addinivalue_line(
        "markers",
        "medium: marks tests as medium speed (1-10 seconds) - integration tests",
    )
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (> 10 seconds) - container/end-to-end tests",
    )

    # Test type markers
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests - isolated component testing"
    )
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests - component interactions",
    )
    config.addinivalue_line(
        "markers", "container: marks tests as container tests - full Docker workflows"
    )

    # Feature area markers
    config.addinivalue_line(
        "markers", "labels: marks tests related to label management functionality"
    )
    config.addinivalue_line(
        "markers", "issues: marks tests related to issue management functionality"
    )
    config.addinivalue_line(
        "markers", "comments: marks tests related to comment management functionality"
    )
    config.addinivalue_line(
        "markers",
        "sub_issues: marks tests related to sub-issues workflow functionality",
    )
    config.addinivalue_line(
        "markers",
        "pull_requests: marks tests related to pull request workflow functionality",
    )
    config.addinivalue_line(
        "markers",
        "git_repositories: "
        "marks tests related to Git repository backup/restore functionality",
    )

    # Infrastructure markers
    config.addinivalue_line(
        "markers",
        "github_api: marks tests that interact with GitHub API (real or mocked)",
    )
    config.addinivalue_line(
        "markers", "storage: marks tests related to data storage and persistence"
    )
    config.addinivalue_line(
        "markers", "backup_workflow: marks tests for backup operation workflows"
    )
    config.addinivalue_line(
        "markers", "restore_workflow: marks tests for restore operation workflows"
    )

    # Special scenario markers
    config.addinivalue_line(
        "markers", "empty_repository: marks tests using empty repository scenarios"
    )
    config.addinivalue_line(
        "markers", "large_dataset: marks tests using large dataset scenarios"
    )
    config.addinivalue_line(
        "markers", "rate_limiting: marks tests that verify rate limiting behavior"
    )
    config.addinivalue_line(
        "markers", "error_simulation: marks tests that simulate error conditions"
    )

    # Enhanced fixture category markers (existing)
    config.addinivalue_line(
        "markers", "enhanced_fixtures: Tests using enhanced fixture patterns"
    )
    config.addinivalue_line(
        "markers", "data_builders: Tests using dynamic data builder fixtures"
    )
    config.addinivalue_line(
        "markers", "workflow_services: Tests using workflow service fixtures"
    )
    config.addinivalue_line(
        "markers", "performance_fixtures: Tests using performance monitoring fixtures"
    )

    # Additional performance and complexity markers
    config.addinivalue_line(
        "markers", "performance: Performance testing and benchmarking"
    )
    config.addinivalue_line("markers", "memory_intensive: Tests with high memory usage")
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
    config.addinivalue_line(
        "markers",
        "cross_component_interaction: "
        "Tests validating interactions between multiple components",
    )
    config.addinivalue_line(
        "markers", "data_enrichment: Tests for data enrichment utilities"
    )

    # Additional compatibility markers
    config.addinivalue_line("markers", "errors: Error handling tests (legacy marker)")
    config.addinivalue_line(
        "markers", "docker: Docker-related tests (legacy marker, use container instead)"
    )


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
