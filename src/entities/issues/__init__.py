"""Issue entity package."""

from .models import Issue
from .queries import IssueQueries

__all__ = [
    "Issue",
    "IssueQueries",
]
