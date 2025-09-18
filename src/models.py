"""
Data models for GitHub entities.

DEPRECATED: This module re-exports models from the entities package.
New code should import directly from src.entities or specific entity packages.

These Pydantic models provide type-safe representations of GitHub data
that will be serialized to/from JSON files.
"""

import warnings

# Re-export all models for backward compatibility
from .entities import (
    GitHubUser,
    Label,
    Comment,
    Issue,
    SubIssue,
    PullRequest,
    PullRequestComment,
    RepositoryData,
)

# Issue deprecation warning for direct imports
warnings.warn(
    "Importing from src.models is deprecated. "
    "Use 'from src.entities import ModelName' instead.",
    DeprecationWarning,
    stacklevel=2,
)

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
