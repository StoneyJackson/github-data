# GitHub Releases and Tags Feature Design

**Document Type:** Feature Design
**Feature:** GitHub Releases and Tags Support
**Date:** 2025-11-02
**Status:** Design Approved - Ready for Implementation

## Overview

This document describes the design for adding GitHub releases and tags support to the github-data project. This feature enables complete backup and restoration of repository releases, including release metadata and binary assets.

## Background

### Current State

The github-data project currently supports:
- Labels, issues, comments, sub-issues
- Pull requests with reviews and comments
- Milestones
- Git repository backup (mirror format with tags)

### Gap Analysis

**Missing capability:** GitHub releases provide a metadata layer on top of git tags that includes:
- Release notes and descriptions
- Binary asset attachments (up to 1000 per release, each up to 2 GiB)
- Draft/prerelease/immutable status flags
- Author attribution and timestamps
- Download tracking and URLs

While git tags are saved via mirror clone, the GitHub release metadata and assets are not captured.

### User Value

Releases are essential for:
- Complete repository migration scenarios
- Version history preservation with release notes
- Binary artifact backup and restore
- Project documentation continuity
- Semantic versioning workflows

## Design Goals

1. **Complete data migration by default** - Assets and metadata included unless opted out
2. **Follow established patterns** - Mirror milestone entity implementation
3. **Flexible configuration** - Allow metadata-only or full backup modes
4. **Performance conscious** - Handle large assets gracefully with progress reporting
5. **Relationship preservation** - Maintain connection to git tags

## Architecture

### Entity Structure

Following the milestone pattern exactly:

```
github_data/entities/releases/
├── __init__.py              # Entity exports
├── models.py                # Release and ReleaseAsset models
├── entity_config.py         # EntityRegistry configuration
├── save_strategy.py         # Save operation implementation
└── restore_strategy.py      # Restore operation implementation
```

### Data Models

**ReleaseAsset Model:**
```python
class ReleaseAsset(BaseModel):
    """Release asset (binary attachment)."""
    id: Union[int, str]
    name: str
    content_type: str
    size: int
    download_count: int
    browser_download_url: str
    created_at: datetime
    updated_at: datetime
    uploader: GitHubUser
    local_path: Optional[str] = None  # Path when downloaded
```

**Release Model:**
```python
class Release(BaseModel):
    """GitHub release entity."""
    id: Union[int, str]
    tag_name: str
    target_commitish: str  # Branch or commit SHA
    name: Optional[str] = None
    body: Optional[str] = None  # Release notes (markdown)
    draft: bool = False
    prerelease: bool = False
    immutable: bool = False  # New 2025 GitHub feature
    created_at: datetime
    published_at: Optional[datetime] = None
    author: GitHubUser
    assets: List[ReleaseAsset] = []
    html_url: str
```

**Field Notes:**
- `download_count` is read-only, cannot be restored
- `immutable` flag cannot be set via API (org/repo setting)
- `local_path` added to asset for restore reference

### Entity Configuration

```python
class ReleasesEntityConfig:
    """Configuration for releases entity."""

    name = "releases"
    env_var = "INCLUDE_RELEASES"
    default_value = True
    value_type = bool
    dependencies: List[str] = []
    description = "Repository releases and tags"

    # Service requirements
    required_services_save: List[str] = []
    required_services_restore: List[str] = []

    # Asset control (separate configuration)
    asset_env_var = "INCLUDE_RELEASE_ASSETS"
    asset_default_value = True  # Complete backup by default
```

### Environment Variables

Two independent controls for flexibility:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `INCLUDE_RELEASES` | boolean | `true` | Enable releases save/restore |
| `INCLUDE_RELEASE_ASSETS` | boolean | `true` | Include asset download/upload |

**Configuration Examples:**

```bash
# 1. Complete backup (default)
INCLUDE_RELEASES=true
INCLUDE_RELEASE_ASSETS=true

# 2. Metadata-only (fast, low storage)
INCLUDE_RELEASES=true
INCLUDE_RELEASE_ASSETS=false

# 3. Skip releases entirely
INCLUDE_RELEASES=false
```

**Validation Rules:**
- `INCLUDE_RELEASE_ASSETS=true` requires `INCLUDE_RELEASES=true`
- Warning if `INCLUDE_RELEASE_ASSETS=true` but `INCLUDE_GIT_REPO=false`

## Data Flow

### Save Operation

**Step 1: Fetch Releases**
- API: `GET /repos/{owner}/{repo}/releases` (REST API)
- Pagination: Handle repositories with many releases
- Note: GraphQL doesn't fully support releases API yet

**Step 2: Process Assets (if enabled)**
- For each release asset:
  - Download binary via `browser_download_url`
  - Save to `data/github-data/release-assets/{tag_name}/{filename}`
  - Store `local_path` in asset JSON
  - Report progress: "Downloading asset 3/15: myapp-v1.2.0.tar.gz (125 MB)"

**Step 3: Save Metadata**
- Write all releases to `data/github-data/releases.json`
- Include asset metadata with local paths

### Restore Operation

**Step 1: Create Releases**
- API: `POST /repos/{owner}/{repo}/releases`
- Process in chronological order (oldest first)
- Preserve draft/prerelease/immutable flags
- Handle tag conflicts (fail with clear error)

**Step 2: Upload Assets (if available)**
- For each asset with `local_path`:
  - Read binary from local storage
  - Upload via `POST {upload_url}` with content
  - Preserve filename and content-type
  - Validate 2 GiB size limit

**Step 3: Metadata Preservation**
- Author attribution in release body
- Timestamps in release description
- Note if original was immutable (cannot be set via API)

### Storage Format

```
/data/
├── github-data/
│   ├── releases.json          # All release metadata + asset refs
│   ├── labels.json            # Existing
│   ├── issues.json            # Existing
│   └── release-assets/        # Binary files (if enabled)
│       ├── v1.0.0/
│       │   ├── app-linux.tar.gz
│       │   ├── app-macos.tar.gz
│       │   └── checksums.txt
│       └── v2.0.0/
│           ├── app-linux.tar.gz
│           └── app-macos.tar.gz
└── git-repo/                   # Existing git mirror
    └── .git/                   # Includes tags
```

## Dependencies & Integration

### Relationship to Git Repository Backup

- **Git tags**: Already saved via mirror clone when `INCLUDE_GIT_REPO=true`
- **Releases**: Add GitHub metadata layer on top of tags
- **Independence**: Releases can be saved without git repo (metadata-only scenario)
- **Coordination**: Release `tag_name` must match existing git tag for full functionality

### Entity Dependencies

```
releases → (no dependencies)
  ├── Uses existing GitHubUser entity (for author/uploader)
  └── Independent of issues/PRs/milestones
```

No dependencies means releases can be enabled/disabled independently.

### API Integration

**REST API Endpoints:**
- `GET /repos/{owner}/{repo}/releases` - List releases
- `GET /repos/{owner}/{repo}/releases/{id}` - Get specific release
- `POST /repos/{owner}/{repo}/releases` - Create release
- `POST {upload_url}` - Upload asset
- Asset download via `browser_download_url`

**Rate Limiting:**
- Same retry logic as other entities
- Exponential backoff for asset downloads
- Progress reporting for long-running operations

## Error Handling

### Save Operation Errors

| Error | Handling |
|-------|----------|
| Release fetch failure | Propagate exception, fail operation |
| Asset download failure | Warn, continue with other assets |
| Network timeout | Retry with exponential backoff (max 3) |
| Asset too large (>2 GiB) | Skip asset, log warning |
| Storage full | Fail operation with clear error |

### Restore Operation Errors

| Error | Handling |
|-------|----------|
| Tag already exists | Fail with conflict error |
| Asset upload failure | Warn, continue with release metadata |
| Asset file missing | Warn, skip asset upload |
| Invalid release data | Fail with validation error |
| API authentication failure | Propagate exception |

### Immutable Release Handling

- **Save**: Capture `immutable` flag in JSON
- **Restore**: Cannot set via API (org/repo setting only)
- **Documentation**: Add note to release body if originally immutable
- **User guidance**: Document manual steps for immutable setup

## Testing Strategy

### Unit Tests

**File:** `tests/unit/test_release_models.py`
- Model validation and serialization
- Asset path handling and sanitization
- Tag name validation
- Date/time handling

**File:** `tests/unit/test_release_error_handling.py`
- API error scenarios (rate limits, 404, 403, 5xx)
- Network timeout handling
- Invalid data handling
- Missing file scenarios
- Asset size validation

**File:** `tests/unit/test_release_edge_cases.py`
- Unicode in release names/bodies
- Large asset sets (100+ files)
- Empty releases (no assets)
- Releases without tags (drafts)
- Asset name conflicts
- Extremely long fields

### Integration Tests

**File:** `tests/integration/test_release_save_restore.py`
- Save/restore round-trip with mocked GitHub API
- Asset download/upload simulation
- Pagination handling
- Chronological ordering verification
- Metadata preservation validation

**File:** `tests/integration/test_release_api_integration.py`
- REST API interaction patterns
- Rate limiting behavior
- Error recovery and retries
- Progress reporting accuracy

### Container Tests

**File:** `tests/integration/test_release_container_workflows.py`
- Full Docker workflow with `INCLUDE_RELEASES=true`
- Asset persistence across container runs
- Environment variable validation (both boolean formats)
- Volume mounting for large assets
- Multi-release backup/restore scenarios

**Test Coverage Goals:**
- Unit tests: 90%+ coverage
- Integration tests: Key workflows validated
- Container tests: Complete end-to-end validation
- Performance: Benchmark large asset operations

## Performance Considerations

### Asset Download/Upload

- **Large files**: Progress reporting every 10%
- **Parallel operations**: Download multiple assets concurrently (limit 5)
- **Streaming**: Stream large files to avoid memory issues
- **Resumable**: Consider resumable downloads for very large assets (future)

### Storage Impact

- **Typical release**: 50-500 MB per version
- **Large projects**: Multiple GB across all releases
- **Mitigation**: Default to metadata-only via env var (future consideration)
- **User control**: Clear documentation of storage requirements

### API Rate Limits

- **Release listing**: 1 API call + pagination
- **Asset download**: Uses direct URLs (no API limit)
- **Asset upload**: 1 API call per asset
- **Typical impact**: Minimal for most repositories

## Documentation Updates

### README.md Updates

Add releases section after milestones:

```markdown
### GitHub Metadata Management
- **Labels**: Complete label save/restore with conflict resolution
- **Issues & Comments**: Full issue data with hierarchical sub-issues
- **Milestones**: Project milestone organization
- **Releases & Tags**: Version releases with binary assets
- **Pull Requests**: PR workflows with branch dependency validation
```

Add environment variables:

```markdown
| `INCLUDE_RELEASES` | No | Include releases in save/restore operations (default: `true`) |
| `INCLUDE_RELEASE_ASSETS` | No | Include release asset binaries (default: `true`) |
```

Add usage examples in selective operations section.

### TODO.md Updates

Move from "Future Roadmap" to "Completed Features":

```markdown
✅ **Releases and tags** - version release metadata and binary assets
```

### CLAUDE.md Updates

Add to completed features:
- Release save and restore with asset support

## Implementation Phases

### Phase 1: Core Entity Structure (2-3 hours)
- Create `entities/releases/` directory
- Implement models with Pydantic validation
- Create entity configuration
- Unit tests for models

### Phase 2: Save Strategy (3-4 hours)
- Implement REST API integration
- Asset download logic with progress
- JSON storage implementation
- Integration tests for save

### Phase 3: Restore Strategy (3-4 hours)
- Release creation via API
- Asset upload implementation
- Error handling and validation
- Integration tests for restore

### Phase 4: Testing & Validation (4-5 hours)
- Complete unit test coverage
- Edge case testing
- Container workflow tests
- Performance benchmarking

### Phase 5: Documentation & Polish (2-3 hours)
- README updates
- Error message improvements
- Code review and cleanup
- Final validation

**Total Estimate:** 14-19 hours

## Success Criteria

- [ ] Releases entity auto-discovered by EntityRegistry
- [ ] Save operation captures all release metadata
- [ ] Asset download/upload works for files up to 2 GiB
- [ ] Environment variables control release/asset inclusion
- [ ] Restore creates releases in target repository
- [ ] All tests pass (unit, integration, container)
- [ ] Documentation complete and accurate
- [ ] Performance acceptable for typical repositories

## Open Questions

None - design approved and ready for implementation.

## References

- [GitHub Releases API Documentation](https://docs.github.com/en/rest/releases/releases)
- [Milestone Entity Implementation](../completed/2025-Q4/milestone-phase3-afternoon-session-results/2025-10-18-04-04-milestone-phase3-afternoon-session-results.md)
- [Entity Registry System](../completed/2025-Q4/entity-registry-system/)
- [Immutable Releases Feature](https://github.blog/changelog/2025-10-28-immutable-releases-are-now-generally-available/)
