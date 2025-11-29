"""
Rate limiting handler for GitHub API operations.

Implements exponential backoff with jitter and comprehensive monitoring.
Separated from boundary layer to maintain clean separation of concerns.
"""

import time
import random
import logging
from typing import Callable, TypeVar, Any
from github.GithubException import RateLimitExceededException, GithubException

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RateLimitHandler:
    """
    Handles rate limiting logic for GitHub API operations.

    Implements exponential backoff with jitter and comprehensive monitoring.
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        jitter: bool = True,
    ):
        """
        Initialize rate limit handler.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay for exponential backoff
            max_delay: Maximum delay between retries
            jitter: Whether to add random jitter to delays
        """
        self._max_retries = max_retries
        self._base_delay = base_delay
        self._max_delay = max_delay
        self._jitter = jitter

    def execute_with_retry(self, operation: Callable[[], T], github_client: Any) -> T:
        """
        Execute operation with rate limit retry logic.

        Args:
            operation: Function to execute with retry logic
            github_client: GitHub client for rate limit monitoring

        Returns:
            Result of the operation

        Raises:
            RateLimitExceededException: If max retries exceeded
            GithubException: For other GitHub API errors
        """
        last_exception = None

        for attempt in range(self._max_retries + 1):
            try:
                result = operation()
                self._monitor_rate_limit_status(github_client)
                return result

            except RateLimitExceededException as e:
                last_exception = e
                if self._should_retry(attempt):
                    self._handle_rate_limit_retry(attempt)
                else:
                    self._handle_max_retries_reached()
                    raise

            except GithubException as e:
                self._handle_github_api_error(e)
                raise

        # Safety fallback - should never be reached
        if last_exception:
            raise last_exception
        raise RuntimeError("Unexpected end of retry loop")

    def _should_retry(self, attempt: int) -> bool:
        """Check if we should retry the operation."""
        return attempt < self._max_retries

    def _handle_rate_limit_retry(self, attempt: int) -> None:
        """Handle rate limit retry with delay."""
        delay = self._calculate_retry_delay(attempt)
        logger.warning(
            f"GitHub API rate limit exceeded. Retrying in {delay:.1f}s "
            f"(attempt {attempt + 1}/{self._max_retries + 1})"
        )
        time.sleep(delay)

    def _handle_max_retries_reached(self) -> None:
        """Handle max retries reached scenario."""
        logger.error(
            f"GitHub API rate limit exceeded. "
            f"Max retries ({self._max_retries}) reached."
        )

    def _handle_github_api_error(self, error: GithubException) -> None:
        """Handle general GitHub API errors.

        Note: 404 errors are logged at DEBUG level as they are often expected
        (e.g., checking if a repository exists before creating it).
        """
        # Log 404 errors at DEBUG level - they're often expected behavior
        if error.status == 404:
            logger.debug(f"GitHub API 404: {error.data}")
            return

        logger.error(f"GitHub API error: {error.status} - {error.data}")

    def _monitor_rate_limit_status(self, github_client: Any) -> None:
        """Monitor rate limit status and log warnings if low."""
        try:
            rate_limit = github_client.get_rate_limit()
            core_limit = getattr(rate_limit, "core", None)

            if self._is_rate_limit_low(core_limit):
                self._log_low_rate_limit_warning(core_limit)

        except (AttributeError, GithubException, TypeError):
            # Skip rate limit monitoring if it fails (e.g., in tests)
            pass

    def _is_rate_limit_low(self, core_limit: Any) -> bool:
        """Check if rate limit is low (below threshold)."""
        if not core_limit or not hasattr(core_limit, "remaining"):
            return False

        remaining_count = getattr(core_limit, "remaining", None)
        return (
            remaining_count is not None
            and isinstance(remaining_count, int)
            and remaining_count < 100
        )

    def _log_low_rate_limit_warning(self, core_limit: Any) -> None:
        """Log warning about low rate limit."""
        remaining_count = getattr(core_limit, "remaining", 0)
        reset_time = getattr(core_limit, "reset", None)
        logger.warning(
            f"GitHub API rate limit low: {remaining_count} "
            f"requests remaining, resets at {reset_time}"
        )

    def _calculate_retry_delay(self, attempt: int) -> float:
        """
        Calculate retry delay with exponential backoff and optional jitter.

        Args:
            attempt: Current attempt number (0-based)

        Returns:
            Delay in seconds
        """
        delay = min(self._base_delay * (2**attempt), self._max_delay)

        if self._jitter:
            delay = self._add_jitter_to_delay(delay)

        return float(max(delay, 0.1))  # Ensure minimum delay

    def _add_jitter_to_delay(self, delay: float) -> float:
        """Add random jitter to delay to prevent thundering herd."""
        jitter_range = delay * 0.25  # Up to 25% jitter
        return delay + random.uniform(-jitter_range, jitter_range)
