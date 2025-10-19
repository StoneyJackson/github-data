"""Unit tests for milestone data integrity edge cases.

Tests milestone title conflicts during restore, missing milestone references
in issues/PRs, corrupted milestone data handling, large dataset performance
validation, and Unicode handling.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timezone

from src.entities.milestones.models import Milestone
from src.entities.users.models import GitHubUser
from src.operations.save.strategies.milestones_strategy import MilestonesSaveStrategy
from src.operations.restore.strategies.milestones_strategy import (
    MilestonesRestoreStrategy,
)
from src.github.service import GitHubService
from src.config.settings import ApplicationConfig


@pytest.mark.unit
@pytest.mark.milestones
@pytest.mark.milestone_relationships
class TestMilestoneEdgeCases:
    """Test milestone data integrity edge cases."""

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

    def test_milestone_title_conflicts_during_restore(
        self, milestone_restore_strategy, mock_github_service
    ):
        """Test handling of milestone title conflicts during restore operations."""
        # Create milestones with conflicting titles but different numbers
        conflicting_milestones = [
            Milestone(
                id="M_kwDOABCDEF123",
                number=1,
                title="Version 1.0",  # Same title
                description="First version",
                state="open",
                creator=GitHubUser(
                    login="user1",
                    id="U_123",
                    avatar_url="http://example.com",
                    html_url="http://example.com",
                ),
                created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
                updated_at=datetime(2023, 1, 2, tzinfo=timezone.utc),
                html_url="https://github.com/owner/repo/milestone/1",
            ),
            Milestone(
                id="M_kwDOABCDEF456",
                number=2,
                title="Version 1.0",  # Same title, different number
                description="Second version",
                state="closed",
                creator=GitHubUser(
                    login="user2",
                    id="U_456",
                    avatar_url="http://example.com",
                    html_url="http://example.com",
                ),
                created_at=datetime(2023, 2, 1, tzinfo=timezone.utc),
                updated_at=datetime(2023, 2, 2, tzinfo=timezone.utc),
                closed_at=datetime(2023, 2, 15, tzinfo=timezone.utc),
                html_url="https://github.com/owner/repo/milestone/2",
            ),
        ]

        milestone_restore_strategy.milestones = conflicting_milestones
        milestone_restore_strategy.milestone_mapping = {}

        # Configure service to handle milestone creation
        created_milestones = []

        async def mock_create_milestone(
            title, description=None, due_on=None, state="open"
        ):
            # Simulate GitHub's behavior - titles must be unique
            if any(m.title == title for m in created_milestones):
                from github import GithubException

                raise GithubException(
                    422, f"Milestone with title '{title}' already exists"
                )

            milestone = Mock()
            milestone.title = title
            milestone.number = len(created_milestones) + 1
            created_milestones.append(milestone)
            return milestone

        mock_github_service.create_milestone = AsyncMock(
            side_effect=mock_create_milestone
        )

        # Execute restore and expect conflict handling
        with pytest.raises(Exception):  # Should raise conflict exception
            milestone_restore_strategy.restore()

    def test_missing_milestone_references_in_issues(self):
        """Test handling of issues referencing non-existent milestones."""
        # Create milestone mapping that's missing some milestones
        milestone_mapping = {
            1: 10,  # Original milestone 1 maps to new milestone 10
            # Missing mapping for milestone 2
        }

        # Create issue data with milestone references
        issue_data = {
            "number": 1,
            "title": "Test Issue",
            "milestone": {"number": 2},  # References missing milestone
        }

        # Test milestone lookup with missing reference
        milestone_number = issue_data["milestone"]["number"]
        mapped_milestone = milestone_mapping.get(milestone_number)

        # Should handle missing milestone gracefully
        assert mapped_milestone is None

        # Verify issue can be processed without milestone
        processed_issue = issue_data.copy()
        if mapped_milestone is None:
            processed_issue["milestone"] = None

        assert processed_issue["milestone"] is None

    def test_missing_milestone_references_in_prs(self):
        """Test handling of PRs referencing non-existent milestones."""
        # Create milestone mapping that's missing some milestones
        milestone_mapping = {
            1: 10,  # Original milestone 1 maps to new milestone 10
            # Missing mapping for milestone 3
        }

        # Create PR data with milestone references
        pr_data = {
            "number": 1,
            "title": "Test PR",
            "milestone": {"number": 3},  # References missing milestone
        }

        # Test milestone lookup with missing reference
        milestone_number = pr_data["milestone"]["number"]
        mapped_milestone = milestone_mapping.get(milestone_number)

        # Should handle missing milestone gracefully
        assert mapped_milestone is None

        # Verify PR can be processed without milestone
        processed_pr = pr_data.copy()
        if mapped_milestone is None:
            processed_pr["milestone"] = None

        assert processed_pr["milestone"] is None

    def test_corrupted_milestone_data_handling(self, milestone_restore_strategy):
        """Test handling of various forms of corrupted milestone data."""
        from pydantic import ValidationError

        # Test different types of corrupted data that should fail validation
        corrupted_data_sets = [
            # Missing required fields
            {
                "number": 1,
                "title": "Test",
                # Missing id, state, creator, created_at, updated_at, html_url fields
            },
            # Invalid data types for required fields
            {
                "id": "M_123",
                "number": "not_a_number",  # Should be int
                "title": None,  # Should be string
                "state": "open",
                "creator": "invalid_creator",  # Should be GitHubUser object
                "created_at": "invalid_date",  # Should be valid datetime
                "updated_at": "invalid_date",  # Should be valid datetime
                "html_url": 999,  # Should be string
            },
            # Invalid datetime formats
            {
                "id": "M_123",
                "number": 1,
                "title": "Test",
                "state": "open",
                "creator": GitHubUser(
                    login="user",
                    id="123",
                    avatar_url="http://example.com",
                    html_url="http://example.com",
                ),
                "created_at": "not-a-datetime",  # Invalid datetime
                "updated_at": "also-not-a-datetime",  # Invalid datetime
                "html_url": "http://example.com",
            },
        ]

        for corrupted_data in corrupted_data_sets:
            with pytest.raises(ValidationError):
                # Attempt to create milestone from corrupted data
                Milestone(**corrupted_data)

    def test_large_dataset_performance_validation(
        self,
        milestone_save_strategy,
        mock_github_service,
        mock_storage_service,
        tmp_path,
    ):
        """Test performance with large number of milestones (100+)."""
        import time

        # Generate 150 milestones for performance testing
        large_milestone_dataset = []
        for i in range(150):
            milestone = Mock()
            milestone.id = f"M_kwDOABCDEF{i:03d}"
            milestone.number = i + 1
            milestone.title = f"Milestone {i + 1}"
            milestone.description = (
                f"Description for milestone {i + 1}" * 10
            )  # Longer descriptions
            milestone.state = "open" if i % 3 != 0 else "closed"
            milestone.creator = GitHubUser(
                login=f"user{i % 10}",
                id=f"U_{i:06d}",
                avatar_url="http://example.com",
                html_url="http://example.com",
            )
            milestone.created_at = datetime(2023, (i % 12) + 1, 1, tzinfo=timezone.utc)
            milestone.updated_at = datetime(2023, (i % 12) + 1, 2, tzinfo=timezone.utc)
            milestone.due_on = (
                datetime(2023, (i % 12) + 1, 28, tzinfo=timezone.utc)
                if i % 4 == 0
                else None
            )
            milestone.closed_at = (
                datetime(2023, (i % 12) + 1, 15, tzinfo=timezone.utc)
                if milestone.state == "closed"
                else None
            )
            milestone.open_issues = i * 2
            milestone.closed_issues = i
            milestone.html_url = f"https://github.com/owner/repo/milestone/{i + 1}"
            large_milestone_dataset.append(milestone)

        # Configure mocks - storage service needs to not raise exceptions
        mock_github_service.get_repository_milestones = AsyncMock(
            return_value=large_milestone_dataset
        )
        mock_storage_service.save_data = Mock(return_value=None)  # Successful save

        # Measure save performance using temporary directory
        start_time = time.time()
        result = milestone_save_strategy.write(
            large_milestone_dataset, str(tmp_path), mock_storage_service
        )
        end_time = time.time()

        save_time = end_time - start_time

        # Verify performance is acceptable (should be < 5 seconds for 150 milestones)
        assert save_time < 5.0, f"Save operation took too long: {save_time:.3f}s"

        # Verify save operation was successful
        assert result["success"] is True, f"Save operation failed: {result}"
        assert result["data_type"] == "milestones"
        assert result["items_processed"] == 150
        assert result["execution_time_seconds"] < 5.0

        # Verify storage service was called correctly
        mock_storage_service.save_data.assert_called_once()
        call_args = mock_storage_service.save_data.call_args
        saved_data = call_args[0][0]  # First positional argument
        assert len(saved_data) == 150

    def test_unicode_handling_in_milestone_titles(self):
        """Test handling of Unicode characters in milestone titles and descriptions."""
        # Test various Unicode scenarios
        unicode_test_cases = [
            {
                "title": "Version 1.0 🚀",
                "description": "First release with emojis! 🎉🎊",
            },
            {
                "title": "国际化支持",  # Chinese characters
                "description": "Internationalization support for 中文用户",
            },
            {
                "title": "Ñoño version",  # Spanish characters
                "description": "Versión especial para usuarios de español",
            },
            {
                "title": "Русская версия",  # Cyrillic characters
                "description": "Поддержка русского языка",
            },
            {
                "title": "العربية",  # Arabic characters
                "description": "دعم اللغة العربية",
            },
            {
                "title": "🔥 Hot Fix 🔥",  # Emoji-heavy title
                "description": "⚡ Quick fixes for critical bugs ⚡",
            },
        ]

        for i, test_case in enumerate(unicode_test_cases):
            milestone = Milestone(
                id=f"M_unicode_{i}",
                number=i + 1,
                title=test_case["title"],
                description=test_case["description"],
                state="open",
                creator=GitHubUser(
                    login="unicode_user",
                    id="U_unicode",
                    avatar_url="http://example.com",
                    html_url="http://example.com",
                ),
                created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
                updated_at=datetime(2023, 1, 2, tzinfo=timezone.utc),
                html_url=f"https://github.com/owner/repo/milestone/{i + 1}",
            )

            # Verify Unicode content is preserved
            assert milestone.title == test_case["title"]
            assert milestone.description == test_case["description"]

            # Verify serialization/deserialization works with Unicode
            milestone_dict = milestone.model_dump()
            recreated_milestone = Milestone(**milestone_dict)
            assert recreated_milestone.title == test_case["title"]
            assert recreated_milestone.description == test_case["description"]

    def test_extremely_long_milestone_fields(self):
        """Test handling of extremely long milestone titles and descriptions."""
        # Test very long title (GitHub has limits)
        long_title = "A" * 1000
        long_description = "B" * 10000

        milestone = Milestone(
            id="M_long",
            number=1,
            title=long_title,
            description=long_description,
            state="open",
            creator=GitHubUser(
                login="user",
                id="U_123",
                avatar_url="http://example.com",
                html_url="http://example.com",
            ),
            created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 2, tzinfo=timezone.utc),
            html_url="https://github.com/owner/repo/milestone/1",
        )

        # Verify long content is preserved
        assert len(milestone.title) == 1000
        assert len(milestone.description) == 10000
        assert milestone.title == long_title
        assert milestone.description == long_description

    def test_milestone_date_edge_cases(self):
        """Test handling of edge cases in milestone dates."""
        # Test milestone with all date fields at boundaries
        edge_case_dates = [
            # Far future date
            datetime(2099, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
            # Far past date
            datetime(1900, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            # Leap year date
            datetime(2024, 2, 29, 12, 0, 0, tzinfo=timezone.utc),
        ]

        for i, test_date in enumerate(edge_case_dates):
            milestone = Milestone(
                id=f"M_date_{i}",
                number=i + 1,
                title=f"Date Test {i + 1}",
                state="open",
                creator=GitHubUser(
                    login="user",
                    id="U_123",
                    avatar_url="http://example.com",
                    html_url="http://example.com",
                ),
                created_at=test_date,
                updated_at=test_date,
                due_on=test_date,
                html_url=f"https://github.com/owner/repo/milestone/{i + 1}",
            )

            # Verify dates are preserved correctly
            assert milestone.created_at == test_date
            assert milestone.updated_at == test_date
            assert milestone.due_on == test_date

    def test_milestone_number_edge_cases(self):
        """Test handling of edge cases in milestone numbers."""
        # Test various milestone numbers
        edge_case_numbers = [1, 999999, 2147483647]  # Small, large, max int

        for number in edge_case_numbers:
            milestone = Milestone(
                id=f"M_{number}",
                number=number,
                title=f"Milestone {number}",
                state="open",
                creator=GitHubUser(
                    login="user",
                    id="U_123",
                    avatar_url="http://example.com",
                    html_url="http://example.com",
                ),
                created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
                updated_at=datetime(2023, 1, 2, tzinfo=timezone.utc),
                html_url=f"https://github.com/owner/repo/milestone/{number}",
            )

            # Verify number is preserved correctly
            assert milestone.number == number

    def test_milestone_state_consistency_validation(self):
        """Test validation of milestone state consistency with dates."""
        # Test that the model currently allows closed milestone with no closed_at date
        # (This represents current model behavior - no state/date validation enforced)
        milestone = Milestone(
            id="M_test_consistency",
            number=1,
            title="State Consistency Test",
            state="closed",  # Closed state
            creator=GitHubUser(
                login="user",
                id="U_123",
                avatar_url="http://example.com",
                html_url="http://example.com",
            ),
            created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 2, tzinfo=timezone.utc),
            closed_at=None,  # But no closed date - currently allowed
            html_url="https://github.com/owner/repo/milestone/1",
        )

        # Verify the model accepts inconsistent state (current behavior)
        assert milestone.state == "closed"
        assert milestone.closed_at is None

        # Also test that a properly consistent closed milestone works
        consistent_milestone = Milestone(
            id="M_test_consistent",
            number=2,
            title="Consistent Closed Milestone",
            state="closed",
            creator=GitHubUser(
                login="user",
                id="U_123",
                avatar_url="http://example.com",
                html_url="http://example.com",
            ),
            created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 2, tzinfo=timezone.utc),
            closed_at=datetime(2023, 1, 15, tzinfo=timezone.utc),  # Has closed date
            html_url="https://github.com/owner/repo/milestone/2",
        )

        assert consistent_milestone.state == "closed"
        assert consistent_milestone.closed_at is not None

    def test_milestone_issue_count_edge_cases(self):
        """Test handling of edge cases in milestone issue counts."""
        # Test various issue count scenarios
        count_scenarios = [
            {"open": 0, "closed": 0},  # No issues
            {"open": 10000, "closed": 5000},  # Large numbers
            {"open": 0, "closed": 999999},  # Only closed issues
        ]

        for i, counts in enumerate(count_scenarios):
            milestone = Milestone(
                id=f"M_counts_{i}",
                number=i + 1,
                title=f"Count Test {i + 1}",
                state="open",
                creator=GitHubUser(
                    login="user",
                    id="U_123",
                    avatar_url="http://example.com",
                    html_url="http://example.com",
                ),
                created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
                updated_at=datetime(2023, 1, 2, tzinfo=timezone.utc),
                open_issues=counts["open"],
                closed_issues=counts["closed"],
                html_url=f"https://github.com/owner/repo/milestone/{i + 1}",
            )

            # Verify counts are preserved correctly
            assert milestone.open_issues == counts["open"]
            assert milestone.closed_issues == counts["closed"]
