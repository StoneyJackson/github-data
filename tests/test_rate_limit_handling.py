"""Tests for GitHub API rate limit handling."""

from unittest.mock import Mock, patch
import pytest
from github.GithubException import RateLimitExceededException, GithubException

from src.github.boundary import GitHubApiBoundary


class TestRateLimitHandling:
    """Test rate limit handling functionality."""

    @pytest.fixture
    def boundary(self):
        """Create boundary instance for testing."""
        return GitHubApiBoundary("fake-token", max_retries=2, base_delay=0.1)

    def test_successful_operation_with_low_rate_limit_warning(self, boundary, caplog):
        """Test successful operation logs warning when rate limit is low."""
        mock_operation = Mock(return_value="success")

        # Mock rate limit check to show low remaining
        mock_rate_limit = Mock()
        mock_rate_limit.core.remaining = 50  # Below threshold of 100
        mock_rate_limit.core.reset = None

        with patch.object(
            boundary._github, "get_rate_limit", return_value=mock_rate_limit
        ):
            result = boundary._rate_limiter.execute_with_retry(
                mock_operation, boundary._github
            )

        assert result == "success"
        mock_operation.assert_called_once()

        # Check warning was logged
        assert "GitHub API rate limit low: 50 requests remaining" in caplog.text

    def test_rate_limit_exceeded_with_successful_retry(self, boundary, caplog):
        """Test rate limit exceeded with successful retry."""
        mock_operation = Mock(
            side_effect=[
                RateLimitExceededException(403, {"message": "API rate limit exceeded"}),
                "success",
            ]
        )

        # Mock rate limit check for successful call
        mock_rate_limit = Mock()
        mock_rate_limit.core.remaining = 1000
        mock_rate_limit.core.reset = None

        with patch.object(
            boundary._github, "get_rate_limit", return_value=mock_rate_limit
        ):
            with patch("time.sleep") as mock_sleep:  # Speed up test
                result = boundary._rate_limiter.execute_with_retry(
                    mock_operation, boundary._github
                )

        assert result == "success"
        assert mock_operation.call_count == 2
        mock_sleep.assert_called_once()

        # Check retry warning was logged
        assert "GitHub API rate limit exceeded. Retrying" in caplog.text

    def test_rate_limit_exceeded_max_retries_reached(self, boundary, caplog):
        """Test rate limit exceeded with max retries reached."""
        mock_operation = Mock(
            side_effect=RateLimitExceededException(
                403, {"message": "API rate limit exceeded"}
            )
        )

        with patch("time.sleep"):  # Speed up test
            with pytest.raises(RateLimitExceededException):
                boundary._rate_limiter.execute_with_retry(
                    mock_operation, boundary._github
                )

        # Should try 3 times total (initial + 2 retries)
        assert mock_operation.call_count == 3

        # Check error was logged
        assert "Max retries (2) reached" in caplog.text

    def test_other_github_exception_not_retried(self, boundary, caplog):
        """Test that other GitHub exceptions are not retried."""
        mock_operation = Mock(
            side_effect=GithubException(404, {"message": "Not Found"})
        )

        with pytest.raises(GithubException):
            boundary._rate_limiter.execute_with_retry(mock_operation, boundary._github)

        # Should only try once
        mock_operation.assert_called_once()

        # Check error was logged
        assert "GitHub API error: 404" in caplog.text

    def test_retry_delay_calculation(self, boundary):
        """Test retry delay calculation with exponential backoff."""
        # Test without jitter
        boundary._rate_limiter._jitter = False

        assert boundary._rate_limiter._calculate_retry_delay(0) == 0.1  # base_delay
        assert boundary._rate_limiter._calculate_retry_delay(1) == 0.2  # base_delay * 2
        assert boundary._rate_limiter._calculate_retry_delay(2) == 0.4  # base_delay * 4

        # Test with jitter enabled
        boundary._rate_limiter._jitter = True
        delay = boundary._rate_limiter._calculate_retry_delay(1)
        assert 0.15 <= delay <= 0.25  # 0.2 ± 25%

    def test_retry_delay_max_limit(self, boundary):
        """Test retry delay respects maximum limit."""
        boundary._rate_limiter._max_delay = 0.5
        boundary._rate_limiter._jitter = False

        # Large attempt number should be capped at max_delay
        assert boundary._rate_limiter._calculate_retry_delay(10) == 0.5

    def test_get_rate_limit_status_success(self, boundary):
        """Test successful rate limit status retrieval."""
        from datetime import datetime

        # Mock rate limit response
        mock_rate_limit = Mock()
        mock_rate_limit.core.limit = 5000
        mock_rate_limit.core.remaining = 4999
        mock_rate_limit.core.reset = datetime(2025, 1, 1, 12, 0, 0)
        mock_rate_limit.search.limit = 30
        mock_rate_limit.search.remaining = 29
        mock_rate_limit.search.reset = datetime(2025, 1, 1, 12, 5, 0)

        with patch.object(
            boundary._github, "get_rate_limit", return_value=mock_rate_limit
        ):
            status = boundary.get_rate_limit_status()

        expected = {
            "core": {
                "limit": 5000,
                "remaining": 4999,
                "reset": "2025-01-01T12:00:00",
            },
            "search": {
                "limit": 30,
                "remaining": 29,
                "reset": "2025-01-01T12:05:00",
            },
        }

        assert status == expected

    def test_get_rate_limit_status_error(self, boundary, caplog):
        """Test rate limit status retrieval with error."""
        with patch.object(
            boundary._github,
            "get_rate_limit",
            side_effect=GithubException(403, {"message": "Forbidden"}),
        ):
            with pytest.raises(GithubException):
                boundary.get_rate_limit_status()

        assert "GitHub API error: 403" in caplog.text

    @patch("src.github.boundary.GitHubApiBoundary._fetch_repository_labels")
    def test_get_repository_labels_with_retry(self, mock_impl, boundary):
        """Test that public methods use retry wrapper."""
        mock_impl.return_value = [{"name": "bug"}]

        # Mock rate limit check
        mock_rate_limit = Mock()
        mock_rate_limit.core.remaining = 1000

        with patch.object(
            boundary._github, "get_rate_limit", return_value=mock_rate_limit
        ):
            result = boundary.get_repository_labels("test/repo")

        assert result == [{"name": "bug"}]
        mock_impl.assert_called_once_with("test/repo")


class TestRateLimitConfiguration:
    """Test rate limit configuration options."""

    def test_default_configuration(self):
        """Test default rate limit configuration."""
        boundary = GitHubApiBoundary("fake-token")

        assert boundary._rate_limiter._max_retries == 3
        assert boundary._rate_limiter._base_delay == 1.0
        assert boundary._rate_limiter._max_delay == 60.0
        assert boundary._rate_limiter._jitter is True

    def test_custom_configuration(self):
        """Test custom rate limit configuration."""
        boundary = GitHubApiBoundary(
            "fake-token", max_retries=5, base_delay=2.0, max_delay=120.0, jitter=False
        )

        assert boundary._rate_limiter._max_retries == 5
        assert boundary._rate_limiter._base_delay == 2.0
        assert boundary._rate_limiter._max_delay == 120.0
        assert boundary._rate_limiter._jitter is False
