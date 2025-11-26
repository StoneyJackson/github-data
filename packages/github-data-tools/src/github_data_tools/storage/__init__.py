"""
Storage package with dependency injection support.

Provides factory functions for creating storage service implementations
and exports core storage protocols for dependency inversion.
"""

from github_data_core.storage.protocols import StorageService
from github_data_core.storage.json_storage_service import JsonStorageService


def create_storage_service(storage_type: str = "json") -> StorageService:
    """
    Factory function for storage services.

    Args:
        storage_type: Type of storage service to create (default: "json")

    Returns:
        Configured StorageService instance

    Raises:
        ValueError: If unknown storage type is specified
    """
    if storage_type == "json":
        return JsonStorageService()
    raise ValueError(f"Unknown storage type: {storage_type}")


# Export main interfaces and factory
__all__ = ["StorageService", "JsonStorageService", "create_storage_service"]
