"""Enhanced environment variable fixtures for testing.

Provides fixture patterns for environment variable testing scenarios
using the new ConfigBuilder and ConfigFactory utilities.
"""

import os
import pytest
from contextlib import contextmanager
from typing import Dict
from unittest.mock import patch

from tests.shared.builders import ConfigBuilder, ConfigFactory
from src.config.settings import ApplicationConfig


@pytest.fixture
def minimal_env_vars():
    """Minimal required environment variables for testing."""
    return {
        "OPERATION": "save",
        "GITHUB_TOKEN": "test-token",
        "GITHUB_REPO": "test-owner/test-repo",
    }


@pytest.fixture
def standard_env_vars(minimal_env_vars):
    """Standard environment variables with common defaults."""
    return {
        **minimal_env_vars,
        "DATA_PATH": "/tmp/test-data",
        "LABEL_CONFLICT_STRATEGY": "skip",
        "INCLUDE_GIT_REPO": "true",
        "INCLUDE_ISSUES": "true",
        "INCLUDE_ISSUE_COMMENTS": "true",
        "INCLUDE_PULL_REQUESTS": "true",
        "INCLUDE_PULL_REQUEST_COMMENTS": "true",
        "INCLUDE_SUB_ISSUES": "true",
        "GIT_AUTH_METHOD": "token",
    }


@pytest.fixture
def pr_enabled_env_vars(standard_env_vars):
    """Environment variables with pull request features enabled."""
    return {
        **standard_env_vars,
        "INCLUDE_PULL_REQUESTS": "true",
        "INCLUDE_PULL_REQUEST_COMMENTS": "true",
    }


@pytest.fixture
def minimal_features_env_vars(minimal_env_vars):
    """Environment variables with minimal features enabled."""
    return {
        **minimal_env_vars,
        "DATA_PATH": "/tmp/test-data",
        "INCLUDE_GIT_REPO": "false",
        "INCLUDE_ISSUES": "false",
        "INCLUDE_ISSUE_COMMENTS": "false",
        "INCLUDE_PULL_REQUESTS": "false",
        "INCLUDE_PULL_REQUEST_COMMENTS": "false",
        "INCLUDE_SUB_ISSUES": "false",
    }


@pytest.fixture
def all_features_env_vars(standard_env_vars):
    """Environment variables with all features enabled."""
    return {
        **standard_env_vars,
        "INCLUDE_GIT_REPO": "true",
        "INCLUDE_ISSUES": "true",
        "INCLUDE_ISSUE_COMMENTS": "true",
        "INCLUDE_PULL_REQUESTS": "true",
        "INCLUDE_PULL_REQUEST_COMMENTS": "true",
        "INCLUDE_SUB_ISSUES": "true",
    }


@pytest.fixture
def restore_env_vars(standard_env_vars):
    """Environment variables for restore operations."""
    return {
        **standard_env_vars,
        "OPERATION": "restore",
    }


@pytest.fixture
def issues_only_env_vars(minimal_env_vars):
    """Environment variables for issues and comments only."""
    return {
        **minimal_env_vars,
        "DATA_PATH": "/tmp/test-data",
        "INCLUDE_GIT_REPO": "false",
        "INCLUDE_ISSUES": "true",
        "INCLUDE_ISSUE_COMMENTS": "true",
        "INCLUDE_PULL_REQUESTS": "false",
        "INCLUDE_PULL_REQUEST_COMMENTS": "false",
        "INCLUDE_SUB_ISSUES": "false",
    }


@pytest.fixture
def config_builder():
    """Provide a fresh ConfigBuilder instance for each test."""
    return ConfigBuilder()


@pytest.fixture
def config_factory():
    """Provide access to ConfigFactory for each test."""
    return ConfigFactory


@contextmanager
def env_config(**env_overrides):
    """Context manager for environment variable testing.

    Example usage:
        def test_something():
            with env_config(INCLUDE_PULL_REQUESTS="true") as config:
                assert config.include_pull_requests is True
    """
    base_env = {
        "OPERATION": "save",
        "GITHUB_TOKEN": "test-token",
        "GITHUB_REPO": "test-owner/test-repo",
        "DATA_PATH": "/tmp/test-data",
        "LABEL_CONFLICT_STRATEGY": "skip",
        "INCLUDE_GIT_REPO": "true",
        "INCLUDE_ISSUES": "true",
        "INCLUDE_ISSUE_COMMENTS": "true",
        "INCLUDE_PULL_REQUESTS": "true",
        "INCLUDE_PULL_REQUEST_COMMENTS": "true",
        "INCLUDE_SUB_ISSUES": "true",
        "GIT_AUTH_METHOD": "token",
    }

    env_vars = {**base_env, **env_overrides}

    with patch.dict(os.environ, env_vars, clear=True):
        yield ApplicationConfig.from_environment()


@pytest.fixture
def env_config_context():
    """Provide the env_config context manager as a fixture."""
    return env_config


def make_env_vars(**overrides) -> Dict[str, str]:
    """Helper function to create environment variable dictionaries.

    Args:
        **overrides: Environment variable overrides

    Returns:
        Dictionary of environment variables

    Example:
        env_vars = make_env_vars(INCLUDE_PULL_REQUESTS="true")
    """
    base_env = {
        "OPERATION": "save",
        "GITHUB_TOKEN": "test-token",
        "GITHUB_REPO": "test-owner/test-repo",
        "DATA_PATH": "/tmp/test-data",
        "LABEL_CONFLICT_STRATEGY": "skip",
        "INCLUDE_GIT_REPO": "true",
        "INCLUDE_ISSUES": "true",
        "INCLUDE_ISSUE_COMMENTS": "true",
        "INCLUDE_PULL_REQUESTS": "true",
        "INCLUDE_PULL_REQUEST_COMMENTS": "true",
        "INCLUDE_SUB_ISSUES": "true",
        "GIT_AUTH_METHOD": "token",
    }

    return {**base_env, **overrides}
