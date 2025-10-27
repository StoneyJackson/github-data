"""Typed strategy context for entity strategy creation."""

from typing import Optional, Any, TYPE_CHECKING, Callable
from dataclasses import dataclass

if TYPE_CHECKING:
    from src.git.service import GitRepositoryService
    from src.github.service import GitHubService


def service_property(func: Callable[[Any], Any]) -> property:
    """Decorator to create a validated service property.

    Converts a method that defines service metadata into a property
    that validates and returns the service.

    The decorated function's name determines the service name
    and corresponding private attribute (_<name>).

    Usage:
        @service_property
        def git_service(self) -> GitService:
            '''Git repository service.'''
            ...

    This creates a property that:
    - Returns self._git_service if not None
    - Raises RuntimeError with clear message if None
    - Preserves type hints for mypy and IDEs

    Args:
        func: Method defining service metadata (name and type)

    Returns:
        Property that validates and returns the service
    """
    service_name = func.__name__
    private_attr = f"_{service_name}"

    def wrapper(self: Any) -> Any:
        value = getattr(self, private_attr, None)
        if value is None:
            raise RuntimeError(f"{service_name} is required but was not provided")
        return value

    # Preserve type hints from original function before converting to property
    wrapper.__annotations__ = getattr(func, "__annotations__", {})
    return property(wrapper)


@dataclass
class StrategyContext:
    """Typed container for services available to entity strategies.

    Services are stored as private optional attributes and exposed
    as typed properties that validate on access.

    This design enables:
    - Compile-time type checking (mypy validates service usage)
    - IDE autocomplete for available services
    - Clear runtime errors when required services missing
    - Adding new services without breaking existing entities

    Adding new services:
    1. Add private attribute: _new_service: Optional[NewService] = None
    2. Add decorated property with type hint
    3. Existing entities unaffected (backward compatible)

    Example:
        context = StrategyContext(_git_service=git_svc)
        service = context.git_service  # Typed, validated
    """

    # Private optional storage for services
    _git_service: Optional["GitRepositoryService"] = None
    _github_service: Optional["GitHubService"] = None
    _conflict_strategy: Optional[Any] = None

    # Non-service configuration (has default, no validation needed)
    _include_original_metadata: bool = True

    # Public typed properties with validation

    @service_property
    def git_service(self) -> "GitRepositoryService":  # type: ignore[empty-body]
        """Git repository service for cloning/restoring repositories."""
        ...

    @service_property
    def github_service(self) -> "GitHubService":  # type: ignore[empty-body]
        """GitHub API service for issues, PRs, labels, etc."""
        ...

    @service_property
    def conflict_strategy(self) -> Any:
        """Conflict resolution strategy for label/issue restoration."""
        ...

    @property
    def include_original_metadata(self) -> bool:
        """Whether to preserve original GitHub metadata during restore."""
        return self._include_original_metadata
