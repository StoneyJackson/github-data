"""Data builder fixtures for creating test data."""

import pytest


class GitHubDataBuilder:
    """Builder for creating GitHub test data with fluent interface."""

    def __init__(self):
        self._data = {
            "labels": [],
            "issues": [],
            "comments": [],
            "pull_requests": [],
            "pr_comments": [],
            "pr_reviews": [],
            "pr_review_comments": [],
            "sub_issues": [],
        }
        self._issue_counter = 1
        self._label_counter = 1
        self._comment_counter = 1

    def reset(self):
        """Reset the builder to initial state."""
        self.__init__()
        return self

    def with_labels(self, count):
        """Add labels to the test data."""
        for i in range(count):
            label_id = self._label_counter
            self._data["labels"].append(
                {
                    "id": 1000 + label_id,
                    "name": f"label-{label_id}",
                    "color": "d73a4a",
                    "description": f"Test label {label_id}",
                    "url": (
                        f"https://api.github.com/repos/owner/repo/"
                        f"labels/label-{label_id}"
                    ),
                }
            )
            self._label_counter += 1
        return self

    def with_issues(self, count):
        """Add issues to the test data."""
        for i in range(count):
            issue_id = self._issue_counter
            self._data["issues"].append(
                {
                    "id": 2000 + issue_id,
                    "number": issue_id,
                    "title": f"Issue {issue_id}",
                    "body": f"Test issue {issue_id}",
                    "state": "open",
                    "user": {
                        "login": "testuser",
                        "id": 3001,
                        "avatar_url": "https://github.com/testuser.png",
                        "html_url": "https://github.com/testuser",
                    },
                    "assignees": [],
                    "labels": [],
                    "created_at": "2023-01-15T10:30:00Z",
                    "updated_at": "2023-01-15T14:20:00Z",
                    "closed_at": None,
                    "html_url": f"https://github.com/owner/repo/issues/{issue_id}",
                    "comments": 0,
                }
            )
            self._issue_counter += 1
        return self

    def with_comments(self, comments_per_issue):
        """Add comments to existing issues."""
        for issue in self._data["issues"]:
            for i in range(comments_per_issue):
                comment_id = self._comment_counter
                self._data["comments"].append(
                    {
                        "id": 4000 + comment_id,
                        "body": f"Comment {comment_id}",
                        "user": {
                            "login": "testuser",
                            "id": 3001,
                            "avatar_url": "https://github.com/testuser.png",
                            "html_url": "https://github.com/testuser",
                        },
                        "created_at": "2023-01-15T12:00:00Z",
                        "updated_at": "2023-01-15T12:00:00Z",
                        "html_url": (
                            f"https://github.com/owner/repo/issues/"
                            f"{issue['number']}#issuecomment-"
                            f"{4000 + comment_id}"
                        ),
                        "issue_url": (
                            f"https://api.github.com/repos/owner/repo/"
                            f"issues/{issue['number']}"
                        ),
                        "issue_number": issue["number"],
                    }
                )
                self._comment_counter += 1
                issue["comments"] = comments_per_issue
        return self

    def with_sub_issue_hierarchy(self, parent_count, sub_issues_per_parent):
        """Add sub-issue hierarchy to the test data."""
        # Ensure we have enough issues
        total_needed = parent_count * (1 + sub_issues_per_parent)
        current_issues = len(self._data["issues"])
        if current_issues < total_needed:
            self.with_issues(total_needed - current_issues)

        # Create sub-issue relationships
        for i in range(parent_count):
            parent_idx = i * (1 + sub_issues_per_parent)
            parent_issue = self._data["issues"][parent_idx]

            for j in range(sub_issues_per_parent):
                sub_issue_idx = parent_idx + j + 1
                sub_issue = self._data["issues"][sub_issue_idx]

                self._data["sub_issues"].append(
                    {
                        "sub_issue_id": sub_issue["id"],
                        "sub_issue_number": sub_issue["number"],
                        "parent_issue_id": parent_issue["id"],
                        "parent_issue_number": parent_issue["number"],
                        "position": j + 1,
                    }
                )

        return self

    def build(self):
        """Return the built test data."""
        return self._data


class ParametrizedDataFactory:
    """Factory for creating parametrized test data scenarios."""

    def __call__(self, scenario):
        """Create test data for a specific scenario."""
        builder = GitHubDataBuilder()

        scenarios = {
            "basic": lambda: builder.with_labels(2)
            .with_issues(2)
            .with_comments(1)
            .build(),
            "large": lambda: builder.with_labels(10)
            .with_issues(50)
            .with_comments(3)
            .build(),
            "mixed_states": lambda: self._create_mixed_states(builder),
            "empty": lambda: builder.build(),
        }

        return scenarios.get(scenario, scenarios["basic"])()

    def _create_mixed_states(self, builder):
        """Create test data with mixed issue states."""
        data = builder.with_labels(3).with_issues(5).with_comments(2).build()

        # Modify some issues to be closed
        for i, issue in enumerate(data["issues"]):
            if i % 2 == 0:
                issue["state"] = "closed"
                issue["closed_at"] = "2023-01-20T10:00:00Z"

        return data


@pytest.fixture
def github_data_builder():
    """Provide GitHub data builder for creating test data."""
    return GitHubDataBuilder()


@pytest.fixture
def parametrized_data_factory():
    """Provide parametrized data factory for scenario-based test data."""
    return ParametrizedDataFactory()
