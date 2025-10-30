"""Tests for protocol validation utilities."""

import pytest
from unittest.mock import Mock

from github_data.github.protocols import GitHubApiBoundary
from tests.shared.mocks.boundary_factory import MockBoundaryFactory
from tests.shared.mocks.protocol_validation import (
    ProtocolValidator,
    BoundaryMockAuditor,
    validate_boundary_mock,
    assert_boundary_mock_complete,
)


class TestProtocolValidator:
    """Test the protocol validation functionality."""

    def test_validate_protocol_completeness_with_complete_mock(
        self, sample_github_data
    ):
        """Test validation of a complete mock boundary."""
        mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)

        is_complete, issues, details = ProtocolValidator.validate_protocol_completeness(
            mock_boundary, GitHubApiBoundary
        )

        assert is_complete
        assert len(issues) == 0
        assert details["completeness_percentage"] == 100.0
        assert details["total_protocol_methods"] > 20  # Should have many methods
        assert len(details["properly_configured"]) > 20
        assert len(details["missing_methods"]) == 0
        assert len(details["misconfigured_methods"]) == 0

    def test_validate_protocol_completeness_with_incomplete_mock(self):
        """Test validation of an incomplete mock boundary."""
        # Create a deliberately incomplete mock
        mock_boundary = Mock()
        mock_boundary.get_repository_labels.return_value = []
        mock_boundary.create_issue.return_value = {"id": 1}
        # Missing many other methods

        is_complete, issues, details = ProtocolValidator.validate_protocol_completeness(
            mock_boundary, GitHubApiBoundary
        )

        assert not is_complete
        assert len(issues) > 0
        assert details["completeness_percentage"] < 100.0
        assert (
            len(details["missing_methods"]) > 0
            or len(details["misconfigured_methods"]) > 0
        )

    def test_generate_validation_report_complete(self, sample_github_data):
        """Test generating validation report for complete mock."""
        mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)

        report = ProtocolValidator.generate_validation_report(
            mock_boundary, GitHubApiBoundary
        )

        assert "PASSED: Mock boundary is fully protocol-compliant" in report
        assert "100.0%" in report
        assert "✅" in report

    def test_generate_validation_report_incomplete(self):
        """Test generating validation report for incomplete mock."""
        mock_boundary = Mock()
        mock_boundary.get_repository_labels.return_value = []

        report = ProtocolValidator.generate_validation_report(
            mock_boundary, GitHubApiBoundary
        )

        assert "FAILED: Mock boundary has protocol compliance issues" in report
        assert "Missing Methods" in report
        assert "MockBoundaryFactory.create_auto_configured" in report
        assert "❌" in report

    def test_assert_protocol_complete_success(self, sample_github_data):
        """Test assertion passes for complete mock."""
        mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)

        # Should not raise
        ProtocolValidator.assert_protocol_complete(mock_boundary, GitHubApiBoundary)

    def test_assert_protocol_complete_failure(self):
        """Test assertion fails for incomplete mock."""
        mock_boundary = Mock()
        mock_boundary.get_repository_labels.return_value = []

        with pytest.raises(AssertionError) as excinfo:
            ProtocolValidator.assert_protocol_complete(mock_boundary, GitHubApiBoundary)

        assert "not protocol-complete" in str(excinfo.value)

    def test_assert_protocol_complete_custom_error(self):
        """Test assertion with custom error message."""
        mock_boundary = Mock()

        with pytest.raises(AssertionError) as excinfo:
            ProtocolValidator.assert_protocol_complete(
                mock_boundary, GitHubApiBoundary, "Custom error message"
            )

        assert "Custom error message" in str(excinfo.value)


class TestConvenienceFunctions:
    """Test convenience functions for protocol validation."""

    def test_validate_boundary_mock_true(self, sample_github_data):
        """Test convenience function returns True for complete mock."""
        mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)

        assert validate_boundary_mock(mock_boundary) is True

    def test_validate_boundary_mock_false(self):
        """Test convenience function returns False for incomplete mock."""
        mock_boundary = Mock()
        mock_boundary.get_repository_labels.return_value = []

        assert validate_boundary_mock(mock_boundary) is False

    def test_assert_boundary_mock_complete_success(self, sample_github_data):
        """Test convenience assertion passes for complete mock."""
        mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)

        # Should not raise
        assert_boundary_mock_complete(mock_boundary)

    def test_assert_boundary_mock_complete_failure(self):
        """Test convenience assertion fails for incomplete mock."""
        mock_boundary = Mock()

        with pytest.raises(AssertionError):
            assert_boundary_mock_complete(mock_boundary)


class TestBoundaryMockAuditor:
    """Test the boundary mock auditor functionality."""

    def test_audit_test_file_with_patterns(self, tmp_path):
        """Test auditing a file with mock patterns."""
        test_file = tmp_path / "test_example.py"
        test_file.write_text(
            """
from unittest.mock import Mock

def test_example():
    mock_boundary = Mock()
    mock_boundary.get_repository_labels.return_value = []
    mock_boundary.get_repository_issues.return_value = []
    mock_boundary.create_issue.return_value = {"id": 1}
"""
        )

        result = BoundaryMockAuditor.audit_test_file(str(test_file))

        assert result["total_patterns"] > 0
        assert result["mock_variables"] >= 1
        assert result["uses_factory_pattern"] is False
        assert "mock_boundary" in [
            p.get("variable") for p in result["manual_patterns"] if p.get("variable")
        ]

    def test_audit_test_file_with_factory(self, tmp_path):
        """Test auditing a file that uses MockBoundaryFactory."""
        test_file = tmp_path / "test_factory.py"
        test_file.write_text(
            """
from tests.shared.mocks.boundary_factory import MockBoundaryFactory

def test_example():
    mock_boundary = MockBoundaryFactory.create_auto_configured(sample_data)
"""
        )

        result = BoundaryMockAuditor.audit_test_file(str(test_file))

        assert result["uses_factory_pattern"] is True
        assert (
            result["total_patterns"] >= 0
        )  # May have some patterns from the factory call

    def test_audit_test_file_not_found(self):
        """Test auditing a non-existent file."""
        result = BoundaryMockAuditor.audit_test_file("/nonexistent/file.py")

        assert "error" in result
        assert "File not found" in result["error"]

    def test_generate_audit_summary_empty(self):
        """Test generating summary with no audit results."""
        summary = BoundaryMockAuditor.generate_audit_summary([])

        assert "No audit results to summarize" in summary

    def test_generate_audit_summary_with_results(self):
        """Test generating summary with audit results."""
        results = [
            {
                "file_path": "/test1.py",
                "total_patterns": 15,
                "uses_factory_pattern": False,
                "migration_priority": "high",
            },
            {
                "file_path": "/test2.py",
                "total_patterns": 3,
                "uses_factory_pattern": True,
                "migration_priority": "low",
            },
        ]

        summary = BoundaryMockAuditor.generate_audit_summary(results)

        assert "**Total files audited**: 2" in summary
        assert "**Factory adoption rate**: 50.0%" in summary
        assert "High priority" in summary
        assert "test1.py" in summary
        assert "Estimated Migration Effort" in summary


class TestIntegrationWithFactoryMethods:
    """Integration tests with various factory methods."""

    def test_create_with_data_full_is_protocol_complete(self, sample_github_data):
        """Test that create_with_data full is protocol complete."""
        mock_boundary = MockBoundaryFactory.create_with_data(
            "full", sample_data=sample_github_data
        )

        assert validate_boundary_mock(mock_boundary)
        assert_boundary_mock_complete(mock_boundary)

    def test_create_with_data_empty_is_protocol_complete(self):
        """Test that create_with_data empty is protocol complete."""
        mock_boundary = MockBoundaryFactory.create_with_data("empty")

        assert validate_boundary_mock(mock_boundary)
        assert_boundary_mock_complete(mock_boundary)

    def test_create_for_restore_is_protocol_complete(self):
        """Test that create_for_restore is protocol complete."""
        mock_boundary = MockBoundaryFactory.create_for_restore()

        assert validate_boundary_mock(mock_boundary)
        assert_boundary_mock_complete(mock_boundary)

    def test_create_auto_configured_is_protocol_complete(self, sample_github_data):
        """Test that create_auto_configured is protocol complete."""
        mock_boundary = MockBoundaryFactory.create_auto_configured(sample_github_data)

        assert validate_boundary_mock(mock_boundary)
        assert_boundary_mock_complete(mock_boundary)

    def test_create_protocol_complete_validates(self, sample_github_data):
        """Test that create_protocol_complete validates itself."""
        mock_boundary = MockBoundaryFactory.create_protocol_complete(sample_github_data)

        assert validate_boundary_mock(mock_boundary)
        assert_boundary_mock_complete(mock_boundary)
