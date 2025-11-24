"""Releases entity configuration for EntityRegistry."""

from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from github_data_core.entities.strategy_context import StrategyContext
    from github_data_tools.entities.releases.save_strategy import ReleasesSaveStrategy
    from github_data_tools.entities.releases.restore_strategy import (
        ReleasesRestoreStrategy,
    )


class ReleasesEntityConfig:
    """Configuration for releases entity.

    Releases have no dependencies and are enabled by default.
    Uses convention-based strategy loading.
    """

    name = "releases"
    env_var = "INCLUDE_RELEASES"
    default_value = True
    value_type = bool
    dependencies: List[str] = []
    description = "Repository releases and tags"

    # Service requirements
    required_services_save: List[str] = []
    required_services_restore: List[str] = []

    # Converter declarations
    converters = {
        "convert_to_release": {
            "module": "github_data.entities.releases.converters",
            "function": "convert_to_release",
            "target_model": "Release",
        },
        "convert_to_release_asset": {
            "module": "github_data.entities.releases.converters",
            "function": "convert_to_release_asset",
            "target_model": "ReleaseAsset",
        },
    }

    # GitHub API operations
    github_api_operations = {
        "get_repository_releases": {
            "boundary_method": "get_repository_releases",
            "converter": "convert_to_release",
        },
        "create_release": {
            "boundary_method": "create_release",
            "converter": "convert_to_release",
        },
    }

    @staticmethod
    def create_save_strategy(
        context: "StrategyContext",
    ) -> Optional["ReleasesSaveStrategy"]:
        """Create save strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            ReleasesSaveStrategy instance
        """
        from github_data_tools.entities.releases.save_strategy import ReleasesSaveStrategy

        return ReleasesSaveStrategy()

    @staticmethod
    def create_restore_strategy(
        context: "StrategyContext",
    ) -> Optional["ReleasesRestoreStrategy"]:
        """Create restore strategy instance.

        Args:
            context: Typed strategy context with validated services

        Returns:
            ReleasesRestoreStrategy instance
        """
        from github_data_tools.entities.releases.restore_strategy import (
            ReleasesRestoreStrategy,
        )

        return ReleasesRestoreStrategy()
