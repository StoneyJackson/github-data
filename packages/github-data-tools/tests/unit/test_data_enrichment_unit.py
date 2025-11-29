"""
Test Data Enrichment Utilities

Tests for comment enrichment, sub-issue relationship building,
and URL construction utilities.
"""

import pytest
from github_data_tools.github.utils.data_enrichment import (
    CommentEnricher,
    SubIssueRelationshipBuilder,
    URLEnricher,
)

pytestmark = [
    pytest.mark.unit,
    pytest.mark.fast,
]


class TestCommentEnricher:
    """Test comment enrichment functionality."""

    def test_enrich_issue_comments_basic(self):
        """Test basic issue comment enrichment."""
        comments = [
            {"id": 1, "body": "First comment"},
            {"id": 2, "body": "Second comment"},
        ]
        issue_url = "https://github.com/owner/repo/issues/123"

        result = CommentEnricher.enrich_issue_comments(comments, issue_url)

        assert len(result) == 2
        assert result[0]["issue_url"] == issue_url
        assert result[1]["issue_url"] == issue_url
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2

    def test_enrich_issue_comments_empty_list(self):
        """Test enrichment with empty comment list."""
        comments = []
        issue_url = "https://github.com/owner/repo/issues/123"

        result = CommentEnricher.enrich_issue_comments(comments, issue_url)

        assert result == []

    def test_enrich_pr_comments_basic(self):
        """Test basic pull request comment enrichment."""
        comments = [
            {"id": 1, "body": "PR comment 1"},
            {"id": 2, "body": "PR comment 2"},
        ]
        pr_url = "https://github.com/owner/repo/pull/456"

        result = CommentEnricher.enrich_pr_comments(comments, pr_url)

        assert len(result) == 2
        assert result[0]["pull_request_url"] == pr_url
        assert result[1]["pull_request_url"] == pr_url
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2

    def test_enrich_pr_comments_empty_list(self):
        """Test PR comment enrichment with empty list."""
        comments = []
        pr_url = "https://github.com/owner/repo/pull/456"

        result = CommentEnricher.enrich_pr_comments(comments, pr_url)

        assert result == []

    def test_enrich_comments_preserves_existing_data(self):
        """Test that enrichment preserves existing comment data."""
        comments = [
            {
                "id": 1,
                "body": "Test comment",
                "created_at": "2023-01-01T00:00:00Z",
                "user": {"login": "testuser"},
            }
        ]
        issue_url = "https://github.com/owner/repo/issues/123"

        result = CommentEnricher.enrich_issue_comments(comments, issue_url)

        comment = result[0]
        assert comment["id"] == 1
        assert comment["body"] == "Test comment"
        assert comment["created_at"] == "2023-01-01T00:00:00Z"
        assert comment["user"]["login"] == "testuser"
        assert comment["issue_url"] == issue_url


class TestSubIssueRelationshipBuilder:
    """Test sub-issue relationship building functionality."""

    def test_build_repository_relationships_basic(self):
        """Test basic repository sub-issue relationship building."""
        issues_nodes = [
            {
                "id": "issue_1",
                "number": 1,
                "subIssues": {
                    "nodes": [
                        {"id": "sub_1", "number": 2, "position": 1},
                        {"id": "sub_2", "number": 3, "position": 2},
                    ]
                },
            },
            {
                "id": "issue_2",
                "number": 4,
                "subIssues": {
                    "nodes": [
                        {"id": "sub_3", "number": 5, "position": 1},
                    ]
                },
            },
        ]

        result = SubIssueRelationshipBuilder.build_repository_relationships(
            issues_nodes
        )

        assert len(result) == 3

        # Check first relationship
        assert result[0]["sub_issue_id"] == "sub_1"
        assert result[0]["sub_issue_number"] == 2
        assert result[0]["parent_issue_id"] == "issue_1"
        assert result[0]["parent_issue_number"] == 1
        assert result[0]["position"] == 1

        # Check second relationship
        assert result[1]["sub_issue_id"] == "sub_2"
        assert result[1]["sub_issue_number"] == 3
        assert result[1]["parent_issue_id"] == "issue_1"
        assert result[1]["parent_issue_number"] == 1
        assert result[1]["position"] == 2

        # Check third relationship
        assert result[2]["sub_issue_id"] == "sub_3"
        assert result[2]["sub_issue_number"] == 5
        assert result[2]["parent_issue_id"] == "issue_2"
        assert result[2]["parent_issue_number"] == 4
        assert result[2]["position"] == 1

    def test_build_repository_relationships_empty_sub_issues(self):
        """Test repository relationships with no sub-issues."""
        issues_nodes = [
            {
                "id": "issue_1",
                "number": 1,
                "subIssues": {"nodes": []},
            }
        ]

        result = SubIssueRelationshipBuilder.build_repository_relationships(
            issues_nodes
        )

        assert result == []

    def test_build_repository_relationships_missing_sub_issues_key(self):
        """Test repository relationships when subIssues key is missing."""
        issues_nodes = [
            {
                "id": "issue_1",
                "number": 1,
            }
        ]

        result = SubIssueRelationshipBuilder.build_repository_relationships(
            issues_nodes
        )

        assert result == []

    def test_build_issue_relationships_with_metadata(self):
        """Test building issue relationships with metadata."""
        sub_issues_nodes = [
            {
                "id": "sub_1",
                "number": 2,
                "position": 1,
                "title": "Sub-issue 1",
                "state": "open",
                "url": "https://github.com/owner/repo/issues/2",
            },
            {
                "id": "sub_2",
                "number": 3,
                "position": 2,
                "title": "Sub-issue 2",
                "state": "closed",
                "url": "https://github.com/owner/repo/issues/3",
            },
        ]
        parent_issue = {
            "id": "issue_1",
            "number": 1,
        }

        result = SubIssueRelationshipBuilder.build_issue_relationships(
            sub_issues_nodes, parent_issue
        )

        assert len(result) == 2

        # Check first relationship with metadata
        rel1 = result[0]
        assert rel1["sub_issue_id"] == "sub_1"
        assert rel1["sub_issue_number"] == 2
        assert rel1["parent_issue_id"] == "issue_1"
        assert rel1["parent_issue_number"] == 1
        assert rel1["position"] == 1
        assert rel1["title"] == "Sub-issue 1"
        assert rel1["state"] == "open"
        assert rel1["url"] == "https://github.com/owner/repo/issues/2"

        # Check second relationship with metadata
        rel2 = result[1]
        assert rel2["sub_issue_id"] == "sub_2"
        assert rel2["sub_issue_number"] == 3
        assert rel2["parent_issue_id"] == "issue_1"
        assert rel2["parent_issue_number"] == 1
        assert rel2["position"] == 2
        assert rel2["title"] == "Sub-issue 2"
        assert rel2["state"] == "closed"
        assert rel2["url"] == "https://github.com/owner/repo/issues/3"

    def test_create_relationship_object_without_metadata(self):
        """Test creating relationship object without metadata."""
        sub_issue = {
            "id": "sub_1",
            "number": 2,
            "position": 1,
            "title": "Sub-issue 1",
            "state": "open",
            "url": "https://github.com/owner/repo/issues/2",
        }
        parent_issue = {
            "id": "issue_1",
            "number": 1,
        }

        result = SubIssueRelationshipBuilder.create_relationship_object(
            sub_issue, parent_issue, 1, include_metadata=False
        )

        expected_keys = {
            "sub_issue_id",
            "sub_issue_number",
            "parent_issue_id",
            "parent_issue_number",
            "position",
        }
        assert set(result.keys()) == expected_keys
        assert result["sub_issue_id"] == "sub_1"
        assert result["sub_issue_number"] == 2
        assert result["parent_issue_id"] == "issue_1"
        assert result["parent_issue_number"] == 1
        assert result["position"] == 1

    def test_create_relationship_object_with_metadata(self):
        """Test creating relationship object with metadata."""
        sub_issue = {
            "id": "sub_1",
            "number": 2,
            "position": 1,
            "title": "Sub-issue 1",
            "state": "open",
            "url": "https://github.com/owner/repo/issues/2",
        }
        parent_issue = {
            "id": "issue_1",
            "number": 1,
        }

        result = SubIssueRelationshipBuilder.create_relationship_object(
            sub_issue, parent_issue, 1, include_metadata=True
        )

        expected_keys = {
            "sub_issue_id",
            "sub_issue_number",
            "parent_issue_id",
            "parent_issue_number",
            "position",
            "title",
            "state",
            "url",
        }
        assert set(result.keys()) == expected_keys
        assert result["sub_issue_id"] == "sub_1"
        assert result["sub_issue_number"] == 2
        assert result["parent_issue_id"] == "issue_1"
        assert result["parent_issue_number"] == 1
        assert result["position"] == 1
        assert result["title"] == "Sub-issue 1"
        assert result["state"] == "open"
        assert result["url"] == "https://github.com/owner/repo/issues/2"

    def test_create_relationship_object_missing_position(self):
        """Test creating relationship object when position is missing."""
        sub_issue = {
            "id": "sub_1",
            "number": 2,
        }
        parent_issue = {
            "id": "issue_1",
            "number": 1,
        }

        result = SubIssueRelationshipBuilder.create_relationship_object(
            sub_issue, parent_issue, 1, include_metadata=False
        )

        assert result["position"] == 1


class TestURLEnricher:
    """Test URL construction functionality."""

    def test_build_api_url_basic(self):
        """Test basic API URL construction."""
        repo_name = "owner/repo"
        resource_type = "labels"
        resource_id = "bug"

        result = URLEnricher.build_api_url(repo_name, resource_type, resource_id)

        expected = "https://api.github.com/repos/owner/repo/labels/bug"
        assert result == expected

    def test_build_api_url_different_resources(self):
        """Test API URL construction for different resource types."""
        repo_name = "owner/repo"

        # Test labels
        labels_url = URLEnricher.build_api_url(repo_name, "labels", "enhancement")
        expected = "https://api.github.com/repos/owner/repo/labels/enhancement"
        assert labels_url == expected

        # Test issues
        issues_url = URLEnricher.build_api_url(repo_name, "issues", "123")
        expected = "https://api.github.com/repos/owner/repo/issues/123"
        assert issues_url == expected

        # Test pulls
        pulls_url = URLEnricher.build_api_url(repo_name, "pulls", "456")
        expected = "https://api.github.com/repos/owner/repo/pulls/456"
        assert pulls_url == expected

    def test_build_github_url_basic(self):
        """Test basic GitHub web URL construction."""
        repo_name = "owner/repo"
        resource_type = "issues"
        resource_id = "123"

        result = URLEnricher.build_github_url(repo_name, resource_type, resource_id)

        expected = "https://github.com/owner/repo/issues/123"
        assert result == expected

    def test_build_github_url_different_resources(self):
        """Test GitHub URL construction for different resource types."""
        repo_name = "owner/repo"

        # Test issues
        issues_url = URLEnricher.build_github_url(repo_name, "issues", "123")
        assert issues_url == "https://github.com/owner/repo/issues/123"

        # Test pull requests
        pull_url = URLEnricher.build_github_url(repo_name, "pull", "456")
        assert pull_url == "https://github.com/owner/repo/pull/456"

        # Test commit
        commit_url = URLEnricher.build_github_url(repo_name, "commit", "abc123")
        assert commit_url == "https://github.com/owner/repo/commit/abc123"

    def test_build_api_url_with_special_characters(self):
        """Test API URL construction with special characters in resource ID."""
        repo_name = "owner/repo"
        resource_type = "labels"
        resource_id = "needs%20review"

        result = URLEnricher.build_api_url(repo_name, resource_type, resource_id)

        expected = "https://api.github.com/repos/owner/repo/labels/needs%20review"
        assert result == expected

    def test_build_github_url_with_numeric_ids(self):
        """Test GitHub URL construction with numeric resource IDs."""
        repo_name = "owner/repo"
        resource_type = "issues"
        resource_id = "12345"

        result = URLEnricher.build_github_url(repo_name, resource_type, resource_id)

        expected = "https://github.com/owner/repo/issues/12345"
        assert result == expected


class TestDataEnrichmentIntegration:
    """Integration tests for data enrichment utilities."""

    def test_comment_enrichment_preserves_modifications(self):
        """Test that comment enrichment doesn't interfere with existing mods."""
        comments = [
            {"id": 1, "body": "Original comment"},
            {"id": 2, "body": "Another comment"},
        ]

        # First enrichment
        issue_url = "https://github.com/owner/repo/issues/1"
        result1 = CommentEnricher.enrich_issue_comments(comments, issue_url)

        # Second enrichment (different URL)
        pr_url = "https://github.com/owner/repo/pull/2"
        result2 = CommentEnricher.enrich_pr_comments(result1, pr_url)

        # Check both URLs are present
        assert result2[0]["issue_url"] == issue_url
        assert result2[0]["pull_request_url"] == pr_url
        assert result2[1]["issue_url"] == issue_url
        assert result2[1]["pull_request_url"] == pr_url

    def test_url_enricher_consistency(self):
        """Test that URL enricher produces consistent URLs."""
        repo_name = "owner/repo"

        # API URLs
        api_url_1 = URLEnricher.build_api_url(repo_name, "issues", "1")
        api_url_2 = URLEnricher.build_api_url(repo_name, "issues", "2")

        # GitHub URLs
        github_url_1 = URLEnricher.build_github_url(repo_name, "issues", "1")
        github_url_2 = URLEnricher.build_github_url(repo_name, "issues", "2")

        # Check patterns are consistent
        assert api_url_1.replace("/1", "/2") == api_url_2
        assert github_url_1.replace("/1", "/2") == github_url_2
        assert "api.github.com" in api_url_1
        assert "github.com" in github_url_1
        assert "api.github.com" not in github_url_1


class TestDataEnrichmentWorkflowIntegration:
    """Integration tests for data enrichment with workflow services."""

    @pytest.mark.integration
    @pytest.mark.save_workflow
    def test_comment_enrichment_in_save_workflow(
        self, save_workflow_services, parametrized_data_factory
    ):
        """Test comment enrichment within complete save workflow."""
        services = save_workflow_services
        github_service = services["github"]

        # Create test data with comments and issues
        test_data = parametrized_data_factory("basic")

        # Configure boundary to return test data with comments
        boundary = github_service._boundary
        boundary.get_repository_issues.return_value = test_data["issues"]
        boundary.get_all_issue_comments.return_value = test_data["comments"]

        # Test comment enrichment during backup process
        issues = boundary.get_repository_issues("owner/repo")
        comments = boundary.get_all_issue_comments("owner/repo")

        # Enrich comments with issue URLs
        enriched_comments = []
        for comment in comments:
            # Find matching issue for this comment
            matching_issue = next(
                (
                    issue
                    for issue in issues
                    if issue["number"] == comment["issue_number"]
                ),
                None,
            )
            if matching_issue:
                issue_url = matching_issue["html_url"]
                enriched = CommentEnricher.enrich_issue_comments([comment], issue_url)
                enriched_comments.extend(enriched)

        # Verify enrichment preserved original data and added URLs
        assert len(enriched_comments) == len(test_data["comments"])
        for enriched_comment in enriched_comments:
            assert "issue_url" in enriched_comment
            assert "id" in enriched_comment
            assert "body" in enriched_comment
            assert enriched_comment["issue_url"].startswith("https://github.com/")

    @pytest.mark.integration
    @pytest.mark.restore_workflow
    def test_sub_issue_relationships_in_restore_workflow(
        self, restore_workflow_services, github_data_builder
    ):
        """Test sub-issue relationship building during restore workflow."""
        services = restore_workflow_services
        github_service = services["github"]

        # Create test data with sub-issue hierarchies
        test_data = (
            github_data_builder.with_issues(8).with_sub_issue_hierarchy(3, 2).build()
        )

        # Configure boundary for restore operations
        boundary = github_service._boundary
        boundary.get_repository_labels.return_value = []
        boundary.get_repository_issues.return_value = []
        boundary.create_issue.return_value = {
            "id": 1,
            "number": 1,
            "title": "Created Issue",
            "html_url": "https://github.com/owner/repo/issues/1",
        }

        # Test sub-issue relationship building
        issues_nodes = []
        for issue in test_data["issues"]:
            # Convert sub-issues data to the format expected by
            # SubIssueRelationshipBuilder
            sub_issues_for_issue = [
                sub
                for sub in test_data["sub_issues"]
                if sub["parent_issue_id"] == issue["id"]
            ]

            sub_issues_nodes = []
            for sub_rel in sub_issues_for_issue:
                # Find the sub-issue data
                sub_issue = next(
                    (
                        iss
                        for iss in test_data["issues"]
                        if iss["id"] == sub_rel["sub_issue_id"]
                    ),
                    None,
                )
                if sub_issue:
                    sub_issues_nodes.append(
                        {
                            "id": sub_issue["id"],
                            "number": sub_issue["number"],
                            "position": sub_rel["position"],
                            "title": sub_issue["title"],
                            "state": sub_issue["state"],
                            "url": sub_issue["html_url"],
                        }
                    )

            issues_nodes.append(
                {
                    "id": issue["id"],
                    "number": issue["number"],
                    "subIssues": {"nodes": sub_issues_nodes},
                }
            )

        # Build relationships using the enrichment utility
        relationships = SubIssueRelationshipBuilder.build_repository_relationships(
            issues_nodes
        )

        # Verify relationships match expected structure
        assert len(relationships) == len(test_data["sub_issues"])
        for rel in relationships:
            assert "sub_issue_id" in rel
            assert "parent_issue_id" in rel
            assert "position" in rel
            assert "sub_issue_number" in rel
            assert "parent_issue_number" in rel

    @pytest.mark.integration
    @pytest.mark.cross_component_interaction
    def test_url_enrichment_cross_component_consistency(
        self, integration_test_environment
    ):
        """Test URL enrichment consistency across multiple data types."""
        env = integration_test_environment
        test_data = env["test_data"]

        repo_name = "owner/repo"

        # Test URL enrichment for different resource types using test data
        url_mappings = {
            "labels": ("labels", lambda item: item["name"]),
            "issues": ("issues", lambda item: str(item["number"])),
            "pull_requests": ("pulls", lambda item: str(item["number"])),
        }

        enriched_urls = {}
        for data_type, (resource_type, id_extractor) in url_mappings.items():
            if test_data[data_type]:  # Only test if we have data of this type
                sample_item = test_data[data_type][0]
                resource_id = id_extractor(sample_item)

                api_url = URLEnricher.build_api_url(
                    repo_name, resource_type, resource_id
                )
                github_url = URLEnricher.build_github_url(
                    repo_name, resource_type, resource_id
                )

                enriched_urls[data_type] = {
                    "api_url": api_url,
                    "github_url": github_url,
                    "resource_id": resource_id,
                }

        # Verify URL patterns are consistent across resource types
        for data_type, urls in enriched_urls.items():
            assert urls["api_url"].startswith("https://api.github.com/repos/")
            assert urls["github_url"].startswith("https://github.com/")
            assert repo_name in urls["api_url"]
            assert repo_name in urls["github_url"]
            assert urls["resource_id"] in urls["api_url"]
            assert urls["resource_id"] in urls["github_url"]

    @pytest.mark.integration
    @pytest.mark.performance
    def test_data_enrichment_performance_monitoring(
        self, performance_monitoring_services, github_data_builder
    ):
        """Test data enrichment utilities with performance monitoring."""
        # Create large dataset for performance testing
        test_data = github_data_builder.with_issues(100).with_comments(1).build()

        # Test comment enrichment performance
        comments = test_data["comments"]
        issue_url_base = "https://github.com/owner/repo/issues"

        import time

        start_time = time.time()

        enriched_comments = []
        for comment in comments:
            issue_url = f"{issue_url_base}/{comment['issue_number']}"
            enriched = CommentEnricher.enrich_issue_comments([comment], issue_url)
            enriched_comments.extend(enriched)

        enrichment_time = time.time() - start_time

        # Verify performance characteristics
        assert len(enriched_comments) == len(comments)
        assert enrichment_time < 1.0  # Should complete in under 1 second for 100 items

        # Test URL enrichment performance
        start_time = time.time()

        api_urls = []
        github_urls = []
        for i in range(100):
            api_url = URLEnricher.build_api_url("owner/repo", "issues", str(i + 1))
            github_url = URLEnricher.build_github_url(
                "owner/repo", "issues", str(i + 1)
            )
            api_urls.append(api_url)
            github_urls.append(github_url)

        url_generation_time = time.time() - start_time

        # Verify URL generation performance
        assert len(api_urls) == 100
        assert len(github_urls) == 100
        assert url_generation_time < 0.1  # Should be very fast for URL generation

        # Verify all URLs are unique and well-formed
        assert len(set(api_urls)) == 100  # All unique
        assert len(set(github_urls)) == 100  # All unique
        assert all(url.startswith("https://api.github.com/") for url in api_urls)
        assert all(url.startswith("https://github.com/") for url in github_urls)
