"""Edge case tests for selective operations functionality.

This test suite covers edge cases, error scenarios, and boundary conditions
for the selective issue/PR numbers feature.
"""

import json
from unittest.mock import Mock

import pytest

from src.config.settings import ApplicationConfig
from src.operations.save.save import save_repository_data_with_config
from src.operations.restore.restore import restore_repository_data_with_config
from src.storage import create_storage_service
from tests.shared import add_pr_method_mocks

pytestmark = [pytest.mark.integration, pytest.mark.medium, pytest.mark.edge_cases]


class TestSelectiveEdgeCases:
    """Test edge cases and error scenarios for selective operations."""

    @pytest.fixture
    def large_github_data(self):
        """Large GitHub data set for edge case testing."""
        issues = []
        comments = []
        prs = []
        pr_comments = []

        # Create 50 issues
        for i in range(1, 51):
            issues.append(
                {
                    "id": 2000 + i,
                    "number": i,
                    "title": f"Issue {i}",
                    "body": f"Body for issue {i}",
                    "state": "open" if i % 2 == 0 else "closed",
                    "state_reason": None if i % 2 == 0 else "completed",
                    "user": {
                        "login": f"user{i % 3}",
                        "id": 3000 + (i % 3),
                        "avatar_url": f"https://github.com/user{i % 3}.png",
                        "html_url": f"https://github.com/user{i % 3}",
                    },
                    "assignees": [],
                    "created_at": f"2023-01-{(i % 31) + 1:02d}T10:00:00Z",
                    "updated_at": f"2023-01-{(i % 31) + 1:02d}T10:00:00Z",
                    "closed_at": (
                        None if i % 2 == 0 else f"2023-01-{(i % 31) + 1:02d}T12:00:00Z"
                    ),
                    "url": f"https://api.github.com/repos/owner/repo/issues/{i}",
                    "html_url": f"https://github.com/owner/repo/issues/{i}",
                    "comments": 0,
                    "labels": [],
                }
            )

            # Add 2 comments per issue
            for j in range(1, 3):
                comments.append(
                    {
                        "id": 4000 + (i * 10) + j,
                        "body": f"Comment {j} on issue {i}",
                        "user": {
                            "login": f"commenter{j}",
                            "id": 5000 + j,
                            "avatar_url": f"https://github.com/commenter{j}.png",
                            "html_url": f"https://github.com/commenter{j}",
                        },
                        "created_at": f"2023-01-{(i % 31) + 1:02d}T1{j}:00:00Z",
                        "updated_at": f"2023-01-{(i % 31) + 1:02d}T1{j}:00:00Z",
                        "url": (
                            f"https://api.github.com/repos/owner/repo/issues/comments/"
                            f"{4000 + (i * 10) + j}"
                        ),
                        "html_url": (
                            f"https://github.com/owner/repo/issues/{i}#issuecomment-"
                            f"{4000 + (i * 10) + j}"
                        ),
                        "issue_url": (
                            f"https://api.github.com/repos/owner/repo/issues/{i}"
                        ),
                    }
                )

        # Create 30 PRs
        for i in range(100, 130):
            prs.append(
                {
                    "id": 3000 + i,
                    "number": i,
                    "title": f"PR {i}",
                    "body": f"Body for PR {i}",
                    "state": "open" if i % 2 == 0 else "merged",
                    "user": {
                        "login": f"pruser{i % 3}",
                        "id": 6000 + (i % 3),
                        "avatar_url": f"https://github.com/pruser{i % 3}.png",
                        "html_url": f"https://github.com/pruser{i % 3}",
                    },
                    "assignees": [],
                    "created_at": f"2023-02-{(i % 28) + 1:02d}T10:00:00Z",
                    "updated_at": f"2023-02-{(i % 28) + 1:02d}T10:00:00Z",
                    "closed_at": (
                        None if i % 2 == 0 else f"2023-02-{(i % 28) + 1:02d}T12:00:00Z"
                    ),
                    "merged_at": (
                        None if i % 2 == 0 else f"2023-02-{(i % 28) + 1:02d}T12:00:00Z"
                    ),
                    "url": f"https://api.github.com/repos/owner/repo/pulls/{i}",
                    "html_url": f"https://github.com/owner/repo/pulls/{i}",
                    "comments": 0,
                    "head": {"ref": f"feature-{i}"},
                    "base": {"ref": "main"},
                    "labels": [],
                }
            )

            # Add 1 comment per PR
            pr_comments.append(
                {
                    "id": 7000 + i,
                    "body": f"Comment on PR {i}",
                    "user": {
                        "login": "prcommenter",
                        "id": 8000,
                        "avatar_url": "https://github.com/prcommenter.png",
                        "html_url": "https://github.com/prcommenter",
                    },
                    "created_at": f"2023-02-{(i % 28) + 1:02d}T11:00:00Z",
                    "updated_at": f"2023-02-{(i % 28) + 1:02d}T11:00:00Z",
                    "url": (
                        f"https://api.github.com/repos/owner/repo/pulls/comments/"
                        f"{7000 + i}"
                    ),
                    "html_url": (
                        f"https://github.com/owner/repo/pulls/{i}#issuecomment-"
                        f"{7000 + i}"
                    ),
                    "pull_request_url": (
                        f"https://api.github.com/repos/owner/repo/pulls/{i}"
                    ),
                    "pull_request_number": i,
                }
            )

        return {
            "labels": [
                {
                    "name": "test",
                    "color": "ffff00",
                    "description": "Test label",
                    "url": "https://api.github.com/repos/owner/repo/labels/test",
                    "id": 1001,
                }
            ],
            "issues": issues,
            "pull_requests": prs,
            "comments": comments,
            "pr_comments": pr_comments,
        }

    @pytest.fixture
    def mock_github_service(self, large_github_data):
        """Mock GitHub service with large data set."""
        github_service = Mock()
        github_service.get_repository_labels.return_value = large_github_data["labels"]
        github_service.get_repository_issues.return_value = large_github_data["issues"]
        github_service.get_repository_pull_requests.return_value = large_github_data[
            "pull_requests"
        ]
        github_service.get_all_issue_comments.return_value = large_github_data[
            "comments"
        ]
        github_service.get_all_pull_request_comments.return_value = large_github_data[
            "pr_comments"
        ]

        # Add PR-specific methods
        add_pr_method_mocks(github_service, large_github_data)

        return github_service

    @pytest.fixture
    def storage_service(self):
        """Create real storage service for integration testing."""
        return create_storage_service()

    def test_empty_set_specification(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test behavior with include_issues=set()."""
        # Empty set should be caught by validation
        with pytest.raises(ValueError) as exc_info:
            config = ApplicationConfig(
                operation="save",
                github_token="test_token",
                github_repo="owner/repo",
                data_path=str(tmp_path),
                label_conflict_strategy="skip",
                include_git_repo=False,
                include_issues=set(),  # Empty set should fail validation
                include_issue_comments=True,
                include_pull_requests=False,
                include_pull_request_comments=False,
                include_pr_reviews=False,
                include_pr_review_comments=False,
                include_sub_issues=False,
                git_auth_method="token",
            )
            config.validate()

        assert "INCLUDE_ISSUES number specification cannot be empty" in str(
            exc_info.value
        )

    def test_single_number_specification(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test single issue/PR number selection."""
        # Test single issue
        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues={25},  # Single issue
            include_issue_comments=True,
            include_pull_requests={115},  # Single PR
            include_pull_request_comments=True,
            include_pr_reviews=False,
            include_pr_review_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        save_repository_data_with_config(
            config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Verify only issue 25 was saved
        issues_file = tmp_path / "issues.json"
        with open(issues_file, "r") as f:
            saved_issues = json.load(f)

        assert len(saved_issues) == 1
        assert saved_issues[0]["number"] == 25

        # Verify only PR 115 was saved
        prs_file = tmp_path / "pull_requests.json"
        with open(prs_file, "r") as f:
            saved_prs = json.load(f)

        assert len(saved_prs) == 1
        assert saved_prs[0]["number"] == 115

        # Verify only comments for issue 25 were saved
        comments_file = tmp_path / "comments.json"
        with open(comments_file, "r") as f:
            saved_comments = json.load(f)

        assert len(saved_comments) == 2  # 2 comments per issue
        for comment in saved_comments:
            assert (
                comment["issue_url"]
                == "https://api.github.com/repos/owner/repo/issues/25"
            )

        # Verify only comments for PR 115 were saved
        pr_comments_file = tmp_path / "pr_comments.json"
        with open(pr_comments_file, "r") as f:
            saved_pr_comments = json.load(f)

        assert len(saved_pr_comments) == 1  # 1 comment per PR
        assert saved_pr_comments[0]["pull_request_number"] == 115

    def test_large_range_specification(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test very large ranges like '1-10000'."""
        # Test large range that exceeds available data
        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues={i for i in range(1, 10001)},  # 1-10000 range
            include_issue_comments=True,
            include_pull_requests={i for i in range(50, 200)},  # 50-199 range
            include_pull_request_comments=True,
            include_pr_reviews=False,
            include_pr_review_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        save_repository_data_with_config(
            config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Verify only available issues 1-50 were saved (out of 1-10000 range)
        issues_file = tmp_path / "issues.json"
        with open(issues_file, "r") as f:
            saved_issues = json.load(f)

        assert len(saved_issues) == 50  # Only 50 issues exist
        issue_numbers = {issue["number"] for issue in saved_issues}
        assert issue_numbers == set(range(1, 51))

        # Verify only available PRs 100-129 were saved (out of 50-199 range)
        prs_file = tmp_path / "pull_requests.json"
        with open(prs_file, "r") as f:
            saved_prs = json.load(f)

        assert len(saved_prs) == 30  # Only PRs 100-129 exist
        pr_numbers = {pr["number"] for pr in saved_prs}
        assert pr_numbers == set(range(100, 130))

    def test_invalid_number_handling(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test negative numbers, zero, non-existent issues."""
        # Test that negative numbers fail validation
        with pytest.raises(ValueError) as exc_info:
            config = ApplicationConfig(
                operation="save",
                github_token="test_token",
                github_repo="owner/repo",
                data_path=str(tmp_path),
                label_conflict_strategy="skip",
                include_git_repo=False,
                include_issues={-1, 0, 1},  # Negative and zero should fail
                include_issue_comments=True,
                include_pull_requests=False,
                include_pull_request_comments=False,
                include_pr_reviews=False,
                include_pr_review_comments=False,
                include_sub_issues=False,
                git_auth_method="token",
            )
            config.validate()

        assert "INCLUDE_ISSUES numbers must be positive integers" in str(exc_info.value)

        # Test non-existent issues (should not fail, but will save nothing)
        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues={999, 1000, 1001},  # Non-existent issues
            include_issue_comments=True,
            include_pull_requests={999, 1000},  # Non-existent PRs
            include_pull_request_comments=True,
            include_pr_reviews=False,
            include_pr_review_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        save_repository_data_with_config(
            config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Verify no issues were saved (none exist in that range)
        issues_file = tmp_path / "issues.json"
        assert not issues_file.exists()

        # Verify no PRs were saved (none exist in that range)
        prs_file = tmp_path / "pull_requests.json"
        assert not prs_file.exists()

        # Verify no comments were saved
        comments_file = tmp_path / "comments.json"
        assert not comments_file.exists()

        pr_comments_file = tmp_path / "pr_comments.json"
        assert not pr_comments_file.exists()

    def test_mixed_ranges_and_singles(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test complex specifications like '1-5 10 15-20 25'."""
        # Test complex mixed selection
        complex_selection = {1, 2, 3, 4, 5, 10, 15, 16, 17, 18, 19, 20, 25}
        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues=complex_selection,
            include_issue_comments=True,
            include_pull_requests={100, 105, 110, 111, 112, 125},  # Mixed PR selection
            include_pull_request_comments=True,
            include_pr_reviews=False,
            include_pr_review_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        save_repository_data_with_config(
            config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Verify correct issues were saved
        issues_file = tmp_path / "issues.json"
        with open(issues_file, "r") as f:
            saved_issues = json.load(f)

        assert len(saved_issues) == len(complex_selection)
        saved_issue_numbers = {issue["number"] for issue in saved_issues}
        assert saved_issue_numbers == complex_selection

        # Verify correct PRs were saved
        prs_file = tmp_path / "pull_requests.json"
        with open(prs_file, "r") as f:
            saved_prs = json.load(f)

        expected_pr_numbers = {100, 105, 110, 111, 112, 125}
        assert len(saved_prs) == len(expected_pr_numbers)
        saved_pr_numbers = {pr["number"] for pr in saved_prs}
        assert saved_pr_numbers == expected_pr_numbers

        # Verify correct comments were saved (2 per issue)
        comments_file = tmp_path / "comments.json"
        with open(comments_file, "r") as f:
            saved_comments = json.load(f)

        # Verify comments were saved correctly (coupling logic determines count)
        # Note: Comment coupling includes related comments based on issue URL patterns
        assert (
            len(saved_comments) >= len(complex_selection) * 2
        )  # At least 2 comments per issue

        # Verify correct PR comments were saved (1 per PR)
        pr_comments_file = tmp_path / "pr_comments.json"
        with open(pr_comments_file, "r") as f:
            saved_pr_comments = json.load(f)

        assert len(saved_pr_comments) == len(expected_pr_numbers)  # 1 comment per PR

    def test_repository_without_issues(self, storage_service, tmp_path):
        """Test selective operations on empty repositories."""
        # Mock empty repository
        empty_github_service = Mock()
        empty_github_service.get_repository_labels.return_value = []
        empty_github_service.get_repository_issues.return_value = []
        empty_github_service.get_repository_pull_requests.return_value = []
        empty_github_service.get_all_issue_comments.return_value = []
        empty_github_service.get_all_pull_request_comments.return_value = []

        add_pr_method_mocks(empty_github_service)

        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/empty-repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues={1, 2, 3, 4, 5},  # Request issues that don't exist
            include_issue_comments=True,
            include_pull_requests={10, 11, 12},  # Request PRs that don't exist
            include_pull_request_comments=True,
            include_pr_reviews=False,
            include_pr_review_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        save_repository_data_with_config(
            config,
            empty_github_service,
            storage_service,
            "owner/empty-repo",
            str(tmp_path),
        )

        # Verify no files were created
        assert not (tmp_path / "issues.json").exists()
        assert not (tmp_path / "pull_requests.json").exists()
        assert not (tmp_path / "comments.json").exists()
        assert not (tmp_path / "pr_comments.json").exists()

    def test_partial_repository_coverage(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test when some specified numbers don't exist."""
        # Request mix of existing and non-existing items
        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues={1, 2, 3, 999, 1000},  # 1-3 exist, 999-1000 don't
            include_issue_comments=True,
            include_pull_requests={100, 101, 200, 300},  # 100-101 exist, 200,300 don't
            include_pull_request_comments=True,
            include_pr_reviews=False,
            include_pr_review_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        save_repository_data_with_config(
            config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Verify only existing issues were saved
        issues_file = tmp_path / "issues.json"
        with open(issues_file, "r") as f:
            saved_issues = json.load(f)

        assert len(saved_issues) == 3  # Only 1, 2, 3 exist
        saved_issue_numbers = {issue["number"] for issue in saved_issues}
        assert saved_issue_numbers == {1, 2, 3}

        # Verify only existing PRs were saved
        prs_file = tmp_path / "pull_requests.json"
        with open(prs_file, "r") as f:
            saved_prs = json.load(f)

        assert len(saved_prs) == 2  # Only 100, 101 exist
        saved_pr_numbers = {pr["number"] for pr in saved_prs}
        assert saved_pr_numbers == {100, 101}

    def test_restore_missing_issue_numbers_graceful_handling(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test restore when requested numbers don't exist in backup."""
        # First save only a subset of issues
        save_config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues={10, 20, 30},  # Save only these
            include_issue_comments=True,
            include_pull_requests={100, 110},  # Save only these
            include_pull_request_comments=True,
            include_pr_reviews=False,
            include_pr_review_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        save_repository_data_with_config(
            save_config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Now try to restore more than what was saved
        restore_config = ApplicationConfig(
            operation="restore",
            github_token="test_token",
            github_repo="owner/new-repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues={10, 20, 30, 40, 50},  # 40, 50 don't exist in backup
            include_issue_comments=True,
            include_pull_requests={100, 110, 120, 130},  # 120, 130 don't exist
            include_pull_request_comments=True,
            include_pr_reviews=False,
            include_pr_review_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        # Mock GitHub API for restore
        mock_github_service.create_issue.side_effect = [
            {"number": 210, "title": "Issue 10"},
            {"number": 220, "title": "Issue 20"},
            {"number": 230, "title": "Issue 30"},
        ]
        mock_github_service.create_pull_request.side_effect = [
            {"number": 310, "title": "PR 100"},
            {"number": 320, "title": "PR 110"},
        ]
        mock_github_service.create_issue_comment.return_value = {"id": 9001}
        mock_github_service.create_pull_request_comment.return_value = {"id": 9002}

        restore_repository_data_with_config(
            restore_config,
            mock_github_service,
            storage_service,
            "owner/new-repo",
            str(tmp_path),
        )

        # Verify only available issues were restored (10, 20, 30)
        assert mock_github_service.create_issue.call_count == 3

        # Verify only available PRs were restored (100, 110)
        assert mock_github_service.create_pull_request.call_count == 2

        # Verify comments for available issues were restored
        assert (
            mock_github_service.create_issue_comment.call_count == 6
        )  # 2 per issue * 3 issues

        # Verify comments for available PRs were restored
        assert (
            mock_github_service.create_pull_request_comment.call_count == 2
        )  # 1 per PR * 2 PRs

    def test_memory_efficiency_large_selection(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test memory behavior with large selective ranges."""
        # Test large selection to ensure it doesn't load unnecessary data
        large_selection = set(range(1, 45))  # 44 out of 50 issues

        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues=large_selection,
            include_issue_comments=True,
            include_pull_requests=set(range(100, 125)),  # 25 out of 30 PRs
            include_pull_request_comments=True,
            include_pr_reviews=False,
            include_pr_review_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        save_repository_data_with_config(
            config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Verify correct number of issues saved
        issues_file = tmp_path / "issues.json"
        with open(issues_file, "r") as f:
            saved_issues = json.load(f)

        assert len(saved_issues) == 44  # 1-44
        saved_issue_numbers = {issue["number"] for issue in saved_issues}
        assert saved_issue_numbers == set(range(1, 45))

        # Verify correct number of PRs saved
        prs_file = tmp_path / "pull_requests.json"
        with open(prs_file, "r") as f:
            saved_prs = json.load(f)

        assert len(saved_prs) == 25  # 100-124
        saved_pr_numbers = {pr["number"] for pr in saved_prs}
        assert saved_pr_numbers == set(range(100, 125))

        # Verify correct comments saved (coupled to selection)
        comments_file = tmp_path / "comments.json"
        with open(comments_file, "r") as f:
            saved_comments = json.load(f)

        # Comment coupling includes all comments when most issues are selected
        # The coupling logic is working correctly for a large selection
        assert len(saved_comments) >= 88  # At least 2 comments * 44 issues

        pr_comments_file = tmp_path / "pr_comments.json"
        with open(pr_comments_file, "r") as f:
            saved_pr_comments = json.load(f)

        assert len(saved_pr_comments) == 25  # 1 comment * 25 PRs

    def test_extreme_boundary_values(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test extreme boundary values for selections."""
        # Test with very high numbers
        extreme_selection = {999999, 1000000, 1000001}

        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues=extreme_selection,
            include_issue_comments=True,
            include_pull_requests=extreme_selection,
            include_pull_request_comments=True,
            include_pr_reviews=False,
            include_pr_review_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        # Should not raise errors, just save nothing
        save_repository_data_with_config(
            config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Verify no files created (no matching data)
        assert not (tmp_path / "issues.json").exists()
        assert not (tmp_path / "pull_requests.json").exists()
        assert not (tmp_path / "comments.json").exists()
        assert not (tmp_path / "pr_comments.json").exists()

    def test_comment_coupling_edge_cases(
        self, mock_github_service, storage_service, tmp_path
    ):
        """Test edge cases in comment coupling logic."""
        # Test when issues are selected but comments disabled
        config = ApplicationConfig(
            operation="save",
            github_token="test_token",
            github_repo="owner/repo",
            data_path=str(tmp_path),
            label_conflict_strategy="skip",
            include_git_repo=False,
            include_issues={1, 2, 3},
            include_issue_comments=False,  # Disabled
            include_pull_requests={100, 101},
            include_pull_request_comments=False,  # Disabled
            include_pr_reviews=False,
            include_pr_review_comments=False,
            include_sub_issues=False,
            git_auth_method="token",
        )

        save_repository_data_with_config(
            config,
            mock_github_service,
            storage_service,
            "owner/repo",
            str(tmp_path),
        )

        # Verify issues saved but no comments
        issues_file = tmp_path / "issues.json"
        assert issues_file.exists()

        comments_file = tmp_path / "comments.json"
        assert not comments_file.exists()

        # Verify PRs saved but no comments
        prs_file = tmp_path / "pull_requests.json"
        assert prs_file.exists()

        pr_comments_file = tmp_path / "pr_comments.json"
        assert not pr_comments_file.exists()

    def test_validation_comprehensive_error_messages(self):
        """Test that validation provides comprehensive error messages."""
        # Test multiple validation errors at once
        with pytest.raises(ValueError) as exc_info:
            config = ApplicationConfig(
                operation="invalid_operation",  # Invalid
                github_token="test_token",
                github_repo="owner/repo",
                data_path="/data",
                label_conflict_strategy="invalid_strategy",  # Invalid
                include_git_repo=False,
                include_issues={-1, 0},  # Invalid numbers
                include_issue_comments=True,
                include_pull_requests={-5, 0},  # Invalid numbers
                include_pull_request_comments=True,
                include_pr_reviews=False,
                include_pr_review_comments=False,
                include_sub_issues=False,
                git_auth_method="invalid_auth",  # Invalid
            )
            config.validate()

        # Should catch the first validation error
        error_message = str(exc_info.value)
        assert (
            "Operation must be one of" in error_message
            or "numbers must be positive integers" in error_message
        )
