"""Tests for EntityConfig protocol with StrategyContext."""

from typing import Optional, List
from github_data.entities.base import EntityConfig
from github_data.entities.strategy_context import StrategyContext


class TestEntityConfigProtocol:
    """Test that EntityConfig protocol is correctly defined."""

    def test_protocol_requires_required_services_save(self):
        """Test that protocol includes required_services_save attribute."""

        class ValidConfig:
            name = "test"
            env_var = "TEST"
            default_value = True
            value_type = bool
            dependencies: List[str] = []
            description = "Test"
            required_services_save: List[str] = ["git_service"]
            required_services_restore: List[str] = ["git_service"]

            @staticmethod
            def create_save_strategy(context: StrategyContext) -> Optional[object]:
                return None

            @staticmethod
            def create_restore_strategy(context: StrategyContext) -> Optional[object]:
                return None

        # Should not raise - protocol satisfied
        config: EntityConfig = ValidConfig()  # type: ignore
        assert config.required_services_save == ["git_service"]

    def test_protocol_requires_required_services_restore(self):
        """Test that protocol includes required_services_restore attribute."""

        class ValidConfig:
            name = "test"
            env_var = "TEST"
            default_value = True
            value_type = bool
            dependencies: List[str] = []
            description = "Test"
            required_services_save: List[str] = []
            required_services_restore: List[str] = ["conflict_strategy"]

            @staticmethod
            def create_save_strategy(context: StrategyContext) -> Optional[object]:
                return None

            @staticmethod
            def create_restore_strategy(context: StrategyContext) -> Optional[object]:
                return None

        config: EntityConfig = ValidConfig()  # type: ignore
        assert config.required_services_restore == ["conflict_strategy"]

    def test_factory_methods_accept_strategy_context(self):
        """Test that factory methods accept StrategyContext parameter."""

        class ConfigWithContext:
            name = "test"
            env_var = "TEST"
            default_value = True
            value_type = bool
            dependencies: List[str] = []
            description = "Test"
            required_services_save: List[str] = []
            required_services_restore: List[str] = []

            @staticmethod
            def create_save_strategy(context: StrategyContext) -> Optional[object]:
                # Should be able to access typed context
                return None

            @staticmethod
            def create_restore_strategy(context: StrategyContext) -> Optional[object]:
                return None

        config: EntityConfig = ConfigWithContext()  # type: ignore
        context = StrategyContext()

        # Should be callable with StrategyContext
        result = config.create_save_strategy(context)
        assert result is None
