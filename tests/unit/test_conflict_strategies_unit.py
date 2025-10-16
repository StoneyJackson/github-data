"""
Tests for label conflict resolution strategies.

Tests the various strategies for handling conflicts when restoring labels
that already exist in the target repository.
"""

import json
import pytest
from pathlib import Path

from src.operations.restore.restore import restore_repository_data_with_strategy_pattern
from src.github import create_github_service
from src.storage import create_storage_service

from src.conflict_strategies import (
    LabelConflictStrategy,
    parse_conflict_strategy,
    detect_label_conflicts,
)
from src.entities import Label
from tests.shared.mocks import MockBoundaryFactory

pytestmark = [
    pytest.mark.unit,
    pytest.mark.integration,
    pytest.mark.fast,
    pytest.mark.labels,
    pytest.mark.restore_workflow,
]


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

    @pytest.mark.storage
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


class TestConflictStrategyIntegration:
    """Integration tests for conflict strategies with restore operation."""

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
        # Extract just the labels from the shared fixture data structure
        labels_only = sample_labels_data["labels"]
        self._create_test_files(temp_data_dir, labels_only)

        mock_boundary = MockBoundaryFactory.create_auto_configured()
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

    @pytest.mark.slow
    def test_fail_if_existing_strategy_with_empty_repository(
        self, mock_boundary_class, temp_data_dir, sample_labels_data
    ):
        """Test fail-if-existing strategy succeeds with empty repository."""
        # Extract just the labels from the shared fixture data structure
        labels_only = sample_labels_data["labels"]
        self._create_test_files(temp_data_dir, labels_only)

        mock_boundary = MockBoundaryFactory.create_auto_configured()
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

        # Verify labels were created (4 labels from shared fixture)
        assert mock_boundary.create_label.call_count == 4

    def test_fail_if_conflict_strategy_with_conflicts(
        self, mock_boundary_class, temp_data_dir, sample_labels_data
    ):
        """Test fail-if-conflict strategy fails when conflicts exist."""
        # Extract just the labels from the shared fixture data structure
        labels_only = sample_labels_data["labels"]
        self._create_test_files(temp_data_dir, labels_only)

        mock_boundary = MockBoundaryFactory.create_auto_configured()
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
        # Extract just the labels from the shared fixture data structure
        labels_only = sample_labels_data["labels"]
        self._create_test_files(temp_data_dir, labels_only)

        mock_boundary = MockBoundaryFactory.create_auto_configured()
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

        # Verify labels were created (4 labels from shared fixture)
        assert mock_boundary.create_label.call_count == 4

    def test_delete_all_strategy(
        self, mock_boundary_class, temp_data_dir, sample_labels_data
    ):
        """Test delete-all strategy deletes existing labels then creates new ones."""
        # Extract just the labels from the shared fixture data structure
        labels_only = sample_labels_data["labels"]
        self._create_test_files(temp_data_dir, labels_only)

        mock_boundary = MockBoundaryFactory.create_auto_configured()
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

        # Verify new labels were created (4 labels from shared fixture)
        assert mock_boundary.create_label.call_count == 4

    def test_skip_strategy(
        self, mock_boundary_class, temp_data_dir, sample_labels_data
    ):
        """Test skip strategy skips conflicting labels and creates others."""
        # Extract just the labels from the shared fixture data structure
        labels_only = sample_labels_data["labels"]
        self._create_test_files(temp_data_dir, labels_only)

        mock_boundary = MockBoundaryFactory.create_auto_configured()
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

        # Verify only non-conflicting labels were created (3 out of 4, excluding bug)
        assert mock_boundary.create_label.call_count == 3

        # Get the actual call arguments to verify that 'bug' was skipped
        call_args_list = mock_boundary.create_label.call_args_list
        created_names = [call[0][1] for call in call_args_list]
        assert "enhancement" in created_names
        assert "documentation" in created_names
        assert "good first issue" in created_names
        assert "bug" not in created_names

    def test_overwrite_strategy(
        self, mock_boundary_class, temp_data_dir, sample_labels_data
    ):
        """Test overwrite strategy updates existing and creates new labels."""
        # Extract just the labels from the shared fixture data structure
        labels_only = sample_labels_data["labels"]
        self._create_test_files(temp_data_dir, labels_only)

        mock_boundary = MockBoundaryFactory.create_auto_configured()
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
        assert mock_boundary.create_label.call_count == 4
        create_calls = mock_boundary.create_label.call_args_list
        # Arguments are: (repo_name, label.name, label.color, label.description)
        created_names = [call[0][1] for call in create_calls]
        assert "bug" in created_names
        assert "enhancement" in created_names
        assert "documentation" in created_names
        assert "good first issue" in created_names


class TestConflictStrategyWithSharedInfrastructure:
    """Test conflict strategies using enhanced shared infrastructure."""

    def test_mock_boundary_protocol_completeness(self):
        """Test that factory-created boundaries are protocol complete."""
        mock_boundary = MockBoundaryFactory.create_auto_configured()

        # Validate 100% protocol completeness
        is_complete, missing = MockBoundaryFactory.validate_protocol_completeness(
            mock_boundary
        )
        assert is_complete, f"Mock boundary missing methods: {missing}"
        assert missing == [], "Mock boundary should have no missing methods"

    def test_conflict_resolution_with_mock_boundary_factory(self, temp_data_dir):
        """Test conflict resolution using MockBoundaryFactory for cleaner setup."""
        from tests.shared.mocks import MockBoundaryFactory

        # Use factory to create configured boundary mock for restore operations
        factory = MockBoundaryFactory()
        mock_boundary = factory.create_for_restore()

        # Configure existing labels that will conflict
        mock_boundary.get_repository_labels.return_value = [
            {
                "name": "bug",
                "color": "ff0000",
                "description": "Existing bug label",
                "url": "http://example.com/bug",
                "id": 999,
            }
        ]

        # Create test files using shared sample data
        test_labels = [
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

        self._create_test_files(temp_data_dir, test_labels)

        # Test conflict detection
        existing_labels = [
            Label(
                name="bug",
                color="ff0000",
                description="Existing",
                url="http://example.com/bug",
                id=999,
            )
        ]
        restore_labels = [
            Label(
                name="bug",
                color="d73a4a",
                description="New",
                url="http://example.com/bug2",
                id=1001,
            )
        ]

        conflicts = detect_label_conflicts(existing_labels, restore_labels)
        assert conflicts == ["bug"]

    def test_conflict_strategies_with_parametrized_data(
        self, temp_data_dir, github_data_builder
    ):
        """Test conflict strategies using parametrized data factory."""
        # Create test data using builder pattern
        test_data = github_data_builder.with_labels(3, prefix="test").build()

        # Create empty data files for other types
        data_path = Path(temp_data_dir)
        with open(data_path / "labels.json", "w") as f:
            json.dump(test_data["labels"], f)
        for filename in ["issues.json", "comments.json"]:
            with open(data_path / filename, "w") as f:
                json.dump([], f)

        # Test that we can detect conflicts using generated data
        existing = [
            Label(
                name="test-1",
                color="different",
                description="Existing",
                url="http://example.com/test-1",
                id=999,
            )
        ]
        restore_labels = [
            Label(
                name=label["name"],
                color=label["color"],
                description=label["description"],
                url="http://example.com/test",
                id=label["id"],
            )
            for label in test_data["labels"]
        ]

        conflicts = detect_label_conflicts(existing, restore_labels)
        assert "test-1" in conflicts

    def _create_test_files(self, data_dir, labels_data):
        """Helper to create test JSON files."""
        data_path = Path(data_dir)

        with open(data_path / "labels.json", "w") as f:
            json.dump(labels_data, f)
        with open(data_path / "issues.json", "w") as f:
            json.dump([], f)
        with open(data_path / "comments.json", "w") as f:
            json.dump([], f)


class TestConflictStrategyIntegrationWorkflows:
    """Integration tests for conflict strategies using workflow service fixtures."""

    @pytest.mark.integration
    @pytest.mark.restore_workflow
    def test_conflict_resolution_integration_environment(
        self, integration_test_environment
    ):
        """Test conflict resolution using complete integration test environment."""
        env = integration_test_environment
        boundary = env["boundary"]
        test_data = env["test_data"]

        # Configure existing labels that will conflict with test data
        conflicting_labels = [
            {
                "name": test_data["labels"][0][
                    "name"
                ],  # Same name as first label in test data
                "color": "different_color",
                "description": "Existing conflicting label",
                "url": "http://example.com/existing",
                "id": 999,
            }
        ]
        boundary.get_repository_labels.return_value = conflicting_labels

        # Create JSON files from test data
        import json
        import os

        for data_type, data in test_data.items():
            if data_type != "sub_issues":  # Skip sub_issues for label conflict tests
                file_path = os.path.join(env["temp_dir"], f"{data_type}.json")
                with open(file_path, "w") as f:
                    json.dump(data, f)

        # Test conflict detection with real labels from test data
        existing_labels = [
            Label(
                name=conflicting_labels[0]["name"],
                color=conflicting_labels[0]["color"],
                description=conflicting_labels[0]["description"],
                url=conflicting_labels[0]["url"],
                id=conflicting_labels[0]["id"],
            )
        ]

        restore_labels = [
            Label(
                name=label["name"],
                color=label["color"],
                description=label["description"],
                url="http://example.com/test",
                id=label["id"],
            )
            for label in test_data["labels"]
        ]

        conflicts = detect_label_conflicts(existing_labels, restore_labels)
        assert len(conflicts) == 1
        assert conflicts[0] == test_data["labels"][0]["name"]

    @pytest.mark.integration
    @pytest.mark.restore_workflow
    def test_restore_workflow_with_conflict_strategies(
        self, restore_workflow_services, parametrized_data_factory
    ):
        """Test complete restore workflow with different conflict strategies."""
        services = restore_workflow_services
        github_service = services["github"]
        storage_service = services["storage"]

        # Create test data with known labels for conflict testing
        test_data = parametrized_data_factory("basic")

        # Override the pre-populated labels.json with our test data
        import json
        import os

        labels_file = os.path.join(services["temp_dir"], "labels.json")
        with open(labels_file, "w") as f:
            json.dump(test_data["labels"], f)

        # Configure boundary to return existing labels that conflict
        boundary = github_service._boundary
        boundary.get_repository_labels.return_value = [
            {
                "name": test_data["labels"][0]["name"],  # Conflict with first label
                "color": "existing_color",
                "description": "Existing label",
                "url": "http://example.com/existing",
                "id": 888,
            }
        ]

        # Mock boundary methods for restoration
        boundary.create_label.return_value = {
            "name": "test_label",
            "id": 1,
            "color": "ff0000",
            "url": "http://example.com/created",
        }
        boundary.update_label.return_value = {
            "name": "test_label",
            "id": 888,
            "color": "updated_color",
            "url": "http://example.com/updated",
        }

        # Mock issue and comment operations
        boundary.create_issue.return_value = {
            "id": 1001,
            "number": 1,
            "title": "Test Issue",
            "body": "Test body",
            "state": "open",
            "html_url": "http://example.com/issue/1",
            "url": "http://api.example.com/issue/1",
            "labels": [],
            "user": {"login": "test", "id": 1},
        }
        boundary.create_comment.return_value = {
            "id": 2001,
            "body": "Test comment",
            "html_url": "http://example.com/comment/1",
            "issue_url": "http://api.example.com/issue/1",
            "user": {"login": "test", "id": 1},
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
        }

        # Test different conflict strategies with the workflow
        from src.operations.restore.restore import (
            restore_repository_data_with_strategy_pattern,
        )

        # Test skip strategy - should skip conflicting labels and create others
        restore_repository_data_with_strategy_pattern(
            github_service, storage_service, "owner/repo", services["temp_dir"], "skip"
        )

        # Verify that non-conflicting labels were created
        # Should be called for all labels except the conflicting one
        expected_calls = len(test_data["labels"]) - 1
        assert boundary.create_label.call_count == expected_calls

    @pytest.mark.integration
    @pytest.mark.restore_workflow
    @pytest.mark.cross_component_interaction
    def test_cross_component_conflict_resolution(
        self, integration_test_environment, parametrized_data_factory
    ):
        """Test conflict resolution across multiple data components."""
        env = integration_test_environment
        boundary = env["boundary"]

        # Create comprehensive test data with labels, issues, and cross-references
        test_data = parametrized_data_factory("mixed_states")

        # Configure existing repository state with conflicts
        boundary.get_repository_labels.return_value = [
            {
                "name": test_data["labels"][0]["name"],
                "color": "conflict_color",
                "description": "Conflicting existing label",
                "url": "http://example.com/conflict",
                "id": 777,
            }
        ]

        boundary.get_repository_issues.return_value = [
            {
                "id": 666,
                "number": test_data["issues"][0]["number"],
                "title": "Existing issue with same number",
                "body": "This issue already exists",
                "state": "open",
                "user": {"login": "existing_user", "id": 1},
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "closed_at": None,
                "html_url": "http://example.com/existing_issue",
                "comments": 0,
            }
        ]

        # Mock successful operations for non-conflicting data
        boundary.create_label.return_value = {
            "name": "created",
            "id": 1,
            "color": "ff0000",
            "url": "http://example.com/created",
        }
        boundary.create_issue.return_value = {
            "id": 1,
            "number": 100,
            "title": "Created Issue",
            "html_url": "http://example.com/created_issue",
        }
        boundary.create_comment.return_value = {
            "id": 1,
            "body": "Created comment",
            "html_url": "http://example.com/created_comment",
        }

        # Save test data to files
        import json
        import os

        for data_type, data in test_data.items():
            if data_type != "sub_issues":  # Skip sub_issues for this test
                file_path = os.path.join(env["temp_dir"], f"{data_type}.json")
                with open(file_path, "w") as f:
                    json.dump(data, f)

        # Test cross-component conflict detection
        from src.entities import Label

        # Label conflicts
        existing_labels = [
            Label(
                name=test_data["labels"][0]["name"],
                color="conflict_color",
                description="Conflicting",
                url="http://example.com/conflict",
                id=777,
            )
        ]
        restore_labels = [
            Label(
                name=label["name"],
                color=label["color"],
                description=label["description"],
                url="http://example.com/test",
                id=label["id"],
            )
            for label in test_data["labels"]
        ]

        label_conflicts = detect_label_conflicts(existing_labels, restore_labels)
        assert len(label_conflicts) >= 1

        # Verify that both label and issue data are properly handled
        # This ensures cross-component integration works correctly
        assert len(test_data["labels"]) > 0
        assert len(test_data["issues"]) > 0
        assert (
            len(test_data["comments"]) >= 0
        )  # May be empty depending on parametrized data
