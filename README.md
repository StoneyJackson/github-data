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
  - [Selective Issue and PR Operations](#selective-issue-and-pr-operations)
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
| `LABEL_CONFLICT_STRATEGY` | No | How to handle label conflicts during restore (default: `skip`) |
| `INCLUDE_GIT_REPO` | No | Enable/disable Git repository save (default: `true`) |
| `INCLUDE_ISSUES` | No | Include issues in save/restore operations. Supports boolean values (`true`/`false`) or selective numbers (e.g., `"1-5 10 15-20"`) (default: `true`) |
| `INCLUDE_ISSUE_COMMENTS` | No | Include issue comments in save/restore - requires `INCLUDE_ISSUES=true` (default: `true`) |
| `INCLUDE_PULL_REQUESTS` | No | Include pull requests in save/restore operations. Supports boolean values (`true`/`false`) or selective numbers (e.g., `"10-15 20"`) (default: `true`) |
| `INCLUDE_PULL_REQUEST_COMMENTS` | No | Include pull request comments in save/restore - requires `INCLUDE_PULL_REQUESTS=true` (default: `true`) |
| `INCLUDE_SUB_ISSUES` | No | Include sub-issue relationships in save/restore (default: `true`) |
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

Boolean environment variables (`INCLUDE_GIT_REPO`, `INCLUDE_ISSUES`, `INCLUDE_ISSUE_COMMENTS`, `INCLUDE_PULL_REQUESTS`, `INCLUDE_PULL_REQUEST_COMMENTS`, `INCLUDE_SUB_ISSUES`) accept the following values:
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

### Selective Issue and PR Operations

The GitHub Data tool supports selective operations for issues and pull requests, allowing you to work with specific numbers instead of all data. This feature provides significant performance improvements and enables focused data migration scenarios.

#### Quick Start: Selective Operations

**Save Only Critical Issues:**
```bash
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=your_token \
  -e GITHUB_REPO=owner/repo \
  -e INCLUDE_ISSUES="1-10 15 20-25" \
  -e INCLUDE_ISSUE_COMMENTS=true \
  -v $(pwd)/data:/data \
  ghcr.io/stoneyjackson/github-data:latest
```

**Restore Specific PRs:**
```bash
docker run --rm \
  -e OPERATION=restore \
  -e GITHUB_TOKEN=your_token \
  -e GITHUB_REPO=owner/new-repo \
  -e INCLUDE_PULL_REQUESTS="1 3 5-7" \
  -e INCLUDE_PULL_REQUEST_COMMENTS=true \
  -v $(pwd)/data:/data \
  ghcr.io/stoneyjackson/github-data:latest
```

#### Selective Format Specification

| Format | Example | Description |
|--------|---------|-------------|
| **All** | `true` | Include all items (default) |
| **None** | `false` | Skip all items |
| **Single** | `"5"` | Include only item #5 |
| **Range** | `"1-10"` | Include items #1 through #10 |
| **Multiple Singles** | `"1 5 10"` | Include items #1, #5, and #10 |
| **Mixed** | `"1-5 10 15-20"` | Include items #1-5, #10, and #15-20 |

#### Automatic Comment Coupling

Comments automatically follow their parent issue/PR selections:
- `INCLUDE_ISSUES="5"` → Only comments from issue #5 are included
- `INCLUDE_PULL_REQUESTS="10-12"` → Only comments from PRs #10-12 are included
- Set `INCLUDE_ISSUE_COMMENTS=false` to disable comment saving entirely

#### Use Cases and Examples

**Issue Migration Between Repositories:**

1. **Save from source repository:**
```bash
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_REPO=oldorg/oldrepo \
  -e INCLUDE_ISSUES="100-150 200" \
  -e INCLUDE_ISSUE_COMMENTS=true \
  -v $(pwd)/migration:/data \
  ghcr.io/stoneyjackson/github-data:latest
```

2. **Restore to target repository:**
```bash
docker run --rm \
  -e OPERATION=restore \
  -e GITHUB_REPO=neworg/newrepo \
  -e INCLUDE_ISSUES="100-150 200" \
  -e INCLUDE_ISSUE_COMMENTS=true \
  -v $(pwd)/migration:/data \
  ghcr.io/stoneyjackson/github-data:latest
```

**Backup Optimization:**
```bash
# Backup only current milestone issues
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_REPO=owner/repo \
  -e INCLUDE_ISSUES="500-600" \
  -e INCLUDE_PULL_REQUESTS="300-350" \
  -v $(pwd)/milestone-backup:/data \
  ghcr.io/stoneyjackson/github-data:latest
```

**Testing and Development:**
```bash
# Generate test data for specific scenarios
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_REPO=owner/repo \
  -e INCLUDE_ISSUES="1 5 10-15" \
  -e INCLUDE_ISSUE_COMMENTS=false \
  -v $(pwd)/test-data:/data \
  ghcr.io/stoneyjackson/github-data:latest
```

**Mixed Configuration Examples:**
```bash
# All issues, selective PRs
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_REPO=owner/repo \
  -e INCLUDE_ISSUES=true \
  -e INCLUDE_PULL_REQUESTS="10-20 25 30-35" \
  -v $(pwd)/data:/data \
  ghcr.io/stoneyjackson/github-data:latest

# Selective issues, no PRs
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_REPO=owner/repo \
  -e INCLUDE_ISSUES="1-50" \
  -e INCLUDE_PULL_REQUESTS=false \
  -v $(pwd)/data:/data \
  ghcr.io/stoneyjackson/github-data:latest
```

#### Performance Considerations

- **Memory Usage**: Scales with selected items, not total repository size
- **API Efficiency**: Selective operations can reduce API calls by 50-90%
- **Optimal Range Size**: Ranges of 50-100 items balance efficiency and memory usage
- **Comment Coupling**: Minimal performance impact, automatically optimized

#### Best Practices

1. **Start Small**: Test with small ranges before processing large selections
2. **Use Ranges**: `"1-100"` is more efficient than `"1 2 3 ... 100"`
3. **Comment Strategy**: Enable comments only when needed
4. **Backup Verification**: Always verify restored data in test environments first
5. **Mixed Configurations**: Combine boolean and selective as needed

#### Troubleshooting

**Common Issues:**
- **Missing Numbers Warning**: Numbers not found in source repository (safe to ignore)
- **Empty Results**: Verify repository contains specified issue/PR numbers
- **API Rate Limits**: Use smaller selections or implement delays for large operations

**Error Messages:**
- `"No issues were saved, skipping all issue comments"` - Expected behavior when issues are disabled
- `"Issues not found in repository: [X, Y, Z]"` - Specified numbers don't exist (warning only)
- `"INCLUDE_ISSUES number specification cannot be empty"` - Use `false` instead of empty string

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

Git repositories are saved using **Mirror Clone** format:
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
