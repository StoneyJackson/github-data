"""Tests for enhanced boundary factory with protocol completeness."""

from unittest.mock import Mock

from tests.shared.mocks.boundary_factory import MockBoundaryFactory


class TestEnhancedBoundaryFactory:
    """Test the enhanced boundary factory functionality."""

    def test_protocol_completeness_validation(self):
        """Test that protocol completeness validation works."""

        # Create a truly incomplete mock by using a plain dict instead of Mock
        class IncompleteMock:
            def __init__(self):
                self.get_repository_labels = Mock(return_value=[])

        incomplete_mock = IncompleteMock()

        is_complete, missing = MockBoundaryFactory.validate_protocol_completeness(
            incomplete_mock
        )
        assert not is_complete
        assert len(missing) > 0
        assert "create_issue" in missing  # Should be missing create methods

    def test_create_protocol_complete(self, sample_github_data):
        """Test creating a protocol-complete boundary mock."""
        mock_boundary = MockBoundaryFactory.create_protocol_complete(sample_github_data)

        # Validate completeness
        is_complete, missing = MockBoundaryFactory.validate_protocol_completeness(
            mock_boundary
        )
        assert is_complete, f"Missing methods: {missing}"

        # Test some key methods are configured
        assert mock_boundary.get_repository_labels() == sample_github_data["labels"]
        assert mock_boundary.get_repository_issues() == sample_github_data["issues"]
        assert mock_boundary.create_issue.return_value["number"] == 999
        assert mock_boundary.get_rate_limit_status()["remaining"] == 5000

    def test_create_with_data_full_uses_enhanced_configuration(
        self, sample_github_data
    ):
        """Test that create_with_data uses the enhanced configuration."""
        mock_boundary = MockBoundaryFactory.create_with_data(
            "full", sample_data=sample_github_data
        )

        # Should be protocol complete
        is_complete, missing = MockBoundaryFactory.validate_protocol_completeness(
            mock_boundary
        )
        assert is_complete, f"Missing methods: {missing}"

        # Should have sample data configured
        assert mock_boundary.get_repository_labels() == sample_github_data["labels"]
        assert mock_boundary.get_repository_issues() == sample_github_data["issues"]

        # Should have all creation methods configured
        assert mock_boundary.create_label.return_value["id"] == 999
        assert mock_boundary.create_issue.return_value["number"] == 999

    def test_create_with_data_empty_has_all_methods(self):
        """Test that empty configuration still has all methods."""
        mock_boundary = MockBoundaryFactory.create_with_data("empty")

        # Should be protocol complete
        is_complete, missing = MockBoundaryFactory.validate_protocol_completeness(
            mock_boundary
        )
        assert is_complete, f"Missing methods: {missing}"

        # Should have empty data
        assert mock_boundary.get_repository_labels() == []
        assert mock_boundary.get_repository_issues() == []

        # Should still have creation methods configured
        assert mock_boundary.create_issue.return_value["number"] == 999

    def test_create_for_restore_is_protocol_complete(self):
        """Test that restore mock is protocol complete."""
        mock_boundary = MockBoundaryFactory.create_for_restore()

        # Should be protocol complete
        is_complete, missing = MockBoundaryFactory.validate_protocol_completeness(
            mock_boundary
        )
        assert is_complete, f"Missing methods: {missing}"

        # Should be configured for empty repository
        assert mock_boundary.get_repository_labels() == []

        # Should have detailed creation responses
        create_result = mock_boundary.create_issue.return_value
        assert create_result["number"] == 999
        assert create_result["title"] == "test"
        assert "user" in create_result

    def test_backward_compatibility(self, sample_github_data):
        """Test that old usage patterns still work."""
        # Old pattern should still work
        mock_boundary = MockBoundaryFactory.create_with_data(
            "full", sample_data=sample_github_data
        )

        # Add PR support (old method)
        MockBoundaryFactory.add_pr_support(mock_boundary, sample_github_data)

        # Should still be complete and have PR methods working
        is_complete, missing = MockBoundaryFactory.validate_protocol_completeness(
            mock_boundary
        )
        assert is_complete, f"Missing methods: {missing}"

        assert mock_boundary.get_repository_pull_requests() == sample_github_data.get(
            "pull_requests", []
        )
