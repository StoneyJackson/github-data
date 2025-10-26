# Strategy Pattern Implementation Plan with Code Examples

**Date**: 2025-09-19 21:45  
**Topic**: Implementation plan for Vision 2 (Strategy Pattern) with concrete code examples

## Overview

This document provides a detailed implementation plan for refactoring the current restore operation architecture using Vision 2 (Strategy Pattern). The plan includes concrete code examples to demonstrate how entity-specific logic will be extracted into strategies while preserving orchestrator control over cross-cutting concerns.

## Current Architecture Analysis

The current implementation has a mixed approach:
- `restore.py:23-58` - Main entry point delegates to use case architecture
- `restore_repository.py:21-64` - Orchestrates validation and job execution
- Individual jobs (RestoreLabelsJob, RestoreIssuesJob, etc.) handle entity-specific logic
- The orchestrator maintains control over service coordination and dependency management

## Strategy Pattern Implementation Plan

### Phase 1: Define Strategy Interfaces

Create a clear contract that entities must implement while keeping orchestration simple.

```python
# src/strategies/restore_strategy.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..entities import Label, Issue, Comment, PullRequest, SubIssue

class RestoreEntityStrategy(ABC):
    """Base strategy for entity restoration operations."""
    
    @abstractmethod
    def get_entity_name(self) -> str:
        """Return the entity type name (e.g., 'labels', 'issues')."""
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """Return list of entity types this entity depends on."""
        pass
    
    @abstractmethod
    def load_data(self, input_path: str, storage_service) -> List[Any]:
        """Load entity data from storage."""
        pass
    
    @abstractmethod
    def transform_for_creation(self, entity: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Transform entity for GitHub API creation."""
        pass
    
    @abstractmethod
    def create_entity(self, github_service, repo_name: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create entity via GitHub API."""
        pass
    
    @abstractmethod
    def post_create_actions(self, github_service, repo_name: str, entity: Any, created_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Perform any post-creation actions (e.g., close issues)."""
        pass

class RestoreConflictStrategy(ABC):
    """Strategy for handling conflicts during restoration."""
    
    @abstractmethod
    def resolve_conflicts(self, existing_entities: List[Any], entities_to_restore: List[Any]) -> List[Any]:
        """Resolve conflicts and return entities to create."""
        pass
```

### Phase 2: Implement Concrete Strategies

#### Labels Strategy
```python
# src/strategies/labels_restore_strategy.py
from typing import List, Dict, Any
from .restore_strategy import RestoreEntityStrategy, RestoreConflictStrategy
from ..entities import Label

class LabelsRestoreStrategy(RestoreEntityStrategy):
    def __init__(self, conflict_strategy: RestoreConflictStrategy):
        self._conflict_strategy = conflict_strategy
    
    def get_entity_name(self) -> str:
        return "labels"
    
    def get_dependencies(self) -> List[str]:
        return []  # Labels have no dependencies
    
    def load_data(self, input_path: str, storage_service) -> List[Label]:
        from pathlib import Path
        labels_file = Path(input_path) / "labels.json"
        return storage_service.load_data(labels_file, Label)
    
    def transform_for_creation(self, label: Label, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "name": label.name,
            "color": label.color,
            "description": label.description or ""
        }
    
    def create_entity(self, github_service, repo_name: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        github_service.create_label(
            repo_name, 
            entity_data["name"], 
            entity_data["color"], 
            entity_data["description"]
        )
        return {"name": entity_data["name"]}  # Return identifier
    
    def post_create_actions(self, github_service, repo_name: str, entity: Label, created_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        # Labels don't need post-creation actions
        pass
    
    def resolve_conflicts(self, github_service, repo_name: str, entities_to_restore: List[Label]) -> List[Label]:
        # Get existing labels
        raw_existing = github_service.get_repository_labels(repo_name)
        existing_labels = [Label.from_dict(label) for label in raw_existing]
        
        # Apply conflict resolution strategy
        return self._conflict_strategy.resolve_conflicts(existing_labels, entities_to_restore)
```

#### Issues Strategy
```python
# src/strategies/issues_restore_strategy.py
from typing import List, Dict, Any
from .restore_strategy import RestoreEntityStrategy
from ..entities import Issue

class IssuesRestoreStrategy(RestoreEntityStrategy):
    def __init__(self, include_original_metadata: bool = True):
        self._include_original_metadata = include_original_metadata
    
    def get_entity_name(self) -> str:
        return "issues"
    
    def get_dependencies(self) -> List[str]:
        return ["labels"]  # Issues depend on labels
    
    def load_data(self, input_path: str, storage_service) -> List[Issue]:
        from pathlib import Path
        issues_file = Path(input_path) / "issues.json"
        return storage_service.load_data(issues_file, Issue)
    
    def transform_for_creation(self, issue: Issue, context: Dict[str, Any]) -> Dict[str, Any]:
        # Prepare issue body with metadata if needed
        if self._include_original_metadata:
            from ..github.metadata import add_issue_metadata_footer
            issue_body = add_issue_metadata_footer(issue)
        else:
            issue_body = issue.body or ""
        
        # Convert label objects to names
        label_names = [label.name for label in issue.labels]
        
        return {
            "title": issue.title,
            "body": issue_body,
            "labels": label_names,
            "original_number": issue.number,
            "original_state": issue.state,
            "state_reason": issue.state_reason
        }
    
    def create_entity(self, github_service, repo_name: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        created_issue = github_service.create_issue(
            repo_name,
            entity_data["title"],
            entity_data["body"],
            entity_data["labels"]
        )
        return {
            "number": created_issue["number"],
            "original_number": entity_data["original_number"],
            "original_state": entity_data["original_state"],
            "state_reason": entity_data.get("state_reason")
        }
    
    def post_create_actions(self, github_service, repo_name: str, entity: Issue, created_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        # Close issue if it was originally closed
        if created_data["original_state"] == "closed":
            github_service.close_issue(
                repo_name, 
                created_data["number"], 
                created_data.get("state_reason")
            )
        
        # Store number mapping for dependent entities
        if "issue_number_mapping" not in context:
            context["issue_number_mapping"] = {}
        context["issue_number_mapping"][created_data["original_number"]] = created_data["number"]
```

#### Comments Strategy
```python
# src/strategies/comments_restore_strategy.py
from typing import List, Dict, Any
from .restore_strategy import RestoreEntityStrategy
from ..entities import Comment

class CommentsRestoreStrategy(RestoreEntityStrategy):
    def __init__(self, include_original_metadata: bool = True):
        self._include_original_metadata = include_original_metadata
    
    def get_entity_name(self) -> str:
        return "comments"
    
    def get_dependencies(self) -> List[str]:
        return ["issues"]  # Comments depend on issues
    
    def load_data(self, input_path: str, storage_service) -> List[Comment]:
        from pathlib import Path
        comments_file = Path(input_path) / "comments.json"
        comments = storage_service.load_data(comments_file, Comment)
        # Sort by creation time for chronological order
        return sorted(comments, key=lambda c: c.created_at)
    
    def transform_for_creation(self, comment: Comment, context: Dict[str, Any]) -> Dict[str, Any]:
        # Get issue number mapping from context
        issue_mapping = context.get("issue_number_mapping", {})
        original_issue_number = self._extract_issue_number_from_url(comment.issue_url)
        new_issue_number = issue_mapping.get(original_issue_number)
        
        if new_issue_number is None:
            return None  # Skip this comment
        
        # Prepare comment body
        if self._include_original_metadata:
            from ..github.metadata import add_comment_metadata_footer
            comment_body = add_comment_metadata_footer(comment)
        else:
            comment_body = comment.body
        
        return {
            "body": comment_body,
            "issue_number": new_issue_number,
            "original_issue_number": original_issue_number
        }
    
    def create_entity(self, github_service, repo_name: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        github_service.create_issue_comment(
            repo_name,
            entity_data["issue_number"],
            entity_data["body"]
        )
        return {"issue_number": entity_data["issue_number"]}
    
    def post_create_actions(self, github_service, repo_name: str, entity: Comment, created_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        # Comments don't need post-creation actions
        pass
    
    def _extract_issue_number_from_url(self, issue_url: str) -> int:
        from urllib.parse import urlparse
        parsed_url = urlparse(issue_url)
        path_parts = parsed_url.path.strip("/").split("/")
        issues_index = path_parts.index("issues")
        return int(path_parts[issues_index + 1])
```

### Phase 3: Strategy-Based Orchestrator

```python
# src/strategies/restore_orchestrator.py
from typing import List, Dict, Any, Set
from .restore_strategy import RestoreEntityStrategy

class StrategyBasedRestoreOrchestrator:
    def __init__(self, github_service, storage_service):
        self._github_service = github_service
        self._storage_service = storage_service
        self._strategies: Dict[str, RestoreEntityStrategy] = {}
        self._context: Dict[str, Any] = {}
    
    def register_strategy(self, strategy: RestoreEntityStrategy) -> None:
        """Register an entity restoration strategy."""
        self._strategies[strategy.get_entity_name()] = strategy
    
    def execute_restore(self, repo_name: str, input_path: str, requested_entities: List[str]) -> List[Dict[str, Any]]:
        """Execute restore operation using registered strategies."""
        results = []
        
        # Resolve dependency order
        execution_order = self._resolve_execution_order(requested_entities)
        
        # Execute strategies in dependency order
        for entity_name in execution_order:
            if entity_name in self._strategies:
                result = self._execute_strategy(entity_name, repo_name, input_path)
                results.append(result)
        
        return results
    
    def _resolve_execution_order(self, requested_entities: List[str]) -> List[str]:
        """Resolve execution order based on dependencies."""
        resolved = []
        remaining = set(requested_entities)
        
        while remaining:
            # Find entities with no unresolved dependencies
            ready = []
            for entity in remaining:
                if entity in self._strategies:
                    deps = self._strategies[entity].get_dependencies()
                    if all(dep in resolved or dep not in requested_entities for dep in deps):
                        ready.append(entity)
            
            if not ready:
                raise ValueError(f"Circular dependency detected in: {remaining}")
            
            # Add ready entities to resolution order
            for entity in ready:
                resolved.append(entity)
                remaining.remove(entity)
        
        return resolved
    
    def _execute_strategy(self, entity_name: str, repo_name: str, input_path: str) -> Dict[str, Any]:
        """Execute a single entity restoration strategy."""
        strategy = self._strategies[entity_name]
        
        try:
            # Load data
            entities = strategy.load_data(input_path, self._storage_service)
            
            # Handle conflicts if applicable
            if hasattr(strategy, 'resolve_conflicts'):
                entities = strategy.resolve_conflicts(self._github_service, repo_name, entities)
            
            # Create entities
            created_count = 0
            for entity in entities:
                entity_data = strategy.transform_for_creation(entity, self._context)
                if entity_data is None:
                    continue  # Skip entity (e.g., missing dependency)
                
                created_data = strategy.create_entity(self._github_service, repo_name, entity_data)
                strategy.post_create_actions(self._github_service, repo_name, entity, created_data, self._context)
                created_count += 1
            
            return {
                "entity_name": entity_name,
                "success": True,
                "entities_processed": len(entities),
                "entities_created": created_count
            }
            
        except Exception as e:
            return {
                "entity_name": entity_name,
                "success": False,
                "error": str(e),
                "entities_processed": 0,
                "entities_created": 0
            }
```

### Phase 4: Integration with Current Architecture

```python
# Modified src/operations/restore.py integration
def restore_repository_data_with_services(
    github_service: RepositoryService,
    storage_service: StorageService,
    repo_name: str,
    data_path: str,
    label_conflict_strategy: str = "fail-if-existing",
    include_original_metadata: bool = True,
    include_prs: bool = False,
    include_sub_issues: bool = False,
) -> None:
    """Restore using strategy pattern approach."""
    
    # Create orchestrator
    from ..strategies.restore_orchestrator import StrategyBasedRestoreOrchestrator
    orchestrator = StrategyBasedRestoreOrchestrator(github_service, storage_service)
    
    # Register strategies
    from ..strategies.labels_restore_strategy import LabelsRestoreStrategy
    from ..strategies.issues_restore_strategy import IssuesRestoreStrategy  
    from ..strategies.comments_restore_strategy import CommentsRestoreStrategy
    
    # Create conflict resolution strategy
    conflict_strategy = _create_conflict_strategy(label_conflict_strategy)
    
    # Register entity strategies
    orchestrator.register_strategy(LabelsRestoreStrategy(conflict_strategy))
    orchestrator.register_strategy(IssuesRestoreStrategy(include_original_metadata))
    orchestrator.register_strategy(CommentsRestoreStrategy(include_original_metadata))
    
    # Add PR and sub-issue strategies if requested
    if include_prs:
        from ..strategies.pull_requests_restore_strategy import PullRequestsRestoreStrategy
        orchestrator.register_strategy(PullRequestsRestoreStrategy(include_original_metadata))
    
    if include_sub_issues:
        from ..strategies.sub_issues_restore_strategy import SubIssuesRestoreStrategy
        orchestrator.register_strategy(SubIssuesRestoreStrategy())
    
    # Determine entities to restore
    requested_entities = ["labels", "issues", "comments"]
    if include_prs:
        requested_entities.extend(["pull_requests"])
    if include_sub_issues:
        requested_entities.append("sub_issues")
    
    # Execute restoration
    results = orchestrator.execute_restore(repo_name, data_path, requested_entities)
    
    # Handle errors (maintain backward compatibility)
    failed_operations = [r for r in results if not r["success"]]
    if failed_operations:
        error_messages = [r["error"] for r in failed_operations]
        raise Exception(f"Restore operation failed: {'; '.join(error_messages)}")
```

## Implementation Benefits

### 1. Clear Separation of Concerns
- **Orchestrator**: Handles service coordination, dependency resolution, cross-cutting concerns
- **Strategies**: Focus solely on entity-specific transformation and creation logic
- **Data Flow**: Parent-to-child data flows naturally through orchestrator context

### 2. Service Coordination
- GitHub and Storage services remain centrally managed by orchestrator
- Rate limiting, caching, and transaction management handled at orchestrator level
- No complex inter-strategy communication needed

### 3. Simplified Data Passing
- Context object enables parent entities to pass data to children
- Issue number mapping flows from Issues strategy to Comments strategy
- No complex inter-entity communication protocols needed

### 4. Easy Extension
- New entities require only implementing RestoreEntityStrategy interface
- Dependency declaration enables automatic execution ordering
- Conflict resolution strategies can be composed and reused

## Migration Strategy

### Phase 1: Extract Labels Strategy (Week 1)
1. Create strategy interfaces and base classes
2. Implement LabelsRestoreStrategy with existing conflict resolution logic
3. Update restore.py to use strategy for labels only
4. Test thoroughly with existing test suite

### Phase 2: Extract Issues Strategy (Week 2)
1. Implement IssuesRestoreStrategy
2. Add context-based data passing for issue number mapping
3. Update restore.py to use strategy for issues
4. Verify issue creation and state management

### Phase 3: Extract Comments Strategy (Week 3)
1. Implement CommentsRestoreStrategy with dependency on issues
2. Test parent-to-child data flow (issue number mapping)
3. Verify comment ordering and metadata handling

### Phase 4: Extract Remaining Strategies (Week 4)
1. Implement PullRequestsRestoreStrategy and SubIssuesRestoreStrategy
2. Handle complex dependencies (sub-issues depend on issues)
3. Complete migration and remove old implementation

### Phase 5: Optimization and Enhancement (Week 5)
1. Add parallel execution within entity types where possible
2. Enhance error handling and partial failure recovery
3. Add comprehensive logging and progress reporting

## Next Steps

1. **Review and Approve Plan**: Validate approach with architectural decisions
2. **Create Strategy Interfaces**: Start with base strategy contracts
3. **Implement Labels Strategy**: Begin with simplest entity (no dependencies)
4. **Test Integration**: Ensure compatibility with existing test suite
5. **Iterate and Refine**: Improve based on initial implementation feedback

This strategy pattern approach provides a clean migration path from the current architecture while maintaining all existing functionality and improving separation of concerns.