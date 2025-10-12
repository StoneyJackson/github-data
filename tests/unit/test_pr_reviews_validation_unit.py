"""Unit tests for PR reviews configuration validation."""

from unittest.mock import patch
from src.config.settings import ApplicationConfig


class TestPRReviewsConfiguration:
    """Test PR reviews configuration validation."""

    @patch.dict(
        "os.environ",
        {
            "OPERATION": "save",
            "GITHUB_TOKEN": "test_token",
            "GITHUB_REPO": "owner/repo",
            "INCLUDE_PULL_REQUESTS": "true",
            "INCLUDE_PR_REVIEWS": "true",
        },
    )
    def test_pr_reviews_enabled_with_pull_requests(self):
        """Test that PR reviews can be enabled when pull requests are enabled."""
        config = ApplicationConfig.from_environment()
        config.validate()

        assert config.include_pr_reviews is True
        assert config.include_pull_requests is True

    @patch.dict(
        "os.environ",
        {
            "OPERATION": "save",
            "GITHUB_TOKEN": "test_token",
            "GITHUB_REPO": "owner/repo",
            "INCLUDE_PULL_REQUESTS": "false",
            "INCLUDE_PR_REVIEWS": "true",
        },
    )
    def test_pr_reviews_disabled_when_pull_requests_disabled(self):
        """Test that PR reviews are disabled when pull requests are disabled."""
        config = ApplicationConfig.from_environment()
        config.validate()

        # Should be disabled due to validation logic
        assert config.include_pr_reviews is False

    @patch.dict(
        "os.environ",
        {
            "OPERATION": "save",
            "GITHUB_TOKEN": "test_token",
            "GITHUB_REPO": "owner/repo",
            "INCLUDE_PULL_REQUESTS": "true",
            "INCLUDE_PR_REVIEWS": "true",
            "INCLUDE_PR_REVIEW_COMMENTS": "true",
        },
    )
    def test_pr_review_comments_enabled_with_dependencies(self):
        """Test that PR review comments can be enabled when dependencies are met."""
        config = ApplicationConfig.from_environment()
        config.validate()

        assert config.include_pr_review_comments is True
        assert config.include_pr_reviews is True
        assert config.include_pull_requests is True

    @patch.dict(
        "os.environ",
        {
            "OPERATION": "save",
            "GITHUB_TOKEN": "test_token",
            "GITHUB_REPO": "owner/repo",
            "INCLUDE_PULL_REQUESTS": "true",
            "INCLUDE_PR_REVIEWS": "false",
            "INCLUDE_PR_REVIEW_COMMENTS": "true",
        },
    )
    def test_pr_review_comments_disabled_when_pr_reviews_disabled(self):
        """Test that PR review comments are disabled when PR reviews are disabled."""
        config = ApplicationConfig.from_environment()
        config.validate()

        # Should be disabled due to validation logic
        assert config.include_pr_review_comments is False

    @patch.dict(
        "os.environ",
        {
            "OPERATION": "save",
            "GITHUB_TOKEN": "test_token",
            "GITHUB_REPO": "owner/repo",
            "INCLUDE_PULL_REQUESTS": "false",
            "INCLUDE_PR_REVIEWS": "false",
            "INCLUDE_PR_REVIEW_COMMENTS": "true",
        },
    )
    def test_pr_review_comments_disabled_when_pull_requests_disabled(self):
        """Test that PR review comments are disabled when pull requests are disabled."""
        config = ApplicationConfig.from_environment()
        config.validate()

        # Should be disabled due to validation logic
        assert config.include_pr_review_comments is False
