"""
Example modernized unit test demonstrating Phase 5 improvements.

This test file serves as a reference implementation showing:
- Standardized test markers and organization
- Shared test utilities usage
- Enhanced fixture integration
- Modern testing patterns and best practices

This file is for documentation purposes and demonstrates the
test infrastructure modernization implemented in Phase 5.
"""

import pytest

from tests.shared import (
    TestDataHelper,
    MockHelper,
    AssertionHelper,
    FixtureHelper,
)

# Other fixtures are auto-injected by pytest via conftest.py

# Standardized markers: base + infrastructure
pytestmark = [
    pytest.mark.unit,
    pytest.mark.fast,
    pytest.mark.save_workflow,  # Workflow type
]


class TestModernizedDataProcessing:
    """Example test class demonstrating modernized testing patterns."""

    def test_basic_entity_creation_with_helpers(self):
        """Test basic entity creation using TestDataHelper."""
        # Arrange - Use TestDataHelper for standardized entities
        user = TestDataHelper.create_test_user(login="alice", user_id=123)
        issue = TestDataHelper.create_test_issue(
            title="Modern Test Issue", state="open", user=user
        )
        comment = TestDataHelper.create_test_comment(
            body="Modern test comment", user=user, issue_number=issue.number
        )

        # Act - Process entities (example processing)
        processed_issue = self._process_issue(issue)
        processed_comment = self._process_comment(comment)

        # Assert - Use AssertionHelper for validation
        AssertionHelper.assert_valid_issue(processed_issue)
        AssertionHelper.assert_valid_comment(processed_comment)
        assert processed_issue.title == "Modern Test Issue"
        assert processed_comment.body == "Modern test comment"

    def test_mock_service_interaction_with_helpers(self):
        """Test service interaction using MockHelper."""
        # Arrange - Use MockHelper for standardized mocks
        mock_github = MockHelper.create_github_client_mock()
        mock_storage = MockHelper.create_storage_service_mock()

        # Configure mock responses
        mock_github.get_repository_issues.return_value = [
            FixtureHelper.create_sample_test_data()["issues"][0]
        ]

        # Act - Test service interaction
        result = self._backup_issues_service(mock_github, mock_storage, "owner/repo")

        # Assert - Use AssertionHelper for mock verification
        assert result is True
        AssertionHelper.assert_mock_called_with_repo(
            mock_github.get_repository_issues, "owner/repo"
        )
        mock_storage.save_issues.assert_called_once()

    @pytest.mark.enhanced_fixtures
    def test_with_github_data_builder(self, github_data_builder):
        """Test using enhanced github_data_builder fixture."""
        # Arrange - Use data builder for complex scenarios
        test_data = (
            github_data_builder.reset()
            .with_labels(3)
            .with_issues(5, state="mixed")
            .with_comments()
            .build()
        )

        # Act - Process built data
        issues_count = len(test_data["issues"])
        comments_count = len(test_data["comments"])
        labels_count = len(test_data["labels"])

        # Assert - Verify builder results
        assert issues_count == 5
        assert comments_count > 0  # Builder adds comments
        assert labels_count == 3

        # Validate data structure
        for issue_data in test_data["issues"]:
            assert "title" in issue_data
            assert "state" in issue_data
            assert issue_data["state"] in ["open", "closed"]

    @pytest.mark.enhanced_fixtures
    def test_with_parametrized_data_factory(self, parametrized_data_factory):
        """Test using parametrized_data_factory for scenarios."""
        # Test multiple scenarios
        scenarios = ["basic", "large", "mixed_states"]

        for scenario in scenarios:
            # Arrange - Get scenario data
            test_data = parametrized_data_factory(scenario)

            # Act - Process scenario
            result = self._process_repository_data(test_data)

            # Assert - Verify scenario handling
            assert result is not None
            assert "processed" in result
            assert result["processed"] is True

    @pytest.mark.integration
    @pytest.mark.medium
    def test_workflow_integration_with_services(self, save_workflow_services):
        """Test complete workflow using workflow services fixture."""
        # Arrange - Use pre-configured workflow services
        services = save_workflow_services
        github_service = services["github"]
        storage_service = services["storage"]
        temp_dir = services["temp_dir"]

        # Act - Execute workflow
        result = self._execute_save_workflow(
            github_service, storage_service, "test/repo", temp_dir
        )

        # Assert - Verify workflow execution
        assert result["success"] is True

        # Verify service interactions
        github_service._boundary.get_repository_labels.assert_called_once_with(
            "test/repo"
        )
        github_service._boundary.get_repository_issues.assert_called_once_with(
            "test/repo"
        )

        # Verify storage operations happened (files should exist)
        from pathlib import Path

        assert Path(temp_dir, "labels.json").exists()
        assert Path(temp_dir, "issues.json").exists()

    @pytest.mark.enhanced_fixtures
    def test_boundary_with_repository_data(self, boundary_with_repository_data):
        """Test using enhanced boundary with realistic data."""
        # Arrange - Use boundary with pre-configured data
        boundary = boundary_with_repository_data

        # Act - Interact with boundary
        labels = boundary.get_repository_labels("owner/repo")
        issues = boundary.get_repository_issues("owner/repo")

        # Assert - Verify realistic data
        assert len(labels) > 0
        assert len(issues) > 0

        # Validate data structure
        for label in labels:
            assert "name" in label
            assert "color" in label

        for issue in issues:
            assert "title" in issue
            assert "number" in issue
            assert "user" in issue

    @pytest.mark.error_simulation
    def test_error_handling_patterns(self):
        """Test error handling using standardized patterns."""
        # Arrange - Create mock that simulates errors
        mock_github = MockHelper.create_github_client_mock()
        mock_github.get_repository_issues.side_effect = Exception("API Error")

        # Act & Assert - Test error handling
        with pytest.raises(Exception) as exc_info:
            self._backup_issues_service(mock_github, None, "owner/repo")

        assert "API Error" in str(exc_info.value)

    def test_data_validation_with_assertion_helper(self):
        """Test data validation using AssertionHelper."""
        # Arrange - Create entities using helpers
        user = TestDataHelper.create_test_user()
        issue = TestDataHelper.create_test_issue(user=user)
        comment = TestDataHelper.create_test_comment(user=user)
        label = TestDataHelper.create_test_label()

        # Act - No processing needed for validation test

        # Assert - Use AssertionHelper for comprehensive validation
        AssertionHelper.assert_valid_github_user(user)
        AssertionHelper.assert_valid_issue(issue)
        AssertionHelper.assert_valid_comment(comment)
        AssertionHelper.assert_valid_label(label)

    # Helper methods for demonstration (normally would be actual implementation)

    def _process_issue(self, issue):
        """Example issue processing."""
        # Simulate processing
        return issue

    def _process_comment(self, comment):
        """Example comment processing."""
        # Simulate processing
        return comment

    def _backup_issues_service(self, github_client, storage_service, repo):
        """Example backup service."""
        try:
            issues = github_client.get_repository_issues(repo)
            if storage_service:
                storage_service.save_issues(issues)
            return True
        except Exception:
            raise

    def _process_repository_data(self, test_data):
        """Example repository data processing."""
        return {
            "processed": True,
            "scenario": "unknown",  # Simplified for example
            "issues_count": len(test_data.get("issues", [])),
            "labels_count": len(test_data.get("labels", [])),
        }

    def _execute_save_workflow(self, github_service, storage_service, repo, temp_dir):
        """Example workflow execution."""
        from pathlib import Path

        # Simulate workflow execution
        github_service._boundary.get_repository_labels(repo)
        github_service._boundary.get_repository_issues(repo)

        # Use correct storage interface
        storage_service.write([], Path(temp_dir) / "labels.json")
        storage_service.write([], Path(temp_dir) / "issues.json")

        return {"success": True, "repo": repo}


class TestMarkerDemonstration:
    """Demonstrate different marker usage patterns."""

    @pytest.mark.restore_workflow
    def test_label_restore_workflow(self):
        """Test specific to label restore workflow."""
        # This test would only run when testing label restore functionality
        label = TestDataHelper.create_test_label(name="feature", color="00ff00")

        # Simulate restore workflow
        restored_label = self._restore_label(label)

        AssertionHelper.assert_valid_label(restored_label)

    @pytest.mark.github_api
    @pytest.mark.rate_limiting
    def test_github_api_rate_limiting(self):
        """Test specific to GitHub API rate limiting."""
        # This test would only run when testing API rate limiting
        mock_client = MockHelper.create_github_client_mock()

        # Simulate rate limiting scenario
        result = self._handle_rate_limiting(mock_client)

        assert result["rate_limited"] is False

    @pytest.mark.storage
    @pytest.mark.performance
    def test_storage_performance(self):
        """Test specific to storage performance."""
        # This test would only run when testing storage performance
        storage_mock = MockHelper.create_storage_service_mock()
        test_data = FixtureHelper.create_sample_test_data()

        # Simulate performance test
        result = self._measure_storage_performance(storage_mock, test_data)

        assert result["duration"] < 1.0  # Should be fast

    def _restore_label(self, label):
        """Example label restoration."""
        return label

    def _handle_rate_limiting(self, client):
        """Example rate limiting handling."""
        return {"rate_limited": False}

    def _measure_storage_performance(self, storage, data):
        """Example performance measurement."""
        import time

        start = time.time()
        # Simulate storage operation
        storage.save_issues(data["issues"])
        end = time.time()
        return {"duration": end - start}


class TestFixtureIntegration:
    """Demonstrate integration with various fixture types."""

    def test_with_minimal_data(self):
        """Test using minimal test data."""
        # Arrange - Use FixtureHelper for minimal data
        test_data = FixtureHelper.create_minimal_test_data()

        # Act - Process empty data
        result = self._handle_empty_repository(test_data)

        # Assert - Verify empty data handling
        assert result["empty"] is True
        assert result["issues_count"] == 0
        assert result["labels_count"] == 0

    def test_with_sample_data(self):
        """Test using sample test data."""
        # Arrange - Use FixtureHelper for sample data
        test_data = FixtureHelper.create_sample_test_data()

        # Act - Process sample data
        result = self._handle_repository_data(test_data)

        # Assert - Verify sample data handling
        assert result["empty"] is False
        assert result["issues_count"] == 1
        assert result["labels_count"] == 2

    def _handle_empty_repository(self, data):
        """Example empty repository handling."""
        return {
            "empty": len(data["issues"]) == 0 and len(data["labels"]) == 0,
            "issues_count": len(data["issues"]),
            "labels_count": len(data["labels"]),
        }

    def _handle_repository_data(self, data):
        """Example repository data handling."""
        return {
            "empty": False,
            "issues_count": len(data["issues"]),
            "labels_count": len(data["labels"]),
        }
