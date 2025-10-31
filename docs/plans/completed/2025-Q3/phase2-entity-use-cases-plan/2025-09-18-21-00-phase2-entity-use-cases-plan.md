# Phase 2: Entity-Specific Use Cases Implementation Plan

## Overview

This plan details the implementation of Phase 2 from the reorganization analysis: moving from operation-based use cases to entity-specific use cases while preserving cross-entity orchestration capabilities. This builds on the completed Phase 1 entity model separation.

## Current State Analysis

### Phase 1 Completion Status
- ✅ Entity models separated into `src/entities/` structure
- ✅ Backward compatibility maintained via `src/models.py` re-exports
- ✅ Clean entity boundaries established (base, labels, comments, issues, pull_requests, repository)

### Current Use Case Structure
```
src/use_cases/
├── save/
│   ├── __init__.py
│   ├── labels/
│   │   ├── __init__.py
│   │   ├── save_labels_job.py
│   │   └── save_labels_use_case.py
│   ├── issues/
│   │   ├── __init__.py
│   │   ├── save_issues_job.py
│   │   └── save_issues_use_case.py
│   ├── comments/
│   │   ├── __init__.py
│   │   ├── save_comments_job.py
│   │   └── save_comments_use_case.py
│   ├── sub_issues/
│   │   ├── __init__.py
│   │   ├── save_sub_issues_job.py
│   │   └── save_sub_issues_use_case.py
│   └── pull_requests/
│       ├── __init__.py
│       ├── save_pull_requests_job.py
│       └── save_pull_requests_use_case.py
└── restore/
    ├── __init__.py
    ├── labels/
    │   ├── __init__.py
    │   ├── restore_labels_job.py
    │   └── restore_labels_use_case.py
    ├── issues/
    │   ├── __init__.py
    │   ├── restore_issues_job.py
    │   └── restore_issues_use_case.py
    ├── comments/
    │   ├── __init__.py
    │   ├── restore_comments_job.py
    │   └── restore_comments_use_case.py
    ├── sub_issues/
    │   ├── __init__.py
    │   ├── restore_sub_issues_job.py
    │   └── restore_sub_issues_use_case.py
    └── pull_requests/
        ├── __init__.py
        ├── restore_pull_requests_job.py
        └── restore_pull_requests_use_case.py
```

### Dependencies Analysis
- **Cross-entity dependencies**: Issues depend on labels, sub-issues have parent-child relationships
- **Operation orchestration**: Current `src/operations/` handles cross-entity coordination
- **Shared services**: GitHub API clients, storage utilities, job management

## Target Structure

```
src/
├── entities/
│   ├── base/
│   │   ├── __init__.py
│   │   └── models.py
│   ├── labels/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── save_use_cases.py
│   │   ├── restore_use_cases.py
│   │   └── queries.py
│   ├── comments/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── save_use_cases.py
│   │   ├── restore_use_cases.py
│   │   └── queries.py
│   ├── issues/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── save_use_cases.py
│   │   ├── restore_use_cases.py
│   │   └── queries.py
│   ├── pull_requests/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── save_use_cases.py
│   │   ├── restore_use_cases.py
│   │   └── queries.py
│   └── repository/
│       ├── __init__.py
│       └── models.py
├── operations/
│   ├── __init__.py
│   ├── save_orchestrator.py     # Cross-entity save coordination
│   └── restore_orchestrator.py  # Cross-entity restore coordination
├── shared/
│   ├── __init__.py
│   ├── jobs/                    # Common job patterns
│   ├── github/                  # API clients (unchanged)
│   └── storage/                 # Storage utilities (unchanged)
└── [existing structure preserved for backward compatibility]
```

## Implementation Steps

### Step 1: Create Shared Services Foundation
**Estimated Time**: 2 hours

#### 1.1 Create Shared Directory Structure
```bash
mkdir -p src/shared/{jobs,queries,converters}
touch src/shared/__init__.py
touch src/shared/{jobs,queries,converters}/__init__.py
```

#### 1.2 Extract Common Job Patterns
**File**: `src/shared/jobs/base_job.py`
```python
"""Base job patterns for entity operations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, TypeVar, Generic
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from ...github.rest_client import GitHubRestClient
from ...github.graphql_client import GitHubGraphQLClient
from ...storage.storage_adapter import StorageAdapter

T = TypeVar('T')

@dataclass
class JobResult(Generic[T]):
    """Standard job result wrapper."""
    success: bool
    data: T | None = None
    error: str | None = None
    metadata: Dict[str, Any] | None = None

class BaseEntityJob(ABC, Generic[T]):
    """Base class for entity-specific jobs."""
    
    def __init__(
        self,
        github_rest: GitHubRestClient,
        github_graphql: GitHubGraphQLClient,
        storage: StorageAdapter,
        repository: str,
        max_workers: int = 10
    ):
        self.github_rest = github_rest
        self.github_graphql = github_graphql
        self.storage = storage
        self.repository = repository
        self.max_workers = max_workers
    
    @abstractmethod
    async def execute(self) -> JobResult[List[T]]:
        """Execute the job and return results."""
        pass
    
    def _parallel_process(self, items: List[Any], process_func, max_workers: int = None) -> List[Any]:
        """Helper for parallel processing of items."""
        workers = max_workers or self.max_workers
        results = []
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_item = {executor.submit(process_func, item): item for item in items}
            
            for future in as_completed(future_to_item):
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as exc:
                    item = future_to_item[future]
                    print(f'Item {item} generated an exception: {exc}')
        
        return results
```

#### 1.3 Extract Common Query Patterns
**File**: `src/shared/queries/base_queries.py`
```python
"""Base query patterns for GitHub API operations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseQueries(ABC):
    """Base class for entity-specific queries."""
    
    @abstractmethod
    def get_graphql_query(self) -> str:
        """Get GraphQL query for bulk entity retrieval."""
        pass
    
    @abstractmethod
    def get_rest_endpoints(self) -> Dict[str, str]:
        """Get REST API endpoints for entity operations.""" 
        pass
    
    def get_pagination_params(self) -> Dict[str, Any]:
        """Get standard pagination parameters."""
        return {
            "per_page": 100,
            "page": 1
        }
```

#### 1.4 Extract Common Converters
**File**: `src/shared/converters/base_converters.py`
```python
"""Base converter patterns for API response transformation."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, TypeVar
from datetime import datetime

T = TypeVar('T')

class BaseConverter(ABC):
    """Base class for entity-specific converters."""
    
    @abstractmethod
    def from_graphql(self, data: Dict[str, Any]) -> T:
        """Convert GraphQL response to entity model."""
        pass
    
    @abstractmethod
    def from_rest(self, data: Dict[str, Any]) -> T:
        """Convert REST API response to entity model."""
        pass
    
    @abstractmethod
    def to_api_format(self, entity: T) -> Dict[str, Any]:
        """Convert entity model to API request format."""
        pass
    
    def _parse_datetime(self, date_str: str | None) -> datetime | None:
        """Helper to parse GitHub datetime strings."""
        if not date_str:
            return None
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
```

### Step 2: Migrate Labels Entity
**Estimated Time**: 3 hours

#### 2.1 Create Labels Queries
**File**: `src/entities/labels/queries.py`
```python
"""GraphQL and REST queries for labels."""

from typing import Dict
from ...shared.queries.base_queries import BaseQueries

class LabelQueries(BaseQueries):
    """GitHub API queries for labels."""
    
    def get_graphql_query(self) -> str:
        """GraphQL query for bulk label retrieval."""
        return """
        query GetRepositoryLabels($owner: String!, $name: String!, $cursor: String) {
            repository(owner: $owner, name: $name) {
                labels(first: 100, after: $cursor) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    nodes {
                        id
                        name
                        color
                        description
                        url
                    }
                }
            }
        }
        """
    
    def get_rest_endpoints(self) -> Dict[str, str]:
        """REST API endpoints for label operations."""
        return {
            "list": "/repos/{owner}/{repo}/labels",
            "create": "/repos/{owner}/{repo}/labels",
            "update": "/repos/{owner}/{repo}/labels/{name}",
            "delete": "/repos/{owner}/{repo}/labels/{name}"
        }
```

#### 2.2 Create Labels Use Cases
**File**: `src/entities/labels/save_use_cases.py`
```python
"""Save use cases for labels entity."""

from typing import List
from ...shared.jobs.base_job import BaseEntityJob, JobResult
from ...shared.converters.base_converters import BaseConverter
from .models import Label
from .queries import LabelQueries

class LabelConverter(BaseConverter[Label]):
    """Converter for label API responses."""
    
    def from_graphql(self, data: dict) -> Label:
        """Convert GraphQL label data to Label model."""
        return Label(
            id=data["id"],
            name=data["name"],
            color=data["color"],
            description=data.get("description"),
            url=data["url"]
        )
    
    def from_rest(self, data: dict) -> Label:
        """Convert REST API label data to Label model."""
        return Label(
            id=data["id"],
            name=data["name"],
            color=data["color"],
            description=data.get("description"),
            url=data["url"]
        )
    
    def to_api_format(self, label: Label) -> dict:
        """Convert Label model to API request format."""
        return {
            "name": label.name,
            "color": label.color,
            "description": label.description
        }

class SaveLabelsJob(BaseEntityJob[Label]):
    """Job for saving repository labels."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queries = LabelQueries()
        self.converter = LabelConverter()
    
    async def execute(self) -> JobResult[List[Label]]:
        """Execute label saving operation."""
        try:
            # Use GraphQL for efficient bulk retrieval
            owner, repo = self.repository.split('/')
            variables = {"owner": owner, "name": repo}
            
            labels = []
            cursor = None
            
            while True:
                if cursor:
                    variables["cursor"] = cursor
                
                response = await self.github_graphql.execute_query(
                    self.queries.get_graphql_query(),
                    variables
                )
                
                if not response or "repository" not in response:
                    break
                
                label_data = response["repository"]["labels"]
                
                # Convert to Label models
                page_labels = [
                    self.converter.from_graphql(label_node)
                    for label_node in label_data["nodes"]
                ]
                labels.extend(page_labels)
                
                # Check for next page
                page_info = label_data["pageInfo"]
                if not page_info["hasNextPage"]:
                    break
                cursor = page_info["endCursor"]
            
            # Save to storage
            await self.storage.save_labels(labels)
            
            return JobResult(success=True, data=labels)
            
        except Exception as e:
            return JobResult(success=False, error=str(e))

class SaveLabelsUseCase:
    """Use case for saving repository labels."""
    
    def __init__(self, save_job: SaveLabelsJob):
        self.save_job = save_job
    
    async def execute(self) -> JobResult[List[Label]]:
        """Execute the save labels use case."""
        return await self.save_job.execute()
```

**File**: `src/entities/labels/restore_use_cases.py`
```python
"""Restore use cases for labels entity."""

from typing import List
from ...shared.jobs.base_job import BaseEntityJob, JobResult
from .models import Label
from .queries import LabelQueries
from .save_use_cases import LabelConverter

class RestoreLabelsJob(BaseEntityJob[Label]):
    """Job for restoring repository labels."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queries = LabelQueries()
        self.converter = LabelConverter()
    
    async def execute(self) -> JobResult[List[Label]]:
        """Execute label restoration operation."""
        try:
            # Load labels from storage
            stored_labels = await self.storage.load_labels()
            
            # Get existing labels from repository
            endpoints = self.queries.get_rest_endpoints()
            owner, repo = self.repository.split('/')
            
            existing_response = await self.github_rest.get(
                endpoints["list"].format(owner=owner, repo=repo)
            )
            
            existing_labels = {
                label["name"]: self.converter.from_rest(label)
                for label in existing_response
            }
            
            restored_labels = []
            
            # Process each stored label
            for stored_label in stored_labels:
                if stored_label.name in existing_labels:
                    # Update existing label if different
                    existing = existing_labels[stored_label.name]
                    if (existing.color != stored_label.color or 
                        existing.description != stored_label.description):
                        
                        await self.github_rest.patch(
                            endpoints["update"].format(
                                owner=owner, 
                                repo=repo, 
                                name=stored_label.name
                            ),
                            json=self.converter.to_api_format(stored_label)
                        )
                        restored_labels.append(stored_label)
                else:
                    # Create new label
                    await self.github_rest.post(
                        endpoints["create"].format(owner=owner, repo=repo),
                        json=self.converter.to_api_format(stored_label)
                    )
                    restored_labels.append(stored_label)
            
            return JobResult(success=True, data=restored_labels)
            
        except Exception as e:
            return JobResult(success=False, error=str(e))

class RestoreLabelsUseCase:
    """Use case for restoring repository labels."""
    
    def __init__(self, restore_job: RestoreLabelsJob):
        self.restore_job = restore_job
    
    async def execute(self) -> JobResult[List[Label]]:
        """Execute the restore labels use case."""
        return await self.restore_job.execute()
```

#### 2.3 Update Labels Entity Package
**File**: `src/entities/labels/__init__.py`
```python
"""Label entity package."""

from .models import Label
from .save_use_cases import SaveLabelsUseCase, SaveLabelsJob
from .restore_use_cases import RestoreLabelsUseCase, RestoreLabelsJob
from .queries import LabelQueries

__all__ = [
    "Label",
    "SaveLabelsUseCase", 
    "SaveLabelsJob",
    "RestoreLabelsUseCase",
    "RestoreLabelsJob", 
    "LabelQueries"
]
```

### Step 3: Migrate Issues Entity
**Estimated Time**: 4 hours

#### 3.1 Create Issues Queries
**File**: `src/entities/issues/queries.py`
```python
"""GraphQL and REST queries for issues."""

from typing import Dict
from ...shared.queries.base_queries import BaseQueries

class IssueQueries(BaseQueries):
    """GitHub API queries for issues."""
    
    def get_graphql_query(self) -> str:
        """GraphQL query for bulk issue retrieval."""
        return """
        query GetRepositoryIssues($owner: String!, $name: String!, $cursor: String) {
            repository(owner: $owner, name: $name) {
                issues(first: 100, after: $cursor, orderBy: {field: CREATED_AT, direction: ASC}) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    nodes {
                        id
                        number
                        title
                        body
                        state
                        author {
                            login
                            ... on User {
                                id
                                avatarUrl
                                url
                            }
                        }
                        assignees(first: 100) {
                            nodes {
                                login
                                id
                                avatarUrl
                                url
                            }
                        }
                        labels(first: 100) {
                            nodes {
                                id
                                name
                                color
                                description
                                url
                            }
                        }
                        createdAt
                        updatedAt
                        closedAt
                        closedBy {
                            login
                            ... on User {
                                id
                                avatarUrl
                                url
                            }
                        }
                        stateReason
                        url
                        comments {
                            totalCount
                        }
                    }
                }
            }
        }
        """
    
    def get_rest_endpoints(self) -> Dict[str, str]:
        """REST API endpoints for issue operations."""
        return {
            "list": "/repos/{owner}/{repo}/issues",
            "create": "/repos/{owner}/{repo}/issues", 
            "update": "/repos/{owner}/{repo}/issues/{number}",
            "get": "/repos/{owner}/{repo}/issues/{number}"
        }
    
    def get_sub_issue_query(self) -> str:
        """GraphQL query for sub-issue relationships via issue body parsing."""
        return """
        query GetIssueBody($owner: String!, $name: String!, $number: Int!) {
            repository(owner: $owner, name: $name) {
                issue(number: $number) {
                    id
                    number
                    body
                }
            }
        }
        """
```

#### 3.2 Create Issues Use Cases
**File**: `src/entities/issues/save_use_cases.py`
```python
"""Save use cases for issues entity."""

import re
from typing import List, Tuple
from ...shared.jobs.base_job import BaseEntityJob, JobResult
from ...shared.converters.base_converters import BaseConverter
from ..base.models import GitHubUser
from ..labels.models import Label
from .models import Issue, SubIssue
from .queries import IssueQueries

class IssueConverter(BaseConverter[Issue]):
    """Converter for issue API responses."""
    
    def from_graphql(self, data: dict) -> Issue:
        """Convert GraphQL issue data to Issue model."""
        # Convert author
        author_data = data.get("author", {})
        author = GitHubUser(
            login=author_data.get("login", ""),
            id=author_data.get("id", ""),
            avatar_url=author_data.get("avatarUrl", ""),
            html_url=author_data.get("url", "")
        )
        
        # Convert assignees
        assignees = []
        for assignee_data in data.get("assignees", {}).get("nodes", []):
            assignees.append(GitHubUser(
                login=assignee_data.get("login", ""),
                id=assignee_data.get("id", ""),
                avatar_url=assignee_data.get("avatarUrl", ""),
                html_url=assignee_data.get("url", "")
            ))
        
        # Convert labels
        labels = []
        for label_data in data.get("labels", {}).get("nodes", []):
            labels.append(Label(
                id=label_data.get("id", ""),
                name=label_data.get("name", ""),
                color=label_data.get("color", ""),
                description=label_data.get("description"),
                url=label_data.get("url", "")
            ))
        
        # Convert closed_by
        closed_by = None
        if data.get("closedBy"):
            closed_by_data = data["closedBy"]
            closed_by = GitHubUser(
                login=closed_by_data.get("login", ""),
                id=closed_by_data.get("id", ""),
                avatar_url=closed_by_data.get("avatarUrl", ""),
                html_url=closed_by_data.get("url", "")
            )
        
        return Issue(
            id=data["id"],
            number=data["number"],
            title=data["title"],
            body=data.get("body"),
            state=data["state"],
            user=author,
            assignees=assignees,
            labels=labels,
            created_at=self._parse_datetime(data["createdAt"]),
            updated_at=self._parse_datetime(data["updatedAt"]),
            closed_at=self._parse_datetime(data.get("closedAt")),
            closed_by=closed_by,
            state_reason=data.get("stateReason"),
            html_url=data["url"],
            comments_count=data.get("comments", {}).get("totalCount", 0)
        )
    
    def from_rest(self, data: dict) -> Issue:
        """Convert REST API issue data to Issue model."""
        # Similar implementation for REST API format
        # (implementation details similar to GraphQL but with different field names)
        pass
    
    def to_api_format(self, issue: Issue) -> dict:
        """Convert Issue model to API request format."""
        result = {
            "title": issue.title,
            "body": issue.body,
            "state": issue.state.lower()
        }
        
        if issue.assignees:
            result["assignees"] = [user.login for user in issue.assignees]
        
        if issue.labels:
            result["labels"] = [label.name for label in issue.labels]
        
        return result

class SubIssueExtractor:
    """Utility for extracting sub-issue relationships from issue bodies."""
    
    SUB_ISSUE_PATTERNS = [
        r'- \[ \] #(\d+)',  # GitHub task list format
        r'Sub-issues?:\s*#(\d+)',  # Explicit sub-issue declaration
        r'Related:\s*#(\d+)',  # Related issues
        r'Depends on:\s*#(\d+)'  # Dependency declaration
    ]
    
    def extract_sub_issues(self, issue: Issue) -> List[SubIssue]:
        """Extract sub-issue relationships from issue body."""
        if not issue.body:
            return []
        
        sub_issues = []
        position = 0
        
        for pattern in self.SUB_ISSUE_PATTERNS:
            matches = re.finditer(pattern, issue.body, re.IGNORECASE)
            for match in matches:
                sub_issue_number = int(match.group(1))
                sub_issues.append(SubIssue(
                    sub_issue_id=f"sub_{sub_issue_number}",
                    sub_issue_number=sub_issue_number,
                    parent_issue_id=issue.id,
                    parent_issue_number=issue.number,
                    position=position
                ))
                position += 1
        
        return sub_issues

class SaveIssuesJob(BaseEntityJob[Issue]):
    """Job for saving repository issues."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queries = IssueQueries()
        self.converter = IssueConverter()
        self.sub_issue_extractor = SubIssueExtractor()
    
    async def execute(self) -> JobResult[Tuple[List[Issue], List[SubIssue]]]:
        """Execute issue saving operation."""
        try:
            # Use GraphQL for efficient bulk retrieval
            owner, repo = self.repository.split('/')
            variables = {"owner": owner, "name": repo}
            
            issues = []
            all_sub_issues = []
            cursor = None
            
            while True:
                if cursor:
                    variables["cursor"] = cursor
                
                response = await self.github_graphql.execute_query(
                    self.queries.get_graphql_query(),
                    variables
                )
                
                if not response or "repository" not in response:
                    break
                
                issue_data = response["repository"]["issues"]
                
                # Convert to Issue models and extract sub-issues
                for issue_node in issue_data["nodes"]:
                    issue = self.converter.from_graphql(issue_node)
                    issues.append(issue)
                    
                    # Extract sub-issue relationships
                    sub_issues = self.sub_issue_extractor.extract_sub_issues(issue)
                    all_sub_issues.extend(sub_issues)
                
                # Check for next page
                page_info = issue_data["pageInfo"]
                if not page_info["hasNextPage"]:
                    break
                cursor = page_info["endCursor"]
            
            # Save to storage
            await self.storage.save_issues(issues)
            await self.storage.save_sub_issues(all_sub_issues)
            
            return JobResult(success=True, data=(issues, all_sub_issues))
            
        except Exception as e:
            return JobResult(success=False, error=str(e))

class SaveIssuesUseCase:
    """Use case for saving repository issues."""
    
    def __init__(self, save_job: SaveIssuesJob):
        self.save_job = save_job
    
    async def execute(self) -> JobResult[Tuple[List[Issue], List[SubIssue]]]:
        """Execute the save issues use case."""
        return await self.save_job.execute()
```

### Step 4: Update Operations Orchestrators
**Estimated Time**: 2 hours

#### 4.1 Update Save Orchestrator
**File**: `src/operations/save_orchestrator.py`
```python
"""Save operation orchestrator using entity-specific use cases."""

from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..entities.labels import SaveLabelsUseCase, SaveLabelsJob
from ..entities.issues import SaveIssuesUseCase, SaveIssuesJob
from ..entities.comments import SaveCommentsUseCase, SaveCommentsJob
from ..entities.pull_requests import SavePullRequestsUseCase, SavePullRequestsJob
from ..github.rest_client import GitHubRestClient
from ..github.graphql_client import GitHubGraphQLClient
from ..storage.storage_adapter import StorageAdapter

class SaveOrchestrator:
    """Orchestrates entity-specific save operations."""
    
    def __init__(
        self,
        github_rest: GitHubRestClient,
        github_graphql: GitHubGraphQLClient,
        storage: StorageAdapter,
        repository: str
    ):
        self.github_rest = github_rest
        self.github_graphql = github_graphql
        self.storage = storage
        self.repository = repository
    
    async def execute_full_save(self) -> Dict[str, Any]:
        """Execute complete repository save operation."""
        results = {}
        
        # Create entity-specific use cases
        labels_job = SaveLabelsJob(
            self.github_rest, self.github_graphql, self.storage, self.repository
        )
        labels_use_case = SaveLabelsUseCase(labels_job)
        
        issues_job = SaveIssuesJob(
            self.github_rest, self.github_graphql, self.storage, self.repository
        )
        issues_use_case = SaveIssuesUseCase(issues_job)
        
        comments_job = SaveCommentsJob(
            self.github_rest, self.github_graphql, self.storage, self.repository
        )
        comments_use_case = SaveCommentsUseCase(comments_job)
        
        prs_job = SavePullRequestsJob(
            self.github_rest, self.github_graphql, self.storage, self.repository
        )
        prs_use_case = SavePullRequestsUseCase(prs_job)
        
        # Execute in dependency order
        # 1. Save labels first (no dependencies)
        results["labels"] = await labels_use_case.execute()
        
        # 2. Save issues (depends on labels)
        results["issues"] = await issues_use_case.execute()
        
        # 3. Save comments and PRs in parallel (both depend on issues/labels)
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_comments = executor.submit(comments_use_case.execute)
            future_prs = executor.submit(prs_use_case.execute)
            
            results["comments"] = future_comments.result()
            results["pull_requests"] = future_prs.result()
        
        return results
    
    async def execute_selective_save(self, entities: list[str]) -> Dict[str, Any]:
        """Execute selective entity save operation."""
        results = {}
        
        # Mapping of entity names to use case factories
        entity_factories = {
            "labels": lambda: SaveLabelsUseCase(SaveLabelsJob(
                self.github_rest, self.github_graphql, self.storage, self.repository
            )),
            "issues": lambda: SaveIssuesUseCase(SaveIssuesJob(
                self.github_rest, self.github_graphql, self.storage, self.repository
            )),
            "comments": lambda: SaveCommentsUseCase(SaveCommentsJob(
                self.github_rest, self.github_graphql, self.storage, self.repository
            )),
            "pull_requests": lambda: SavePullRequestsUseCase(SavePullRequestsJob(
                self.github_rest, self.github_graphql, self.storage, self.repository
            ))
        }
        
        # Execute requested entities
        for entity in entities:
            if entity in entity_factories:
                use_case = entity_factories[entity]()
                results[entity] = await use_case.execute()
        
        return results
```

### Step 5: Migration and Backward Compatibility
**Estimated Time**: 2 hours

#### 5.1 Create Compatibility Layer
**File**: `src/use_cases/__init__.py`
```python
"""
Use cases package - backward compatibility layer.

DEPRECATED: This package structure is deprecated in favor of entity-specific use cases.
New code should import directly from src.entities.<entity_name> packages.

This module provides backward compatibility for existing imports.
"""

import warnings

# Re-export entity-specific use cases for backward compatibility
from ..entities.labels import SaveLabelsUseCase, RestoreLabelsUseCase
from ..entities.issues import SaveIssuesUseCase, RestoreIssuesUseCase  
from ..entities.comments import SaveCommentsUseCase, RestoreCommentsUseCase
from ..entities.pull_requests import SavePullRequestsUseCase, RestorePullRequestsUseCase

# Issue deprecation warning
warnings.warn(
    "Importing from src.use_cases is deprecated. "
    "Use 'from src.entities.<entity> import UseCase' instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    "SaveLabelsUseCase", "RestoreLabelsUseCase",
    "SaveIssuesUseCase", "RestoreIssuesUseCase", 
    "SaveCommentsUseCase", "RestoreCommentsUseCase",
    "SavePullRequestsUseCase", "RestorePullRequestsUseCase"
]
```

#### 5.2 Update Main Operations Interface
**File**: `src/operations/__init__.py`
```python
"""Operations package - main orchestration interface."""

from .save_orchestrator import SaveOrchestrator
from .restore_orchestrator import RestoreOrchestrator

# Legacy compatibility imports
from ..use_cases import *  # Re-export deprecated use cases

__all__ = [
    "SaveOrchestrator",
    "RestoreOrchestrator"
]
```

### Step 6: Testing Strategy
**Estimated Time**: 3 hours

#### 6.1 Entity-Specific Tests
Create comprehensive test suites for each entity:

- `tests/entities/labels/test_save_use_cases.py`
- `tests/entities/labels/test_restore_use_cases.py`
- `tests/entities/issues/test_save_use_cases.py`
- `tests/entities/issues/test_restore_use_cases.py`
- etc.

#### 6.2 Integration Tests
- `tests/integration/test_entity_orchestration.py` - Cross-entity dependency validation
- `tests/integration/test_backward_compatibility.py` - Compatibility layer validation

#### 6.3 Migration Validation
- All existing tests must pass without modification
- New entity-specific imports must work correctly
- Performance benchmarks must show no regression

## Implementation Checklist

### Foundation
- [ ] Create shared services directory structure
- [ ] Extract common job patterns to shared/jobs/
- [ ] Extract common query patterns to shared/queries/
- [ ] Extract common converter patterns to shared/converters/

### Entity Migration
- [ ] Migrate labels entity (queries, save/restore use cases)
- [ ] Migrate comments entity (queries, save/restore use cases)
- [ ] Migrate issues entity (queries, save/restore use cases, sub-issue extraction)
- [ ] Migrate pull_requests entity (queries, save/restore use cases)
- [ ] Update entity package exports

### Orchestration
- [ ] Update save orchestrator to use entity use cases
- [ ] Update restore orchestrator to use entity use cases
- [ ] Implement selective operation capabilities
- [ ] Preserve cross-entity dependency handling

### Compatibility
- [ ] Create backward compatibility layer in use_cases/
- [ ] Update operations package exports
- [ ] Add deprecation warnings for old import patterns
- [ ] Verify all existing imports continue working

### Testing
- [ ] Create entity-specific test suites
- [ ] Implement integration tests for orchestration
- [ ] Validate backward compatibility
- [ ] Run performance benchmarks
- [ ] Verify all existing tests pass

### Documentation
- [ ] Update developer guides for new import patterns
- [ ] Document entity-specific architecture
- [ ] Create migration guide for teams
- [ ] Update API documentation

## Success Criteria

1. ✅ All existing functionality preserved
2. ✅ Entity-specific use cases provide clear boundaries
3. ✅ Cross-entity orchestration maintains proper dependency handling
4. ✅ Backward compatibility layer functions correctly with deprecation warnings
5. ✅ New entity development follows consistent patterns
6. ✅ Test coverage maintained or improved
7. ✅ Performance characteristics preserved or improved
8. ✅ Code quality metrics maintained (linting, type checking)

## Risk Mitigation

### Rollback Plan
1. Keep current use_cases/ structure as backup
2. Rollback involves removing entities/ use case files and restoring original imports
3. Compatibility layer ensures existing code continues working during transition

### Compatibility Verification
1. **Import testing**: Verify all import patterns work (old and new)
2. **Functional testing**: Ensure use cases behave identically
3. **Integration testing**: Verify orchestration maintains proper coordination
4. **Performance testing**: Ensure no regression in execution time

## Timeline

- **Total Estimated Time**: 16-18 hours
- **Recommended Implementation**: 2-3 development sessions
- **Dependencies**: Requires completed Phase 1 and comprehensive test coverage

## Future Considerations

This Phase 2 implementation enables:
- **Independent entity development**: Teams can work on entities without conflict
- **Consistent patterns**: New entities follow established structure
- **Enhanced testing**: Entity-specific test organization
- **Better maintainability**: Clear separation of concerns with preserved orchestration
- **Performance optimization**: Entity-specific query and caching strategies

The hybrid approach preserves the strengths of operation-based orchestration while gaining the benefits of entity-specific organization.