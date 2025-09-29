import pytest
from src.config.settings import ApplicationConfig


@pytest.fixture
def base_config():
    """Base configuration for testing."""
    return ApplicationConfig(
        operation="save",
        github_token="test-token",
        github_repo="test-owner/test-repo",
        data_path="/tmp/test-data",
        label_conflict_strategy="fail-if-existing",
        include_git_repo=True,
        include_issue_comments=True,
        include_pull_requests=False,
        include_sub_issues=False,
        git_auth_method="token",
    )


@pytest.fixture
def config_with_comments_disabled(base_config):
    """Configuration with issue comments disabled."""
    config = ApplicationConfig(
        operation=base_config.operation,
        github_token=base_config.github_token,
        github_repo=base_config.github_repo,
        data_path=base_config.data_path,
        label_conflict_strategy=base_config.label_conflict_strategy,
        include_git_repo=base_config.include_git_repo,
        include_issue_comments=False,
        include_pull_requests=base_config.include_pull_requests,
        include_sub_issues=base_config.include_sub_issues,
        git_auth_method=base_config.git_auth_method,
    )
    return config


@pytest.fixture
def config_with_minimal_features(base_config):
    """Configuration with minimal features enabled."""
    config = ApplicationConfig(
        operation=base_config.operation,
        github_token=base_config.github_token,
        github_repo=base_config.github_repo,
        data_path=base_config.data_path,
        label_conflict_strategy=base_config.label_conflict_strategy,
        include_git_repo=False,
        include_issue_comments=False,
        include_pull_requests=False,
        include_sub_issues=False,
        git_auth_method=base_config.git_auth_method,
    )
    return config


@pytest.fixture
def restore_config(base_config):
    """Configuration for restore operations."""
    config = ApplicationConfig(
        operation="restore",
        github_token=base_config.github_token,
        github_repo=base_config.github_repo,
        data_path=base_config.data_path,
        label_conflict_strategy=base_config.label_conflict_strategy,
        include_git_repo=base_config.include_git_repo,
        include_issue_comments=base_config.include_issue_comments,
        include_pull_requests=base_config.include_pull_requests,
        include_sub_issues=base_config.include_sub_issues,
        git_auth_method=base_config.git_auth_method,
    )
    return config
