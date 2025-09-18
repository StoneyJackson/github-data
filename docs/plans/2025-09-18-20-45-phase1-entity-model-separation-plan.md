# Phase 1: Entity Model Separation Implementation Plan

## Overview

This plan details the implementation of Phase 1 from the reorganization analysis: separating entity models from the monolithic `src/models.py` into entity-specific modules while preserving all existing functionality and maintaining backward compatibility.

## Current State Analysis

### Current Structure
- **Single file**: `src/models.py` (136 lines)
- **7 model classes**: GitHubUser, Label, Comment, PullRequest, PullRequestComment, SubIssue, Issue, RepositoryData
- **32 import references** across the codebase
- **Dependencies**: Complex cross-references between models (Issue → Label, Issue → SubIssue, etc.)

### Dependency Graph
```
GitHubUser (base)
├── Label (independent)
├── Comment → GitHubUser
├── PullRequest → GitHubUser, Label
├── PullRequestComment → GitHubUser  
├── SubIssue (independent)
├── Issue → GitHubUser, Label, SubIssue
└── RepositoryData → All models
```

## Target Structure

```
src/
├── entities/
│   ├── __init__.py           # Re-export all models for backward compatibility
│   ├── base/
│   │   ├── __init__.py
│   │   └── models.py         # GitHubUser (shared base model)
│   ├── labels/
│   │   ├── __init__.py
│   │   └── models.py         # Label
│   ├── comments/
│   │   ├── __init__.py
│   │   └── models.py         # Comment
│   ├── issues/
│   │   ├── __init__.py
│   │   └── models.py         # Issue, SubIssue
│   ├── pull_requests/
│   │   ├── __init__.py
│   │   └── models.py         # PullRequest, PullRequestComment
│   └── repository/
│       ├── __init__.py
│       └── models.py         # RepositoryData
├── models.py                 # Backward compatibility re-export module
└── [existing structure unchanged]
```

## Implementation Steps

### Step 1: Create Entity Directory Structure
**Estimated Time**: 30 minutes

1. Create base directory structure:
   ```bash
   mkdir -p src/entities/{base,labels,comments,issues,pull_requests,repository}
   ```

2. Create all `__init__.py` files:
   ```bash
   touch src/entities/__init__.py
   touch src/entities/{base,labels,comments,issues,pull_requests,repository}/__init__.py
   ```

### Step 2: Extract Base Models
**Estimated Time**: 45 minutes

1. **Create `src/entities/base/models.py`**:
   ```python
   """Base models shared across entities."""
   
   from datetime import datetime
   from typing import Union
   from pydantic import BaseModel
   
   
   class GitHubUser(BaseModel):
       """GitHub user information."""
       
       login: str
       id: Union[int, str]
       avatar_url: str
       html_url: str
   ```

2. **Update `src/entities/base/__init__.py`**:
   ```python
   """Base entity models."""
   
   from .models import GitHubUser
   
   __all__ = ["GitHubUser"]
   ```

### Step 3: Extract Entity-Specific Models
**Estimated Time**: 2 hours

#### 3.1 Labels Entity
**File**: `src/entities/labels/models.py`
```python
"""Label entity models."""

from typing import Union
from pydantic import BaseModel


class Label(BaseModel):
    """GitHub repository label."""
    
    name: str
    color: str
    description: str | None = None
    url: str
    id: Union[int, str]
```

#### 3.2 Comments Entity
**File**: `src/entities/comments/models.py`
```python
"""Comment entity models."""

from datetime import datetime
from typing import Union
from pydantic import BaseModel

from ..base.models import GitHubUser


class Comment(BaseModel):
    """GitHub issue comment."""
    
    id: Union[int, str]
    body: str
    user: GitHubUser
    created_at: datetime
    updated_at: datetime
    html_url: str
    issue_url: str
    
    @property
    def issue_number(self) -> int:
        """Extract issue number from issue_url."""
        return int(self.issue_url.split("/")[-1])
```

#### 3.3 Issues Entity
**File**: `src/entities/issues/models.py`
```python
"""Issue entity models."""

from datetime import datetime
from typing import List, Union
from pydantic import BaseModel, Field, ConfigDict

from ..base.models import GitHubUser
from ..labels.models import Label


class SubIssue(BaseModel):
    """GitHub sub-issue relationship."""
    
    sub_issue_id: Union[int, str]
    sub_issue_number: int
    parent_issue_id: Union[int, str]
    parent_issue_number: int
    position: int


class Issue(BaseModel):
    """GitHub repository issue."""
    
    id: Union[int, str]
    number: int
    title: str
    body: str | None = None
    state: str
    user: GitHubUser
    assignees: List[GitHubUser] = Field(default_factory=list)
    labels: List[Label] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None
    closed_by: GitHubUser | None = None
    state_reason: str | None = None
    html_url: str
    comments_count: int = Field(alias="comments")
    sub_issues: List["SubIssue"] = Field(default_factory=list)
    
    model_config = ConfigDict(populate_by_name=True)
```

#### 3.4 Pull Requests Entity
**File**: `src/entities/pull_requests/models.py`
```python
"""Pull request entity models."""

from datetime import datetime
from typing import List, Union
from pydantic import BaseModel, Field, ConfigDict

from ..base.models import GitHubUser
from ..labels.models import Label


class PullRequest(BaseModel):
    """GitHub repository pull request."""
    
    id: Union[int, str]
    number: int
    title: str
    body: str | None = None
    state: str  # OPEN, CLOSED, MERGED
    user: GitHubUser  # author
    assignees: List[GitHubUser] = Field(default_factory=list)
    labels: List[Label] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None
    merged_at: datetime | None = None
    merge_commit_sha: str | None = None
    base_ref: str  # base branch
    head_ref: str  # head branch
    html_url: str
    comments_count: int = Field(alias="comments")
    
    model_config = ConfigDict(populate_by_name=True)


class PullRequestComment(BaseModel):
    """GitHub pull request comment."""
    
    id: Union[int, str]
    body: str
    user: GitHubUser
    created_at: datetime
    updated_at: datetime
    html_url: str
    pull_request_url: str
    
    @property
    def pull_request_number(self) -> int:
        """Extract pull request number from pull_request_url."""
        return int(self.pull_request_url.split("/")[-1])
```

#### 3.5 Repository Entity
**File**: `src/entities/repository/models.py`
```python
"""Repository entity models."""

from datetime import datetime
from typing import List
from pydantic import BaseModel, Field

from ..labels.models import Label
from ..issues.models import Issue, SubIssue
from ..comments.models import Comment
from ..pull_requests.models import PullRequest, PullRequestComment


class RepositoryData(BaseModel):
    """Complete repository data for backup/restore."""
    
    repository_name: str
    exported_at: datetime
    labels: List[Label] = Field(default_factory=list)
    issues: List[Issue] = Field(default_factory=list)
    comments: List[Comment] = Field(default_factory=list)
    pull_requests: List[PullRequest] = Field(default_factory=list)
    pr_comments: List[PullRequestComment] = Field(default_factory=list)
    sub_issues: List[SubIssue] = Field(default_factory=list)
```

### Step 4: Create Entity Package Exports
**Estimated Time**: 30 minutes

Update each entity's `__init__.py` to export its models:

#### `src/entities/labels/__init__.py`
```python
"""Label entity package."""

from .models import Label

__all__ = ["Label"]
```

#### `src/entities/comments/__init__.py`
```python
"""Comment entity package."""

from .models import Comment

__all__ = ["Comment"]
```

#### `src/entities/issues/__init__.py`
```python
"""Issue entity package."""

from .models import Issue, SubIssue

__all__ = ["Issue", "SubIssue"]
```

#### `src/entities/pull_requests/__init__.py`
```python
"""Pull request entity package."""

from .models import PullRequest, PullRequestComment

__all__ = ["PullRequest", "PullRequestComment"]
```

#### `src/entities/repository/__init__.py`
```python
"""Repository entity package."""

from .models import RepositoryData

__all__ = ["RepositoryData"]
```

### Step 5: Create Main Entity Package Export
**Estimated Time**: 15 minutes

**File**: `src/entities/__init__.py`
```python
"""Entity models package.

This package provides entity-specific model modules while maintaining
backward compatibility with the original models.py structure.
"""

# Import all models to maintain backward compatibility
from .base import GitHubUser
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
```

### Step 6: Update Original Models File for Backward Compatibility
**Estimated Time**: 15 minutes

**File**: `src/models.py`
```python
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
    stacklevel=2
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
```

## Testing Strategy

### Step 7: Validation Testing
**Estimated Time**: 1 hour

1. **Run existing test suite**:
   ```bash
   make test-fast
   ```

2. **Verify all imports work**:
   ```bash
   python -c "from src.models import Label, Issue, Comment; print('Legacy imports work')"
   python -c "from src.entities import Label, Issue, Comment; print('New imports work')"
   ```

3. **Test model instantiation**:
   ```python
   # Test script to verify models work identically
   from src.models import Issue as LegacyIssue
   from src.entities.issues import Issue as NewIssue
   
   # Should be identical
   assert LegacyIssue == NewIssue
   ```

### Step 8: Code Quality Checks
**Estimated Time**: 30 minutes

1. **Run linting**:
   ```bash
   make lint
   ```

2. **Run type checking**:
   ```bash
   make type-check
   ```

3. **Run formatting**:
   ```bash
   make format
   ```

## Risk Mitigation

### Rollback Plan
1. Keep original `src/models.py` as `src/models.py.backup`
2. If issues arise, restore original file and remove entities directory
3. All existing imports continue to work unchanged

### Compatibility Verification
1. **Import verification**: Test all existing import patterns
2. **Model equivalence**: Verify new models are functionally identical
3. **Serialization compatibility**: Ensure JSON serialization remains unchanged

## Success Criteria

1. ✅ All existing tests pass without modification
2. ✅ No changes required to existing import statements
3. ✅ New entity-based imports work correctly
4. ✅ Code quality checks pass
5. ✅ Models maintain identical behavior and serialization
6. ✅ Deprecation warning system functions correctly

## Timeline

- **Total Estimated Time**: 5-6 hours
- **Recommended Sprint**: Single development session with immediate testing
- **Dependencies**: Requires comprehensive test coverage verification first

## Future Considerations

This Phase 1 implementation sets the foundation for:
- **Phase 2**: Entity-specific use cases and queries
- **Gradual migration**: Teams can start using new imports immediately
- **Documentation updates**: Update developer guides to recommend new import patterns
- **Legacy cleanup**: Future removal of backward compatibility layer

## Implementation Checklist

- [ ] Create directory structure
- [ ] Extract GitHubUser to base models
- [ ] Create labels entity module
- [ ] Create comments entity module  
- [ ] Create issues entity module (Issue + SubIssue)
- [ ] Create pull_requests entity module (PullRequest + PullRequestComment)
- [ ] Create repository entity module (RepositoryData)
- [ ] Set up entity package exports
- [ ] Update main entities package
- [ ] Implement backward compatibility in models.py
- [ ] Run full test suite validation
- [ ] Verify import compatibility
- [ ] Run code quality checks
- [ ] Document new import patterns
- [ ] Create rollback backup