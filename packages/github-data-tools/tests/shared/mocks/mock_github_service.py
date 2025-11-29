"""
Mock GitHub service for testing.

Provides a fake implementation of the RepositoryService protocol
for unit testing without external dependencies.
"""

from typing import Dict, List, Any, Optional
from github_data_tools.github.protocols import RepositoryService


class MockGitHubService(RepositoryService):
    """Mock GitHub service for testing."""

    def __init__(self, mock_data: Optional[Dict[str, Any]] = None):
        """Initialize with optional mock data."""
        self.mock_data = mock_data or {}
        self.created_labels = []
        self.deleted_labels = []
        self.updated_labels = []
        self.created_issues = []
        self.created_comments = []
        self.closed_issues = []
        self.created_pull_requests = []
        self.created_pr_comments = []
        self.added_sub_issues = []
        self.removed_sub_issues = []
        self.reprioritized_sub_issues = []

    # Repository Data Operations (Read)

    def get_repository_labels(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all labels from repository."""
        return self.mock_data.get("labels", [])

    def get_repository_issues(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all issues from repository."""
        return self.mock_data.get("issues", [])

    def get_issue_comments(
        self, repo_name: str, issue_number: int
    ) -> List[Dict[str, Any]]:
        """Get comments for specific issue."""
        comments = self.mock_data.get("comments", [])
        return [c for c in comments if c.get("issue_number") == issue_number]

    def get_all_issue_comments(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all issue comments."""
        return self.mock_data.get("comments", [])

    def get_repository_pull_requests(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all pull requests from repository."""
        return self.mock_data.get("pull_requests", [])

    def get_pull_request_comments(
        self, repo_name: str, pr_number: int
    ) -> List[Dict[str, Any]]:
        """Get comments for specific pull request."""
        pr_comments = self.mock_data.get("pr_comments", [])
        return [c for c in pr_comments if c.get("pr_number") == pr_number]

    def get_all_pull_request_comments(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all pull request comments."""
        return self.mock_data.get("pr_comments", [])

    def get_pull_request_reviews(
        self, repo_name: str, pr_number: int
    ) -> List[Dict[str, Any]]:
        """Get reviews for specific pull request."""
        pr_reviews = self.mock_data.get("pr_reviews", [])
        return [r for r in pr_reviews if r.get("pr_number") == pr_number]

    def get_all_pull_request_reviews(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all pull request reviews."""
        return self.mock_data.get("pr_reviews", [])

    def get_pull_request_review_comments(
        self, repo_name: str, review_id: str
    ) -> List[Dict[str, Any]]:
        """Get comments for specific pull request review."""
        pr_review_comments = self.mock_data.get("pr_review_comments", [])
        return [
            c for c in pr_review_comments if str(c.get("review_id")) == str(review_id)
        ]

    def get_all_pull_request_review_comments(
        self, repo_name: str
    ) -> List[Dict[str, Any]]:
        """Get all pull request review comments."""
        return self.mock_data.get("pr_review_comments", [])

    def get_repository_sub_issues(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get sub-issue relationships from repository."""
        return self.mock_data.get("sub_issues", [])

    def get_issue_sub_issues(
        self, repo_name: str, issue_number: int
    ) -> List[Dict[str, Any]]:
        """Get sub-issues for specific issue."""
        sub_issues = self.mock_data.get("sub_issues", [])
        return [s for s in sub_issues if s.get("parent_issue_number") == issue_number]

    def get_issue_parent(
        self, repo_name: str, issue_number: int
    ) -> Optional[Dict[str, Any]]:
        """Get parent issue if this issue is a sub-issue."""
        sub_issues = self.mock_data.get("sub_issues", [])
        for sub_issue in sub_issues:
            if sub_issue.get("sub_issue_number") == issue_number:
                return {"number": sub_issue.get("parent_issue_number")}
        return None

    def get_repository_milestones(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all milestones from the repository."""
        return self.mock_data.get("milestones", [])

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        return self.mock_data.get("rate_limit", {"remaining": 5000, "limit": 5000})

    # Repository Modification Operations (Write)

    def create_label(
        self, repo_name: str, name: str, color: str, description: str
    ) -> Dict[str, Any]:
        """Create a new label."""
        label_data = {
            "name": name,
            "color": color,
            "description": description,
            "id": len(self.created_labels) + 1,
        }
        self.created_labels.append(label_data)
        return label_data

    def delete_label(self, repo_name: str, label_name: str) -> None:
        """Delete a label."""
        self.deleted_labels.append(label_name)

    def update_label(
        self, repo_name: str, old_name: str, name: str, color: str, description: str
    ) -> Dict[str, Any]:
        """Update an existing label."""
        label_data = {
            "old_name": old_name,
            "name": name,
            "color": color,
            "description": description,
        }
        self.updated_labels.append(label_data)
        return label_data

    def create_issue(
        self, repo_name: str, title: str, body: str, labels: List[str]
    ) -> Dict[str, Any]:
        """Create a new issue."""
        issue_data = {
            "number": len(self.created_issues) + 1,
            "title": title,
            "body": body,
            "labels": [{"name": label} for label in labels],
            "state": "open",
        }
        self.created_issues.append(issue_data)
        return issue_data

    def create_issue_comment(
        self, repo_name: str, issue_number: int, body: str
    ) -> Dict[str, Any]:
        """Create a new comment."""
        comment_data = {
            "id": len(self.created_comments) + 1,
            "issue_number": issue_number,
            "body": body,
        }
        self.created_comments.append(comment_data)
        return comment_data

    def close_issue(
        self, repo_name: str, issue_number: int, state_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Close an issue."""
        issue_data = {
            "number": issue_number,
            "state": "closed",
            "state_reason": state_reason,
        }
        self.closed_issues.append(issue_data)
        return issue_data

    def create_pull_request(
        self, repo_name: str, title: str, body: str, head: str, base: str
    ) -> Dict[str, Any]:
        """Create a new pull request."""
        pr_data = {
            "number": len(self.created_pull_requests) + 1,
            "title": title,
            "body": body,
            "head": {"ref": head},
            "base": {"ref": base},
            "state": "open",
        }
        self.created_pull_requests.append(pr_data)
        return pr_data

    def create_pull_request_comment(
        self, repo_name: str, pr_number: int, body: str
    ) -> Dict[str, Any]:
        """Create a new PR comment."""
        comment_data = {
            "id": len(self.created_pr_comments) + 1,
            "pr_number": pr_number,
            "body": body,
        }
        self.created_pr_comments.append(comment_data)
        return comment_data

    def create_pull_request_review(
        self, repo_name: str, pr_number: int, body: str, state: str
    ) -> Dict[str, Any]:
        """Create a new pull request review."""
        review_data = {
            "id": len(getattr(self, "created_pr_reviews", [])) + 1,
            "pr_number": pr_number,
            "body": body,
            "state": state,
        }
        if not hasattr(self, "created_pr_reviews"):
            self.created_pr_reviews = []
        self.created_pr_reviews.append(review_data)
        return review_data

    def create_pull_request_review_comment(
        self, repo_name: str, review_id: str, body: str
    ) -> Dict[str, Any]:
        """Create a new pull request review comment."""
        comment_data = {
            "id": len(getattr(self, "created_pr_review_comments", [])) + 1,
            "review_id": review_id,
            "body": body,
        }
        if not hasattr(self, "created_pr_review_comments"):
            self.created_pr_review_comments = []
        self.created_pr_review_comments.append(comment_data)
        return comment_data

    def add_sub_issue(
        self, repo_name: str, parent_issue_number: int, sub_issue_number: int
    ) -> Dict[str, Any]:
        """Add existing issue as sub-issue."""
        sub_issue_data = {
            "parent_issue_number": parent_issue_number,
            "sub_issue_number": sub_issue_number,
        }
        self.added_sub_issues.append(sub_issue_data)
        return sub_issue_data

    def remove_sub_issue(
        self, repo_name: str, parent_issue_number: int, sub_issue_number: int
    ) -> None:
        """Remove sub-issue relationship."""
        removal_data = {
            "parent_issue_number": parent_issue_number,
            "sub_issue_number": sub_issue_number,
        }
        self.removed_sub_issues.append(removal_data)

    def reprioritize_sub_issue(
        self,
        repo_name: str,
        parent_issue_number: int,
        sub_issue_number: int,
        position: int,
    ) -> Dict[str, Any]:
        """Change sub-issue order/position."""
        reprioritize_data = {
            "parent_issue_number": parent_issue_number,
            "sub_issue_number": sub_issue_number,
            "position": position,
        }
        self.reprioritized_sub_issues.append(reprioritize_data)
        return reprioritize_data

    def create_milestone(
        self,
        repo_name: str,
        title: str,
        description: Optional[str] = None,
        due_on: Optional[str] = None,
        state: str = "open",
    ) -> Dict[str, Any]:
        """Create a new milestone."""
        milestone_data = {
            "number": len(getattr(self, "created_milestones", [])) + 1,
            "title": title,
            "description": description,
            "due_on": due_on,
            "state": state,
        }
        if not hasattr(self, "created_milestones"):
            self.created_milestones = []
        self.created_milestones.append(milestone_data)
        return milestone_data
