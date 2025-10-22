"""Migration utilities for converting static fixtures to GitHubDataBuilder patterns."""

from typing import Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path

from .github_data_builder import GitHubDataBuilder


class FixtureToBuilderMigrator:
    """Utilities for migrating static fixtures to builder patterns."""

    @staticmethod
    def convert_milestone_fixtures(fixture_data: Dict[str, Any]) -> GitHubDataBuilder:
        """Convert milestone fixture data to builder calls.

        Args:
            fixture_data: Dictionary containing milestone fixture data

        Returns:
            GitHubDataBuilder instance configured with equivalent data
        """
        builder = GitHubDataBuilder()

        if "milestones" in fixture_data:
            milestones = fixture_data["milestones"]
            if milestones:
                # Convert milestone data to builder format
                custom_milestones = []
                for milestone in milestones:
                    converted_milestone = {
                        "id": milestone.get(
                            "id", f"M_kwDO{milestone.get('number', 1):06d}"
                        ),
                        "number": milestone.get("number", 1),
                        "title": milestone.get("title", "Converted Milestone"),
                        "description": milestone.get("description"),
                        "state": milestone.get("state", "open"),
                        "creator_login": milestone.get("creator_login", "converter"),
                        "creator_id": milestone.get("creator_id", "U_converter"),
                        "created_at": _parse_datetime(milestone.get("created_at")),
                        "updated_at": _parse_datetime(milestone.get("updated_at")),
                        "due_on": _parse_datetime(milestone.get("due_on")),
                        "closed_at": _parse_datetime(milestone.get("closed_at")),
                        "open_issues": milestone.get("open_issues", 0),
                        "closed_issues": milestone.get("closed_issues", 0),
                        "url": milestone.get(
                            "url",
                            (
                                f"https://github.com/owner/repo/milestone/"
                                f"{milestone.get('number', 1)}"
                            ),
                        ),
                    }
                    custom_milestones.append(converted_milestone)

                builder.with_milestones(custom_milestones=custom_milestones)

        # Handle issues with milestone relationships
        if "issues" in fixture_data:
            issues = fixture_data["issues"]
            if issues:
                builder.with_issues(custom_issues=issues)

                # Check for milestone relationships
                milestone_mappings = {}
                for issue in issues:
                    if issue.get("milestone"):
                        milestone_number = issue["milestone"]["number"]
                        issue_number = issue["number"]
                        if milestone_number not in milestone_mappings:
                            milestone_mappings[milestone_number] = []
                        milestone_mappings[milestone_number].append(issue_number)

                if milestone_mappings:
                    builder.with_milestone_relationships(milestone_mappings)

        return builder

    @staticmethod
    def convert_sub_issue_fixtures(fixture_data: Dict[str, Any]) -> GitHubDataBuilder:
        """Convert sub-issue fixture data to builder calls.

        Args:
            fixture_data: Dictionary containing sub-issue fixture data

        Returns:
            GitHubDataBuilder instance configured with equivalent data
        """
        builder = GitHubDataBuilder()

        # Add issues first
        if "issues" in fixture_data:
            builder.with_issues(custom_issues=fixture_data["issues"])

        # Add sub-issue relationships
        if "sub_issues" in fixture_data:
            builder.with_sub_issues(custom_sub_issues=fixture_data["sub_issues"])

        # Add other entities if present
        for entity_type in ["labels", "comments", "pull_requests", "pr_comments"]:
            if entity_type in fixture_data and fixture_data[entity_type]:
                if entity_type == "labels":
                    builder.with_labels(custom_labels=fixture_data[entity_type])
                elif entity_type == "comments":
                    builder.with_comments(custom_comments=fixture_data[entity_type])
                elif entity_type == "pull_requests":
                    builder.with_pull_requests(custom_prs=fixture_data[entity_type])
                elif entity_type == "pr_comments":
                    builder.with_pr_comments(
                        custom_pr_comments=fixture_data[entity_type]
                    )

        return builder

    @staticmethod
    def analyze_fixture_complexity(fixture_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze fixture data to suggest appropriate builder methods.

        Args:
            fixture_data: Dictionary containing fixture data

        Returns:
            Analysis report with suggested builder methods
        """
        analysis = {
            "entity_counts": {},
            "relationships": {},
            "suggested_methods": [],
            "complexity_score": 0,
        }

        # Count entities
        for entity_type in [
            "labels",
            "issues",
            "comments",
            "pull_requests",
            "pr_comments",
            "milestones",
            "sub_issues",
        ]:
            count = len(fixture_data.get(entity_type, []))
            analysis["entity_counts"][entity_type] = count
            if count > 0:
                analysis["complexity_score"] += count

        # Analyze relationships
        if "issues" in fixture_data:
            issues_with_milestones = sum(
                1 for issue in fixture_data["issues"] if issue.get("milestone")
            )
            analysis["relationships"]["issues_with_milestones"] = issues_with_milestones

        if "sub_issues" in fixture_data:
            parent_issues = set(
                rel["parent_issue_number"] for rel in fixture_data["sub_issues"]
            )
            analysis["relationships"]["parent_issues_count"] = len(parent_issues)
            analysis["relationships"]["sub_issues_count"] = len(
                fixture_data["sub_issues"]
            )

        # Suggest methods based on analysis
        suggestions = []
        if analysis["entity_counts"]["labels"] > 0:
            suggestions.append(f"with_labels({analysis['entity_counts']['labels']})")
        if analysis["entity_counts"]["issues"] > 0:
            suggestions.append(f"with_issues({analysis['entity_counts']['issues']})")
        if analysis["entity_counts"]["milestones"] > 0:
            suggestions.append(
                f"with_milestones({analysis['entity_counts']['milestones']})"
            )
            if analysis["relationships"].get("issues_with_milestones", 0) > 0:
                suggestions.append("with_milestone_relationships()")
        if analysis["entity_counts"]["sub_issues"] > 0:
            suggestions.append("with_sub_issues()")

        analysis["suggested_methods"] = suggestions

        return analysis

    @staticmethod
    def generate_migration_code(
        fixture_data: Dict[str, Any], builder_name: str = "builder"
    ) -> str:
        """Generate Python code for migrating fixture to builder pattern.

        Args:
            fixture_data: Dictionary containing fixture data
            builder_name: Variable name for the builder instance

        Returns:
            Python code string for creating equivalent data with builder
        """
        analysis = FixtureToBuilderMigrator.analyze_fixture_complexity(fixture_data)

        lines = [f"{builder_name} = GitHubDataBuilder()"]

        # Add method calls based on analysis
        for method in analysis["suggested_methods"]:
            lines.append(f"{builder_name} = {builder_name}.{method}")

        lines.append(f"data = {builder_name}.build()")

        return "\n".join(lines)

    @staticmethod
    def validate_migration(
        original_fixture: Dict[str, Any], builder_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate that migration preserved essential data.

        Args:
            original_fixture: Original fixture data
            builder_data: Data generated by builder

        Returns:
            Validation report with any discrepancies
        """
        report = {
            "is_valid": True,
            "discrepancies": [],
            "entity_count_comparison": {},
        }

        # Compare entity counts
        for entity_type in [
            "labels",
            "issues",
            "comments",
            "pull_requests",
            "pr_comments",
            "milestones",
            "sub_issues",
        ]:
            original_count = len(original_fixture.get(entity_type, []))
            builder_count = len(builder_data.get(entity_type, []))

            report["entity_count_comparison"][entity_type] = {
                "original": original_count,
                "builder": builder_count,
                "matches": original_count == builder_count,
            }

            if original_count != builder_count:
                report["is_valid"] = False
                report["discrepancies"].append(
                    f"{entity_type}: expected {original_count}, got {builder_count}"
                )

        # Validate specific relationships
        if "sub_issues" in original_fixture and "sub_issues" in builder_data:
            original_relationships = set(
                (rel["parent_issue_number"], rel["sub_issue_number"])
                for rel in original_fixture["sub_issues"]
            )
            builder_relationships = set(
                (rel["parent_issue_number"], rel["sub_issue_number"])
                for rel in builder_data["sub_issues"]
            )

            if original_relationships != builder_relationships:
                report["is_valid"] = False
                report["discrepancies"].append("Sub-issue relationships don't match")

        return report


def _parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Parse datetime string with fallback to None."""
    if not dt_str:
        return None

    try:
        # Handle ISO format with timezone
        if dt_str.endswith("Z"):
            dt_str = dt_str[:-1] + "+00:00"
        return datetime.fromisoformat(dt_str)
    except (ValueError, TypeError):
        # Fallback for other formats
        try:
            return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S%z")
        except (ValueError, TypeError):
            return None


def load_and_convert_fixture_file(fixture_path: Path) -> GitHubDataBuilder:
    """Load a fixture file and convert it to a builder.

    Args:
        fixture_path: Path to the fixture file

    Returns:
        GitHubDataBuilder instance with converted data
    """
    with open(fixture_path, "r") as f:
        if fixture_path.suffix == ".json":
            fixture_data = json.load(f)
        else:
            # For .py files, we'd need to import and extract the data
            # This is a simplified version - in practice you'd need more
            # sophisticated parsing
            raise NotImplementedError("Python fixture file parsing not implemented")

    # Determine conversion strategy based on content
    if "milestones" in fixture_data:
        return FixtureToBuilderMigrator.convert_milestone_fixtures(fixture_data)
    elif "sub_issues" in fixture_data:
        return FixtureToBuilderMigrator.convert_sub_issue_fixtures(fixture_data)
    else:
        # Generic conversion
        builder = GitHubDataBuilder()
        for entity_type, data in fixture_data.items():
            if entity_type == "labels" and data:
                builder.with_labels(custom_labels=data)
            elif entity_type == "issues" and data:
                builder.with_issues(custom_issues=data)
            elif entity_type == "comments" and data:
                builder.with_comments(custom_comments=data)
            elif entity_type == "pull_requests" and data:
                builder.with_pull_requests(custom_prs=data)
            elif entity_type == "pr_comments" and data:
                builder.with_pr_comments(custom_pr_comments=data)

        return builder
