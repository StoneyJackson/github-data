"""Test data builders for GitHub Data tests."""

from typing import List, Dict, Any, Optional


class GitHubDataBuilder:
    """Builder for creating customizable GitHub test data."""

    def __init__(self):
        self.data = {
            "labels": [],
            "issues": [],
            "comments": [],
            "pull_requests": [],
            "pr_comments": [],
        }
        self._label_id_counter = 1000
        self._issue_id_counter = 2000
        self._comment_id_counter = 4000
        self._pr_id_counter = 5000
        self._pr_comment_id_counter = 6000
        self._user_id_counter = 3000

    def with_labels(
        self, count: int = 2, custom_labels: Optional[List[Dict[str, Any]]] = None
    ) -> "GitHubDataBuilder":
        """Add labels to the test data.

        Args:
            count: Number of default labels to create
            custom_labels: Optional list of custom label data
        """
        if custom_labels:
            self.data["labels"].extend(custom_labels)
        else:
            # First create some default labels
            default_labels = [
                {
                    "name": "bug",
                    "color": "d73a4a",
                    "description": "Something isn't working",
                    "url": "https://api.github.com/repos/owner/repo/labels/bug",
                    "id": self._label_id_counter,
                },
                {
                    "name": "enhancement",
                    "color": "a2eeef",
                    "description": "New feature or request",
                    "url": (
                        "https://api.github.com/repos/owner/repo/labels/enhancement"
                    ),
                    "id": self._label_id_counter + 1,
                },
                {
                    "name": "documentation",
                    "color": "0075ca",
                    "description": "Improvements or additions to documentation",
                    "url": (
                        "https://api.github.com/repos/owner/repo/labels/documentation"
                    ),
                    "id": self._label_id_counter + 2,
                },
            ]

            # Add default labels up to the default count
            for i in range(min(count, len(default_labels))):
                self.data["labels"].append(default_labels[i])

            # If we need more labels than defaults, generate them
            if count > len(default_labels):
                for i in range(len(default_labels), count):
                    generated_label = {
                        "name": f"label-{i + 1}",
                        "color": f"{(i * 37) % 16777215:06x}",  # Generate hex colors
                        "description": f"Generated label {i + 1}",
                        "url": (
                            f"https://api.github.com/repos/owner/repo/labels/"
                            f"label-{i + 1}"
                        ),
                        "id": self._label_id_counter + i,
                    }
                    self.data["labels"].append(generated_label)

            self._label_id_counter += count

        return self

    def with_issues(
        self,
        count: int = 3,
        include_closed: bool = False,
        custom_issues: Optional[List[Dict[str, Any]]] = None,
    ) -> "GitHubDataBuilder":
        """Add issues to the test data.

        Args:
            count: Number of issues to create
            include_closed: Whether to include closed issues
            custom_issues: Optional list of custom issue data
        """
        if custom_issues:
            self.data["issues"].extend(custom_issues)
        else:
            for i in range(count):
                issue_number = i + 1
                is_closed = include_closed and i % 2 == 1  # Every other issue is closed

                issue = {
                    "id": self._issue_id_counter + i,
                    "number": issue_number,
                    "title": f"Test issue {issue_number}",
                    "body": (
                        f"This is test issue {issue_number}" if i % 2 == 0 else None
                    ),
                    "state": "closed" if is_closed else "open",
                    "user": {
                        "login": f"user{issue_number}",
                        "id": self._user_id_counter + i,
                        "avatar_url": f"https://github.com/user{issue_number}.png",
                        "html_url": f"https://github.com/user{issue_number}",
                    },
                    "assignees": [],
                    "labels": [],
                    "created_at": f"2023-01-{min(10 + i, 31):02d}T10:00:00Z",
                    "updated_at": f"2023-01-{min(10 + i, 31):02d}T10:00:00Z",
                    "closed_at": (
                        f"2023-01-{min(10 + i, 31):02d}T16:00:00Z"
                        if is_closed
                        else None
                    ),
                    "html_url": f"https://github.com/owner/repo/issues/{issue_number}",
                    "comments": 0,
                }

                self.data["issues"].append(issue)

            self._issue_id_counter += count
            self._user_id_counter += count

        return self

    def with_comments(
        self,
        issue_count: int = 2,
        comments_per_issue: int = 1,
        custom_comments: Optional[List[Dict[str, Any]]] = None,
    ) -> "GitHubDataBuilder":
        """Add comments to the test data.

        Args:
            issue_count: Number of issues to add comments to
            comments_per_issue: Number of comments per issue
            custom_comments: Optional list of custom comment data
        """
        if custom_comments:
            self.data["comments"].extend(custom_comments)
        else:
            # Ensure we have enough issues
            if len(self.data["issues"]) < issue_count:
                self.with_issues(issue_count)

            comment_id = self._comment_id_counter
            for i in range(issue_count):
                issue = self.data["issues"][i]
                issue_number = issue["number"]

                for j in range(comments_per_issue):
                    comment = {
                        "id": comment_id,
                        "body": f"Comment {j + 1} on issue {issue_number}",
                        "user": {
                            "login": f"commenter{j + 1}",
                            "id": self._user_id_counter + j,
                            "avatar_url": (f"https://github.com/commenter{j + 1}.png"),
                            "html_url": f"https://github.com/commenter{j + 1}",
                        },
                        "created_at": (
                            f"2023-01-{min(10 + i, 31):02d}T"
                            f"{min(12 + j, 23):02d}:00:00Z"
                        ),
                        "updated_at": (
                            f"2023-01-{min(10 + i, 31):02d}T"
                            f"{min(12 + j, 23):02d}:00:00Z"
                        ),
                        "html_url": (
                            f"https://github.com/owner/repo/issues/{issue_number}"
                            f"#issuecomment-{comment_id}"
                        ),
                        "issue_url": (
                            f"https://api.github.com/repos/owner/repo/issues/"
                            f"{issue_number}"
                        ),
                    }

                    self.data["comments"].append(comment)
                    comment_id += 1

                # Update issue comment count
                issue["comments"] = comments_per_issue

            self._comment_id_counter = comment_id
            self._user_id_counter += comments_per_issue

        return self

    def with_pull_requests(
        self, count: int = 2, custom_prs: Optional[List[Dict[str, Any]]] = None
    ) -> "GitHubDataBuilder":
        """Add pull requests to the test data.

        Args:
            count: Number of PRs to create
            custom_prs: Optional list of custom PR data
        """
        if custom_prs:
            self.data["pull_requests"].extend(custom_prs)
        else:
            for i in range(count):
                pr_number = i + 1
                is_merged = i % 3 == 0  # Every third PR is merged

                pr = {
                    "id": self._pr_id_counter + i,
                    "number": pr_number,
                    "title": f"Test PR {pr_number}",
                    "body": f"This is test PR {pr_number}",
                    "state": "MERGED" if is_merged else "OPEN",
                    "user": {
                        "login": f"pruser{pr_number}",
                        "id": self._user_id_counter + i,
                        "avatar_url": f"https://github.com/pruser{pr_number}.png",
                        "html_url": f"https://github.com/pruser{pr_number}",
                    },
                    "assignees": [],
                    "labels": [],
                    "created_at": f"2023-01-{min(15 + i, 31):02d}T10:00:00Z",
                    "updated_at": f"2023-01-{min(15 + i, 31):02d}T15:00:00Z",
                    "closed_at": (
                        f"2023-01-{min(15 + i, 31):02d}T15:00:00Z"
                        if is_merged
                        else None
                    ),
                    "merged_at": (
                        f"2023-01-{min(15 + i, 31):02d}T15:00:00Z"
                        if is_merged
                        else None
                    ),
                    "merge_commit_sha": f"abc123def{pr_number}" if is_merged else None,
                    "base_ref": "main",
                    "head_ref": f"feature/test-{pr_number}",
                    "html_url": f"https://github.com/owner/repo/pull/{pr_number}",
                    "comments": 0,
                }

                self.data["pull_requests"].append(pr)

            self._pr_id_counter += count
            self._user_id_counter += count

        return self

    def with_pr_comments(
        self,
        pr_count: int = 2,
        comments_per_pr: int = 1,
        custom_pr_comments: Optional[List[Dict[str, Any]]] = None,
    ) -> "GitHubDataBuilder":
        """Add PR comments to the test data.

        Args:
            pr_count: Number of PRs to add comments to
            comments_per_pr: Number of comments per PR
            custom_pr_comments: Optional list of custom PR comment data
        """
        if custom_pr_comments:
            self.data["pr_comments"].extend(custom_pr_comments)
        else:
            # Ensure we have enough PRs
            if len(self.data["pull_requests"]) < pr_count:
                self.with_pull_requests(pr_count)

            comment_id = self._pr_comment_id_counter
            for i in range(pr_count):
                pr = self.data["pull_requests"][i]
                pr_number = pr["number"]

                for j in range(comments_per_pr):
                    comment = {
                        "id": comment_id,
                        "body": f"PR comment {j + 1} on PR {pr_number}",
                        "user": {
                            "login": f"prcommenter{j + 1}",
                            "id": self._user_id_counter + j,
                            "avatar_url": (
                                f"https://github.com/prcommenter{j + 1}.png"
                            ),
                            "html_url": f"https://github.com/prcommenter{j + 1}",
                        },
                        "created_at": (
                            f"2023-01-{min(15 + i, 31):02d}T"
                            f"{min(13 + j, 23):02d}:00:00Z"
                        ),
                        "updated_at": (
                            f"2023-01-{min(15 + i, 31):02d}T"
                            f"{min(13 + j, 23):02d}:00:00Z"
                        ),
                        "html_url": (
                            f"https://github.com/owner/repo/pull/{pr_number}"
                            f"#issuecomment-{comment_id}"
                        ),
                        "pull_request_url": (
                            f"https://github.com/owner/repo/pull/{pr_number}"
                        ),
                    }

                    self.data["pr_comments"].append(comment)
                    comment_id += 1

                # Update PR comment count
                pr["comments"] = comments_per_pr

            self._pr_comment_id_counter = comment_id
            self._user_id_counter += comments_per_pr

        return self

    def with_unicode_content(self) -> "GitHubDataBuilder":
        """Add issues and comments with unicode content for testing."""
        unicode_issue = {
            "id": self._issue_id_counter,
            "number": 999,
            "title": "Unicode test: 测试 🚀 Special chars: äöü",
            "body": "Unicode content: こんにちは 世界 🌍",
            "state": "open",
            "user": {
                "login": "unicode-user",
                "id": self._user_id_counter,
                "avatar_url": "https://github.com/unicode-user.png",
                "html_url": "https://github.com/unicode-user",
            },
            "assignees": [],
            "labels": [],
            "created_at": "2023-01-20T10:00:00Z",
            "updated_at": "2023-01-20T10:00:00Z",
            "closed_at": None,
            "html_url": "https://github.com/owner/repo/issues/999",
            "comments": 1,
        }

        unicode_comment = {
            "id": self._comment_id_counter,
            "body": "Unicode comment: Привет мир! 🎉",
            "user": {
                "login": "unicode-commenter",
                "id": self._user_id_counter + 1,
                "avatar_url": "https://github.com/unicode-commenter.png",
                "html_url": "https://github.com/unicode-commenter",
            },
            "created_at": "2023-01-20T11:00:00Z",
            "updated_at": "2023-01-20T11:00:00Z",
            "html_url": (
                f"https://github.com/owner/repo/issues/999"
                f"#issuecomment-{self._comment_id_counter}"
            ),
            "issue_url": "https://api.github.com/repos/owner/repo/issues/999",
        }

        self.data["issues"].append(unicode_issue)
        self.data["comments"].append(unicode_comment)

        self._issue_id_counter += 1
        self._comment_id_counter += 1
        self._user_id_counter += 2

        return self

    def build(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return the complete data structure."""
        return self.data.copy()

    def build_minimal(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return minimal test data with just one of each type."""
        return (
            GitHubDataBuilder()
            .with_labels(1)
            .with_issues(1)
            .with_comments(1, 1)
            .with_pull_requests(1)
            .with_pr_comments(1, 1)
            .build()
        )

    def build_complex(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return complex test data with multiple items and relationships."""
        return (
            GitHubDataBuilder()
            .with_labels(3)
            .with_issues(5, include_closed=True)
            .with_comments(3, 2)
            .with_pull_requests(3)
            .with_pr_comments(2, 2)
            .with_unicode_content()
            .build()
        )
