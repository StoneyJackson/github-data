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

This project uses a comprehensive multi-layered testing approach:

- **Unit Tests**: Fast, isolated component tests
- **Integration Tests**: Component interaction and workflow tests
- **Container Integration Tests**: Full Docker workflow validation

For complete testing documentation, commands, and best practices, see **[docs/testing.md](docs/testing.md)**.

### Quick Testing Commands

```bash
make test-fast                    # Fast feedback (excludes slow container tests)
make test-container               # Full Docker workflow tests (requires Docker)
make test-with-test-coverage      # Analyze test file coverage
make test-fast-with-test-coverage # Fast tests with test file coverage
make check                        # All quality checks (fast)
make check-all                    # All quality checks including container tests
```

### Coverage Configuration

The project uses pytest-cov with branch coverage enabled by default:

- **Source Coverage**: Default test commands measure coverage of `src/` files only
- **Test Coverage**: Special commands (`*-with-test-coverage`) measure coverage of test files
- **Branch Coverage**: Enabled for all test scenarios to catch untested code paths
- **Reports**: Terminal output with missing lines + HTML reports in `htmlcov/`

## Scripts and Tools

The `scripts/` directory contains useful developer and maintainer commands:

- **`scripts/reuse`** - Wrapper for the REUSE license compliance tool using Docker container

Usage: `./scripts/reuse [command]` (e.g., `./scripts/reuse lint`)

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
