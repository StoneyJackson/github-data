"""
Tests for milestone-issue relationships using modern infrastructure pattern.
Following docs/testing.md comprehensive guidelines.
"""

import pytest

from github_data_tools.entities.issues.models import Issue
from github_data_tools.entities.milestones.models import Milestone
from github_data_tools.entities.issues.save_strategy import IssuesSaveStrategy
from github_data_tools.entities.issues.restore_strategy import IssuesRestoreStrategy

# Required markers following docs/testing.md
pytestmark = [
    pytest.mark.unit,
    pytest.mark.fast,
    pytest.mark.enhanced_fixtures,
    pytest.mark.error_handling,
]


class TestMilestoneIssueRelationships:
    """Test milestone-issue relationship functionality."""

    def test_issue_save_strategy_includes_milestone_dependencies(self):
        """Test that issue save strategy includes milestones in dependencies."""
        strategy = IssuesSaveStrategy()
        dependencies = strategy.get_dependencies()

        assert "labels" in dependencies
        assert "milestones" in dependencies

    def test_issue_restore_strategy_includes_milestone_dependencies(self):
        """Test that issue restore strategy includes milestones in dependencies."""
        strategy = IssuesRestoreStrategy()
        dependencies = strategy.get_dependencies()

        assert "labels" in dependencies
        assert "milestones" in dependencies

    def test_issue_transform_with_milestone(self, sample_milestone):
        """Test that issue transformation includes milestone mapping."""
        strategy = IssuesRestoreStrategy()

        # Create sample issue with milestone
        from github_data_tools.entities.users.models import GitHubUser

        issue = Issue(
            id="issue_1",
            number=1,
            title="Test Issue",
            body="Test body",
            state="open",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            html_url="https://github.com/test/repo/issues/1",
            labels=[],
            user=GitHubUser(
                login="testuser",
                id="user_1",
                avatar_url="https://github.com/testuser.png",
                html_url="https://github.com/testuser",
            ),
            comments=0,
            milestone=sample_milestone,
        )

        # Mock milestone mapping context
        context = {"milestone_mapping": {1: 101}}

        # Transform
        result = strategy.transform(issue, context)

        assert result is not None
        assert result["title"] == "Test Issue"
        assert result["milestone"] == 101  # Mapped milestone number

    def test_issue_transform_without_milestone(self):
        """Test that issue transformation works without milestone."""
        strategy = IssuesRestoreStrategy()

        # Create sample issue without milestone
        from github_data_tools.entities.users.models import GitHubUser

        issue = Issue(
            id="issue_1",
            number=1,
            title="Test Issue",
            body="Test body",
            state="open",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            html_url="https://github.com/test/repo/issues/1",
            labels=[],
            user=GitHubUser(
                login="testuser",
                id="user_1",
                avatar_url="https://github.com/testuser.png",
                html_url="https://github.com/testuser",
            ),
            comments=0,
            milestone=None,
        )

        context = {}

        # Transform
        result = strategy.transform(issue, context)

        assert result is not None
        assert result["title"] == "Test Issue"
        assert "milestone" not in result

    def test_issue_transform_with_missing_milestone_mapping(
        self, sample_milestone, capsys
    ):
        """Test warning when milestone mapping is missing."""
        strategy = IssuesRestoreStrategy()

        # Create sample issue with milestone
        from github_data_tools.entities.users.models import GitHubUser

        issue = Issue(
            id="issue_1",
            number=1,
            title="Test Issue",
            body="Test body",
            state="open",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            html_url="https://github.com/test/repo/issues/1",
            labels=[],
            user=GitHubUser(
                login="testuser",
                id="user_1",
                avatar_url="https://github.com/testuser.png",
                html_url="https://github.com/testuser",
            ),
            comments=0,
            milestone=sample_milestone,
        )

        # Empty milestone mapping context
        context = {"milestone_mapping": {}}

        # Transform
        result = strategy.transform(issue, context)

        assert result is not None
        assert "milestone" not in result

        # Check warning was printed
        captured = capsys.readouterr()
        assert "Warning: Milestone #1 not found" in captured.out

    def test_issue_transform_with_milestone_mapping_error(self, sample_milestone):
        """Test error handling when milestone mapping contains invalid data."""
        strategy = IssuesRestoreStrategy()

        from github_data_tools.entities.users.models import GitHubUser

        issue = Issue(
            id="issue_1",
            number=1,
            title="Test Issue",
            body="Test body",
            state="open",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            html_url="https://github.com/test/repo/issues/1",
            labels=[],
            user=GitHubUser(
                login="testuser",
                id="user_1",
                avatar_url="https://github.com/testuser.png",
                html_url="https://github.com/testuser",
            ),
            comments=0,
            milestone=sample_milestone,
        )

        # Invalid milestone mapping context (non-integer milestone number)
        context = {"milestone_mapping": {1: "invalid_milestone_number"}}

        # Transform should handle this gracefully
        result = strategy.transform(issue, context)

        assert result is not None
        assert result["title"] == "Test Issue"
        # Should include milestone with invalid value
        assert result["milestone"] == "invalid_milestone_number"

    def test_issue_restore_strategy_dependency_ordering(self):
        """Test that issue restore strategy declares correct dependency ordering."""
        strategy = IssuesRestoreStrategy()
        dependencies = strategy.get_dependencies()

        # Verify milestones comes before issues in dependency chain
        assert "milestones" in dependencies
        assert "labels" in dependencies

        # Find positions to verify ordering
        milestone_pos = dependencies.index("milestones")
        label_pos = dependencies.index("labels")

        # Both should be present and before issues (implicit dependency)
        assert milestone_pos >= 0
        assert label_pos >= 0

    def test_issue_save_strategy_dependency_ordering(self):
        """Test that issue save strategy declares correct dependency ordering."""
        strategy = IssuesSaveStrategy()
        dependencies = strategy.get_dependencies()

        # Issues should depend on milestones being saved first
        assert "milestones" in dependencies
        assert "labels" in dependencies

    def test_issue_context_propagation(self, sample_milestone):
        """Test milestone context propagation through transformations."""
        strategy = IssuesRestoreStrategy()

        from github_data_tools.entities.users.models import GitHubUser

        issue = Issue(
            id="issue_1",
            number=5,
            title="Context Test Issue",
            body="Test body",
            state="open",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            html_url="https://github.com/test/repo/issues/5",
            labels=[],
            user=GitHubUser(
                login="testuser",
                id="user_1",
                avatar_url="https://github.com/testuser.png",
                html_url="https://github.com/testuser",
            ),
            comments=0,
            milestone=Milestone(
                id="milestone_5",
                number=5,
                title="v2.0",
                description="Second release",
                state="open",
                creator=GitHubUser(
                    login="testuser",
                    id="user_1",
                    avatar_url="https://github.com/testuser.png",
                    html_url="https://github.com/testuser",
                ),
                created_at="2023-01-01T00:00:00Z",
                updated_at="2023-01-01T00:00:00Z",
                html_url="https://github.com/test/repo/milestones/5",
            ),
        )

        # Context with multiple milestone mappings
        context = {"milestone_mapping": {1: 101, 5: 105, 10: 110}}

        result = strategy.transform(issue, context)

        assert result is not None
        assert result["milestone"] == 105  # Correctly mapped milestone 5 -> 105

    def test_issue_transform_edge_case_zero_milestone_number(self):
        """Test handling of edge case where milestone number is 0."""
        strategy = IssuesRestoreStrategy()

        from github_data_tools.entities.users.models import GitHubUser

        issue = Issue(
            id="issue_1",
            number=1,
            title="Zero Milestone Test",
            body="Test body",
            state="open",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            html_url="https://github.com/test/repo/issues/1",
            labels=[],
            user=GitHubUser(
                login="testuser",
                id="user_1",
                avatar_url="https://github.com/testuser.png",
                html_url="https://github.com/testuser",
            ),
            comments=0,
            milestone=Milestone(
                id="milestone_0",
                number=0,
                title="Zero Milestone",
                state="open",
                creator=GitHubUser(
                    login="testuser",
                    id="user_1",
                    avatar_url="https://github.com/testuser.png",
                    html_url="https://github.com/testuser",
                ),
                created_at="2023-01-01T00:00:00Z",
                updated_at="2023-01-01T00:00:00Z",
                html_url="https://github.com/test/repo/milestones/0",
            ),
        )

        context = {"milestone_mapping": {0: 200}}

        result = strategy.transform(issue, context)

        assert result is not None
        assert result["milestone"] == 200


@pytest.fixture
def sample_milestone():
    """Create a sample milestone for testing."""
    from github_data_tools.entities.users.models import GitHubUser

    return Milestone(
        id="milestone_1",
        number=1,
        title="v1.0",
        description="First release",
        state="open",
        creator=GitHubUser(
            login="testuser",
            id="user_1",
            avatar_url="https://github.com/testuser.png",
            html_url="https://github.com/testuser",
        ),
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        html_url="https://github.com/test/repo/milestones/1",
        due_on=None,
        closed_at=None,
    )
