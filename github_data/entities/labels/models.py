"""Label entity models."""

from typing import Union, Optional
from pydantic import BaseModel


class Label(BaseModel):
    """GitHub repository label."""

    name: str
    color: str
    description: Optional[str] = None
    url: str
    id: Union[int, str]
