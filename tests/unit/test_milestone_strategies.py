"""
Tests for milestone save and restore strategies - comprehensive coverage.
Following docs/testing.md comprehensive guidelines.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.operations.save.strategies.milestones_strategy import MilestonesSaveStrategy
from src.operations.restore.strategies.milestones_strategy import (
    MilestonesRestoreStrategy,
)
from src.entities.milestones.models import Milestone
from tests.shared.builders.config_builder import ConfigBuilder
from tests.shared.mocks.boundary_factory import MockBoundaryFactory

# Required markers following docs/testing.md
pytestmark = [
    pytest.mark.unit,
    pytest.mark.fast,
    pytest.mark.milestones,
    pytest.mark.enhanced_fixtures,
    pytest.mark.error_handling,
    pytest.mark.strategy_factory,
]


class TestMilestonesSaveStrategy:
    """Test milestone save strategy comprehensive functionality."""

    def test_save_strategy_entity_name(self):
        """Test save strategy returns correct entity name."""
        strategy = MilestonesSaveStrategy()
        assert strategy.get_entity_name() == "milestones"

    def test_save_strategy_dependencies(self):
        """Test save strategy has no dependencies."""
        strategy = MilestonesSaveStrategy()
        dependencies = strategy.get_dependencies()
        assert dependencies == []

    def test_save_strategy_converter_name(self):
        """Test save strategy returns correct converter name."""
        strategy = MilestonesSaveStrategy()
        assert strategy.get_converter_name() == "convert_to_milestone"

    def test_save_strategy_service_method(self):
        """Test save strategy returns correct service method."""
        strategy = MilestonesSaveStrategy()
        assert strategy.get_service_method() == "get_repository_milestones"

    def test_save_strategy_process_data_no_modification(self):
        """Test save strategy transform returns entities unchanged."""
        strategy = MilestonesSaveStrategy()

        sample_entities = [
            {"id": 1, "title": "Milestone 1"},
            {"id": 2, "title": "Milestone 2"},
        ]
        context = {"repo": "test/repo"}

        result = strategy.transform(sample_entities, context)

        assert result == sample_entities
        assert result is sample_entities  # Same object reference

    def test_save_strategy_should_skip_when_disabled(self):
        """Test save strategy skips when milestones disabled in config."""
        strategy = MilestonesSaveStrategy()

        # Use ConfigBuilder with milestones disabled
        config = ConfigBuilder().with_milestones(False).build()

        assert strategy.should_skip(config) is True

    def test_save_strategy_should_not_skip_when_enabled(self):
        """Test save strategy does not skip when milestones enabled in config."""
        strategy = MilestonesSaveStrategy()

        # Use ConfigBuilder with milestones enabled
        config = ConfigBuilder().with_milestones(True).build()

        assert strategy.should_skip(config) is False

    def test_save_strategy_should_not_skip_when_attribute_missing(self):
        """Test save strategy defaults to not skip when config attribute missing."""
        strategy = MilestonesSaveStrategy()

        # Use default ConfigBuilder which has milestones enabled by default
        config = ConfigBuilder().build()

        assert strategy.should_skip(config) is False


class TestMilestonesRestoreStrategy:
    """Test milestone restore strategy comprehensive functionality."""

    def test_restore_strategy_entity_name(self):
        """Test restore strategy returns correct entity name."""
        strategy = MilestonesRestoreStrategy()
        assert strategy.get_entity_name() == "milestones"

    def test_restore_strategy_dependencies(self):
        """Test restore strategy has no dependencies."""
        strategy = MilestonesRestoreStrategy()
        dependencies = strategy.get_dependencies()
        assert dependencies == []

    def test_restore_strategy_read_file_exists(self, tmp_path):
        """Test restore strategy reads data when file exists."""
        strategy = MilestonesRestoreStrategy()

        # Create actual test data file
        milestone_file = tmp_path / "milestones.json"
        test_data = [
            {
                "id": "milestone_1",
                "number": 1,
                "title": "v1.0",
                "state": "open",
                "creator": {
                    "login": "testuser",
                    "id": "user_1",
                    "avatar_url": "https://github.com/testuser.png",
                    "html_url": "https://github.com/testuser",
                },
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "html_url": "https://github.com/test/repo/milestones/1",
            }
        ]

        # Create the file so it exists
        import json

        with open(milestone_file, "w") as f:
            json.dump(test_data, f)

        # Mock storage service
        mock_storage = Mock()
        mock_storage.read.return_value = [Milestone(**test_data[0])]

        # Test read
        result = strategy.read(str(tmp_path), mock_storage)

        # Verify storage service was called correctly
        mock_storage.read.assert_called_once_with(milestone_file, Milestone)

        assert len(result) == 1
        assert isinstance(result[0], Milestone)

    def test_restore_strategy_read_file_not_exists(self, tmp_path):
        """Test restore strategy returns empty list when file doesn't exist."""
        strategy = MilestonesRestoreStrategy()

        # Mock storage service (shouldn't be called)
        mock_storage = Mock()

        # Test read with non-existent file
        result = strategy.read(str(tmp_path), mock_storage)

        # Should return empty list without calling storage service
        assert result == []
        mock_storage.read.assert_not_called()

    def test_restore_strategy_transform_full_milestone(self, sample_milestone):
        """Test transform with full milestone data."""
        strategy = MilestonesRestoreStrategy()

        # Create milestone with all fields
        milestone = Milestone(
            id="milestone_1",
            number=1,
            title="v1.0 Release",
            description="First major release",
            state="open",
            creator=sample_milestone.creator,
            created_at=datetime(2023, 1, 1),
            updated_at=datetime(2023, 1, 15),
            due_on=datetime(2023, 12, 31),
            html_url="https://github.com/test/repo/milestones/1",
        )

        context = {}
        result = strategy.transform(milestone, context)

        assert result is not None
        assert result["title"] == "v1.0 Release"
        assert result["description"] == "First major release"
        assert result["state"] == "open"
        assert result["due_on"] == "2023-12-31T00:00:00"

    def test_restore_strategy_transform_minimal_milestone(self, sample_milestone):
        """Test transform with minimal milestone data."""
        strategy = MilestonesRestoreStrategy()

        context = {}
        result = strategy.transform(sample_milestone, context)

        assert result is not None
        assert result["title"] == "v1.0"
        assert result["state"] == "open"
        assert "description" not in result  # None description should be omitted
        assert "due_on" not in result  # None due_on should be omitted

    def test_restore_strategy_write_success(self, sample_github_data):
        """Test write successful API call."""
        strategy = MilestonesRestoreStrategy()

        # Use MockBoundaryFactory for protocol completeness
        mock_github_service = MockBoundaryFactory.create_auto_configured(
            sample_github_data
        )
        mock_github_service.create_milestone.return_value = {
            "number": 101,
            "title": "v1.0",
            "state": "open",
        }

        entity_data = {
            "title": "v1.0",
            "description": "First release",
            "state": "open",
            "due_on": "2023-12-31T23:59:59",
        }

        result = strategy.write(mock_github_service, "test/repo", entity_data)

        # Verify API call
        mock_github_service.create_milestone.assert_called_once_with(
            repo_name="test/repo",
            title="v1.0",
            description="First release",
            due_on="2023-12-31T23:59:59",
            state="open",
        )

        assert result["number"] == 101

    def test_restore_strategy_write_already_exists(self, sample_github_data):
        """Test write handles 'already exists' error gracefully."""
        strategy = MilestonesRestoreStrategy()

        # Use MockBoundaryFactory and add specific error behavior
        mock_github_service = MockBoundaryFactory.create_auto_configured(
            sample_github_data
        )
        mock_github_service.create_milestone.side_effect = Exception(
            "Milestone already exists"
        )

        entity_data = {"title": "Existing Milestone", "state": "open"}

        with patch(
            "src.operations.restore.strategies.milestones_strategy.logger"
        ) as mock_logger:
            result = strategy.write(mock_github_service, "test/repo", entity_data)

            # Should log warning and return mock response
            mock_logger.warning.assert_called_once()
            warning_call_args = mock_logger.warning.call_args[0][0]
            assert "already exists" in warning_call_args

            assert result["title"] == "Existing Milestone"
            assert result["number"] == -1

    def test_restore_strategy_write_other_error(self, sample_github_data):
        """Test write re-raises non-'already exists' errors."""
        strategy = MilestonesRestoreStrategy()

        # Use MockBoundaryFactory and add specific error behavior
        mock_github_service = MockBoundaryFactory.create_auto_configured(
            sample_github_data
        )
        mock_github_service.create_milestone.side_effect = Exception("Network error")

        entity_data = {"title": "Test Milestone", "state": "open"}

        with pytest.raises(Exception) as exc_info:
            strategy.write(mock_github_service, "test/repo", entity_data)

        assert "Network error" in str(exc_info.value)

    def test_restore_strategy_post_create_actions_successful_creation(
        self, sample_milestone
    ):
        """Test post_create_actions stores milestone mapping for successful creation."""
        strategy = MilestonesRestoreStrategy()

        mock_github_service = Mock()
        created_data = {"number": 101, "title": "v1.0"}
        context = {}

        strategy.post_create_actions(
            mock_github_service, "test/repo", sample_milestone, created_data, context
        )

        # Verify milestone mapping was stored
        assert "milestone_mapping" in context
        assert context["milestone_mapping"][1] == 101  # original number -> new number

    def test_restore_strategy_post_create_actions_failed_creation(
        self, sample_milestone
    ):
        """Test post_create_actions skips mapping for failed creation."""
        strategy = MilestonesRestoreStrategy()

        mock_github_service = Mock()
        created_data = {"number": -1, "title": "v1.0"}  # Failed creation indicator
        context = {}

        strategy.post_create_actions(
            mock_github_service, "test/repo", sample_milestone, created_data, context
        )

        # Should not create milestone mapping for failed creation
        assert context.get("milestone_mapping", {}) == {}

    def test_restore_strategy_post_create_actions_existing_mapping(
        self, sample_milestone
    ):
        """Test post_create_actions updates existing milestone mapping."""
        strategy = MilestonesRestoreStrategy()

        mock_github_service = Mock()
        created_data = {"number": 102, "title": "v1.0"}
        context = {"milestone_mapping": {5: 105}}  # Existing mapping

        strategy.post_create_actions(
            mock_github_service, "test/repo", sample_milestone, created_data, context
        )

        # Verify both mappings exist
        assert context["milestone_mapping"][1] == 102  # New mapping
        assert context["milestone_mapping"][5] == 105  # Existing mapping preserved

    def test_restore_strategy_should_skip_when_disabled(self):
        """Test restore strategy skips when milestones disabled in config."""
        strategy = MilestonesRestoreStrategy()

        config = ConfigBuilder().with_milestones(False).build()

        assert strategy.should_skip(config) is True

    def test_restore_strategy_should_not_skip_when_enabled(self):
        """Test restore strategy does not skip when milestones enabled in config."""
        strategy = MilestonesRestoreStrategy()

        config = ConfigBuilder().with_milestones(True).build()

        assert strategy.should_skip(config) is False

    def test_restore_strategy_should_not_skip_when_attribute_missing(self):
        """Test restore strategy defaults to not skip when config attribute missing."""
        strategy = MilestonesRestoreStrategy()

        config = ConfigBuilder().build()  # Uses default milestone setting (True)

        assert strategy.should_skip(config) is False


class TestMilestoneStrategiesIntegration:
    """Test integration scenarios between save and restore strategies."""

    def test_strategy_consistency(self):
        """Test that save and restore strategies have consistent entity names."""
        save_strategy = MilestonesSaveStrategy()
        restore_strategy = MilestonesRestoreStrategy()

        assert save_strategy.get_entity_name() == restore_strategy.get_entity_name()

    def test_dependency_consistency(self):
        """Test that save and restore strategies have consistent dependencies."""
        save_strategy = MilestonesSaveStrategy()
        restore_strategy = MilestonesRestoreStrategy()

        assert save_strategy.get_dependencies() == restore_strategy.get_dependencies()

    def test_config_skip_consistency(self):
        """Test that save and restore strategies handle config skipping consistently."""
        save_strategy = MilestonesSaveStrategy()
        restore_strategy = MilestonesRestoreStrategy()

        # Test with enabled config
        enabled_config = ConfigBuilder().with_milestones(True).build()

        assert save_strategy.should_skip(
            enabled_config
        ) == restore_strategy.should_skip(enabled_config)

        # Test with disabled config
        disabled_config = ConfigBuilder().with_milestones(False).build()

        assert save_strategy.should_skip(
            disabled_config
        ) == restore_strategy.should_skip(disabled_config)


@pytest.fixture
def sample_milestone():
    """Create a sample milestone for testing."""
    from src.entities.users.models import GitHubUser

    return Milestone(
        id="milestone_1",
        number=1,
        title="v1.0",
        description=None,
        state="open",
        creator=GitHubUser(
            login="testuser",
            id="user_1",
            avatar_url="https://github.com/testuser.png",
            html_url="https://github.com/testuser",
        ),
        created_at=datetime(2023, 1, 1),
        updated_at=datetime(2023, 1, 1),
        html_url="https://github.com/test/repo/milestones/1",
        due_on=None,
        closed_at=None,
    )
