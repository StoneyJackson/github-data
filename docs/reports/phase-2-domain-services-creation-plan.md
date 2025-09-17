# Phase 2: Domain Services Creation - Detailed Implementation Plan

**Phase:** 2 of 5  
**Duration:** 2-3 sprints (4-6 weeks)  
**Priority:** High - Enables complex business logic encapsulation  
**Dependencies:** Phase 1 completion (enhanced entities required)

## Executive Summary

This phase creates dedicated domain services to handle complex business logic that spans multiple entities or requires sophisticated algorithms. Services will encapsulate the logic currently scattered across operations and provide clean interfaces for entity coordination.

## Service Architecture Strategy

### Service Design Principles
- **Single Responsibility**: Each service handles one business domain
- **Stateless**: Services contain no instance state, only behavior
- **Entity-Focused**: Services orchestrate entity methods, not replace them
- **Testable**: All services fully unit testable in isolation

### Directory Structure
```
src/domain/
├── __init__.py
├── services/
│   ├── __init__.py
│   ├── issue_services.py          # 3 services, 12 methods
│   ├── label_services.py          # 3 services, 9 methods
│   ├── repository_services.py     # 2 services, 8 methods
│   └── validation_services.py     # 2 services, 6 methods
├── exceptions.py                   # Domain-specific exceptions
└── types.py                       # Domain value objects and types
```

## Sprint 1: Core Infrastructure and Issue Services (Week 1-2)

### Sprint Goal
Establish domain service infrastructure and implement the most complex business logic around issue hierarchy management.

### Task 1.1: Domain Infrastructure Setup (4 hours)

#### Create Domain Directory Structure
**Files to create:**
- `src/domain/__init__.py`
- `src/domain/services/__init__.py`
- `src/domain/exceptions.py`
- `src/domain/types.py`

#### Domain Exceptions Implementation
**File:** `src/domain/exceptions.py`
```python
"""Domain-specific exceptions for business rule violations."""

from typing import List, Optional, Dict, Any


class DomainError(Exception):
    """Base exception for domain-related errors."""
    pass


class DomainValidationError(DomainError):
    """Raised when business rules are violated."""
    
    def __init__(self, entity_type: str, validation_error: str, 
                 suggestions: List[str] = None, entity_data: Dict[str, Any] = None):
        self.entity_type = entity_type
        self.validation_error = validation_error
        self.suggestions = suggestions or []
        self.entity_data = entity_data or {}
        
        message = f"{entity_type} validation failed: {validation_error}"
        if suggestions:
            message += f"\nSuggestions: {'; '.join(suggestions)}"
        super().__init__(message)


class StateTransitionError(DomainError):
    """Raised when invalid state transitions are attempted."""
    
    def __init__(self, entity: str, current_state: str, attempted_state: str,
                 allowed_transitions: List[str] = None):
        self.entity = entity
        self.current_state = current_state
        self.attempted_state = attempted_state
        self.allowed_transitions = allowed_transitions or []
        
        message = f"{entity} cannot transition from '{current_state}' to '{attempted_state}'"
        if allowed_transitions:
            message += f"\nAllowed transitions: {', '.join(allowed_transitions)}"
        super().__init__(message)


class ConflictError(DomainError):
    """Raised when entity conflicts are detected."""
    
    def __init__(self, conflict_type: str, conflicting_entities: List[str], 
                 resolution_suggestions: List[str] = None):
        self.conflict_type = conflict_type
        self.conflicting_entities = conflicting_entities
        self.resolution_suggestions = resolution_suggestions or []
        
        message = f"{conflict_type} conflict detected: {', '.join(conflicting_entities)}"
        if resolution_suggestions:
            message += f"\nResolution options: {'; '.join(resolution_suggestions)}"
        super().__init__(message)


class HierarchyError(DomainError):
    """Raised when hierarchy constraints are violated."""
    
    def __init__(self, operation: str, issue_number: int, constraint: str,
                 current_depth: int = None, max_depth: int = None):
        self.operation = operation
        self.issue_number = issue_number
        self.constraint = constraint
        self.current_depth = current_depth
        self.max_depth = max_depth
        
        message = f"Hierarchy constraint violated for issue #{issue_number}: {constraint}"
        if current_depth is not None and max_depth is not None:
            message += f" (current depth: {current_depth}, max: {max_depth})"
        super().__init__(message)
```

### Task 1.2: Issue Hierarchy Service (8 hours)

#### IssueHierarchyService Implementation
**File:** `src/domain/services/issue_services.py`
```python
"""Issue domain services for complex business logic."""

from typing import List, Dict, Set, Optional, Tuple
from datetime import datetime, timedelta

from ..exceptions import HierarchyError, DomainValidationError
from ...models import Issue, SubIssue


class IssueHierarchyService:
    """Manages complex sub-issue relationships and validation."""
    
    MAX_HIERARCHY_DEPTH = 8  # GitHub's sub-issue limit
    
    @staticmethod
    def validate_hierarchy_depth(issue: Issue, new_sub_issue: Issue, 
                                all_issues: List[Issue]) -> bool:
        """Validate that adding sub-issue won't exceed depth limit."""
        # Build hierarchy map
        hierarchy_map = IssueHierarchyService._build_hierarchy_map(all_issues)
        
        # Calculate current depth of parent issue
        parent_depth = IssueHierarchyService._calculate_depth(issue.number, hierarchy_map)
        
        # Calculate depth of new sub-issue's tree
        sub_issue_tree_depth = IssueHierarchyService._calculate_sub_tree_depth(
            new_sub_issue.number, hierarchy_map
        )
        
        total_depth = parent_depth + 1 + sub_issue_tree_depth
        
        if total_depth > IssueHierarchyService.MAX_HIERARCHY_DEPTH:
            raise HierarchyError(
                operation="add_sub_issue",
                issue_number=issue.number,
                constraint=f"Would exceed maximum hierarchy depth of {IssueHierarchyService.MAX_HIERARCHY_DEPTH}",
                current_depth=total_depth,
                max_depth=IssueHierarchyService.MAX_HIERARCHY_DEPTH
            )
        
        return True
    
    @staticmethod
    def detect_circular_dependencies(issues: List[Issue]) -> List[str]:
        """Detect circular dependencies in sub-issue relationships."""
        # Build adjacency list
        graph = {}
        for issue in issues:
            graph[issue.number] = [sub.sub_issue_number for sub in issue.sub_issues]
        
        # Use DFS to detect cycles
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node: int, path: List[int]) -> None:
            if node in rec_stack:
                # Found cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(" → ".join(map(str, cycle)))
                return
            
            if node in visited:
                return
                
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                dfs(neighbor, path.copy())
            
            rec_stack.remove(node)
        
        for issue_number in graph:
            if issue_number not in visited:
                dfs(issue_number, [])
        
        return cycles
    
    @staticmethod
    def calculate_hierarchy_tree(issues: List[Issue]) -> Dict[int, List[Issue]]:
        """Calculate complete hierarchy tree structure."""
        # Create lookup map
        issue_map = {issue.number: issue for issue in issues}
        
        # Build hierarchy tree
        tree = {}
        
        for issue in issues:
            if not issue.sub_issues:
                # Leaf node or root with no children
                tree[issue.number] = []
            else:
                # Has children
                children = []
                for sub_issue in sorted(issue.sub_issues, key=lambda x: x.position):
                    if sub_issue.sub_issue_number in issue_map:
                        children.append(issue_map[sub_issue.sub_issue_number])
                tree[issue.number] = children
        
        return tree
    
    @staticmethod
    def get_hierarchy_metrics(issues: List[Issue]) -> Dict[str, int]:
        """Calculate hierarchy metrics for analysis."""
        hierarchy_map = IssueHierarchyService._build_hierarchy_map(issues)
        
        # Calculate metrics
        total_issues = len(issues)
        root_issues = len([i for i in issues if not IssueHierarchyService._has_parent(i.number, hierarchy_map)])
        leaf_issues = len([i for i in issues if not i.sub_issues])
        max_depth = max([IssueHierarchyService._calculate_depth(i.number, hierarchy_map) for i in issues], default=0)
        avg_children = sum(len(i.sub_issues) for i in issues) / total_issues if total_issues > 0 else 0
        
        return {
            "total_issues": total_issues,
            "root_issues": root_issues,
            "leaf_issues": leaf_issues,
            "max_hierarchy_depth": max_depth,
            "average_children_per_issue": round(avg_children, 2)
        }
    
    @staticmethod
    def _build_hierarchy_map(issues: List[Issue]) -> Dict[int, List[int]]:
        """Build parent-to-children mapping."""
        hierarchy = {}
        for issue in issues:
            hierarchy[issue.number] = [sub.sub_issue_number for sub in issue.sub_issues]
        return hierarchy
    
    @staticmethod
    def _calculate_depth(issue_number: int, hierarchy_map: Dict[int, List[int]]) -> int:
        """Calculate depth of issue in hierarchy (0 = root)."""
        # Find all paths to this issue
        def find_parents(num: int) -> List[int]:
            parents = []
            for parent, children in hierarchy_map.items():
                if num in children:
                    parents.append(parent)
            return parents
        
        def max_depth_to_root(num: int, visited: Set[int] = None) -> int:
            if visited is None:
                visited = set()
            
            if num in visited:
                return 0  # Avoid infinite recursion
            
            visited.add(num)
            parents = find_parents(num)
            
            if not parents:
                return 0  # Root node
            
            return 1 + max(max_depth_to_root(parent, visited.copy()) for parent in parents)
        
        return max_depth_to_root(issue_number)
    
    @staticmethod
    def _calculate_sub_tree_depth(issue_number: int, hierarchy_map: Dict[int, List[int]]) -> int:
        """Calculate maximum depth of sub-tree rooted at issue."""
        children = hierarchy_map.get(issue_number, [])
        if not children:
            return 0
        
        return 1 + max(IssueHierarchyService._calculate_sub_tree_depth(child, hierarchy_map) 
                      for child in children)
    
    @staticmethod
    def _has_parent(issue_number: int, hierarchy_map: Dict[int, List[int]]) -> bool:
        """Check if issue has a parent in the hierarchy."""
        for children in hierarchy_map.values():
            if issue_number in children:
                return True
        return False
```

**Test Implementation:**
**File:** `tests/domain/services/test_issue_hierarchy_service.py`
```python
"""Tests for IssueHierarchyService."""

import pytest
from src.domain.services.issue_services import IssueHierarchyService
from src.domain.exceptions import HierarchyError
from src.models import Issue, SubIssue, GitHubUser
from datetime import datetime


class TestIssueHierarchyService:
    
    def test_validate_hierarchy_depth_within_limit(self):
        """Test hierarchy validation passes within depth limit."""
        # Create test issues with 7-level hierarchy
        issues = self._create_deep_hierarchy(7)
        parent = issues[0]
        new_sub = self._create_issue(8)
        
        # Should pass - adding 8th level is at the limit
        assert IssueHierarchyService.validate_hierarchy_depth(parent, new_sub, issues)
    
    def test_validate_hierarchy_depth_exceeds_limit(self):
        """Test hierarchy validation fails when exceeding depth limit."""
        # Create test issues with 8-level hierarchy (at limit)
        issues = self._create_deep_hierarchy(8)
        parent = issues[-1]  # Deepest issue
        new_sub = self._create_issue(9)
        
        # Should fail - would create 9th level
        with pytest.raises(HierarchyError) as exc_info:
            IssueHierarchyService.validate_hierarchy_depth(parent, new_sub, issues)
        
        assert exc_info.value.current_depth == 9
        assert exc_info.value.max_depth == 8
    
    def test_detect_circular_dependencies_none(self):
        """Test circular dependency detection with valid hierarchy."""
        issues = [
            self._create_issue_with_subs(1, [2, 3]),
            self._create_issue_with_subs(2, [4]),
            self._create_issue_with_subs(3, [5]),
            self._create_issue(4),
            self._create_issue(5)
        ]
        
        cycles = IssueHierarchyService.detect_circular_dependencies(issues)
        assert cycles == []
    
    def test_detect_circular_dependencies_simple_cycle(self):
        """Test detection of simple A → B → A cycle."""
        issues = [
            self._create_issue_with_subs(1, [2]),
            self._create_issue_with_subs(2, [1])  # Creates cycle
        ]
        
        cycles = IssueHierarchyService.detect_circular_dependencies(issues)
        assert len(cycles) == 1
        assert "1 → 2 → 1" in cycles[0] or "2 → 1 → 2" in cycles[0]
    
    def _create_issue(self, number: int) -> Issue:
        """Helper to create test issue."""
        return Issue(
            id=number,
            number=number,
            title=f"Test Issue {number}",
            state="open",
            user=GitHubUser(login="test", id=1, avatar_url="", html_url=""),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            html_url=f"https://github.com/test/repo/issues/{number}",
            comments_count=0
        )
    
    def _create_issue_with_subs(self, number: int, sub_numbers: List[int]) -> Issue:
        """Helper to create issue with sub-issues."""
        issue = self._create_issue(number)
        issue.sub_issues = [
            SubIssue(
                sub_issue_id=sub_num,
                sub_issue_number=sub_num,
                parent_issue_id=number,
                parent_issue_number=number,
                position=i
            ) for i, sub_num in enumerate(sub_numbers)
        ]
        return issue
    
    def _create_deep_hierarchy(self, depth: int) -> List[Issue]:
        """Helper to create linear hierarchy of specified depth."""
        issues = []
        for i in range(1, depth + 1):
            if i < depth:
                issue = self._create_issue_with_subs(i, [i + 1])
            else:
                issue = self._create_issue(i)
            issues.append(issue)
        return issues
```

## Sprint 2: Label and Repository Services (Week 3)

### Sprint Goal
Implement label conflict resolution services and repository-level validation services.

### Task 2.1: Label Services Implementation (6 hours)

#### LabelConflictService Implementation
**File:** `src/domain/services/label_services.py`
```python
"""Label domain services for conflict resolution and validation."""

from typing import List, Dict, Set, Tuple, Optional
from ..exceptions import ConflictError, DomainValidationError
from ...models import Label


class LabelConflictService:
    """Enhanced conflict detection with business rules."""
    
    # System labels that have special handling rules
    SYSTEM_LABELS = {
        "bug", "enhancement", "question", "documentation", 
        "good first issue", "help wanted", "invalid", "wontfix"
    }
    
    @staticmethod
    def detect_conflicts(existing: List[Label], new: List[Label]) -> List[str]:
        """Detect name conflicts between existing and new labels."""
        existing_names = {label.name.lower() for label in existing}
        new_names = {label.name.lower() for label in new}
        
        conflicts = existing_names.intersection(new_names)
        return list(conflicts)
    
    @staticmethod
    def detect_semantic_conflicts(existing: List[Label], new: List[Label]) -> List[str]:
        """Detect semantic conflicts beyond exact name matches."""
        conflicts = []
        
        # Check for case-insensitive conflicts
        existing_lower = {label.name.lower(): label.name for label in existing}
        new_lower = {label.name.lower(): label.name for label in new}
        
        for new_name_lower, new_name in new_lower.items():
            if new_name_lower in existing_lower:
                existing_name = existing_lower[new_name_lower]
                if existing_name != new_name:  # Different casing
                    conflicts.append(f"Case conflict: '{existing_name}' vs '{new_name}'")
        
        # Check for similar names (Levenshtein distance < 3)
        for existing_label in existing:
            for new_label in new:
                if LabelConflictService._are_similar_names(existing_label.name, new_label.name):
                    conflicts.append(f"Similar names: '{existing_label.name}' vs '{new_label.name}'")
        
        # Check for color conflicts with same name semantics
        existing_by_color = {}
        for label in existing:
            color = label.color.lower()
            if color not in existing_by_color:
                existing_by_color[color] = []
            existing_by_color[color].append(label)
        
        for new_label in new:
            color = new_label.color.lower()
            if color in existing_by_color:
                for existing_label in existing_by_color[color]:
                    if LabelConflictService._are_semantically_similar(existing_label, new_label):
                        conflicts.append(f"Color conflict: '{existing_label.name}' and '{new_label.name}' both use #{color}")
        
        return conflicts
    
    @staticmethod
    def suggest_merge_strategy(conflicts: List[str]) -> Dict[str, str]:
        """Suggest resolution strategies for detected conflicts."""
        strategies = {}
        
        for conflict in conflicts:
            if "Case conflict" in conflict:
                strategies[conflict] = "rename_to_match_existing_case"
            elif "Similar names" in conflict:
                strategies[conflict] = "review_and_decide_manually"
            elif "Color conflict" in conflict:
                strategies[conflict] = "assign_different_color"
            else:
                strategies[conflict] = "manual_review_required"
        
        return strategies
    
    @staticmethod
    def resolve_conflicts_automatically(existing: List[Label], new: List[Label], 
                                      strategy: str) -> Tuple[List[Label], List[str]]:
        """Automatically resolve conflicts based on strategy."""
        if strategy == "prefer_existing":
            return LabelConflictService._prefer_existing(existing, new)
        elif strategy == "prefer_new":
            return LabelConflictService._prefer_new(existing, new)
        elif strategy == "merge_descriptions":
            return LabelConflictService._merge_descriptions(existing, new)
        else:
            raise DomainValidationError(
                entity_type="LabelConflictResolution",
                validation_error=f"Unknown resolution strategy: {strategy}",
                suggestions=["prefer_existing", "prefer_new", "merge_descriptions"]
            )
    
    @staticmethod
    def _are_similar_names(name1: str, name2: str, threshold: int = 3) -> bool:
        """Check if two names are similar using Levenshtein distance."""
        # Simple Levenshtein distance implementation
        if len(name1) < len(name2):
            name1, name2 = name2, name1
        
        if len(name2) == 0:
            return len(name1) <= threshold
        
        previous_row = list(range(len(name2) + 1))
        for i, c1 in enumerate(name1):
            current_row = [i + 1]
            for j, c2 in enumerate(name2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1] <= threshold
    
    @staticmethod
    def _are_semantically_similar(label1: Label, label2: Label) -> bool:
        """Check if labels are semantically similar."""
        # Similar if names are similar or both are system labels
        return (LabelConflictService._are_similar_names(label1.name, label2.name) or
                (label1.name.lower() in LabelConflictService.SYSTEM_LABELS and 
                 label2.name.lower() in LabelConflictService.SYSTEM_LABELS))


class LabelValidationService:
    """Comprehensive label validation logic."""
    
    @staticmethod
    def validate_label_set(labels: List[Label]) -> List[str]:
        """Validate an entire set of labels for consistency."""
        errors = []
        
        # Check for duplicate names
        names = [label.name for label in labels]
        duplicates = [name for name in names if names.count(name) > 1]
        if duplicates:
            errors.append(f"Duplicate label names: {', '.join(set(duplicates))}")
        
        # Check for duplicate colors with different names
        color_map = {}
        for label in labels:
            color = label.color.lower()
            if color in color_map:
                errors.append(f"Color #{color} used by multiple labels: {color_map[color]} and {label.name}")
            else:
                color_map[color] = label.name
        
        # Validate individual labels
        for label in labels:
            label_errors = LabelValidationService._validate_single_label(label)
            errors.extend(label_errors)
        
        return errors
    
    @staticmethod
    def validate_repository_consistency(labels: List[Label]) -> bool:
        """Validate that labels are consistent for repository use."""
        # Check for required system labels
        required_system_labels = {"bug", "enhancement"}
        existing_names = {label.name.lower() for label in labels}
        
        missing_required = required_system_labels - existing_names
        if missing_required:
            raise DomainValidationError(
                entity_type="RepositoryLabels",
                validation_error=f"Missing required system labels: {', '.join(missing_required)}",
                suggestions=[f"Add label '{name}'" for name in missing_required]
            )
        
        return True
    
    @staticmethod
    def _validate_single_label(label: Label) -> List[str]:
        """Validate a single label."""
        errors = []
        
        # Validate name
        if not label.name or label.name.strip() != label.name:
            errors.append(f"Label '{label.name}' has invalid name (empty or whitespace)")
        
        if len(label.name) > 50:
            errors.append(f"Label '{label.name}' name too long (max 50 characters)")
        
        # Validate color
        if not label.is_valid_hex_color():
            errors.append(f"Label '{label.name}' has invalid color: #{label.color}")
        
        return errors


class LabelMigrationService:
    """Handle label transformations during restore."""
    
    @staticmethod
    def transform_for_target_repo(labels: List[Label], 
                                target_standards: Dict[str, str]) -> List[Label]:
        """Transform labels to match target repository standards."""
        transformed = []
        
        for label in labels:
            new_label = Label(
                name=label.name,
                color=label.color,
                description=label.description,
                url=label.url,
                id=label.id
            )
            
            # Apply transformations based on standards
            if label.name.lower() in target_standards:
                new_label.name = target_standards[label.name.lower()]
            
            # Ensure system labels have standard colors
            if label.name.lower() == "bug" and label.color.lower() != "d73a4a":
                new_label.color = "d73a4a"  # GitHub's standard bug color
            elif label.name.lower() == "enhancement" and label.color.lower() != "a2eeef":
                new_label.color = "a2eeef"  # GitHub's standard enhancement color
            
            transformed.append(new_label)
        
        return transformed
    
    @staticmethod
    def suggest_standard_labels() -> List[Label]:
        """Suggest a standard set of repository labels."""
        from datetime import datetime
        
        standard_labels = [
            Label(name="bug", color="d73a4a", description="Something isn't working", 
                  url="", id="bug"),
            Label(name="enhancement", color="a2eeef", description="New feature or request", 
                  url="", id="enhancement"),
            Label(name="documentation", color="0075ca", description="Improvements or additions to documentation", 
                  url="", id="documentation"),
            Label(name="good first issue", color="7057ff", description="Good for newcomers", 
                  url="", id="good-first-issue"),
            Label(name="help wanted", color="008672", description="Extra attention is needed", 
                  url="", id="help-wanted"),
            Label(name="question", color="d876e3", description="Further information is requested", 
                  url="", id="question"),
        ]
        
        return standard_labels
```

## Sprint 3: Repository and Validation Services (Week 4)

### Sprint Goal
Complete repository-level services and comprehensive validation services.

### Task 3.1: Repository Services Implementation (6 hours)

#### RepositoryValidationService Implementation
**File:** `src/domain/services/repository_services.py`
```python
"""Repository-level domain services."""

from pathlib import Path
from typing import List, Dict, Set, Optional
from datetime import datetime

from ..exceptions import DomainValidationError
from ...models import RepositoryData, Issue, Label, Comment, PullRequest


class RepositoryValidationService:
    """Validates repository data integrity and consistency."""
    
    @staticmethod
    def validate_complete_dataset(repo_data: RepositoryData, 
                                include_prs: bool = False,
                                include_sub_issues: bool = False) -> bool:
        """Validate that repository data is complete and consistent."""
        errors = []
        
        # Validate basic data integrity
        errors.extend(RepositoryValidationService._validate_data_integrity(repo_data))
        
        # Validate entity relationships
        errors.extend(RepositoryValidationService._validate_relationships(repo_data))
        
        # Validate optional data if requested
        if include_prs:
            errors.extend(RepositoryValidationService._validate_pr_data(repo_data))
        
        if include_sub_issues:
            errors.extend(RepositoryValidationService._validate_sub_issue_data(repo_data))
        
        if errors:
            raise DomainValidationError(
                entity_type="RepositoryData",
                validation_error="Repository data validation failed",
                suggestions=errors
            )
        
        return True
    
    @staticmethod
    def validate_file_requirements(data_path: Path, include_prs: bool = False, 
                                 include_sub_issues: bool = False) -> bool:
        """Validate that all required data files exist."""
        required_files = ["labels.json", "issues.json", "comments.json"]
        
        if include_prs:
            required_files.extend(["pull_requests.json", "pr_comments.json"])
        
        if include_sub_issues:
            required_files.append("sub_issues.json")
        
        missing_files = []
        for filename in required_files:
            file_path = data_path / filename
            if not file_path.exists():
                missing_files.append(str(file_path))
        
        if missing_files:
            raise DomainValidationError(
                entity_type="RepositoryFiles",
                validation_error="Required data files are missing",
                suggestions=[f"Create or restore file: {f}" for f in missing_files]
            )
        
        return True
    
    @staticmethod
    def calculate_data_metrics(repo_data: RepositoryData) -> Dict[str, any]:
        """Calculate comprehensive metrics for repository data."""
        metrics = {
            "basic_counts": {
                "labels": len(repo_data.labels),
                "issues": len(repo_data.issues),
                "comments": len(repo_data.comments),
                "pull_requests": len(repo_data.pull_requests),
                "pr_comments": len(repo_data.pr_comments),
                "sub_issues": len(repo_data.sub_issues)
            },
            "issue_metrics": RepositoryValidationService._calculate_issue_metrics(repo_data.issues),
            "label_metrics": RepositoryValidationService._calculate_label_metrics(repo_data.labels),
            "activity_metrics": RepositoryValidationService._calculate_activity_metrics(repo_data),
            "data_quality": RepositoryValidationService._calculate_quality_metrics(repo_data)
        }
        
        return metrics
    
    @staticmethod
    def _validate_data_integrity(repo_data: RepositoryData) -> List[str]:
        """Validate basic data integrity rules."""
        errors = []
        
        # Check repository name
        if not repo_data.repository_name or not repo_data.repository_name.strip():
            errors.append("Repository name is empty or invalid")
        
        # Check export timestamp
        if repo_data.exported_at > datetime.now():
            errors.append("Export timestamp is in the future")
        
        # Check for empty required collections
        if not repo_data.labels:
            errors.append("No labels found - repository should have at least system labels")
        
        return errors
    
    @staticmethod
    def _validate_relationships(repo_data: RepositoryData) -> List[str]:
        """Validate entity relationships and references."""
        errors = []
        
        # Build reference maps
        issue_numbers = {issue.number for issue in repo_data.issues}
        label_names = {label.name for label in repo_data.labels}
        
        # Validate comment-issue relationships
        for comment in repo_data.comments:
            # Extract issue number from issue_url
            try:
                issue_number = int(comment.issue_url.split('/')[-1])
                if issue_number not in issue_numbers:
                    errors.append(f"Comment {comment.id} references non-existent issue #{issue_number}")
            except (ValueError, IndexError):
                errors.append(f"Comment {comment.id} has invalid issue_url format")
        
        # Validate issue-label relationships
        for issue in repo_data.issues:
            for label in issue.labels:
                if label.name not in label_names:
                    errors.append(f"Issue #{issue.number} references non-existent label '{label.name}'")
        
        # Validate sub-issue relationships
        for sub_issue in repo_data.sub_issues:
            if sub_issue.parent_issue_number not in issue_numbers:
                errors.append(f"Sub-issue relationship references non-existent parent #{sub_issue.parent_issue_number}")
            if sub_issue.sub_issue_number not in issue_numbers:
                errors.append(f"Sub-issue relationship references non-existent sub-issue #{sub_issue.sub_issue_number}")
        
        return errors
    
    @staticmethod
    def _calculate_issue_metrics(issues: List[Issue]) -> Dict[str, any]:
        """Calculate issue-specific metrics."""
        if not issues:
            return {"total": 0}
        
        open_issues = [i for i in issues if i.state == "open"]
        closed_issues = [i for i in issues if i.state == "closed"]
        
        # Calculate average age
        now = datetime.now()
        ages = [(now - issue.created_at).days for issue in issues]
        
        return {
            "total": len(issues),
            "open": len(open_issues),
            "closed": len(closed_issues),
            "open_percentage": round(len(open_issues) / len(issues) * 100, 1),
            "average_age_days": round(sum(ages) / len(ages), 1),
            "has_assignees": len([i for i in issues if i.assignees]),
            "has_labels": len([i for i in issues if i.labels]),
            "with_sub_issues": len([i for i in issues if i.sub_issues])
        }


class RepositoryMigrationService:
    """Handles repository data migration and transformation."""
    
    @staticmethod
    def prepare_for_restore(repo_data: RepositoryData, target_repo: str) -> RepositoryData:
        """Prepare repository data for restoration to target repository."""
        # Create a copy to avoid modifying original
        prepared_data = RepositoryData(
            repository_name=target_repo,
            exported_at=repo_data.exported_at,
            labels=repo_data.labels.copy(),
            issues=repo_data.issues.copy(),
            comments=repo_data.comments.copy(),
            pull_requests=repo_data.pull_requests.copy(),
            pr_comments=repo_data.pr_comments.copy(),
            sub_issues=repo_data.sub_issues.copy()
        )
        
        # Update URLs to point to target repository
        prepared_data = RepositoryMigrationService._update_urls_for_target(prepared_data, target_repo)
        
        # Validate prepared data
        RepositoryValidationService.validate_complete_dataset(prepared_data)
        
        return prepared_data
    
    @staticmethod
    def _update_urls_for_target(repo_data: RepositoryData, target_repo: str) -> RepositoryData:
        """Update all URLs to point to target repository."""
        # This would update html_url fields to point to target repository
        # Implementation depends on URL format requirements
        return repo_data
```

## Integration Testing Strategy

### Test Coverage Requirements
- **Service Integration Tests**: 95%+ coverage for service interactions
- **Business Logic Tests**: 100% coverage for business rule enforcement
- **Error Handling Tests**: All exception paths tested
- **Performance Tests**: Services meet performance targets

### Test Structure
```
tests/domain/services/
├── __init__.py
├── test_issue_services.py           # 30+ test methods
├── test_label_services.py           # 25+ test methods
├── test_repository_services.py      # 20+ test methods
├── test_service_integration.py      # Cross-service tests
└── fixtures/
    ├── complex_hierarchies.py
    ├── conflict_scenarios.py
    └── repository_datasets.py
```

## Performance Targets

### Service Performance Requirements
- **Hierarchy calculations**: <50ms for 1000 issues
- **Conflict detection**: <100ms for 500 labels
- **Repository validation**: <200ms for complete dataset
- **Memory usage**: <10MB additional for service operations

## Migration from Current Code

### Files to Refactor
1. **`src/operations/restore.py`**: Replace procedural logic with service calls
2. **`src/conflict_strategies.py`**: Move logic to LabelConflictService
3. **`src/github/metadata.py`**: Move validation to domain services

### Backward Compatibility
- Keep existing function signatures
- Add deprecation warnings
- Provide adapter methods
- Document migration path

## Success Criteria

### Phase 2 Completion
- [ ] All 10 domain services implemented
- [ ] 35+ service methods with business logic
- [ ] Complete test suite with integration tests
- [ ] Performance benchmarks meet targets
- [ ] Documentation for service usage
- [ ] Migration plan for Phase 3 prepared

This comprehensive service layer provides the foundation for extracting business logic from operations while maintaining clean, testable, and performant code.