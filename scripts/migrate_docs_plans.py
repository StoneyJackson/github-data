#!/usr/bin/env python3
"""
Migration script to reorganize docs/plans into active/completed structure.

This script:
1. Analyzes all markdown files in docs/plans
2. Groups files by topic patterns
3. Organizes completed work by quarter and work item
4. Generates a chronological index
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple


def parse_filename(filename: str) -> Tuple[str, str, str]:
    """
    Parse a filename to extract date, time, and topic.

    Expected format: YYYY-MM-DD-HH-MM-topic-description.md
    Returns: (date_str, time_str, topic)
    """
    # Remove .md extension
    name = filename.replace('.md', '')

    # Try to match the pattern YYYY-MM-DD-HH-MM-rest
    pattern = r'^(\d{4}-\d{2}-\d{2})-(\d{2}-\d{2})-(.+)$'
    match = re.match(pattern, name)

    if match:
        date_str = match.group(1)
        time_str = match.group(2)
        topic = match.group(3)
        return date_str, time_str, topic

    # Fallback: try YYYY-MM-DD-rest (no time)
    pattern = r'^(\d{4}-\d{2}-\d{2})-(.+)$'
    match = re.match(pattern, name)

    if match:
        date_str = match.group(1)
        topic = match.group(2)
        return date_str, "00-00", topic

    # If no pattern matches, return as-is
    return "unknown", "00-00", name


def get_quarter(date_str: str) -> str:
    """Convert date string to quarter format (e.g., 2025-Q3)."""
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        quarter = (date.month - 1) // 3 + 1
        return f"{date.year}-Q{quarter}"
    except ValueError:
        return "unknown"


def extract_topic_key(topic: str) -> str:
    """
    Extract a simplified topic key for grouping related files.

    Examples:
    - "strategy-pattern-implementation-plan" -> "strategy-pattern"
    - "entity-decomposition-analysis" -> "entity-decomposition"
    - "fix-test-failures" -> "fix-test-failures"
    """
    # Remove common suffixes
    suffixes = [
        '-plan', '-implementation', '-analysis', '-completion',
        '-design', '-refactor', '-refactoring', '-summary',
        '-session', '-review', '-fixes', '-continuation'
    ]

    topic_key = topic
    for suffix in suffixes:
        if topic_key.endswith(suffix):
            topic_key = topic_key[:-len(suffix)]

    # For very short topics after suffix removal, keep more context
    if len(topic_key) < 5 and topic != topic_key:
        # Keep one suffix level
        for suffix in suffixes:
            if topic.endswith(suffix):
                parts = topic.rsplit('-', 2)
                if len(parts) >= 2:
                    topic_key = '-'.join(parts[:-1])
                break

    return topic_key


def group_files_by_topic(files: List[Tuple[str, str, str, str]]) -> Dict[str, List[Tuple[str, str, str, str]]]:
    """
    Group files by topic key.

    Args:
        files: List of (filepath, date, time, topic) tuples

    Returns:
        Dict mapping topic_key to list of files
    """
    groups = defaultdict(list)

    for filepath, date, time, topic in files:
        topic_key = extract_topic_key(topic)
        groups[topic_key].append((filepath, date, time, topic))

    return dict(groups)


def create_work_item_name(topic_key: str, files: List[Tuple[str, str, str, str]]) -> str:
    """
    Create a readable work item directory name.

    If there's only one file for this topic, use a more descriptive name.
    Otherwise, use the topic key.
    """
    if len(files) == 1:
        # Single file - might be a one-off session
        _, _, _, topic = files[0]
        return topic
    else:
        # Multiple files - use the common topic key
        return topic_key


def migrate_files(source_dir: Path, dry_run: bool = False):
    """
    Migrate files from flat structure to active/completed structure.

    Args:
        source_dir: Path to docs/plans directory
        dry_run: If True, only print what would be done
    """
    print(f"Scanning {source_dir}...")

    # Find all markdown files
    all_files = []

    # Get files from root level
    for file in source_dir.glob('*.md'):
        date, time, topic = parse_filename(file.name)
        all_files.append((str(file), date, time, topic))

    # Get files from subdirectories (like 2025-09/)
    for subdir in source_dir.iterdir():
        if subdir.is_dir():
            for file in subdir.glob('*.md'):
                date, time, topic = parse_filename(file.name)
                all_files.append((str(file), date, time, topic))

    print(f"Found {len(all_files)} files to migrate")

    # Group files by topic
    topic_groups = group_files_by_topic(all_files)
    print(f"Identified {len(topic_groups)} topic groups")

    # Create directory structure
    completed_dir = source_dir / 'completed'
    active_dir = source_dir / 'active'

    if not dry_run:
        completed_dir.mkdir(exist_ok=True)
        active_dir.mkdir(exist_ok=True)

    # Organize by quarter and work item
    quarter_stats = defaultdict(int)
    moves = []

    for topic_key, files in topic_groups.items():
        # Determine which quarter(s) these files belong to
        quarters = set()
        for _, date, _, _ in files:
            quarter = get_quarter(date)
            quarters.add(quarter)

        # If files span multiple quarters, use the earliest
        primary_quarter = sorted(quarters)[0] if quarters else "unknown"

        # Create work item directory
        work_item_name = create_work_item_name(topic_key, files)
        work_item_dir = completed_dir / primary_quarter / work_item_name

        if not dry_run:
            work_item_dir.mkdir(parents=True, exist_ok=True)

        # Move files
        for filepath, date, time, topic in files:
            source_file = Path(filepath)
            dest_file = work_item_dir / source_file.name

            moves.append((source_file, dest_file))
            quarter_stats[primary_quarter] += 1

            if dry_run:
                print(f"  Would move: {source_file.relative_to(source_dir)} -> {dest_file.relative_to(source_dir)}")
            else:
                shutil.move(str(source_file), str(dest_file))

    # Print summary
    print("\nMigration Summary:")
    print(f"  Total files: {len(all_files)}")
    print(f"  Work items: {len(topic_groups)}")
    print("\nFiles per quarter:")
    for quarter in sorted(quarter_stats.keys()):
        print(f"  {quarter}: {quarter_stats[quarter]} files")

    return moves


def generate_chronology_index(source_dir: Path):
    """Generate a chronological index of all migrated files."""
    print("\nGenerating chronology index...")

    completed_dir = source_dir / 'completed'
    if not completed_dir.exists():
        print("No completed directory found")
        return

    # Collect all files with metadata
    all_files = []
    for quarter_dir in sorted(completed_dir.iterdir()):
        if not quarter_dir.is_dir():
            continue

        for work_item_dir in sorted(quarter_dir.iterdir()):
            if not work_item_dir.is_dir():
                continue

            # Collect both .md and .txt files
            for pattern in ['*.md', '*.txt']:
                for doc_file in sorted(work_item_dir.glob(pattern)):
                    date, time, topic = parse_filename(doc_file.name)
                    rel_path = doc_file.relative_to(source_dir)
                    all_files.append((date, time, topic, str(rel_path)))

    # Sort chronologically
    all_files.sort(key=lambda x: (x[0], x[1]))

    # Generate index
    index_content = ["# Chronological Index", ""]
    index_content.append(f"Total documents: {len(all_files)}")
    index_content.append("")

    current_quarter = None
    for date, time, topic, rel_path in all_files:
        quarter = get_quarter(date)

        if quarter != current_quarter:
            index_content.append(f"\n## {quarter}\n")
            current_quarter = quarter

        # Format: - 2025-09-15 15:08 - [topic](path)
        time_display = time.replace('-', ':') if time != "00-00" else ""
        display_name = topic.replace('-', ' ').title()
        index_content.append(f"- {date} {time_display} - [{display_name}]({rel_path})")

    # Write index file
    index_file = source_dir / 'chronology.md'
    with open(index_file, 'w') as f:
        f.write('\n'.join(index_content))

    print(f"Created chronology index: {index_file}")


def cleanup_empty_dirs(source_dir: Path):
    """Remove empty subdirectories after migration."""
    for item in source_dir.iterdir():
        if item.is_dir() and item.name not in ['completed', 'active']:
            # Check if empty
            if not any(item.iterdir()):
                print(f"Removing empty directory: {item}")
                item.rmdir()


if __name__ == '__main__':
    # Configuration
    source_dir = Path(__file__).parent.parent / 'docs' / 'plans'

    print("=" * 60)
    print("Documentation Plans Migration Script")
    print("=" * 60)

    # Execute migration
    moves = migrate_files(source_dir, dry_run=False)

    # Generate chronology
    generate_chronology_index(source_dir)

    # Cleanup
    cleanup_empty_dirs(source_dir)

    print("\n" + "=" * 60)
    print("Migration complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Review the new structure in docs/plans/completed/")
    print("  2. Check the chronology index at docs/plans/chronology.md")
    print("  3. Use docs/plans/active/ for new in-progress work")
