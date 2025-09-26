# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the GitHub Data project - a containerized solution for saving and restoring GitHub repository labels, issues, sub-issues, comments, and pull requests. It provides tools to backup and restore GitHub repository issue management data, hierarchical sub-issue relationships, and pull request workflows.

## Project Status

This GitHub Data project is in initial development phase. The foundation includes:
- DevContainer environment for consistent development
- Docker-in-Docker support for containerized operations
- Python project with PDM package management
- Development tooling (pytest, black, flake8, mypy)
- Base tooling for GitHub API interactions

**Completed features:**
- Comprehensive GitHub API client with GraphQL and REST support
- Label backup and restore functionality with conflict resolution
- Issue backup and restore capabilities with metadata preservation
- Comment backup and restore functionality
- Sub-issues support with hierarchical relationships and two-phase restore (NEW)
- Pull request backup and restore capabilities
- Rate limiting and caching for API operations
- CLI interface for repository data operations

**Future development phases:**
- Enhanced CLI options for selective PR and sub-issues backup/restore
- Configuration management for multiple repositories
- Advanced filtering and selection options

## Getting Started

This GitHub Data project provides containerized tools for backing up and restoring GitHub repository data:

1. Configure your GitHub access credentials and target repositories
2. Use the backup tools to save repository labels, issues, comments, sub-issues, and pull requests
3. Use the restore tools to recreate repository state from saved JSON data
4. Customize backup/restore operations for specific data requirements
5. Handle hierarchical sub-issue relationships and pull request workflows with branch dependency validation

## Development Environment

This repository uses DevContainer for consistent development environments:

- **Base Environment**: Ubuntu-based container with Docker-in-Docker support
- **Pre-installed Tools**:
  - Node.js LTS
  - Python 3 with pip and venv
  - Git, build tools, and common utilities
  - Claude Code CLI (`@anthropic-ai/claude-code`)
  - Docker CLI and Docker Compose

## Claude Code Agents

This repository is configured to use Claude Code agents for specialized development tasks. Agents provide autonomous, multi-step task execution for complex operations.

### Available Agents

The following specialized agents are available for this project:

- **general-purpose**: Multi-step research, code search, and complex task execution
- **backup-restore-workflow**: GitHub repository backup/restore operations, data migration, and containerized workflows
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
- Backup and restore operations

For manual agent invocation or configuration changes, refer to the Claude Code documentation.

## Package Management

This project uses [PDM](https://pdm.fming.dev/) for modern Python dependency management:
- Dependencies defined in `pyproject.toml` following PEP 621
- Lock file (`pdm.lock`) ensures reproducible builds
- Development dependencies separate from production

## Development Commands

All development uses PDM for package management:

- `make install-dev` - Install all dependencies (including dev tools)
- `make test` - Run all tests with source code coverage
- `make test-fast` - Run all tests except slow container tests (recommended for development)
- `make test-with-test-coverage` - Run all tests with test file coverage analysis
- `make test-fast-with-test-coverage` - Run fast tests with test file coverage analysis
- `make lint` - Run flake8 linting
- `make format` - Format code with black
- `make type-check` - Run mypy type checking
- `make check` - Run all quality checks (excluding container tests for speed)
- `make check-all` - Run all quality checks including container integration tests
- `make docker-build` - Build the container image

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
- **Feature Markers**: `labels`, `issues`, `comments`, `backup_workflow`, `restore_workflow`
- **Fixture Categories**: `enhanced_fixtures`, `data_builders`, `error_simulation`, `workflow_services`
- **Scenario Markers**: `empty_repository`, `large_dataset`, `rate_limiting`, `api_errors`

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

For complete testing documentation, commands, and best practices, see **[docs/testing.md](docs/testing.md)**.

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
- **[docs/testing.md](docs/testing.md)** - Complete testing guide and best practices
- Use TDD.
- Never commit to main.