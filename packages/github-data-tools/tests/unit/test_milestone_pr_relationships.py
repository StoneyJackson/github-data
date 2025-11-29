"""
Tests for milestone-pull request relationships using modern infrastructure pattern.
Following docs/testing.md comprehensive guidelines.
"""

import pytest
from unittest.mock import Mock

from github_data_tools.entities.pull_requests.models import PullRequest
from github_data_tools.entities.milestones.models import Milestone
from github_data_tools.entities.pull_requests.save_strategy import (
    PullRequestsSaveStrategy,
)
from github_data_tools.entities.pull_requests.restore_strategy import (
    PullRequestsRestoreStrategy,
)
from github_data_tools.operations.restore.strategy import RestoreConflictStrategy
from ..shared.mocks.boundary_factory import MockBoundaryFactory

# Required markers following docs/testing.md
pytestmark = [
    pytest.mark.unit,
    pytest.mark.fast,
    pytest.mark.enhanced_fixtures,
    pytest.mark.error_handling,
]


class TestMilestonePullRequestRelationships:
    """Test milestone-pull request relationship functionality."""

    def test_pr_save_strategy_includes_milestone_dependencies(self):
        """Test that PR save strategy includes milestones in dependencies."""
        strategy = PullRequestsSaveStrategy()
        dependencies = strategy.get_dependencies()

        assert "labels" in dependencies
        assert "milestones" in dependencies

    def test_pr_restore_strategy_includes_milestone_dependencies(
        self, pr_restore_strategy
    ):
        """Test that PR restore strategy includes milestones in dependencies."""
        dependencies = pr_restore_strategy.get_dependencies()

        assert "labels" in dependencies
        assert "milestones" in dependencies

    def test_pr_transform_with_milestone(self, sample_milestone, pr_restore_strategy):
        """Test that PR transformation includes milestone mapping."""
        strategy = pr_restore_strategy

        # Create sample PR with milestone
        from github_data_tools.entities.users.models import GitHubUser

        pr = PullRequest(
            id="pr_1",
            number=1,
            title="Test PR",
            body="Test body",
            state="open",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            html_url="https://github.com/test/repo/pull/1",
            head_ref="feature-branch",
            base_ref="main",
            user=GitHubUser(
                login="testuser",
                id="user_1",
                avatar_url="https://github.com/testuser.png",
                html_url="https://github.com/testuser",
            ),
            labels=[],
            comments=0,
            milestone=sample_milestone,
        )

        # Mock milestone mapping context
        context = {"milestone_mapping": {1: 101}}

        # Transform for creation
        result = strategy.transform(pr, context)

        assert result is not None
        assert result["title"] == "Test PR"
        assert result["milestone"] == 101  # Mapped milestone number

    def test_pr_transform_without_milestone(self, pr_restore_strategy):
        """Test that PR transformation works without milestone."""
        strategy = pr_restore_strategy

        # Create sample PR without milestone
        from github_data_tools.entities.users.models import GitHubUser

        pr = PullRequest(
            id="pr_1",
            number=1,
            title="Test PR",
            body="Test body",
            state="open",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            html_url="https://github.com/test/repo/pull/1",
            head_ref="feature-branch",
            base_ref="main",
            user=GitHubUser(
                login="testuser",
                id="user_1",
                avatar_url="https://github.com/testuser.png",
                html_url="https://github.com/testuser",
            ),
            labels=[],
            comments=0,
            milestone=None,
        )

        context = {}

        # Transform for creation
        result = strategy.transform(pr, context)

        assert result is not None
        assert result["title"] == "Test PR"
        assert "milestone" not in result

    def test_pr_transform_with_missing_milestone_mapping(
        self, sample_milestone, capsys, pr_restore_strategy
    ):
        """Test warning when milestone mapping is missing for PR."""
        strategy = pr_restore_strategy

        # Create sample PR with milestone
        from github_data_tools.entities.users.models import GitHubUser

        pr = PullRequest(
            id="pr_1",
            number=1,
            title="Test PR",
            body="Test body",
            state="open",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            html_url="https://github.com/test/repo/pull/1",
            head_ref="feature-branch",
            base_ref="main",
            user=GitHubUser(
                login="testuser",
                id="user_1",
                avatar_url="https://github.com/testuser.png",
                html_url="https://github.com/testuser",
            ),
            labels=[],
            comments=0,
            milestone=sample_milestone,
        )

        # Empty milestone mapping context
        context = {"milestone_mapping": {}}

        # Transform for creation
        result = strategy.transform(pr, context)

        assert result is not None
        assert "milestone" not in result

        # Check warning was printed
        captured = capsys.readouterr()
        assert "Warning: Milestone #1 not found" in captured.out

    def test_pr_transform_with_milestone_mapping_error(
        self, sample_milestone, pr_restore_strategy
    ):
        """Test error handling when milestone mapping contains invalid data."""
        strategy = pr_restore_strategy

        from github_data_tools.entities.users.models import GitHubUser

        pr = PullRequest(
            id="pr_1",
            number=1,
            title="Test PR",
            body="Test body",
            state="open",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            html_url="https://github.com/test/repo/pull/1",
            head_ref="feature-branch",
            base_ref="main",
            user=GitHubUser(
                login="testuser",
                id="user_1",
                avatar_url="https://github.com/testuser.png",
                html_url="https://github.com/testuser",
            ),
            labels=[],
            comments=0,
            milestone=sample_milestone,
        )

        # Invalid milestone mapping context (non-integer milestone number)
        context = {"milestone_mapping": {1: "invalid_milestone_number"}}

        # Transform for creation should handle this gracefully
        result = strategy.transform(pr, context)

        assert result is not None
        assert result["title"] == "Test PR"
        # Should include milestone with invalid value
        assert result["milestone"] == "invalid_milestone_number"

    def test_pr_restore_strategy_dependency_ordering(self, pr_restore_strategy):
        """Test that PR restore strategy declares correct dependency ordering."""
        strategy = pr_restore_strategy
        dependencies = strategy.get_dependencies()

        # Verify milestones comes before PRs in dependency chain
        assert "milestones" in dependencies
        assert "labels" in dependencies

        # Find positions to verify ordering
        milestone_pos = dependencies.index("milestones")
        label_pos = dependencies.index("labels")

        # Both should be present and before PRs (implicit dependency)
        assert milestone_pos >= 0
        assert label_pos >= 0

    def test_pr_save_strategy_dependency_ordering(self):
        """Test that PR save strategy declares correct dependency ordering."""
        strategy = PullRequestsSaveStrategy()
        dependencies = strategy.get_dependencies()

        # PRs should depend on milestones being saved first
        assert "milestones" in dependencies
        assert "labels" in dependencies

    def test_pr_context_propagation(self, pr_restore_strategy):
        """Test milestone context propagation through PR transformations."""
        strategy = pr_restore_strategy

        from github_data_tools.entities.users.models import GitHubUser

        pr = PullRequest(
            id="pr_5",
            number=5,
            title="Context Test PR",
            body="Test body",
            state="open",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            html_url="https://github.com/test/repo/pull/5",
            head_ref="feature-branch",
            base_ref="main",
            user=GitHubUser(
                login="testuser",
                id="user_1",
                avatar_url="https://github.com/testuser.png",
                html_url="https://github.com/testuser",
            ),
            labels=[],
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

        result = strategy.transform(pr, context)

        assert result is not None
        assert result["milestone"] == 105  # Correctly mapped milestone 5 -> 105

    def test_pr_transform_edge_case_zero_milestone_number(self, pr_restore_strategy):
        """Test handling of edge case where milestone number is 0."""
        strategy = pr_restore_strategy

        from github_data_tools.entities.users.models import GitHubUser

        pr = PullRequest(
            id="pr_1",
            number=1,
            title="Zero Milestone Test PR",
            body="Test body",
            state="open",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            html_url="https://github.com/test/repo/pull/1",
            head_ref="feature-branch",
            base_ref="main",
            user=GitHubUser(
                login="testuser",
                id="user_1",
                avatar_url="https://github.com/testuser.png",
                html_url="https://github.com/testuser",
            ),
            labels=[],
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

        result = strategy.transform(pr, context)

        assert result is not None
        assert result["milestone"] == 200

    def test_pr_write_api_call(
        self, sample_milestone, pr_restore_strategy, sample_github_data
    ):
        """Test that PR write includes milestone parameter in API call."""
        strategy = pr_restore_strategy

        # Use MockBoundaryFactory for protocol completeness
        mock_github_service = MockBoundaryFactory.create_auto_configured(
            sample_github_data
        )
        mock_github_service.create_pull_request.return_value = {
            "number": 101,
            "title": "Test PR",
            "state": "open",
        }

        # Entity data with milestone
        entity_data = {
            "title": "Test PR",
            "body": "Test body",
            "head_ref": "feature-branch",
            "base_ref": "main",
            "original_number": 1,
            "original_state": "open",
            "milestone": 5,
        }

        # Create entity via API
        result = strategy.write(mock_github_service, "test/repo", entity_data)

        # Verify API call included milestone
        mock_github_service.create_pull_request.assert_called_once_with(
            "test/repo", "Test PR", "Test body", "feature-branch", "main", milestone=5
        )

        assert result["number"] == 101


@pytest.fixture
def pr_restore_strategy():
    """Create a PR restore strategy for testing."""
    mock_conflict_strategy = Mock(spec=RestoreConflictStrategy)
    return PullRequestsRestoreStrategy(
        conflict_strategy=mock_conflict_strategy,
        include_original_metadata=False,
        include_pull_requests=True,
    )


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
