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
            "milestones": [],
            "sub_issues": [],
            "pr_reviews": [],
            "pr_review_comments": [],
            "users": [],
            "repositories": [],
        }
        self._label_id_counter = 1000
        self._issue_id_counter = 2000
        self._comment_id_counter = 4000
        self._pr_id_counter = 5000
        self._pr_comment_id_counter = 6000
        self._user_id_counter = 3000
        self._milestone_id_counter = 7000
        self._sub_issue_id_counter = 8000
        self._pr_review_id_counter = 9000
        self._pr_review_comment_id_counter = 10000
        self._repository_id_counter = 11000

    def _get_user_for_entity(
        self, index: int, entity_type: str = "user"
    ) -> Dict[str, Any]:
        """Get a user for an entity, either from existing users or create inline."""
        if self.data["users"]:
            # Use existing users in round-robin fashion
            user = self.data["users"][index % len(self.data["users"])]
            return {
                "login": user["login"],
                "id": user["id"],
                "avatar_url": user["avatar_url"],
                "html_url": user["html_url"],
            }
        else:
            # Create inline user (legacy behavior)
            user_id = self._user_id_counter + index
            login = f"{entity_type}{index + 1}"
            return {
                "login": login,
                "id": user_id,
                "avatar_url": f"https://github.com/{login}.png",
                "html_url": f"https://github.com/{login}",
            }

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
                    "user": self._get_user_for_entity(i, "user"),
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
            # Only increment user counter if we're not using existing users
            if not self.data["users"]:
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
                        "user": self._get_user_for_entity(j, "commenter"),
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
            # Only increment user counter if we're not using existing users
            if not self.data["users"]:
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
                    "user": self._get_user_for_entity(i, "pruser"),
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
            # Only increment user counter if we're not using existing users
            if not self.data["users"]:
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
                        "user": self._get_user_for_entity(j, "prcommenter"),
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
            # Only increment user counter if we're not using existing users
            if not self.data["users"]:
                self._user_id_counter += comments_per_pr

        return self

    def with_milestones(
        self,
        count: int = 2,
        include_closed: bool = False,
        with_due_dates: bool = True,
        custom_milestones: Optional[List[Dict[str, Any]]] = None,
    ) -> "GitHubDataBuilder":
        """Add milestones to the test data.

        Args:
            count: Number of milestones to create
            include_closed: Whether to include closed milestones
            with_due_dates: Whether to include due dates
            custom_milestones: Optional list of custom milestone data
        """
        if custom_milestones:
            self.data["milestones"].extend(custom_milestones)
        else:
            for i in range(count):
                milestone_number = i + 1
                is_closed = include_closed and i % 2 == 1

                milestone = {
                    "id": f"M_kwDO{self._milestone_id_counter + i:06d}",
                    "number": milestone_number,
                    "title": f"Milestone {milestone_number}",
                    "description": (
                        f"Test milestone {milestone_number}" if i % 2 == 0 else None
                    ),
                    "state": "closed" if is_closed else "open",
                    "creator": {
                        "login": f"milestone_user{milestone_number}",
                        "id": self._user_id_counter + i,
                        "avatar_url": (
                            f"https://github.com/milestone_user{milestone_number}.png"
                        ),
                        "html_url": (
                            f"https://github.com/milestone_user{milestone_number}"
                        ),
                    },
                    "created_at": f"2023-{min(1 + i, 12):02d}-01T00:00:00Z",
                    "updated_at": f"2023-{min(1 + i, 12):02d}-02T00:00:00Z",
                    "due_on": (
                        f"2023-{min(1 + i, 12):02d}-28T00:00:00Z"
                        if with_due_dates and i % 3 == 0
                        else None
                    ),
                    "closed_at": (
                        f"2023-{min(1 + i, 12):02d}-15T00:00:00Z" if is_closed else None
                    ),
                    "open_issues": 5 - (i * 2) if not is_closed else 0,
                    "closed_issues": i * 2,
                    "url": (
                        f"https://github.com/owner/repo/milestone/{milestone_number}"
                    ),
                }

                self.data["milestones"].append(milestone)

            self._milestone_id_counter += count
            # Only increment user counter if we're not using existing users
            if not self.data["users"]:
                self._user_id_counter += count

        return self

    def with_milestone_relationships(
        self,
        milestone_issue_mapping: Optional[Dict[int, List[int]]] = None,
    ) -> "GitHubDataBuilder":
        """Add milestone relationships to existing issues and PRs.

        Args:
            milestone_issue_mapping: Dict mapping milestone numbers to lists of
                issue numbers
        """
        if (
            not milestone_issue_mapping
            and self.data["milestones"]
            and self.data["issues"]
        ):
            # Auto-assign milestones to issues
            milestone_count = len(self.data["milestones"])
            for i, issue in enumerate(self.data["issues"]):
                milestone_number = (i % milestone_count) + 1
                # Find the milestone and assign a deep copy of the milestone object
                milestone = next(
                    (
                        m
                        for m in self.data["milestones"]
                        if m["number"] == milestone_number
                    ),
                    None,
                )
                if milestone:
                    import copy

                    issue["milestone"] = copy.deepcopy(milestone)

        elif milestone_issue_mapping:
            # Use explicit mapping
            for milestone_number, issue_numbers in milestone_issue_mapping.items():
                # Find the milestone and assign a deep copy of the milestone object
                milestone = next(
                    (
                        m
                        for m in self.data["milestones"]
                        if m["number"] == milestone_number
                    ),
                    None,
                )
                if milestone:
                    import copy

                    for issue_number in issue_numbers:
                        # Find issue and assign milestone
                        for issue in self.data["issues"]:
                            if issue["number"] == issue_number:
                                issue["milestone"] = copy.deepcopy(milestone)
                                break

        return self

    def with_sub_issues(
        self,
        parent_issue_numbers: Optional[List[int]] = None,
        sub_issues_per_parent: int = 2,
        max_hierarchy_depth: int = 3,
        custom_sub_issues: Optional[List[Dict[str, Any]]] = None,
    ) -> "GitHubDataBuilder":
        """Add sub-issues to the test data.

        Args:
            parent_issue_numbers: List of parent issue numbers to create sub-issues for
            sub_issues_per_parent: Number of sub-issues per parent
            max_hierarchy_depth: Maximum depth of hierarchy (not used yet,
                for future expansion)
            custom_sub_issues: Optional list of custom sub-issue data
        """
        if custom_sub_issues:
            self.data["sub_issues"].extend(custom_sub_issues)
        else:
            # Ensure we have some issues to be parents
            if not self.data["issues"]:
                self.with_issues(3)  # Create some default issues

            # Determine parent issues
            if parent_issue_numbers:
                parent_issues = [
                    issue
                    for issue in self.data["issues"]
                    if issue["number"] in parent_issue_numbers
                ]
            else:
                # Use first few issues as parents
                parent_issues = self.data["issues"][: min(2, len(self.data["issues"]))]

            # Create sub-issues for each parent
            current_issue_number = (
                max([issue["number"] for issue in self.data["issues"]], default=0) + 1
            )

            for parent_issue in parent_issues:
                for i in range(sub_issues_per_parent):
                    sub_issue_number = current_issue_number + i
                    sub_issue_id = self._sub_issue_id_counter + i

                    # Create the sub-issue as a regular issue
                    sub_issue = {
                        "id": sub_issue_id,
                        "number": sub_issue_number,
                        "title": (f"Sub-issue {i + 1} of #{parent_issue['number']}"),
                        "body": (
                            f"Sub-issue {i + 1} for parent issue "
                            f"#{parent_issue['number']}"
                        ),
                        "state": "open" if i % 2 == 0 else "closed",
                        "user": self._get_user_for_entity(i, "subissue_user"),
                        "assignees": [],
                        "labels": [],
                        "created_at": f"2023-01-{min(16 + i, 31):02d}T10:00:00Z",
                        "updated_at": f"2023-01-{min(16 + i, 31):02d}T10:00:00Z",
                        "closed_at": (
                            f"2023-01-{min(16 + i, 31):02d}T16:00:00Z"
                            if i % 2 == 1
                            else None
                        ),
                        "html_url": (
                            f"https://github.com/owner/repo/issues/{sub_issue_number}"
                        ),
                        "comments": 0,
                    }

                    # Create the sub-issue relationship
                    sub_issue_relationship = {
                        "sub_issue_id": sub_issue_id,
                        "sub_issue_number": sub_issue_number,
                        "parent_issue_id": parent_issue["id"],
                        "parent_issue_number": parent_issue["number"],
                        "position": i + 1,
                    }

                    self.data["issues"].append(sub_issue)
                    self.data["sub_issues"].append(sub_issue_relationship)

                current_issue_number += sub_issues_per_parent
                self._sub_issue_id_counter += sub_issues_per_parent

            # Only increment user counter if we're not using existing users
            if not self.data["users"]:
                self._user_id_counter += len(parent_issues) * sub_issues_per_parent

        return self

    def with_sub_issue_hierarchy(
        self,
        depth: int = 3,
        children_per_level: int = 2,
        include_orphaned: bool = False,
    ) -> "GitHubDataBuilder":
        """Create a complex sub-issue hierarchy.

        Args:
            depth: Depth of the hierarchy tree
            children_per_level: Number of children at each level
            include_orphaned: Whether to include orphaned sub-issues
        """
        # Ensure we have a root issue
        if not self.data["issues"]:
            self.with_issues(1)

        root_issue = self.data["issues"][0]
        current_issue_number = (
            max([issue["number"] for issue in self.data["issues"]], default=0) + 1
        )

        def create_hierarchy_level(parent_issue, current_depth, max_depth):
            nonlocal current_issue_number

            if current_depth >= max_depth:
                return current_issue_number

            for i in range(children_per_level):
                child_issue_number = current_issue_number
                child_issue_id = self._sub_issue_id_counter + (
                    current_issue_number - root_issue["number"] - 1
                )

                # Create child issue
                child_issue = {
                    "id": child_issue_id,
                    "number": child_issue_number,
                    "title": f"Level {current_depth + 1} Sub-issue {i + 1}",
                    "body": f"Sub-issue at depth {current_depth + 1}",
                    "state": "open" if (current_depth + i) % 2 == 0 else "closed",
                    "user": self._get_user_for_entity(i, "hierarchy_user"),
                    "assignees": [],
                    "labels": [],
                    "created_at": (
                        f"2023-01-{min(20 + current_depth + i, 31):02d}T10:00:00Z"
                    ),
                    "updated_at": (
                        f"2023-01-{min(20 + current_depth + i, 31):02d}T10:00:00Z"
                    ),
                    "closed_at": (
                        (f"2023-01-{min(20 + current_depth + i, 31):02d}T" f"16:00:00Z")
                        if (current_depth + i) % 2 == 1
                        else None
                    ),
                    "html_url": (
                        f"https://github.com/owner/repo/issues/{child_issue_number}"
                    ),
                    "comments": 0,
                }

                # Create relationship
                sub_issue_relationship = {
                    "sub_issue_id": child_issue_id,
                    "sub_issue_number": child_issue_number,
                    "parent_issue_id": parent_issue["id"],
                    "parent_issue_number": parent_issue["number"],
                    "position": i + 1,
                }

                self.data["issues"].append(child_issue)
                self.data["sub_issues"].append(sub_issue_relationship)

                current_issue_number += 1

                # Recurse for deeper levels
                current_issue_number = create_hierarchy_level(
                    child_issue, current_depth + 1, max_depth
                )

            return current_issue_number

        final_issue_number = create_hierarchy_level(root_issue, 0, depth)

        # Add orphaned sub-issues if requested
        if include_orphaned:
            orphaned_issue_id = self._sub_issue_id_counter + (
                final_issue_number - root_issue["number"]
            )
            orphaned_issue = {
                "id": orphaned_issue_id,
                "number": final_issue_number,
                "title": "Orphaned Sub-issue",
                "body": "This sub-issue has no parent",
                "state": "open",
                "user": self._get_user_for_entity(0, "orphan_user"),
                "assignees": [],
                "labels": [],
                "created_at": "2023-01-25T10:00:00Z",
                "updated_at": "2023-01-25T10:00:00Z",
                "closed_at": None,
                "html_url": (
                    f"https://github.com/owner/repo/issues/{final_issue_number}"
                ),
                "comments": 0,
            }

            # Orphaned relationship (parent doesn't exist)
            orphaned_relationship = {
                "sub_issue_id": orphaned_issue_id,
                "sub_issue_number": final_issue_number,
                "parent_issue_id": 99999,  # Non-existent parent
                "parent_issue_number": 99999,
                "position": 1,
            }

            self.data["issues"].append(orphaned_issue)
            self.data["sub_issues"].append(orphaned_relationship)

        # Update counters
        total_created = final_issue_number - root_issue["number"]
        self._sub_issue_id_counter += total_created
        # Only increment user counter if we're not using existing users
        if not self.data["users"]:
            self._user_id_counter += total_created

        return self

    def with_pr_reviews(
        self,
        pr_count: int = 2,
        reviews_per_pr: int = 1,
        include_requested_changes: bool = False,
        custom_reviews: Optional[List[Dict[str, Any]]] = None,
    ) -> "GitHubDataBuilder":
        """Add PR reviews to the test data.

        Args:
            pr_count: Number of PRs to add reviews to
            reviews_per_pr: Number of reviews per PR
            include_requested_changes: Whether to include reviews with requested changes
            custom_reviews: Optional list of custom review data
        """
        if custom_reviews:
            self.data["pr_reviews"].extend(custom_reviews)
        else:
            # Ensure we have enough PRs
            if len(self.data["pull_requests"]) < pr_count:
                self.with_pull_requests(pr_count)

            review_id = self._pr_review_id_counter
            review_states = ["APPROVED", "COMMENTED"]
            if include_requested_changes:
                review_states.append("CHANGES_REQUESTED")

            review_counter = 0
            for i in range(pr_count):
                pr = self.data["pull_requests"][i]
                pr_number = pr["number"]

                for j in range(reviews_per_pr):
                    review_state = review_states[review_counter % len(review_states)]
                    review_counter += 1
                    is_changes_requested = review_state == "CHANGES_REQUESTED"

                    review = {
                        "id": review_id,
                        "pull_request_number": pr_number,
                        "user": self._get_user_for_entity(j, "reviewer"),
                        "body": (
                            f"Review {j + 1} for PR {pr_number}"
                            if review_state == "COMMENTED"
                            else (
                                f"Changes requested for PR {pr_number}"
                                if is_changes_requested
                                else f"Approved PR {pr_number}"
                            )
                        ),
                        "state": review_state,
                        "commit_id": f"commit_{pr_number}_{j + 1}",
                        "submitted_at": (
                            f"2023-01-{min(15 + i, 31):02d}T"
                            f"{min(14 + j, 23):02d}:00:00Z"
                        ),
                        "html_url": (
                            f"https://github.com/owner/repo/pull/{pr_number}"
                            f"#pullrequestreview-{review_id}"
                        ),
                        "pull_request_url": (
                            f"https://github.com/owner/repo/pull/{pr_number}"
                        ),
                        "author_association": (
                            "COLLABORATOR" if j == 0 else "CONTRIBUTOR"
                        ),
                    }

                    self.data["pr_reviews"].append(review)
                    review_id += 1

            self._pr_review_id_counter = review_id
            # Only increment user counter if we're not using existing users
            if not self.data["users"]:
                self._user_id_counter += reviews_per_pr

        return self

    def with_pr_review_comments(
        self,
        review_count: int = 2,
        comments_per_review: int = 1,
        include_suggestions: bool = False,
        custom_review_comments: Optional[List[Dict[str, Any]]] = None,
    ) -> "GitHubDataBuilder":
        """Add PR review comments to the test data.

        Args:
            review_count: Number of reviews to add comments to
            comments_per_review: Number of comments per review
            include_suggestions: Whether to include code suggestions
            custom_review_comments: Optional list of custom review comment data
        """
        if custom_review_comments:
            self.data["pr_review_comments"].extend(custom_review_comments)
        else:
            # Ensure we have enough reviews
            if len(self.data["pr_reviews"]) < review_count:
                self.with_pr_reviews(pr_count=review_count, reviews_per_pr=1)

            comment_id = self._pr_review_comment_id_counter

            for i in range(min(review_count, len(self.data["pr_reviews"]))):
                review = self.data["pr_reviews"][i]
                pr_number = review["pull_request_number"]

                for j in range(comments_per_review):
                    is_suggestion = include_suggestions and j % 2 == 0

                    # Generate line numbers for code positioning
                    line_number = 10 + j * 5
                    original_line = line_number if j % 2 == 0 else None

                    comment_body = (
                        f"```suggestion\n# Suggested change for line {line_number}\n"
                        f"print('improved code')\n```"
                        if is_suggestion
                        else (
                            f"Review comment {j + 1} on PR {pr_number} - "
                            f"line {line_number}"
                        )
                    )

                    review_comment = {
                        "id": comment_id,
                        "pull_request_number": pr_number,
                        "pull_request_review_id": review["id"],
                        "user": self._get_user_for_entity(j, "review_commenter"),
                        "body": comment_body,
                        "commit_id": review["commit_id"],
                        "path": "src/main.py",
                        "position": line_number,
                        "original_position": original_line,
                        "line": line_number,
                        "original_line": original_line,
                        "diff_hunk": (
                            f"@@ -{line_number-2},{line_number+2} "
                            f"+{line_number-2},{line_number+2} @@\n"
                            f" context line {line_number-1}\n"
                            f"-old line {line_number}\n"
                            f"+new line {line_number}\n"
                            f" context line {line_number+1}"
                        ),
                        "created_at": (
                            f"2023-01-{min(15 + i, 31):02d}T"
                            f"{min(15 + j, 23):02d}:00:00Z"
                        ),
                        "updated_at": (
                            f"2023-01-{min(15 + i, 31):02d}T"
                            f"{min(15 + j, 23):02d}:00:00Z"
                        ),
                        "html_url": (
                            f"https://github.com/owner/repo/pull/{pr_number}"
                            f"#discussion_r{comment_id}"
                        ),
                        "pull_request_url": (
                            f"https://github.com/owner/repo/pull/{pr_number}"
                        ),
                        "author_association": (
                            "COLLABORATOR" if j == 0 else "CONTRIBUTOR"
                        ),
                        "start_line": line_number - 1 if j % 3 == 0 else None,
                        "start_side": "RIGHT" if j % 3 == 0 else None,
                        "side": "RIGHT",
                        "subject_type": "line",
                        "in_reply_to_id": comment_id - 1 if j > 0 else None,
                    }

                    self.data["pr_review_comments"].append(review_comment)
                    comment_id += 1

            self._pr_review_comment_id_counter = comment_id
            # Only increment user counter if we're not using existing users
            if not self.data["users"]:
                self._user_id_counter += comments_per_review

        return self

    def with_users(
        self,
        count: int = 5,
        include_organizations: bool = False,
        custom_users: Optional[List[Dict[str, Any]]] = None,
    ) -> "GitHubDataBuilder":
        """Add standalone user support to the test data.

        Args:
            count: Number of default users to create
            include_organizations: Include organization accounts alongside user accounts
            custom_users: Optional list of custom user data
        """
        if custom_users:
            for user in custom_users:
                # Ensure required fields
                if "id" not in user:
                    user["id"] = self._user_id_counter
                    self._user_id_counter += 1
                if "login" not in user:
                    user["login"] = f"custom_user{user['id']}"
                if "avatar_url" not in user:
                    user["avatar_url"] = f"https://github.com/{user['login']}.png"
                if "html_url" not in user:
                    user["html_url"] = f"https://github.com/{user['login']}"
                if "type" not in user:
                    user["type"] = "User"

            self.data["users"].extend(custom_users)
        else:
            # Create default users
            for i in range(count):
                user_id = self._user_id_counter
                is_org = (
                    include_organizations and i % 3 == 0
                )  # Every 3rd user is an org
                user_type = "Organization" if is_org else "User"
                login_prefix = "org" if is_org else "user"

                user = {
                    "login": f"{login_prefix}{user_id}",
                    "id": user_id,
                    "avatar_url": f"https://github.com/{login_prefix}{user_id}.png",
                    "html_url": f"https://github.com/{login_prefix}{user_id}",
                    "type": user_type,
                    "site_admin": False,
                    "name": f"Test {user_type} {user_id}",
                    "email": (
                        f"{login_prefix}{user_id}@example.com" if not is_org else None
                    ),
                    "bio": (
                        f"This is a test {user_type.lower()} account for testing "
                        f"purposes."
                    ),
                    "location": "Test City, TC",
                    "blog": f"https://{login_prefix}{user_id}.example.com",
                    "company": f"Test Company {user_id}" if not is_org else None,
                    "public_repos": i * 2,
                    "public_gists": i,
                    "followers": i * 10,
                    "following": i * 5,
                    "created_at": "2020-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                }

                # Add organization-specific fields
                if is_org:
                    user.update(
                        {
                            "description": (
                                f"Test organization {user_id} for development testing"
                            ),
                            "gravatar_id": "",
                            "organization_billing_email": (
                                f"billing@{login_prefix}{user_id}.example.com"
                            ),
                        }
                    )

                self.data["users"].append(user)
                self._user_id_counter += 1

        return self

    def with_repositories(
        self,
        count: int = 3,
        include_private: bool = False,
        include_archived: bool = False,
        custom_repositories: Optional[List[Dict[str, Any]]] = None,
    ) -> "GitHubDataBuilder":
        """Add repository metadata support to the test data.

        Args:
            count: Number of repositories to create
            include_private: Include private repositories
            include_archived: Include archived repositories
            custom_repositories: Optional list of custom repository data
        """
        if custom_repositories:
            for repo in custom_repositories:
                # Ensure required fields
                if "id" not in repo:
                    repo["id"] = self._repository_id_counter
                    self._repository_id_counter += 1
                if "name" not in repo:
                    repo["name"] = f"custom-repo-{repo['id']}"
                if "full_name" not in repo:
                    repo["full_name"] = f"owner/{repo['name']}"
                if "html_url" not in repo:
                    repo["html_url"] = f"https://github.com/{repo['full_name']}"

            self.data["repositories"].extend(custom_repositories)
        else:
            # Create default repositories
            for i in range(count):
                repo_id = self._repository_id_counter
                is_private = include_private and i % 2 == 0
                is_archived = include_archived and i % 3 == 0

                # Select owner from existing users or create default
                if self.data["users"]:
                    existing_user = self.data["users"][i % len(self.data["users"])]
                    # Create a copy to avoid reference issues
                    owner = {
                        "login": existing_user["login"],
                        "id": existing_user["id"],
                        "avatar_url": existing_user["avatar_url"],
                        "html_url": existing_user["html_url"],
                        "type": existing_user["type"],
                    }
                else:
                    owner = {
                        "login": f"repoowner{repo_id}",
                        "id": self._user_id_counter,
                        "avatar_url": f"https://github.com/repoowner{repo_id}.png",
                        "html_url": f"https://github.com/repoowner{repo_id}",
                        "type": "User",
                    }
                    self._user_id_counter += 1

                repo_name = f"test-repo-{repo_id}"
                full_name = f"{owner['login']}/{repo_name}"

                repository = {
                    "id": repo_id,
                    "name": repo_name,
                    "full_name": full_name,
                    "owner": owner,
                    "private": is_private,
                    "archived": is_archived,
                    "disabled": False,
                    "html_url": f"https://github.com/{full_name}",
                    "clone_url": f"https://github.com/{full_name}.git",
                    "ssh_url": f"git@github.com:{full_name}.git",
                    "git_url": f"git://github.com/{full_name}.git",
                    "description": (
                        f"Test repository {repo_id} for development and testing"
                    ),
                    "fork": i % 4 == 0,  # Every 4th repo is a fork
                    "homepage": f"https://{repo_name}.example.com",
                    "language": ["Python", "JavaScript", "Go", "Rust"][i % 4],
                    "forks_count": i * 2,
                    "stargazers_count": i * 10,
                    "watchers_count": i * 5,
                    "size": 1024 * (i + 1),
                    "default_branch": "main",
                    "open_issues_count": i,
                    "is_template": i % 5 == 0,  # Every 5th repo is a template
                    "topics": [f"topic-{j}" for j in range(i % 3 + 1)],
                    "has_issues": True,
                    "has_projects": True,
                    "has_wiki": i % 2 == 0,
                    "has_pages": i % 3 == 0,
                    "has_downloads": True,
                    "has_discussions": i % 2 == 1,
                    "allow_forking": True,
                    "allow_merge_commit": True,
                    "allow_squash_merge": True,
                    "allow_rebase_merge": i % 2 == 0,
                    "allow_auto_merge": False,
                    "delete_branch_on_merge": True,
                    "allow_update_branch": False,
                    "use_squash_pr_title_as_default": False,
                    "squash_merge_commit_title": "COMMIT_OR_PR_TITLE",
                    "squash_merge_commit_message": "COMMIT_MESSAGES",
                    "merge_commit_title": "MERGE_MESSAGE",
                    "merge_commit_message": "PR_TITLE",
                    "visibility": "private" if is_private else "public",
                    "permissions": {
                        "admin": True,
                        "maintain": True,
                        "push": True,
                        "triage": True,
                        "pull": True,
                    },
                    "security_and_analysis": {
                        "secret_scanning": {"status": "enabled"},
                        "secret_scanning_push_protection": {"status": "enabled"},
                        "dependabot_security_updates": {"status": "enabled"},
                        "secret_scanning_validity_checks": {"status": "enabled"},
                    },
                    "created_at": "2020-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "pushed_at": "2023-12-01T00:00:00Z",
                }

                self.data["repositories"].append(repository)
                self._repository_id_counter += 1

        return self

    def with_unicode_content(self) -> "GitHubDataBuilder":
        """Add issues and comments with unicode content for testing."""
        unicode_issue = {
            "id": self._issue_id_counter,
            "number": 999,
            "title": "Unicode test: 测试 🚀 Special chars: äöü",
            "body": "Unicode content: こんにちは 世界 🌍",
            "state": "open",
            "user": self._get_user_for_entity(0, "unicode-user"),
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
            "user": self._get_user_for_entity(1, "unicode-commenter"),
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
        # Only increment user counter if we're not using existing users
        if not self.data["users"]:
            self._user_id_counter += 2

        return self

    def validate_relationships(self) -> List[str]:
        """Validate relationships in the built data and return any errors."""
        errors = []

        # Validate milestone relationships
        milestone_numbers = {
            milestone["number"] for milestone in self.data["milestones"]
        }
        for issue in self.data["issues"]:
            if (
                issue.get("milestone")
                and issue["milestone"]["number"] not in milestone_numbers
            ):
                errors.append(
                    f"Issue #{issue['number']} references non-existent milestone "
                    f"#{issue['milestone']['number']}"
                )

        # Validate sub-issue relationships
        issue_ids = {issue["id"] for issue in self.data["issues"]}
        issue_numbers = {issue["number"] for issue in self.data["issues"]}

        for sub_issue_rel in self.data["sub_issues"]:
            # Check if sub-issue exists
            if sub_issue_rel["sub_issue_id"] not in issue_ids:
                errors.append(
                    f"Sub-issue relationship references non-existent sub-issue ID "
                    f"{sub_issue_rel['sub_issue_id']}"
                )

            # Check if parent issue exists (skip validation for intentionally
            # orphaned sub-issues)
            is_intentional_orphan = (
                sub_issue_rel["parent_issue_id"] == 99999
                and sub_issue_rel["parent_issue_number"] == 99999
            )
            if (
                sub_issue_rel["parent_issue_id"] not in issue_ids
                and not is_intentional_orphan
            ):
                errors.append(
                    f"Sub-issue #{sub_issue_rel['sub_issue_number']} references "
                    f"non-existent parent issue ID {sub_issue_rel['parent_issue_id']}"
                )

        # Validate comment relationships
        for comment in self.data["comments"]:
            if "issue_url" in comment:
                # Extract issue number from URL
                try:
                    issue_number = int(comment["issue_url"].split("/")[-1])
                    if issue_number not in issue_numbers:
                        errors.append(
                            f"Comment {comment['id']} references non-existent issue "
                            f"#{issue_number}"
                        )
                except (ValueError, IndexError):
                    errors.append(
                        f"Comment {comment['id']} has invalid issue_url format"
                    )

        # Validate PR review relationships
        pr_numbers = {pr["number"] for pr in self.data["pull_requests"]}
        for review in self.data["pr_reviews"]:
            if review["pull_request_number"] not in pr_numbers:
                errors.append(
                    f"Review {review['id']} references non-existent PR "
                    f"#{review['pull_request_number']}"
                )

        # Validate PR review comment relationships
        review_ids = {review["id"] for review in self.data["pr_reviews"]}
        for review_comment in self.data["pr_review_comments"]:
            if review_comment["pull_request_review_id"] not in review_ids:
                errors.append(
                    f"Review comment {review_comment['id']} references non-existent "
                    f"review #{review_comment['pull_request_review_id']}"
                )
            if review_comment["pull_request_number"] not in pr_numbers:
                errors.append(
                    f"Review comment {review_comment['id']} references non-existent PR "
                    f"#{review_comment['pull_request_number']}"
                )

        # Validate user references across all entities
        user_ids = {user["id"] for user in self.data["users"]}
        if user_ids:  # Only validate if standalone users exist
            # Check issue user references
            for issue in self.data["issues"]:
                if issue["user"]["id"] not in user_ids:
                    errors.append(
                        f"Issue #{issue['number']} references non-existent user ID "
                        f"{issue['user']['id']}"
                    )

            # Check PR user references
            for pr in self.data["pull_requests"]:
                if pr["user"]["id"] not in user_ids:
                    errors.append(
                        f"PR #{pr['number']} references non-existent user ID "
                        f"{pr['user']['id']}"
                    )

        # Validate repository relationships
        repo_ids = {repo["id"] for repo in self.data["repositories"]}
        if user_ids and repo_ids:  # Cross-validate repository owners
            for repo in self.data["repositories"]:
                if repo["owner"]["id"] not in user_ids:
                    errors.append(
                        f"Repository {repo['full_name']} references non-existent owner "
                        f"user ID {repo['owner']['id']}"
                    )

        return errors

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
            .with_users(8, include_organizations=True)
            .with_repositories(2, include_private=True, include_archived=False)
            .with_labels(3)
            .with_issues(5, include_closed=True)
            .with_comments(3, 2)
            .with_pull_requests(3)
            .with_pr_comments(2, 2)
            .with_pr_reviews(3, 2, include_requested_changes=True)
            .with_pr_review_comments(2, 2, include_suggestions=True)
            .with_milestones(3, include_closed=True, with_due_dates=True)
            .with_milestone_relationships()
            .with_sub_issues(parent_issue_numbers=[1, 2], sub_issues_per_parent=2)
            .with_unicode_content()
            .build()
        )

    def build_milestone_workflow(self) -> Dict[str, List[Dict[str, Any]]]:
        """Complete milestone workflow with issues and sub-issues."""
        return (
            GitHubDataBuilder()
            .with_labels(2)
            .with_milestones(2, include_closed=False, with_due_dates=True)
            .with_issues(4, include_closed=False)
            .with_milestone_relationships()
            .with_sub_issues(parent_issue_numbers=[1, 3], sub_issues_per_parent=2)
            .with_comments(2, 1)
            .build()
        )

    def build_hierarchical_issues(self) -> Dict[str, List[Dict[str, Any]]]:
        """Complex issue hierarchy with sub-issues and milestones."""
        return (
            GitHubDataBuilder()
            .with_labels(2)
            .with_milestones(1, include_closed=False, with_due_dates=True)
            .with_issues(1, include_closed=False)
            .with_milestone_relationships()
            .with_sub_issue_hierarchy(
                depth=3, children_per_level=2, include_orphaned=True
            )
            .build()
        )

    def build_pr_review_workflow(self) -> Dict[str, List[Dict[str, Any]]]:
        """Complete PR workflow with reviews and comments."""
        return (
            GitHubDataBuilder()
            .with_labels(2)
            .with_pull_requests(3)
            .with_pr_comments(2, 1)
            .with_pr_reviews(3, 2, include_requested_changes=True)
            .with_pr_review_comments(3, 3, include_suggestions=True)
            .build()
        )

    def build_multi_reviewer_workflow(self) -> Dict[str, List[Dict[str, Any]]]:
        """Multi-reviewer PR workflow with approval cycle."""
        return (
            GitHubDataBuilder()
            .with_labels(1)
            .with_pull_requests(2)
            .with_pr_reviews(2, 3, include_requested_changes=True)
            .with_pr_review_comments(2, 2, include_suggestions=True)
            .build()
        )

    def build_review_comment_thread(self) -> Dict[str, List[Dict[str, Any]]]:
        """PR with extensive review comment threads."""
        return (
            GitHubDataBuilder()
            .with_pull_requests(1)
            .with_pr_reviews(1, 1, include_requested_changes=False)
            .with_pr_review_comments(1, 5, include_suggestions=True)
            .build()
        )

    def build_complete_ecosystem(self) -> Dict[str, List[Dict[str, Any]]]:
        """Complete GitHub ecosystem with all entities and relationships."""
        return (
            GitHubDataBuilder()
            .with_users(10, include_organizations=True)
            .with_repositories(3, include_private=True, include_archived=True)
            .with_labels(5)
            .with_milestones(4, include_closed=True, with_due_dates=True)
            .with_issues(8, include_closed=True)
            .with_milestone_relationships()
            .with_sub_issues(parent_issue_numbers=[1, 3, 5], sub_issues_per_parent=3)
            .with_comments(5, 2)
            .with_pull_requests(4)
            .with_pr_comments(3, 2)
            .with_pr_reviews(4, 2, include_requested_changes=True)
            .with_pr_review_comments(3, 3, include_suggestions=True)
            .with_unicode_content()
            .build()
        )

    def build_user_focused_workflow(self) -> Dict[str, List[Dict[str, Any]]]:
        """User-focused workflow with organizations and repository ownership."""
        return (
            GitHubDataBuilder()
            .with_users(6, include_organizations=True)
            .with_repositories(4, include_private=True, include_archived=False)
            .with_labels(3)
            .with_issues(4, include_closed=False)
            .with_comments(2, 1)
            .with_pull_requests(2)
            .with_pr_reviews(2, 1, include_requested_changes=False)
            .build()
        )

    def build_repository_management_scenario(self) -> Dict[str, List[Dict[str, Any]]]:
        """Repository management scenario with varied configurations."""
        return (
            GitHubDataBuilder()
            .with_users(5, include_organizations=True)
            .with_repositories(5, include_private=True, include_archived=True)
            .with_labels(2)
            .with_issues(3, include_closed=False)
            .with_pull_requests(2)
            .build()
        )

    def build_cross_entity_relationships(self) -> Dict[str, List[Dict[str, Any]]]:
        """Complex cross-entity relationship validation scenario."""
        return (
            GitHubDataBuilder()
            .with_users(8, include_organizations=True)
            .with_repositories(3, include_private=True, include_archived=False)
            .with_labels(4)
            .with_milestones(3, include_closed=True, with_due_dates=True)
            .with_issues(6, include_closed=True)
            .with_milestone_relationships()
            .with_sub_issue_hierarchy(
                depth=4, children_per_level=2, include_orphaned=True
            )
            .with_comments(4, 3)
            .with_pull_requests(3)
            .with_pr_comments(2, 2)
            .with_pr_reviews(3, 3, include_requested_changes=True)
            .with_pr_review_comments(2, 4, include_suggestions=True)
            .build()
        )
