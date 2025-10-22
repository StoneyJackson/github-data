"""
Integration tests for milestone save/restore complete cycles.
Following docs/testing.md comprehensive guidelines.
"""

import pytest
import json
from unittest.mock import Mock
from datetime import datetime

from src.entities.milestones.models import Milestone
from src.entities.issues.models import Issue
from src.entities.pull_requests.models import PullRequest
from src.entities.users.models import GitHubUser
from src.operations.save.strategies.milestones_strategy import MilestonesSaveStrategy
from src.operations.restore.strategies.milestones_strategy import (
    MilestonesRestoreStrategy,
)
from src.operations.restore.strategies.issues_strategy import IssuesRestoreStrategy
from src.operations.restore.strategies.pull_requests_strategy import (
    PullRequestsRestoreStrategy,
)

# Required markers following docs/testing.md
pytestmark = [
    pytest.mark.integration,
    pytest.mark.medium,
    pytest.mark.milestones,
    pytest.mark.milestone_integration,
    pytest.mark.save_workflow,
    pytest.mark.restore_workflow,
    pytest.mark.end_to_end,
    pytest.mark.enhanced_fixtures,
]


class TestMilestoneSaveRestoreIntegration:
    """Integration tests for complete milestone save/restore cycles."""

    def test_milestone_save_restore_cycle_basic(
        self, tmp_path, sample_milestones, sample_github_data
    ):
        """Test basic save/restore cycle with milestones only."""
        # Setup
        save_path = tmp_path / "save"
        save_path.mkdir()

        # Mock storage service
        mock_storage = Mock()
        saved_data = []

        def mock_write_data(file_path, data):
            saved_data.extend(data)
            # Simulate actual file creation
            with open(file_path, "w") as f:
                json.dump(
                    [milestone.model_dump() for milestone in data], f, default=str
                )

        mock_storage.write.side_effect = mock_write_data
        mock_storage.read.return_value = sample_milestones

        # SAVE PHASE
        save_strategy = MilestonesSaveStrategy()

        # Simulate save operation
        save_strategy.transform(sample_milestones, {})
        milestone_file = save_path / "milestones.json"
        mock_write_data(milestone_file, sample_milestones)

        # Verify file was created
        assert milestone_file.exists()

        # RESTORE PHASE
        restore_strategy = MilestonesRestoreStrategy()

        # Mock GitHub service for restore
        mock_github_service = Mock()
        mock_github_service.create_milestone.side_effect = [
            {"number": 101, "title": "v1.0"},
            {"number": 102, "title": "v2.0"},
        ]

        # Load data
        loaded_milestones = restore_strategy.read(str(save_path), mock_storage)

        # Restore milestones
        context = {}
        for i, milestone in enumerate(loaded_milestones):
            transform_data = restore_strategy.transform(milestone, context)
            created_data = restore_strategy.write(
                mock_github_service, "test/repo", transform_data
            )
            restore_strategy.post_create_actions(
                mock_github_service, "test/repo", milestone, created_data, context
            )

        # Verify restore results
        assert len(loaded_milestones) == 2
        assert mock_github_service.create_milestone.call_count == 2

        # Verify milestone mapping was created
        assert "milestone_mapping" in context
        assert context["milestone_mapping"][1] == 101
        assert context["milestone_mapping"][2] == 102

    def test_milestone_issue_save_restore_cycle_with_relationships(
        self, tmp_path, sample_milestones, sample_github_user
    ):
        """Test save/restore cycle with issues that have milestone associations."""
        # Setup
        save_path = tmp_path / "save"
        save_path.mkdir()

        # Create issues with milestone relationships
        issues_with_milestones = [
            Issue(
                id="issue_1",
                number=1,
                title="First Issue",
                body="Issue with milestone",
                state="open",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                html_url="https://github.com/test/repo/issues/1",
                labels=[],
                user=sample_github_user,
                comments=0,
                milestone=sample_milestones[0],  # v1.0 milestone
            ),
            Issue(
                id="issue_2",
                number=2,
                title="Second Issue",
                body="Issue without milestone",
                state="open",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                html_url="https://github.com/test/repo/issues/2",
                labels=[],
                user=sample_github_user,
                comments=0,
                milestone=None,
            ),
            Issue(
                id="issue_3",
                number=3,
                title="Third Issue",
                body="Issue with different milestone",
                state="closed",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                html_url="https://github.com/test/repo/issues/3",
                labels=[],
                user=sample_github_user,
                comments=0,
                milestone=sample_milestones[1],  # v2.0 milestone
            ),
        ]

        # Mock storage and GitHub services
        mock_storage = Mock()
        mock_github_service = Mock()

        # Setup storage mocks
        def mock_write_data(file_path, data):
            with open(file_path, "w") as f:
                json.dump([item.model_dump() for item in data], f, default=str)

        mock_storage.write.side_effect = mock_write_data

        def mock_read_data(file_path, model_class):
            if "milestones.json" in str(file_path):
                return sample_milestones
            elif "issues.json" in str(file_path):
                return issues_with_milestones
            return []

        mock_storage.read.side_effect = mock_read_data

        # Setup GitHub service mocks
        mock_github_service.create_milestone.side_effect = [
            {"number": 101, "title": "v1.0"},
            {"number": 102, "title": "v2.0"},
        ]
        mock_github_service.create_issue.side_effect = [
            {"number": 201, "title": "First Issue"},
            {"number": 202, "title": "Second Issue"},
            {"number": 203, "title": "Third Issue"},
        ]

        # SAVE PHASE

        # Save milestones first (dependency order)
        milestone_file = save_path / "milestones.json"
        mock_write_data(milestone_file, sample_milestones)

        # Save issues
        issue_file = save_path / "issues.json"
        mock_write_data(issue_file, issues_with_milestones)

        # RESTORE PHASE
        milestone_restore_strategy = MilestonesRestoreStrategy()
        issue_restore_strategy = IssuesRestoreStrategy()

        context = {}

        # Restore milestones first (dependency order)
        loaded_milestones = milestone_restore_strategy.read(
            str(save_path), mock_storage
        )
        for milestone in loaded_milestones:
            transform_data = milestone_restore_strategy.transform(milestone, context)
            created_data = milestone_restore_strategy.write(
                mock_github_service, "test/repo", transform_data
            )
            milestone_restore_strategy.post_create_actions(
                mock_github_service, "test/repo", milestone, created_data, context
            )

        # Restore issues with milestone relationships
        loaded_issues = issue_restore_strategy.read(str(save_path), mock_storage)
        for issue in loaded_issues:
            transform_data = issue_restore_strategy.transform(issue, context)
            created_data = issue_restore_strategy.write(
                mock_github_service, "test/repo", transform_data
            )

        # Verify milestone mapping was used correctly
        assert "milestone_mapping" in context
        assert context["milestone_mapping"][1] == 101  # v1.0: 1 -> 101
        assert context["milestone_mapping"][2] == 102  # v2.0: 2 -> 102

        # Verify issues were created with correct milestone mappings
        issue_create_calls = mock_github_service.create_issue.call_args_list

        # First issue should have milestone 101 (mapped from 1)
        first_call_kwargs = issue_create_calls[0].kwargs
        assert first_call_kwargs.get("milestone") == 101

        # Second issue should have no milestone
        second_call_kwargs = issue_create_calls[1].kwargs
        assert (
            "milestone" not in second_call_kwargs
            or second_call_kwargs.get("milestone") is None
        )

        # Third issue should have milestone 102 (mapped from 2)
        third_call_kwargs = issue_create_calls[2].kwargs
        assert third_call_kwargs.get("milestone") == 102

    def test_milestone_pr_save_restore_cycle_with_relationships(
        self, tmp_path, sample_milestones, sample_github_user
    ):
        """Test save/restore cycle with PRs that have milestone associations."""
        from src.operations.restore.strategy import RestoreConflictStrategy
        from unittest.mock import Mock

        # Setup
        save_path = tmp_path / "save"
        save_path.mkdir()

        # Create PRs with milestone relationships
        prs_with_milestones = [
            PullRequest(
                id="pr_1",
                number=1,
                title="First PR",
                body="PR with milestone",
                state="open",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                html_url="https://github.com/test/repo/pull/1",
                head_ref="feature-1",
                base_ref="main",
                labels=[],
                comments=0,
                user=sample_github_user,
                milestone=sample_milestones[0],  # v1.0 milestone
            ),
            PullRequest(
                id="pr_2",
                number=2,
                title="Second PR",
                body="PR with different milestone",
                state="closed",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                html_url="https://github.com/test/repo/pull/2",
                head_ref="feature-2",
                base_ref="main",
                labels=[],
                comments=0,
                user=sample_github_user,
                milestone=sample_milestones[1],  # v2.0 milestone
            ),
        ]

        # Mock services
        mock_storage = Mock()
        mock_github_service = Mock()

        # Setup mocks
        def mock_write_data(file_path, data):
            with open(file_path, "w") as f:
                json.dump([item.model_dump() for item in data], f, default=str)

        mock_storage.write.side_effect = mock_write_data

        # Create the actual files so they exist
        milestones_file = save_path / "milestones.json"
        prs_file = save_path / "pull_requests.json"

        with open(milestones_file, "w") as f:
            json.dump([m.model_dump() for m in sample_milestones], f, default=str)
        with open(prs_file, "w") as f:
            json.dump([pr.model_dump() for pr in prs_with_milestones], f, default=str)

        def mock_read_data(file_path, model_class):
            if "milestones.json" in str(file_path):
                return sample_milestones
            elif "pull_requests.json" in str(file_path):
                return prs_with_milestones
            return []

        mock_storage.read.side_effect = mock_read_data

        mock_github_service.create_milestone.side_effect = [
            {"number": 101, "title": "v1.0"},
            {"number": 102, "title": "v2.0"},
        ]
        mock_github_service.create_pull_request.side_effect = [
            {"number": 301, "title": "First PR"},
            {"number": 302, "title": "Second PR"},
        ]

        # SAVE AND RESTORE
        milestone_restore_strategy = MilestonesRestoreStrategy()

        mock_conflict_strategy = Mock(spec=RestoreConflictStrategy)
        pr_restore_strategy = PullRequestsRestoreStrategy(
            conflict_strategy=mock_conflict_strategy
        )

        context = {}

        # Restore milestones first
        loaded_milestones = milestone_restore_strategy.read(
            str(save_path), mock_storage
        )
        for milestone in loaded_milestones:
            transform_data = milestone_restore_strategy.transform(milestone, context)
            created_data = milestone_restore_strategy.write(
                mock_github_service, "test/repo", transform_data
            )
            milestone_restore_strategy.post_create_actions(
                mock_github_service, "test/repo", milestone, created_data, context
            )

        # Restore PRs with milestone relationships
        loaded_prs = pr_restore_strategy.read(str(save_path), mock_storage)
        for pr in loaded_prs:
            transform_data = pr_restore_strategy.transform(pr, context)
            created_data = pr_restore_strategy.write(
                mock_github_service, "test/repo", transform_data
            )

        # Verify PRs were created with correct milestone mappings
        pr_create_calls = mock_github_service.create_pull_request.call_args_list

        # First PR should have milestone 101 (mapped from 1)
        first_call_kwargs = pr_create_calls[0].kwargs
        assert first_call_kwargs.get("milestone") == 101

        # Second PR should have milestone 102 (mapped from 2)
        second_call_kwargs = pr_create_calls[1].kwargs
        assert second_call_kwargs.get("milestone") == 102

    def test_complex_milestone_scenario_mixed_states(
        self, tmp_path, sample_github_user
    ):
        """Test complex scenario with multiple milestones in mixed states."""
        # Setup complex milestone scenario
        complex_milestones = [
            Milestone(
                id="milestone_1",
                number=1,
                title="v1.0 Release",
                description="First major release",
                state="closed",
                creator=sample_github_user,
                created_at=datetime(2023, 1, 1),
                updated_at=datetime(2023, 3, 1),
                due_on=datetime(2023, 2, 28),
                closed_at=datetime(2023, 3, 1),
                open_issues=0,
                closed_issues=5,
                html_url="https://github.com/test/repo/milestones/1",
            ),
            Milestone(
                id="milestone_2",
                number=2,
                title="v2.0 Release",
                description="Second major release",
                state="open",
                creator=sample_github_user,
                created_at=datetime(2023, 3, 1),
                updated_at=datetime(2023, 4, 1),
                due_on=datetime(2023, 6, 30),
                closed_at=None,
                open_issues=3,
                closed_issues=2,
                html_url="https://github.com/test/repo/milestones/2",
            ),
            Milestone(
                id="milestone_3",
                number=3,
                title="Hotfix v1.1",
                description=None,
                state="open",
                creator=sample_github_user,
                created_at=datetime(2023, 3, 15),
                updated_at=datetime(2023, 3, 20),
                due_on=None,
                closed_at=None,
                open_issues=1,
                closed_issues=0,
                html_url="https://github.com/test/repo/milestones/3",
            ),
        ]

        # Create the milestones file so read doesn't return empty list
        save_path = tmp_path / "save"
        save_path.mkdir()
        milestones_file = save_path / "milestones.json"

        # Mock services
        mock_storage = Mock()
        mock_github_service = Mock()
        mock_storage.read.return_value = complex_milestones

        # Create the actual file so it exists
        with open(milestones_file, "w") as f:
            json.dump([m.model_dump() for m in complex_milestones], f, default=str)

        # Setup GitHub service responses for different milestone states
        mock_github_service.create_milestone.side_effect = [
            {"number": 101, "title": "v1.0 Release"},
            {"number": 102, "title": "v2.0 Release"},
            {"number": 103, "title": "Hotfix v1.1"},
        ]

        # Test restore with mixed milestone states
        restore_strategy = MilestonesRestoreStrategy()

        loaded_milestones = restore_strategy.read(str(save_path), mock_storage)
        context = {}

        for milestone in loaded_milestones:
            transform_data = restore_strategy.transform(milestone, context)

            # Verify transform includes appropriate fields based on milestone state
            assert transform_data["title"] == milestone.title
            assert transform_data["state"] == milestone.state

            if milestone.description:
                assert transform_data["description"] == milestone.description
            else:
                assert "description" not in transform_data

            if milestone.due_on:
                assert transform_data["due_on"] == milestone.due_on.isoformat()
            else:
                assert "due_on" not in transform_data

            # Create milestone
            created_data = restore_strategy.write(
                mock_github_service, "test/repo", transform_data
            )
            restore_strategy.post_create_actions(
                mock_github_service, "test/repo", milestone, created_data, context
            )

        # Verify all milestones were processed and mapped correctly
        assert "milestone_mapping" in context
        assert len(context["milestone_mapping"]) == 3
        assert context["milestone_mapping"][1] == 101
        assert context["milestone_mapping"][2] == 102
        assert context["milestone_mapping"][3] == 103

    def test_save_restore_data_integrity_validation(self, tmp_path, sample_milestones):
        """Test that data integrity is maintained through save/restore cycle."""
        # Save milestones to actual files
        save_path = tmp_path / "save"
        save_path.mkdir()

        milestone_file = save_path / "milestones.json"

        # Manual save to file
        with open(milestone_file, "w") as f:
            json.dump(
                [milestone.model_dump() for milestone in sample_milestones],
                f,
                default=str,
            )

        # Verify file contents
        with open(milestone_file, "r") as f:
            saved_data = json.load(f)

        assert len(saved_data) == 2
        assert saved_data[0]["title"] == "v1.0"
        assert saved_data[1]["title"] == "v2.0"

        # Mock storage service for restore
        mock_storage = Mock()
        mock_storage.read.return_value = sample_milestones

        # Test data integrity through restore
        restore_strategy = MilestonesRestoreStrategy()
        loaded_milestones = restore_strategy.read(str(save_path), mock_storage)

        # Verify loaded data matches original
        assert len(loaded_milestones) == 2
        assert loaded_milestones[0].title == sample_milestones[0].title
        assert loaded_milestones[1].title == sample_milestones[1].title
        assert loaded_milestones[0].state == sample_milestones[0].state
        assert loaded_milestones[1].state == sample_milestones[1].state


@pytest.fixture
def sample_github_user():
    """Create a sample GitHub user for testing."""
    return GitHubUser(
        login="testuser",
        id="user_123",
        avatar_url="https://github.com/testuser.png",
        html_url="https://github.com/testuser",
    )


@pytest.fixture
def sample_milestones(sample_github_user):
    """Create sample milestones for testing."""
    return [
        Milestone(
            id="milestone_1",
            number=1,
            title="v1.0",
            description="First release",
            state="closed",
            creator=sample_github_user,
            created_at=datetime(2023, 1, 1),
            updated_at=datetime(2023, 2, 1),
            due_on=datetime(2023, 1, 31),
            closed_at=datetime(2023, 2, 1),
            open_issues=0,
            closed_issues=3,
            html_url="https://github.com/test/repo/milestones/1",
        ),
        Milestone(
            id="milestone_2",
            number=2,
            title="v2.0",
            description="Second release",
            state="open",
            creator=sample_github_user,
            created_at=datetime(2023, 2, 1),
            updated_at=datetime(2023, 3, 1),
            due_on=datetime(2023, 6, 30),
            closed_at=None,
            open_issues=2,
            closed_issues=1,
            html_url="https://github.com/test/repo/milestones/2",
        ),
    ]
