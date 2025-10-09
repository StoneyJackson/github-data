import pytest
from tests.shared.builders import ConfigFactory


@pytest.fixture
def base_config():
    """Base configuration for testing."""
    return ConfigFactory.create_full_config(include_sub_issues=False)


@pytest.fixture
def config_with_comments_disabled():
    """Configuration with issue comments disabled."""
    return ConfigFactory.create_full_config(
        include_issue_comments=False, include_sub_issues=False
    )


@pytest.fixture
def config_with_minimal_features():
    """Configuration with minimal features enabled."""
    return ConfigFactory.create_minimal_config()


@pytest.fixture
def restore_config():
    """Configuration for restore operations."""
    return ConfigFactory.create_restore_config(
        include_pull_requests=True,
        include_pull_request_comments=True
    )


@pytest.fixture
def config_with_pr_comments_only():
    """Configuration with PR comments enabled but PRs disabled (invalid)."""
    return ConfigFactory.create_save_config(
        include_pull_requests=False,
        include_pull_request_comments=True
    )


@pytest.fixture
def config_with_prs_no_comments():
    """Configuration with pull requests enabled but comments disabled."""
    return ConfigFactory.create_save_config(
        include_pull_requests=True,
        include_pull_request_comments=False
    )


@pytest.fixture
def config_with_prs_and_comments():
    """Configuration with both pull requests and PR comments enabled."""
    return ConfigFactory.create_pr_config()


# Environment variable fixtures have been moved to env_fixtures.py
# Import them from there if needed:
# from tests.shared.fixtures.env_fixtures import (
#     minimal_env_vars, standard_env_vars, pr_enabled_env_vars,
#     all_features_env_vars, minimal_features_env_vars
# )
