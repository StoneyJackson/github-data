"""
Tests for milestone entity models and validation.
Following docs/testing.md comprehensive guidelines.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from github_data.entities.milestones.models import Milestone
from github_data.entities.users.models import GitHubUser

# Required markers following docs/testing.md
pytestmark = [
    pytest.mark.unit,
    pytest.mark.fast,
    pytest.mark.enhanced_fixtures,
]


class TestMilestoneEntity:
    """Test milestone entity model validation and behavior."""

    def test_valid_milestone_creation_with_all_fields(self, sample_github_user):
        """Test creating a valid milestone with all fields populated."""
        due_date = datetime(2024, 12, 31, 23, 59, 59)
        closed_date = datetime(2024, 11, 30, 12, 0, 0)
        created_date = datetime(2024, 1, 1, 0, 0, 0)
        updated_date = datetime(2024, 1, 15, 10, 30, 0)

        milestone = Milestone(
            id="milestone_123",
            number=5,
            title="Version 2.0",
            description="Major release with new features",
            state="closed",
            creator=sample_github_user,
            created_at=created_date,
            updated_at=updated_date,
            due_on=due_date,
            closed_at=closed_date,
            open_issues=2,
            closed_issues=15,
            html_url="https://github.com/test/repo/milestones/5",
        )

        assert milestone.id == "milestone_123"
        assert milestone.number == 5
        assert milestone.title == "Version 2.0"
        assert milestone.description == "Major release with new features"
        assert milestone.state == "closed"
        assert milestone.creator == sample_github_user
        assert milestone.created_at == created_date
        assert milestone.updated_at == updated_date
        assert milestone.due_on == due_date
        assert milestone.closed_at == closed_date
        assert milestone.open_issues == 2
        assert milestone.closed_issues == 15
        assert milestone.html_url == "https://github.com/test/repo/milestones/5"

    def test_valid_milestone_creation_with_minimal_fields(self, sample_github_user):
        """Test creating a valid milestone with only required fields."""
        created_date = datetime(2024, 1, 1, 0, 0, 0)
        updated_date = datetime(2024, 1, 15, 10, 30, 0)

        milestone = Milestone(
            id=42,
            number=1,
            title="First Milestone",
            state="open",
            creator=sample_github_user,
            created_at=created_date,
            updated_at=updated_date,
            html_url="https://github.com/test/repo/milestones/1",
        )

        assert milestone.id == 42
        assert milestone.number == 1
        assert milestone.title == "First Milestone"
        assert milestone.description is None
        assert milestone.state == "open"
        assert milestone.creator == sample_github_user
        assert milestone.created_at == created_date
        assert milestone.updated_at == updated_date
        assert milestone.due_on is None
        assert milestone.closed_at is None
        assert milestone.open_issues == 0  # Default value
        assert milestone.closed_issues == 0  # Default value
        assert milestone.html_url == "https://github.com/test/repo/milestones/1"

    def test_milestone_with_string_id(self, sample_github_user):
        """Test milestone creation with string ID (Union[int, str] support)."""
        milestone = Milestone(
            id="gid://github/Milestone/123456789",
            number=10,
            title="GraphQL Milestone",
            state="open",
            creator=sample_github_user,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            html_url="https://github.com/test/repo/milestones/10",
        )

        assert milestone.id == "gid://github/Milestone/123456789"
        assert isinstance(milestone.id, str)

    def test_milestone_with_integer_id(self, sample_github_user):
        """Test milestone creation with integer ID."""
        milestone = Milestone(
            id=999,
            number=10,
            title="REST API Milestone",
            state="open",
            creator=sample_github_user,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            html_url="https://github.com/test/repo/milestones/10",
        )

        assert milestone.id == 999
        assert isinstance(milestone.id, int)

    def test_milestone_state_validation(self, sample_github_user):
        """Test that milestone accepts valid state values."""
        # Test open state
        milestone_open = Milestone(
            id=1,
            number=1,
            title="Open Milestone",
            state="open",
            creator=sample_github_user,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            html_url="https://github.com/test/repo/milestones/1",
        )
        assert milestone_open.state == "open"

        # Test closed state
        milestone_closed = Milestone(
            id=2,
            number=2,
            title="Closed Milestone",
            state="closed",
            creator=sample_github_user,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            closed_at=datetime.now(),
            html_url="https://github.com/test/repo/milestones/2",
        )
        assert milestone_closed.state == "closed"

    def test_milestone_optional_fields_none_handling(self, sample_github_user):
        """Test that optional fields correctly handle None values."""
        milestone = Milestone(
            id=1,
            number=1,
            title="Test Milestone",
            state="open",
            creator=sample_github_user,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            html_url="https://github.com/test/repo/milestones/1",
            description=None,
            due_on=None,
            closed_at=None,
        )

        assert milestone.description is None
        assert milestone.due_on is None
        assert milestone.closed_at is None

    def test_milestone_timestamp_handling(self, sample_github_user):
        """Test that milestone correctly handles various timestamp formats."""
        # Test with datetime objects
        created = datetime(2024, 1, 1, 12, 0, 0)
        updated = datetime(2024, 1, 15, 14, 30, 0)
        due = datetime(2024, 12, 31, 23, 59, 59)

        milestone = Milestone(
            id=1,
            number=1,
            title="Timestamp Test",
            state="open",
            creator=sample_github_user,
            created_at=created,
            updated_at=updated,
            due_on=due,
            html_url="https://github.com/test/repo/milestones/1",
        )

        assert isinstance(milestone.created_at, datetime)
        assert isinstance(milestone.updated_at, datetime)
        assert isinstance(milestone.due_on, datetime)
        assert milestone.created_at == created
        assert milestone.updated_at == updated
        assert milestone.due_on == due

    def test_milestone_issue_count_defaults(self, sample_github_user):
        """Test that issue count fields have correct default values."""
        milestone = Milestone(
            id=1,
            number=1,
            title="Default Count Test",
            state="open",
            creator=sample_github_user,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            html_url="https://github.com/test/repo/milestones/1",
        )

        assert milestone.open_issues == 0
        assert milestone.closed_issues == 0

    def test_milestone_issue_count_custom_values(self, sample_github_user):
        """Test that issue count fields accept custom values."""
        milestone = Milestone(
            id=1,
            number=1,
            title="Custom Count Test",
            state="open",
            creator=sample_github_user,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            open_issues=5,
            closed_issues=12,
            html_url="https://github.com/test/repo/milestones/1",
        )

        assert milestone.open_issues == 5
        assert milestone.closed_issues == 12

    def test_milestone_missing_required_fields(self, sample_github_user):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Milestone(
                # Missing required fields
                description="Incomplete milestone"
            )

        error = exc_info.value
        assert "id" in str(error)
        assert "number" in str(error)
        assert "title" in str(error)
        assert "state" in str(error)
        assert "creator" in str(error)
        assert "created_at" in str(error)
        assert "updated_at" in str(error)
        assert "html_url" in str(error)

    def test_milestone_invalid_field_types(self, sample_github_user):
        """Test that invalid field types raise ValidationError."""
        with pytest.raises(ValidationError):
            Milestone(
                id=1,
                number="not_a_number",  # Should be int
                title="Invalid Type Test",
                state="open",
                creator=sample_github_user,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                html_url="https://github.com/test/repo/milestones/1",
            )

    def test_milestone_model_config(self, sample_github_user):
        """Test that model configuration is properly set."""
        milestone = Milestone(
            id=1,
            number=1,
            title="Config Test",
            state="open",
            creator=sample_github_user,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            html_url="https://github.com/test/repo/milestones/1",
        )

        # Verify model_config is set correctly
        assert milestone.model_config["populate_by_name"] is True


@pytest.fixture
def sample_github_user():
    """Create a sample GitHub user for testing."""
    return GitHubUser(
        login="testuser",
        id="user_123",
        avatar_url="https://github.com/testuser.png",
        html_url="https://github.com/testuser",
    )
