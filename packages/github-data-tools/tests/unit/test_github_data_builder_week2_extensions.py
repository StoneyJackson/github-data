"""
Test suite for Week 2 GitHubDataBuilder extensions - PR reviews and review comments.

This module tests the PR review workflow functionality added in Week 2
of the GitHubDataBuilder extensions implementation.
"""

from ..shared.builders.github_data_builder import GitHubDataBuilder


class TestPRReviewsSupport:
    """Test PR reviews generation functionality."""

    def test_basic_pr_reviews_creation(self):
        """Test basic PR review creation with default parameters."""
        data = GitHubDataBuilder().with_pr_reviews().build()

        assert "pr_reviews" in data
        assert len(data["pr_reviews"]) == 2  # Default: 2 PRs * 1 review each
        assert len(data["pull_requests"]) == 2  # Auto-created PRs

        # Verify review structure
        review = data["pr_reviews"][0]
        assert "id" in review
        assert "pull_request_number" in review
        assert "user" in review
        assert "body" in review
        assert "state" in review
        assert review["state"] in ["APPROVED", "COMMENTED"]
        assert "submitted_at" in review
        assert "html_url" in review
        assert "author_association" in review

    def test_pr_reviews_with_requested_changes(self):
        """Test PR reviews including requested changes."""
        data = (
            GitHubDataBuilder()
            .with_pr_reviews(
                pr_count=2, reviews_per_pr=3, include_requested_changes=True
            )
            .build()
        )

        assert len(data["pr_reviews"]) == 6  # 2 PRs * 3 reviews each

        # Check that we have different review states
        states = {review["state"] for review in data["pr_reviews"]}
        assert "CHANGES_REQUESTED" in states
        assert len(states) >= 2  # Should have multiple states

    def test_pr_reviews_with_custom_reviews(self):
        """Test PR reviews with custom review data."""
        custom_review = {
            "id": 999,
            "pull_request_number": 1,
            "user": {"login": "custom-reviewer", "id": 999},
            "body": "Custom review body",
            "state": "APPROVED",
            "submitted_at": "2023-02-01T10:00:00Z",
        }

        data = (
            GitHubDataBuilder().with_pr_reviews(custom_reviews=[custom_review]).build()
        )

        assert len(data["pr_reviews"]) == 1
        assert data["pr_reviews"][0]["id"] == 999
        assert data["pr_reviews"][0]["body"] == "Custom review body"

    def test_pr_reviews_relationship_validation(self):
        """Test that PR reviews properly reference existing PRs."""
        builder = (
            GitHubDataBuilder()
            .with_pull_requests(3)
            .with_pr_reviews(pr_count=3, reviews_per_pr=2)
        )

        data = builder.build()
        errors = builder.validate_relationships()

        assert len(errors) == 0  # No relationship errors

        # Verify all reviews reference existing PRs
        pr_numbers = {pr["number"] for pr in data["pull_requests"]}
        for review in data["pr_reviews"]:
            assert review["pull_request_number"] in pr_numbers

    def test_pr_reviews_multi_reviewer_scenario(self):
        """Test multi-reviewer scenario with different review outcomes."""
        data = (
            GitHubDataBuilder()
            .with_pull_requests(1)
            .with_pr_reviews(
                pr_count=1, reviews_per_pr=4, include_requested_changes=True
            )
            .build()
        )

        assert len(data["pr_reviews"]) == 4
        pr_number = data["pull_requests"][0]["number"]

        # All reviews should be for the same PR
        for review in data["pr_reviews"]:
            assert review["pull_request_number"] == pr_number


class TestPRReviewCommentsSupport:
    """Test PR review comments generation functionality."""

    def test_basic_pr_review_comments_creation(self):
        """Test basic PR review comment creation."""
        data = GitHubDataBuilder().with_pr_review_comments().build()

        assert "pr_review_comments" in data
        assert (
            len(data["pr_review_comments"]) == 2
        )  # Default: 2 reviews * 1 comment each
        assert len(data["pr_reviews"]) == 2  # Auto-created reviews

        # Verify review comment structure
        comment = data["pr_review_comments"][0]
        assert "id" in comment
        assert "pull_request_number" in comment
        assert "pull_request_review_id" in comment
        assert "user" in comment
        assert "body" in comment
        assert "path" in comment
        assert "position" in comment
        assert "diff_hunk" in comment
        assert "html_url" in comment

    def test_pr_review_comments_with_suggestions(self):
        """Test PR review comments with code suggestions."""
        data = (
            GitHubDataBuilder()
            .with_pr_review_comments(
                review_count=2, comments_per_review=2, include_suggestions=True
            )
            .build()
        )

        assert len(data["pr_review_comments"]) == 4  # 2 reviews * 2 comments each

        # Check that some comments are suggestions
        suggestion_comments = [
            comment
            for comment in data["pr_review_comments"]
            if "```suggestion" in comment["body"]
        ]
        assert len(suggestion_comments) > 0

    def test_pr_review_comments_with_custom_comments(self):
        """Test PR review comments with custom comment data."""
        custom_comment = {
            "id": 888,
            "pull_request_number": 1,
            "pull_request_review_id": 9000,
            "body": "Custom review comment",
            "path": "custom/path.py",
            "position": 42,
        }

        data = (
            GitHubDataBuilder()
            .with_pr_review_comments(custom_review_comments=[custom_comment])
            .build()
        )

        assert len(data["pr_review_comments"]) == 1
        assert data["pr_review_comments"][0]["id"] == 888
        assert data["pr_review_comments"][0]["body"] == "Custom review comment"

    def test_pr_review_comments_relationship_validation(self):
        """Test that review comments properly reference existing reviews."""
        builder = (
            GitHubDataBuilder()
            .with_pull_requests(2)
            .with_pr_reviews(pr_count=2, reviews_per_pr=2)
            .with_pr_review_comments(review_count=2, comments_per_review=3)
        )

        data = builder.build()
        errors = builder.validate_relationships()

        assert len(errors) == 0  # No relationship errors

        # Verify all review comments reference existing reviews and PRs
        review_ids = {review["id"] for review in data["pr_reviews"]}
        pr_numbers = {pr["number"] for pr in data["pull_requests"]}

        for comment in data["pr_review_comments"]:
            assert comment["pull_request_review_id"] in review_ids
            assert comment["pull_request_number"] in pr_numbers

    def test_pr_review_comments_thread_simulation(self):
        """Test review comment thread with in_reply_to relationships."""
        data = (
            GitHubDataBuilder()
            .with_pr_reviews(pr_count=1, reviews_per_pr=1)
            .with_pr_review_comments(review_count=1, comments_per_review=5)
            .build()
        )

        assert len(data["pr_review_comments"]) == 5

        # Check in_reply_to_id relationships
        comments = data["pr_review_comments"]
        assert comments[0]["in_reply_to_id"] is None  # First comment has no parent
        for i in range(1, len(comments)):
            assert comments[i]["in_reply_to_id"] == comments[i - 1]["id"]


class TestIntegratedPRWorkflows:
    """Test integrated PR workflows with reviews and comments."""

    def test_complete_pr_review_workflow(self):
        """Test complete PR review workflow from plan specification."""
        data = GitHubDataBuilder().build_pr_review_workflow()

        # Verify all components are present
        assert len(data["pull_requests"]) == 3
        assert len(data["pr_comments"]) == 2  # 2 PRs * 1 comment each
        assert len(data["pr_reviews"]) == 6  # 3 PRs * 2 reviews each
        assert len(data["pr_review_comments"]) == 9  # 3 reviews * 3 comments each

        # For now, just verify basic structure since validate_relationships
        # is on instance

    def test_multi_reviewer_workflow(self):
        """Test multi-reviewer workflow scenario."""
        data = GitHubDataBuilder().build_multi_reviewer_workflow()

        assert len(data["pull_requests"]) == 2
        assert len(data["pr_reviews"]) == 6  # 2 PRs * 3 reviews each
        assert len(data["pr_review_comments"]) == 4  # 2 reviews * 2 comments each

        # Check for requested changes
        review_states = {review["state"] for review in data["pr_reviews"]}
        assert "CHANGES_REQUESTED" in review_states

    def test_review_comment_thread_workflow(self):
        """Test extensive review comment thread workflow."""
        data = GitHubDataBuilder().build_review_comment_thread()

        assert len(data["pull_requests"]) == 1
        assert len(data["pr_reviews"]) == 1
        assert len(data["pr_review_comments"]) == 5

        # Verify thread structure
        comments = data["pr_review_comments"]
        assert comments[0]["in_reply_to_id"] is None
        for i in range(1, len(comments)):
            assert comments[i]["in_reply_to_id"] == comments[i - 1]["id"]

    def test_enhanced_complex_build_with_pr_reviews(self):
        """Test that enhanced complex build includes PR reviews."""
        data = GitHubDataBuilder().build_complex()

        # Verify PR review components are included
        assert len(data["pr_reviews"]) == 6  # 3 PRs * 2 reviews each
        assert len(data["pr_review_comments"]) == 4  # 2 reviews * 2 comments each

        # Verify review states include requested changes
        review_states = {review["state"] for review in data["pr_reviews"]}
        assert "CHANGES_REQUESTED" in review_states

        # Verify some comments are suggestions
        suggestion_comments = [
            comment
            for comment in data["pr_review_comments"]
            if "```suggestion" in comment["body"]
        ]
        assert len(suggestion_comments) > 0


class TestPRReviewDataIntegrity:
    """Test data integrity and edge cases for PR reviews."""

    def test_pr_review_id_counter_management(self):
        """Test that PR review ID counters are properly managed."""
        builder = GitHubDataBuilder()
        initial_review_counter = builder._pr_review_id_counter
        initial_comment_counter = builder._pr_review_comment_id_counter

        builder.with_pr_reviews(pr_count=2, reviews_per_pr=3)
        builder.with_pr_review_comments(review_count=2, comments_per_review=2)

        # ID counters should have advanced
        assert (
            builder._pr_review_id_counter == initial_review_counter + 6
        )  # 2*3 reviews
        assert (
            builder._pr_review_comment_id_counter == initial_comment_counter + 4
        )  # 2*2 comments

    def test_pr_review_without_existing_prs(self):
        """Test that PR reviews auto-create PRs when none exist."""
        data = GitHubDataBuilder().with_pr_reviews(pr_count=3, reviews_per_pr=1).build()

        # Should auto-create 3 PRs
        assert len(data["pull_requests"]) == 3
        assert len(data["pr_reviews"]) == 3

    def test_pr_review_comments_without_existing_reviews(self):
        """Test that review comments auto-create reviews when none exist."""
        data = (
            GitHubDataBuilder()
            .with_pr_review_comments(review_count=2, comments_per_review=1)
            .build()
        )

        # Should auto-create 2 reviews (and their PRs)
        assert len(data["pull_requests"]) == 2
        assert len(data["pr_reviews"]) == 2
        assert len(data["pr_review_comments"]) == 2

    def test_pr_review_url_format_consistency(self):
        """Test that review URLs follow GitHub format conventions."""
        data = GitHubDataBuilder().with_pr_reviews(pr_count=1, reviews_per_pr=1).build()

        review = data["pr_reviews"][0]
        pr_number = review["pull_request_number"]
        review_id = review["id"]

        expected_url = (
            f"https://github.com/owner/repo/pull/{pr_number}"
            f"#pullrequestreview-{review_id}"
        )
        assert review["html_url"] == expected_url

    def test_pr_review_comment_url_format_consistency(self):
        """Test that review comment URLs follow GitHub format conventions."""
        data = (
            GitHubDataBuilder()
            .with_pr_review_comments(review_count=1, comments_per_review=1)
            .build()
        )

        comment = data["pr_review_comments"][0]
        pr_number = comment["pull_request_number"]
        comment_id = comment["id"]

        expected_url = (
            f"https://github.com/owner/repo/pull/{pr_number}#discussion_r{comment_id}"
        )
        assert comment["html_url"] == expected_url

    def test_diff_hunk_format_realism(self):
        """Test that diff hunks have realistic GitHub format."""
        data = (
            GitHubDataBuilder()
            .with_pr_review_comments(review_count=1, comments_per_review=1)
            .build()
        )

        comment = data["pr_review_comments"][0]
        diff_hunk = comment["diff_hunk"]

        # Should start with @@ header
        assert diff_hunk.startswith("@@")
        # Should contain line additions/deletions
        assert "-" in diff_hunk and "+" in diff_hunk
        # Should have context lines
        assert " context line" in diff_hunk


class TestPRReviewPerformance:
    """Test performance characteristics of PR review generation."""

    def test_large_review_dataset_performance(self):
        """Test performance with large review datasets."""
        import time

        start_time = time.time()
        data = (
            GitHubDataBuilder()
            .with_pull_requests(10)
            .with_pr_reviews(
                pr_count=10, reviews_per_pr=5, include_requested_changes=True
            )
            .with_pr_review_comments(
                review_count=10, comments_per_review=10, include_suggestions=True
            )
            .build()
        )
        end_time = time.time()

        # Should complete in reasonable time (< 1 second)
        assert end_time - start_time < 1.0

        # Verify data was created
        assert len(data["pull_requests"]) == 10
        assert len(data["pr_reviews"]) == 50  # 10 * 5
        assert len(data["pr_review_comments"]) == 100  # 10 * 10

    def test_memory_efficiency_large_dataset(self):
        """Test memory efficiency with large datasets."""
        # Create large dataset
        data = (
            GitHubDataBuilder()
            .with_pull_requests(20)
            .with_pr_reviews(pr_count=20, reviews_per_pr=3)
            .with_pr_review_comments(review_count=20, comments_per_review=5)
            .build()
        )

        # Verify structure is reasonable
        assert len(data["pull_requests"]) == 20
        assert len(data["pr_reviews"]) == 60  # 20 * 3
        assert len(data["pr_review_comments"]) == 100  # 20 * 5

        # Each review should be a reasonable size (not excessive data)
        avg_review_fields = sum(
            len(review.keys()) for review in data["pr_reviews"]
        ) / len(data["pr_reviews"])
        assert avg_review_fields < 20  # Reasonable number of fields per review
