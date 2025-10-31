"""
GraphQL query definitions for GitHub API operations.

This module provides optimized queries for backup operations that fetch
repository data in single requests instead of multiple REST calls.

All queries are organized by functionality and re-exported here for
backward compatibility with existing imports.
"""

from .labels import REPOSITORY_LABELS_QUERY
from .issues import REPOSITORY_ISSUES_QUERY, ISSUE_COMMENTS_QUERY
from .comments import REPOSITORY_COMMENTS_QUERY
from .pull_requests import (
    REPOSITORY_PULL_REQUESTS_QUERY,
    PULL_REQUEST_COMMENTS_QUERY,
    REPOSITORY_PR_COMMENTS_QUERY,
)
from .sub_issues import REPOSITORY_SUB_ISSUES_QUERY, ISSUE_SUB_ISSUES_QUERY
from .utility import REPOSITORY_BACKUP_QUERY, RATE_LIMIT_QUERY

__all__ = [
    # Labels
    "REPOSITORY_LABELS_QUERY",
    # Issues
    "REPOSITORY_ISSUES_QUERY",
    "ISSUE_COMMENTS_QUERY",
    # Comments
    "REPOSITORY_COMMENTS_QUERY",
    # Pull Requests
    "REPOSITORY_PULL_REQUESTS_QUERY",
    "PULL_REQUEST_COMMENTS_QUERY",
    "REPOSITORY_PR_COMMENTS_QUERY",
    # Sub-Issues
    "REPOSITORY_SUB_ISSUES_QUERY",
    "ISSUE_SUB_ISSUES_QUERY",
    # Utility
    "REPOSITORY_BACKUP_QUERY",
    "RATE_LIMIT_QUERY",
]
