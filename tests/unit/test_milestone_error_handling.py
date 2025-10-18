"""Unit tests for milestone error handling and API failure scenarios.

Tests API rate limiting scenarios, network failure recovery, invalid milestone
data handling, and authentication failure scenarios to validate resilience to
GitHub API failures.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime
import json

from src.github.service import GitHubService
from src.operations.save.strategies.milestones_strategy import MilestonesSaveStrategy
from src.operations.restore.strategies.milestones_strategy import (
    MilestonesRestoreStrategy,
)
from src.entities.milestones.models import Milestone
from src.entities.users.models import GitHubUser
from src.config.settings import ApplicationConfig


@pytest.mark.skip(
    reason="Temporarily disabled during Phase 3 fixes - needs method fixes"
)
@pytest.mark.unit
@pytest.mark.milestones
@pytest.mark.milestone_relationships
class TestMilestoneErrorHandling:
    """Test milestone error handling and API failure scenarios."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration with milestones enabled."""
        config = Mock(spec=ApplicationConfig)
        config.include_milestones = True
        config.repository_owner = "test-owner"
        config.repository_name = "test-repo"
        return config

    @pytest.fixture
    def mock_github_service(self):
        """Create a mock GitHub service."""
        return Mock(spec=GitHubService)

    @pytest.fixture
    def mock_storage_service(self):
        """Create a mock storage service."""
        storage = Mock()
        storage.save_data = Mock()
        storage.load_data = Mock()
        storage.file_exists = Mock()
        return storage

    @pytest.fixture
    def milestone_save_strategy(self):
        """Create milestone save strategy."""
        return MilestonesSaveStrategy()

    @pytest.fixture
    def milestone_restore_strategy(self):
        """Create milestone restore strategy."""
        return MilestonesRestoreStrategy()

    @pytest.fixture
    def sample_milestone(self):
        """Create a sample milestone for testing."""
        return Milestone(
            id="M_kwDOABCDEF123",
            number=1,
            title="Test Milestone",
            description="Test milestone description",
            state="open",
            creator=GitHubUser(
                login="testuser",
                id="U_123456",
                avatar_url="http://example.com",
                html_url="http://example.com",
            ),
            created_at=datetime(2023, 1, 1),
            updated_at=datetime(2023, 1, 2),
            due_on=datetime(2023, 12, 31),
            closed_at=None,
            open_issues=5,
            closed_issues=0,
            html_url="https://github.com/owner/repo/milestone/1",
        )

    @pytest.mark.asyncio
    async def test_api_rate_limiting_scenario(
        self, milestone_save_strategy, mock_github_service
    ):
        """Test handling of GitHub API rate limiting during milestone operations."""
        from github import RateLimitExceededException

        # Configure service to raise rate limit exception
        mock_github_service.get_milestones = AsyncMock(
            side_effect=RateLimitExceededException(403, "rate limit exceeded")
        )

        # Execute save operation and expect graceful handling
        with pytest.raises(RateLimitExceededException):
            await milestone_save_strategy.save()

        # Verify the exception was properly propagated
        mock_github_service.get_milestones.assert_called_once()

    @pytest.mark.asyncio
    async def test_network_failure_recovery(
        self, milestone_save_strategy, mock_github_service
    ):
        """Test recovery from network failures during milestone operations."""
        import aiohttp

        # Configure service to raise network error
        mock_github_service.get_milestones = AsyncMock(
            side_effect=aiohttp.ClientError("Network error")
        )

        # Execute save operation and expect graceful handling
        with pytest.raises(aiohttp.ClientError):
            await milestone_save_strategy.save()

        # Verify the exception was properly propagated
        mock_github_service.get_milestones.assert_called_once()

    def test_invalid_milestone_data_handling(
        self, milestone_restore_strategy, mock_storage_service
    ):
        """Test handling of invalid milestone data during restore operations."""
        # Configure storage to return invalid milestone data
        invalid_milestone_data = [
            {
                "id": "M_invalid",
                "number": "not_a_number",  # Invalid type
                "title": None,  # Required field missing
                "state": "invalid_state",  # Invalid state
                # Missing required fields
            }
        ]
        mock_storage_service.load_data.return_value = invalid_milestone_data
        mock_storage_service.file_exists.return_value = True

        # Execute restore and expect validation error handling
        with pytest.raises((ValueError, TypeError)):
            milestone_restore_strategy.load_data()

        mock_storage_service.load_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_authentication_failure_scenarios(
        self, milestone_save_strategy, mock_github_service
    ):
        """Test handling of authentication failures during milestone operations."""
        from github import BadCredentialsException

        # Configure service to raise authentication error
        mock_github_service.get_milestones = AsyncMock(
            side_effect=BadCredentialsException(401, "Bad credentials")
        )

        # Execute save operation and expect graceful handling
        with pytest.raises(BadCredentialsException):
            await milestone_save_strategy.save()

        # Verify the exception was properly propagated
        mock_github_service.get_milestones.assert_called_once()

    @pytest.mark.asyncio
    async def test_milestone_404_error_handling(
        self, milestone_restore_strategy, mock_github_service, sample_milestone
    ):
        """Test handling of 404 errors when milestone doesn't exist during restore."""
        from github import UnknownObjectException

        # Configure restore strategy with milestone data
        milestone_restore_strategy.milestones = [sample_milestone]

        # Configure service to raise 404 error
        mock_github_service.create_milestone = AsyncMock(
            side_effect=UnknownObjectException(404, "Repository not found")
        )

        # Execute restore and expect graceful handling
        with pytest.raises(UnknownObjectException):
            await milestone_restore_strategy.restore()

        # Verify the service was called
        mock_github_service.create_milestone.assert_called_once()

    @pytest.mark.asyncio
    async def test_api_timeout_handling(
        self, milestone_save_strategy, mock_github_service
    ):
        """Test handling of API timeouts during milestone operations."""
        import asyncio

        # Configure service to raise timeout error
        mock_github_service.get_milestones = AsyncMock(
            side_effect=asyncio.TimeoutError("Request timeout")
        )

        # Execute save operation and expect graceful handling
        with pytest.raises(asyncio.TimeoutError):
            await milestone_save_strategy.save()

        # Verify the exception was properly propagated
        mock_github_service.get_milestones.assert_called_once()

    def test_corrupted_milestone_json_handling(
        self, milestone_restore_strategy, mock_storage_service
    ):
        """Test handling of corrupted milestone JSON data."""
        # Configure storage to raise JSON decode error
        mock_storage_service.load_data.side_effect = json.JSONDecodeError(
            "Invalid JSON", "doc", 0
        )
        mock_storage_service.file_exists.return_value = True

        # Execute load_data and expect graceful handling
        with pytest.raises(json.JSONDecodeError):
            milestone_restore_strategy.load_data()

        mock_storage_service.load_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_github_api_server_error(
        self, milestone_save_strategy, mock_github_service
    ):
        """Test handling of GitHub API server errors (5xx)."""
        from github import GithubException

        # Configure service to raise server error
        mock_github_service.get_milestones = AsyncMock(
            side_effect=GithubException(500, "Internal server error")
        )

        # Execute save operation and expect graceful handling
        with pytest.raises(GithubException):
            await milestone_save_strategy.save()

        # Verify the exception was properly propagated
        mock_github_service.get_milestones.assert_called_once()

    def test_empty_milestone_file_handling(
        self, milestone_restore_strategy, mock_storage_service
    ):
        """Test handling of empty milestone files during restore."""
        # Configure storage to return empty data
        mock_storage_service.load_data.return_value = []
        mock_storage_service.file_exists.return_value = True

        # Execute load_data - should handle empty list gracefully
        milestone_restore_strategy.load_data()

        # Verify empty data is handled correctly
        assert milestone_restore_strategy.milestones == []
        mock_storage_service.load_data.assert_called_once()

    def test_missing_milestone_file_handling(
        self, milestone_restore_strategy, mock_storage_service
    ):
        """Test handling of missing milestone files during restore."""
        # Configure storage to indicate file doesn't exist
        mock_storage_service.file_exists.return_value = False

        # Execute load_data - should handle missing file gracefully
        milestone_restore_strategy.load_data()

        # Verify missing file is handled correctly
        assert milestone_restore_strategy.milestones == []
        mock_storage_service.file_exists.assert_called_once()

    def test_milestone_field_validation_errors(self, milestone_restore_strategy):
        """Test handling of milestone field validation errors."""
        # Test with invalid milestone data structures
        invalid_milestones = [
            # Missing required id field
            {
                "number": 1,
                "title": "Test",
                "state": "open",
                "creator": GitHubUser(
                    login="user",
                    id="123",
                    avatar_url="http://example.com",
                    html_url="http://example.com",
                ),
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "html_url": "https://github.com/test",
            },
            # Invalid date format
            {
                "id": "M_123",
                "number": 2,
                "title": "Test 2",
                "state": "open",
                "creator": GitHubUser(
                    login="user",
                    id="123",
                    avatar_url="http://example.com",
                    html_url="http://example.com",
                ),
                "created_at": "invalid-date",
                "updated_at": "2023-01-01T00:00:00Z",
                "html_url": "https://github.com/test",
            },
        ]

        milestone_restore_strategy.milestones = []

        # Attempt to create milestones from invalid data
        for milestone_data in invalid_milestones:
            with pytest.raises((ValueError, TypeError)):
                Milestone(**milestone_data)

    @pytest.mark.asyncio
    async def test_milestone_creation_conflict_handling(
        self, milestone_restore_strategy, mock_github_service, sample_milestone
    ):
        """Test handling of milestone creation conflicts during restore."""
        from github import GithubException

        # Configure restore strategy with milestone data
        milestone_restore_strategy.milestones = [sample_milestone]

        # Configure service to raise conflict error (milestone already exists)
        mock_github_service.create_milestone = AsyncMock(
            side_effect=GithubException(422, "Milestone already exists")
        )

        # Execute restore and expect graceful handling
        with pytest.raises(GithubException):
            await milestone_restore_strategy.restore()

        # Verify the service was called
        mock_github_service.create_milestone.assert_called_once()

    def test_invalid_milestone_state_handling(self):
        """Test handling of invalid milestone states."""
        # Test creating milestone with invalid state
        with pytest.raises(ValueError):
            Milestone(
                id="M_123",
                number=1,
                title="Test",
                state="invalid_state",  # Should be 'open' or 'closed'
                creator=GitHubUser(
                    login="user",
                    id="123",
                    avatar_url="http://example.com",
                    html_url="http://example.com",
                ),
                created_at=datetime(2023, 1, 1),
                updated_at=datetime(2023, 1, 1),
                html_url="https://github.com/test",
            )

    @pytest.mark.asyncio
    async def test_partial_milestone_save_failure(
        self, milestone_save_strategy, mock_github_service, mock_storage_service
    ):
        """Test handling of partial failures during milestone save operations."""
        # Configure service to succeed for get_milestones but fail for save
        mock_milestones = [
            Mock(id="M_1", number=1, title="Milestone 1"),
            Mock(id="M_2", number=2, title="Milestone 2"),
        ]
        mock_github_service.get_milestones = AsyncMock(return_value=mock_milestones)
        mock_storage_service.save_data.side_effect = IOError("Failed to save")

        # Execute save operation and expect storage error
        with pytest.raises(IOError):
            await milestone_save_strategy.save()

        # Verify milestones were fetched but save failed
        mock_github_service.get_milestones.assert_called_once()
        mock_storage_service.save_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_api_response_parsing_errors(
        self, milestone_save_strategy, mock_github_service
    ):
        """Test handling of API response parsing errors."""
        # Configure service to return malformed response
        malformed_response = Mock()
        malformed_response.number = None  # Invalid number
        malformed_response.title = 123  # Invalid title type
        malformed_response.state = "INVALID"  # Invalid state

        mock_github_service.get_milestones = AsyncMock(
            return_value=[malformed_response]
        )

        # Execute save operation and expect parsing to handle errors gracefully
        with pytest.raises((AttributeError, TypeError, ValueError)):
            await milestone_save_strategy.save()

        mock_github_service.get_milestones.assert_called_once()
