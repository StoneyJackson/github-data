"""Tests for main entry point with EntityRegistry."""

import pytest
import os


@pytest.mark.unit
def test_no_operation():
    try:
        setup_environment()
        delete_from_environment("OPERATION")
        assert_main_errors()
    finally:
        cleanup_environment()


@pytest.mark.unit
def test_bad_operation():
    try:
        setup_environment()
        set_environment("OPERATION", "bad")
        assert_main_errors()
    finally:
        cleanup_environment()


@pytest.mark.unit
def test_no_github_token():
    try:
        setup_environment()
        delete_from_environment("GITHUB_TOKEN")
        assert_main_errors()
    finally:
        cleanup_environment()


@pytest.mark.unit
def test_no_github_repo():
    try:
        setup_environment()
        delete_from_environment("GITHUB_REPO")
        assert_main_errors()
    finally:
        cleanup_environment()


@pytest.mark.unit
def test_bad_boolean():
    try:
        setup_environment()
        set_environment("INCLUDE_ISSUES", "not_a_valid_bool")
        assert_main_errors()
    finally:
        cleanup_environment("INCLUDE_ISSUES")


def assert_main_errors():
    from github_data_tools.main import main

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1


def setup_environment():
    params = {
        "OPERATION": "SAVE",
        "GITHUB_TOKEN": "test_token",
        "GITHUB_REPO": "owner/repo",
    }
    for key, value in params.items():
        set_environment(key, value)


def set_environment(key, value):
    os.environ[key] = value


def delete_from_environment(key):
    if key in os.environ:
        del os.environ[key]


def cleanup_environment(*args):
    for key in ["OPERATION", "GITHUB_TOKEN", "GITHUB_REPO"] + list(args):
        delete_from_environment(key)


# Repository Creation Control Tests


@pytest.mark.unit
def test_load_create_repository_if_missing_default():
    """Test CREATE_REPOSITORY_IF_MISSING defaults to true."""
    from unittest.mock import patch
    from github_data_tools.main import Main

    with patch.dict(os.environ, {"OPERATION": "restore"}, clear=True):
        main = Main()
        main._operation = "restore"
        main._load_create_repository_if_missing_from_environment()

        assert main._create_repository_if_missing is True


@pytest.mark.unit
def test_load_create_repository_if_missing_true_values():
    """Test CREATE_REPOSITORY_IF_MISSING accepts true values."""
    from unittest.mock import patch
    from github_data_tools.main import Main

    for value in ["true", "True", "TRUE", "yes", "on"]:
        with patch.dict(
            os.environ, {"OPERATION": "restore", "CREATE_REPOSITORY_IF_MISSING": value}
        ):
            main = Main()
            main._operation = "restore"
            main._load_create_repository_if_missing_from_environment()

            assert (
                main._create_repository_if_missing is True
            ), f"Failed for value: {value}"


@pytest.mark.unit
def test_load_create_repository_if_missing_false_values():
    """Test CREATE_REPOSITORY_IF_MISSING accepts false values."""
    from unittest.mock import patch
    from github_data_tools.main import Main

    for value in ["false", "False", "FALSE", "no", "off"]:
        with patch.dict(
            os.environ, {"OPERATION": "restore", "CREATE_REPOSITORY_IF_MISSING": value}
        ):
            main = Main()
            main._operation = "restore"
            main._load_create_repository_if_missing_from_environment()

            assert (
                main._create_repository_if_missing is False
            ), f"Failed for value: {value}"


@pytest.mark.unit
def test_load_create_repository_if_missing_invalid_value_exits():
    """Test CREATE_REPOSITORY_IF_MISSING exits on invalid value."""
    from unittest.mock import patch
    from github_data_tools.main import Main

    with patch.dict(
        os.environ, {"OPERATION": "restore", "CREATE_REPOSITORY_IF_MISSING": "maybe"}
    ):
        main = Main()
        main._operation = "restore"

        with pytest.raises(SystemExit):
            main._load_create_repository_if_missing_from_environment()


@pytest.mark.unit
def test_load_create_repository_if_missing_skipped_for_save():
    """Test CREATE_REPOSITORY_IF_MISSING not loaded for save operation."""
    from unittest.mock import patch
    from github_data_tools.main import Main

    with patch.dict(
        os.environ, {"OPERATION": "save", "CREATE_REPOSITORY_IF_MISSING": "false"}
    ):
        main = Main()
        main._operation = "save"
        main._create_repository_if_missing = True  # Set to default
        main._load_create_repository_if_missing_from_environment()

        # Should remain at default since save operation skips loading
        assert main._create_repository_if_missing is True


@pytest.mark.unit
def test_load_repository_visibility_default():
    """Test REPOSITORY_VISIBILITY defaults to public."""
    from unittest.mock import patch
    from github_data_tools.main import Main

    with patch.dict(os.environ, {"OPERATION": "restore"}, clear=True):
        main = Main()
        main._operation = "restore"
        main._load_repository_visibility_from_environment()

        assert main._repository_visibility == "public"


@pytest.mark.unit
def test_load_repository_visibility_valid_values():
    """Test REPOSITORY_VISIBILITY accepts public and private."""
    from unittest.mock import patch
    from github_data_tools.main import Main

    for value in ["public", "Public", "PUBLIC"]:
        with patch.dict(
            os.environ, {"OPERATION": "restore", "REPOSITORY_VISIBILITY": value}
        ):
            main = Main()
            main._operation = "restore"
            main._load_repository_visibility_from_environment()

            assert main._repository_visibility == "public", f"Failed for value: {value}"

    for value in ["private", "Private", "PRIVATE"]:
        with patch.dict(
            os.environ, {"OPERATION": "restore", "REPOSITORY_VISIBILITY": value}
        ):
            main = Main()
            main._operation = "restore"
            main._load_repository_visibility_from_environment()

            assert (
                main._repository_visibility == "private"
            ), f"Failed for value: {value}"


@pytest.mark.unit
def test_load_repository_visibility_invalid_value_exits():
    """Test REPOSITORY_VISIBILITY exits on invalid value."""
    from unittest.mock import patch
    from github_data_tools.main import Main

    with patch.dict(
        os.environ, {"OPERATION": "restore", "REPOSITORY_VISIBILITY": "internal"}
    ):
        main = Main()
        main._operation = "restore"

        with pytest.raises(SystemExit):
            main._load_repository_visibility_from_environment()


@pytest.mark.unit
def test_load_repository_visibility_skipped_for_save():
    """Test REPOSITORY_VISIBILITY not loaded for save operation."""
    from unittest.mock import patch
    from github_data_tools.main import Main

    with patch.dict(
        os.environ, {"OPERATION": "save", "REPOSITORY_VISIBILITY": "private"}
    ):
        main = Main()
        main._operation = "save"
        main._repository_visibility = "public"  # Set to default
        main._load_repository_visibility_from_environment()

        # Should remain at default since save operation skips loading
        assert main._repository_visibility == "public"


# Repository Existence Check Tests


@pytest.mark.unit
def test_ensure_repository_exists_when_repo_exists():
    """Test _ensure_repository_exists does nothing when repo exists."""
    from unittest.mock import patch, MagicMock
    from github_data_tools.main import Main

    with patch.dict(os.environ, {"OPERATION": "restore"}):
        main = Main()
        main._operation = "restore"
        main._repo_name = "owner/repo"
        main._github_service = MagicMock()
        main._github_service.get_repository_metadata.return_value = {"id": 123}

        # Should not raise
        main._ensure_repository_exists()

        main._github_service.get_repository_metadata.assert_called_once_with(
            "owner/repo"
        )
        main._github_service.create_repository.assert_not_called()


@pytest.mark.unit
def test_ensure_repository_exists_creates_when_missing_and_flag_true():
    """Test _ensure_repository_exists creates repo when missing and flag is true."""
    from unittest.mock import patch, MagicMock
    from github_data_tools.main import Main

    with patch.dict(os.environ, {"OPERATION": "restore"}):
        main = Main()
        main._operation = "restore"
        main._repo_name = "owner/repo"
        main._create_repository_if_missing = True
        main._repository_visibility = "public"
        main._github_service = MagicMock()
        main._github_service.get_repository_metadata.return_value = None

        with (
            patch("builtins.print"),
            patch.object(main, "_wait_for_repository_availability"),
        ):
            main._ensure_repository_exists()

        main._github_service.create_repository.assert_called_once_with(
            "owner/repo", private=False, description=""
        )


@pytest.mark.unit
def test_ensure_repository_exists_creates_private_when_visibility_private():
    """Test _ensure_repository_exists creates private repo."""
    from unittest.mock import patch, MagicMock
    from github_data_tools.main import Main

    with patch.dict(os.environ, {"OPERATION": "restore"}):
        main = Main()
        main._operation = "restore"
        main._repo_name = "owner/repo"
        main._create_repository_if_missing = True
        main._repository_visibility = "private"
        main._github_service = MagicMock()
        main._github_service.get_repository_metadata.return_value = None

        with (
            patch("builtins.print"),
            patch.object(main, "_wait_for_repository_availability"),
        ):
            main._ensure_repository_exists()

        main._github_service.create_repository.assert_called_once_with(
            "owner/repo", private=True, description=""
        )


@pytest.mark.unit
def test_wait_for_repository_availability_succeeds_immediately():
    """Test _wait_for_repository_availability succeeds on first attempt."""
    from unittest.mock import patch, MagicMock
    from github_data_tools.main import Main

    with patch.dict(os.environ, {"OPERATION": "restore"}):
        main = Main()
        main._repo_name = "owner/repo"
        main._github_service = MagicMock()
        main._github_service.get_repository_metadata.return_value = {"id": 123}

        with patch("builtins.print"), patch("time.sleep"):
            main._wait_for_repository_availability(max_attempts=3, delay_seconds=0.1)

        # Should only call once since it succeeds immediately
        assert main._github_service.get_repository_metadata.call_count == 1


@pytest.mark.unit
def test_wait_for_repository_availability_succeeds_after_retries():
    """Test _wait_for_repository_availability succeeds after retries."""
    from unittest.mock import patch, MagicMock
    from github_data_tools.main import Main

    with patch.dict(os.environ, {"OPERATION": "restore"}):
        main = Main()
        main._repo_name = "owner/repo"
        main._github_service = MagicMock()
        # Return None first 2 times, then success
        main._github_service.get_repository_metadata.side_effect = [
            None,
            None,
            {"id": 123},
        ]

        with patch("builtins.print"), patch("time.sleep"):
            main._wait_for_repository_availability(max_attempts=5, delay_seconds=0.1)

        # Should call 3 times before succeeding
        assert main._github_service.get_repository_metadata.call_count == 3


@pytest.mark.unit
def test_wait_for_repository_availability_times_out():
    """Test _wait_for_repository_availability times out gracefully."""
    from unittest.mock import patch, MagicMock
    from github_data_tools.main import Main

    with patch.dict(os.environ, {"OPERATION": "restore"}):
        main = Main()
        main._repo_name = "owner/repo"
        main._github_service = MagicMock()
        main._github_service.get_repository_metadata.return_value = None

        with patch("builtins.print"), patch("time.sleep"):
            # Should not raise an exception even after timeout
            main._wait_for_repository_availability(max_attempts=3, delay_seconds=0.1)

        # Should call max_attempts times
        assert main._github_service.get_repository_metadata.call_count == 3


@pytest.mark.unit
def test_ensure_repository_exists_fails_when_missing_and_flag_false():
    """Test _ensure_repository_exists exits when repo missing."""
    from unittest.mock import patch, MagicMock
    from github_data_tools.main import Main

    with patch.dict(os.environ, {"OPERATION": "restore"}):
        main = Main()
        main._operation = "restore"
        main._repo_name = "owner/repo"
        main._create_repository_if_missing = False
        main._github_service = MagicMock()
        main._github_service.get_repository_metadata.return_value = None

        with pytest.raises(SystemExit):
            main._ensure_repository_exists()


@pytest.mark.unit
def test_ensure_repository_exists_skipped_for_save():
    """Test _ensure_repository_exists does nothing for save operation."""
    from unittest.mock import patch, MagicMock
    from github_data_tools.main import Main

    with patch.dict(os.environ, {"OPERATION": "save"}):
        main = Main()
        main._operation = "save"
        main._github_service = MagicMock()

        main._ensure_repository_exists()

        main._github_service.get_repository_metadata.assert_not_called()


# Integration into Main Flow Tests


@pytest.mark.unit
def test_main_calls_ensure_repository_exists_for_restore():
    """Test main() calls _ensure_repository_exists for restore."""
    from unittest.mock import patch
    from github_data_tools.main import Main

    with patch.dict(
        os.environ,
        {
            "OPERATION": "restore",
            "GITHUB_TOKEN": "token",
            "GITHUB_REPO": "owner/repo",
            "DATA_PATH": "/data",
        },
    ):
        with patch.object(Main, "_ensure_repository_exists") as mock_ensure:
            with patch.object(Main, "_execute_operation"):
                with patch.object(Main, "_build_github_service"):
                    with patch.object(Main, "_build_storage_service"):
                        with patch.object(Main, "_build_git_service"):
                            with patch.object(Main, "_build_orchestrator"):
                                main = Main()
                                main.main()

        mock_ensure.assert_called_once()


@pytest.mark.unit
def test_main_execution_order():
    """Test main() calls methods in correct order."""
    from unittest.mock import patch
    from github_data_tools.main import Main

    env = {
        "OPERATION": "restore",
        "GITHUB_TOKEN": "token",
        "GITHUB_REPO": "owner/repo",
    }
    with patch.dict(os.environ, env):
        main = Main()
        calls = []

        # Patch all methods to track call order
        with patch.object(
            main,
            "_load_operation_from_environment",
            side_effect=lambda: calls.append("load_op"),
        ):
            with patch.object(
                main,
                "_load_registry_from_environment",
                side_effect=lambda: calls.append("load_registry"),
            ):
                with patch.object(
                    main,
                    "_load_github_token_from_environment",
                    side_effect=lambda: calls.append("load_token"),
                ):
                    with patch.object(
                        main,
                        "_load_github_repo_from_environment",
                        side_effect=lambda: calls.append("load_repo"),
                    ):
                        with patch.object(
                            main,
                            "_load_data_path_from_environment",
                            side_effect=lambda: calls.append("load_path"),
                        ):
                            loader = "_load_create_repository_if_missing_from_environment"  # noqa: E501
                            with patch.object(
                                main,
                                loader,
                                side_effect=lambda: calls.append("load_create_flag"),
                            ):
                                vis_loader = "_load_repository_visibility_from_environment"  # noqa: E501
                                with patch.object(
                                    main,
                                    vis_loader,
                                    side_effect=lambda: calls.append("load_visibility"),
                                ):
                                    with patch.object(
                                        main,
                                        "_build_github_service",
                                        side_effect=lambda: calls.append(
                                            "build_github"
                                        ),
                                    ):
                                        with patch.object(
                                            main,
                                            "_build_storage_service",
                                            side_effect=lambda: calls.append(
                                                "build_storage"
                                            ),
                                        ):
                                            with patch.object(
                                                main,
                                                "_ensure_repository_exists",
                                                side_effect=lambda: calls.append(
                                                    "ensure_repo"
                                                ),
                                            ):
                                                with patch.object(
                                                    main,
                                                    "_build_git_service",
                                                    side_effect=lambda: calls.append(
                                                        "build_git"
                                                    ),
                                                ):
                                                    with patch.object(
                                                        main,
                                                        "_build_orchestrator",
                                                        side_effect=lambda: calls.append(  # noqa: E731, E501
                                                            "build_orch"
                                                        ),
                                                    ):
                                                        with patch.object(
                                                            main,
                                                            "_execute_operation",
                                                            side_effect=lambda: calls.append(  # noqa: E731, E501
                                                                "execute"
                                                            ),
                                                        ):
                                                            main.main()

        expected = [
            "load_op",
            "load_registry",
            "load_token",
            "load_repo",
            "load_path",
            "load_create_flag",
            "load_visibility",
            "build_github",
            "build_storage",
            "ensure_repo",
            "build_git",
            "build_orch",
            "execute",
        ]
        assert calls == expected
