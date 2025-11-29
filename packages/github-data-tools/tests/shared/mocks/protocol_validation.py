"""Protocol validation utilities for ensuring boundary mock completeness."""

from typing import List, Dict, Tuple, Any

from github_data_tools.github.protocols import GitHubApiBoundary


class ProtocolValidator:
    """Validator for protocol completeness and mock configuration correctness."""

    @staticmethod
    def validate_protocol_completeness(
        mock_boundary, protocol_class
    ) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Validate that a mock boundary implements all protocol methods.

        Args:
            mock_boundary: Mock boundary to validate
            protocol_class: Protocol class to validate against

        Returns:
            Tuple of (is_complete, missing_methods, validation_details)
        """
        protocol_methods = []
        for name in dir(protocol_class):
            if not name.startswith("_"):
                attr = getattr(protocol_class, name)
                if callable(attr) and hasattr(attr, "__isabstractmethod__"):
                    protocol_methods.append(name)

        missing_methods = []
        misconfigured_methods = []
        properly_configured = []

        for method_name in protocol_methods:
            try:
                # Check if the method was explicitly configured
                # For Mock objects, we need to check if it was set up
                # before being accessed
                if (
                    hasattr(mock_boundary, "_mock_children")
                    and method_name in mock_boundary._mock_children
                ):
                    # Method was explicitly set up
                    method = getattr(mock_boundary, method_name)
                    if hasattr(method, "return_value") or hasattr(
                        method, "side_effect"
                    ):
                        properly_configured.append(method_name)
                    else:
                        misconfigured_methods.append(method_name)
                elif (
                    hasattr(mock_boundary, "__dict__")
                    and method_name in mock_boundary.__dict__
                ):
                    # Method was configured via direct assignment
                    method = getattr(mock_boundary, method_name)
                    if hasattr(method, "return_value") or hasattr(
                        method, "side_effect"
                    ):
                        properly_configured.append(method_name)
                    else:
                        misconfigured_methods.append(method_name)
                else:
                    # Method was not explicitly configured
                    missing_methods.append(method_name)
            except AttributeError:
                missing_methods.append(method_name)

        is_complete = len(missing_methods) == 0 and len(misconfigured_methods) == 0

        validation_details = {
            "total_protocol_methods": len(protocol_methods),
            "missing_methods": missing_methods,
            "misconfigured_methods": misconfigured_methods,
            "properly_configured": properly_configured,
            "completeness_percentage": (
                (len(properly_configured) / len(protocol_methods)) * 100
                if protocol_methods
                else 100
            ),
        }

        return is_complete, missing_methods + misconfigured_methods, validation_details

    @staticmethod
    def generate_validation_report(mock_boundary, protocol_class) -> str:
        """Generate a detailed validation report for a mock boundary.

        Args:
            mock_boundary: Mock boundary to validate
            protocol_class: Protocol class to validate against

        Returns:
            Formatted validation report
        """
        is_complete, issues, details = ProtocolValidator.validate_protocol_completeness(
            mock_boundary, protocol_class
        )

        report = [
            f"# Protocol Validation Report: {protocol_class.__name__}",
            "",
            f"**Protocol completeness**: {details['completeness_percentage']:.1f}%",
            f"**Total protocol methods**: {details['total_protocol_methods']}",
            f"**Properly configured**: {len(details['properly_configured'])}",
            "",
        ]

        if is_complete:
            report.extend(
                [
                    "✅ **PASSED: Mock boundary is fully protocol-compliant**",
                    "",
                    "All required protocol methods are properly configured "
                    "with return_value or side_effect.",
                ]
            )
        else:
            report.extend(
                ["❌ **FAILED: Mock boundary has protocol compliance issues**", ""]
            )

            if details["missing_methods"]:
                report.extend(
                    [
                        f"## Missing Methods ({len(details['missing_methods'])})",
                        "These methods are not present on the mock boundary:",
                        "",
                    ]
                )
                for method in details["missing_methods"]:
                    report.append(f"- `{method}`")
                report.append("")

            if details["misconfigured_methods"]:
                report.extend(
                    [
                        f"## Misconfigured Methods "
                        f"({len(details['misconfigured_methods'])})",
                        "These methods exist but are not properly configured:",
                        "",
                    ]
                )
                for method in details["misconfigured_methods"]:
                    report.append(f"- `{method}` (no return_value or side_effect)")
                report.append("")

        if details["properly_configured"]:
            report.extend(
                [
                    f"## Properly Configured Methods "
                    f"({len(details['properly_configured'])})",
                    "These methods are correctly configured:",
                ]
            )
            if len(details["properly_configured"]) <= 10:
                report.append("")
                for method in details["properly_configured"]:
                    report.append(f"- `{method}`")
            else:
                report.append(
                    f" (showing first 10 of {len(details['properly_configured'])})"
                )
                report.append("")
                for method in details["properly_configured"][:10]:
                    report.append(f"- `{method}`")
                report.append(
                    f"- ... and {len(details['properly_configured']) - 10} more"
                )
            report.append("")

        report.extend(["## Recommendation", ""])

        if not is_complete:
            report.extend(
                [
                    "**Suggested fix:**",
                    "```python",
                    "# Replace manual mock setup with factory pattern",
                    "mock_boundary = "
                    "MockBoundaryFactory.create_auto_configured(sample_data)",
                    "```",
                    "",
                    "This will provide 100% protocol completeness with "
                    "appropriate return values.",
                ]
            )
        else:
            report.append(
                "✅ Mock boundary is correctly configured and protocol-compliant."
            )

        return "\n".join(report)

    @staticmethod
    def assert_protocol_complete(
        mock_boundary, protocol_class, error_message: str = None
    ) -> None:
        """Assert that a mock boundary is protocol-complete,
        raising AssertionError if not.

        Args:
            mock_boundary: Mock boundary to validate
            protocol_class: Protocol class to validate against
            error_message: Optional custom error message
        """
        is_complete, issues, details = ProtocolValidator.validate_protocol_completeness(
            mock_boundary, protocol_class
        )

        if not is_complete:
            if error_message is None:
                completeness = details["completeness_percentage"]
                extra_issues = f" and {len(issues) - 5} more" if len(issues) > 5 else ""
                error_message = (
                    f"Mock boundary is not protocol-complete "
                    f"({completeness:.1f}% complete). "
                    f"Issues found: {', '.join(issues[:5])}{extra_issues}"
                )

            raise AssertionError(error_message)


class BoundaryMockAuditor:
    """Auditor for analyzing boundary mock usage patterns across test files."""

    @staticmethod
    def audit_test_file(file_path: str) -> Dict[str, Any]:
        """Audit a test file for boundary mock usage patterns.

        Args:
            file_path: Path to the test file to audit

        Returns:
            Audit results with patterns and recommendations
        """
        try:
            with open(file_path, "r") as f:
                content = f.read()
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}

        from tests.shared.mocks.migration_utils import BoundaryMockMigrator

        patterns = BoundaryMockMigrator.detect_manual_mock_patterns(content)
        suggestions = BoundaryMockMigrator.suggest_sample_data_usage(patterns)

        # Check for existing MockBoundaryFactory usage
        factory_usage = "MockBoundaryFactory" in content

        audit_result = {
            "file_path": file_path,
            "total_patterns": len(patterns),
            "mock_variables": len(
                set(p.get("variable") for p in patterns if p.get("variable"))
            ),
            "uses_factory_pattern": factory_usage,
            "manual_patterns": patterns,
            "suggested_data_types": list(suggestions.keys()),
            "migration_priority": "low",
        }

        # Determine migration priority
        if audit_result["total_patterns"] >= 10:
            audit_result["migration_priority"] = "high"
        elif audit_result["total_patterns"] >= 5:
            audit_result["migration_priority"] = "medium"

        return audit_result

    @staticmethod
    def generate_audit_summary(audit_results: List[Dict[str, Any]]) -> str:
        """Generate a summary report from multiple file audits.

        Args:
            audit_results: List of audit results from audit_test_file

        Returns:
            Formatted audit summary report
        """
        if not audit_results:
            return "No audit results to summarize."

        # Calculate statistics
        total_files = len(audit_results)
        files_with_patterns = len(
            [r for r in audit_results if r.get("total_patterns", 0) > 0]
        )
        files_using_factory = len(
            [r for r in audit_results if r.get("uses_factory_pattern")]
        )
        total_patterns = sum(r.get("total_patterns", 0) for r in audit_results)

        high_priority = [
            r for r in audit_results if r.get("migration_priority") == "high"
        ]
        medium_priority = [
            r for r in audit_results if r.get("migration_priority") == "medium"
        ]
        low_priority = [
            r for r in audit_results if r.get("migration_priority") == "low"
        ]

        factory_adoption_rate = (
            (files_using_factory / total_files) * 100 if total_files > 0 else 0
        )

        report = [
            "# Boundary Mock Usage Audit Summary",
            "",
            "## Overview",
            f"- **Total files audited**: {total_files}",
            f"- **Files with manual mock patterns**: {files_with_patterns}",
            f"- **Files using MockBoundaryFactory**: {files_using_factory}",
            f"- **Factory adoption rate**: {factory_adoption_rate:.1f}%",
            f"- **Total manual patterns detected**: {total_patterns}",
            "",
            "## Migration Priority Distribution",
            f"- **High priority** ({len(high_priority)} files): 10+ patterns",
            f"- **Medium priority** ({len(medium_priority)} files): 5-9 patterns",
            f"- **Low priority** ({len(low_priority)} files): 1-4 patterns",
            "",
        ]

        if high_priority:
            report.extend(
                ["## High Priority Files", "These files should be migrated first:", ""]
            )
            for result in high_priority[:10]:  # Show top 10
                report.append(
                    f"- `{result['file_path']}` ({result['total_patterns']} patterns)"
                )
            if len(high_priority) > 10:
                report.append(f"- ... and {len(high_priority) - 10} more")
            report.append("")

        report.extend(["## Recommendations", "", "### Immediate Actions"])

        if high_priority:
            report.append(
                "1. **Migrate high-priority files** to "
                "MockBoundaryFactory.create_auto_configured()"
            )

        if factory_adoption_rate < 50:
            report.append("2. **Focus on factory adoption** - current rate is low")

        if files_with_patterns > files_using_factory:
            report.append(
                "3. **Systematic migration** - many files still use manual patterns"
            )

        report.extend(
            [
                "",
                "### Long-term Goals",
                "- Achieve 90%+ factory adoption rate",
                "- Eliminate manual mock configurations for protocol methods",
                "- Standardize on shared sample data usage",
                "",
                "### Estimated Migration Effort",
                f"- High priority files: {len(high_priority)} × 2-3 hours = "
                f"{len(high_priority) * 2.5:.1f} hours",
                f"- Medium priority files: {len(medium_priority)} × 1-2 hours = "
                f"{len(medium_priority) * 1.5:.1f} hours",
                f"- Low priority files: {len(low_priority)} × 0.5-1 hour = "
                f"{len(low_priority) * 0.75:.1f} hours",
            ]
        )

        total_effort = (
            len(high_priority) * 2.5
            + len(medium_priority) * 1.5
            + len(low_priority) * 0.75
        )
        report.append(f"- **Total estimated effort**: {total_effort:.1f} hours")

        return "\n".join(report)


def validate_boundary_mock(mock_boundary, protocol_class=GitHubApiBoundary) -> bool:
    """Convenience function to validate a boundary mock for protocol completeness.

    Args:
        mock_boundary: Mock boundary to validate
        protocol_class: Protocol class to validate against
            (defaults to GitHubApiBoundary)

    Returns:
        True if mock is protocol-complete, False otherwise
    """
    is_complete, _, _ = ProtocolValidator.validate_protocol_completeness(
        mock_boundary, protocol_class
    )
    return is_complete


def assert_boundary_mock_complete(
    mock_boundary, protocol_class=GitHubApiBoundary
) -> None:
    """Convenience function to assert boundary mock protocol completeness.

    Args:
        mock_boundary: Mock boundary to validate
        protocol_class: Protocol class to validate against
            (defaults to GitHubApiBoundary)

    Raises:
        AssertionError: If mock is not protocol-complete
    """
    ProtocolValidator.assert_protocol_complete(mock_boundary, protocol_class)
