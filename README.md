# GitHub Data

A containerized tool for saving and restoring comprehensive GitHub repository data including labels, issues, comments, sub-issues, pull requests, and complete Git repository history. This tool allows you to save and restore GitHub repository metadata alongside full Git repository data with commit history, branches, and tags.

> **⚠️ Development Status**: This project is under active development. See [TODO.md](TODO.md) for current progress and upcoming features.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Usage](#usage)
  - [Save Data](#save-data)
  - [Restore Data](#restore-data)
  - [Environment Variables](#environment-variables)
  - [Git Repository Save](#git-repository-save)
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
- **Labels**: Complete label save/restore with conflict resolution strategies
- **Issues & Comments**: Full issue data with hierarchical sub-issue relationships
- **Pull Requests**: PR workflows with branch dependency validation
- **Rate Limiting**: Intelligent API rate limiting with automatic retries

### Git Repository Save
- **Complete Repository Cloning**: Full commit history, branches, and tags
- **Mirror Clone Format**: Complete repository saves with full Git history
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
  ghcr.io/stoneyjackson/github-data:latest
```

### Restore Data

Restore GitHub repository labels, issues, comments, sub-issues, and pull requests from JSON files:

```bash
docker run --rm \
  -v /path/to/data:/data \
  -e GITHUB_TOKEN=your_token_here \
  -e GITHUB_REPO=owner/repository \
  -e OPERATION=restore \
  ghcr.io/stoneyjackson/github-data:latest
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPERATION` | Yes | Operation to perform: `save` or `restore` |
| `GITHUB_TOKEN` | Yes | GitHub personal access token with repo and read:user permissions. See [Token Setup Guide](docs/github-token-setup.md) |
| `GITHUB_REPO` | Yes | Target repository in format `owner/repository` |
| `DATA_PATH` | No | Path inside container for data files (default: `/data`) |
| `LABEL_CONFLICT_STRATEGY` | No | How to handle label conflicts during restore (default: `fail-if-existing`) |
| `INCLUDE_GIT_REPO` | No | Enable/disable Git repository save (default: `true`) |
| `INCLUDE_ISSUE_COMMENTS` | No | Include issue comments in backup/restore (default: `true`) |
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
  ghcr.io/stoneyjackson/github-data:latest
```

#### Boolean Environment Variables

Boolean environment variables (`INCLUDE_GIT_REPO`, `INCLUDE_ISSUE_COMMENTS`) accept the following values:
- **True values**: `true`, `True`, `TRUE`, `1`, `yes`, `YES`, `on`, `ON`
- **False values**: `false`, `False`, `FALSE`, `0`, `no`, `NO`, `off`, `OFF`, or any other value

Examples:
```bash
# Save repository data including issue comments (default behavior)
docker run --rm \
  -v /path/to/data:/data \
  -e GITHUB_TOKEN=your_token_here \
  -e GITHUB_REPO=owner/repository \
  -e OPERATION=save \
  ghcr.io/stoneyjackson/github-data:latest

# Save repository data excluding issue comments
docker run --rm \
  -v /path/to/data:/data \
  -e GITHUB_TOKEN=your_token_here \
  -e GITHUB_REPO=owner/repository \
  -e OPERATION=save \
  -e INCLUDE_ISSUE_COMMENTS=false \
  ghcr.io/stoneyjackson/github-data:latest

# Restore repository data excluding issue comments
docker run --rm \
  -v /path/to/data:/data \
  -e GITHUB_TOKEN=your_token_here \
  -e GITHUB_REPO=owner/new-repository \
  -e OPERATION=restore \
  -e INCLUDE_ISSUE_COMMENTS=false \
  ghcr.io/stoneyjackson/github-data:latest
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

### Git Repository Save

The Git repository save feature provides complete repository cloning alongside GitHub metadata save.

#### Configuration

Git repository save is controlled through environment variables:

```bash
# Enable/disable Git repository save (default: true)
INCLUDE_GIT_REPO=true

# Authentication method: token, ssh (default: token)
GIT_AUTH_METHOD=token

# GitHub token for private repositories
GITHUB_TOKEN=your_github_token
```

#### Usage Examples

```bash
# Save with Git repository (default behavior)
docker run --rm \
  -v /path/to/data:/data \
  -e GITHUB_TOKEN=your_token \
  -e GITHUB_REPO=owner/repository \
  -e OPERATION=save \
  ghcr.io/stoneyjackson/github-data:latest

# Save excluding Git repository (metadata only)
docker run --rm \
  -v /path/to/data:/data \
  -e INCLUDE_GIT_REPO=false \
  -e GITHUB_TOKEN=your_token \
  -e GITHUB_REPO=owner/repository \
  -e OPERATION=save \
  ghcr.io/stoneyjackson/github-data:latest

# Basic Git repository save
docker run --rm \
  -v /path/to/data:/data \
  -e GITHUB_TOKEN=your_token \
  -e GITHUB_REPO=owner/repository \
  -e OPERATION=save \
  ghcr.io/stoneyjackson/github-data:latest
```

#### Git Save Format

Git repositories are backed up using **Mirror Clone** format:
- Complete repository clone with all branches, tags, and references
- Best for: Complete repository save, easy browsing with Git tools
- Storage: Directory structure with `.git` contents

#### Directory Structure

```
/data/
├── github-data/          # JSON metadata (existing)
│   ├── issues.json
│   ├── labels.json
│   └── pull_requests.json
└── git-repo/             # Git repository data (new, flattened structure)
    ├── .git/             # Git repository content
    ├── README.md         # Repository files
    └── ...               # Other repository content
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
└── git-repo/               # Git repository data (if enabled, flattened structure)
    ├── .git/               # Git repository content (mirror format)
    ├── README.md           # Repository files
    └── ...                 # Other repository content
```

### GitHub Metadata
Each JSON file contains structured data that can be used to recreate the repository's issue management state, hierarchical sub-issue relationships, and pull request workflows. All data includes original metadata (authors, timestamps, relationships) preserved in the restored content.

### Git Repository Data
- **Mirror clones**: Complete `.git` directory structure with all branches, tags, and commit history
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
