# Product Requirements Document: GitHub Milestones Support

**Document Type:** Product Requirements Document  
**Feature:** GitHub Milestones Save/Restore Support  
**Date:** 2025-10-16  
**Status:** Draft  

## Executive Summary

This PRD defines the requirements for adding GitHub milestone save/restore functionality to the GitHub Data project. This feature will enable users to backup and restore milestone data along with their associated issues and pull requests, maintaining organizational structure and project management workflows.

## Problem Statement

Currently, the GitHub Data project saves and restores labels, issues, comments, sub-issues, and pull requests, but does not support milestones. This creates an incomplete backup that loses critical project organization data used for release planning, sprint management, and goal tracking.

**Impact:** Teams using milestone-driven development workflows cannot fully restore their repository's organizational structure, resulting in:
- Lost release planning data
- Broken project phase organization  
- Missing progress tracking information
- Incomplete repository state restoration

## Objectives

### Primary Goals
1. **Complete Repository State**: Enable full backup/restore of milestone-based project organization
2. **Relationship Preservation**: Maintain issue/PR ↔ milestone associations during save/restore operations
3. **Backward Compatibility**: Ensure existing workflows continue unchanged when milestones are disabled
4. **User Control**: Provide granular control over milestone operations via configuration

### Success Metrics
- All repository milestones can be saved and restored accurately
- Issue/PR milestone relationships are preserved across save/restore cycles
- Zero impact on existing functionality when milestone support is disabled
- Implementation follows existing architectural patterns

## User Stories

### As a Development Team Lead
- **I want to** backup milestone data with my repository issues and PRs
- **So that** I can restore complete project organization structure
- **Acceptance Criteria:**
  - All milestones are saved with complete metadata
  - Issue/PR milestone associations are preserved
  - Restoration recreates identical milestone structure

### As a Release Manager  
- **I want to** restore milestone data for release planning
- **So that** I can continue managing releases after repository migration
- **Acceptance Criteria:**
  - Milestones restore with correct due dates and progress tracking
  - Associated issues/PRs maintain milestone relationships
  - Milestone state (open/closed) is preserved

### As a System Administrator
- **I want to** control milestone operations independently
- **So that** I can optimize backup/restore performance based on organizational needs
- **Acceptance Criteria:**
  - `INCLUDE_MILESTONES` environment variable controls milestone operations
  - Default behavior includes milestones (`INCLUDE_MILESTONES=true`)
  - When disabled, system operates exactly as before

## Functional Requirements

### FR1: Milestone Data Model
**Requirement:** Create comprehensive milestone entity model  
**Priority:** High  
**Details:**
- Support all GitHub milestone fields (id, number, title, description, state, etc.)
- Include creator information and timestamps
- Handle optional fields (description, due_on, closed_at)
- Support both open and closed milestone states

### FR2: Milestone Save Operations
**Requirement:** Save all repository milestones to JSON storage  
**Priority:** High  
**Details:**
- Retrieve milestones via GitHub REST API
- Convert milestone data to standardized format
- Store milestones in JSON files following existing patterns
- Include pagination support for repositories with many milestones

### FR3: Milestone Restore Operations  
**Requirement:** Restore milestones with dependency ordering
**Priority:** High  
**Details:**
- Restore milestones before issues/PRs to maintain referential integrity
- Dependency chain: Milestones have no dependencies `[]`, Issues depend on `["labels", "milestones"]`, Pull Requests depend on `["labels", "milestones"]`
- Handle milestone creation conflicts (title uniqueness)
- Restore milestone metadata including due dates and descriptions
- Support both open and closed milestone restoration

### FR4: Issue/PR Milestone Relationships
**Requirement:** Preserve milestone associations in issues and pull requests
**Priority:** High  
**Details:**
- Update issue model to include milestone field
- Update pull request model to include milestone field  
- Populate milestone data during issue/PR save operations
- Restore milestone associations during issue/PR restoration

### FR5: Configuration Control
**Requirement:** Provide user control over milestone operations
**Priority:** High  
**Details:**
- Add `INCLUDE_MILESTONES` boolean environment variable
- Default value: `true` (milestones included by default)
- When `false`: system operates as before (no milestone operations)
- When `true`: milestones are included in save/restore workflows

### FR6: GraphQL Integration
**Requirement:** Support milestone data in GraphQL queries
**Priority:** Medium  
**Details:**
- Add milestone fields to repository GraphQL queries
- Include milestone data in issue/PR GraphQL responses
- Update GraphQL converters to handle milestone data

## Non-Functional Requirements

### NFR1: Performance
- Milestone operations must not significantly impact existing save/restore performance
- Milestone API calls should respect existing rate limiting infrastructure
- Bulk operations should use pagination to handle large milestone datasets

### NFR2: Reliability  
- Milestone restoration must maintain referential integrity
- Failed milestone operations should not break issue/PR restoration
- Error handling should follow existing patterns

### NFR3: Compatibility
- Zero impact on existing functionality when `INCLUDE_MILESTONES=false`
- Backward compatibility with existing saved data (no milestone data)
- Forward compatibility for future milestone feature enhancements

### NFR4: Maintainability
- Implementation must follow existing architectural patterns
- Code should integrate with existing service/boundary/storage layers
- Tests must follow established testing conventions and markers

## Technical Requirements

### TR1: Data Model Implementation
```python
# New entity: src/entities/milestones/models.py
class Milestone(BaseModel):
    id: Union[int, str]
    number: int
    title: str
    description: Optional[str] = None
    state: str  # "open" | "closed"
    creator: GitHubUser
    created_at: datetime
    updated_at: datetime
    due_on: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    open_issues: int = 0
    closed_issues: int = 0
    html_url: str
```

### TR2: Entity Model Updates
```python
# Update existing models
class Issue(BaseModel):
    # ... existing fields
    milestone: Optional[Milestone] = None

class PullRequest(BaseModel):
    # ... existing fields  
    milestone: Optional[Milestone] = None
```

### TR3: Environment Variable Configuration
- Variable: `INCLUDE_MILESTONES`
- Type: Boolean
- Default: `true`
- Accepted values: `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off` (case-insensitive)
- Configuration Location: Add to `ApplicationConfig` class in `src/config/settings.py`:
  ```python
  include_milestones: bool = _parse_enhanced_bool_env("INCLUDE_MILESTONES", default=True)
  ```

### TR4: API Integration
- REST API: Use existing GitHub service patterns for milestone endpoints
- GraphQL: Extend existing queries to include milestone data
  - New file: `src/github/queries/milestones.py` (following pattern in `labels.py`)
  - Add milestone conversion functions in `src/github/graphql_converters.py`
- Rate Limiting: Integrate with existing rate limiting infrastructure
- Caching: Leverage existing cache mechanisms for milestone data

### TR5: Storage Integration
- File Structure: Follow existing JSON storage patterns
- Location: Store milestones in `milestones/` directory within data path
- Format: JSON files with standardized naming convention (`milestones.json`)
- Strategy Classes:
  - `src/operations/save/strategies/milestones_strategy.py` - `MilestonesSaveStrategy`
  - `src/operations/restore/strategies/milestones_strategy.py` - `MilestonesRestoreStrategy`
- Dependency Ordering: Restore milestones before issues/PRs

## User Interface Requirements

### UIR1: Environment Variable Control
**Current Behavior Maintained:**
```bash
# Existing variables continue to work unchanged
INCLUDE_ISSUES=true
INCLUDE_ISSUE_COMMENTS=true  
INCLUDE_PULL_REQUESTS=true
INCLUDE_PULL_REQUEST_COMMENTS=true
INCLUDE_SUB_ISSUES=true
```

**New Variable Added:**
```bash
# New milestone control (default: true)
INCLUDE_MILESTONES=true
```

### UIR2: Docker Command Examples
**Save with milestones (default behavior):**
```bash
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=your_token_here \
  -e GITHUB_REPO=owner/repo \
  -e DATA_PATH=/data \
  -v $(pwd)/save:/data \
  github-data:latest
```

**Save without milestones:**
```bash
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=your_token_here \
  -e GITHUB_REPO=owner/repo \
  -e DATA_PATH=/data \
  -e INCLUDE_MILESTONES=false \
  -v $(pwd)/save:/data \
  github-data:latest
```

**Restore with milestones:**
```bash
docker run --rm \
  -e OPERATION=restore \
  -e GITHUB_TOKEN=your_token_here \
  -e GITHUB_REPO=owner/repo \
  -e DATA_PATH=/data \
  -e INCLUDE_MILESTONES=true \
  -v $(pwd)/save:/data \
  github-data:latest
```

## Implementation Phases

### Phase 1: Core Infrastructure (Priority: High)
**Duration:** 1-2 days  
**Deliverables:**
- Milestone entity model creation
- Milestone service operations (save/restore)
- REST API boundary methods
- Basic milestone storage operations
- Environment variable configuration

**Acceptance Criteria:**
- Milestones can be saved to and restored from JSON storage
- `INCLUDE_MILESTONES` environment variable controls operations
- Basic milestone CRUD operations work via GitHub API

### Phase 2: Relationship Integration (Priority: High)  
**Duration:** 1 day  
**Deliverables:**
- Issue/PR model updates with milestone fields
- GraphQL query enhancements
- Milestone relationship restoration
- Dependency ordering implementation

**Acceptance Criteria:**
- Issues/PRs maintain milestone associations across save/restore
- Milestones restore before dependent entities
- GraphQL queries include milestone data

### Phase 3: Testing and Validation (Priority: High)
**Duration:** 1 day  
**Deliverables:**
- Comprehensive unit tests with appropriate markers
- Integration tests for milestone workflows
- End-to-end save/restore validation
- Error handling and edge case coverage
- Add testing markers to `pytest.ini`:
  ```ini
  milestones: Milestone management functionality tests
  include_milestones: Milestone feature toggle tests (INCLUDE_MILESTONES)
  ```

**Acceptance Criteria:**
- All tests pass with existing quality standards
- Test coverage meets project requirements
- Error scenarios are properly handled
- Tests follow existing marker patterns (`@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.milestones`)

**Total Estimated Effort:** 3-4 days

## Risk Assessment

### High-Impact Risks
1. **Dependency Ordering Complexity**
   - **Risk:** Milestone restoration order affects issue/PR integrity
   - **Mitigation:** Implement explicit dependency ordering in restore workflow
   - **Owner:** Development Team

2. **GraphQL Query Performance**
   - **Risk:** Adding milestone data increases query response size
   - **Mitigation:** Use pagination and selective field queries
   - **Owner:** Development Team

### Medium-Impact Risks  
1. **API Rate Limiting**
   - **Risk:** Additional milestone API calls approach rate limits
   - **Mitigation:** Leverage existing rate limiting and caching infrastructure
   - **Owner:** Development Team

2. **Backward Compatibility**
   - **Risk:** Changes break existing workflows
   - **Mitigation:** Comprehensive testing with `INCLUDE_MILESTONES=false`
   - **Owner:** QA Team

### Low-Impact Risks
1. **Storage Volume Increase**
   - **Risk:** Milestone data increases backup size
   - **Mitigation:** Milestones are typically low-volume data
   - **Owner:** Operations Team

## Dependencies

### Internal Dependencies
- Existing GitHub service layer infrastructure
- Current JSON storage service patterns  
- Established GraphQL query and converter system
- Issue and pull request entity models

### External Dependencies
- GitHub REST API milestone endpoints
- GitHub GraphQL API milestone fields
- Docker container runtime environment
- Python PDM package management system

## Success Criteria

### Functional Success
- [ ] All repository milestones can be saved accurately
- [ ] All repository milestones can be restored accurately  
- [ ] Issue/PR milestone relationships are preserved
- [ ] `INCLUDE_MILESTONES=false` maintains existing behavior
- [ ] `INCLUDE_MILESTONES=true` (default) includes milestone operations

### Technical Success
- [ ] Implementation follows existing architectural patterns
- [ ] All tests pass with appropriate markers and coverage
- [ ] Code quality meets project standards (lint, type-check, format)
- [ ] Performance impact is minimal
- [ ] Error handling is comprehensive

### User Experience Success
- [ ] Environment variable configuration is intuitive
- [ ] Docker command usage remains unchanged for existing workflows
- [ ] Documentation clearly explains milestone functionality
- [ ] Migration path is clear for users wanting milestone support

## Out of Scope

The following items are explicitly **not included** in this release:

1. **Milestone Analytics**: Progress tracking, completion statistics, or milestone reporting
2. **Advanced Filtering**: Selective milestone save/restore based on criteria
3. **Milestone Templates**: Predefined milestone structures or automation
4. **Cross-Repository Milestones**: Support for milestones spanning multiple repositories
5. **Milestone Dependencies**: Support for milestone-to-milestone relationships
6. **Milestone Notifications**: Email or webhook notifications for milestone events
7. **UI/Web Interface**: Graphical interface for milestone management
8. **Milestone Import/Export**: Support for non-GitHub milestone data formats

## Approval and Sign-off

| Role | Name | Approval | Date |
|------|------|----------|------|
| Product Owner | TBD | Pending | TBD |
| Tech Lead | TBD | Pending | TBD |
| QA Lead | TBD | Pending | TBD |

---

*Document Version: 1.0*  
*Last Updated: 2025-10-16*  
*Next Review Date: TBD*