"""
Test cases for dependency injection implementation.

Verifies that the new dependency injection architecture works correctly
with mock services.
"""

from tests.mocks.mock_github_service import MockGitHubService
from tests.mocks.mock_storage_service import MockStorageService
from src.operations.save import save_repository_data_with_services
from src.models import Label


class TestDependencyInjection:
    """Test dependency injection implementation."""

    def test_save_operations_use_dependency_injection(self, tmp_path):
        """Test that save operations properly use injected services."""
        # Arrange
        github_service = MockGitHubService()
        storage_service = MockStorageService()

        # Add some mock data that will actually be retrieved
        github_service.mock_data = {
            "labels": [],
            "issues": [],
            "comments": [],
            "pull_requests": [],
            "pr_comments": [],
            "sub_issues": [],
        }

        # Act
        save_repository_data_with_services(
            github_service, storage_service, "test/repo", str(tmp_path)
        )

        # Assert - verify save calls were made to storage service
        assert (
            len(storage_service.save_calls) == 7
        )  # labels, issues, comments, PRs, PR comments, sub-issues,
        # updated issues with associations

        # Verify all expected file types were saved
        expected_files = [
            "labels.json",
            "issues.json",
            "comments.json",
            "pull_requests.json",
            "pr_comments.json",
            "sub_issues.json",
        ]
        for filename in expected_files:
            assert storage_service.was_data_saved(tmp_path / filename)

        # Verify all data counts are 0 (empty mock data)
        for filename in expected_files:
            assert storage_service.get_saved_data_count(tmp_path / filename) == 0

    def test_mock_github_service_functionality(self):
        """Test mock GitHub service implements protocol correctly."""
        # Arrange
        mock_data = {
            "labels": [
                {
                    "name": "enhancement",
                    "color": "a2eeef",
                    "description": "New feature",
                    "url": "https://api.github.com/repos/test/repo/labels/enhancement",
                    "id": 1,
                }
            ],
            "issues": [
                {"number": 1, "title": "Issue 1"},
                {"number": 2, "title": "Issue 2"},
            ],
        }

        github_service = MockGitHubService(mock_data)

        # Act & Assert
        labels = github_service.get_repository_labels("test/repo")
        issues = github_service.get_repository_issues("test/repo")

        assert len(labels) == 1
        assert labels[0]["name"] == "enhancement"
        assert len(issues) == 2

        # Test creation tracking
        created_label = github_service.create_label(
            "test/repo", "test", "ffffff", "Test label"
        )
        assert len(github_service.created_labels) == 1
        assert created_label["name"] == "test"

    def test_mock_storage_service_functionality(self, tmp_path):
        """Test mock storage service implements protocol correctly."""
        # Arrange
        storage_service = MockStorageService()
        test_labels = [
            Label(
                name="bug",
                color="d73a4a",
                description="Bug report",
                url="https://api.github.com/test",
                id=1,
            ),
            Label(
                name="feature",
                color="a2eeef",
                description="New feature",
                url="https://api.github.com/test",
                id=2,
            ),
        ]

        # Act - save data
        labels_file = tmp_path / "test_labels.json"
        storage_service.save_data(test_labels, labels_file)

        # Add mock data for loading
        storage_service.add_mock_data(
            labels_file,
            [
                {
                    "name": "bug",
                    "color": "d73a4a",
                    "description": "Bug report",
                    "url": "https://api.github.com/test",
                    "id": 1,
                },
                {
                    "name": "feature",
                    "color": "a2eeef",
                    "description": "New feature",
                    "url": "https://api.github.com/test",
                    "id": 2,
                },
            ],
        )

        # Act - load data
        loaded_labels = storage_service.load_data(labels_file, Label)

        # Assert
        assert len(storage_service.save_calls) == 1
        assert len(storage_service.load_calls) == 1
        assert len(loaded_labels) == 2
        assert loaded_labels[0].name == "bug"
        assert loaded_labels[1].name == "feature"

        # Test tracking
        assert storage_service.was_data_saved(labels_file)
        assert storage_service.get_saved_data_count(labels_file) == 2

    def test_protocols_are_implemented(self):
        """Test that services properly implement their protocols."""
        from src.github.protocols import RepositoryService
        from src.storage.protocols import StorageService as StorageProtocol

        # Test GitHub service implements protocol
        github_service = MockGitHubService()
        assert isinstance(github_service, RepositoryService)

        # Test storage service implements protocol
        storage_service = MockStorageService()
        assert isinstance(storage_service, StorageProtocol)

        # Test all required methods exist
        assert hasattr(github_service, "get_repository_labels")
        assert hasattr(github_service, "create_label")
        assert hasattr(storage_service, "save_data")
        assert hasattr(storage_service, "load_data")
