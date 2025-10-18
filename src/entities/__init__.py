"""Entity models package.

This package provides entity-specific model modules while maintaining
backward compatibility with the original models.py structure.
"""

# Import all models to maintain backward compatibility
from .users import GitHubUser
from .labels import Label
from .comments import Comment
from .issues import Issue
from .sub_issues import SubIssue
from .pull_requests import PullRequest
from .pr_comments import PullRequestComment
from .pr_reviews import PullRequestReview
from .pr_review_comments import PullRequestReviewComment
from .repository import RepositoryData
from .milestones import Milestone

__all__ = [
    "GitHubUser",
    "Label",
    "Comment",
    "Issue",
    "SubIssue",
    "PullRequest",
    "PullRequestComment",
    "PullRequestReview",
    "PullRequestReviewComment",
    "RepositoryData",
    "Milestone",
]
