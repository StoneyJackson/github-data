"""Label entity package."""

from .models import Label
from .queries import LabelQueries

__all__ = [
    "Label",
    "LabelQueries",
]
