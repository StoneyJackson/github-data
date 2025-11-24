"""Sub-issue entity models."""

from typing import Union
from pydantic import BaseModel


class SubIssue(BaseModel):
    """GitHub sub-issue relationship."""

    sub_issue_id: Union[int, str]
    sub_issue_number: int
    parent_issue_id: Union[int, str]
    parent_issue_number: int
    position: int
