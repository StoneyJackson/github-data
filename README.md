# GitHub Data

A containerized tool for saving and restoring comprehensive GitHub repository data including labels, issues, comments, sub-issues, pull requests, and complete Git repository history. This tool allows you to backup and restore GitHub repository metadata alongside full Git repository data with commit history, branches, and tags.

> **⚠️ Development Status**: This project is under active development. See [TODO.md](TODO.md) for current progress and upcoming features.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Usage](#usage)
  - [Save Data](#save-data)
  - [Restore Data](#restore-data)
  - [Environment Variables](#environment-variables)
  - [Git Repository Backup](#git-repository-backup)
- [Data Format](#data-format)
- [Contributing](#contributing)
- [License](#license)

## Overview

The `github-data` container provides two main operations:
- **Save**: Extract labels, issues, comments, sub-issues, pull requests, and complete Git repository history from a GitHub repository
- **Restore**: Read saved data and restore/recreate repository labels, issues, comments, sub-issue relationships, pull requests, and Git repository data

All configuration is done through environment variables, and data files are accessed by mounting a local directory into the container.

## Features

### GitHub Metadata Management
- **Labels**: Complete label backup/restore with conflict resolution strategies
- **Issues & Comments**: Full issue data with hierarchical sub-issue relationships
- **Pull Requests**: PR workflows with branch dependency validation
- **Rate Limiting**: Intelligent API rate limiting with automatic retries

### Git Repository Backup (NEW)
- **Complete Repository Cloning**: Full commit history, branches, and tags
- **Multiple Backup Formats**: Mirror clones and Git bundles
- **Repository Validation**: Integrity checks and verification  
- **Flexible Restore Options**: Restore to new locations or directories
- **Authentication Support**: Token-based authentication for private repositories

## Important Notes

- **Pull Request Restoration**: While PRs can be saved and restored, restored PRs will have current timestamps (not original creation/merge times) and require that the original branch references exist in the target repository.
- **GraphQL API**: The tool uses GitHub's GraphQL API for efficient data retrieval, with automatic fallback to REST API for write operations.

## Usage

### Save Data

Save GitHub repository labels, issues, comments, sub-issues, and pull requests to JSON files:

```bash
docker run --rm \
  -v /path/to/data:/data \
  -e GITHUB_TOKEN=your_token_here \
  -e GITHUB_REPO=owner/repository \
  -e OPERATION=save \
  github-data
```

### Restore Data

Restore GitHub repository labels, issues, comments, sub-issues, and pull requests from JSON files:

```bash
docker run --rm \
  -v /path/to/data:/data \
  -e GITHUB_TOKEN=your_token_here \
  -e GITHUB_REPO=owner/repository \
  -e OPERATION=restore \
  github-data
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPERATION` | Yes | Operation to perform: `save` or `restore` |
| `GITHUB_TOKEN` | Yes | GitHub personal access token with repo and read:user permissions. See [Token Setup Guide](docs/github-token-setup.md) |
| `GITHUB_REPO` | Yes | Target repository in format `owner/repository` |
| `DATA_PATH` | No | Path inside container for data files (default: `/data`) |
| `LABEL_CONFLICT_STRATEGY` | No | How to handle label conflicts during restore (default: `fail-if-existing`) |
| `INCLUDE_GIT_REPO` | No | Enable/disable Git repository backup (default: `true`) |
| `GIT_BACKUP_FORMAT` | No | Git backup format: `mirror`, `bundle` (default: `mirror`) |
| `GIT_AUTH_METHOD` | No | Git authentication method: `token`, `ssh` (default: `token`) |

#### Label Conflict Strategies

When restoring labels to a repository that already has labels, you can choose how conflicts are handled:

- **`fail-if-existing`** (default): Fail if any labels exist in the target repository
- **`fail-if-conflict`**: Fail only if labels with the same names exist
- **`overwrite`**: Update existing labels with restored data, create non-conflicting ones
- **`skip`**: Skip restoring labels that already exist, create only new ones
- **`delete-all`**: Delete all existing labels before restoring

Example with conflict strategy:
```bash
docker run --rm \
  -v /path/to/data:/data \
  -e GITHUB_TOKEN=your_token_here \
  -e GITHUB_REPO=owner/repository \
  -e OPERATION=restore \
  -e LABEL_CONFLICT_STRATEGY=overwrite \
  github-data
```

#### GitHub Token Permissions

**Create Token**: Visit [https://github.com/settings/tokens/new](https://github.com/settings/tokens/new)

**Required scopes:**
- `repo` (Full control of private repositories) - for both public and private repositories
- OR `public_repo` (Access public repositories) - for public repositories only

**Additional scopes for pull requests:**
- `pull` permissions are included in the `repo` scope
- For public repos only: may need `read:user` for PR author information

**Optional scopes:**
- `read:org` (Read org membership) - for organization repositories

#### Rate Limiting

The tool automatically handles GitHub API rate limiting with intelligent retry logic:

- **Automatic Retries**: Operations are automatically retried when rate limits are hit
- **Exponential Backoff**: Retry delays increase exponentially (1s, 2s, 4s, etc.) up to 60 seconds
- **Smart Monitoring**: Warns when rate limit is low (< 100 requests remaining)
- **Maximum 3 Retries**: After 3 failed attempts due to rate limiting, the operation will fail

For large repositories, operations may take longer when approaching rate limits as the tool waits for the rate limit window to reset.

### Git Repository Backup

The Git repository backup feature provides complete repository cloning alongside GitHub metadata backup.

#### Configuration

Git repository backup is controlled through environment variables:

```bash
# Enable/disable Git repository backup (default: true)
INCLUDE_GIT_REPO=true

# Backup format: mirror, bundle (default: mirror)
GIT_BACKUP_FORMAT=mirror

# Authentication method: token, ssh (default: token)  
GIT_AUTH_METHOD=token

# GitHub token for private repositories
GITHUB_TOKEN=your_github_token
```

#### Usage Examples

```bash
# Backup with Git repository (default behavior)
docker run --rm \
  -v /path/to/data:/data \
  -e GITHUB_TOKEN=your_token \
  -e GITHUB_REPO=owner/repository \
  -e OPERATION=save \
  github-data

# Backup excluding Git repository (metadata only)
docker run --rm \
  -v /path/to/data:/data \
  -e INCLUDE_GIT_REPO=false \
  -e GITHUB_TOKEN=your_token \
  -e GITHUB_REPO=owner/repository \
  -e OPERATION=save \
  github-data

# Backup with bundle format
docker run --rm \
  -v /path/to/data:/data \
  -e GIT_BACKUP_FORMAT=bundle \
  -e GITHUB_TOKEN=your_token \
  -e GITHUB_REPO=owner/repository \
  -e OPERATION=save \
  github-data
```

#### Backup Formats

- **Mirror Clone** (`mirror`): Complete repository clone with all branches, tags, and references
  - Best for: Complete repository backup, easy browsing with Git tools
  - Storage: Directory structure with `.git` contents
  
- **Bundle** (`bundle`): Compressed Git bundle containing repository data
  - Best for: Space-efficient storage, single-file backups
  - Storage: Single `.bundle` file that can be cloned from

#### Directory Structure

```
/data/
├── github-data/          # JSON metadata (existing)
│   ├── issues.json
│   ├── labels.json
│   └── pull_requests.json
└── git-data/             # Git repository data (new)
    ├── repository/       # Mirror clone (if mirror format)
    └── repository.bundle # Bundle file (if bundle format)
```

## Data Format

The container saves/restores data with the following directory structure:

```
/data/
├── github-data/            # GitHub metadata (JSON format)
│   ├── labels.json         # Repository labels
│   ├── issues.json         # Issues and their metadata
│   ├── comments.json       # All issue comments
│   ├── sub_issues.json     # Sub-issue relationships
│   ├── pull_requests.json  # Pull requests and their metadata
│   └── pr_comments.json    # All pull request comments
└── git-data/               # Git repository data (if enabled)
    ├── repository/         # Mirror clone (default format)
    └── repository.bundle   # Bundle file (alternative format)
```

### GitHub Metadata
Each JSON file contains structured data that can be used to recreate the repository's issue management state, hierarchical sub-issue relationships, and pull request workflows. All data includes original metadata (authors, timestamps, relationships) preserved in the restored content.

### Git Repository Data
- **Mirror clones**: Complete `.git` directory structure with all branches, tags, and commit history
- **Bundle files**: Compressed Git bundle format containing complete repository data
- **Validation**: All Git data includes integrity checks and metadata for verification

## Contributing

For development setup, testing, coding standards, and contribution guidelines, see **[CONTRIBUTING.md](CONTRIBUTING.md)**.

Quick start for developers:
```bash
make install-dev  # Setup development environment
make check        # Run quality checks before committing
```

## License

This project is licensed under the MIT License - see the [LICENSES/MIT.txt](LICENSES/MIT.txt) file for details.

**AI Development Notice**: This project was built using Claude AI assistance and is subject to Anthropic's [Consumer Terms of Service](https://www.anthropic.com/legal/consumer-terms) and [Acceptable Use Policy](https://anthropic.com/aup). You may not use this project to: develop competing AI products or services, train rival AI models, reverse engineer AI systems, engage in deceptive practices, violate intellectual property rights, or for any activities prohibited under Anthropic's usage policies.
