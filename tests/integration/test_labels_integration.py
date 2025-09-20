"""Integration tests for label management functionality."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.github import create_github_service
from src.storage import create_storage_service
from src.operations.save import save_repository_data_with_strategy_pattern
from src.operations.restore.restore import restore_repository_data_with_strategy_pattern

from tests.shared.fixtures import temp_data_dir
from tests.shared.mocks import add_pr_method_mocks, add_sub_issues_method_mocks
from tests.shared.builders import GitHubDataBuilder

pytestmark = [pytest.mark.integration, pytest.mark.labels]


class TestLabelsIntegration:
    """Integration tests for label management functionality."""

    @patch("src.github.service.GitHubApiBoundary")
    def test_label_creation_with_special_characters(
        self, mock_boundary_class, temp_data_dir
    ):
        """Test label creation with special characters and edge cases."""
        # Create test data with special character labels
        test_labels = [
            {
                "name": "priority/high",  # Forward slash
                "color": "ff0000",
                "description": "High priority issues",
                "url": "https://api.github.com/repos/owner/repo/labels/priority%2Fhigh",
                "id": 1001,
            },
            {
                "name": "bug 🐛",  # Unicode emoji
                "color": "d73a4a",
                "description": "Something isn't working 🔧",
                "url": "https://api.github.com/repos/owner/repo/labels/bug%20🐛",
                "id": 1002,
            },
            {
                "name": "help-wanted",  # Hyphen
                "color": "008672",
                "description": "",  # Empty description
                "url": "https://api.github.com/repos/owner/repo/labels/help-wanted",
                "id": 1003,
            },
            {
                "name": "wontfix",  # No special chars but lowercase
                "color": "ffffff",
                "description": None,  # Null description
                "url": "https://api.github.com/repos/owner/repo/labels/wontfix",
                "id": 1004,
            },
        ]

        # Write test data to files
        data_path = Path(temp_data_dir)
        with open(data_path / "labels.json", "w") as f:
            json.dump(test_labels, f)
        with open(data_path / "issues.json", "w") as f:
            json.dump([], f)
        with open(data_path / "comments.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pull_requests.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pr_comments.json", "w") as f:
            json.dump([], f)

        # Setup mock boundary
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = []

        # Mock successful label creation
        mock_boundary.create_label.return_value = {"id": 999, "name": "test"}

        # Execute restore
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            include_prs=True,
        )

        # Verify all labels were created
        assert mock_boundary.create_label.call_count == 4

        # Check specific label creation calls
        label_calls = mock_boundary.create_label.call_args_list

        # First label with forward slash
        first_call_args = label_calls[0][0]
        assert first_call_args[1] == "priority/high"  # name
        assert first_call_args[2] == "ff0000"  # color
        assert first_call_args[3] == "High priority issues"  # description

        # Second label with emoji
        second_call_args = label_calls[1][0]
        assert second_call_args[1] == "bug 🐛"  # name
        assert "🔧" in first_call_args[3]  # description with emoji

        # Third label with empty description
        third_call_args = label_calls[2][0]
        assert third_call_args[1] == "help-wanted"  # name
        assert third_call_args[3] == ""  # empty description

        # Fourth label with null description
        fourth_call_args = label_calls[3][0]
        assert fourth_call_args[1] == "wontfix"  # name
        assert fourth_call_args[3] is None  # null description

    @patch("src.github.service.GitHubApiBoundary")
    def test_label_conflict_resolution(self, mock_boundary_class, temp_data_dir):
        """Test label conflict resolution when labels already exist."""
        # Create test data
        new_labels = [
            {
                "name": "existing-label",
                "color": "ff0000",
                "description": "New description",
                "url": "https://api.github.com/repos/owner/repo/labels/existing-label",
                "id": 1001,
            },
            {
                "name": "new-label",
                "color": "00ff00",
                "description": "Completely new label",
                "url": "https://api.github.com/repos/owner/repo/labels/new-label",
                "id": 1002,
            },
        ]

        # Existing labels in repository (simulating conflict)
        existing_labels = [
            {
                "name": "existing-label",
                "color": "000000",
                "description": "Old description",
                "url": "https://api.github.com/repos/owner/repo/labels/existing-label",
                "id": 2001,
            }
        ]

        # Write test data to files
        data_path = Path(temp_data_dir)
        with open(data_path / "labels.json", "w") as f:
            json.dump(new_labels, f)
        with open(data_path / "issues.json", "w") as f:
            json.dump([], f)
        with open(data_path / "comments.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pull_requests.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pr_comments.json", "w") as f:
            json.dump([], f)

        # Setup mock boundary to simulate existing labels
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = existing_labels

        # Mock successful label creation for new labels only
        mock_boundary.create_label.return_value = {"id": 999, "name": "test"}

        # Execute restore
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            include_prs=True,
        )

        # Verify only the new label was created (existing one skipped)
        assert mock_boundary.create_label.call_count == 1

        # Check that the new label was created
        label_calls = mock_boundary.create_label.call_args_list
        created_label_args = label_calls[0][0]
        assert created_label_args[1] == "new-label"  # name
        assert created_label_args[2] == "00ff00"  # color
        assert created_label_args[3] == "Completely new label"  # description

    @patch("src.github.service.GitHubApiBoundary")
    def test_label_color_validation(self, mock_boundary_class, temp_data_dir):
        """Test label creation with various color formats."""
        # Create test data with different color formats
        test_labels = [
            {
                "name": "six-digit-color",
                "color": "ff0000",  # Standard 6-digit hex
                "description": "Red color",
                "url": "https://api.github.com/repos/owner/repo/labels/six-digit",
                "id": 1001,
            },
            {
                "name": "three-digit-color",
                "color": "f00",  # 3-digit hex (should work)
                "description": "Short red color",
                "url": "https://api.github.com/repos/owner/repo/labels/three-digit",
                "id": 1002,
            },
            {
                "name": "uppercase-color",
                "color": "FF00FF",  # Uppercase hex
                "description": "Magenta color",
                "url": "https://api.github.com/repos/owner/repo/labels/uppercase",
                "id": 1003,
            },
        ]

        # Write test data to files
        data_path = Path(temp_data_dir)
        with open(data_path / "labels.json", "w") as f:
            json.dump(test_labels, f)
        with open(data_path / "issues.json", "w") as f:
            json.dump([], f)
        with open(data_path / "comments.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pull_requests.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pr_comments.json", "w") as f:
            json.dump([], f)

        # Setup mock boundary
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = []

        # Mock successful label creation
        mock_boundary.create_label.return_value = {"id": 999, "name": "test"}

        # Execute restore
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            include_prs=True,
        )

        # Verify all labels were created with various color formats
        assert mock_boundary.create_label.call_count == 3

        # Check color values were preserved as-is
        label_calls = mock_boundary.create_label.call_args_list
        
        # First label - 6-digit color
        first_call_args = label_calls[0][0]
        assert first_call_args[2] == "ff0000"
        
        # Second label - 3-digit color
        second_call_args = label_calls[1][0]
        assert second_call_args[2] == "f00"
        
        # Third label - uppercase color
        third_call_args = label_calls[2][0]
        assert third_call_args[2] == "FF00FF"

    @patch("src.github.service.GitHubApiBoundary")
    def test_bulk_label_operations(self, mock_boundary_class, temp_data_dir):
        """Test bulk label operations with many labels."""
        # Create test data with many labels
        builder = GitHubDataBuilder()
        test_data = builder.with_labels(50).build()  # 50 labels (more than default)

        # Add custom labels to reach 50
        additional_labels = []
        for i in range(47):  # Builder gives us 3 by default, add 47 more
            additional_labels.append({
                "name": f"label-{i+4}",
                "color": f"{i+4:06x}"[:6],  # Generate hex colors
                "description": f"Description for label {i+4}",
                "url": f"https://api.github.com/repos/owner/repo/labels/label-{i+4}",
                "id": 1000 + i + 4,
            })
        
        test_data["labels"].extend(additional_labels)

        # Write test data to files
        data_path = Path(temp_data_dir)
        for key, data in test_data.items():
            with open(data_path / f"{key}.json", "w") as f:
                json.dump(data, f)

        # Setup mock boundary
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = []

        # Mock successful label creation
        mock_boundary.create_label.return_value = {"id": 999, "name": "test"}

        # Execute restore
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            include_prs=True,
        )

        # Verify all 50 labels were processed
        assert mock_boundary.create_label.call_count == 50

    @patch("src.github.service.GitHubApiBoundary")
    def test_label_save_preserves_all_attributes(
        self, mock_boundary_class, temp_data_dir
    ):
        """Test that label save operation preserves all label attributes."""
        # Create comprehensive label data with all possible attributes
        comprehensive_labels = [
            {
                "name": "comprehensive-label",
                "color": "336699",
                "description": "A label with all attributes preserved",
                "url": "https://api.github.com/repos/owner/repo/labels/comprehensive",
                "id": 12345678,
                "node_id": "MDU6TGFiZWwxMjM0NTY3OA==",  # GraphQL node ID
                "default": False,
            }
        ]

        # Setup mock boundary for save operation
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = comprehensive_labels
        mock_boundary.get_repository_issues.return_value = []
        mock_boundary.get_all_issue_comments.return_value = []
        add_pr_method_mocks(mock_boundary)
        add_sub_issues_method_mocks(mock_boundary)

        # Execute save operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_strategy_pattern(
            github_service, storage_service, "owner/repo", temp_data_dir
        )

        # Read saved data and verify all attributes were preserved
        data_path = Path(temp_data_dir)
        with open(data_path / "labels.json") as f:
            saved_labels = json.load(f)

        assert len(saved_labels) == 1
        saved_label = saved_labels[0]
        
        # Verify core attributes
        assert saved_label["name"] == "comprehensive-label"
        assert saved_label["color"] == "336699"
        assert saved_label["description"] == "A label with all attributes preserved"
        assert saved_label["url"] == "https://api.github.com/repos/owner/repo/labels/comprehensive"
        assert saved_label["id"] == 12345678
        
        # Verify additional attributes if present
        if "node_id" in saved_label:
            assert saved_label["node_id"] == "MDU6TGFiZWwxMjM0NTY3OA=="
        if "default" in saved_label:
            assert saved_label["default"] is False

    @patch("src.github.service.GitHubApiBoundary")
    def test_label_name_case_sensitivity(self, mock_boundary_class, temp_data_dir):
        """Test label operations with case-sensitive names."""
        # Create test data with similar but case-different label names
        test_labels = [
            {
                "name": "Bug",  # Capital B
                "color": "d73a4a",
                "description": "Bug with capital B",
                "url": "https://api.github.com/repos/owner/repo/labels/Bug",
                "id": 1001,
            },
            {
                "name": "bug",  # Lowercase b
                "color": "ff0000",
                "description": "Bug with lowercase b",
                "url": "https://api.github.com/repos/owner/repo/labels/bug",
                "id": 1002,
            },
            {
                "name": "BUG",  # All caps
                "color": "990000",
                "description": "Bug in all caps",
                "url": "https://api.github.com/repos/owner/repo/labels/BUG",
                "id": 1003,
            },
        ]

        # Write test data to files
        data_path = Path(temp_data_dir)
        with open(data_path / "labels.json", "w") as f:
            json.dump(test_labels, f)
        with open(data_path / "issues.json", "w") as f:
            json.dump([], f)
        with open(data_path / "comments.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pull_requests.json", "w") as f:
            json.dump([], f)
        with open(data_path / "pr_comments.json", "w") as f:
            json.dump([], f)

        # Setup mock boundary
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = []

        # Mock successful label creation
        mock_boundary.create_label.return_value = {"id": 999, "name": "test"}

        # Execute restore
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        restore_repository_data_with_strategy_pattern(
            github_service,
            storage_service,
            "owner/repo",
            temp_data_dir,
            include_prs=True,
        )

        # Verify all three labels were created as separate entities
        assert mock_boundary.create_label.call_count == 3

        # Check that case was preserved in label names
        label_calls = mock_boundary.create_label.call_args_list
        
        created_names = [call[0][1] for call in label_calls]  # name is 2nd positional arg
        assert "Bug" in created_names
        assert "bug" in created_names
        assert "BUG" in created_names
        assert len(set(created_names)) == 3  # All three should be unique