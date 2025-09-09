"""Integration tests for GitHub Data save/restore workflows."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.actions.save import save_repository_data
from src.actions.restore import restore_repository_data

pytestmark = [pytest.mark.integration]


class TestSaveRestoreIntegration:
    """Integration tests for complete save/restore workflows."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary directory for test data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def sample_github_data(self):
        """Sample GitHub API JSON data that boundary would return."""
        return {
            "labels": [
                {
                    "name": "bug",
                    "color": "d73a4a",
                    "description": "Something isn't working",
                    "url": "https://api.github.com/repos/owner/repo/labels/bug",
                    "id": 1001,
                },
                {
                    "name": "enhancement",
                    "color": "a2eeef",
                    "description": "New feature or request",
                    "url": "https://api.github.com/repos/owner/repo/labels/enhancement",
                    "id": 1002,
                },
            ],
            "issues": [
                {
                    "id": 2001,
                    "number": 1,
                    "title": "Fix authentication bug",
                    "body": "Users cannot login with valid credentials",
                    "state": "open",
                    "user": {
                        "login": "alice",
                        "id": 3001,
                        "avatar_url": "https://github.com/alice.png",
                        "html_url": "https://github.com/alice",
                    },
                    "assignees": [],
                    "labels": [
                        {
                            "name": "bug",
                            "color": "d73a4a",
                            "description": "Something isn't working",
                            "url": "https://api.github.com/repos/owner/repo/labels/bug",
                            "id": 1001,
                        }
                    ],
                    "created_at": "2023-01-15T10:30:00Z",
                    "updated_at": "2023-01-15T14:20:00Z",
                    "closed_at": None,
                    "html_url": "https://github.com/owner/repo/issues/1",
                    "comments": 2,
                },
                {
                    "id": 2002,
                    "number": 2,
                    "title": "Add user dashboard",
                    "body": None,
                    "state": "closed",
                    "user": {
                        "login": "bob",
                        "id": 3002,
                        "avatar_url": "https://github.com/bob.png",
                        "html_url": "https://github.com/bob",
                    },
                    "assignees": [
                        {
                            "login": "alice",
                            "id": 3001,
                            "avatar_url": "https://github.com/alice.png",
                            "html_url": "https://github.com/alice",
                        }
                    ],
                    "labels": [
                        {
                            "name": "enhancement",
                            "color": "a2eeef",
                            "description": "New feature or request",
                            "url": (
                                "https://api.github.com/repos/owner/repo/"
                                "labels/enhancement"
                            ),
                            "id": 1002,
                        }
                    ],
                    "created_at": "2023-01-10T09:00:00Z",
                    "updated_at": "2023-01-12T16:45:00Z",
                    "closed_at": "2023-01-12T16:45:00Z",
                    "html_url": "https://github.com/owner/repo/issues/2",
                    "comments": 0,
                },
            ],
            "comments": [
                {
                    "id": 4001,
                    "body": "I can reproduce this issue",
                    "user": {
                        "login": "charlie",
                        "id": 3003,
                        "avatar_url": "https://github.com/charlie.png",
                        "html_url": "https://github.com/charlie",
                    },
                    "created_at": "2023-01-15T12:00:00Z",
                    "updated_at": "2023-01-15T12:00:00Z",
                    "html_url": (
                        "https://github.com/owner/repo/issues/1#issuecomment-4001"
                    ),
                    "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
                },
                {
                    "id": 4002,
                    "body": "Fixed in PR #3",
                    "user": {
                        "login": "alice",
                        "id": 3001,
                        "avatar_url": "https://github.com/alice.png",
                        "html_url": "https://github.com/alice",
                    },
                    "created_at": "2023-01-15T14:00:00Z",
                    "updated_at": "2023-01-15T14:00:00Z",
                    "html_url": (
                        "https://github.com/owner/repo/issues/1#issuecomment-4002"
                    ),
                    "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
                },
            ],
        }

    @patch("src.github.service.GitHubApiBoundary")
    def test_save_creates_json_files_with_correct_structure(
        self, mock_boundary_class, temp_data_dir, sample_github_data
    ):
        """Test that save operation creates properly structured JSON files."""
        # Setup mock boundary to return our sample data
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = sample_github_data["labels"]
        mock_boundary.get_repository_issues.return_value = sample_github_data["issues"]
        mock_boundary.get_all_issue_comments.return_value = sample_github_data[
            "comments"
        ]

        # Execute save operation
        save_repository_data("fake_token", "owner/repo", temp_data_dir)

        # Verify JSON files were created
        data_path = Path(temp_data_dir)
        assert (data_path / "labels.json").exists()
        assert (data_path / "issues.json").exists()
        assert (data_path / "comments.json").exists()

        # Verify labels.json content and structure
        with open(data_path / "labels.json") as f:
            labels_data = json.load(f)
        assert len(labels_data) == 2
        assert labels_data[0]["name"] == "bug"
        assert labels_data[0]["color"] == "d73a4a"
        assert labels_data[1]["name"] == "enhancement"
        assert labels_data[1]["description"] == "New feature or request"

        # Verify issues.json content and structure
        with open(data_path / "issues.json") as f:
            issues_data = json.load(f)
        assert len(issues_data) == 2

        # Check first issue (open with body)
        issue1 = issues_data[0]
        assert issue1["title"] == "Fix authentication bug"
        assert issue1["state"] == "open"
        assert issue1["body"] == "Users cannot login with valid credentials"
        assert issue1["user"]["login"] == "alice"
        assert len(issue1["labels"]) == 1
        assert issue1["labels"][0]["name"] == "bug"
        assert issue1["closed_at"] is None

        # Check second issue (closed with assignee, no body)
        issue2 = issues_data[1]
        assert issue2["title"] == "Add user dashboard"
        assert issue2["state"] == "closed"
        assert issue2["body"] is None
        assert issue2["user"]["login"] == "bob"
        assert len(issue2["assignees"]) == 1
        assert issue2["assignees"][0]["login"] == "alice"
        assert issue2["closed_at"] is not None

        # Verify comments.json content and structure
        with open(data_path / "comments.json") as f:
            comments_data = json.load(f)
        assert len(comments_data) == 2
        assert comments_data[0]["body"] == "I can reproduce this issue"
        assert comments_data[0]["user"]["login"] == "charlie"
        assert comments_data[1]["body"] == "Fixed in PR #3"
        assert comments_data[1]["user"]["login"] == "alice"

    @patch("src.github.service.GitHubApiBoundary")
    def test_restore_recreates_data_from_json_files(
        self, mock_boundary_class, temp_data_dir, sample_github_data
    ):
        """Test that restore operation correctly recreates repository data."""
        # Create JSON files (simulating previous save operation)
        data_path = Path(temp_data_dir)

        with open(data_path / "labels.json", "w") as f:
            json.dump(sample_github_data["labels"], f)
        with open(data_path / "issues.json", "w") as f:
            json.dump(sample_github_data["issues"], f)
        with open(data_path / "comments.json", "w") as f:
            json.dump(sample_github_data["comments"], f)

        # Setup mock boundary for creation operations
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # Mock return values for create operations
        mock_boundary.create_label.side_effect = [
            {
                "name": "bug",
                "id": 5001,
                "color": "d73a4a",
                "description": "Something isn't working",
                "url": "https://api.github.com/repos/owner/target_repo/labels/bug",
            },
            {
                "name": "enhancement",
                "id": 5002,
                "color": "a2eeef",
                "description": "New feature or request",
                "url": "https://api.github.com/repos/owner/target_repo/labels/enhancement",  # noqa: E501
            },
        ]
        mock_boundary.create_issue.side_effect = [
            {
                "number": 10,
                "title": "Fix authentication bug",
                "id": 6001,
                "body": "Test issue body",
                "state": "open",
                "user": {
                    "login": "testuser",
                    "id": 1,
                    "avatar_url": "https://github.com/images/error/testuser_happy.gif",
                    "url": "https://api.github.com/users/testuser",
                    "html_url": "https://github.com/testuser",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-12T16:45:00Z",
                "updated_at": "2023-01-12T16:45:00Z",
                "closed_at": None,
                "html_url": "https://github.com/owner/target_repo/issues/10",
                "comments": 0,
            },
            {
                "number": 11,
                "title": "Add user dashboard",
                "id": 6002,
                "body": "Test issue body",
                "state": "open",
                "user": {
                    "login": "testuser",
                    "id": 1,
                    "avatar_url": "https://github.com/images/error/testuser_happy.gif",
                    "url": "https://api.github.com/users/testuser",
                    "html_url": "https://github.com/testuser",
                },
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-15T09:30:00Z",
                "updated_at": "2023-01-15T09:30:00Z",
                "closed_at": None,
                "html_url": "https://github.com/owner/target_repo/issues/11",
                "comments": 0,
            },
        ]

        # Execute restore operation
        restore_repository_data("fake_token", "owner/target_repo", temp_data_dir)

        # Verify boundary methods were called correctly
        assert mock_boundary.create_label.call_count == 2
        assert mock_boundary.create_issue.call_count == 2

        # Verify label creation calls
        label_calls = mock_boundary.create_label.call_args_list

        # First label call
        first_label_call = label_calls[0][1]  # keyword arguments
        assert first_label_call["name"] == "bug"
        assert first_label_call["color"] == "d73a4a"
        assert first_label_call["description"] == "Something isn't working"

        # Second label call
        second_label_call = label_calls[1][1]
        assert second_label_call["name"] == "enhancement"
        assert second_label_call["color"] == "a2eeef"
        assert second_label_call["description"] == "New feature or request"

        # Verify issue creation calls
        issue_calls = mock_boundary.create_issue.call_args_list

        # First issue call
        first_issue_call = issue_calls[0][1]
        assert first_issue_call["title"] == "Fix authentication bug"
        assert first_issue_call["body"] == "Users cannot login with valid credentials"
        assert first_issue_call["labels"] == ["bug"]

        # Second issue call (with None body converted to empty string)
        second_issue_call = issue_calls[1][1]
        assert second_issue_call["title"] == "Add user dashboard"
        assert second_issue_call["body"] == ""  # None converted to empty string
        assert second_issue_call["labels"] == ["enhancement"]

    @patch("src.github.service.GitHubApiBoundary")
    def test_complete_save_restore_cycle_preserves_data_integrity(
        self, mock_boundary_class, temp_data_dir, sample_github_data
    ):
        """Test that complete save → restore cycle preserves all data correctly."""

        # Phase 1: Save operation
        save_boundary = Mock()
        mock_boundary_class.return_value = save_boundary
        save_boundary.get_repository_labels.return_value = sample_github_data["labels"]
        save_boundary.get_repository_issues.return_value = sample_github_data["issues"]
        save_boundary.get_all_issue_comments.return_value = sample_github_data[
            "comments"
        ]

        save_repository_data("fake_token", "owner/source_repo", temp_data_dir)

        # Phase 2: Restore operation with fresh mock
        restore_boundary = Mock()
        mock_boundary_class.return_value = restore_boundary
        restore_boundary.create_label.return_value = {
            "id": 999,
            "name": "test",
            "color": "ffffff",
            "description": "test",
            "url": "https://api.github.com/repos/owner/target_repo/labels/test",
        }
        restore_boundary.create_issue.return_value = {
            "number": 999,
            "title": "test",
            "id": 999,
            "body": "test",
            "state": "open",
            "user": {
                "login": "testuser",
                "id": 1,
                "avatar_url": "https://github.com/images/error/testuser_happy.gif",
                "url": "https://api.github.com/users/testuser",
                "html_url": "https://github.com/testuser",
            },
            "assignees": [],
            "labels": [],
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "closed_at": None,
            "html_url": "https://github.com/owner/target_repo/issues/999",
            "comments": 0,
        }

        restore_repository_data("fake_token", "owner/target_repo", temp_data_dir)

        # Verify data integrity by checking that saved data matches restored data

        # Check that same number of items were saved and restored
        assert save_boundary.get_repository_labels.call_count == 1
        assert restore_boundary.create_label.call_count == 2

        assert save_boundary.get_repository_issues.call_count == 1
        assert restore_boundary.create_issue.call_count == 2

        # Verify that all original label data was preserved in restore calls
        restore_label_calls = restore_boundary.create_label.call_args_list
        original_labels = sample_github_data["labels"]

        for i, (original, call) in enumerate(zip(original_labels, restore_label_calls)):
            restored_args = call[1]  # keyword arguments
            assert restored_args["name"] == original["name"]
            assert restored_args["color"] == original["color"]
            assert restored_args["description"] == original["description"]

        # Verify that all original issue data was preserved
        restore_issue_calls = restore_boundary.create_issue.call_args_list
        original_issues = sample_github_data["issues"]

        for i, (original, call) in enumerate(zip(original_issues, restore_issue_calls)):
            restored_args = call[1]
            assert restored_args["title"] == original["title"]
            # Handle None body conversion
            expected_body = original["body"] or ""
            assert restored_args["body"] == expected_body
            # Check that labels were extracted correctly
            expected_labels = [label["name"] for label in original["labels"]]
            assert restored_args["labels"] == expected_labels

    @patch("src.github.service.GitHubApiBoundary")
    def test_save_handles_empty_repository(self, mock_boundary_class, temp_data_dir):
        """Test save operation with repository that has no data."""
        # Setup mock for empty repository
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = []
        mock_boundary.get_repository_issues.return_value = []
        mock_boundary.get_all_issue_comments.return_value = []

        # Execute save operation
        save_repository_data("fake_token", "owner/empty_repo", temp_data_dir)

        # Verify JSON files are created even with empty data
        data_path = Path(temp_data_dir)
        assert (data_path / "labels.json").exists()
        assert (data_path / "issues.json").exists()
        assert (data_path / "comments.json").exists()

        # Verify files contain empty arrays
        with open(data_path / "labels.json") as f:
            assert json.load(f) == []
        with open(data_path / "issues.json") as f:
            assert json.load(f) == []
        with open(data_path / "comments.json") as f:
            assert json.load(f) == []

    @patch("src.github.service.GitHubApiBoundary")
    def test_restore_handles_empty_json_files(self, mock_boundary_class, temp_data_dir):
        """Test restore operation with empty JSON files."""
        # Create empty JSON files
        data_path = Path(temp_data_dir)
        for filename in ["labels.json", "issues.json", "comments.json"]:
            with open(data_path / filename, "w") as f:
                json.dump([], f)

        # Setup mock boundary
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # Execute restore operation
        restore_repository_data("fake_token", "owner/repo", temp_data_dir)

        # Verify no creation methods were called for empty data
        assert mock_boundary.create_label.call_count == 0
        assert mock_boundary.create_issue.call_count == 0

    def test_restore_fails_when_json_files_missing(self, temp_data_dir):
        """Test restore fails gracefully when required files are missing."""
        with pytest.raises(FileNotFoundError) as exc_info:
            restore_repository_data("fake_token", "owner/repo", temp_data_dir)

        assert "labels.json" in str(exc_info.value)

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

        # Use nested directory that doesn't exist
        nested_path = Path(temp_data_dir) / "backup" / "github-data"

        # Execute save operation
        save_repository_data("fake_token", "owner/repo", str(nested_path))

        # Verify directory was created
        assert nested_path.exists()
        assert nested_path.is_dir()

        # Verify files were created in the new directory
        assert (nested_path / "labels.json").exists()
        assert (nested_path / "issues.json").exists()
        assert (nested_path / "comments.json").exists()


class TestErrorHandlingIntegration:
    """Integration tests for error scenarios and edge cases."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary directory for test data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @patch("src.github.service.GitHubApiBoundary")
    def test_restore_handles_github_api_failures_gracefully(
        self, mock_boundary_class, temp_data_dir
    ):
        """Test that restore continues despite GitHub API failures."""
        # Create test data files
        data_path = Path(temp_data_dir)

        test_labels = [
            {
                "name": "bug",
                "color": "ff0000",
                "description": "Bug label",
                "url": "http://example.com",
                "id": 1,
            },
            {
                "name": "feature",
                "color": "00ff00",
                "description": "Feature label",
                "url": "http://example.com",
                "id": 2,
            },
        ]

        with open(data_path / "labels.json", "w") as f:
            json.dump(test_labels, f)
        with open(data_path / "issues.json", "w") as f:
            json.dump([], f)
        with open(data_path / "comments.json", "w") as f:
            json.dump([], f)

        # Setup mock to simulate GitHub API failures
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary

        # First label succeeds, second fails
        mock_boundary.create_label.side_effect = [
            {
                "id": 100,
                "name": "bug",
                "color": "ff0000",
                "description": "Bug label",
                "url": "http://example.com",
            },  # Success
            Exception("API rate limit exceeded"),  # Failure
        ]

        # Execute restore operation - should fail fast on second error
        with pytest.raises(RuntimeError, match="Failed to create label 'feature'"):
            restore_repository_data("fake_token", "owner/repo", temp_data_dir)

        # Verify first label succeeded, second failed and stopped execution
        assert mock_boundary.create_label.call_count == 2

    def test_restore_handles_malformed_json_files(self, temp_data_dir):
        """Test restore operation with malformed JSON files."""
        # Create malformed JSON file
        data_path = Path(temp_data_dir)
        with open(data_path / "labels.json", "w") as f:
            f.write("{ invalid json syntax }")
        with open(data_path / "issues.json", "w") as f:
            json.dump([], f)
        with open(data_path / "comments.json", "w") as f:
            json.dump([], f)

        # Restore should fail with JSON decode error
        with pytest.raises(json.JSONDecodeError):
            restore_repository_data("fake_token", "owner/repo", temp_data_dir)

    @patch("src.github.service.GitHubApiBoundary")
    def test_data_type_conversion_and_validation(
        self, mock_boundary_class, temp_data_dir
    ):
        """Test that data types are properly converted and validated."""
        # Test data with various data type scenarios
        complex_github_data = {
            "labels": [
                {
                    "name": "priority/high",
                    "color": "ff0000",
                    "description": None,  # Test None handling
                    "url": (
                        "https://api.github.com/repos/owner/repo/labels/priority%2Fhigh"
                    ),
                    "id": 1234567890,  # Large integer
                }
            ],
            "issues": [
                {
                    "id": 9876543210,  # Large integer
                    "number": 42,
                    "title": "Issue with unicode: 测试 🚀",  # Unicode handling
                    "body": "",  # Empty string
                    "state": "closed",
                    "user": {
                        "login": "test.user-123",  # Special characters in username
                        "id": 111,
                        "avatar_url": "https://github.com/avatar.png",
                        "html_url": "https://github.com/test.user-123",
                    },
                    "assignees": [],
                    "labels": [],
                    "created_at": "2023-12-25T09:30:45Z",  # ISO datetime
                    "updated_at": "2023-12-25T09:30:45Z",
                    "closed_at": "2023-12-25T10:15:30Z",
                    "html_url": "https://github.com/owner/repo/issues/42",
                    "comments": 0,
                }
            ],
            "comments": [],
        }

        # Setup mock boundary
        mock_boundary = Mock()
        mock_boundary_class.return_value = mock_boundary
        mock_boundary.get_repository_labels.return_value = complex_github_data["labels"]
        mock_boundary.get_repository_issues.return_value = complex_github_data["issues"]
        mock_boundary.get_all_issue_comments.return_value = complex_github_data[
            "comments"
        ]

        # Execute save operation
        save_repository_data("fake_token", "owner/repo", temp_data_dir)

        # Verify data was saved correctly
        data_path = Path(temp_data_dir)

        # Check labels with None description
        with open(data_path / "labels.json") as f:
            labels_data = json.load(f)
        assert labels_data[0]["description"] is None
        assert labels_data[0]["name"] == "priority/high"
        assert isinstance(labels_data[0]["id"], int)

        # Check issues with unicode and datetime
        with open(data_path / "issues.json") as f:
            issues_data = json.load(f)
        assert "测试 🚀" in issues_data[0]["title"]
        assert issues_data[0]["body"] == ""
        assert isinstance(issues_data[0]["id"], int)
        assert isinstance(
            issues_data[0]["created_at"], str
        )  # Datetime serialized as string
