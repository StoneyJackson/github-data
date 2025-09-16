"""
Test Data Enrichment Utilities

Tests for comment enrichment, sub-issue relationship building,
and URL construction utilities.
"""

from src.github.utils.data_enrichment import (
    CommentEnricher,
    SubIssueRelationshipBuilder,
    URLEnricher,
)


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
            sub_issue, parent_issue, include_metadata=False
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
            sub_issue, parent_issue, include_metadata=True
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
            sub_issue, parent_issue, include_metadata=False
        )

        assert result["position"] is None


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
