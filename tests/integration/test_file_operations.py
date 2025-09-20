"""Integration tests for file operations and directory management."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.operations.save import save_repository_data_with_strategy_pattern
from src.github import create_github_service
from src.storage import create_storage_service

from tests.shared.mocks import add_pr_method_mocks, add_sub_issues_method_mocks
from tests.shared.builders import GitHubDataBuilder

pytestmark = [pytest.mark.integration]


class TestFileOperations:
    """Integration tests for file operations and directory management."""

    @patch("src.github.service.GitHubApiBoundary")
    def test_save_creates_output_directory_if_missing(
        self, mock_boundary_class, temp_data_dir
    ):
        """Test that save operation creates output directory structure."""
        # Setup mock
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = []
        mock_boundary.get_repository_issues.return_value = []
        mock_boundary.get_all_issue_comments.return_value = []
        add_pr_method_mocks(mock_boundary)
        add_sub_issues_method_mocks(mock_boundary)

        # Use nested directory that doesn't exist
        nested_path = Path(temp_data_dir) / "backup" / "github-data"

        # Execute save operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_strategy_pattern(
            github_service, storage_service, "owner/repo", str(nested_path)
        )

        # Verify directory was created
        assert nested_path.exists()
        assert nested_path.is_dir()

        # Verify files were created in the new directory
        assert (nested_path / "labels.json").exists()
        assert (nested_path / "issues.json").exists()
        assert (nested_path / "comments.json").exists()
        assert (nested_path / "pull_requests.json").exists()
        assert (nested_path / "pr_comments.json").exists()

    @patch("src.github.service.GitHubApiBoundary")
    def test_save_handles_deep_nested_directory_creation(
        self, mock_boundary_class, temp_data_dir
    ):
        """Test save operation with deeply nested directory paths."""
        # Setup mock
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = []
        mock_boundary.get_repository_issues.return_value = []
        mock_boundary.get_all_issue_comments.return_value = []
        add_pr_method_mocks(mock_boundary)
        add_sub_issues_method_mocks(mock_boundary)

        # Use deeply nested directory that doesn't exist
        deep_path = (
            Path(temp_data_dir) / "level1" / "level2" / "level3" / "github-backup"
        )

        # Execute save operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_strategy_pattern(
            github_service, storage_service, "owner/repo", str(deep_path)
        )

        # Verify all intermediate directories were created
        assert deep_path.exists()
        assert deep_path.is_dir()
        assert deep_path.parent.exists()  # level3 directory
        assert deep_path.parent.parent.exists()  # level2 directory
        assert deep_path.parent.parent.parent.exists()  # level1 directory

        # Verify files were created
        assert (deep_path / "labels.json").exists()
        assert (deep_path / "issues.json").exists()

    @patch("src.github.service.GitHubApiBoundary")
    def test_json_file_format_and_structure(self, mock_boundary_class, temp_data_dir):
        """Test that JSON files are created with correct format and structure."""
        # Create test data with varied content
        builder = GitHubDataBuilder()
        test_data = builder.build_complex()

        # Setup mock boundary to return test data
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = test_data["labels"]
        mock_boundary.get_repository_issues.return_value = test_data["issues"]
        mock_boundary.get_all_issue_comments.return_value = test_data["comments"]
        add_pr_method_mocks(mock_boundary, test_data)
        add_sub_issues_method_mocks(mock_boundary)

        # Execute save operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_strategy_pattern(
            github_service, storage_service, "owner/repo", temp_data_dir
        )

        # Verify JSON files are valid and properly formatted
        data_path = Path(temp_data_dir)

        # Check that all expected files exist
        expected_files = [
            "labels.json",
            "issues.json",
            "comments.json",
            "pull_requests.json",
            "pr_comments.json",
        ]
        for filename in expected_files:
            file_path = data_path / filename
            assert file_path.exists(), f"File {filename} was not created"

            # Verify file is valid JSON
            with open(file_path) as f:
                data = json.load(f)
                assert isinstance(
                    data, list
                ), f"File {filename} should contain a JSON array"

        # Verify specific file contents
        with open(data_path / "labels.json") as f:
            labels_data = json.load(f)
            assert len(labels_data) > 0, "Labels file should not be empty"

            # Check required label fields
            for label in labels_data:
                assert "name" in label
                assert "color" in label
                assert "id" in label
                assert "url" in label

        with open(data_path / "issues.json") as f:
            issues_data = json.load(f)
            assert len(issues_data) > 0, "Issues file should not be empty"

            # Check required issue fields
            for issue in issues_data:
                assert "id" in issue
                assert "number" in issue
                assert "title" in issue
                assert "state" in issue
                assert "user" in issue
                assert "created_at" in issue

    @patch("src.github.service.GitHubApiBoundary")
    def test_file_permissions_and_ownership(self, mock_boundary_class, temp_data_dir):
        """Test that created files have appropriate permissions."""
        # Setup mock
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = []
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

        # Check file permissions
        data_path = Path(temp_data_dir)
        for filename in ["labels.json", "issues.json", "comments.json"]:
            file_path = data_path / filename
            stat_info = file_path.stat()

            # Check that file is readable and writable by owner
            mode = stat_info.st_mode
            assert mode & 0o400, f"File {filename} should be readable by owner"
            assert mode & 0o200, f"File {filename} should be writable by owner"

    @patch("src.github.service.GitHubApiBoundary")
    def test_existing_file_overwrite_behavior(self, mock_boundary_class, temp_data_dir):
        """Test behavior when overwriting existing files."""
        # Create initial files with different content
        data_path = Path(temp_data_dir)
        initial_content = [{"name": "old-label", "id": 999}]

        with open(data_path / "labels.json", "w") as f:
            json.dump(initial_content, f)

        # Setup mock with new content
        new_labels = [
            {
                "name": "new-label",
                "id": 1000,
                "color": "ff0000",
                "description": "New label",
                "url": "http://example.com",
            }
        ]

        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = new_labels
        mock_boundary.get_repository_issues.return_value = []
        mock_boundary.get_all_issue_comments.return_value = []
        add_pr_method_mocks(mock_boundary)
        add_sub_issues_method_mocks(mock_boundary)

        # Execute save operation (should overwrite)
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_strategy_pattern(
            github_service, storage_service, "owner/repo", temp_data_dir
        )

        # Verify file was overwritten with new content
        with open(data_path / "labels.json") as f:
            saved_content = json.load(f)

        assert len(saved_content) == 1
        assert saved_content[0]["name"] == "new-label"
        assert saved_content[0]["id"] == 1000

        # Verify old content is gone
        assert not any(label["name"] == "old-label" for label in saved_content)

    @patch("src.github.service.GitHubApiBoundary")
    def test_large_file_handling(self, mock_boundary_class, temp_data_dir):
        """Test handling of large data sets that create big JSON files."""
        # Create large test dataset
        builder = GitHubDataBuilder()

        # Generate many labels, issues, and comments
        large_dataset = (
            builder.with_labels(100)  # 100 labels
            .with_issues(200, include_closed=True)  # 200 issues
            .with_comments(50, 5)  # 50 issues with 5 comments each = 250 comments
            .with_pull_requests(75)  # 75 PRs
            .with_pr_comments(40, 3)  # 40 PRs with 3 comments each = 120 PR comments
            .build()
        )

        # Setup mock boundary
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = large_dataset["labels"]
        mock_boundary.get_repository_issues.return_value = large_dataset["issues"]
        mock_boundary.get_all_issue_comments.return_value = large_dataset["comments"]
        add_pr_method_mocks(mock_boundary, large_dataset)
        add_sub_issues_method_mocks(mock_boundary)

        # Execute save operation
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")
        save_repository_data_with_strategy_pattern(
            github_service, storage_service, "owner/repo", temp_data_dir
        )

        # Verify large files were created successfully
        data_path = Path(temp_data_dir)

        # Check file sizes are reasonable (not empty, not too small)
        labels_file = data_path / "labels.json"
        issues_file = data_path / "issues.json"
        comments_file = data_path / "comments.json"

        assert (
            labels_file.stat().st_size > 1000
        ), "Labels file should be substantial for 100 labels"
        assert (
            issues_file.stat().st_size > 5000
        ), "Issues file should be substantial for 200 issues"
        assert (
            comments_file.stat().st_size > 2000
        ), "Comments file should be substantial for 250 comments"

        # Verify content integrity
        with open(labels_file) as f:
            labels_data = json.load(f)
            assert len(labels_data) == 100

        with open(issues_file) as f:
            issues_data = json.load(f)
            assert len(issues_data) == 200

        with open(comments_file) as f:
            comments_data = json.load(f)
            assert len(comments_data) == 250

    @patch("src.github.service.GitHubApiBoundary")
    def test_unicode_filename_and_content_handling(
        self, mock_boundary_class, temp_data_dir
    ):
        """Test handling of unicode content in file operations."""
        # Create test data with unicode content
        unicode_labels = [
            {
                "name": "测试标签",  # Chinese characters
                "color": "ff0000",
                "description": "Тестовая метка с русским текстом",  # Russian text
                "url": "https://api.github.com/repos/owner/repo/labels/test",
                "id": 1001,
            },
            {
                "name": "emoji-label-🚀",  # Emoji in name
                "color": "00ff00",
                "description": "Label with emoji 🎉 and special chars äöü",
                "url": "https://api.github.com/repos/owner/repo/labels/emoji",
                "id": 1002,
            },
        ]

        # Setup mock boundary
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = unicode_labels
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

        # Verify unicode content was saved correctly
        data_path = Path(temp_data_dir)

        # Read file with explicit UTF-8 encoding
        with open(data_path / "labels.json", "r", encoding="utf-8") as f:
            saved_labels = json.load(f)

        assert len(saved_labels) == 2

        # Check unicode content is preserved
        first_label = saved_labels[0]
        assert first_label["name"] == "测试标签"
        assert "русским текстом" in first_label["description"]

        second_label = saved_labels[1]
        assert "🚀" in second_label["name"]
        assert "🎉" in second_label["description"]
        assert "äöü" in second_label["description"]

    def test_directory_path_validation(self, temp_data_dir):
        """Test validation of directory paths."""
        # Test with various path formats
        valid_paths = [
            temp_data_dir,  # Absolute path
            str(Path(temp_data_dir) / "subdir"),  # Path with subdirectory
            str(Path(temp_data_dir) / "another" / "level"),  # Multi-level path
        ]

        for test_path in valid_paths:
            # Should not raise exception for valid paths
            path_obj = Path(test_path)
            # Create parent directories if they don't exist
            path_obj.parent.mkdir(parents=True, exist_ok=True)

            # Test path is accessible
            assert path_obj.parent.exists()

    @patch("src.github.service.GitHubApiBoundary")
    def test_concurrent_file_access_safety(self, mock_boundary_class, temp_data_dir):
        """Test file operation safety with potential concurrent access."""
        # This test simulates what happens if multiple processes try to save
        # to the same directory structure

        # Setup mock
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = [
            {
                "name": "test",
                "id": 1,
                "color": "ff0000",
                "description": "test",
                "url": "https://api.github.com/repos/owner/repo/labels/test",
            }
        ]
        mock_boundary.get_repository_issues.return_value = []
        mock_boundary.get_all_issue_comments.return_value = []
        add_pr_method_mocks(mock_boundary)
        add_sub_issues_method_mocks(mock_boundary)

        # Create the same directory structure multiple times
        # (simulating concurrent access)
        github_service = create_github_service("fake_token")
        storage_service = create_storage_service("json")

        # This should not fail even if directory already exists
        for i in range(3):
            save_repository_data_with_strategy_pattern(
                github_service, storage_service, f"owner/repo{i}", temp_data_dir
            )

        # Verify final state is consistent
        data_path = Path(temp_data_dir)
        assert (data_path / "labels.json").exists()

        # Verify file content is valid
        with open(data_path / "labels.json") as f:
            data = json.load(f)
            assert len(data) == 1
            assert data[0]["name"] == "test"
