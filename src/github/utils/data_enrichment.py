"""
Data Enrichment Utilities for GitHub Data Project

This module provides utilities for enriching GitHub data with additional metadata,
including comment URL enrichment, sub-issue relationship building, and URL construction.
"""

from typing import List, Dict, Any


class CommentEnricher:
    """Utility for enriching GitHub comments with additional metadata."""

    @staticmethod
    def enrich_issue_comments(
        comments: List[Dict[str, Any]], issue_url: str
    ) -> List[Dict[str, Any]]:
        """
        Add issue URLs to comments.

        Args:
            comments (List[Dict[str, Any]]): List of comment dictionaries
            issue_url (str): URL of the parent issue

        Returns:
            List[Dict[str, Any]]: Enriched comments with issue_url added
        """
        for comment in comments:
            comment["issue_url"] = issue_url
        return comments

    @staticmethod
    def enrich_pr_comments(
        comments: List[Dict[str, Any]], pr_url: str
    ) -> List[Dict[str, Any]]:
        """
        Add pull request URLs to comments.

        Args:
            comments (List[Dict[str, Any]]): List of comment dictionaries
            pr_url (str): URL of the parent pull request

        Returns:
            List[Dict[str, Any]]: Enriched comments with pull_request_url added
        """
        for comment in comments:
            comment["pull_request_url"] = pr_url
        return comments

    @staticmethod
    def enrich_comments_from_parents(
        parent_nodes: List[Dict[str, Any]],
        comment_key: str = "comments",
        url_key: str = "url",
    ) -> List[Dict[str, Any]]:
        """
        Generic method to enrich comments from parent nodes.

        Args:
            parent_nodes: List of parent nodes containing comments
            comment_key: Key for accessing comments. Defaults to "comments".
            url_key (str, optional): Key for accessing parent URL. Defaults to "url".

        Returns:
            List[Dict[str, Any]]: Flattened and enriched comments
        """
        all_comments = []
        for parent in parent_nodes:
            parent_url = parent.get(url_key)
            if parent_url and comment_key in parent:
                comments = parent[comment_key].get("nodes", [])
                for comment in comments:
                    parent_type = parent.__class__.__name__.lower()
                    comment[f"{parent_type}_url"] = parent_url
                all_comments.append(comment)
        return all_comments


class SubIssueRelationshipBuilder:
    """Utility for building hierarchical sub-issue relationships."""

    @staticmethod
    def build_repository_relationships(
        issues_nodes: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Extract sub-issue relationships from repository issues.

        Args:
            issues_nodes (List[Dict[str, Any]]): List of issue nodes

        Returns:
            List[Dict[str, Any]]: List of sub-issue relationship objects
        """
        all_sub_issues = []
        for issue in issues_nodes:
            sub_issues = issue.get("subIssues", {}).get("nodes", [])
            for position, sub_issue in enumerate(sub_issues, 1):
                all_sub_issues.append(
                    SubIssueRelationshipBuilder.create_relationship_object(
                        sub_issue, issue, position, include_metadata=False
                    )
                )
        return all_sub_issues

    @staticmethod
    def build_issue_relationships(
        sub_issues_nodes: List[Dict[str, Any]], parent_issue: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Build enriched sub-issue relationships for a specific issue.

        Args:
            sub_issues_nodes (List[Dict[str, Any]]): List of sub-issue nodes
            parent_issue (Dict[str, Any]): Parent issue context

        Returns:
            List[Dict[str, Any]]: List of enriched sub-issue relationship objects
        """
        return [
            SubIssueRelationshipBuilder.create_relationship_object(
                sub_issue, parent_issue, position + 1, include_metadata=True
            )
            for position, sub_issue in enumerate(sub_issues_nodes)
        ]

    @staticmethod
    def create_relationship_object(
        sub_issue: Dict[str, Any],
        parent_issue: Dict[str, Any],
        position: int,
        include_metadata: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a standardized sub-issue relationship object.

        Args:
            sub_issue (Dict[str, Any]): Sub-issue details
            parent_issue (Dict[str, Any]): Parent issue details
            position (int): Position of sub-issue in parent's list
            include_metadata: Include additional metadata. Defaults to False.

        Returns:
            Dict[str, Any]: Standardized relationship object
        """
        relationship = {
            "sub_issue_id": sub_issue["id"],
            "sub_issue_number": sub_issue["number"],
            "parent_issue_id": parent_issue["id"],
            "parent_issue_number": parent_issue["number"],
            "position": position,
        }

        if include_metadata:
            relationship.update(
                {
                    "title": sub_issue.get("title"),
                    "state": sub_issue.get("state"),
                    "url": sub_issue.get("url"),
                }
            )

        return relationship


class URLEnricher:
    """Utility for constructing consistent GitHub and API URLs."""

    @staticmethod
    def build_api_url(repo_name: str, resource_type: str, resource_id: str) -> str:
        """
        Construct a consistent GitHub API URL.

        Args:
            repo_name (str): Repository name in owner/repo format
            resource_type (str): Type of resource (e.g., 'labels', 'issues')
            resource_id (str): Specific resource identifier

        Returns:
            str: Constructed API URL
        """
        base_url = "https://api.github.com/repos"
        return f"{base_url}/{repo_name}/{resource_type}/{resource_id}"

    @staticmethod
    def build_github_url(repo_name: str, resource_type: str, resource_id: str) -> str:
        """
        Construct a consistent GitHub web URL.

        Args:
            repo_name (str): Repository name in owner/repo format
            resource_type (str): Type of resource (e.g., 'issues', 'pull')
            resource_id (str): Specific resource identifier

        Returns:
            str: Constructed GitHub web URL
        """
        return f"https://github.com/{repo_name}/{resource_type}/{resource_id}"
