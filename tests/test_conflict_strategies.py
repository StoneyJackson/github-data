"""
Tests for label conflict resolution strategies.

Tests the various strategies for handling conflicts when restoring labels
that already exist in the target repository.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.operations.restore.restore import restore_repository_data_with_strategy_pattern
from src.github import create_github_service
from src.storage import create_storage_service
from src.conflict_strategies import (
    LabelConflictStrategy,
    parse_conflict_strategy,
    detect_label_conflicts,
)
from src.entities import Label


class TestConflictStrategyParsing:
    """Test parsing and validation of conflict strategy strings."""

    def test_parse_valid_strategies(self):
        """Test parsing all valid strategy strings."""
        valid_strategies = [
            ("fail-if-existing", LabelConflictStrategy.FAIL_IF_EXISTING),
            ("fail-if-conflict", LabelConflictStrategy.FAIL_IF_CONFLICT),
            ("overwrite", LabelConflictStrategy.OVERWRITE),
            ("skip", LabelConflictStrategy.SKIP),
            ("delete-all", LabelConflictStrategy.DELETE_ALL),
        ]

        for strategy_str, expected_enum in valid_strategies:
            result = parse_conflict_strategy(strategy_str)
            assert result == expected_enum

    def test_parse_invalid_strategy_raises_error(self):
        """Test that invalid strategy strings raise ValueError."""
        with pytest.raises(ValueError, match="Invalid conflict strategy 'invalid'"):
            parse_conflict_strategy("invalid")

    def test_parse_invalid_strategy_shows_valid_options(self):
        """Test that error message shows all valid options."""
        with pytest.raises(ValueError) as exc_info:
            parse_conflict_strategy("bad-strategy")

        error_message = str(exc_info.value)
        assert "fail-if-existing" in error_message
        assert "fail-if-conflict" in error_message
        assert "overwrite" in error_message
        assert "skip" in error_message
        assert "delete-all" in error_message


class TestConflictDetection:
    """Test label conflict detection logic."""

    def test_detect_conflicts_with_matching_names(self):
        """Test conflict detection when labels have matching names."""
        existing = [
            Label(
                name="bug",
                color="ff0000",
                description="Bug label",
                url="http://example.com/bug",
                id=1,
            ),
            Label(
                name="feature",
                color="00ff00",
                description="Feature label",
                url="http://example.com/feature",
                id=2,
            ),
        ]

        to_restore = [
            Label(
                name="bug",
                color="ff0000",
                description="Different bug label",
                url="http://example.com/bug2",
                id=3,
            ),
            Label(
                name="docs",
                color="0000ff",
                description="Documentation label",
                url="http://example.com/docs",
                id=4,
            ),
        ]

        conflicts = detect_label_conflicts(existing, to_restore)
        assert conflicts == ["bug"]

    def test_detect_no_conflicts_with_different_names(self):
        """Test that no conflicts are detected when all names are different."""
        existing = [
            Label(
                name="bug",
                color="ff0000",
                description="Bug label",
                url="http://example.com/bug",
                id=1,
            ),
        ]

        to_restore = [
            Label(
                name="feature",
                color="00ff00",
                description="Feature label",
                url="http://example.com/feature",
                id=2,
            ),
        ]

        conflicts = detect_label_conflicts(existing, to_restore)
        assert conflicts == []

    def test_detect_conflicts_with_empty_lists(self):
        """Test conflict detection with empty label lists."""
        assert detect_label_conflicts([], []) == []

        existing = [
            Label(
                name="bug",
                color="ff0000",
                description="Bug",
                url="http://example.com/bug",
                id=1,
            )
        ]
        assert detect_label_conflicts(existing, []) == []
        assert detect_label_conflicts([], existing) == []


@patch("src.github.service.GitHubApiBoundary")
class TestConflictStrategyIntegration:
    """Integration tests for conflict strategies with restore operation."""

    @pytest.fixture
    def sample_labels_data(self):
        """Sample label data for testing."""
        return [
            {
                "name": "bug",
                "color": "d73a4a",
                "description": "Something isn't working",
                "id": 1001,
                "url": "https://api.github.com/repos/owner/repo/labels/bug",
            },
            {
                "name": "enhancement",
                "color": "a2eeef",
                "description": "New feature or request",
                "id": 1002,
                "url": "https://api.github.com/repos/owner/repo/labels/enhancement",
            },
        ]

    def _create_test_files(self, data_dir, labels_data):
        """Helper to create test JSON files."""
        data_path = Path(data_dir)

        with open(data_path / "labels.json", "w") as f:
            json.dump(labels_data, f)
        with open(data_path / "issues.json", "w") as f:
            json.dump([], f)
        with open(data_path / "comments.json", "w") as f:
            json.dump([], f)

    def test_fail_if_existing_strategy_with_existing_labels(
        self, mock_boundary_class, temp_data_dir, sample_labels_data
    ):
        """Test fail-if-existing strategy fails when any labels exist."""
        self._create_test_files(temp_data_dir, sample_labels_data)

        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # Mock existing labels in repository
        mock_boundary.get_repository_labels.return_value = [
            {
                "name": "existing",
                "color": "ffffff",
                "description": "",
                "url": "http://example.com/existing",
                "id": 999,
            }
        ]

        # Should fail because repository has existing labels
        with pytest.raises(Exception, match="Repository has 1 existing labels"):
            github_service = create_github_service("token")
            storage_service = create_storage_service("json")
            restore_repository_data_with_strategy_pattern(
                github_service,
                storage_service,
                "owner/repo",
                temp_data_dir,
                "fail-if-existing",
            )

    def test_fail_if_existing_strategy_with_empty_repository(
        self, mock_boundary_class, temp_data_dir, sample_labels_data
    ):
        """Test fail-if-existing strategy succeeds with empty repository."""
        self._create_test_files(temp_data_dir, sample_labels_data)

        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # Mock empty repository
        mock_boundary.get_repository_labels.return_value = []
        mock_boundary.create_label.return_value = {
            "name": "test",
            "id": 1,
            "color": "ff0000",
            "url": "http://example.com/test",
        }

        # Should succeed because repository is empty
        github_service = create_github_service("token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            "fail-if-existing",
        )

        # Verify labels were created
        assert mock_boundary.create_label.call_count == 2

    def test_fail_if_conflict_strategy_with_conflicts(
        self, mock_boundary_class, temp_data_dir, sample_labels_data
    ):
        """Test fail-if-conflict strategy fails when conflicts exist."""
        self._create_test_files(temp_data_dir, sample_labels_data)

        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # Mock existing labels that conflict with restore data
        mock_boundary.get_repository_labels.return_value = [
            {
                "name": "bug",
                "color": "ff0000",
                "description": "Different bug",
                "url": "http://example.com/bug",
                "id": 999,
            }
        ]

        # Should fail because 'bug' label conflicts
        with pytest.raises(Exception, match="Label conflicts detected: bug"):
            github_service = create_github_service("token")
            storage_service = create_storage_service("json")
            restore_repository_data_with_strategy_pattern(
                github_service,
                storage_service,
                "owner/repo",
                temp_data_dir,
                "fail-if-conflict",
            )

    def test_fail_if_conflict_strategy_without_conflicts(
        self, mock_boundary_class, temp_data_dir, sample_labels_data
    ):
        """Test fail-if-conflict strategy succeeds without conflicts."""
        self._create_test_files(temp_data_dir, sample_labels_data)

        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # Mock existing labels that don't conflict
        mock_boundary.get_repository_labels.return_value = [
            {
                "name": "docs",
                "color": "ffffff",
                "description": "Documentation",
                "url": "http://example.com/docs",
                "id": 999,
            }
        ]
        mock_boundary.create_label.return_value = {
            "name": "test",
            "id": 1,
            "color": "ff0000",
            "url": "http://example.com/test",
        }

        # Should succeed because no conflicts
        github_service = create_github_service("token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            "fail-if-conflict",
        )

        # Verify labels were created
        assert mock_boundary.create_label.call_count == 2

    def test_delete_all_strategy(
        self, mock_boundary_class, temp_data_dir, sample_labels_data
    ):
        """Test delete-all strategy deletes existing labels then creates new ones."""
        self._create_test_files(temp_data_dir, sample_labels_data)

        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # Mock existing labels
        mock_boundary.get_repository_labels.return_value = [
            {
                "name": "old1",
                "color": "ffffff",
                "description": "",
                "url": "http://example.com/old1",
                "id": 1,
            },
            {
                "name": "old2",
                "color": "000000",
                "description": "",
                "url": "http://example.com/old2",
                "id": 2,
            },
        ]
        mock_boundary.create_label.return_value = {
            "name": "test",
            "id": 1,
            "color": "ff0000",
            "url": "http://example.com/test",
        }

        github_service = create_github_service("token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service, storage_service, "owner/repo", temp_data_dir, "delete-all"
        )

        # Verify existing labels were deleted
        assert mock_boundary.delete_label.call_count == 2
        mock_boundary.delete_label.assert_any_call("owner/repo", "old1")
        mock_boundary.delete_label.assert_any_call("owner/repo", "old2")

        # Verify new labels were created
        assert mock_boundary.create_label.call_count == 2

    def test_skip_strategy(
        self, mock_boundary_class, temp_data_dir, sample_labels_data
    ):
        """Test skip strategy skips conflicting labels and creates others."""
        self._create_test_files(temp_data_dir, sample_labels_data)

        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # Mock existing label that conflicts with first restore label
        mock_boundary.get_repository_labels.return_value = [
            {
                "name": "bug",
                "color": "ff0000",
                "description": "Existing bug",
                "url": "http://example.com/bug",
                "id": 999,
            }
        ]
        mock_boundary.create_label.return_value = {
            "name": "test",
            "id": 1,
            "color": "ff0000",
            "url": "http://example.com/test",
        }

        github_service = create_github_service("token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service, storage_service, "owner/repo", temp_data_dir, "skip"
        )

        # Verify only non-conflicting label was created (enhancement, not bug)
        assert mock_boundary.create_label.call_count == 1
        mock_boundary.create_label.assert_called_once()

        # Get the actual call arguments to verify it was 'enhancement'
        call_args = mock_boundary.create_label.call_args
        # Arguments are: (repo_name, label.name, label.color, label.description)
        assert call_args[0][1] == "enhancement"

    def test_overwrite_strategy(
        self, mock_boundary_class, temp_data_dir, sample_labels_data
    ):
        """Test overwrite strategy updates existing and creates new labels."""
        self._create_test_files(temp_data_dir, sample_labels_data)

        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # Mock existing label that conflicts with first restore label
        mock_boundary.get_repository_labels.return_value = [
            {
                "name": "bug",
                "color": "ff0000",
                "description": "Old bug",
                "url": "http://example.com/bug",
                "id": 999,
            }
        ]
        mock_boundary.create_label.return_value = {
            "name": "test",
            "id": 1,
            "color": "ff0000",
            "url": "http://example.com/test",
        }
        mock_boundary.update_label.return_value = {
            "name": "bug",
            "id": 999,
            "color": "d73a4a",
            "url": "http://example.com/bug",
        }

        github_service = create_github_service("token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service, storage_service, "owner/repo", temp_data_dir, "overwrite"
        )

        # Verify conflicting label was deleted first (overwrite deletes then recreates)
        assert mock_boundary.delete_label.call_count == 1
        delete_call = mock_boundary.delete_label.call_args
        assert delete_call[0][1] == "bug"  # deleted label name

        # Verify all labels were created (both conflicting and non-conflicting)
        assert mock_boundary.create_label.call_count == 2
        create_calls = mock_boundary.create_label.call_args_list
        # Arguments are: (repo_name, label.name, label.color, label.description)
        created_names = [call[0][1] for call in create_calls]
        assert "bug" in created_names
        assert "enhancement" in created_names
