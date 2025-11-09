# Distributed Converter Registry Phase 2 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Migrate entities incrementally from the monolithic converters.py to distributed entity-specific converter modules, validating the pattern with each migration.

**Architecture:** Start with simple entities (labels, milestones) to validate the pattern, then proceed to complex entities (issues, pull requests). Each entity gets its own converters.py module with converter declarations in entity_config.py. Registry automatically discovers and loads distributed converters while maintaining legacy fallback.

**Tech Stack:** Python 3, entity config declarations, pytest for testing

---

## Prerequisites

**Files to review:**
- `github_data/github/converter_registry.py` - Registry implementation from Phase 1
- `github_data/github/converters.py` - Current monolithic converter file
- `github_data/entities/labels/entity_config.py` - Example entity config
- Design document: `docs/plans/active/architectural-improvements/2025-11-07-distributed-converter-registry-design.md`
- Phase 1 plan: `docs/plans/active/architectural-improvements/2025-11-07-distributed-converter-registry-phase1.md`

---

## Task 1: Migrate Labels Entity (Pilot)

**Rationale**: Labels entity is the simplest - single converter, no nested entities, good pilot for validating the pattern.

### Step 1: Review current labels converter

**Files:**
- Read: `github_data/github/converters.py`

Read the current `convert_to_label` implementation to understand what needs to be migrated.

Run: `grep -A 20 "def convert_to_label" github_data/github/converters.py`

Expected: See the current implementation

### Step 2: Create labels converter module

**Files:**
- Create: `github_data/entities/labels/converters.py`

```bash
touch github_data/entities/labels/converters.py
```

### Step 3: Write failing test for labels converter loading

**Files:**
- Modify: `tests/unit/entities/labels/test_converters.py`

Create or update test file:

```python
# tests/unit/entities/labels/test_converters.py
"""Unit tests for labels converters."""
import pytest


@pytest.mark.unit
def test_convert_to_label_loads_from_labels_entity():
    """convert_to_label should be loadable from labels entity package."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    # Should have the converter
    assert 'convert_to_label' in registry.list_converters()

    # Should have metadata showing it's from labels entity
    metadata = registry._converter_metadata['convert_to_label']
    assert metadata['entity'] == 'labels'
    assert 'entities.labels.converters' in metadata['module']


@pytest.mark.unit
def test_convert_to_label_transforms_raw_data_correctly():
    """convert_to_label should transform raw GitHub API data to Label model."""
    from github_data.github.converter_registry import get_converter
    from github_data.entities.labels.models import Label

    converter = get_converter('convert_to_label')

    raw_data = {
        "id": 123456,
        "name": "bug",
        "color": "d73a4a",
        "description": "Something isn't working",
        "default": True
    }

    result = converter(raw_data)

    assert isinstance(result, Label)
    assert result.id == 123456
    assert result.name == "bug"
    assert result.color == "d73a4a"
    assert result.description == "Something isn't working"
    assert result.default is True
```

### Step 4: Run tests to verify they fail

Run: `pytest tests/unit/entities/labels/test_converters.py::test_convert_to_label_loads_from_labels_entity -v`

Expected: `FAIL` - converter not yet declared in labels entity config

### Step 5: Implement labels converter module

**Files:**
- Modify: `github_data/entities/labels/converters.py`

```python
# github_data/entities/labels/converters.py
"""Converters for labels entity."""

from typing import Dict, Any
from .models import Label


def convert_to_label(raw_data: Dict[str, Any]) -> Label:
    """
    Convert raw GitHub API label data to Label model.

    Args:
        raw_data: Raw label data from GitHub API

    Returns:
        Label domain model
    """
    return Label(
        id=raw_data["id"],
        name=raw_data["name"],
        color=raw_data["color"],
        description=raw_data.get("description"),
        default=raw_data.get("default", False),
    )
```

### Step 6: Add converter declaration to labels entity config

**Files:**
- Modify: `github_data/entities/labels/entity_config.py`

Read current config:

Run: `cat github_data/entities/labels/entity_config.py`

Add converters declaration:

```python
# Add this to LabelsEntityConfig class
converters = {
    'convert_to_label': {
        'module': 'github_data.entities.labels.converters',
        'function': 'convert_to_label',
        'target_model': 'Label',
    },
}
```

### Step 7: Run tests to verify they pass

Run: `pytest tests/unit/entities/labels/test_converters.py -v`

Expected: `PASS` - converter loads from labels entity

### Step 8: Verify integration with existing code

Run: `pytest tests/unit/entities/labels/ -v`

Expected: All existing label tests still `PASS`

### Step 9: Verify converter registry picks up distributed converter

Run: `python -c "from github_data.github.converter_registry import ConverterRegistry; r = ConverterRegistry(); print(r._converter_metadata['convert_to_label'])"`

Expected: Output showing entity='labels', not 'legacy'

### Step 10: Commit labels entity migration

```bash
git add github_data/entities/labels/converters.py \
        github_data/entities/labels/entity_config.py \
        tests/unit/entities/labels/test_converters.py

git commit -s -m "feat(labels): migrate to distributed converter pattern

Move convert_to_label from monolithic converters.py to labels entity:
- Create labels/converters.py module
- Add converter declaration to entity config
- Add unit tests for converter loading and transformation

First entity migrated to distributed pattern (Phase 2 pilot).

Related to distributed-converter-registry-design Phase 2.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 2: Migrate Milestones Entity

**Rationale**: Milestones is also simple - single converter, minimal nesting, validates pattern again.

### Step 1: Create milestones converter module

**Files:**
- Create: `github_data/entities/milestones/converters.py`

```bash
touch github_data/entities/milestones/converters.py
```

### Step 2: Write failing test for milestones converter

**Files:**
- Create or Modify: `tests/unit/entities/milestones/test_converters.py`

```python
# tests/unit/entities/milestones/test_converters.py
"""Unit tests for milestones converters."""
import pytest


@pytest.mark.unit
def test_convert_to_milestone_loads_from_milestones_entity():
    """convert_to_milestone should load from milestones entity package."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    assert 'convert_to_milestone' in registry.list_converters()

    metadata = registry._converter_metadata['convert_to_milestone']
    assert metadata['entity'] == 'milestones'
    assert 'entities.milestones.converters' in metadata['module']


@pytest.mark.unit
def test_convert_to_milestone_transforms_data():
    """convert_to_milestone should transform raw data to Milestone model."""
    from github_data.github.converter_registry import get_converter
    from github_data.entities.milestones.models import Milestone

    converter = get_converter('convert_to_milestone')

    raw_data = {
        "id": 789,
        "number": 1,
        "title": "Version 1.0",
        "description": "First release",
        "state": "open",
        "open_issues": 5,
        "closed_issues": 10,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
        "due_on": "2024-12-31T00:00:00Z",
        "closed_at": None,
        "creator": {
            "id": 1,
            "login": "testuser",
            "type": "User",
        },
    }

    result = converter(raw_data)

    assert isinstance(result, Milestone)
    assert result.id == 789
    assert result.number == 1
    assert result.title == "Version 1.0"
```

### Step 3: Run test to verify it fails

Run: `pytest tests/unit/entities/milestones/test_converters.py::test_convert_to_milestone_loads_from_milestones_entity -v`

Expected: `FAIL` - not yet declared

### Step 4: Review current milestones converter

Run: `grep -A 30 "def convert_to_milestone" github_data/github/converters.py`

Expected: See current implementation (may use convert_to_user for creator)

### Step 5: Implement milestones converter module

**Files:**
- Modify: `github_data/entities/milestones/converters.py`

```python
# github_data/entities/milestones/converters.py
"""Converters for milestones entity."""

from typing import Dict, Any, Optional
from .models import Milestone
from github_data.github.converter_registry import get_converter


def convert_to_milestone(raw_data: Dict[str, Any]) -> Milestone:
    """
    Convert raw GitHub API milestone data to Milestone model.

    Args:
        raw_data: Raw milestone data from GitHub API

    Returns:
        Milestone domain model
    """
    # Use registry for nested user conversion
    creator = None
    if raw_data.get("creator"):
        creator = get_converter('convert_to_user')(raw_data["creator"])

    return Milestone(
        id=raw_data["id"],
        number=raw_data["number"],
        title=raw_data["title"],
        description=raw_data.get("description"),
        state=raw_data["state"],
        open_issues=raw_data.get("open_issues", 0),
        closed_issues=raw_data.get("closed_issues", 0),
        created_at=raw_data["created_at"],
        updated_at=raw_data.get("updated_at"),
        due_on=raw_data.get("due_on"),
        closed_at=raw_data.get("closed_at"),
        creator=creator,
    )
```

### Step 6: Add converter declaration to milestones config

**Files:**
- Modify: `github_data/entities/milestones/entity_config.py`

Add to MilestonesEntityConfig class:

```python
converters = {
    'convert_to_milestone': {
        'module': 'github_data.entities.milestones.converters',
        'function': 'convert_to_milestone',
        'target_model': 'Milestone',
    },
}
```

### Step 7: Run tests to verify they pass

Run: `pytest tests/unit/entities/milestones/test_converters.py -v`

Expected: `PASS`

### Step 8: Verify existing tests still pass

Run: `pytest tests/unit/entities/milestones/ -v`

Expected: All tests `PASS`

### Step 9: Commit milestones migration

```bash
git add github_data/entities/milestones/converters.py \
        github_data/entities/milestones/entity_config.py \
        tests/unit/entities/milestones/test_converters.py

git commit -s -m "feat(milestones): migrate to distributed converter pattern

Move convert_to_milestone from monolithic file to milestones entity.
Demonstrates nested converter usage via get_converter() for user.

Second entity migrated to distributed pattern (Phase 2).

Related to distributed-converter-registry-design Phase 2.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 3: Migrate Releases Entity (Multiple Converters)

**Rationale**: Releases entity has multiple converters (Release + ReleaseAsset), validating multi-converter declaration pattern.

### Step 1: Create releases converter module

**Files:**
- Create: `github_data/entities/releases/converters.py`

```bash
touch github_data/entities/releases/converters.py
```

### Step 2: Write failing tests for releases converters

**Files:**
- Create or Modify: `tests/unit/entities/releases/test_converters.py`

```python
# tests/unit/entities/releases/test_converters.py
"""Unit tests for releases converters."""
import pytest


@pytest.mark.unit
def test_convert_to_release_loads_from_releases_entity():
    """convert_to_release should load from releases entity package."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    assert 'convert_to_release' in registry.list_converters()

    metadata = registry._converter_metadata['convert_to_release']
    assert metadata['entity'] == 'releases'
    assert 'entities.releases.converters' in metadata['module']


@pytest.mark.unit
def test_convert_to_release_asset_loads_from_releases_entity():
    """convert_to_release_asset should load from releases entity package."""
    from github_data.github.converter_registry import ConverterRegistry

    registry = ConverterRegistry()

    assert 'convert_to_release_asset' in registry.list_converters()

    metadata = registry._converter_metadata['convert_to_release_asset']
    assert metadata['entity'] == 'releases'
    assert 'entities.releases.converters' in metadata['module']


@pytest.mark.unit
def test_convert_to_release_transforms_data():
    """convert_to_release should transform raw data correctly."""
    from github_data.github.converter_registry import get_converter
    from github_data.entities.releases.models import Release

    converter = get_converter('convert_to_release')

    raw_data = {
        "id": 12345,
        "tag_name": "v1.0.0",
        "name": "Version 1.0.0",
        "body": "Release notes",
        "draft": False,
        "prerelease": False,
        "created_at": "2024-01-01T00:00:00Z",
        "published_at": "2024-01-01T12:00:00Z",
        "author": {
            "id": 1,
            "login": "testuser",
            "type": "User",
        },
        "assets": [],
        "html_url": "https://github.com/test/repo/releases/tag/v1.0.0",
        "tarball_url": "https://api.github.com/repos/test/repo/tarball/v1.0.0",
        "zipball_url": "https://api.github.com/repos/test/repo/zipball/v1.0.0",
    }

    result = converter(raw_data)

    assert isinstance(result, Release)
    assert result.id == 12345
    assert result.tag_name == "v1.0.0"


@pytest.mark.unit
def test_convert_to_release_asset_transforms_data():
    """convert_to_release_asset should transform raw data correctly."""
    from github_data.github.converter_registry import get_converter
    from github_data.entities.releases.models import ReleaseAsset

    converter = get_converter('convert_to_release_asset')

    raw_data = {
        "id": 67890,
        "name": "release.zip",
        "content_type": "application/zip",
        "size": 1024000,
        "download_count": 42,
        "browser_download_url": "https://github.com/test/repo/releases/download/v1.0.0/release.zip",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "uploader": {
            "id": 1,
            "login": "testuser",
            "type": "User",
        },
    }

    result = converter(raw_data)

    assert isinstance(result, ReleaseAsset)
    assert result.id == 67890
    assert result.name == "release.zip"
```

### Step 3: Run tests to verify they fail

Run: `pytest tests/unit/entities/releases/test_converters.py -v`

Expected: `FAIL` - converters not yet declared

### Step 4: Review current releases converters

Run: `grep -A 40 "def convert_to_release" github_data/github/converters.py`

Run: `grep -A 30 "def convert_to_release_asset" github_data/github/converters.py`

Expected: See both converter implementations

### Step 5: Implement releases converter module

**Files:**
- Modify: `github_data/entities/releases/converters.py`

```python
# github_data/entities/releases/converters.py
"""Converters for releases entity."""

from typing import Dict, Any, Optional, List
from .models import Release, ReleaseAsset
from github_data.github.converter_registry import get_converter


def convert_to_release(raw_data: Dict[str, Any]) -> Release:
    """
    Convert raw GitHub API release data to Release model.

    Args:
        raw_data: Raw release data from GitHub API

    Returns:
        Release domain model
    """
    # Use registry for nested conversions
    assets = [
        convert_to_release_asset(asset)
        for asset in raw_data.get("assets", [])
    ]

    author = None
    if raw_data.get("author"):
        author = get_converter('convert_to_user')(raw_data["author"])

    return Release(
        id=raw_data["id"],
        tag_name=raw_data["tag_name"],
        name=raw_data.get("name"),
        body=raw_data.get("body"),
        draft=raw_data["draft"],
        prerelease=raw_data["prerelease"],
        created_at=raw_data["created_at"],
        published_at=raw_data.get("published_at"),
        author=author,
        assets=assets,
        html_url=raw_data["html_url"],
        tarball_url=raw_data.get("tarball_url"),
        zipball_url=raw_data.get("zipball_url"),
    )


def convert_to_release_asset(raw_data: Dict[str, Any]) -> ReleaseAsset:
    """
    Convert raw GitHub API release asset data to ReleaseAsset model.

    Args:
        raw_data: Raw asset data from GitHub API

    Returns:
        ReleaseAsset domain model
    """
    uploader = None
    if raw_data.get("uploader"):
        uploader = get_converter('convert_to_user')(raw_data["uploader"])

    return ReleaseAsset(
        id=raw_data["id"],
        name=raw_data["name"],
        content_type=raw_data["content_type"],
        size=raw_data["size"],
        download_count=raw_data["download_count"],
        browser_download_url=raw_data["browser_download_url"],
        created_at=raw_data["created_at"],
        updated_at=raw_data["updated_at"],
        uploader=uploader,
        local_path=raw_data.get("local_path"),
    )
```

### Step 6: Add converter declarations to releases config

**Files:**
- Modify: `github_data/entities/releases/entity_config.py`

Add to ReleasesEntityConfig class:

```python
converters = {
    'convert_to_release': {
        'module': 'github_data.entities.releases.converters',
        'function': 'convert_to_release',
        'target_model': 'Release',
    },
    'convert_to_release_asset': {
        'module': 'github_data.entities.releases.converters',
        'function': 'convert_to_release_asset',
        'target_model': 'ReleaseAsset',
    },
}
```

### Step 7: Run tests to verify they pass

Run: `pytest tests/unit/entities/releases/test_converters.py -v`

Expected: `PASS`

### Step 8: Verify existing tests still pass

Run: `pytest tests/unit/entities/releases/ -v`

Expected: All tests `PASS`

### Step 9: Commit releases migration

```bash
git add github_data/entities/releases/converters.py \
        github_data/entities/releases/entity_config.py \
        tests/unit/entities/releases/test_converters.py

git commit -s -m "feat(releases): migrate to distributed converter pattern

Move convert_to_release and convert_to_release_asset to releases entity.
Demonstrates multi-converter entity declaration.

Third entity migrated to distributed pattern (Phase 2).

Related to distributed-converter-registry-design Phase 2.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 4: Migrate Comments Entity

**Rationale**: Comments is straightforward - validates pattern with another simple entity.

### Step 1: Create comments converter module and tests

**Files:**
- Create: `github_data/entities/comments/converters.py`
- Create or Modify: `tests/unit/entities/comments/test_converters.py`

Follow same pattern as labels:
1. Create converter module file
2. Write failing tests
3. Implement converter using get_converter() for user
4. Add declaration to entity config
5. Run tests
6. Commit

### Step 2: Implementation details

Converter should transform:
- `raw_data` → `Comment` model
- Use `get_converter('convert_to_user')` for user field

Config declaration:

```python
converters = {
    'convert_to_comment': {
        'module': 'github_data.entities.comments.converters',
        'function': 'convert_to_comment',
        'target_model': 'Comment',
    },
}
```

### Step 3: Commit

```bash
git commit -s -m "feat(comments): migrate to distributed converter pattern

Move convert_to_comment to comments entity.

Fourth entity migrated to distributed pattern (Phase 2).

Related to distributed-converter-registry-design Phase 2.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 5: Migrate Issues Entity (Complex)

**Rationale**: Issues entity is complex with many nested converters - validates pattern handles complexity.

### Step 1: Create issues converter module

**Files:**
- Create: `github_data/entities/issues/converters.py`

```bash
touch github_data/entities/issues/converters.py
```

### Step 2: Write comprehensive tests

**Files:**
- Create or Modify: `tests/unit/entities/issues/test_converters.py`

Test should verify:
- Converter loads from issues entity
- Transforms raw data correctly
- Handles all nested entities (labels, milestone, user, assignees, comments)

### Step 3: Review current issues converter

Run: `grep -A 60 "def convert_to_issue" github_data/github/converters.py`

Expected: See complex converter with many nested conversions

### Step 4: Implement issues converter

**Files:**
- Modify: `github_data/entities/issues/converters.py`

```python
# github_data/entities/issues/converters.py
"""Converters for issues entity."""

from typing import Dict, Any, Optional, List
from .models import Issue
from github_data.github.converter_registry import get_converter


def convert_to_issue(raw_data: Dict[str, Any]) -> Issue:
    """
    Convert raw GitHub API issue data to Issue model.

    Args:
        raw_data: Raw issue data from GitHub API

    Returns:
        Issue domain model
    """
    # Use registry for all nested conversions
    labels = [
        get_converter('convert_to_label')(label)
        for label in raw_data.get("labels", [])
    ]

    milestone = None
    if raw_data.get("milestone"):
        milestone = get_converter('convert_to_milestone')(raw_data["milestone"])

    user = None
    if raw_data.get("user"):
        user = get_converter('convert_to_user')(raw_data["user"])

    assignees = [
        get_converter('convert_to_user')(assignee)
        for assignee in raw_data.get("assignees", [])
    ]

    # Comments handled separately in save/restore workflows

    return Issue(
        id=raw_data["id"],
        number=raw_data["number"],
        title=raw_data["title"],
        body=raw_data.get("body"),
        state=raw_data["state"],
        labels=labels,
        assignees=assignees,
        milestone=milestone,
        comments_count=raw_data.get("comments", 0),
        created_at=raw_data["created_at"],
        updated_at=raw_data.get("updated_at"),
        closed_at=raw_data.get("closed_at"),
        user=user,
        html_url=raw_data["html_url"],
        locked=raw_data.get("locked", False),
    )
```

### Step 5: Add converter declaration

**Files:**
- Modify: `github_data/entities/issues/entity_config.py`

```python
converters = {
    'convert_to_issue': {
        'module': 'github_data.entities.issues.converters',
        'function': 'convert_to_issue',
        'target_model': 'Issue',
    },
}
```

### Step 6: Run tests

Run: `pytest tests/unit/entities/issues/test_converters.py -v`

Expected: `PASS`

Run: `pytest tests/unit/entities/issues/ -v`

Expected: All tests `PASS`

### Step 7: Commit issues migration

```bash
git commit -s -m "feat(issues): migrate to distributed converter pattern

Move convert_to_issue to issues entity. Demonstrates complex entity
with multiple nested converters accessed via registry.

Fifth entity migrated to distributed pattern (Phase 2).

Related to distributed-converter-registry-design Phase 2.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 6: Migrate Pull Requests Entity (Complex)

**Rationale**: Pull requests is the most complex entity - validates pattern handles maximum complexity.

### Step 1: Create pull requests converter module and tests

**Files:**
- Create: `github_data/entities/pull_requests/converters.py`
- Create or Modify: `tests/unit/entities/pull_requests/test_converters.py`

### Step 2: Review current PR converter

Run: `grep -A 80 "def convert_to_pull_request" github_data/github/converters.py`

Expected: See very complex converter

### Step 3: Implement PR converter

Similar to issues but with additional fields:
- base/head branch info
- merged status
- review comments
- etc.

Use `get_converter()` for all nested entities.

### Step 4: Add declaration and test

Follow same pattern as previous entities.

### Step 5: Commit

```bash
git commit -s -m "feat(pull_requests): migrate to distributed converter pattern

Move convert_to_pull_request to pull_requests entity. Most complex
entity validates pattern handles all complexity scenarios.

Sixth entity migrated to distributed pattern (Phase 2).

Related to distributed-converter-registry-design Phase 2.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 7: Migrate Remaining Entities

**Rationale**: Complete migration for all remaining entities.

### Entities to Migrate

Review entity registry to identify all entities:

Run: `find github_data/entities -name entity_config.py -type f`

For each remaining entity without converters:
1. Create converter module
2. Write tests
3. Implement converter
4. Add declaration
5. Test
6. Commit

### Batch Commit Strategy

Can commit entities in logical groups:

```bash
git commit -s -m "feat(entities): migrate <entity_group> to distributed converter pattern

Migrate <list of entities> to distributed converter pattern.

Related to distributed-converter-registry-design Phase 2.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 8: Run Comprehensive Validation

**Files:**
- All test files

### Step 1: Run full test suite

Run: `make test`

Expected: All tests `PASS`

### Step 2: Run integration tests

Run: `pytest tests/integration/github/test_distributed_converters.py -v`

Expected: All tests `PASS`

### Step 3: Verify all converters migrated

Run: `python -c "
from github_data.github.converter_registry import ConverterRegistry
r = ConverterRegistry()
legacy_count = sum(1 for name, meta in r._converter_metadata.items() if meta['entity'] == 'legacy')
distributed_count = sum(1 for name, meta in r._converter_metadata.items() if meta['entity'] != 'legacy')
total = len(r.list_converters())
print(f'Total converters: {total}')
print(f'Distributed: {distributed_count}')
print(f'Legacy: {legacy_count}')
if legacy_count == 0 or legacy_count == 1:  # Only convert_to_user might remain
    print('✓ Migration complete!')
else:
    print(f'⚠ {legacy_count} converters still in legacy file')
"`

Expected: Most or all converters migrated from legacy

### Step 4: Check test coverage

Run: `pytest tests/unit/entities/*/test_converters.py --cov=github_data.entities --cov-report=term-missing`

Expected: Good coverage for all entity converters

### Step 5: Run quality checks

Run: `make check-all`

Expected: All checks `PASS`

---

## Task 9: Document Migration Completion

**Files:**
- Create: `docs/plans/2025-11-07-phase2-completion-summary.md`

### Step 1: Create completion summary

```markdown
# Phase 2 Completion Summary

**Date**: 2025-11-07
**Status**: Complete
**Related**: distributed-converter-registry-design.md

## Completed Tasks

### Entity Migrations

- ✅ Labels entity migrated (pilot)
- ✅ Milestones entity migrated
- ✅ Releases entity migrated (multi-converter)
- ✅ Comments entity migrated
- ✅ Issues entity migrated (complex)
- ✅ Pull Requests entity migrated (most complex)
- ✅ [List other migrated entities]

### Migration Statistics

- **Total entities migrated**: X
- **Total converters migrated**: Y
- **Converters remaining in legacy**: Z (likely just convert_to_user)
- **Test coverage**: >90%

## Validation Results

**Test Results**:
- All entity tests: PASS
- Integration tests: PASS
- Converter registry tests: PASS
- Full test suite: PASS

**Quality Checks**:
- Linting: PASS
- Formatting: PASS
- Type checking: PASS

## Migration Lessons Learned

### What Went Well

- Pattern validated with simple entities first
- Registry handles complex nested conversions
- get_converter() provides good loose coupling
- No regressions in existing functionality

### Challenges

- [Document any challenges encountered]

### Best Practices

- Always test converter loading and transformation
- Use get_converter() for all nested conversions
- Follow same structure for all entity converters
- Write tests before implementing

## Phase 2 Success Criteria

- [x] Simple entities migrated successfully
- [x] Complex entities migrated successfully
- [x] All tests pass with no regressions
- [x] Converters properly declared in entity configs
- [x] Legacy fallback no longer needed (or minimal)

## Ready for Phase 3

All entities have been migrated to distributed converter pattern.
Ready for Phase 3 cleanup: remove legacy converter loading code.

## Files Created/Modified

**New converter modules**:
- github_data/entities/labels/converters.py
- github_data/entities/milestones/converters.py
- github_data/entities/releases/converters.py
- [etc for all entities]

**Modified entity configs**:
- github_data/entities/*/entity_config.py (added converter declarations)

**New test files**:
- tests/unit/entities/*/test_converters.py

## Next Steps (Phase 3)

1. Remove _load_legacy_converters() backward compatibility code
2. Reduce converters.py to only common converters (convert_to_user, etc)
3. Update documentation
4. Final validation
5. Mark architectural improvement complete
```

### Step 2: Save completion summary

Run: `write completion summary to file`

### Step 3: Commit documentation

```bash
git add docs/plans/2025-11-07-phase2-completion-summary.md
git commit -s -m "docs(converters): add Phase 2 completion summary

Phase 2 of distributed converter registry complete:
- All entities migrated from monolithic converters.py
- Each entity has own converter module with declarations
- All tests passing with comprehensive coverage
- Ready for Phase 3 cleanup

Related to distributed-converter-registry-design Phase 2.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 10: Update Architecture Documentation

**Files:**
- Modify: `docs/architecture/converter-registry.md`
- Modify: `docs/development/adding-entities.md`

### Step 1: Update converter registry architecture doc

Remove or update sections about "Phase 2+" future work.

Update to reflect current state:
- All entities using distributed pattern
- How to add new entities now requires converter module
- Pattern is now standard

### Step 2: Update entity addition guide

Remove "Phase 2+" conditional language.

Make converter creation mandatory for new entities.

### Step 3: Commit documentation updates

```bash
git commit -s -m "docs(converters): update documentation for completed Phase 2

Update architecture and entity guides to reflect completed migration:
- Distributed converter pattern is now standard
- All entities follow the pattern
- Remove conditional Phase 2 language

Related to distributed-converter-registry-design Phase 2.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Phase 2 Complete!

The incremental entity migration is now complete. All entities use the distributed converter pattern with converters colocated in entity packages.

### What Was Built

1. **Migrated all entities** from monolithic converters.py to distributed pattern
2. **Created converter modules** for each entity package
3. **Added converter declarations** to all entity configs
4. **Comprehensive test coverage** for all converters
5. **Validated pattern** with simple and complex entities

### Validation

- ✅ All tests pass (unit, integration, container)
- ✅ No regressions in existing functionality
- ✅ All entities have converter declarations
- ✅ Pattern handles simple and complex cases

### Ready for Phase 3

Can now proceed to Phase 3: cleanup and finalization.
- Remove legacy converter loading
- Clean up monolithic converters.py
- Final documentation updates
