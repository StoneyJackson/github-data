"""Comment entity package."""

from .models import Comment
from .queries import CommentQueries

__all__ = [
    "Comment",
    "CommentQueries",
]
