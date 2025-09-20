"""Pull request entity package."""

from .models import PullRequest
from .queries import PullRequestQueries

__all__ = [
    "PullRequest",
    "PullRequestQueries",
]
