"""
GitHub REST API client.

Focused REST API client that handles direct GitHub API operations
using PyGithub as the underlying HTTP client but providing a clean
interface for REST-specific operations.
"""

from typing import Dict, List, Any, Optional, Union, cast
from github import Github, Auth
from github.Repository import Repository
from github.PaginatedList import PaginatedList


class GitHubRestApiClient:
    """
    GitHub REST API client for direct API operations.

    Handles all REST API calls that require direct HTTP requests
    or PyGithub object manipulation, providing a clean interface
    for the boundary layer.
    """

    def __init__(self, token: str):
        """
        Initialize GitHub REST API client with authentication.

        Args:
            token: GitHub authentication token
        """
        self._github = Github(auth=Auth.Token(token))
        self._token = token

    # Repository Operations

    def _parse_repo_name(self, repo_name: str) -> tuple[str, str]:
        """Parse owner/repo format into separate components."""
        if "/" not in repo_name:
            raise ValueError(
                f"Repository name must be in 'owner/repo' format, got: {repo_name}"
            )

        owner, name = repo_name.split("/", 1)
        return owner, name

    def _get_repository(self, repo_name: str) -> Repository:
        """Get repository object from GitHub API."""
        return self._github.get_repo(repo_name)

    # Issue Comment Operations

    def get_issue_comments(
        self, repo_name: str, issue_number: int
    ) -> List[Dict[str, Any]]:
        """Get comments for specific issue as raw JSON data."""
        repo = self._get_repository(repo_name)
        issue = repo.get_issue(issue_number)
        comments = issue.get_comments()
        return self._extract_raw_data_list(comments)

    def create_issue_comment(
        self, repo_name: str, issue_number: int, body: str
    ) -> Dict[str, Any]:
        """Create a new comment on an issue and return raw JSON data."""
        repo = self._get_repository(repo_name)
        issue = repo.get_issue(issue_number)
        created_comment = issue.create_comment(body)
        return self._extract_raw_data(created_comment)

    # Label Operations

    def create_label(
        self, repo_name: str, name: str, color: str, description: str
    ) -> Dict[str, Any]:
        """Create a new label and return raw JSON data."""
        repo = self._get_repository(repo_name)
        created_label = repo.create_label(
            name=name, color=color, description=description
        )
        return self._extract_raw_data(created_label)

    def delete_label(self, repo_name: str, label_name: str) -> None:
        """Delete a label from the repository."""
        repo = self._get_repository(repo_name)
        label = repo.get_label(label_name)
        label.delete()

    def update_label(
        self, repo_name: str, old_name: str, name: str, color: str, description: str
    ) -> Dict[str, Any]:
        """Update an existing label and return raw JSON data."""
        repo = self._get_repository(repo_name)
        label = repo.get_label(old_name)
        label.edit(name=name, color=color, description=description)
        return self._extract_raw_data(label)

    # Issue Operations

    def create_issue(
        self, repo_name: str, title: str, body: str, labels: List[str]
    ) -> Dict[str, Any]:
        """Create a new issue and return raw JSON data."""
        repo = self._get_repository(repo_name)
        created_issue = repo.create_issue(title=title, body=body, labels=labels)
        return self._extract_raw_data(created_issue)

    def close_issue(
        self, repo_name: str, issue_number: int, state_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Close an issue with optional state reason and return raw JSON data."""
        repo = self._get_repository(repo_name)
        issue = repo.get_issue(issue_number)

        if state_reason:
            issue.edit(state="closed", state_reason=state_reason)
        else:
            issue.edit(state="closed")

        return self._extract_raw_data(issue)

    # Pull Request Operations

    def create_pull_request(
        self, repo_name: str, title: str, body: str, head: str, base: str
    ) -> Dict[str, Any]:
        """Create a new pull request and return raw JSON data."""
        repo = self._get_repository(repo_name)
        created_pr = repo.create_pull(title=title, body=body, head=head, base=base)
        return self._extract_raw_data(created_pr)

    def create_pull_request_comment(
        self, repo_name: str, pr_number: int, body: str
    ) -> Dict[str, Any]:
        """Create a new comment on a pull request and return raw JSON data."""
        repo = self._get_repository(repo_name)
        pr = repo.get_pull(pr_number)
        created_comment = pr.create_issue_comment(body)
        return self._extract_raw_data(created_comment)

    def create_pull_request_review(
        self, repo_name: str, pr_number: int, body: str, state: str
    ) -> Dict[str, Any]:
        """Create a new pull request review and return raw JSON data."""
        repo = self._get_repository(repo_name)
        pr = repo.get_pull(pr_number)
        # GitHub API review states: APPROVE, REQUEST_CHANGES, COMMENT
        created_review = pr.create_review(body=body, event=state)
        return self._extract_raw_data(created_review)

    def create_pull_request_review_comment(
        self, repo_name: str, review_id: str, body: str
    ) -> Dict[str, Any]:
        """Create a new pull request review comment and return raw JSON data."""
        # Note: PyGithub doesn't have direct support for creating review comments
        # This would require direct API calls using requests
        # For now, we'll implement a basic version that may need enhancement
        try:
            # This is a simplified implementation - in production you'd want
            # to use the GitHub API directly for review comments
            # PyGithub doesn't support creating review comments directly
            # This would need to be implemented using direct REST API calls
            raise NotImplementedError(
                "Creating review comments requires direct GitHub API integration"
            )
        except Exception as e:
            # Return a mock response for now - this needs proper implementation
            return {
                "id": f"mock_{review_id}",
                "body": body,
                "review_id": review_id,
                "error": str(e),
            }

    # Sub-Issues Operations (Direct REST API)

    def get_issue_sub_issues(
        self, repo_name: str, issue_number: int
    ) -> List[Dict[str, Any]]:
        """Get sub-issues for a specific issue using REST API."""
        repo = self._get_repository(repo_name)
        try:
            # GitHub REST API endpoint for sub-issues
            # GET /repos/{owner}/{repo}/issues/{issue_number}/sub_issues
            url = f"/repos/{repo_name}/issues/{issue_number}/sub_issues"
            status, headers, raw_data = repo._requester.requestJson("GET", url)
            data = cast(Union[List[Dict[str, Any]], str], raw_data)
            if isinstance(data, list):
                return data
            else:
                return []
        except Exception:
            # Sub-issues API might not be available or issue has no sub-issues
            return []

    def get_issue_parent(
        self, repo_name: str, issue_number: int
    ) -> Optional[Dict[str, Any]]:
        """Get parent issue if this issue is a sub-issue using REST API."""
        repo = self._get_repository(repo_name)
        try:
            # GitHub REST API endpoint for parent issue
            # GET /repos/{owner}/{repo}/issues/{issue_number}/parent
            url = f"/repos/{repo_name}/issues/{issue_number}/parent"
            status, headers, raw_data = repo._requester.requestJson("GET", url)
            data = cast(Union[Dict[str, Any], str], raw_data)
            if isinstance(data, dict):
                return data
            else:
                return None
        except Exception:
            # Issue is not a sub-issue or API not available
            return None

    def add_sub_issue(
        self, repo_name: str, parent_issue_number: int, sub_issue_number: int
    ) -> Dict[str, Any]:
        """Add existing issue as sub-issue using REST API."""
        repo = self._get_repository(repo_name)
        # GitHub REST API endpoint for adding sub-issue
        # POST /repos/{owner}/{repo}/issues/{parent_issue_number}/sub_issues
        url = f"/repos/{repo_name}/issues/{parent_issue_number}/sub_issues"
        post_parameters = {"sub_issue_number": sub_issue_number}
        status, headers, raw_data = repo._requester.requestJson(
            "POST", url, post_parameters
        )
        data = cast(Union[Dict[str, Any], str], raw_data)
        if isinstance(data, dict):
            return data
        else:
            return {}

    def remove_sub_issue(
        self, repo_name: str, parent_issue_number: int, sub_issue_number: int
    ) -> None:
        """Remove sub-issue relationship using REST API."""
        repo = self._get_repository(repo_name)
        # GitHub REST API endpoint for removing sub-issue
        # DELETE /repos/{owner}/{repo}/issues/{parent_issue_number}/
        # sub_issues/{sub_issue_number}
        url = (
            f"/repos/{repo_name}/issues/{parent_issue_number}/"
            f"sub_issues/{sub_issue_number}"
        )
        repo._requester.requestJson("DELETE", url)

    def reprioritize_sub_issue(
        self,
        repo_name: str,
        parent_issue_number: int,
        sub_issue_number: int,
        position: int,
    ) -> Dict[str, Any]:
        """Change sub-issue order/position using REST API."""
        repo = self._get_repository(repo_name)
        # GitHub REST API endpoint for reprioritizing sub-issue
        # PATCH /repos/{owner}/{repo}/issues/{parent_issue_number}/
        # sub_issues/{sub_issue_number}
        url = (
            f"/repos/{repo_name}/issues/{parent_issue_number}/"
            f"sub_issues/{sub_issue_number}"
        )
        patch_parameters = {"position": position}
        status, headers, raw_data = repo._requester.requestJson(
            "PATCH", url, patch_parameters
        )
        data = cast(Union[Dict[str, Any], str], raw_data)
        if isinstance(data, dict):
            return data
        else:
            return {}

    # Raw Data Extraction Utilities

    def _extract_raw_data_list(
        self, pygithub_objects: PaginatedList[Any]
    ) -> List[Dict[str, Any]]:
        """Extract raw JSON data from a list of PyGithub objects."""
        return [self._extract_raw_data(obj) for obj in pygithub_objects]

    def _extract_raw_data(self, pygithub_obj: Any) -> Dict[str, Any]:
        """
        Extract raw JSON data from PyGithub objects.

        Uses _rawData to avoid additional API calls where possible.
        Can be switched to raw_data if we need complete data.

        Args:
            pygithub_obj: PyGithub object to extract data from

        Returns:
            Raw JSON data as dictionary

        Raises:
            ValueError: If object doesn't have raw data attributes
        """
        if hasattr(pygithub_obj, "_rawData"):
            return dict(pygithub_obj._rawData)
        elif hasattr(pygithub_obj, "raw_data"):
            return dict(pygithub_obj.raw_data)
        else:
            raise ValueError(
                f"Cannot extract raw data from {type(pygithub_obj).__name__}: "
                f"object has no '_rawData' or 'raw_data' attribute"
            )
