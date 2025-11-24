"""Tests for main entry point with EntityRegistry."""

import pytest
from unittest.mock import patch, Mock
import os


@pytest.mark.unit
@patch("github_data.main.StrategyBasedSaveOrchestrator")
@patch("github_data.main.EntityRegistry")
@patch("github_data.main.create_github_service")
@patch("github_data.main.create_storage_service")
def test_main_initializes_registry_from_environment(
    mock_storage_factory,
    mock_github_factory,
    mock_registry_class,
    mock_orchestrator_class,
):
    """Test main initializes EntityRegistry from environment."""
    from github_data.main import main

    # Set up environment
    os.environ["OPERATION"] = "save"
    os.environ["GITHUB_TOKEN"] = "test_token"
    os.environ["GITHUB_REPO"] = "owner/repo"

    # Mock registry
    registry_instance = Mock()
    registry_instance.get_enabled_entities.return_value = []
    git_repo_entity = Mock()
    git_repo_entity.is_enabled.return_value = False
    registry_instance.get_entity.return_value = git_repo_entity
    mock_registry_class.from_environment.return_value = registry_instance

    # Mock orchestrator
    orchestrator_instance = Mock()
    orchestrator_instance.execute.return_value = []
    mock_orchestrator_class.return_value = orchestrator_instance

    try:
        main()

        # Verify registry initialized from environment
        mock_registry_class.from_environment.assert_called_once_with(is_strict=False)
    finally:
        # Cleanup
        del os.environ["OPERATION"]
        del os.environ["GITHUB_TOKEN"]
        del os.environ["GITHUB_REPO"]


@pytest.mark.unit
def test_main_passes_registry_to_orchestrator():
    """Test main passes registry to orchestrator constructor."""
    # Implementation test for registry usage
    pass


@pytest.mark.unit
@patch("github_data.main.StrategyBasedSaveOrchestrator")
@patch("github_data.main.EntityRegistry")
@patch("github_data.main.create_github_service")
@patch("github_data.main.create_storage_service")
def test_main_exits_with_error_code_on_save_failure(
    mock_storage_factory,
    mock_github_factory,
    mock_registry_class,
    mock_orchestrator_class,
):
    """Test main exits with non-zero code when save operation has failures."""
    from github_data.main import main

    # Set up environment
    os.environ["OPERATION"] = "save"
    os.environ["GITHUB_TOKEN"] = "fake_token"
    os.environ["GITHUB_REPO"] = "owner/repo"

    # Mock registry
    registry_instance = Mock()
    registry_instance.get_enabled_entities.return_value = []
    git_repo_entity = Mock()
    git_repo_entity.is_enabled.return_value = False
    registry_instance.get_entity.return_value = git_repo_entity
    mock_registry_class.from_environment.return_value = registry_instance

    # Mock orchestrator to return a result with success=False
    orchestrator_instance = Mock()
    orchestrator_instance.execute_save.return_value = [
        {"entity_name": "milestones", "success": False, "error": "401 Unauthorized"}
    ]
    mock_orchestrator_class.return_value = orchestrator_instance

    try:
        # Should exit with code 1
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
    finally:
        # Cleanup
        del os.environ["OPERATION"]
        del os.environ["GITHUB_TOKEN"]
        del os.environ["GITHUB_REPO"]
