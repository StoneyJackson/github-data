"""Data builder and factory pattern fixtures for advanced testing patterns."""

import pytest


@pytest.fixture
def github_data_builder():
    """Factory for building dynamic GitHub data for testing."""

    class GitHubDataBuilder:
        def __init__(self):
            self.reset()

        def reset(self):
            self.data = {
                "labels": [],
                "issues": [],
                "comments": [],
                "pull_requests": [],
                "pr_comments": [],
                "sub_issues": [],
            }
            self._next_id = 1000
            return self

        def with_labels(self, count=3, prefix="label"):
            """Add labels to the data set."""
            colors = ["d73a4a", "a2eeef", "7057ff", "008672", "e4e669"]
            for i in range(count):
                self.data["labels"].append(
                    {
                        "id": self._next_id,
                        "name": f"{prefix}-{i + 1}",
                        "color": colors[i % len(colors)],
                        "description": f"Description for {prefix} {i + 1}",
                        "url": (
                            f"https://api.github.com/repos/owner/repo/labels/"
                            f"{prefix}-{i + 1}"
                        ),
                    }
                )
                self._next_id += 1
            return self

        def with_issues(self, count=5, state="open", with_labels=True):
            """Add issues to the data set."""
            states = ["open", "closed"] if state == "mixed" else [state]
            for i in range(count):
                issue_labels = []
                if with_labels and self.data["labels"]:
                    # Assign random labels
                    import random

                    issue_labels = random.sample(
                        self.data["labels"],
                        min(len(self.data["labels"]), random.randint(1, 3)),
                    )

                self.data["issues"].append(
                    {
                        "id": self._next_id,
                        "number": i + 1,
                        "title": f"Test Issue {i + 1}",
                        "body": f"Description for test issue {i + 1}",
                        "state": states[i % len(states)],
                        "labels": issue_labels,
                        "assignee": None,
                        "milestone": None,
                        "user": {"login": "testuser", "id": 1},
                        "assignees": [],
                        "created_at": f"2024-01-{(i % 28) + 1:02d}T00:00:00Z",
                        "updated_at": f"2024-01-{(i % 28) + 1:02d}T00:00:00Z",
                        "closed_at": None,
                        "html_url": f"https://github.com/owner/repo/issues/{i + 1}",
                        "comments": 0,
                    }
                )
                self._next_id += 1
            return self

        def with_comments(self, issues_per_comment=2):
            """Add comments to existing issues."""
            for i, issue in enumerate(self.data["issues"]):
                if i % issues_per_comment == 0:  # Every nth issue gets comments
                    comment_count = (i // issues_per_comment) + 1
                    for j in range(comment_count):
                        self.data["comments"].append(
                            {
                                "id": self._next_id,
                                "issue_number": issue["number"],
                                "body": f"Comment {j + 1} on issue #{issue['number']}",
                                "user": {"login": f"user{j + 1}", "id": j + 1},
                                "created_at": (
                                    f"2024-01-{(i % 28) + 1:02d}T{j:02d}:00:00Z"
                                ),
                                "updated_at": (
                                    f"2024-01-{(i % 28) + 1:02d}T{j:02d}:00:00Z"
                                ),
                                "html_url": (
                                    f"https://github.com/owner/repo/issues/"
                                    f"{issue['number']}#issuecomment-{self._next_id}"
                                ),
                                "issue_url": (
                                    f"https://api.github.com/repos/owner/repo/"
                                    f"issues/{issue['number']}"
                                ),
                            }
                        )
                        self._next_id += 1
            return self

        def with_pull_requests(self, count=3, state="OPEN"):
            """Add pull requests to the data set."""
            states = ["OPEN", "CLOSED", "MERGED"] if state == "mixed" else [state]
            for i in range(count):
                self.data["pull_requests"].append(
                    {
                        "id": self._next_id,
                        "number": len(self.data["issues"]) + i + 1,
                        "title": f"Test PR {i + 1}",
                        "body": f"Description for test PR {i + 1}",
                        "state": states[i % len(states)],
                        "user": {"login": "testuser", "id": 1},
                        "assignees": [],
                        "labels": [],
                        "head_ref": f"feature/test-{i + 1}",
                        "base_ref": "main",
                        "created_at": f"2024-02-{(i % 28) + 1:02d}T00:00:00Z",
                        "updated_at": f"2024-02-{(i % 28) + 1:02d}T00:00:00Z",
                        "closed_at": (
                            None
                            if states[i % len(states)] == "OPEN"
                            else f"2024-02-{(i % 28) + 1:02d}T01:00:00Z"
                        ),
                        "merged_at": (
                            f"2024-02-{(i % 28) + 1:02d}T01:00:00Z"
                            if states[i % len(states)] == "MERGED"
                            else None
                        ),
                        "merge_commit_sha": (
                            f"abc123{i + 1:03d}"
                            if states[i % len(states)] == "MERGED"
                            else None
                        ),
                        "html_url": (
                            f"https://github.com/owner/repo/pull/"
                            f"{len(self.data['issues']) + i + 1}"
                        ),
                        "comments": 0,
                    }
                )
                self._next_id += 1
            return self

        def with_pr_comments(self, prs_per_comment=1):
            """Add comments to existing pull requests."""
            for i, pr in enumerate(self.data["pull_requests"]):
                if i % prs_per_comment == 0:
                    comment_count = (i // prs_per_comment) + 1
                    for j in range(comment_count):
                        self.data["pr_comments"].append(
                            {
                                "id": self._next_id,
                                "pull_request_number": pr["number"],
                                "body": f"PR comment {j + 1} on PR #{pr['number']}",
                                "user": {"login": f"reviewer{j + 1}", "id": j + 1},
                                "created_at": (
                                    f"2024-02-{(i % 28) + 1:02d}T{j:02d}:00:00Z"
                                ),
                                "updated_at": (
                                    f"2024-02-{(i % 28) + 1:02d}T{j:02d}:00:00Z"
                                ),
                                "html_url": (
                                    f"https://github.com/owner/repo/pull/"
                                    f"{pr['number']}#issuecomment-{self._next_id}"
                                ),
                                "pull_request_url": (
                                    f"https://github.com/owner/repo/pull/{pr['number']}"
                                ),
                            }
                        )
                        self._next_id += 1
            return self

        def with_sub_issue_hierarchy(self, depth=3, children_per_level=2):
            """Add hierarchical sub-issue relationships."""
            if not self.data["issues"]:
                self.with_issues(depth * children_per_level * 2)

            # Create hierarchy from existing issues
            issues = self.data["issues"]
            for level in range(depth - 1):
                for i in range(children_per_level):
                    parent_idx = level * children_per_level + i
                    child_idx = (level + 1) * children_per_level + i

                    if parent_idx < len(issues) and child_idx < len(issues):
                        self.data["sub_issues"].append(
                            {
                                "parent_issue_id": issues[parent_idx]["id"],
                                "child_issue_id": issues[child_idx]["id"],
                                "parent_issue_number": issues[parent_idx]["number"],
                                "sub_issue_number": issues[child_idx]["number"],
                                "sub_issue_id": issues[child_idx]["id"],
                                "position": i + 1,
                            }
                        )
            return self

        def build(self):
            """Return the built data structure."""
            return self.data.copy()

    return GitHubDataBuilder()


@pytest.fixture
def parametrized_data_factory(github_data_builder):
    """Factory for creating parametrized test data sets."""

    def create_dataset(scenario="basic"):
        """Create data set based on scenario."""
        builder = github_data_builder.reset()

        if scenario == "basic":
            return builder.with_labels(3).with_issues(5).with_comments().build()

        elif scenario == "large":
            return builder.with_labels(10).with_issues(50).with_comments(1).build()

        elif scenario == "pr_focused":
            return (
                builder.with_labels(5)
                .with_issues(3)
                .with_pull_requests(8)
                .with_pr_comments()
                .build()
            )

        elif scenario == "sub_issues":
            return (
                builder.with_labels(3)
                .with_issues(15)
                .with_sub_issue_hierarchy(3, 3)
                .with_comments(3)
                .build()
            )

        elif scenario == "mixed_states":
            return (
                builder.with_labels(5)
                .with_issues(10, state="mixed")
                .with_pull_requests(5, state="mixed")
                .with_comments(2)
                .with_pr_comments()
                .build()
            )

        elif scenario == "empty":
            return builder.build()

        else:
            raise ValueError(f"Unknown scenario: {scenario}")

    return create_dataset
