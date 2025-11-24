# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the GitHub Data project - a monorepo containing multiple Python packages for saving and restoring GitHub repository data. It provides tools to save and restore GitHub repository issue management data, hierarchical sub-issue relationships, pull request workflows, and Git repositories.

## Monorepo Architecture

The project uses **PDM workspace** for monorepo management with five independent packages:

### Package Structure

```
packages/
├── core/                    # github-data-core - Core infrastructure
│   ├── config/             # Configuration and parsing utilities
│   ├── entities/           # Base entity framework
│   ├── storage/            # Storage abstractions
│   └── operations/         # Base orchestrator patterns
│
├── git-repo-tools/         # Git repository backup/restore
│   ├── git/                # Git service implementation
│   └── entities/           # Git repository entity
│
├── github-repo-manager/    # Repository lifecycle management
│   ├── github/             # Repository creation API
│   └── operations/         # Create/check operations
│
├── github-data-tools/      # GitHub data operations (largest package)
│   ├── github/             # GitHub API boundary and service
│   ├── entities/           # 11 entity types (issues, PRs, labels, etc.)
│   ├── operations/         # Save/restore orchestrators
│   └── tools/              # Entity generation tools
│
└── kit-orchestrator/       # Convenience orchestrator
    ├── __main__.py         # Backward-compatible CLI
    └── tests/              # End-to-end container tests
```

### Dependency Graph

```
kit-orchestrator
    ├─> github-data-tools
    ├─> github-repo-manager
    ├─> git-repo-tools
    └─> github-data-core

github-data-tools ──> github-data-core
github-repo-manager ──> github-data-core
git-repo-tools ──> github-data-core
```

All packages depend on `core`, and `kit-orchestrator` depends on all others to provide a unified interface.

## Project Status

**Current Status:** Monorepo conversion complete (v2.0.0)

**Completed features:**
- ✅ Monorepo structure with 5 independent packages
- ✅ PDM workspace for dependency management
- ✅ Selective testing (test only changed packages)
- ✅ Per-package Docker builds
- ✅ Comprehensive GitHub API client with GraphQL and REST support
- ✅ Label, milestone, and release save/restore
- ✅ Issue and comment save/restore with selective filtering
- ✅ Sub-issues support with hierarchical relationships
- ✅ Pull request save/restore with reviews and comments
- ✅ Git repository backup/restore
- ✅ Rate limiting and caching for API operations
- ✅ Kit orchestrator with backward compatibility

**Future development:**
- Enhanced CLI options for individual packages
- Configuration management for multiple repositories
- Advanced filtering and selection options
- Package-specific versioning and releases

## Getting Started

This GitHub Data project provides containerized tools for saving and restoring GitHub repository data:

1. Configure your GitHub access credentials and target repositories
2. Use the save tools to save repository labels, issues, comments, sub-issues, and pull requests
3. Use the restore tools to recreate repository state from saved JSON data
4. Customize save/restore operations for specific data requirements
5. Handle hierarchical sub-issue relationships and pull request workflows with branch dependency validation

## Environment Variables

For a complete list of environment variables and their descriptions, see the [Environment Variables section in the README](README.md#environment-variables).

### Environment Variable Examples

**Save repository data excluding issue comments:**
```bash
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=your_token_here \
  -e GITHUB_REPO=owner/repo \
  -e DATA_PATH=/data \
  -e INCLUDE_ISSUE_COMMENTS=false \
  -v $(pwd)/save:/data \
  github-data:latest
```

**Restore repository data with issue comments included (default):**
```bash
docker run --rm \
  -e OPERATION=restore \
  -e GITHUB_TOKEN=your_token_here \
  -e GITHUB_REPO=owner/repo \
  -e DATA_PATH=/data \
  -e INCLUDE_ISSUE_COMMENTS=true \
  -v $(pwd)/save:/data \
  github-data:latest
```

### Boolean Value Formats

Boolean variables (`INCLUDE_GIT_REPO`, `INCLUDE_ISSUES`, `INCLUDE_ISSUE_COMMENTS`, `INCLUDE_PULL_REQUESTS`, `INCLUDE_PULL_REQUEST_COMMENTS`, `INCLUDE_SUB_ISSUES`) accept these formats:
- **True values**: `true`, `1`, `yes`, `on` (case-insensitive)
- **False values**: `false`, `0`, `no`, `off` (case-insensitive)

## Development Environment

This repository uses DevContainer for consistent development environments:

- **Base Environment**: Ubuntu-based container with Docker-in-Docker support
- **Pre-installed Tools**:
  - Node.js LTS
  - Python 3 with pip and venv
  - Git, build tools, and common utilities
  - Claude Code CLI (`@anthropic-ai/claude-code`)
  - Docker CLI and Docker Compose

## GitHub Service Layer

The GitHub service layer uses a **declarative operation registry** that auto-generates
service methods from entity configurations.

**When adding entities:** See [docs/development/adding-entities.md](docs/development/adding-entities.md)
for the complete guide on using the registry-based approach.

## Claude Code Agents

This repository is configured to use Claude Code agents for specialized development tasks. Agents provide autonomous, multi-step task execution for complex operations.

### Available Agents

The following specialized agents are available for this project:

- **general-purpose**: Multi-step research, code search, and complex task execution
- **backup-restore-workflow**: GitHub repository save/restore operations, data migration, and containerized workflows
- **testing-quality**: Testing strategies, code quality, TDD practices, and development tooling
- **github-api-specialist**: GitHub API operations, GraphQL/REST integration, rate limiting, and API client development

### Agent Configuration

Agent configuration is stored in `.claude/` directory:
- Agent settings and preferences
- Task-specific configurations
- Workflow automation rules

### Using Agents

Agents are automatically invoked by Claude Code when working on tasks that match their specialization:
- Complex multi-step implementations
- GitHub API integrations and workflows
- Testing and quality assurance tasks
- Save and restore operations

For manual agent invocation or configuration changes, refer to the Claude Code documentation.

## Package Management

This project uses [PDM](https://pdm.fming.dev/) with **workspace support** for monorepo management:

- **Root workspace**: Defines member packages and shared dev dependencies
- **Package pyproject.toml**: Each package has independent version and dependencies
- **Lock file**: Single `pdm.lock` at repository root ensures consistent versions
- **Workspace members**: All 5 packages listed in root `pyproject.toml`

### Working with Packages

```bash
# Install all packages and dev dependencies
make install-dev

# Work on a specific package
cd packages/github-data-tools
pdm run pytest tests/

# Test imports across packages
cd packages/kit-orchestrator
pdm run python -c "from github_data_core.entities import EntityRegistry; print('OK')"
```

## Development Commands

### All-Packages Commands

- `make install-dev` - Install all packages with dev dependencies
- `make test-all` - All tests including container tests
- `make test-fast` - All tests except container tests (recommended for dev)
- `make lint` - Run flake8 on all packages
- `make format` - Format code in all packages with black
- `make type-check` - Run mypy on all package sources
- `make check` - All quality checks excluding container tests (fast)
- `make check-all` - Complete quality validation including container tests

### Per-Package Testing

- `make test-core` - Core package tests only
- `make test-git` - Git repo tools tests only
- `make test-github-manager` - GitHub repo manager tests only
- `make test-github-data` - GitHub data tools tests only
- `make test-orchestrator` - Kit orchestrator tests only

### Selective Testing (Recommended)

- `make test-changed` - Test only packages with changes on current branch
- `make test-fast-changed` - Fast tests for changed packages only

The selective testing commands automatically detect which packages changed since main and run only those tests. If core changes, all packages are tested since they all depend on core.

### Docker Builds

- `make docker-build-all` - Build all containers (base + all subprojects)
- `make docker-build-base` - Build base image only
- `make docker-build-git-base` - Build git base image
- `make docker-build-git` - Build git-repo-tools container
- `make docker-build-github-manager` - Build github-repo-manager container
- `make docker-build-github-data` - Build github-data-tools container
- `make docker-build-orchestrator` - Build kit-orchestrator container (recommended)

## Testing

This project uses a comprehensive multi-layered testing approach with enhanced fixtures, performance markers, and extensive test organization:

### Test Categories and Markers

The project uses **pytest markers** for sophisticated test organization and selective execution:

#### Core Test Types
- **Unit Tests** (`@pytest.mark.unit`): Fast, isolated component tests (< 1s each)
- **Integration Tests** (`@pytest.mark.integration`): Component interaction tests (1-10s each)  
- **Container Tests** (`@pytest.mark.container`): Full Docker workflow tests (30s+ each)

#### Enhanced Test Organization
- **Performance Markers**: `fast`, `medium`, `slow`, `performance` for execution time targeting
- **Infrastructure Markers**: `save_workflow`, `restore_workflow`, `github_api`, `storage`, `error_handling`
- **Fixture Categories**: `enhanced_fixtures`, `data_builders`, `error_simulation`, `workflow_services`
- **Scenario Markers**: `empty_repository`, `large_dataset`, `rate_limiting`, `api_errors`

#### Entity-Specific Test Selection

**Entity markers have been deprecated.** Use file paths or `-k` flag filtering for entity-specific tests:

```bash
# By file path (recommended)
pytest tests/unit/entities/releases/           # All release unit tests
pytest tests/unit/entities/{releases,milestones}/  # Multiple entities

# By keyword filter
pytest tests/ -k release                        # All tests matching "release"
pytest tests/integration/ -k milestone          # Milestone integration tests
pytest tests/ -k "release or milestone"         # Multiple entities
```

### Essential Commands

**Development cycle commands:**
- `make test-fast` - All tests except container tests (recommended for development)
- `make test-unit` - Unit tests only (fastest feedback)
- `make test-integration` - Integration tests excluding container tests
- `make test-container` - Container integration tests only (requires Docker)
- `make test` - All tests with source code coverage

**Coverage analysis commands:**
- `make test-with-test-coverage` - Coverage analysis of test files themselves
- `make test-fast-with-test-coverage` - Fast tests with test file coverage

**Quality assurance commands:**
- `make check` - All quality checks excluding container tests (fast)
- `make check-all` - Complete quality validation including container tests

### Shared Fixture System

The project includes a comprehensive shared fixture system in `tests/shared/`:
- **Core Fixtures**: Basic infrastructure (temp directories, sample data)
- **Enhanced Boundary Mocks**: Realistic GitHub API response simulation
- **Workflow Service Fixtures**: Pre-configured service compositions for end-to-end testing
- **Data Builder Patterns**: Dynamic test data generation for custom scenarios
- **Error Simulation**: Comprehensive error handling and resilience testing

### TDD Workflow

Follow Test-Driven Development practices:
1. **Write failing tests first** using appropriate markers and fixtures
2. **Implement minimal code** to pass tests
3. **Run `make test-fast`** for quick validation
4. **Run `make check`** before committing
5. **Use container tests** for final integration validation

For complete testing documentation, commands, and best practices, see **[docs/testing/README.md](docs/testing/README.md)**.

## Code Quality and Standards

### Coding Standards

This project follows **Clean Code** principles from Robert C. Martin's "Clean Code". All code must adhere to the Step-Down Rule and other Clean Code standards. See [CONTRIBUTING.md](CONTRIBUTING.md) for complete coding standards and examples.

### Commit Message Standards

This repository follows the [Conventional Commits](https://www.conventionalcommits.org/) specification. See [CONTRIBUTING.md](CONTRIBUTING.md) for complete commit message guidelines and examples.

**IMPORTANT**: All commits must be signed off using `git commit -s` to comply with the DCO (Developer Certificate of Origin) requirement.

## Session Documentation

Always end Claude Code sessions by asking: "Save session"

- Save sessions, reports, and plans to `docs/planning/YYYY-MM-DD-HH-MM-topic.md`
- Use 24-hour format for timestamps (e.g., `2025-09-08-14-30-feature-implementation.md`)
- Use the current date and time for timestamps
- Include all prompts and their resulting actions
- Include key decisions, commands learned, and outcomes
- Document any new tools, scripts, or processes introduced
- Note follow-up items or unresolved issues
- Always use the current date and time to create the file name when creating a session summary

This creates a searchable history of development decisions and Claude Code interactions.

## Developer Resources

For comprehensive development information, see:
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Main developer documentation, setup, workflow, and coding standards
- **[docs/testing/README.md](docs/testing/README.md)** - Complete testing guide and best practices
- Use TDD.
- Never commit to main.