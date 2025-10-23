"""Tests for GitHubDataBuilder extensions (Week 1 implementation)."""

import pytest

from tests.shared.builders.github_data_builder import GitHubDataBuilder
from tests.shared.builders.migration_utilities import FixtureToBuilderMigrator


class TestMilestoneSupport:
    """Test milestone generation and relationship features."""

    def test_with_milestones_default(self):
        """Test milestone creation with default parameters."""
        builder = GitHubDataBuilder()
        data = builder.with_milestones().build()

        assert len(data["milestones"]) == 2

        milestone = data["milestones"][0]
        assert milestone["number"] == 1
        assert milestone["title"] == "Milestone 1"
        assert milestone["state"] == "open"
        assert milestone["open_issues"] == 5
        assert milestone["closed_issues"] == 0

        # Check ID format
        assert milestone["id"].startswith("M_kwDO")

        # Check dates
        assert isinstance(milestone["created_at"], str)
        assert milestone["created_at"].endswith("Z")  # UTC timezone indicator

    def test_with_milestones_closed(self):
        """Test milestone creation with closed milestones."""
        builder = GitHubDataBuilder()
        data = builder.with_milestones(count=3, include_closed=True).build()

        assert len(data["milestones"]) == 3

        # Every other milestone should be closed
        open_milestones = [m for m in data["milestones"] if m["state"] == "open"]
        closed_milestones = [m for m in data["milestones"] if m["state"] == "closed"]

        assert len(open_milestones) == 2  # milestones 1 and 3
        assert len(closed_milestones) == 1  # milestone 2

        closed_milestone = closed_milestones[0]
        assert closed_milestone["closed_at"] is not None
        assert closed_milestone["open_issues"] == 0

    def test_with_milestones_custom(self):
        """Test milestone creation with custom data."""
        custom_milestones = [
            {
                "id": "M_custom_001",
                "number": 99,
                "title": "Custom Milestone",
                "description": "Custom description",
                "state": "open",
                "creator": {
                    "login": "custom_user",
                    "id": 999,
                    "avatar_url": "https://github.com/custom_user.png",
                    "html_url": "https://github.com/custom_user",
                },
                "created_at": "2023-06-01T00:00:00Z",
                "updated_at": "2023-06-02T00:00:00Z",
                "due_on": "2023-12-31T00:00:00Z",
                "closed_at": None,
                "open_issues": 10,
                "closed_issues": 5,
                "url": "https://github.com/custom/repo/milestone/99",
            }
        ]

        builder = GitHubDataBuilder()
        data = builder.with_milestones(custom_milestones=custom_milestones).build()

        assert len(data["milestones"]) == 1
        milestone = data["milestones"][0]
        assert milestone["title"] == "Custom Milestone"
        assert milestone["number"] == 99
        assert milestone["creator"]["login"] == "custom_user"

    def test_milestone_relationships_auto(self):
        """Test automatic milestone-issue relationships."""
        builder = GitHubDataBuilder()
        data = (
            builder.with_milestones(count=2)
            .with_issues(count=4)
            .with_milestone_relationships()
            .build()
        )

        assert len(data["milestones"]) == 2
        assert len(data["issues"]) == 4

        # Check that issues have milestone assignments
        milestoned_issues = [
            issue for issue in data["issues"] if issue.get("milestone")
        ]
        assert len(milestoned_issues) == 4

        # Check distribution (should alternate between milestone 1 and 2)
        milestone_1_issues = [
            i for i in data["issues"] if i.get("milestone", {}).get("number") == 1
        ]
        milestone_2_issues = [
            i for i in data["issues"] if i.get("milestone", {}).get("number") == 2
        ]

        assert len(milestone_1_issues) == 2
        assert len(milestone_2_issues) == 2

    def test_milestone_relationships_explicit(self):
        """Test explicit milestone-issue mapping."""
        builder = GitHubDataBuilder()
        mapping = {1: [1, 3], 2: [2]}

        data = (
            builder.with_milestones(count=2)
            .with_issues(count=3)
            .with_milestone_relationships(mapping)
            .build()
        )

        # Check specific assignments
        issue_1 = next(i for i in data["issues"] if i["number"] == 1)
        issue_2 = next(i for i in data["issues"] if i["number"] == 2)
        issue_3 = next(i for i in data["issues"] if i["number"] == 3)

        assert issue_1["milestone"]["number"] == 1
        assert issue_2["milestone"]["number"] == 2
        assert issue_3["milestone"]["number"] == 1


class TestSubIssueSupport:
    """Test sub-issue generation and hierarchy features."""

    def test_with_sub_issues_default(self):
        """Test sub-issue creation with default parameters."""
        builder = GitHubDataBuilder()
        data = builder.with_sub_issues().build()

        # Should create 3 parent issues + 4 sub-issues (2 per parent for first
        # 2 parents)
        assert len(data["issues"]) == 7  # 3 original + 4 sub-issues
        assert len(data["sub_issues"]) == 4  # 2 parents × 2 sub-issues each

        # Check sub-issue relationships
        parent_1_subs = [
            rel for rel in data["sub_issues"] if rel["parent_issue_number"] == 1
        ]
        parent_2_subs = [
            rel for rel in data["sub_issues"] if rel["parent_issue_number"] == 2
        ]

        assert len(parent_1_subs) == 2
        assert len(parent_2_subs) == 2

        # Check positions
        assert parent_1_subs[0]["position"] == 1
        assert parent_1_subs[1]["position"] == 2

    def test_with_sub_issues_specific_parents(self):
        """Test sub-issue creation for specific parent issues."""
        builder = GitHubDataBuilder()
        data = (
            builder.with_issues(count=5)
            .with_sub_issues(parent_issue_numbers=[2, 4], sub_issues_per_parent=3)
            .build()
        )

        assert len(data["issues"]) == 11  # 5 original + 6 sub-issues
        assert len(data["sub_issues"]) == 6  # 2 parents × 3 sub-issues each

        # Check that only issues 2 and 4 have sub-issues
        parent_numbers = {rel["parent_issue_number"] for rel in data["sub_issues"]}
        assert parent_numbers == {2, 4}

    def test_with_sub_issues_custom(self):
        """Test sub-issue creation with custom data."""
        custom_sub_issues = [
            {
                "sub_issue_id": 9999,
                "sub_issue_number": 999,
                "parent_issue_id": 1001,
                "parent_issue_number": 101,
                "position": 1,
            }
        ]

        builder = GitHubDataBuilder()
        data = builder.with_sub_issues(custom_sub_issues=custom_sub_issues).build()

        assert len(data["sub_issues"]) == 1
        rel = data["sub_issues"][0]
        assert rel["sub_issue_number"] == 999
        assert rel["parent_issue_number"] == 101

    def test_sub_issue_hierarchy_default(self):
        """Test complex hierarchical sub-issue creation."""
        builder = GitHubDataBuilder()
        data = builder.with_sub_issue_hierarchy().build()

        # Should have 1 root + hierarchy
        # Level 1: 2 children
        # Level 2: 2×2 = 4 children
        # Level 3: 4×2 = 8 children
        # Total: 1 + 2 + 4 + 8 = 15 issues
        # Relationships: 2 + 4 + 8 = 14 relationships

        assert len(data["issues"]) == 15
        assert len(data["sub_issues"]) == 14

    def test_sub_issue_hierarchy_with_orphaned(self):
        """Test hierarchy creation with orphaned sub-issues."""
        builder = GitHubDataBuilder()
        data = builder.with_sub_issue_hierarchy(
            depth=2, children_per_level=1, include_orphaned=True
        ).build()

        # Should have orphaned sub-issue
        orphaned_relationships = [
            rel for rel in data["sub_issues"] if rel["parent_issue_number"] == 99999
        ]
        assert len(orphaned_relationships) == 1

        orphaned_rel = orphaned_relationships[0]
        assert orphaned_rel["parent_issue_id"] == 99999

    def test_sub_issue_hierarchy_custom_depth(self):
        """Test hierarchy creation with custom depth and branching."""
        builder = GitHubDataBuilder()
        data = builder.with_sub_issue_hierarchy(depth=2, children_per_level=3).build()

        # Level 0: 1 root
        # Level 1: 3 children
        # Level 2: 3×3 = 9 children
        # Total: 1 + 3 + 9 = 13 issues

        assert len(data["issues"]) == 13
        assert len(data["sub_issues"]) == 12  # All except root


class TestEnhancedBuildMethods:
    """Test enhanced build methods with new entities."""

    def test_build_complex_includes_milestones_and_sub_issues(self):
        """Test that build_complex includes the new entities."""
        builder = GitHubDataBuilder()
        data = builder.build_complex()

        # Should include all entity types
        assert len(data["milestones"]) == 3
        assert len(data["sub_issues"]) > 0
        assert len(data["issues"]) > 5  # Original + sub-issues

        # Check milestone relationships exist
        milestoned_issues = [
            issue for issue in data["issues"] if issue.get("milestone")
        ]
        assert len(milestoned_issues) > 0

    def test_build_milestone_workflow(self):
        """Test milestone workflow builder."""
        builder = GitHubDataBuilder()
        data = builder.build_milestone_workflow()

        assert len(data["milestones"]) == 2
        assert len(data["issues"]) == 8  # 4 original + 4 sub-issues
        assert len(data["sub_issues"]) == 4

        # All milestones should be open
        open_milestones = [m for m in data["milestones"] if m["state"] == "open"]
        assert len(open_milestones) == 2

    def test_build_hierarchical_issues(self):
        """Test hierarchical issues builder."""
        builder = GitHubDataBuilder()
        data = builder.build_hierarchical_issues()

        assert len(data["milestones"]) == 1
        assert len(data["issues"]) > 1  # Root + hierarchy
        assert len(data["sub_issues"]) > 0

        # Should include orphaned sub-issues
        orphaned_rels = [
            rel for rel in data["sub_issues"] if rel["parent_issue_number"] == 99999
        ]
        assert len(orphaned_rels) == 1


class TestRelationshipValidation:
    """Test relationship validation functionality."""

    def test_validate_relationships_valid_data(self):
        """Test validation with valid relationships."""
        builder = GitHubDataBuilder()
        data = (
            builder.with_milestones(count=2)
            .with_issues(count=3)
            .with_milestone_relationships()
            .with_sub_issues(parent_issue_numbers=[1], sub_issues_per_parent=1)
            .build()
        )

        # Re-create builder with the data to test validation
        test_builder = GitHubDataBuilder()
        test_builder.data = data

        errors = test_builder.validate_relationships()
        assert len(errors) == 0

    def test_validate_relationships_missing_milestone(self):
        """Test validation with missing milestone reference."""
        builder = GitHubDataBuilder()
        builder.with_issues(count=1)

        # Manually add invalid milestone reference
        builder.data["issues"][0]["milestone"] = {"number": 999}

        errors = builder.validate_relationships()
        assert len(errors) == 1
        assert "non-existent milestone #999" in errors[0]

    def test_validate_relationships_missing_parent_issue(self):
        """Test validation with missing parent issue."""
        builder = GitHubDataBuilder()
        builder.with_issues(count=1)

        # Manually add invalid sub-issue relationship
        builder.data["sub_issues"].append(
            {
                "sub_issue_id": 8001,
                "sub_issue_number": 2,
                "parent_issue_id": 99999,
                "parent_issue_number": 999,
                "position": 1,
            }
        )

        errors = builder.validate_relationships()
        assert len(errors) >= 1
        assert any("non-existent parent issue" in error for error in errors)


class TestMigrationUtilities:
    """Test migration utilities for converting fixtures."""

    def test_analyze_fixture_complexity(self):
        """Test fixture complexity analysis."""
        fixture_data = {
            "milestones": [{"number": 1, "title": "Test"}],
            "issues": [{"number": 1}, {"number": 2}],
            "sub_issues": [{"parent_issue_number": 1, "sub_issue_number": 2}],
        }

        analysis = FixtureToBuilderMigrator.analyze_fixture_complexity(fixture_data)

        assert analysis["entity_counts"]["milestones"] == 1
        assert analysis["entity_counts"]["issues"] == 2
        assert analysis["entity_counts"]["sub_issues"] == 1
        assert analysis["complexity_score"] == 4

        # Check suggested methods
        suggestions = analysis["suggested_methods"]
        assert "with_milestones(1)" in suggestions
        assert "with_issues(2)" in suggestions
        assert "with_sub_issues()" in suggestions

    def test_convert_milestone_fixtures(self):
        """Test milestone fixture conversion."""
        fixture_data = {
            "milestones": [
                {
                    "id": "M_test_001",
                    "number": 1,
                    "title": "Test Milestone",
                    "description": "Test description",
                    "state": "open",
                    "creator_login": "testuser",
                    "creator_id": "U_test",
                    "created_at": "2023-01-01T00:00:00+00:00",
                    "updated_at": "2023-01-01T00:00:00+00:00",
                    "due_on": None,
                    "closed_at": None,
                    "open_issues": 3,
                    "closed_issues": 0,
                    "url": "https://github.com/test/repo/milestone/1",
                }
            ]
        }

        builder = FixtureToBuilderMigrator.convert_milestone_fixtures(fixture_data)
        data = builder.build()

        assert len(data["milestones"]) == 1
        milestone = data["milestones"][0]
        assert milestone["title"] == "Test Milestone"
        assert milestone["id"] == "M_test_001"

    def test_convert_sub_issue_fixtures(self):
        """Test sub-issue fixture conversion."""
        fixture_data = {
            "issues": [
                {"id": 1, "number": 1, "title": "Parent Issue"},
                {"id": 2, "number": 2, "title": "Sub Issue"},
            ],
            "sub_issues": [
                {
                    "sub_issue_id": 2,
                    "sub_issue_number": 2,
                    "parent_issue_id": 1,
                    "parent_issue_number": 1,
                    "position": 1,
                }
            ],
        }

        builder = FixtureToBuilderMigrator.convert_sub_issue_fixtures(fixture_data)
        data = builder.build()

        assert len(data["issues"]) == 2
        assert len(data["sub_issues"]) == 1
        assert data["sub_issues"][0]["parent_issue_number"] == 1

    def test_generate_migration_code(self):
        """Test migration code generation."""
        fixture_data = {
            "milestones": [{"number": 1}],
            "issues": [{"number": 1}, {"number": 2}],
        }

        code = FixtureToBuilderMigrator.generate_migration_code(
            fixture_data, "test_builder"
        )

        assert "test_builder = GitHubDataBuilder()" in code
        assert "with_milestones(1)" in code
        assert "with_issues(2)" in code
        assert "data = test_builder.build()" in code

    def test_validate_migration(self):
        """Test migration validation."""
        original = {
            "issues": [{"number": 1}, {"number": 2}],
            "milestones": [{"number": 1}],
        }

        builder_data = {
            "issues": [{"number": 1}, {"number": 2}],
            "milestones": [{"number": 1}],
            "labels": [],
            "comments": [],
            "pull_requests": [],
            "pr_comments": [],
            "sub_issues": [],
            "pr_reviews": [],
            "pr_review_comments": [],
            "users": [],
        }

        report = FixtureToBuilderMigrator.validate_migration(original, builder_data)

        assert report["is_valid"] is True
        assert len(report["discrepancies"]) == 0
        assert report["entity_count_comparison"]["issues"]["matches"] is True
        assert report["entity_count_comparison"]["milestones"]["matches"] is True


@pytest.mark.integration
class TestBuilderIntegration:
    """Integration tests for complete builder workflows."""

    def test_complete_workflow_with_all_entities(self):
        """Test complete workflow using all new builder features."""
        builder = GitHubDataBuilder()
        data = (
            builder.with_labels(3)
            .with_milestones(2, include_closed=True, with_due_dates=True)
            .with_issues(6, include_closed=True)
            .with_milestone_relationships()
            .with_sub_issues(parent_issue_numbers=[1, 3], sub_issues_per_parent=2)
            .with_comments(4, 1)
            .with_pull_requests(2)
            .with_pr_comments(1, 1)
            .build()
        )

        # Validate all entities are present
        assert len(data["labels"]) == 3
        assert len(data["milestones"]) == 2
        assert len(data["issues"]) == 10  # 6 original + 4 sub-issues
        assert len(data["sub_issues"]) == 4
        assert len(data["comments"]) > 0
        assert len(data["pull_requests"]) == 2
        assert len(data["pr_comments"]) > 0

        # Validate relationships
        test_builder = GitHubDataBuilder()
        test_builder.data = data
        errors = test_builder.validate_relationships()
        assert len(errors) == 0, f"Validation errors: {errors}"

    def test_complex_hierarchy_workflow(self):
        """Test complex hierarchical workflow."""
        builder = GitHubDataBuilder()
        data = (
            builder.with_milestones(1)
            .with_issues(1)
            .with_milestone_relationships()
            .with_sub_issue_hierarchy(
                depth=4, children_per_level=2, include_orphaned=True
            )
            .build()
        )

        # Should have deep hierarchy
        assert len(data["issues"]) > 10  # Many issues in hierarchy
        assert len(data["sub_issues"]) > 10  # Many relationships

        # Should have orphaned sub-issue
        orphaned = [
            rel for rel in data["sub_issues"] if rel["parent_issue_number"] == 99999
        ]
        assert len(orphaned) == 1

        # Validate structure
        test_builder = GitHubDataBuilder()
        test_builder.data = data
        errors = test_builder.validate_relationships()
        # Allow orphaned relationship error
        other_errors = [e for e in errors if "99999" not in e]
        assert len(other_errors) == 0, f"Non-orphan validation errors: {other_errors}"
