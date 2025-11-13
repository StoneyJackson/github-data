# GitHub Data

A containerized tool for saving and restoring GitHub repository data.

> **⚠️ Development Status**: This project is under active development. See [TODO.md](TODO.md) for current progress and upcoming features.

## Table of Contents

- [Authentication](#authentication)
- [Usage](#usage)
  - [Save Data](#save-data)
  - [Restore Data](#restore-data)
- [Environment Variables](#environment-variables)
- [Selective Issue and PR Operations](#selective-issue-and-pr-operations)
- [Git Repository Save](#git-repository-save)
- [Data Format](#data-format)
- [Contributing](#contributing)
- [License](#license)

## Authentication

To authorize GitHub-Data to read/write a GitHub repository,
on GitHub, create a personal access token with appropriate permissions.
Pass this token to GitHub-Data as the value of the GITHUB_TOKEN environment
variable. See Usage examples below.

## Usage

### Save Data

Save GitHub repository into the current working directory.

```bash
docker run --rm \
  -e GITHUB_TOKEN=your_token_here \
  -e OPERATION=save \
  -e GITHUB_REPO=owner/repository \
  -v "${PWD}:/data" \
  ghcr.io/stoneyjackson/github-data:latest
```

### Restore Data

Restore data in current working directory to a GitHub repository.

```bash
docker run --rm \
  -e GITHUB_TOKEN=your_token_here \
  -e OPERATION=restore \
  -e GITHUB_REPO=owner/repository \
  -v "${PWD}:/data" \
  ghcr.io/stoneyjackson/github-data:latest
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPERATION` | Yes | Operation to perform: `save` or `restore` |
| `GITHUB_TOKEN` | Yes | GitHub personal access token with repo and read:user permissions. See [Token Setup Guide](docs/github-token-setup.md) |
| `GITHUB_REPO` | Yes | Target repository in format `owner/repository` |
| `DATA_PATH` | No | Path inside container for data files (default: `/data`) |
| `LABEL_CONFLICT_STRATEGY` | No | How to handle label conflicts during restore (default: `skip`) |
| `INCLUDE_GIT_REPO` | No | Enable/disable Git repository save (default: `true`) |
| `INCLUDE_LABELS` | No | Include labels in save/restore operations (default: `true`) |
| `INCLUDE_MILESTONES` | No | Include milestones in save/restore operations (default: `true`) |
| `INCLUDE_ISSUES` | No | Include issues in save/restore operations. Supports boolean values (`true`/`false`) or selective numbers (e.g., `"1-5 10 15-20"`) (default: `true`) |
| `INCLUDE_ISSUE_COMMENTS` | No | Include issue comments in save/restore - requires `INCLUDE_ISSUES=true` (default: `true`) |
| `INCLUDE_PULL_REQUESTS` | No | Include pull requests in save/restore operations. Supports boolean values (`true`/`false`) or selective numbers (e.g., `"10-15 20"`) (default: `true`) |
| `INCLUDE_PULL_REQUEST_COMMENTS` | No | Include pull request comments in save/restore - requires `INCLUDE_PULL_REQUESTS=true` (default: `true`) |
| `INCLUDE_PR_REVIEWS` | No | Include pull request code reviews in save/restore - requires `INCLUDE_PULL_REQUESTS=true` (default: `true`) |
| `INCLUDE_PR_REVIEW_COMMENTS` | No | Include pull request review inline comments in save/restore - requires `INCLUDE_PR_REVIEWS=true` (default: `true`) |
| `INCLUDE_SUB_ISSUES` | No | Include sub-issue relationships in save/restore (default: `true`) |
| `INCLUDE_RELEASES` | No | Include releases in save/restore operations (default: `true`) |
| `INCLUDE_RELEASE_ASSETS` | No | Include release asset binaries in save/restore operations (default: `true`) |
| `GIT_AUTH_METHOD` | No | Git authentication method: `token`, `ssh` (default: `token`) |

### Label Conflict Strategies

When restoring labels to a repository that already has labels, you can choose how conflicts are handled:

- **`fail-if-existing`** (default): Fail if any labels exist in the target repository
- **`fail-if-conflict`**: Fail only if labels with the same names exist
- **`overwrite`**: Update existing labels with restored data, create non-conflicting ones
- **`skip`**: Skip restoring labels that already exist, create only new ones
- **`delete-all`**: Delete all existing labels before restoring

### Boolean Environment Variables

Boolean environment variables (`INCLUDE_GIT_REPO`, `INCLUDE_LABELS`, `INCLUDE_MILESTONES`, `INCLUDE_ISSUES`, `INCLUDE_ISSUE_COMMENTS`, `INCLUDE_PULL_REQUESTS`, `INCLUDE_PULL_REQUEST_COMMENTS`, `INCLUDE_PR_REVIEWS`, `INCLUDE_PR_REVIEW_COMMENTS`, `INCLUDE_SUB_ISSUES`, `INCLUDE_RELEASES`, `INCLUDE_RELEASE_ASSETS`) accept the following values:
- **True values**: `true`, `True`, `TRUE`, `1`, `yes`, `YES`, `on`, `ON`
- **False values**: `false`, `False`, `FALSE`, `0`, `no`, `NO`, `off`, `OFF`, or any other value

### Selective Issue and PR Operations

The GitHub Data tool supports selective operations for issues and pull requests, allowing you to work with specific numbers instead of all data. This feature provides significant performance improvements and enables focused data migration scenarios.

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


## Rate Limiting

The tool automatically handles GitHub API rate limiting with intelligent retry logic:

- **Automatic Retries**: Operations are automatically retried when rate limits are hit
- **Exponential Backoff**: Retry delays increase exponentially (1s, 2s, 4s, etc.) up to 60 seconds
- **Smart Monitoring**: Warns when rate limit is low (< 100 requests remaining)
- **Maximum 3 Retries**: After 3 failed attempts due to rate limiting, the operation will fail

For large repositories, operations may take longer when approaching rate limits as the tool waits for the rate limit window to reset.

## Save Format

### Git Repositories

Git repositories are saved using **Mirror Clone** format:
- Complete repository clone with all branches, tags, and references
- Best for: Complete repository save, easy browsing with Git tools
- Storage: Directory structure with `.git` contents

### Directory Structure

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

### Data Format

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
