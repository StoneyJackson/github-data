# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the GitHub Data project - a containerized solution for saving and restoring GitHub repository labels, issues, subissues, and comments. It provides tools to backup and restore GitHub repository issue management data.

## Development Environment

This repository uses DevContainer for consistent development environments:

- **Base Environment**: Ubuntu-based container with Docker-in-Docker support
- **Pre-installed Tools**:
  - Node.js LTS
  - Python 3 with pip and venv
  - Git, build tools, and common utilities
  - Claude Code CLI (`@anthropic-ai/claude-code`)
  - Docker CLI and Docker Compose

## Developer Scripts

The `scripts/` directory contains useful developer and maintainer commands:

- **`scripts/reuse`** - Wrapper for the REUSE license compliance tool using Docker container

Usage: `./scripts/reuse [command]` (e.g., `./scripts/reuse lint`)

## Getting Started

This GitHub Data project provides containerized tools for backing up and restoring GitHub repository issue management data:

1. Configure your GitHub access credentials and target repositories
2. Use the backup tools to save repository labels, issues, subissues, and comments
3. Use the restore tools to recreate issue management state from saved JSON data
4. Customize backup/restore operations for specific label and issue requirements

## Commit Message Standards

This repository follows the [Conventional Commits](https://www.conventionalcommits.org/) specification. See [CONTRIBUTING.md](CONTRIBUTING.md) for complete commit message guidelines and examples.

**IMPORTANT**: All commits must be signed off using `git commit -s` to comply with the DCO (Developer Certificate of Origin) requirement.

## Session Documentation

Always end Claude Code sessions by asking: "Save session"

- Save summaries to `docs/claude-sessions/YYYY-MM-DD-HH-MM-topic.md`
- Use 24-hour format for timestamps (e.g., `2025-09-08-14-30-feature-implementation.md`)
- Include all prompts and their resulting actions.
- Include key decisions, commands learned, and outcomes
- Document any new tools, scripts, or processes introduced
- Note follow-up items or unresolved issues

This creates a searchable history of development decisions and Claude Code interactions.

## Current Project Status

This GitHub Data project is in initial development phase. The foundation includes:

- DevContainer environment for consistent development
- Docker-in-Docker support for containerized operations
- Python project with PDM package management
- Development tooling (pytest, black, flake8, mypy)
- Base tooling for GitHub API interactions

## Development Commands

All development uses PDM for package management:

- `make install-dev` - Install all dependencies (including dev tools)
- `make test` - Run all tests with pytest
- `make test-fast` - Run all tests except slow container tests (recommended for development)
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
make test-fast      # Fast feedback (excludes slow container tests)
make test-container # Full Docker workflow tests (requires Docker)
make check          # All quality checks (fast)
make check-all      # All quality checks including container tests
```

## Developer Resources

For comprehensive development information, see:
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Main developer documentation, setup, workflow, and coding standards
- **[docs/testing.md](docs/testing.md)** - Complete testing guide and best practices

## Coding Standards

This project follows **Clean Code** principles from Robert C. Martin's "Clean Code". All code must adhere to the Step-Down Rule and other Clean Code standards. See [CONTRIBUTING.md](CONTRIBUTING.md) for complete coding standards and examples.

## Package Management

This project uses [PDM](https://pdm.fming.dev/) for modern Python dependency management:
- Dependencies defined in `pyproject.toml` following PEP 621
- Lock file (`pdm.lock`) ensures reproducible builds
- Development dependencies separate from production

Next development phases will include:
- GitHub API client implementation for issues and labels
- Label backup and restore functionality
- Issue and subissue backup and restore capabilities
- Comment backup and restore functionality
- CLI interface for issue management operations
- Configuration management for multiple repositories
- Always include all prompts and their resulting actions when creating a session summary.
- Always use the current date and time to create the file name when creating a session summary.