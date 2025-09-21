"""
Test cases for dependency injection implementation.

Verifies that the new dependency injection architecture works correctly
with mock services.
"""

import pytest
from tests.mocks.mock_github_service import MockGitHubService
from tests.mocks.mock_storage_service import MockStorageService
from src.operations.save import save_repository_data_with_strategy_pattern
from src.entities import Label
from tests.shared import (
    backup_workflow_services,
    restore_workflow_services,
    MockBoundaryFactory,
    github_service_with_mock,
    storage_service_for_temp_dir
)

pytestmark = [pytest.mark.unit, pytest.mark.fast]


class TestDependencyInjection:
    """Test dependency injection implementation."""

    def test_save_operations_use_dependency_injection(
        self, backup_workflow_services
    ):
        """Test that save operations properly use injected services."""
        # Arrange
        services = backup_workflow_services
        github_service = services["github"]
        storage_service = services["storage"]
        temp_dir = services["temp_dir"]

        # Act
        save_repository_data_with_strategy_pattern(
            github_service, storage_service, "test/repo", temp_dir
        )

        # Assert - verify the services were called appropriately
        # The boundary will be called to get data
        github_service._boundary.get_repository_labels.assert_called_once_with("test/repo")
        github_service._boundary.get_repository_issues.assert_called_once_with("test/repo")
        github_service._boundary.get_all_issue_comments.assert_called_once_with("test/repo")
        github_service._boundary.get_repository_pull_requests.assert_called_once_with("test/repo")
        github_service._boundary.get_all_pull_request_comments.assert_called_once_with("test/repo")
        github_service._boundary.get_repository_sub_issues.assert_called_once_with("test/repo")
        
        # Verify files were created in the temp directory
        import os
        expected_files = [
            "labels.json",
            "issues.json", 
            "comments.json",
            "pull_requests.json",
            "pr_comments.json",
            "sub_issues.json",
        ]
        for filename in expected_files:
            assert os.path.exists(os.path.join(temp_dir, filename))

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

    def test_mock_storage_service_functionality(
        self, storage_service_for_temp_dir
    ):
        """Test storage service implements protocol correctly with real service."""
        # Arrange
        storage_service = storage_service_for_temp_dir
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
        import os
        from pathlib import Path
        labels_file = Path(storage_service._base_path) / "test_labels.json"
        storage_service.save_data(test_labels, labels_file)

        # Act - load data
        loaded_labels = storage_service.load_data(labels_file, Label)

        # Assert
        assert len(loaded_labels) == 2
        assert loaded_labels[0].name == "bug"
        assert loaded_labels[1].name == "feature"
        
        # Verify file exists
        assert os.path.exists(labels_file)

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

    def test_enhanced_boundary_mock_factory_integration(
        self, github_service_with_mock
    ):
        """Test integration with enhanced boundary mock patterns."""
        # Arrange - use pre-configured service with mock boundary
        github_service = github_service_with_mock
        
        # The mock boundary is already configured with empty responses
        # Test that we can override it for specific test scenarios
        github_service._boundary.get_repository_labels.return_value = [
            {"name": "test-label", "color": "ffffff", "id": 999}
        ]
        
        # Act
        labels = github_service.get_repository_labels("test/repo")
        
        # Assert
        assert len(labels) == 1
        assert labels[0]["name"] == "test-label"
        github_service._boundary.get_repository_labels.assert_called_once_with("test/repo")
    
    def test_workflow_services_integration(self, restore_workflow_services):
        """Test integration with workflow-specific service configurations."""
        # Arrange
        services = restore_workflow_services
        github_service = services["github"]
        storage_service = services["storage"]
        temp_dir = services["temp_dir"]
        
        # Act - test that restore workflow services are pre-configured
        # The restore services should have pre-populated data files
        import os
        from pathlib import Path
        assert "data_files" in services
        
        for filename in services["data_files"]:
            file_path = Path(temp_dir) / filename
            assert file_path.exists()
            
            # Verify we can load the pre-populated data
            if filename == "labels.json":
                from src.entities import Label
                labels = storage_service.load_data(file_path, Label)
                assert len(labels) > 0
