# Phase 5: Error Handling Enhancement - Detailed Implementation Plan

**Phase:** 5 of 5  
**Duration:** 2 sprints (3-4 weeks)  
**Priority:** Medium - Improves user experience and debugging  
**Dependencies:** Phase 1-4 completion (all domain infrastructure required)

## Executive Summary

This final phase creates a comprehensive, user-friendly error handling system that provides clear diagnostics, helpful suggestions, and consistent error messages across all domain operations. The enhanced error handling improves both developer experience and end-user troubleshooting.

## Error Handling Strategy

### Core Principles
- **User-Friendly Messages**: Clear, actionable error messages
- **Contextual Information**: Rich error context for debugging
- **Consistent Formatting**: Standardized error presentation
- **Progressive Disclosure**: Basic message + detailed information available
- **Recovery Suggestions**: Practical steps to resolve issues

### Error Categories
1. **Validation Errors**: Business rule violations
2. **State Transition Errors**: Invalid entity state changes
3. **Conflict Errors**: Entity conflicts during operations
4. **Hierarchy Errors**: Sub-issue relationship violations
5. **System Errors**: Infrastructure and external service failures

### Error Handling Architecture
```
src/domain/
├── exceptions/
│   ├── __init__.py
│   ├── base.py                   # Base exception classes
│   ├── validation.py             # Validation-specific exceptions
│   ├── state.py                  # State transition exceptions
│   ├── conflict.py               # Conflict resolution exceptions
│   ├── hierarchy.py              # Hierarchy-specific exceptions
│   └── system.py                 # System and infrastructure errors
├── error_handling/
│   ├── __init__.py
│   ├── error_formatter.py        # Error message formatting
│   ├── error_aggregator.py       # Multiple error collection
│   ├── recovery_suggestions.py   # Recovery guidance system
│   └── error_reporter.py         # Error reporting and logging
└── diagnostics/
    ├── __init__.py
    ├── entity_diagnostics.py     # Entity validation diagnostics
    ├── operation_diagnostics.py  # Operation failure analysis
    └── system_health.py          # System health checks
```

## Sprint 1: Enhanced Exception Hierarchy (Week 1-2)

### Sprint Goal
Create comprehensive exception hierarchy with rich error information and user-friendly messaging.

### Task 1.1: Base Exception Infrastructure (6 hours)

#### Enhanced Base Exception Classes
**File:** `src/domain/exceptions/base.py`
```python
"""Base exception classes for domain errors with rich context."""

from abc import ABC
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import traceback
import uuid


class DomainErrorContext:
    """Rich context information for domain errors."""
    
    def __init__(self, operation: str, entity_type: str = None, entity_id: Union[str, int] = None,
                 timestamp: datetime = None, correlation_id: str = None):
        self.operation = operation
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.timestamp = timestamp or datetime.now()
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.additional_context: Dict[str, Any] = {}
    
    def add_context(self, key: str, value: Any) -> None:
        """Add additional context information."""
        self.additional_context[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for serialization."""
        return {
            "operation": self.operation,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "additional_context": self.additional_context
        }


class BaseDomainError(Exception, ABC):
    """Base class for all domain errors with rich context and user-friendly messaging."""
    
    def __init__(self, message: str, context: DomainErrorContext = None, 
                 user_message: str = None, suggestions: List[str] = None,
                 error_code: str = None, severity: str = "error"):
        self.message = message
        self.user_message = user_message or message
        self.suggestions = suggestions or []
        self.error_code = error_code
        self.severity = severity  # "error", "warning", "info"
        self.context = context
        self.caused_by: Optional[Exception] = None
        self.stack_trace = traceback.format_stack()
        
        super().__init__(self.message)
    
    def add_suggestion(self, suggestion: str) -> 'BaseDomainError':
        """Add recovery suggestion."""
        self.suggestions.append(suggestion)
        return self
    
    def set_user_message(self, message: str) -> 'BaseDomainError':
        """Set user-friendly message."""
        self.user_message = message
        return self
    
    def set_caused_by(self, exception: Exception) -> 'BaseDomainError':
        """Set the underlying cause."""
        self.caused_by = exception
        return self
    
    def get_full_message(self) -> str:
        """Get complete error message with context."""
        parts = [self.user_message]
        
        if self.suggestions:
            parts.append(f"Suggestions: {'; '.join(self.suggestions)}")
        
        if self.context:
            parts.append(f"Operation: {self.context.operation}")
            if self.context.entity_type:
                parts.append(f"Entity: {self.context.entity_type}")
        
        if self.error_code:
            parts.append(f"Code: {self.error_code}")
        
        return " | ".join(parts)
    
    def get_diagnostic_info(self) -> Dict[str, Any]:
        """Get comprehensive diagnostic information."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "severity": self.severity,
            "message": self.message,
            "user_message": self.user_message,
            "suggestions": self.suggestions,
            "context": self.context.to_dict() if self.context else None,
            "caused_by": str(self.caused_by) if self.caused_by else None,
            "timestamp": datetime.now().isoformat()
        }
    
    def to_user_friendly_dict(self) -> Dict[str, Any]:
        """Convert to user-friendly dictionary for CLI output."""
        result = {
            "error": self.user_message,
            "type": self.__class__.__name__.replace("Error", "").lower()
        }
        
        if self.suggestions:
            result["suggestions"] = self.suggestions
        
        if self.context and self.context.entity_type:
            result["entity"] = self.context.entity_type
            if self.context.entity_id:
                result["entity_id"] = self.context.entity_id
        
        if self.error_code:
            result["code"] = self.error_code
        
        return result


class DomainError(BaseDomainError):
    """General domain error for business rule violations."""
    pass


class ValidationError(BaseDomainError):
    """Error for validation failures with detailed field information."""
    
    def __init__(self, entity_type: str, validation_failures: Dict[str, List[str]], 
                 context: DomainErrorContext = None, **kwargs):
        self.entity_type = entity_type
        self.validation_failures = validation_failures
        
        # Create comprehensive message
        failure_count = sum(len(errors) for errors in validation_failures.values())
        message = f"{entity_type} validation failed: {failure_count} error(s) found"
        
        # Create user-friendly message
        user_message = f"Invalid {entity_type.lower()}: "
        field_summaries = []
        for field, errors in validation_failures.items():
            if len(errors) == 1:
                field_summaries.append(f"{field} {errors[0]}")
            else:
                field_summaries.append(f"{field} has {len(errors)} issues")
        user_message += "; ".join(field_summaries)
        
        # Generate suggestions
        suggestions = []
        for field, errors in validation_failures.items():
            for error in errors:
                if "empty" in error.lower():
                    suggestions.append(f"Provide a value for {field}")
                elif "too long" in error.lower():
                    suggestions.append(f"Shorten {field} content")
                elif "invalid" in error.lower():
                    suggestions.append(f"Check {field} format")
        
        super().__init__(
            message=message,
            context=context,
            user_message=user_message,
            suggestions=suggestions[:5],  # Limit to 5 most important
            error_code="VALIDATION_FAILED",
            **kwargs
        )
    
    def get_field_errors(self, field: str) -> List[str]:
        """Get validation errors for specific field."""
        return self.validation_failures.get(field, [])
    
    def has_field_error(self, field: str) -> bool:
        """Check if field has validation errors."""
        return field in self.validation_failures and bool(self.validation_failures[field])
    
    def get_error_summary(self) -> Dict[str, int]:
        """Get summary of validation errors by field."""
        return {field: len(errors) for field, errors in self.validation_failures.items()}
```

### Task 1.2: Specialized Exception Classes (8 hours)

#### State Transition Error Enhancement
**File:** `src/domain/exceptions/state.py`
```python
"""State transition and lifecycle errors."""

from typing import List, Dict, Any, Optional
from .base import BaseDomainError, DomainErrorContext


class StateTransitionError(BaseDomainError):
    """Enhanced error for invalid state transitions with guidance."""
    
    def __init__(self, entity_type: str, entity_id: Union[str, int], 
                 current_state: str, attempted_state: str,
                 allowed_transitions: List[str] = None,
                 transition_rules: Dict[str, str] = None,
                 context: DomainErrorContext = None):
        
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.current_state = current_state
        self.attempted_state = attempted_state
        self.allowed_transitions = allowed_transitions or []
        self.transition_rules = transition_rules or {}
        
        # Create descriptive message
        message = f"{entity_type} #{entity_id} cannot transition from '{current_state}' to '{attempted_state}'"
        
        # Create user-friendly message
        user_message = f"Cannot change {entity_type.lower()} state to '{attempted_state}'"
        if current_state:
            user_message += f" (currently '{current_state}')"
        
        # Generate suggestions
        suggestions = []
        if self.allowed_transitions:
            valid_states = ", ".join(f"'{state}'" for state in self.allowed_transitions)
            suggestions.append(f"Valid transitions from '{current_state}': {valid_states}")
        
        for state, rule in self.transition_rules.items():
            if state == attempted_state:
                suggestions.append(f"To transition to '{state}': {rule}")
        
        # Add general guidance
        if current_state == "closed" and attempted_state in ["open", "reopen"]:
            suggestions.append("Use reopen() method instead of changing state directly")
        elif current_state == "open" and attempted_state == "closed":
            suggestions.append("Use close() method with optional reason")
        
        super().__init__(
            message=message,
            context=context,
            user_message=user_message,
            suggestions=suggestions,
            error_code="INVALID_STATE_TRANSITION"
        )
    
    def get_transition_guidance(self) -> Dict[str, Any]:
        """Get detailed guidance for valid transitions."""
        return {
            "current_state": self.current_state,
            "attempted_state": self.attempted_state,
            "allowed_transitions": self.allowed_transitions,
            "transition_rules": self.transition_rules,
            "suggested_actions": self.suggestions
        }


class LifecycleError(BaseDomainError):
    """Error for entity lifecycle violations."""
    
    def __init__(self, entity_type: str, entity_id: Union[str, int],
                 operation: str, lifecycle_stage: str,
                 required_stage: str = None,
                 context: DomainErrorContext = None):
        
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.operation = operation
        self.lifecycle_stage = lifecycle_stage
        self.required_stage = required_stage
        
        message = f"Cannot perform '{operation}' on {entity_type} #{entity_id} in '{lifecycle_stage}' stage"
        if required_stage:
            message += f" (requires '{required_stage}' stage)"
        
        user_message = f"Operation '{operation}' not allowed for {entity_type.lower()} in current state"
        
        suggestions = []
        if required_stage:
            suggestions.append(f"Entity must be in '{required_stage}' stage for this operation")
        
        # Add stage-specific guidance
        if lifecycle_stage == "draft" and operation in ["merge", "close"]:
            suggestions.append("Convert from draft to ready-for-review first")
        elif lifecycle_stage == "closed" and operation in ["edit", "assign"]:
            suggestions.append("Reopen the item before making changes")
        
        super().__init__(
            message=message,
            context=context,
            user_message=user_message,
            suggestions=suggestions,
            error_code="LIFECYCLE_VIOLATION"
        )
```

#### Conflict Error Enhancement
**File:** `src/domain/exceptions/conflict.py`
```python
"""Conflict detection and resolution errors."""

from typing import List, Dict, Any, Optional, Union
from .base import BaseDomainError, DomainErrorContext


class ConflictError(BaseDomainError):
    """Enhanced error for entity conflicts with resolution strategies."""
    
    def __init__(self, conflict_type: str, conflicting_entities: List[str],
                 resolution_strategies: List[str] = None,
                 conflict_details: Dict[str, Any] = None,
                 context: DomainErrorContext = None):
        
        self.conflict_type = conflict_type
        self.conflicting_entities = conflicting_entities
        self.resolution_strategies = resolution_strategies or []
        self.conflict_details = conflict_details or {}
        
        # Create descriptive message
        entity_list = ", ".join(conflicting_entities[:3])
        if len(conflicting_entities) > 3:
            entity_list += f" and {len(conflicting_entities) - 3} more"
        
        message = f"{conflict_type.replace('_', ' ').title()} conflict detected: {entity_list}"
        
        # Create user-friendly message
        user_message = f"Conflict found: {conflict_type.replace('_', ' ')}"
        if len(conflicting_entities) == 1:
            user_message += f" with {conflicting_entities[0]}"
        else:
            user_message += f" involving {len(conflicting_entities)} items"
        
        # Generate suggestions from resolution strategies
        suggestions = []
        for strategy in self.resolution_strategies:
            suggestions.append(self._format_resolution_strategy(strategy))
        
        # Add conflict-specific suggestions
        if conflict_type == "label_name":
            suggestions.append("Rename one of the conflicting labels")
            suggestions.append("Use --conflict-strategy=overwrite to replace existing")
        elif conflict_type == "issue_number":
            suggestions.append("Use automatic number remapping")
            suggestions.append("Manually resolve number conflicts before import")
        elif conflict_type == "hierarchy_circular":
            suggestions.append("Remove circular sub-issue relationships")
            suggestions.append("Restructure issue hierarchy")
        
        super().__init__(
            message=message,
            context=context,
            user_message=user_message,
            suggestions=suggestions[:5],
            error_code=f"CONFLICT_{conflict_type.upper()}"
        )
    
    def get_resolution_options(self) -> Dict[str, str]:
        """Get available resolution options with descriptions."""
        options = {}
        for strategy in self.resolution_strategies:
            options[strategy] = self._get_strategy_description(strategy)
        return options
    
    def get_conflict_analysis(self) -> Dict[str, Any]:
        """Get detailed conflict analysis."""
        return {
            "type": self.conflict_type,
            "affected_entities": self.conflicting_entities,
            "conflict_count": len(self.conflicting_entities),
            "resolution_options": self.get_resolution_options(),
            "details": self.conflict_details
        }
    
    def _format_resolution_strategy(self, strategy: str) -> str:
        """Format resolution strategy as user-friendly suggestion."""
        strategy_formats = {
            "fail_if_existing": "Operation will fail if conflicts exist",
            "fail_if_conflict": "Operation will fail on any conflicts",
            "overwrite": "Replace existing items with new ones",
            "skip": "Skip conflicting items and continue",
            "merge": "Attempt to merge conflicting items",
            "rename": "Automatically rename conflicting items"
        }
        return strategy_formats.get(strategy, f"Use strategy: {strategy}")
    
    def _get_strategy_description(self, strategy: str) -> str:
        """Get detailed description of resolution strategy."""
        descriptions = {
            "fail_if_existing": "Stop operation if any existing items would conflict",
            "fail_if_conflict": "Stop operation only if actual conflicts detected",
            "overwrite": "Replace all existing items with imported versions",
            "skip": "Skip items that would conflict, import others",
            "merge": "Combine conflicting items using merge rules",
            "rename": "Automatically rename conflicting items"
        }
        return descriptions.get(strategy, "Custom resolution strategy")


class DataIntegrityError(BaseDomainError):
    """Error for data integrity violations."""
    
    def __init__(self, integrity_type: str, affected_entities: List[str],
                 integrity_details: Dict[str, Any] = None,
                 context: DomainErrorContext = None):
        
        self.integrity_type = integrity_type
        self.affected_entities = affected_entities
        self.integrity_details = integrity_details or {}
        
        message = f"Data integrity violation: {integrity_type}"
        user_message = f"Data integrity issue detected: {integrity_type.replace('_', ' ')}"
        
        suggestions = []
        if integrity_type == "orphaned_comments":
            suggestions.append("Remove comments that reference non-existent issues")
            suggestions.append("Create missing issues before importing comments")
        elif integrity_type == "missing_labels":
            suggestions.append("Create referenced labels before importing issues")
            suggestions.append("Remove label references from issues")
        elif integrity_type == "broken_hierarchy":
            suggestions.append("Fix sub-issue parent-child relationships")
            suggestions.append("Remove invalid hierarchy references")
        
        super().__init__(
            message=message,
            context=context,
            user_message=user_message,
            suggestions=suggestions,
            error_code=f"INTEGRITY_{integrity_type.upper()}"
        )
```

#### Hierarchy Error Enhancement
**File:** `src/domain/exceptions/hierarchy.py`
```python
"""Hierarchy-specific errors with detailed guidance."""

from typing import List, Dict, Any, Optional
from .base import BaseDomainError, DomainErrorContext


class HierarchyError(BaseDomainError):
    """Enhanced error for hierarchy constraint violations."""
    
    def __init__(self, operation: str, issue_number: int, constraint: str,
                 current_depth: int = None, max_depth: int = None,
                 hierarchy_path: List[int] = None,
                 context: DomainErrorContext = None):
        
        self.operation = operation
        self.issue_number = issue_number
        self.constraint = constraint
        self.current_depth = current_depth
        self.max_depth = max_depth
        self.hierarchy_path = hierarchy_path or []
        
        message = f"Hierarchy constraint violated for issue #{issue_number}: {constraint}"
        if current_depth is not None and max_depth is not None:
            message += f" (depth: {current_depth}, max: {max_depth})"
        
        user_message = f"Cannot {operation.replace('_', ' ')} issue #{issue_number}: {constraint.lower()}"
        
        suggestions = []
        
        # Depth-specific suggestions
        if current_depth and max_depth and current_depth > max_depth:
            suggestions.append(f"Reduce hierarchy depth to {max_depth} levels or less")
            suggestions.append("Move some sub-issues to higher levels in the hierarchy")
            if self.hierarchy_path:
                path_str = " → ".join(map(str, self.hierarchy_path))
                suggestions.append(f"Current path: {path_str}")
        
        # Operation-specific suggestions
        if operation == "add_sub_issue":
            suggestions.append("Create sub-issue at a higher level in the hierarchy")
            suggestions.append("Remove some intermediate levels")
        elif operation == "create_hierarchy":
            suggestions.append("Simplify the hierarchy structure")
            suggestions.append("Break large hierarchies into separate trees")
        
        # Constraint-specific suggestions
        if "circular" in constraint.lower():
            suggestions.append("Remove circular references in sub-issue relationships")
            suggestions.append("Check for issues that reference themselves as sub-issues")
        elif "closed" in constraint.lower():
            suggestions.append("Reopen parent issue before adding sub-issues")
            suggestions.append("Add sub-issues to open issues only")
        
        super().__init__(
            message=message,
            context=context,
            user_message=user_message,
            suggestions=suggestions,
            error_code="HIERARCHY_CONSTRAINT_VIOLATED"
        )
    
    def get_hierarchy_analysis(self) -> Dict[str, Any]:
        """Get detailed hierarchy analysis."""
        return {
            "operation": self.operation,
            "affected_issue": self.issue_number,
            "constraint_violated": self.constraint,
            "current_depth": self.current_depth,
            "max_allowed_depth": self.max_depth,
            "hierarchy_path": self.hierarchy_path,
            "suggested_actions": self.suggestions
        }


class CircularDependencyError(HierarchyError):
    """Specific error for circular dependency detection."""
    
    def __init__(self, cycle_path: List[int], context: DomainErrorContext = None):
        self.cycle_path = cycle_path
        
        cycle_str = " → ".join(map(str, cycle_path))
        constraint = f"Circular dependency detected: {cycle_str}"
        
        super().__init__(
            operation="validate_hierarchy",
            issue_number=cycle_path[0] if cycle_path else 0,
            constraint=constraint,
            hierarchy_path=cycle_path,
            context=context
        )
        
        # Override suggestions for circular dependency
        self.suggestions = [
            f"Break the cycle by removing one of these relationships: {cycle_str}",
            "Ensure parent-child relationships flow in one direction only",
            "Check for issues that indirectly reference themselves"
        ]
        
        self.error_code = "CIRCULAR_DEPENDENCY"
    
    def get_cycle_analysis(self) -> Dict[str, Any]:
        """Get analysis of the circular dependency."""
        return {
            "cycle_path": self.cycle_path,
            "cycle_length": len(self.cycle_path),
            "break_points": [
                f"Remove {self.cycle_path[i]} → {self.cycle_path[(i+1) % len(self.cycle_path)]}"
                for i in range(len(self.cycle_path))
            ]
        }
```

## Sprint 2: Error Formatting and Recovery System (Week 3)

### Sprint Goal
Implement comprehensive error formatting, recovery suggestions, and user-friendly error reporting.

### Task 2.1: Error Formatter Implementation (6 hours)

#### Error Formatting System
**File:** `src/domain/error_handling/error_formatter.py`
```python
"""Error formatting system for consistent, user-friendly error presentation."""

from typing import Dict, Any, List, Optional, Union
from enum import Enum
import json
from ..exceptions.base import BaseDomainError


class ErrorFormat(Enum):
    """Available error formatting options."""
    SIMPLE = "simple"           # Basic message only
    DETAILED = "detailed"       # Message + suggestions + context
    JSON = "json"              # JSON format for API/scripting
    PRETTY = "pretty"          # Formatted for terminal display
    DIAGNOSTIC = "diagnostic"   # Full diagnostic information


class ErrorFormatter:
    """Formats domain errors for different output contexts."""
    
    def __init__(self, default_format: ErrorFormat = ErrorFormat.PRETTY):
        self.default_format = default_format
        self.color_enabled = True
        self.show_error_codes = True
        self.max_suggestions = 5
    
    def format_error(self, error: BaseDomainError, 
                    format_type: ErrorFormat = None) -> str:
        """Format error according to specified format."""
        format_type = format_type or self.default_format
        
        if format_type == ErrorFormat.SIMPLE:
            return self._format_simple(error)
        elif format_type == ErrorFormat.DETAILED:
            return self._format_detailed(error)
        elif format_type == ErrorFormat.JSON:
            return self._format_json(error)
        elif format_type == ErrorFormat.PRETTY:
            return self._format_pretty(error)
        elif format_type == ErrorFormat.DIAGNOSTIC:
            return self._format_diagnostic(error)
        else:
            return str(error)
    
    def format_multiple_errors(self, errors: List[BaseDomainError],
                             format_type: ErrorFormat = None) -> str:
        """Format multiple errors with summary."""
        if not errors:
            return "No errors to display"
        
        format_type = format_type or self.default_format
        
        if len(errors) == 1:
            return self.format_error(errors[0], format_type)
        
        # Multiple errors - add summary
        summary = self._create_error_summary(errors)
        formatted_errors = [self.format_error(error, format_type) for error in errors]
        
        if format_type == ErrorFormat.JSON:
            return json.dumps({
                "summary": summary,
                "errors": [error.to_user_friendly_dict() for error in errors]
            }, indent=2)
        else:
            result = [self._format_summary(summary)]
            result.extend(formatted_errors)
            return "\n\n".join(result)
    
    def _format_simple(self, error: BaseDomainError) -> str:
        """Simple format: just the user message."""
        return error.user_message
    
    def _format_detailed(self, error: BaseDomainError) -> str:
        """Detailed format: message + context + suggestions."""
        lines = [f"Error: {error.user_message}"]
        
        if error.context:
            if error.context.entity_type:
                lines.append(f"Entity: {error.context.entity_type}")
            if error.context.operation:
                lines.append(f"Operation: {error.context.operation}")
        
        if error.suggestions:
            lines.append("Suggestions:")
            for i, suggestion in enumerate(error.suggestions[:self.max_suggestions], 1):
                lines.append(f"  {i}. {suggestion}")
        
        if self.show_error_codes and error.error_code:
            lines.append(f"Error Code: {error.error_code}")
        
        return "\n".join(lines)
    
    def _format_json(self, error: BaseDomainError) -> str:
        """JSON format for API/scripting use."""
        return json.dumps(error.to_user_friendly_dict(), indent=2)
    
    def _format_pretty(self, error: BaseDomainError) -> str:
        """Pretty format for terminal display with colors and symbols."""
        lines = []
        
        # Error header with icon
        severity_icon = self._get_severity_icon(error.severity)
        error_line = f"{severity_icon} {error.user_message}"
        if self.color_enabled:
            error_line = self._colorize(error_line, self._get_severity_color(error.severity))
        lines.append(error_line)
        
        # Context information
        if error.context:
            context_parts = []
            if error.context.entity_type:
                entity_info = error.context.entity_type
                if error.context.entity_id:
                    entity_info += f" #{error.context.entity_id}"
                context_parts.append(entity_info)
            
            if error.context.operation:
                context_parts.append(f"during {error.context.operation}")
            
            if context_parts:
                context_line = f"  └─ {' '.join(context_parts)}"
                if self.color_enabled:
                    context_line = self._colorize(context_line, "dim")
                lines.append(context_line)
        
        # Suggestions
        if error.suggestions:
            lines.append("")
            suggestions_header = "💡 Suggestions:"
            if self.color_enabled:
                suggestions_header = self._colorize(suggestions_header, "blue")
            lines.append(suggestions_header)
            
            for i, suggestion in enumerate(error.suggestions[:self.max_suggestions], 1):
                suggestion_line = f"  {i}. {suggestion}"
                if self.color_enabled:
                    suggestion_line = self._colorize(suggestion_line, "cyan")
                lines.append(suggestion_line)
        
        # Error code
        if self.show_error_codes and error.error_code:
            code_line = f"Code: {error.error_code}"
            if self.color_enabled:
                code_line = self._colorize(code_line, "dim")
            lines.append("")
            lines.append(code_line)
        
        return "\n".join(lines)
    
    def _format_diagnostic(self, error: BaseDomainError) -> str:
        """Full diagnostic format with all available information."""
        diagnostic_info = error.get_diagnostic_info()
        return json.dumps(diagnostic_info, indent=2, default=str)
    
    def _create_error_summary(self, errors: List[BaseDomainError]) -> Dict[str, Any]:
        """Create summary of multiple errors."""
        error_types = {}
        severities = {}
        
        for error in errors:
            error_type = error.__class__.__name__
            error_types[error_type] = error_types.get(error_type, 0) + 1
            severities[error.severity] = severities.get(error.severity, 0) + 1
        
        return {
            "total_errors": len(errors),
            "error_types": error_types,
            "severities": severities,
            "most_common": max(error_types.items(), key=lambda x: x[1]) if error_types else None
        }
    
    def _format_summary(self, summary: Dict[str, Any]) -> str:
        """Format error summary for display."""
        lines = [f"🚨 {summary['total_errors']} errors found"]
        
        if summary.get("most_common"):
            error_type, count = summary["most_common"]
            lines.append(f"Most common: {error_type} ({count} occurrences)")
        
        return "\n".join(lines)
    
    def _get_severity_icon(self, severity: str) -> str:
        """Get icon for error severity."""
        icons = {
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        return icons.get(severity, "❓")
    
    def _get_severity_color(self, severity: str) -> str:
        """Get color for error severity."""
        colors = {
            "error": "red",
            "warning": "yellow",
            "info": "blue"
        }
        return colors.get(severity, "white")
    
    def _colorize(self, text: str, color: str) -> str:
        """Add color to text (placeholder for actual color implementation)."""
        # In real implementation, would use colorama or similar
        return text
```

### Task 2.2: Recovery Suggestion System (6 hours)

#### Recovery Guidance System
**File:** `src/domain/error_handling/recovery_suggestions.py`
```python
"""Intelligent recovery suggestion system."""

from typing import List, Dict, Any, Optional, Callable
from ..exceptions.base import BaseDomainError
from ..exceptions.validation import ValidationError
from ..exceptions.state import StateTransitionError
from ..exceptions.conflict import ConflictError
from ..exceptions.hierarchy import HierarchyError


class RecoverySuggestionEngine:
    """Intelligent system for generating contextual recovery suggestions."""
    
    def __init__(self):
        self.suggestion_providers: Dict[type, Callable] = {
            ValidationError: self._suggest_validation_recovery,
            StateTransitionError: self._suggest_state_recovery,
            ConflictError: self._suggest_conflict_recovery,
            HierarchyError: self._suggest_hierarchy_recovery
        }
        
        self.common_solutions = {
            "empty_field": "Provide a value for the required field",
            "invalid_format": "Check the format and try again",
            "permission_denied": "Ensure you have the necessary permissions",
            "not_found": "Verify the item exists and try again"
        }
    
    def generate_suggestions(self, error: BaseDomainError) -> List[str]:
        """Generate contextual recovery suggestions for an error."""
        suggestions = []
        
        # Add existing suggestions from error
        suggestions.extend(error.suggestions)
        
        # Generate type-specific suggestions
        error_type = type(error)
        if error_type in self.suggestion_providers:
            type_suggestions = self.suggestion_providers[error_type](error)
            suggestions.extend(type_suggestions)
        
        # Add context-aware suggestions
        context_suggestions = self._suggest_from_context(error)
        suggestions.extend(context_suggestions)
        
        # Add operation-specific suggestions
        if error.context and error.context.operation:
            operation_suggestions = self._suggest_for_operation(error.context.operation, error)
            suggestions.extend(operation_suggestions)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in seen:
                seen.add(suggestion)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions[:8]  # Limit to most relevant suggestions
    
    def _suggest_validation_recovery(self, error: ValidationError) -> List[str]:
        """Generate suggestions for validation errors."""
        suggestions = []
        
        for field, errors in error.validation_failures.items():
            for field_error in errors:
                if "empty" in field_error.lower() or "required" in field_error.lower():
                    suggestions.append(f"Provide a valid value for {field}")
                elif "too long" in field_error.lower():
                    # Extract length if possible
                    words = field_error.split()
                    max_length = None
                    for word in words:
                        if word.isdigit():
                            max_length = word
                            break
                    if max_length:
                        suggestions.append(f"Limit {field} to {max_length} characters or less")
                    else:
                        suggestions.append(f"Reduce the length of {field}")
                elif "invalid" in field_error.lower():
                    if field.lower() in ["email", "url", "color", "hex"]:
                        suggestions.append(f"Check {field} format (examples: user@domain.com, #FF0000)")
                    else:
                        suggestions.append(f"Check {field} format and ensure it meets requirements")
        
        # Add general validation suggestions
        suggestions.append("Use validation methods on entities before operations")
        suggestions.append("Check input data against business rules")
        
        return suggestions
    
    def _suggest_state_recovery(self, error: StateTransitionError) -> List[str]:
        """Generate suggestions for state transition errors."""
        suggestions = []
        
        current = error.current_state.lower()
        attempted = error.attempted_state.lower()
        
        # Common state transition patterns
        if current == "closed" and attempted in ["open", "reopen"]:
            suggestions.append(f"Use the reopen() method instead of setting state directly")
            suggestions.append("Check if the item can be reopened (business rules may prevent it)")
        
        elif current == "open" and attempted == "closed":
            suggestions.append("Use the close() method with an optional reason")
            suggestions.append("Ensure all requirements for closing are met")
        
        elif current == "draft" and attempted in ["open", "published"]:
            suggestions.append("Complete all required fields before publishing")
            suggestions.append("Use the publish() or ready_for_review() method")
        
        # Add valid transitions if available
        if error.allowed_transitions:
            valid_states = "', '".join(error.allowed_transitions)
            suggestions.append(f"Valid states from '{current}': '{valid_states}'")
        
        # Entity-specific suggestions
        if error.entity_type.lower() == "issue":
            suggestions.append("Issues can only be 'open' or 'closed'")
            if current == "closed":
                suggestions.append("Closed issues require a close reason and timestamp")
        
        elif error.entity_type.lower() == "pullrequest":
            suggestions.append("Pull requests can be 'open', 'closed', or 'merged'")
            if attempted == "merged":
                suggestions.append("Ensure PR meets merge requirements before merging")
        
        return suggestions
    
    def _suggest_conflict_recovery(self, error: ConflictError) -> List[str]:
        """Generate suggestions for conflict errors."""
        suggestions = []
        
        conflict_type = error.conflict_type.lower()
        
        if "label" in conflict_type:
            suggestions.append("Rename conflicting labels to unique names")
            suggestions.append("Use --conflict-strategy=overwrite to replace existing labels")
            suggestions.append("Use --conflict-strategy=skip to skip conflicting labels")
            suggestions.append("Merge similar labels manually before import")
        
        elif "issue" in conflict_type:
            suggestions.append("Use automatic issue number remapping")
            suggestions.append("Manually resolve issue number conflicts")
            suggestions.append("Import to a different repository to avoid conflicts")
        
        elif "hierarchy" in conflict_type:
            suggestions.append("Simplify the issue hierarchy structure")
            suggestions.append("Remove circular sub-issue relationships")
            suggestions.append("Break large hierarchies into smaller trees")
        
        # Add strategy-specific suggestions
        if error.resolution_strategies:
            strategies = ", ".join(error.resolution_strategies)
            suggestions.append(f"Available resolution strategies: {strategies}")
        
        # Add prevention suggestions
        suggestions.append("Run conflict detection before importing")
        suggestions.append("Use preview mode to see potential conflicts")
        
        return suggestions
    
    def _suggest_hierarchy_recovery(self, error: HierarchyError) -> List[str]:
        """Generate suggestions for hierarchy errors."""
        suggestions = []
        
        if error.current_depth and error.max_depth:
            excess_depth = error.current_depth - error.max_depth
            if excess_depth > 0:
                suggestions.append(f"Reduce hierarchy depth by {excess_depth} level(s)")
                suggestions.append("Move some sub-issues to higher levels")
                suggestions.append("Create multiple smaller hierarchies instead")
        
        if "circular" in error.constraint.lower():
            suggestions.append("Remove circular references in sub-issue relationships")
            suggestions.append("Ensure parent-child relationships flow in one direction")
            if error.hierarchy_path:
                path_str = " → ".join(map(str, error.hierarchy_path))
                suggestions.append(f"Break cycle at any point in: {path_str}")
        
        if "closed" in error.constraint.lower():
            suggestions.append("Reopen parent issues before adding sub-issues")
            suggestions.append("Only add sub-issues to open issues")
        
        # Operation-specific suggestions
        if error.operation == "add_sub_issue":
            suggestions.append("Consider creating the sub-issue at a higher level")
            suggestions.append("Validate hierarchy constraints before adding")
        
        return suggestions
    
    def _suggest_from_context(self, error: BaseDomainError) -> List[str]:
        """Generate suggestions based on error context."""
        suggestions = []
        
        if not error.context:
            return suggestions
        
        # Entity-type specific suggestions
        if error.context.entity_type:
            entity_type = error.context.entity_type.lower()
            
            if entity_type == "issue":
                suggestions.append("Validate issue data using Issue.is_valid() before operations")
                suggestions.append("Use IssueFactory for creating valid issues")
            
            elif entity_type == "label":
                suggestions.append("Check label name and color format")
                suggestions.append("Use LabelFactory for creating standard labels")
            
            elif entity_type == "pullrequest":
                suggestions.append("Ensure branch names are valid")
                suggestions.append("Check merge requirements before operations")
        
        # Add correlation ID for tracking
        if error.context.correlation_id:
            suggestions.append(f"Reference correlation ID {error.context.correlation_id[:8]}... for support")
        
        return suggestions
    
    def _suggest_for_operation(self, operation: str, error: BaseDomainError) -> List[str]:
        """Generate operation-specific suggestions."""
        suggestions = []
        
        operation = operation.lower()
        
        if "restore" in operation:
            suggestions.append("Validate data files exist before restore")
            suggestions.append("Use --dry-run to preview restore operations")
            suggestions.append("Check target repository permissions")
        
        elif "save" in operation or "export" in operation:
            suggestions.append("Ensure source repository is accessible")
            suggestions.append("Check write permissions for output directory")
            suggestions.append("Verify GitHub token has required scopes")
        
        elif "validate" in operation:
            suggestions.append("Fix validation errors before proceeding")
            suggestions.append("Use entity validation methods for detailed error info")
        
        elif "create" in operation:
            suggestions.append("Use factory methods for validated object creation")
            suggestions.append("Check required fields are provided")
        
        return suggestions
```

## Testing and Integration Strategy

### Test Coverage Requirements
- **Exception Classes**: 100% coverage for all exception types
- **Error Formatting**: 95% coverage for all format types
- **Recovery Suggestions**: 90% coverage for suggestion generation
- **Integration Tests**: Error handling across all domain operations

### Test Structure
```
tests/domain/error_handling/
├── __init__.py
├── test_exceptions.py           # Exception class tests
├── test_error_formatter.py      # Formatting system tests
├── test_recovery_suggestions.py # Recovery guidance tests
├── test_error_integration.py    # Cross-system integration
└── fixtures/
    ├── sample_errors.py         # Error scenarios for testing
    └── error_examples.py        # Real-world error examples
```

### Performance Targets
- **Error Creation**: <1ms per exception
- **Error Formatting**: <5ms for complex formatting
- **Suggestion Generation**: <10ms for complex analysis
- **Memory Usage**: <1MB additional for error handling

## Success Criteria

### Phase 5 Completion Definition
- [ ] Comprehensive exception hierarchy with rich context
- [ ] User-friendly error formatting for all output types
- [ ] Intelligent recovery suggestion system
- [ ] Consistent error handling across all domain operations
- [ ] Performance targets met for error operations
- [ ] Complete test coverage for error scenarios
- [ ] Documentation with error handling guidelines

### Quality Gates
1. **User Experience**: Error messages are clear and actionable
2. **Developer Experience**: Rich diagnostic information available
3. **Consistency**: Standardized error handling patterns
4. **Performance**: Error handling doesn't impact operation speed
5. **Coverage**: All error scenarios properly handled

This comprehensive error handling system provides a superior user experience while maintaining detailed diagnostic capabilities for developers and support teams.