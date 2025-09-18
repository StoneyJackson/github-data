"""Entity models package.

This package provides entity-specific model modules while maintaining
backward compatibility with the original models.py structure.
"""

# Import all models to maintain backward compatibility
from .users import GitHubUser
from .labels import Label
from .comments import Comment
from .issues import Issue, SubIssue
from .pull_requests import PullRequest, PullRequestComment
from .repository import RepositoryData

__all__ = [
    "GitHubUser",
    "Label",
    "Comment",
    "Issue",
    "SubIssue",
    "PullRequest",
    "PullRequestComment",
    "RepositoryData",
]
