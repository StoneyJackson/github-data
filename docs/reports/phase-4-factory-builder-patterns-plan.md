# Phase 4: Factory and Builder Patterns - Detailed Implementation Plan

**Phase:** 4 of 5  
**Duration:** 2-3 sprints (4-6 weeks)  
**Priority:** Medium-High - Enables clean object creation and validation  
**Dependencies:** Phase 1-3 completion (entities, services, and migrated operations)

## Executive Summary

This phase introduces factory and builder patterns to provide clean, validated object creation throughout the system. Factories ensure entities are created with proper business rule validation, while builders enable complex object composition with fluent interfaces.

## Pattern Strategy

### Factory Pattern Benefits
- **Centralized Creation**: All entity creation goes through validated factories
- **Business Rule Enforcement**: No invalid entities can be created
- **Consistent Initialization**: Standard initialization patterns
- **Testing Support**: Easy mock creation for testing

### Builder Pattern Benefits
- **Complex Object Assembly**: Step-by-step construction of complex entities
- **Fluent Interface**: Readable, self-documenting object creation
- **Validation Integration**: Validation at each building step
- **Immutability Support**: Build-then-freeze pattern for data integrity

### Directory Structure
```
src/domain/
├── factories/
│   ├── __init__.py
│   ├── issue_factory.py           # Issue creation with validation
│   ├── label_factory.py           # Label creation with standards
│   ├── comment_factory.py         # Comment creation and analysis
│   ├── pull_request_factory.py    # PR creation with state validation
│   └── repository_factory.py      # Repository data assembly
├── builders/
│   ├── __init__.py
│   ├── repository_data_builder.py # Complex repository data construction
│   ├── issue_hierarchy_builder.py # Sub-issue hierarchy construction
│   └── label_set_builder.py       # Label set with conflict resolution
└── value_objects/
    ├── __init__.py
    ├── metadata.py                 # Value objects for metadata
    ├── timestamps.py               # Time-related value objects
    └── identifiers.py              # ID and number value objects
```

## Sprint 1: Core Factory Infrastructure (Week 1-2)

### Sprint Goal
Establish factory infrastructure and implement entity factories with comprehensive validation.

### Task 1.1: Factory Base Classes and Infrastructure (4 hours)

#### Base Factory Implementation
**File:** `src/domain/factories/__init__.py`
```python
"""Domain object factories for validated entity creation."""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Dict, Any, List
from ..exceptions import DomainValidationError

T = TypeVar('T')


class BaseFactory(ABC, Generic[T]):
    """Base factory for domain entities with validation."""
    
    @abstractmethod
    def create(self, **kwargs) -> T:
        """Create and validate entity."""
        pass
    
    @abstractmethod
    def create_from_dict(self, data: Dict[str, Any]) -> T:
        """Create entity from dictionary data."""
        pass
    
    def validate_creation_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate data before entity creation."""
        errors = []
        
        # Common validation logic
        if not isinstance(data, dict):
            errors.append("Creation data must be a dictionary")
            return errors
        
        # Subclasses will implement specific validation
        errors.extend(self._validate_specific_data(data))
        
        return errors
    
    @abstractmethod
    def _validate_specific_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate entity-specific creation data."""
        pass
    
    def _ensure_valid_creation(self, data: Dict[str, Any]) -> None:
        """Ensure creation data is valid, raising exception if not."""
        errors = self.validate_creation_data(data)
        if errors:
            raise DomainValidationError(
                entity_type=self.__class__.__name__.replace('Factory', ''),
                validation_error="Entity creation validation failed",
                suggestions=errors
            )


class ValidationMixin:
    """Mixin for common validation patterns."""
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required: List[str]) -> List[str]:
        """Validate that required fields are present and non-empty."""
        errors = []
        for field in required:
            if field not in data:
                errors.append(f"Required field missing: {field}")
            elif data[field] is None:
                errors.append(f"Required field cannot be None: {field}")
            elif isinstance(data[field], str) and not data[field].strip():
                errors.append(f"Required field cannot be empty: {field}")
        return errors
    
    @staticmethod
    def validate_field_types(data: Dict[str, Any], type_specs: Dict[str, type]) -> List[str]:
        """Validate that fields have correct types."""
        errors = []
        for field, expected_type in type_specs.items():
            if field in data and data[field] is not None:
                if not isinstance(data[field], expected_type):
                    errors.append(f"Field {field} must be {expected_type.__name__}, got {type(data[field]).__name__}")
        return errors
```

### Task 1.2: Issue Factory Implementation (8 hours)

#### IssueFactory Implementation
**File:** `src/domain/factories/issue_factory.py`
```python
"""Factory for creating validated Issue entities."""

from datetime import datetime
from typing import Dict, Any, List, Optional
from ..exceptions import DomainValidationError, StateTransitionError
from ...models import Issue, GitHubUser, Label, SubIssue
from . import BaseFactory, ValidationMixin


class IssueFactory(BaseFactory[Issue], ValidationMixin):
    """Factory for creating valid Issue entities with business rule enforcement."""
    
    # Business constants
    MAX_TITLE_LENGTH = 256
    MAX_ASSIGNEES = 10
    VALID_STATES = {"open", "closed"}
    
    def create(self, title: str, body: str = "", state: str = "open", 
               user: GitHubUser = None, labels: List[Label] = None, 
               assignees: List[GitHubUser] = None, **kwargs) -> Issue:
        """Create issue with validation and business rule enforcement."""
        
        # Set defaults
        labels = labels or []
        assignees = assignees or []
        
        # Create data dictionary
        creation_data = {
            "title": title,
            "body": body,
            "state": state,
            "user": user,
            "labels": labels,
            "assignees": assignees,
            **kwargs
        }
        
        # Validate and create
        self._ensure_valid_creation(creation_data)
        return self._create_issue_entity(creation_data)
    
    def create_from_github_data(self, raw_data: Dict[str, Any]) -> Issue:
        """Create issue from GitHub API response with validation."""
        # Transform GitHub API data to our format
        transformed_data = self._transform_github_data(raw_data)
        
        # Validate and create
        self._ensure_valid_creation(transformed_data)
        return self._create_issue_entity(transformed_data)
    
    def create_from_dict(self, data: Dict[str, Any]) -> Issue:
        """Create issue from dictionary data with validation."""
        self._ensure_valid_creation(data)
        return self._create_issue_entity(data)
    
    def create_sub_issue(self, parent_issue: Issue, title: str, body: str = "", 
                        position: Optional[int] = None, **kwargs) -> Issue:
        """Create sub-issue with hierarchy validation."""
        from ..services.issue_services import IssueHierarchyService
        
        # Validate parent can accept sub-issues
        if not parent_issue.can_accept_sub_issues():
            raise StateTransitionError(
                entity=f"Issue #{parent_issue.number}",
                current_state=parent_issue.state,
                attempted_state="accept_sub_issues"
            )
        
        # Calculate position if not provided
        if position is None:
            existing_positions = [sub.position for sub in parent_issue.sub_issues]
            position = max(existing_positions, default=0) + 1
        
        # Create the sub-issue
        sub_issue = self.create(
            title=title,
            body=body,
            user=parent_issue.user,  # Inherit user from parent
            **kwargs
        )
        
        # Validate hierarchy constraints would be met
        # (This assumes we have access to all issues - might need dependency injection)
        
        return sub_issue
    
    def create_test_issue(self, number: int = 1, **overrides) -> Issue:
        """Create issue for testing purposes with sensible defaults."""
        defaults = {
            "id": number,
            "number": number,
            "title": f"Test Issue {number}",
            "body": f"Test issue body for issue #{number}",
            "state": "open",
            "user": self._create_test_user(),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "html_url": f"https://github.com/test/repo/issues/{number}",
            "comments_count": 0
        }
        
        # Apply overrides
        defaults.update(overrides)
        
        return self.create_from_dict(defaults)
    
    def _validate_specific_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate issue-specific creation data."""
        errors = []
        
        # Required fields validation
        required_fields = ["title", "state", "user"]
        errors.extend(self.validate_required_fields(data, required_fields))
        
        # Type validation
        type_specs = {
            "title": str,
            "body": str,
            "state": str,
            "number": int,
            "comments_count": int
        }
        errors.extend(self.validate_field_types(data, type_specs))
        
        # Business rule validation
        if "title" in data and data["title"]:
            errors.extend(self._validate_title(data["title"]))
        
        if "state" in data:
            errors.extend(self._validate_state(data["state"]))
        
        if "assignees" in data and data["assignees"]:
            errors.extend(self._validate_assignees(data["assignees"]))
        
        if "labels" in data and data["labels"]:
            errors.extend(self._validate_labels(data["labels"]))
        
        return errors
    
    def _validate_title(self, title: str) -> List[str]:
        """Validate issue title business rules."""
        errors = []
        
        if not title.strip():
            errors.append("Issue title cannot be empty or whitespace only")
        
        if len(title) > self.MAX_TITLE_LENGTH:
            errors.append(f"Issue title cannot exceed {self.MAX_TITLE_LENGTH} characters")
        
        # Check for suspicious patterns
        if title.lower().strip() in ["test", "todo", "fix", "bug"]:
            errors.append(f"Issue title '{title}' is too generic - provide more descriptive title")
        
        return errors
    
    def _validate_state(self, state: str) -> List[str]:
        """Validate issue state business rules."""
        errors = []
        
        if state.lower() not in self.VALID_STATES:
            errors.append(f"Invalid issue state '{state}'. Must be one of: {', '.join(self.VALID_STATES)}")
        
        return errors
    
    def _validate_assignees(self, assignees: List[GitHubUser]) -> List[str]:
        """Validate assignees business rules."""
        errors = []
        
        if len(assignees) > self.MAX_ASSIGNEES:
            errors.append(f"Cannot assign more than {self.MAX_ASSIGNEES} users to an issue")
        
        # Check for duplicate assignees
        user_logins = [user.login for user in assignees]
        if len(user_logins) != len(set(user_logins)):
            errors.append("Cannot assign the same user multiple times")
        
        return errors
    
    def _validate_labels(self, labels: List[Label]) -> List[str]:
        """Validate labels business rules."""
        errors = []
        
        # Check for duplicate labels
        label_names = [label.name for label in labels]
        if len(label_names) != len(set(label_names)):
            errors.append("Cannot apply the same label multiple times")
        
        # Validate each label
        for label in labels:
            if not label.is_valid():  # Assuming this method exists from Phase 1
                errors.append(f"Invalid label: {label.name}")
        
        return errors
    
    def _create_issue_entity(self, data: Dict[str, Any]) -> Issue:
        """Create the actual Issue entity from validated data."""
        # Set defaults for optional fields
        defaults = {
            "body": "",
            "assignees": [],
            "labels": [],
            "closed_at": None,
            "closed_by": None,
            "state_reason": None,
            "comments_count": 0,
            "sub_issues": []
        }
        
        # Merge with defaults
        entity_data = {**defaults, **data}
        
        # Create and return entity
        return Issue(**entity_data)
    
    def _transform_github_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform GitHub API data to our entity format."""
        # Handle GitHub API field mappings
        transformed = {}
        
        # Direct mappings
        direct_fields = ["id", "number", "title", "body", "state", "html_url", "created_at", "updated_at"]
        for field in direct_fields:
            if field in raw_data:
                transformed[field] = raw_data[field]
        
        # Complex mappings
        if "user" in raw_data:
            transformed["user"] = self._create_github_user_from_data(raw_data["user"])
        
        if "assignees" in raw_data:
            transformed["assignees"] = [
                self._create_github_user_from_data(assignee) 
                for assignee in raw_data["assignees"]
            ]
        
        if "labels" in raw_data:
            transformed["labels"] = [
                self._create_label_from_data(label)
                for label in raw_data["labels"]
            ]
        
        # Handle optional fields
        transformed["comments_count"] = raw_data.get("comments", 0)
        transformed["closed_at"] = raw_data.get("closed_at")
        transformed["closed_by"] = raw_data.get("closed_by")
        transformed["state_reason"] = raw_data.get("state_reason")
        
        return transformed
    
    def _create_github_user_from_data(self, user_data: Dict[str, Any]) -> GitHubUser:
        """Create GitHubUser from API data."""
        return GitHubUser(
            login=user_data["login"],
            id=user_data["id"],
            avatar_url=user_data["avatar_url"],
            html_url=user_data["html_url"]
        )
    
    def _create_label_from_data(self, label_data: Dict[str, Any]) -> Label:
        """Create Label from API data."""
        return Label(
            name=label_data["name"],
            color=label_data["color"],
            description=label_data.get("description"),
            url=label_data["url"],
            id=label_data["id"]
        )
    
    def _create_test_user(self) -> GitHubUser:
        """Create test user for testing purposes."""
        return GitHubUser(
            login="testuser",
            id=1,
            avatar_url="https://github.com/testuser.png",
            html_url="https://github.com/testuser"
        )
```

### Task 1.3: Label Factory Implementation (6 hours)

#### LabelFactory Implementation
**File:** `src/domain/factories/label_factory.py`
```python
"""Factory for creating validated Label entities."""

import re
from typing import Dict, Any, List, Optional
from ..exceptions import DomainValidationError
from ...models import Label
from . import BaseFactory, ValidationMixin


class LabelFactory(BaseFactory[Label], ValidationMixin):
    """Factory for creating valid Label entities with standards compliance."""
    
    # Business constants
    MAX_NAME_LENGTH = 50
    COLOR_PATTERN = re.compile(r'^[0-9A-Fa-f]{6}$')
    
    # Standard system labels
    SYSTEM_LABELS = {
        "bug": {"color": "d73a4a", "description": "Something isn't working"},
        "enhancement": {"color": "a2eeef", "description": "New feature or request"},
        "documentation": {"color": "0075ca", "description": "Improvements or additions to documentation"},
        "good first issue": {"color": "7057ff", "description": "Good for newcomers"},
        "help wanted": {"color": "008672", "description": "Extra attention is needed"},
        "question": {"color": "d876e3", "description": "Further information is requested"},
        "wontfix": {"color": "ffffff", "description": "This will not be worked on"},
        "invalid": {"color": "e4e669", "description": "This doesn't seem right"},
        "duplicate": {"color": "cfd3d7", "description": "This issue or pull request already exists"}
    }
    
    def create(self, name: str, color: str, description: str = "", **kwargs) -> Label:
        """Create label with validation and standards compliance."""
        creation_data = {
            "name": name,
            "color": color,
            "description": description,
            **kwargs
        }
        
        self._ensure_valid_creation(creation_data)
        return self._create_label_entity(creation_data)
    
    def create_from_dict(self, data: Dict[str, Any]) -> Label:
        """Create label from dictionary data with validation."""
        self._ensure_valid_creation(data)
        return self._create_label_entity(data)
    
    def create_system_label(self, label_type: str, **overrides) -> Label:
        """Create standard system label with predefined properties."""
        if label_type.lower() not in self.SYSTEM_LABELS:
            available = ", ".join(self.SYSTEM_LABELS.keys())
            raise DomainValidationError(
                entity_type="Label",
                validation_error=f"Unknown system label type: {label_type}",
                suggestions=[f"Available system labels: {available}"]
            )
        
        system_config = self.SYSTEM_LABELS[label_type.lower()]
        
        # Create with system defaults, allowing overrides
        creation_data = {
            "name": label_type,
            "color": system_config["color"],
            "description": system_config["description"],
            "url": "",
            "id": f"system-{label_type}",
            **overrides
        }
        
        return self.create_from_dict(creation_data)
    
    def create_standard_set(self) -> List[Label]:
        """Create a standard set of repository labels."""
        standard_labels = []
        
        for label_type in ["bug", "enhancement", "documentation", "good first issue", "help wanted", "question"]:
            standard_labels.append(self.create_system_label(label_type))
        
        return standard_labels
    
    def create_with_auto_color(self, name: str, description: str = "", 
                              color_preference: Optional[str] = None) -> Label:
        """Create label with automatically generated color if not provided."""
        if color_preference and self._is_valid_color(color_preference):
            color = color_preference
        else:
            color = self._generate_color_for_name(name)
        
        return self.create(name, color, description)
    
    def create_test_label(self, name: str = "test-label", **overrides) -> Label:
        """Create label for testing purposes."""
        defaults = {
            "name": name,
            "color": "f0f0f0",
            "description": f"Test label: {name}",
            "url": f"https://github.com/test/repo/labels/{name}",
            "id": f"test-{name}"
        }
        
        defaults.update(overrides)
        return self.create_from_dict(defaults)
    
    def _validate_specific_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate label-specific creation data."""
        errors = []
        
        # Required fields
        required_fields = ["name", "color"]
        errors.extend(self.validate_required_fields(data, required_fields))
        
        # Type validation
        type_specs = {
            "name": str,
            "color": str,
            "description": str,
            "url": str
        }
        errors.extend(self.validate_field_types(data, type_specs))
        
        # Business rule validation
        if "name" in data and data["name"]:
            errors.extend(self._validate_name(data["name"]))
        
        if "color" in data and data["color"]:
            errors.extend(self._validate_color(data["color"]))
        
        return errors
    
    def _validate_name(self, name: str) -> List[str]:
        """Validate label name business rules."""
        errors = []
        
        # Basic validation
        if not name.strip():
            errors.append("Label name cannot be empty or whitespace only")
        
        if len(name) > self.MAX_NAME_LENGTH:
            errors.append(f"Label name cannot exceed {self.MAX_NAME_LENGTH} characters")
        
        # Check for invalid characters (GitHub restrictions)
        if any(char in name for char in ['<', '>', '&', '"', "'"]):
            errors.append("Label name cannot contain HTML special characters")
        
        # Check for leading/trailing whitespace
        if name != name.strip():
            errors.append("Label name cannot have leading or trailing whitespace")
        
        return errors
    
    def _validate_color(self, color: str) -> List[str]:
        """Validate label color business rules."""
        errors = []
        
        # Remove # prefix if present
        clean_color = color.lstrip('#')
        
        if not self.COLOR_PATTERN.match(clean_color):
            errors.append(f"Label color must be a valid 6-character hex code (got: {color})")
        
        return errors
    
    def _is_valid_color(self, color: str) -> bool:
        """Check if color is valid hex."""
        clean_color = color.lstrip('#')
        return bool(self.COLOR_PATTERN.match(clean_color))
    
    def _generate_color_for_name(self, name: str) -> str:
        """Generate a color based on label name hash."""
        import hashlib
        
        # Create hash of name
        hash_obj = hashlib.md5(name.encode())
        hex_hash = hash_obj.hexdigest()
        
        # Take first 6 characters as color
        color = hex_hash[:6]
        
        # Ensure color has good contrast (not too light or dark)
        return self._adjust_color_contrast(color)
    
    def _adjust_color_contrast(self, color: str) -> str:
        """Adjust color for better contrast and visibility."""
        # Convert to RGB for brightness calculation
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        
        # Calculate brightness (0-255)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        
        # If too light or too dark, adjust
        if brightness > 200:  # Too light
            r = max(0, r - 50)
            g = max(0, g - 50)
            b = max(0, b - 50)
        elif brightness < 80:  # Too dark
            r = min(255, r + 80)
            g = min(255, g + 80)
            b = min(255, b + 80)
        
        # Convert back to hex
        return f"{r:02x}{g:02x}{b:02x}"
    
    def _create_label_entity(self, data: Dict[str, Any]) -> Label:
        """Create the actual Label entity from validated data."""
        # Set defaults
        defaults = {
            "description": "",
            "url": "",
            "id": f"label-{data.get('name', 'unknown')}"
        }
        
        # Clean color (remove # if present)
        if "color" in data:
            data["color"] = data["color"].lstrip('#')
        
        # Merge with defaults
        entity_data = {**defaults, **data}
        
        return Label(**entity_data)
```

## Sprint 2: Builder Pattern Implementation (Week 3)

### Sprint Goal
Implement builder patterns for complex object composition with validation at each step.

### Task 2.1: Repository Data Builder (8 hours)

#### RepositoryDataBuilder Implementation
**File:** `src/domain/builders/repository_data_builder.py`
```python
"""Builder for constructing complex RepositoryData with validation."""

from datetime import datetime
from typing import List, Dict, Optional, Set
from pathlib import Path

from ..exceptions import DomainValidationError, ConflictError
from ..services.repository_services import RepositoryValidationService
from ..services.label_services import LabelConflictService
from ..services.issue_services import IssueHierarchyService
from ...models import RepositoryData, Label, Issue, Comment, PullRequest, PullRequestComment, SubIssue


class RepositoryDataBuilder:
    """Fluent interface for building repository data with validation."""
    
    def __init__(self, repo_name: str, exported_at: Optional[datetime] = None):
        """Initialize builder with repository name."""
        self._repo_name = repo_name
        self._exported_at = exported_at or datetime.now()
        
        # Data collections
        self._labels: List[Label] = []
        self._issues: List[Issue] = []
        self._comments: List[Comment] = []
        self._pull_requests: List[PullRequest] = []
        self._pr_comments: List[PullRequestComment] = []
        self._sub_issues: List[SubIssue] = []
        
        # Validation tracking
        self._validation_errors: List[str] = []
        self._warnings: List[str] = []
        
        # Build state
        self._is_built = False
    
    def add_labels(self, labels: List[Label], resolve_conflicts: bool = True) -> 'RepositoryDataBuilder':
        """Add labels with conflict detection and resolution."""
        if self._is_built:
            raise DomainValidationError("RepositoryDataBuilder", "Cannot modify builder after build() called")
        
        # Detect conflicts with existing labels
        conflicts = LabelConflictService.detect_conflicts(self._labels, labels)
        
        if conflicts and not resolve_conflicts:
            raise ConflictError(
                "label_name", 
                conflicts,
                ["Use resolve_conflicts=True", "Remove conflicting labels before adding"]
            )
        
        if conflicts and resolve_conflicts:
            # Automatically resolve conflicts by preferring new labels
            resolved_labels, conflict_log = LabelConflictService.resolve_conflicts_automatically(
                self._labels, labels, "prefer_new"
            )
            self._labels = resolved_labels
            self._warnings.extend([f"Resolved label conflict: {log}" for log in conflict_log])
        else:
            self._labels.extend(labels)
        
        # Validate label set consistency
        validation_errors = LabelConflictService.validate_label_set(self._labels)
        if validation_errors:
            self._validation_errors.extend(validation_errors)
        
        return self
    
    def add_issues(self, issues: List[Issue], validate_hierarchy: bool = True) -> 'RepositoryDataBuilder':
        """Add issues with hierarchy validation."""
        if self._is_built:
            raise DomainValidationError("RepositoryDataBuilder", "Cannot modify builder after build() called")
        
        # Validate individual issues
        for issue in issues:
            if not issue.is_valid():  # Assuming this method from Phase 1
                self._validation_errors.append(f"Invalid issue #{issue.number}: {issue.validation_errors}")
                continue
            
            # Check for duplicate issue numbers
            existing_numbers = {i.number for i in self._issues}
            if issue.number in existing_numbers:
                self._validation_errors.append(f"Duplicate issue number: #{issue.number}")
                continue
        
        # Add valid issues
        valid_issues = [i for i in issues if i.is_valid()]
        self._issues.extend(valid_issues)
        
        # Validate hierarchy if requested
        if validate_hierarchy and self._issues:
            try:
                circular_deps = IssueHierarchyService.detect_circular_dependencies(self._issues)
                if circular_deps:
                    self._validation_errors.extend([f"Circular dependency: {dep}" for dep in circular_deps])
                
                # Validate hierarchy metrics
                metrics = IssueHierarchyService.get_hierarchy_metrics(self._issues)
                if metrics["max_hierarchy_depth"] > 8:
                    self._validation_errors.append(f"Hierarchy too deep: {metrics['max_hierarchy_depth']} levels (max 8)")
                
            except Exception as e:
                self._validation_errors.append(f"Hierarchy validation failed: {str(e)}")
        
        return self
    
    def add_comments(self, comments: List[Comment], validate_references: bool = True) -> 'RepositoryDataBuilder':
        """Add comments with reference validation."""
        if self._is_built:
            raise DomainValidationError("RepositoryDataBuilder", "Cannot modify builder after build() called")
        
        if validate_references:
            issue_numbers = {issue.number for issue in self._issues}
            
            for comment in comments:
                # Validate comment references existing issue
                try:
                    issue_number = int(comment.issue_url.split('/')[-1])
                    if issue_number not in issue_numbers:
                        self._validation_errors.append(
                            f"Comment {comment.id} references non-existent issue #{issue_number}"
                        )
                except (ValueError, IndexError):
                    self._validation_errors.append(f"Comment {comment.id} has invalid issue_url format")
        
        # Validate individual comments
        for comment in comments:
            if comment.is_empty():  # Assuming this method from Phase 1
                self._warnings.append(f"Empty comment: {comment.id}")
            
            if comment.exceeds_max_length():  # Assuming this method from Phase 1
                self._validation_errors.append(f"Comment {comment.id} exceeds maximum length")
        
        self._comments.extend(comments)
        return self
    
    def add_pull_requests(self, pull_requests: List[PullRequest]) -> 'RepositoryDataBuilder':
        """Add pull requests with validation."""
        if self._is_built:
            raise DomainValidationError("RepositoryDataBuilder", "Cannot modify builder after build() called")
        
        for pr in pull_requests:
            # Validate PR state and branches
            if not pr.are_branches_valid():  # Assuming this method from Phase 1
                self._validation_errors.append(f"PR #{pr.number} has invalid branch configuration")
            
            # Check for duplicate PR numbers
            existing_numbers = {p.number for p in self._pull_requests}
            if pr.number in existing_numbers:
                self._validation_errors.append(f"Duplicate PR number: #{pr.number}")
                continue
        
        self._pull_requests.extend(pull_requests)
        return self
    
    def add_pr_comments(self, pr_comments: List[PullRequestComment], validate_references: bool = True) -> 'RepositoryDataBuilder':
        """Add PR comments with reference validation."""
        if self._is_built:
            raise DomainValidationError("RepositoryDataBuilder", "Cannot modify builder after build() called")
        
        if validate_references:
            pr_numbers = {pr.number for pr in self._pull_requests}
            
            for comment in pr_comments:
                # Validate comment references existing PR
                try:
                    pr_number = int(comment.pull_request_url.split('/')[-1])
                    if pr_number not in pr_numbers:
                        self._validation_errors.append(
                            f"PR comment {comment.id} references non-existent PR #{pr_number}"
                        )
                except (ValueError, IndexError):
                    self._validation_errors.append(f"PR comment {comment.id} has invalid pull_request_url format")
        
        self._pr_comments.extend(pr_comments)
        return self
    
    def add_sub_issues(self, sub_issues: List[SubIssue], validate_hierarchy: bool = True) -> 'RepositoryDataBuilder':
        """Add sub-issue relationships with hierarchy validation."""
        if self._is_built:
            raise DomainValidationError("RepositoryDataBuilder", "Cannot modify builder after build() called")
        
        if validate_hierarchy:
            issue_numbers = {issue.number for issue in self._issues}
            
            for sub_issue in sub_issues:
                # Validate both parent and child exist
                if sub_issue.parent_issue_number not in issue_numbers:
                    self._validation_errors.append(
                        f"Sub-issue references non-existent parent #{sub_issue.parent_issue_number}"
                    )
                
                if sub_issue.sub_issue_number not in issue_numbers:
                    self._validation_errors.append(
                        f"Sub-issue references non-existent child #{sub_issue.sub_issue_number}"
                    )
        
        self._sub_issues.extend(sub_issues)
        return self
    
    def with_metadata(self, exported_at: datetime = None, **metadata) -> 'RepositoryDataBuilder':
        """Set metadata for the repository data."""
        if exported_at:
            self._exported_at = exported_at
        
        # Could extend to support additional metadata
        return self
    
    def validate_build_requirements(self) -> List[str]:
        """Validate that all requirements for building are met."""
        errors = []
        
        # Check minimum required data
        if not self._labels:
            errors.append("Repository must have at least one label")
        
        # Check for required system labels
        label_names = {label.name.lower() for label in self._labels}
        required_labels = {"bug", "enhancement"}
        missing_required = required_labels - label_names
        if missing_required:
            errors.append(f"Missing required system labels: {', '.join(missing_required)}")
        
        # Add any accumulated validation errors
        errors.extend(self._validation_errors)
        
        return errors
    
    def get_warnings(self) -> List[str]:
        """Get accumulated warnings that don't prevent building."""
        return self._warnings.copy()
    
    def get_build_summary(self) -> Dict[str, any]:
        """Get summary of current build state."""
        return {
            "repository_name": self._repo_name,
            "exported_at": self._exported_at.isoformat(),
            "counts": {
                "labels": len(self._labels),
                "issues": len(self._issues),
                "comments": len(self._comments),
                "pull_requests": len(self._pull_requests),
                "pr_comments": len(self._pr_comments),
                "sub_issues": len(self._sub_issues)
            },
            "validation_errors": len(self._validation_errors),
            "warnings": len(self._warnings),
            "is_built": self._is_built
        }
    
    def validate_and_build(self) -> RepositoryData:
        """Validate entire repository data set and return if valid."""
        # Check build requirements
        build_errors = self.validate_build_requirements()
        if build_errors:
            raise DomainValidationError(
                entity_type="RepositoryData",
                validation_error="Repository data validation failed",
                suggestions=build_errors
            )
        
        # Create the repository data
        repo_data = RepositoryData(
            repository_name=self._repo_name,
            exported_at=self._exported_at,
            labels=self._labels.copy(),
            issues=self._issues.copy(),
            comments=self._comments.copy(),
            pull_requests=self._pull_requests.copy(),
            pr_comments=self._pr_comments.copy(),
            sub_issues=self._sub_issues.copy()
        )
        
        # Final validation using repository service
        try:
            RepositoryValidationService.validate_complete_dataset(
                repo_data, 
                include_prs=bool(self._pull_requests),
                include_sub_issues=bool(self._sub_issues)
            )
        except DomainValidationError as e:
            raise DomainValidationError(
                entity_type="RepositoryData",
                validation_error="Final repository validation failed",
                suggestions=[e.validation_error] + e.suggestions
            )
        
        # Mark as built
        self._is_built = True
        
        return repo_data
    
    def build_unsafe(self) -> RepositoryData:
        """Build repository data without validation (for testing/recovery scenarios)."""
        repo_data = RepositoryData(
            repository_name=self._repo_name,
            exported_at=self._exported_at,
            labels=self._labels.copy(),
            issues=self._issues.copy(),
            comments=self._comments.copy(),
            pull_requests=self._pull_requests.copy(),
            pr_comments=self._pr_comments.copy(),
            sub_issues=self._sub_issues.copy()
        )
        
        self._is_built = True
        return repo_data
```

## Sprint 3: Specialized Builders and Integration (Week 4)

### Sprint Goal
Implement specialized builders for complex scenarios and integrate all factory/builder patterns.

### Task 3.1: Issue Hierarchy Builder (6 hours)

#### IssueHierarchyBuilder Implementation
**File:** `src/domain/builders/issue_hierarchy_builder.py`
```python
"""Builder for constructing complex issue hierarchies with validation."""

from typing import List, Dict, Optional, Set, Tuple
from ..exceptions import HierarchyError, DomainValidationError
from ..services.issue_services import IssueHierarchyService
from ..factories.issue_factory import IssueFactory
from ...models import Issue, SubIssue


class IssueHierarchyBuilder:
    """Builder for creating and validating complex issue hierarchies."""
    
    def __init__(self, root_issue: Issue):
        """Initialize with root issue."""
        self._root_issue = root_issue
        self._issue_factory = IssueFactory()
        
        # Hierarchy tracking
        self._all_issues: Dict[int, Issue] = {root_issue.number: root_issue}
        self._hierarchy_map: Dict[int, List[int]] = {root_issue.number: []}
        self._sub_issue_relationships: List[SubIssue] = []
        
        # Validation state
        self._max_depth = 8
        self._validation_errors: List[str] = []
    
    def add_sub_issue(self, parent_number: int, title: str, body: str = "", 
                     position: Optional[int] = None, **kwargs) -> 'IssueHierarchyBuilder':
        """Add sub-issue to specified parent with validation."""
        # Validate parent exists
        if parent_number not in self._all_issues:
            raise DomainValidationError(
                entity_type="IssueHierarchy",
                validation_error=f"Parent issue #{parent_number} not found in hierarchy"
            )
        
        parent_issue = self._all_issues[parent_number]
        
        # Create sub-issue
        sub_issue_number = self._generate_next_issue_number()
        sub_issue = self._issue_factory.create(
            title=title,
            body=body,
            user=parent_issue.user,  # Inherit user from parent
            **kwargs
        )
        sub_issue.number = sub_issue_number
        
        # Calculate position
        if position is None:
            existing_positions = [
                rel.position for rel in self._sub_issue_relationships 
                if rel.parent_issue_number == parent_number
            ]
            position = max(existing_positions, default=0) + 1
        
        # Validate hierarchy constraints
        self._validate_hierarchy_addition(parent_issue, sub_issue)
        
        # Add to tracking structures
        self._all_issues[sub_issue_number] = sub_issue
        self._hierarchy_map[sub_issue_number] = []
        self._hierarchy_map[parent_number].append(sub_issue_number)
        
        # Create relationship
        relationship = SubIssue(
            sub_issue_id=sub_issue.id,
            sub_issue_number=sub_issue_number,
            parent_issue_id=parent_issue.id,
            parent_issue_number=parent_number,
            position=position
        )
        self._sub_issue_relationships.append(relationship)
        
        return self
    
    def add_existing_as_sub_issue(self, parent_number: int, sub_issue: Issue, 
                                 position: Optional[int] = None) -> 'IssueHierarchyBuilder':
        """Add existing issue as sub-issue with validation."""
        # Validate parent exists
        if parent_number not in self._all_issues:
            raise DomainValidationError(
                entity_type="IssueHierarchy",
                validation_error=f"Parent issue #{parent_number} not found in hierarchy"
            )
        
        parent_issue = self._all_issues[parent_number]
        
        # Validate hierarchy constraints
        self._validate_hierarchy_addition(parent_issue, sub_issue)
        
        # Calculate position
        if position is None:
            existing_positions = [
                rel.position for rel in self._sub_issue_relationships 
                if rel.parent_issue_number == parent_number
            ]
            position = max(existing_positions, default=0) + 1
        
        # Add to tracking structures
        self._all_issues[sub_issue.number] = sub_issue
        if sub_issue.number not in self._hierarchy_map:
            self._hierarchy_map[sub_issue.number] = []
        self._hierarchy_map[parent_number].append(sub_issue.number)
        
        # Create relationship
        relationship = SubIssue(
            sub_issue_id=sub_issue.id,
            sub_issue_number=sub_issue.number,
            parent_issue_id=parent_issue.id,
            parent_issue_number=parent_number,
            position=position
        )
        self._sub_issue_relationships.append(relationship)
        
        return self
    
    def set_max_depth(self, max_depth: int) -> 'IssueHierarchyBuilder':
        """Set maximum allowed hierarchy depth."""
        if max_depth < 1 or max_depth > 8:
            raise DomainValidationError(
                entity_type="IssueHierarchy",
                validation_error=f"Max depth must be between 1 and 8, got {max_depth}"
            )
        
        self._max_depth = max_depth
        return self
    
    def reorder_sub_issues(self, parent_number: int, new_order: List[int]) -> 'IssueHierarchyBuilder':
        """Reorder sub-issues for a parent."""
        # Validate parent exists
        if parent_number not in self._all_issues:
            raise DomainValidationError(
                entity_type="IssueHierarchy",
                validation_error=f"Parent issue #{parent_number} not found"
            )
        
        # Get current sub-issues for parent
        current_subs = [
            rel for rel in self._sub_issue_relationships 
            if rel.parent_issue_number == parent_number
        ]
        
        # Validate new order contains all current sub-issues
        current_numbers = {rel.sub_issue_number for rel in current_subs}
        new_order_set = set(new_order)
        
        if current_numbers != new_order_set:
            raise DomainValidationError(
                entity_type="IssueHierarchy",
                validation_error="New order must contain exactly the same sub-issues",
                suggestions=[f"Expected: {sorted(current_numbers)}", f"Got: {sorted(new_order)}"]
            )
        
        # Update positions
        for i, sub_issue_number in enumerate(new_order):
            for rel in current_subs:
                if rel.sub_issue_number == sub_issue_number:
                    rel.position = i
                    break
        
        return self
    
    def validate_hierarchy(self) -> List[str]:
        """Validate the entire hierarchy for consistency."""
        errors = []
        
        # Check for circular dependencies
        circular_deps = IssueHierarchyService.detect_circular_dependencies(list(self._all_issues.values()))
        if circular_deps:
            errors.extend([f"Circular dependency detected: {dep}" for dep in circular_deps])
        
        # Check depth constraints
        for issue in self._all_issues.values():
            depth = self._calculate_issue_depth(issue.number)
            if depth > self._max_depth:
                errors.append(f"Issue #{issue.number} depth ({depth}) exceeds maximum ({self._max_depth})")
        
        # Check position consistency
        for parent_number in self._hierarchy_map:
            sub_relationships = [
                rel for rel in self._sub_issue_relationships 
                if rel.parent_issue_number == parent_number
            ]
            
            positions = [rel.position for rel in sub_relationships]
            if len(positions) != len(set(positions)):
                errors.append(f"Duplicate positions in parent #{parent_number}")
            
            if positions and (min(positions) < 0 or max(positions) >= len(positions)):
                errors.append(f"Invalid position values in parent #{parent_number}")
        
        return errors
    
    def get_hierarchy_summary(self) -> Dict[str, any]:
        """Get summary of the current hierarchy."""
        metrics = IssueHierarchyService.get_hierarchy_metrics(list(self._all_issues.values()))
        
        return {
            **metrics,
            "root_issue": self._root_issue.number,
            "relationships": len(self._sub_issue_relationships),
            "validation_errors": len(self.validate_hierarchy())
        }
    
    def build(self) -> Tuple[List[Issue], List[SubIssue]]:
        """Build and return the complete hierarchy."""
        # Final validation
        validation_errors = self.validate_hierarchy()
        if validation_errors:
            raise DomainValidationError(
                entity_type="IssueHierarchy",
                validation_error="Hierarchy validation failed",
                suggestions=validation_errors
            )
        
        # Update issue sub_issues fields
        for issue in self._all_issues.values():
            issue_subs = [
                rel for rel in self._sub_issue_relationships 
                if rel.parent_issue_number == issue.number
            ]
            issue.sub_issues = sorted(issue_subs, key=lambda x: x.position)
        
        return list(self._all_issues.values()), self._sub_issue_relationships.copy()
    
    def _validate_hierarchy_addition(self, parent: Issue, sub_issue: Issue) -> None:
        """Validate that adding sub-issue to parent is allowed."""
        # Check if parent can accept sub-issues
        if not parent.can_accept_sub_issues():  # From Phase 1
            raise HierarchyError(
                operation="add_sub_issue",
                issue_number=parent.number,
                constraint=f"Parent issue in state '{parent.state}' cannot accept sub-issues"
            )
        
        # Check depth constraints
        parent_depth = self._calculate_issue_depth(parent.number)
        sub_depth = self._calculate_sub_tree_depth(sub_issue.number)
        total_depth = parent_depth + 1 + sub_depth
        
        if total_depth > self._max_depth:
            raise HierarchyError(
                operation="add_sub_issue",
                issue_number=parent.number,
                constraint=f"Would exceed maximum depth of {self._max_depth}",
                current_depth=total_depth,
                max_depth=self._max_depth
            )
        
        # Check for circular reference
        if self._would_create_cycle(parent.number, sub_issue.number):
            raise HierarchyError(
                operation="add_sub_issue",
                issue_number=parent.number,
                constraint=f"Would create circular dependency with issue #{sub_issue.number}"
            )
    
    def _calculate_issue_depth(self, issue_number: int) -> int:
        """Calculate depth of issue in hierarchy."""
        return IssueHierarchyService._calculate_depth(issue_number, self._hierarchy_map)
    
    def _calculate_sub_tree_depth(self, issue_number: int) -> int:
        """Calculate depth of sub-tree rooted at issue."""
        return IssueHierarchyService._calculate_sub_tree_depth(issue_number, self._hierarchy_map)
    
    def _would_create_cycle(self, parent_number: int, sub_issue_number: int) -> bool:
        """Check if adding relationship would create cycle."""
        # Simple check: is parent a descendant of sub_issue?
        def is_descendant(ancestor: int, descendant: int, visited: Set[int] = None) -> bool:
            if visited is None:
                visited = set()
            
            if ancestor in visited:
                return False
            
            visited.add(ancestor)
            children = self._hierarchy_map.get(ancestor, [])
            
            if descendant in children:
                return True
            
            return any(is_descendant(child, descendant, visited.copy()) for child in children)
        
        return is_descendant(sub_issue_number, parent_number)
    
    def _generate_next_issue_number(self) -> int:
        """Generate next available issue number."""
        existing_numbers = set(self._all_issues.keys())
        next_number = max(existing_numbers) + 1
        
        while next_number in existing_numbers:
            next_number += 1
        
        return next_number
```

## Integration Testing and Usage Examples

### Test Coverage Requirements
- **Factory Tests**: 95%+ coverage for all creation paths
- **Builder Tests**: 90%+ coverage for fluent interface usage
- **Integration Tests**: All factory/builder combinations tested
- **Error Handling**: All validation paths tested

### Usage Examples

#### Example 1: Building Repository Data
```python
from src.domain.builders.repository_data_builder import RepositoryDataBuilder
from src.domain.factories.label_factory import LabelFactory
from src.domain.factories.issue_factory import IssueFactory

# Create repository data using builder pattern
builder = RepositoryDataBuilder("my-repo")

# Add standard labels using factory
label_factory = LabelFactory()
standard_labels = label_factory.create_standard_set()
builder.add_labels(standard_labels)

# Create issues using factory
issue_factory = IssueFactory()
issue1 = issue_factory.create("Bug in authentication", "Users cannot login")
issue2 = issue_factory.create("Add dark mode", "Implement dark theme")

builder.add_issues([issue1, issue2])

# Build with validation
repo_data = builder.validate_and_build()
```

#### Example 2: Creating Issue Hierarchy
```python
from src.domain.builders.issue_hierarchy_builder import IssueHierarchyBuilder
from src.domain.factories.issue_factory import IssueFactory

# Create root issue
factory = IssueFactory()
root_issue = factory.create("Epic: User Management", "Complete user management system")

# Build hierarchy
hierarchy_builder = IssueHierarchyBuilder(root_issue)

# Add sub-issues
hierarchy_builder.add_sub_issue(
    root_issue.number, 
    "Implement user registration", 
    "Add user registration form and backend"
)

hierarchy_builder.add_sub_issue(
    root_issue.number,
    "Add password reset",
    "Implement forgot password functionality"
)

# Build hierarchy
issues, relationships = hierarchy_builder.build()
```

## Success Criteria

### Phase 4 Completion Definition
- [ ] All entity factories implemented with validation
- [ ] Builder patterns for complex object creation
- [ ] Integration with existing operations layer
- [ ] Comprehensive test suite for all patterns
- [ ] Performance benchmarks meet targets
- [ ] Documentation with usage examples
- [ ] Migration guide from manual object creation

### Quality Gates
1. **Factory Coverage**: All entities can be created through factories
2. **Validation**: No invalid entities can be created
3. **Builder Fluency**: Complex objects built with readable interfaces
4. **Integration**: Seamless integration with operations
5. **Performance**: Object creation performance within targets

This comprehensive factory and builder implementation provides clean, validated object creation throughout the system while maintaining performance and usability.