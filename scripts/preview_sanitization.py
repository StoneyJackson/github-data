#!/usr/bin/env python3
"""
Preview how content will be sanitized during restore operations.

This utility reads saved JSON files and shows what sanitization transformations
will be applied when the data is restored, without actually performing a restore.

Usage:
    python scripts/preview_sanitization.py <data-directory>

Example:
    python scripts/preview_sanitization.py ./save
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Import sanitization function
sys.path.insert(0, str(Path(__file__).parent.parent))
from github_data.github.sanitizers import sanitize_mentions


def load_json_file(file_path: Path) -> List[Dict[str, Any]]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}", file=sys.stderr)
        return []


def preview_field(entity_type: str, entity_id: str, field_name: str,
                  original: str) -> bool:
    """
    Preview sanitization for a single field.

    Returns True if sanitization would make changes, False otherwise.
    """
    if not original:
        return False

    sanitized = sanitize_mentions(original)

    if original != sanitized:
        print(f"\n{entity_type} {entity_id} - {field_name}:")
        print(f"  Original:  {original[:100]}{'...' if len(original) > 100 else ''}")
        print(f"  Sanitized: {sanitized[:100]}{'...' if len(sanitized) > 100 else ''}")
        return True

    return False


def preview_issues(data_dir: Path) -> int:
    """Preview issue sanitization. Returns count of changes."""
    issues_file = data_dir / "issues.json"
    if not issues_file.exists():
        return 0

    issues = load_json_file(issues_file)
    changes = 0

    for issue in issues:
        issue_id = f"#{issue.get('number', '?')}"

        if preview_field("Issue", issue_id, "body", issue.get('body', '')):
            changes += 1

    return changes


def preview_comments(data_dir: Path) -> int:
    """Preview comment sanitization. Returns count of changes."""
    comments_file = data_dir / "comments.json"
    if not comments_file.exists():
        return 0

    comments = load_json_file(comments_file)
    changes = 0

    for comment in comments:
        comment_id = f"comment-{comment.get('id', '?')}"

        if preview_field("Comment", comment_id, "body", comment.get('body', '')):
            changes += 1

    return changes


def preview_pull_requests(data_dir: Path) -> int:
    """Preview pull request sanitization. Returns count of changes."""
    prs_file = data_dir / "pull_requests.json"
    if not prs_file.exists():
        return 0

    prs = load_json_file(prs_file)
    changes = 0

    for pr in prs:
        pr_id = f"PR #{pr.get('number', '?')}"

        if preview_field("Pull Request", pr_id, "body", pr.get('body', '')):
            changes += 1

    return changes


def preview_pr_comments(data_dir: Path) -> int:
    """Preview PR comment sanitization. Returns count of changes."""
    comments_file = data_dir / "pr_comments.json"
    if not comments_file.exists():
        return 0

    comments = load_json_file(comments_file)
    changes = 0

    for comment in comments:
        comment_id = f"PR-comment-{comment.get('id', '?')}"

        if preview_field("PR Comment", comment_id, "body", comment.get('body', '')):
            changes += 1

    return changes


def preview_pr_reviews(data_dir: Path) -> int:
    """Preview PR review sanitization. Returns count of changes."""
    reviews_file = data_dir / "pr_reviews.json"
    if not reviews_file.exists():
        return 0

    reviews = load_json_file(reviews_file)
    changes = 0

    for review in reviews:
        review_id = f"review-{review.get('id', '?')}"

        if preview_field("PR Review", review_id, "body", review.get('body', '')):
            changes += 1

    return changes


def preview_pr_review_comments(data_dir: Path) -> int:
    """Preview PR review comment sanitization. Returns count of changes."""
    comments_file = data_dir / "pr_review_comments.json"
    if not comments_file.exists():
        return 0

    comments = load_json_file(comments_file)
    changes = 0

    for comment in comments:
        comment_id = f"review-comment-{comment.get('id', '?')}"

        if preview_field("PR Review Comment", comment_id, "body",
                        comment.get('body', '')):
            changes += 1

    return changes


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Preview sanitization that will occur during restore",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview sanitization for data in ./save directory
  python scripts/preview_sanitization.py ./save

  # Preview sanitization for specific repository backup
  python scripts/preview_sanitization.py ./backups/my-repo-2025-11-20
        """
    )
    parser.add_argument(
        'data_dir',
        type=Path,
        help='Directory containing saved JSON files'
    )

    args = parser.parse_args()

    if not args.data_dir.exists():
        print(f"Error: Directory not found: {args.data_dir}", file=sys.stderr)
        return 1

    if not args.data_dir.is_dir():
        print(f"Error: Not a directory: {args.data_dir}", file=sys.stderr)
        return 1

    print(f"Previewing sanitization for: {args.data_dir}")
    print("=" * 70)

    total_changes = 0
    total_changes += preview_issues(args.data_dir)
    total_changes += preview_comments(args.data_dir)
    total_changes += preview_pull_requests(args.data_dir)
    total_changes += preview_pr_comments(args.data_dir)
    total_changes += preview_pr_reviews(args.data_dir)
    total_changes += preview_pr_review_comments(args.data_dir)

    print("\n" + "=" * 70)
    if total_changes == 0:
        print("No sanitization changes needed - content is clean!")
    else:
        print(f"Total fields that will be sanitized: {total_changes}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
