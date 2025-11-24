"""Tests for Week 3 GitHubDataBuilder extensions - Users and Repositories."""

import pytest
from tests.shared.builders.github_data_builder import GitHubDataBuilder


class TestStandaloneUserSupport:
    """Test standalone user generation functionality."""

    def test_with_users_default(self):
        """Test basic user generation with default settings."""
        data = GitHubDataBuilder().with_users(3).build()

        assert len(data["users"]) == 3

        for i, user in enumerate(data["users"]):
            assert "login" in user
            assert "id" in user
            assert "avatar_url" in user
            assert "html_url" in user
            assert user["type"] == "User"
            assert user["site_admin"] is False
            assert "name" in user
            assert "email" in user
            assert "bio" in user
            assert user["login"].startswith("user")
            assert user["avatar_url"] == f"https://github.com/{user['login']}.png"

    def test_with_users_include_organizations(self):
        """Test user generation with organizations included."""
        data = GitHubDataBuilder().with_users(6, include_organizations=True).build()

        assert len(data["users"]) == 6

        # Every 3rd user should be an organization
        user_types = [user["type"] for user in data["users"]]
        org_count = user_types.count("Organization")
        user_count = user_types.count("User")

        assert org_count == 2  # Indices 0, 3
        assert user_count == 4  # Indices 1, 2, 4, 5

        # Check organization-specific fields
        for user in data["users"]:
            if user["type"] == "Organization":
                assert user["login"].startswith("org")
                assert "description" in user
                assert "organization_billing_email" in user
                assert user["email"] is None
            else:
                assert user["login"].startswith("user")
                assert user["email"] is not None

    def test_with_users_custom_users(self):
        """Test user generation with custom user data."""
        custom_users = [
            {"login": "testuser1", "name": "Test User 1"},
            {"login": "testorg1", "type": "Organization"},
        ]

        data = GitHubDataBuilder().with_users(custom_users=custom_users).build()

        assert len(data["users"]) == 2

        user1 = data["users"][0]
        assert user1["login"] == "testuser1"
        assert user1["name"] == "Test User 1"
        assert user1["type"] == "User"  # Default type
        assert "id" in user1  # Auto-generated

        org1 = data["users"][1]
        assert org1["login"] == "testorg1"
        assert org1["type"] == "Organization"

    def test_with_users_comprehensive_fields(self):
        """Test that all expected user fields are generated."""
        data = GitHubDataBuilder().with_users(1, include_organizations=True).build()

        user = data["users"][0]  # This will be an org (index 0)

        required_fields = [
            "login",
            "id",
            "avatar_url",
            "html_url",
            "type",
            "site_admin",
            "name",
            "bio",
            "location",
            "blog",
            "public_repos",
            "public_gists",
            "followers",
            "following",
            "created_at",
            "updated_at",
        ]

        for field in required_fields:
            assert field in user, f"Missing field: {field}"


class TestRepositoryMetadataSupport:
    """Test repository metadata generation functionality."""

    def test_with_repositories_default(self):
        """Test basic repository generation with default settings."""
        data = GitHubDataBuilder().with_repositories(2).build()

        assert len(data["repositories"]) == 2

        for repo in data["repositories"]:
            assert "id" in repo
            assert "name" in repo
            assert "full_name" in repo
            assert "owner" in repo
            assert repo["private"] is False  # Default
            assert repo["archived"] is False  # Default
            assert "html_url" in repo
            assert "clone_url" in repo
            assert repo["name"].startswith("test-repo-")
            assert "description" in repo

    def test_with_repositories_with_users(self):
        """Test repository generation with existing users."""
        data = GitHubDataBuilder().with_users(3).with_repositories(2).build()

        assert len(data["users"]) == 3
        assert len(data["repositories"]) == 2

        # Repository owners should be selected from existing users
        user_ids = {user["id"] for user in data["users"]}
        for repo in data["repositories"]:
            assert repo["owner"]["id"] in user_ids

    def test_with_repositories_include_private_archived(self):
        """Test repository generation with private and archived options."""
        data = (
            GitHubDataBuilder()
            .with_repositories(4, include_private=True, include_archived=True)
            .build()
        )

        repos = data["repositories"]
        assert len(repos) == 4

        # Check private/archived distribution
        private_count = sum(1 for repo in repos if repo["private"])
        archived_count = sum(1 for repo in repos if repo["archived"])

        assert private_count == 2  # Every 2nd repo (indices 0, 2)
        assert archived_count == 2  # Every 3rd repo (indices 0, 3)

    def test_with_repositories_custom_repositories(self):
        """Test repository generation with custom repository data."""
        custom_repos = [
            {"name": "custom-repo", "description": "Custom test repository"},
            {"name": "another-repo", "private": True},
        ]

        data = (
            GitHubDataBuilder()
            .with_repositories(custom_repositories=custom_repos)
            .build()
        )

        assert len(data["repositories"]) == 2

        repo1 = data["repositories"][0]
        assert repo1["name"] == "custom-repo"
        assert repo1["description"] == "Custom test repository"
        assert "id" in repo1  # Auto-generated

        repo2 = data["repositories"][1]
        assert repo2["name"] == "another-repo"
        assert repo2["private"] is True

    def test_with_repositories_comprehensive_fields(self):
        """Test that all expected repository fields are generated."""
        data = GitHubDataBuilder().with_repositories(1).build()

        repo = data["repositories"][0]

        required_fields = [
            "id",
            "name",
            "full_name",
            "owner",
            "private",
            "archived",
            "disabled",
            "html_url",
            "clone_url",
            "ssh_url",
            "git_url",
            "description",
            "fork",
            "homepage",
            "language",
            "forks_count",
            "stargazers_count",
            "watchers_count",
            "size",
            "default_branch",
            "open_issues_count",
            "is_template",
            "topics",
            "has_issues",
            "has_projects",
            "has_wiki",
            "has_pages",
            "visibility",
            "permissions",
            "security_and_analysis",
            "created_at",
            "updated_at",
            "pushed_at",
        ]

        for field in required_fields:
            assert field in repo, f"Missing field: {field}"


class TestEnhancedValidation:
    """Test enhanced validation system with new entities."""

    def test_validate_user_references(self):
        """Test validation of user references across entities."""
        builder = GitHubDataBuilder()
        builder.with_users(2)
        builder.with_issues(1)

        # Manually break user reference for testing
        data = builder.build()
        data["issues"][0]["user"]["id"] = 99999  # Non-existent user ID
        builder.data = data

        errors = builder.validate_relationships()
        assert len(errors) >= 1
        assert any("references non-existent user ID" in error for error in errors)

    def test_validate_repository_owner_references(self):
        """Test validation of repository owner references."""
        builder = GitHubDataBuilder()
        builder.with_users(2)
        builder.with_repositories(1)

        # Get the data and check that validation works first
        data = builder.build()
        builder.data = data
        errors = builder.validate_relationships()
        assert len(errors) == 0  # Should be valid initially

        # Manually break repository owner reference for testing
        data["repositories"][0]["owner"]["id"] = 99999  # Non-existent user ID
        builder.data = data

        errors = builder.validate_relationships()
        assert len(errors) >= 1
        assert any("references non-existent owner user ID" in error for error in errors)

    def test_validate_all_relationships_with_new_entities(self):
        """Test comprehensive relationship validation with all entities."""
        data = (
            GitHubDataBuilder()
            .with_users(5, include_organizations=True)
            .with_repositories(2, include_private=True)
            .with_labels(2)
            .with_milestones(2, include_closed=True)
            .with_issues(3, include_closed=True)
            .with_milestone_relationships()
            .with_sub_issues(sub_issues_per_parent=1)
            .with_comments(2, 1)
            .with_pull_requests(2)
            .with_pr_reviews(2, 1)
            .with_pr_review_comments(1, 1)
            .build()
        )

        builder = GitHubDataBuilder()
        builder.data = data
        errors = builder.validate_relationships()

        # Should have no validation errors with properly built data
        assert len(errors) == 0, f"Validation errors: {errors}"


class TestAdvancedRelationshipScenarios:
    """Test advanced relationship scenario builders."""

    def test_build_complete_ecosystem(self):
        """Test complete ecosystem builder with all entities."""
        data = GitHubDataBuilder().build_complete_ecosystem()

        # Verify all entity types are present
        assert len(data["users"]) == 10
        assert len(data["repositories"]) == 3
        assert len(data["labels"]) == 5
        assert len(data["milestones"]) == 4
        assert len(data["issues"]) >= 8  # Base issues + sub-issues
        assert len(data["comments"]) >= 10  # 5 issues * 2 comments
        assert len(data["pull_requests"]) == 4
        assert len(data["pr_reviews"]) >= 8  # 4 PRs * 2 reviews

        # Verify organizations are included
        user_types = [user["type"] for user in data["users"]]
        assert "Organization" in user_types

        # Verify repository variations
        repo_states = [
            (repo["private"], repo["archived"]) for repo in data["repositories"]
        ]
        assert (True, False) in repo_states  # Private repo
        assert (False, True) in repo_states or (
            True,
            True,
        ) in repo_states  # Archived repo

    def test_build_user_focused_workflow(self):
        """Test user-focused workflow builder."""
        data = GitHubDataBuilder().build_user_focused_workflow()

        assert len(data["users"]) == 6
        assert len(data["repositories"]) == 4
        assert len(data["issues"]) == 4
        assert len(data["pull_requests"]) == 2

        # Verify user-repository ownership relationships
        user_ids = {user["id"] for user in data["users"]}
        for repo in data["repositories"]:
            assert repo["owner"]["id"] in user_ids

    def test_build_repository_management_scenario(self):
        """Test repository management scenario builder."""
        data = GitHubDataBuilder().build_repository_management_scenario()

        assert len(data["repositories"]) == 5
        assert len(data["users"]) == 5

        # Verify repository configuration variations
        private_count = sum(1 for repo in data["repositories"] if repo["private"])
        archived_count = sum(1 for repo in data["repositories"] if repo["archived"])

        assert private_count >= 1  # At least some private repos
        assert archived_count >= 1  # At least some archived repos

    def test_build_cross_entity_relationships(self):
        """Test cross-entity relationship builder."""
        data = GitHubDataBuilder().build_cross_entity_relationships()

        # Verify comprehensive entity coverage
        assert len(data["users"]) == 8
        assert len(data["repositories"]) == 3
        assert len(data["milestones"]) == 3
        assert len(data["issues"]) >= 6  # Base + hierarchical sub-issues
        assert len(data["pull_requests"]) == 3
        assert len(data["pr_reviews"]) >= 9  # 3 PRs * 3 reviews

        # Verify complex hierarchy exists
        assert len(data["sub_issues"]) > 0

        # Validate all relationships are intact
        builder = GitHubDataBuilder()
        builder.data = data
        errors = builder.validate_relationships()
        assert len(errors) == 0, f"Relationship validation errors: {errors}"


class TestIntegrationWithPreviousWeeks:
    """Test integration with Week 1 and Week 2 features."""

    def test_enhanced_complex_builder(self):
        """Test the enhanced complex builder includes all entities."""
        data = GitHubDataBuilder().build_complex()

        # Verify all entity types from all weeks are present
        assert len(data["users"]) == 8  # NEW: Week 3
        assert len(data["repositories"]) == 2  # NEW: Week 3
        assert len(data["labels"]) == 3
        assert len(data["issues"]) >= 5  # Base + sub-issues
        assert len(data["comments"]) >= 6  # Issues + unicode
        assert len(data["pull_requests"]) == 3
        assert len(data["pr_comments"]) >= 4  # 2 PRs * 2 comments
        assert len(data["milestones"]) == 3  # Week 1
        assert len(data["sub_issues"]) >= 4  # Week 1
        assert len(data["pr_reviews"]) >= 6  # Week 2
        assert len(data["pr_review_comments"]) >= 4  # Week 2

        # Verify organizations are included
        user_types = [user["type"] for user in data["users"]]
        assert "Organization" in user_types

    def test_week3_features_with_existing_workflows(self):
        """Test Week 3 features work with existing workflow patterns."""
        # Test milestone workflow with users and repositories
        data = (
            GitHubDataBuilder()
            .with_users(4, include_organizations=True)
            .with_repositories(2)
            .with_labels(2)
            .with_milestones(2, include_closed=False, with_due_dates=True)
            .with_issues(4, include_closed=False)
            .with_milestone_relationships()
            .with_sub_issues(parent_issue_numbers=[1, 3], sub_issues_per_parent=2)
            .with_comments(2, 1)
            .build()
        )

        assert len(data["users"]) == 4
        assert len(data["repositories"]) == 2
        assert len(data["milestones"]) == 2
        assert len(data["issues"]) >= 4

        # Validate relationships
        builder = GitHubDataBuilder()
        builder.data = data
        errors = builder.validate_relationships()
        assert len(errors) == 0

    def test_all_builders_with_validation(self):
        """Test that all builders produce valid relationship data."""
        builders = [
            "build_minimal",
            "build_complex",
            "build_milestone_workflow",
            "build_hierarchical_issues",
            "build_pr_review_workflow",
            "build_multi_reviewer_workflow",
            "build_review_comment_thread",
            "build_complete_ecosystem",
            "build_user_focused_workflow",
            "build_repository_management_scenario",
            "build_cross_entity_relationships",
        ]

        for builder_name in builders:
            builder_instance = GitHubDataBuilder()
            builder_method = getattr(builder_instance, builder_name)
            data = builder_method()

            # Validate relationships for this builder
            builder_instance.data = data
            errors = builder_instance.validate_relationships()
            assert (
                len(errors) == 0
            ), f"Builder {builder_name} has validation errors: {errors}"


class TestPerformanceAndScaling:
    """Test performance characteristics of Week 3 features."""

    def test_large_user_dataset_performance(self):
        """Test performance with large user datasets."""
        import time

        start_time = time.time()
        data = GitHubDataBuilder().with_users(50, include_organizations=True).build()
        end_time = time.time()

        assert len(data["users"]) == 50
        assert (end_time - start_time) < 0.1  # Should complete in under 100ms

    def test_large_repository_dataset_performance(self):
        """Test performance with large repository datasets."""
        import time

        start_time = time.time()
        data = (
            GitHubDataBuilder()
            .with_users(20)
            .with_repositories(25, include_private=True, include_archived=True)
            .build()
        )
        end_time = time.time()

        assert len(data["repositories"]) == 25
        assert (end_time - start_time) < 0.1  # Should complete in under 100ms

    def test_complete_ecosystem_performance(self):
        """Test performance of complete ecosystem builder."""
        import time

        start_time = time.time()
        data = GitHubDataBuilder().build_complete_ecosystem()
        end_time = time.time()

        # Verify comprehensive data
        total_entities = sum(len(entities) for entities in data.values())
        assert total_entities > 50  # Should have substantial data
        assert (end_time - start_time) < 0.15  # Should complete in under 150ms


if __name__ == "__main__":
    pytest.main([__file__])
