"""Tests for GitHub API rate limit handling in the new service architecture."""

from unittest.mock import Mock, patch
import pytest
from github.GithubException import RateLimitExceededException, GithubException

from src.github.boundary import GitHubApiBoundary
from src.github.rate_limiter import RateLimitHandler
from src.github.service import GitHubService

pytestmark = [pytest.mark.unit, pytest.mark.fast]


class TestRateLimitHandler:
    """Test rate limit handler functionality."""

    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter instance for testing."""
        return RateLimitHandler(max_retries=2, base_delay=0.1)

    @pytest.fixture
    def mock_github_client(self):
        """Create mock GitHub client."""
        return Mock()

    def test_successful_operation_with_low_rate_limit_warning(
        self, rate_limiter, mock_github_client, caplog
    ):
        """Test successful operation logs warning when rate limit is low."""
        mock_operation = Mock(return_value="success")

        # Mock rate limit check to show low remaining
        mock_rate_limit = Mock()
        mock_rate_limit.core.remaining = 50  # Below threshold of 100
        mock_rate_limit.core.reset = None

        mock_github_client.get_rate_limit.return_value = mock_rate_limit

        result = rate_limiter.execute_with_retry(mock_operation, mock_github_client)

        assert result == "success"
        mock_operation.assert_called_once()

        # Check warning was logged
        assert "GitHub API rate limit low: 50 requests remaining" in caplog.text

    def test_rate_limit_exceeded_with_successful_retry(
        self, rate_limiter, mock_github_client, caplog
    ):
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
        mock_github_client.get_rate_limit.return_value = mock_rate_limit

        with patch("time.sleep") as mock_sleep:  # Speed up test
            result = rate_limiter.execute_with_retry(mock_operation, mock_github_client)

        assert result == "success"
        assert mock_operation.call_count == 2
        mock_sleep.assert_called_once()

        # Check retry warning was logged
        assert "GitHub API rate limit exceeded. Retrying" in caplog.text

    def test_rate_limit_exceeded_max_retries_reached(
        self, rate_limiter, mock_github_client, caplog
    ):
        """Test rate limit exceeded with max retries reached."""
        mock_operation = Mock(
            side_effect=RateLimitExceededException(
                403, {"message": "API rate limit exceeded"}
            )
        )

        with patch("time.sleep"):  # Speed up test
            with pytest.raises(RateLimitExceededException):
                rate_limiter.execute_with_retry(mock_operation, mock_github_client)

        # Should try 3 times total (initial + 2 retries)
        assert mock_operation.call_count == 3

        # Check error was logged
        assert "Max retries (2) reached" in caplog.text

    def test_other_github_exception_not_retried(
        self, rate_limiter, mock_github_client, caplog
    ):
        """Test that other GitHub exceptions are not retried."""
        mock_operation = Mock(
            side_effect=GithubException(404, {"message": "Not Found"})
        )

        with pytest.raises(GithubException):
            rate_limiter.execute_with_retry(mock_operation, mock_github_client)

        # Should only try once
        mock_operation.assert_called_once()

        # Check error was logged
        assert "GitHub API error: 404" in caplog.text

    def test_retry_delay_calculation(self, rate_limiter):
        """Test retry delay calculation with exponential backoff."""
        # Test without jitter
        rate_limiter._jitter = False

        assert rate_limiter._calculate_retry_delay(0) == 0.1  # base_delay
        assert rate_limiter._calculate_retry_delay(1) == 0.2  # base_delay * 2
        assert rate_limiter._calculate_retry_delay(2) == 0.4  # base_delay * 4

        # Test with jitter enabled
        rate_limiter._jitter = True
        delay = rate_limiter._calculate_retry_delay(1)
        assert 0.15 <= delay <= 0.25  # 0.2 ± 25%

    def test_retry_delay_max_limit(self, rate_limiter):
        """Test retry delay respects maximum limit."""
        rate_limiter._max_delay = 0.5
        rate_limiter._jitter = False

        # Large attempt number should be capped at max_delay
        assert rate_limiter._calculate_retry_delay(10) == 0.5


class TestServiceLayerRateLimiting:
    """Test rate limiting in the service layer."""

    @pytest.fixture
    def mock_boundary(self):
        """Create mock boundary."""
        boundary = Mock(spec=GitHubApiBoundary)
        boundary._github = Mock()
        return boundary

    @pytest.fixture
    def github_service(self, mock_boundary):
        """Create GitHub service with mocked boundary."""
        rate_limiter = RateLimitHandler(max_retries=2, base_delay=0.1)
        return GitHubService(mock_boundary, rate_limiter)

    def test_service_uses_rate_limiting_for_data_operations(
        self, github_service, mock_boundary
    ):
        """Test that service layer applies rate limiting to data operations."""
        mock_boundary.get_repository_labels.return_value = [{"name": "bug"}]

        # Mock rate limit status
        mock_rate_limit = Mock()
        mock_rate_limit.core.remaining = 1000
        mock_boundary._github.get_rate_limit.return_value = mock_rate_limit

        result = github_service.get_repository_labels("test/repo")

        assert result == [{"name": "bug"}]
        mock_boundary.get_repository_labels.assert_called_once_with("test/repo")

    def test_service_rate_limiting_with_retry(
        self, github_service, mock_boundary, caplog
    ):
        """Test service layer retry logic works."""
        # First call raises rate limit, second succeeds
        mock_boundary.get_repository_labels.side_effect = [
            RateLimitExceededException(403, {"message": "Rate limit exceeded"}),
            [{"name": "bug"}],
        ]

        # Mock rate limit status for successful call
        mock_rate_limit = Mock()
        mock_rate_limit.core.remaining = 1000
        mock_boundary._github.get_rate_limit.return_value = mock_rate_limit

        with patch("time.sleep"):  # Speed up test
            result = github_service.get_repository_labels("test/repo")

        assert result == [{"name": "bug"}]
        assert mock_boundary.get_repository_labels.call_count == 2
        assert "GitHub API rate limit exceeded. Retrying" in caplog.text


class TestRateLimitConfiguration:
    """Test rate limit configuration options."""

    def test_default_rate_limiter_configuration(self):
        """Test default rate limit configuration."""
        rate_limiter = RateLimitHandler()

        assert rate_limiter._max_retries == 3
        assert rate_limiter._base_delay == 1.0
        assert rate_limiter._max_delay == 60.0
        assert rate_limiter._jitter is True

    def test_custom_rate_limiter_configuration(self):
        """Test custom rate limit configuration."""
        rate_limiter = RateLimitHandler(
            max_retries=5, base_delay=2.0, max_delay=120.0, jitter=False
        )

        assert rate_limiter._max_retries == 5
        assert rate_limiter._base_delay == 2.0
        assert rate_limiter._max_delay == 120.0
        assert rate_limiter._jitter is False

    def test_boundary_no_longer_has_rate_limiting(self):
        """Test that boundary layer no longer has rate limiting built-in."""
        boundary = GitHubApiBoundary("fake-token")

        # Boundary should not have rate limiter - it's ultra-thin now
        assert not hasattr(boundary, "_rate_limiter")
        assert not hasattr(boundary, "max_retries")
        assert not hasattr(boundary, "base_delay")
