# Monorepo Conversion Design

**Date:** 2025-11-23
**Status:** Design Approved
**Author:** Claude Code (via brainstorming session)

## Executive Summary

This document outlines the design for converting the current `github-data` project into a monorepo containing four independent subprojects with a shared core library. The conversion will enable better separation of concerns, improved testability, and reusability of Git operations across different platforms (GitHub, GitLab, Bitbucket, etc.).

## Motivation

### Current Pain Points
1. **Git and GitHub coupling**: Git repository operations are tightly coupled with GitHub-specific operations, preventing reuse with other platforms
2. **Interface clarity**: Git service is accumulating options that clutter the user interface
3. **Testing clarity**: Unclear mocking boundaries make tests less focused
4. **Orchestration flexibility**: Users cannot compose custom workflows from smaller, focused tools

### Goals
1. **Separation of concerns**: Separate Git operations (version control) from GitHub operations (platform features)
2. **Reusability**: Enable Git component to work with GitLab, Bitbucket, and other platforms
3. **Testing clarity**: Establish clear boundaries for mocking (mock sibling components and third-party services)
4. **Composition**: Allow users to compose freeze/restore scripts from focused primitives
5. **Infrastructure consistency**: Single set of CI/CD, linting, formatting, testing tools across all subprojects

### Why Monorepo?
1. **Learning opportunity**: Explore monorepo approach for managing related projects
2. **Reduce duplicate infrastructure**: One set of CI/CD, linting, formatting, etc.
3. **Prevent drift**: Infrastructure stays consistent across subprojects
4. **Atomic changes**: Update core + all subprojects in one commit when needed

## Architecture

### Subprojects

#### 1. Core Library (`github-data-core`)
**Purpose:** Shared infrastructure and framework code

**Responsibilities:**
- CLI and environment variable parsing
- Orchestrator-strategy framework
- JSON storage service
- GitHub REST client base (requests wrapper, rate limiting, retry logic, auth)
- Entity framework (base classes, registry, discovery mechanism)
- Base classes and utilities

**Dependencies:**
- Python standard library only
- Third-party: requests, etc. (no Git CLI, no GitHub-specific logic)

**Package name:** `github-data-core`
**Version:** Independent SemVer (starts at 1.0.0)

#### 2. Git Repo Tools (`git-repo-tools`)
**Purpose:** Save and restore Git repositories

**Responsibilities:**
- Git repository save operations
- Git repository restore operations
- Git CLI interaction layer

**Dependencies:**
- `github-data-core >= 1.0.0`
- External: Git CLI

**Package name:** `git-repo-tools`
**Version:** Independent SemVer with core dependency metadata (e.g., `1.0.0+core1.0`)

#### 3. GitHub Repo Manager (`github-repo-manager`)
**Purpose:** GitHub repository lifecycle management

**Responsibilities:**
- Create GitHub repositories
- Check if GitHub repository exists
- Delete GitHub repositories (to be implemented post-migration)
- Narrow REST API boundary (only repository endpoints)

**Dependencies:**
- `github-data-core >= 1.0.0`
- External: GitHub REST API

**Package name:** `github-repo-manager`
**Version:** Independent SemVer with core dependency metadata (e.g., `1.0.0+core1.0`)

#### 4. GitHub Data Tools (`github-data-tools`)
**Purpose:** Save and restore GitHub repository data

**Responsibilities:**
- Save GitHub data (issues, PRs, labels, milestones, releases, comments, etc.)
- Restore GitHub data
- Full GitHub API boundary (REST + GraphQL)
- Concrete entity definitions (Issue, PullRequest, Label, Milestone, Release, etc.)

**Dependencies:**
- `github-data-core >= 1.0.0`
- External: GitHub REST API, GitHub GraphQL API

**Package name:** `github-data-tools`
**Version:** Independent SemVer with core dependency metadata (e.g., `1.0.0+core1.0`)

#### 5. Kit Orchestrator (`kit-orchestrator`)
**Purpose:** Convenience container with backward-compatible interface

**Responsibilities:**
- Bundles all subproject operations
- Provides monolithic interface matching current behavior
- High-level freeze/restore workflows

**Dependencies:**
- `github-data-core >= 1.0.0`
- `git-repo-tools >= 1.0.0`
- `github-repo-manager >= 1.0.0`
- `github-data-tools >= 1.0.0`

**Package name:** `kit-orchestrator`
**Version:** Independent SemVer (e.g., `1.0.0`)

### Dependency Graph

```
github-data-core (pure Python infrastructure)
  │
  ├──> git-repo-tools (+ Git CLI)
  │
  ├──> github-repo-manager (+ GitHub API - narrow)
  │
  ├──> github-data-tools (+ GitHub API - full, + entity definitions)
  │
  └──> kit-orchestrator (bundles all above)
```

**Key principle:** No cross-subproject dependencies (except orchestrator depends on all)

### Entity Architecture Split

**Entity Framework (in core):**
```
core/src/github_data_core/entities/
├── base.py          # BaseEntity class
├── registry.py      # Entity discovery mechanism
└── framework.py     # Entity framework utilities
```

**Entity Definitions (in github-data-tools):**
```
github-data-tools/src/github_data_tools/entities/
├── issue.py         # Issue entity (extends BaseEntity)
├── pull_request.py  # PullRequest entity
├── label.py         # Label entity
├── milestone.py     # Milestone entity
├── release.py       # Release entity
└── comment.py       # Comment entity
```

**Rationale:**
- Core provides the **framework** (base classes, patterns, registry)
- Subprojects provide **concrete implementations** (specific entities)
- Other subprojects can define their own entities if needed (e.g., Repository entity)

### GitHub API Layering

**In core (`github-data-core`):**
- Base REST client (requests wrapper)
- Rate limiting logic
- Retry/backoff logic
- Token/authentication management

**In github-repo-manager:**
- Narrow REST API boundary (only repository CRUD endpoints)
- Repository-specific service layer

**In github-data-tools:**
- Full REST API boundary (all GitHub endpoints)
- GraphQL API boundary
- Full service layer for save/restore operations

## Directory Structure

```
github-data/
├── packages/
│   ├── core/
│   │   ├── src/github_data_core/
│   │   │   ├── github/          # Base REST client, rate limiting, retry, auth
│   │   │   ├── entities/        # Entity framework (base, registry)
│   │   │   ├── storage/         # JSON storage
│   │   │   ├── parameters/      # CLI/env var parsing
│   │   │   └── orchestration/   # Strategy framework
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   ├── integration/
│   │   │   └── fixtures/        # Entity test fixtures
│   │   ├── docs/                # Core-specific docs
│   │   └── pyproject.toml
│   │
│   ├── git-repo-tools/
│   │   ├── src/git_repo_tools/
│   │   │   ├── git/             # From github_data/git
│   │   │   └── operations/      # save, restore
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   ├── integration/
│   │   │   └── container/
│   │   ├── docs/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   │
│   ├── github-repo-manager/
│   │   ├── src/github_repo_manager/
│   │   │   ├── github/
│   │   │   │   ├── repo_service.py
│   │   │   │   └── repo_boundary.py  # Narrow REST API
│   │   │   └── operations/
│   │   │       ├── create.py    # Extracted from current code
│   │   │       ├── check.py     # New
│   │   │       └── delete.py    # To be implemented post-migration
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   ├── integration/
│   │   │   └── container/
│   │   ├── docs/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   │
│   ├── github-data-tools/
│   │   ├── src/github_data_tools/
│   │   │   ├── github/
│   │   │   │   ├── service.py       # Most of current github service
│   │   │   │   ├── boundary.py      # Full REST + GraphQL
│   │   │   │   └── protocol.py
│   │   │   ├── entities/            # Concrete entity definitions
│   │   │   │   ├── issue.py
│   │   │   │   ├── pull_request.py
│   │   │   │   ├── label.py
│   │   │   │   ├── milestone.py
│   │   │   │   └── release.py
│   │   │   └── operations/
│   │   │       ├── save.py
│   │   │       └── restore.py
│   │   ├── tests/
│   │   │   ├── unit/             # Most current unit tests
│   │   │   ├── integration/      # Most current integration tests
│   │   │   └── container/        # Most current container tests
│   │   ├── docs/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   │
│   └── kit-orchestrator/
│       ├── src/kit_orchestrator/
│       │   └── orchestrator.py   # Bundles all operations
│       ├── tests/
│       │   └── container/        # End-to-end tests
│       ├── docs/
│       ├── Dockerfile            # Multi-stage with all tools
│       └── pyproject.toml
│
├── docker/
│   ├── base.Dockerfile           # Shared base image
│   └── git-base.Dockerfile       # Git-specific base (extends base)
│
├── .github/
│   └── workflows/
│       ├── core.yml              # Core CI
│       ├── git-repo-tools.yml
│       ├── github-repo-manager.yml
│       ├── github-data-tools.yml
│       ├── kit-orchestrator.yml
│       └── all.yml               # Runs all tests (for main branch)
│
├── docs/                         # Shared/root docs
│   ├── architecture.md
│   ├── monorepo.md
│   └── development/
│       └── adding-entities.md    # Updated for new structure
│
├── tests/                        # Shared test utilities (if needed)
│   └── shared/
│       └── # Cross-cutting test fixtures
│
├── scripts/
│   └── test-changed.sh           # Detect and test changed packages
│
├── Makefile                      # Root-level commands
├── pyproject.toml                # Workspace definition
├── pdm.lock                      # Single lock file
├── CLAUDE.md
├── CONTRIBUTING.md
└── README.md
```

## Dependency Management (PDM Workspace)

### Root `pyproject.toml`
```toml
[tool.pdm]
distribution = false

[tool.pdm.workspace]
members = [
    "packages/core",
    "packages/git-repo-tools",
    "packages/github-repo-manager",
    "packages/github-data-tools",
    "packages/kit-orchestrator"
]

[tool.pdm.dev-dependencies]
dev = [
    "pytest>=8.0.0",
    "black>=24.0.0",
    "flake8>=7.0.0",
    "mypy>=1.8.0",
]
```

### Subproject `pyproject.toml` Examples

**Core:**
```toml
[project]
name = "github-data-core"
version = "1.0.0"
dependencies = [
    "requests>=2.31.0",
    # Other core dependencies
]

[tool.pdm]
distribution = true
```

**Git Repo Tools:**
```toml
[project]
name = "git-repo-tools"
version = "1.0.0+core1.0"  # Hybrid versioning
dependencies = [
    "github-data-core>=1.0.0,<2.0.0",
]

[tool.pdm]
distribution = true
```

**GitHub Data Tools:**
```toml
[project]
name = "github-data-tools"
version = "1.0.0+core1.0"
dependencies = [
    "github-data-core>=1.0.0,<2.0.0",
]

[tool.pdm]
distribution = true
```

**Kit Orchestrator:**
```toml
[project]
name = "kit-orchestrator"
version = "1.0.0"
dependencies = [
    "github-data-core>=1.0.0,<2.0.0",
    "git-repo-tools>=1.0.0,<2.0.0",
    "github-repo-manager>=1.0.0,<2.0.0",
    "github-data-tools>=1.0.0,<2.0.0",
]

[tool.pdm]
distribution = true
```

### Versioning Strategy (Hybrid Approach)

**Independent versions with core dependency metadata:**
- Core: `1.2.0`
- Git repo tools: `1.1.0+core1.2` (encodes core dependency)
- GitHub data tools: `2.0.0+core1.2`

**When core has breaking changes:**
1. Core bumps to `2.0.0`
2. Each subproject updates at its own pace
3. Subprojects can stay on core `1.x` until ready to upgrade
4. Version metadata shows core compatibility: `1.1.0+core2.0`

## Testing Strategy

### Test Organization

**Unit tests:** Stay with their respective packages
- `packages/core/tests/unit/` - Core functionality tests
- `packages/git-repo-tools/tests/unit/` - Git operations tests
- `packages/github-data-tools/tests/unit/` - GitHub data operations tests

**Integration tests:** Stay with primary functionality being tested
- `packages/git-repo-tools/tests/integration/` - Git integration tests
- `packages/github-data-tools/tests/integration/` - GitHub integration tests

**Container tests:** Stay with the package that produces the container
- `packages/git-repo-tools/tests/container/` - Git container tests
- `packages/github-data-tools/tests/container/` - GitHub data container tests
- `packages/kit-orchestrator/tests/container/` - End-to-end orchestration tests

**Shared fixtures:**
- Entity fixtures move to `packages/core/tests/fixtures/` (they test the entity framework)

### Test Execution Strategies

**Local Development:**
```bash
make test-fast              # All tests except container tests
make test-unit             # Unit tests only (fastest)
make test-core             # Core tests only
make test-git              # Git repo tools tests only
make test-github-data      # GitHub data tools tests only
make test-changed          # Only test packages with changes on current branch
make test-fast-changed     # Fast tests for changed packages only
```

**CI/CD:**
```bash
make test-all              # All tests including container tests (safe, comprehensive)
```

**Selective Testing (make test-changed):**
- Detects changed files on current branch vs main
- If core changed → test everything (all subprojects depend on core)
- If subproject changed → test only that subproject
- Script: `scripts/test-changed.sh`

### Mocking Boundaries

**Clear mocking strategy:**
- Mock sibling subprojects at their public interface
- Mock third-party services (GitHub API, Git CLI)
- Do NOT mock core library (it's infrastructure, not a boundary)

**Example for github-data-tools tests:**
- Mock GitHub API responses
- Mock Git CLI (if needed, though git-repo-tools handles Git)
- Do NOT mock core storage or parameter parsing

## Docker Strategy

### Shared Base Image

**`docker/base.Dockerfile`:**
```dockerfile
FROM python:3.11-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install PDM
RUN pip install --no-cache-dir pdm

# Set working directory
WORKDIR /app

# Copy core package and install
COPY packages/core /tmp/core
RUN pip install /tmp/core && rm -rf /tmp/core

# This is the base image that all subprojects extend
```

### Subproject Dockerfiles

**`packages/git-repo-tools/Dockerfile`:**
```dockerfile
FROM github-data-base:latest

# Copy and install git-repo-tools
COPY packages/git-repo-tools /app
RUN pip install /app

# Set entrypoint
ENTRYPOINT ["python", "-m", "git_repo_tools"]
```

**`packages/github-data-tools/Dockerfile`:**
```dockerfile
FROM github-data-base:latest

# Copy and install github-data-tools
COPY packages/github-data-tools /app
RUN pip install /app

# Set entrypoint
ENTRYPOINT ["python", "-m", "github_data_tools"]
```

### Kit Orchestrator (Convenience Container)

**`packages/kit-orchestrator/Dockerfile`:**
```dockerfile
FROM github-data-base:latest

# Install all subproject packages
COPY packages/git-repo-tools /tmp/git-repo-tools
COPY packages/github-repo-manager /tmp/github-repo-manager
COPY packages/github-data-tools /tmp/github-data-tools
COPY packages/kit-orchestrator /tmp/kit-orchestrator

RUN pip install /tmp/git-repo-tools && \
    pip install /tmp/github-repo-manager && \
    pip install /tmp/github-data-tools && \
    pip install /tmp/kit-orchestrator && \
    rm -rf /tmp/*

# Set entrypoint to orchestrator
ENTRYPOINT ["python", "-m", "kit_orchestrator"]
```

### Multi-stage builds
All Dockerfiles use multi-stage builds to keep final images small.

## User Experience

### Before (Current Monolithic Container)

```bash
docker run github-data:latest \
  -e OPERATION=restore \
  -e GITHUB_TOKEN=xxx \
  -e GITHUB_REPO=owner/repo \
  -v $(pwd)/data:/data
```

### After (Composed Containers)

**Using individual containers:**
```bash
# Step 1: Ensure repo exists
docker run github-repo-manager:1.0.0 \
  -e OPERATION=check \
  -e GITHUB_TOKEN=xxx \
  -e GITHUB_REPO=owner/repo \
  -e CREATE_IF_MISSING=true \
  -v $(pwd)/data:/data

# Step 2: Restore git repo
docker run git-repo-tools:1.0.0 \
  -e OPERATION=restore \
  -e GITHUB_TOKEN=xxx \
  -e GITHUB_REPO=owner/repo \
  -v $(pwd)/data:/data

# Step 3: Restore GitHub data
docker run github-data-tools:1.0.0 \
  -e OPERATION=restore \
  -e GITHUB_TOKEN=xxx \
  -e GITHUB_REPO=owner/repo \
  -v $(pwd)/data:/data
```

**Using kit-orchestrator (convenience, backward-compatible):**
```bash
docker run kit-orchestrator:1.0.0 \
  -e OPERATION=restore \
  -e GITHUB_TOKEN=xxx \
  -e GITHUB_REPO=owner/repo \
  -v $(pwd)/data:/data
```

### KitScript Integration

Users write KitScript scripts to orchestrate containers:

```bash
#!/usr/bin/env kitscript

# Freeze a repository
github-repo-manager check --repo=owner/name
git-repo-tools save --repo=/path --output=/data/git.json
github-data-tools save --repo=owner/name --output=/data/github.json

# Restore to new repository
github-repo-manager create --repo=owner/new-name --create-if-missing=true
git-repo-tools restore --input=/data/git.json --repo=owner/new-name
github-data-tools restore --input=/data/github.json --repo=owner/new-name
```

## Migration Plan

### Overview
**Strategy:** Big Bang migration (clean break, no backward compatibility during transition)
**Rationale:** Early development, no production instances, cleaner result

### Phase 1: Preparation (Analysis & Planning)
**Status:** Complete (this document)

**Tasks:**
1. ✅ Architecture finalized
2. Create detailed module mapping document
3. Create branch: `feat/monorepo-conversion`

### Phase 2: Create Monorepo Structure

**Tasks:**
1. Create directory skeleton (all packages/ subdirs)
2. Set up root `pyproject.toml` with workspace config
3. Create individual `pyproject.toml` for each package
4. Create base Dockerfiles in `docker/`
5. Create root `Makefile` with all commands
6. Create `scripts/test-changed.sh`

### Phase 3: Extract Core

**Move to `packages/core/`:**
- `github_data/parameters/` → `packages/core/src/github_data_core/parameters/`
- `github_data/orchestration/` → `packages/core/src/github_data_core/orchestration/`
- `github_data/storage/` → `packages/core/src/github_data_core/storage/`
- `github_data/entities/base.py` → `packages/core/src/github_data_core/entities/base.py`
- `github_data/entities/registry.py` → `packages/core/src/github_data_core/entities/registry.py`
- `github_data/github/client.py` → `packages/core/src/github_data_core/github/client.py`
- Rate limiting, retry logic → `packages/core/src/github_data_core/github/`

**Update imports in moved files** (internal imports only, not cross-package yet)

**Move tests:**
- `tests/fixtures/` → `packages/core/tests/fixtures/`
- Tests for core modules → `packages/core/tests/unit/`

### Phase 4: Extract Git Repo Tools

**Move to `packages/git-repo-tools/`:**
- `github_data/git/` → `packages/git-repo-tools/src/git_repo_tools/git/`
- Extract git-related params from `main.py` → `packages/git-repo-tools/src/git_repo_tools/operations/`

**Update imports:**
- Internal: `from git_repo_tools.git import ...`
- Core: `from github_data_core.parameters import ...`

**Move tests:**
- `tests/unit/git/` → `packages/git-repo-tools/tests/unit/`
- Relevant integration tests → `packages/git-repo-tools/tests/integration/`
- Relevant container tests → `packages/git-repo-tools/tests/container/`

### Phase 5: Extract GitHub Repo Manager

**Create new package** (mostly new code):
- Extract `create_repository` from `github_data/github/service.py`
- Create `packages/github-repo-manager/src/github_repo_manager/operations/create.py`
- Create `packages/github-repo-manager/src/github_repo_manager/operations/check.py`
- Create narrow REST boundary for repo endpoints in `packages/github-repo-manager/src/github_repo_manager/github/repo_boundary.py`

**Move/create tests:**
- Extract any existing repo creation tests
- Create new tests for check operation
- Create container tests for repo lifecycle

### Phase 6: Extract GitHub Data Tools

**Move to `packages/github-data-tools/`:**
- Most of `github_data/github/` → `packages/github-data-tools/src/github_data_tools/github/`
- `github_data/entities/*.py` (concrete entities) → `packages/github-data-tools/src/github_data_tools/entities/`
- Extract from `main.py` → `packages/github-data-tools/src/github_data_tools/operations/`

**Update imports:**
- Internal: `from github_data_tools.github import ...`
- Core: `from github_data_core.entities import BaseEntity, Registry`
- Entities: `from github_data_tools.entities import Issue, PullRequest, ...`

**Move tests:**
- Most of `tests/unit/github/` → `packages/github-data-tools/tests/unit/`
- Most of `tests/unit/entities/` → `packages/github-data-tools/tests/unit/entities/`
- Most of `tests/integration/` → `packages/github-data-tools/tests/integration/`
- Most of `tests/container/` → `packages/github-data-tools/tests/container/`

### Phase 7: Create Kit Orchestrator

**Create new package:**
- Wrapper that invokes all subproject operations
- Maintains backward-compatible interface with current monolithic container

**Create convenience CLI:**
- `kit-orchestrator save` → calls git + github save operations
- `kit-orchestrator restore` → calls ensure-repo + git restore + github restore

**Create end-to-end container tests:**
- Full freeze/restore workflow tests
- Backward compatibility tests

### Phase 8: Update Infrastructure

**Tasks:**
1. Update GitHub Actions workflows (one per package + all.yml)
2. Update root Makefile with all commands
3. Ensure `scripts/test-changed.sh` is functional
4. Update documentation:
   - Root README.md (explains monorepo structure)
   - Each package gets its own README.md
   - Update CLAUDE.md with new structure
   - Create docs/architecture.md with dependency graph
   - Create docs/monorepo.md with monorepo guidelines
   - Update docs/development/adding-entities.md for new structure

### Phase 9: Validation

**Tasks:**
1. Run full test suite: `make check-all`
2. Build all Docker images: `make docker-build-all`
3. Run end-to-end container tests
4. Test backward compatibility (kit-orchestrator behaves like old monolith)
5. Test selective testing: `make test-changed`
6. Verify all CI/CD workflows

### Phase 10: Cleanup

**Tasks:**
1. Add all new files to git
2. Create commit for monorepo conversion
3. Delete old monolithic code (github_data/ directory if it still exists)
4. Run all tests to verify cleanup didn't break anything
5. Update any external documentation or references

### Phase 11: Release

**Tasks:**
1. Tag release: `v2.0.0` (major version bump for breaking structure change)
2. Update CHANGELOG with monorepo conversion details
3. Create GitHub release with migration notes

## Module Mapping (Detailed)

### Current → Core

| Current Location | New Location | Notes |
|-----------------|--------------|-------|
| `github_data/parameters/` | `packages/core/src/github_data_core/parameters/` | All parameter parsing |
| `github_data/orchestration/` | `packages/core/src/github_data_core/orchestration/` | Strategy framework |
| `github_data/storage/` | `packages/core/src/github_data_core/storage/` | JSON storage |
| `github_data/entities/base.py` | `packages/core/src/github_data_core/entities/base.py` | Entity base class |
| `github_data/entities/registry.py` | `packages/core/src/github_data_core/entities/registry.py` | Entity discovery |
| `github_data/github/client.py` (base parts) | `packages/core/src/github_data_core/github/client.py` | Base REST client |
| Rate limiting logic | `packages/core/src/github_data_core/github/rate_limiter.py` | New file |
| Retry logic | `packages/core/src/github_data_core/github/retry.py` | New file |
| Auth logic | `packages/core/src/github_data_core/github/auth.py` | New file |
| `tests/fixtures/` | `packages/core/tests/fixtures/` | Entity test fixtures |

### Current → Git Repo Tools

| Current Location | New Location | Notes |
|-----------------|--------------|-------|
| `github_data/git/` | `packages/git-repo-tools/src/git_repo_tools/git/` | All Git operations |
| Git params in `main.py` | `packages/git-repo-tools/src/git_repo_tools/operations/` | Extract and reorganize |
| `tests/unit/git/` | `packages/git-repo-tools/tests/unit/` | Git unit tests |

### Current → GitHub Repo Manager

| Current Location | New Location | Notes |
|-----------------|--------------|-------|
| `create_repository()` in service | `packages/github-repo-manager/src/github_repo_manager/operations/create.py` | Extract method |
| New | `packages/github-repo-manager/src/github_repo_manager/operations/check.py` | New functionality |
| New | `packages/github-repo-manager/src/github_repo_manager/github/repo_boundary.py` | Narrow API boundary |

### Current → GitHub Data Tools

| Current Location | New Location | Notes |
|-----------------|--------------|-------|
| Most of `github_data/github/` | `packages/github-data-tools/src/github_data_tools/github/` | Except repo creation |
| `github_data/entities/*.py` (concrete) | `packages/github-data-tools/src/github_data_tools/entities/` | Issue, PR, Label, etc. |
| GitHub data params in `main.py` | `packages/github-data-tools/src/github_data_tools/operations/` | Extract and reorganize |
| Most of `tests/unit/github/` | `packages/github-data-tools/tests/unit/` | GitHub unit tests |
| Most of `tests/unit/entities/` | `packages/github-data-tools/tests/unit/entities/` | Entity tests |
| Most of `tests/integration/` | `packages/github-data-tools/tests/integration/` | Integration tests |
| Most of `tests/container/` | `packages/github-data-tools/tests/container/` | Container tests |

### Current → Kit Orchestrator

| Current Location | New Location | Notes |
|-----------------|--------------|-------|
| Orchestration logic in `main.py` | `packages/kit-orchestrator/src/kit_orchestrator/orchestrator.py` | High-level workflows |
| New | `packages/kit-orchestrator/tests/container/` | End-to-end tests |

## Makefile Commands

### Installation
```bash
make install-dev              # Install all packages in workspace with dev dependencies
```

### Testing
```bash
make test-all                 # All tests including container tests
make test-fast                # All tests except container tests (recommended for dev)
make test-unit                # Unit tests only (fastest)
make test-integration         # Integration tests excluding container tests
make test-container           # Container integration tests only

# Per-package testing
make test-core                # Core tests only
make test-git                 # Git repo tools tests only
make test-github-manager      # GitHub repo manager tests only
make test-github-data         # GitHub data tools tests only
make test-orchestrator        # Kit orchestrator tests only

# Selective testing (smart)
make test-changed             # Test only packages with changes on current branch
make test-fast-changed        # Fast tests for changed packages only

# Coverage
make test-with-test-coverage       # Coverage analysis of test files
make test-fast-with-test-coverage  # Fast tests with test file coverage
```

### Quality Checks
```bash
make lint                     # Run flake8 linting
make format                   # Format code with black
make type-check               # Run mypy type checking
make check                    # All quality checks excluding container tests (fast)
make check-all                # Complete quality validation including container tests
```

### Docker
```bash
make docker-build-all         # Build all containers (base + all subprojects)
make docker-build-base        # Build base image only
make docker-build-git         # Build git-repo-tools container
make docker-build-github-manager  # Build github-repo-manager container
make docker-build-github-data     # Build github-data-tools container
make docker-build-orchestrator    # Build kit-orchestrator container
```

## CI/CD Strategy

### Per-Package Workflows

Each package has its own GitHub Actions workflow:
- `core.yml` - Runs core tests
- `git-repo-tools.yml` - Runs git-repo-tools tests
- `github-repo-manager.yml` - Runs github-repo-manager tests
- `github-data-tools.yml` - Runs github-data-tools tests
- `kit-orchestrator.yml` - Runs kit-orchestrator tests

**Trigger strategy:**
- On PR: Run only workflows for packages with changes
- On push to main: Run all workflows (comprehensive validation)

### Comprehensive Workflow

`all.yml` - Runs complete validation:
1. Install all dependencies
2. Run all tests (including container tests)
3. Run all quality checks
4. Build all Docker images
5. Run end-to-end tests with kit-orchestrator

**Trigger:** On push to main, on release tags

## Benefits

### Separation of Concerns
- Git operations isolated from GitHub operations
- GitHub repo lifecycle separate from data migration
- Clear, focused responsibilities per subproject

### Reusability
- Git component can be reused with GitLab, Bitbucket, etc.
- Core library provides common infrastructure to all

### Testing
- Clear mocking boundaries (mock siblings and third-party services)
- Focused tests per subproject
- Selective testing speeds up development

### Composition
- Users compose freeze/restore scripts from focused primitives
- Fine-grained control over workflows
- Convenience orchestrator for backward compatibility

### Infrastructure
- Single set of CI/CD, linting, formatting tools
- Consistent infrastructure across all subprojects
- Prevents drift over time
- Atomic cross-component changes when needed

## Risks and Mitigations

### Risk: Increased Complexity
**Mitigation:**
- Comprehensive documentation
- Clear module mapping
- Makefile abstracts complexity

### Risk: Breaking Changes During Migration
**Mitigation:**
- Big bang approach (clean break)
- No production instances to worry about
- Comprehensive test suite validates migration

### Risk: Docker Build Times
**Mitigation:**
- Shared base image (build once, reuse)
- Multi-stage builds keep images small
- Layer caching

### Risk: Learning Curve
**Mitigation:**
- This is a learning opportunity (stated goal)
- Comprehensive design document
- Clear directory structure

### Risk: Coordination Between Packages
**Mitigation:**
- Core version constraints in subproject dependencies
- Hybrid versioning shows core compatibility
- Atomic commits when needed (monorepo advantage)

## Success Criteria

1. ✅ All tests pass in new structure
2. ✅ All Docker images build successfully
3. ✅ Kit orchestrator provides backward-compatible interface
4. ✅ Users can compose workflows from individual containers
5. ✅ Git component is decoupled from GitHub (can be reused with other platforms)
6. ✅ Clear mocking boundaries in tests
7. ✅ Single set of infrastructure tools (CI/CD, linting, etc.)
8. ✅ Selective testing works (test only changed packages)

## Future Enhancements

### Post-Migration
1. Implement `github-repo-manager delete` operation
2. Add more GitHub repo manager operations (update settings, etc.)
3. Enhanced CLI options for selective data save/restore
4. Configuration management for multiple repositories

### GitLab/Bitbucket Support
1. Create `gitlab-data-tools` subproject (reuses `git-repo-tools` and `core`)
2. Create `bitbucket-data-tools` subproject (reuses `git-repo-tools` and `core`)
3. Platform-agnostic orchestrator

### Advanced Testing
1. Performance benchmarking per subproject
2. Load testing for rate limiting
3. Chaos engineering for error resilience

## References

- PDM Workspace Documentation: https://pdm.fming.dev/latest/usage/workspace/
- Conventional Commits: https://www.conventionalcommits.org/
- Clean Code (Robert C. Martin)
- KitScript: https://gitlab.com/hfossedu/kits/kitscript

## Appendix: Current Codebase Overview

**Primary functionality:** GitHub data save/restore (issues, PRs, labels, milestones, releases, comments)

**Recent additions:**
- Repository creation capability (straddles main.py and github service)
- Release save/restore with asset metadata

**Test organization:**
- `tests/unit/` - Unit tests for all modules
- `tests/integration/` - Integration tests (primarily GitHub data operations)
- `tests/container/` - Container integration tests
- `tests/fixtures/` - Entity test fixtures

**Key modules:**
- `github_data/main.py` - Entry point, parameter processing, orchestration
- `github_data/git/` - Git operations (isolated, ready to extract)
- `github_data/github/` - GitHub operations (service, boundary, protocol)
- `github_data/entities/` - Entity definitions and registry
- `github_data/parameters/` - Parameter parsing
- `github_data/orchestration/` - Strategy framework
- `github_data/storage/` - JSON storage

**Development state:**
- Early development, no production instances
- Active development on feature branches
- Recent work on repository creation and release support

---

**End of Design Document**
