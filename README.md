# GitHub Data

A containerized tool for saving and restoring GitHub repository labels, issues, subissues, and comments to/from JSON files. This tool allows you to backup and restore GitHub repository issue-related data.

> **⚠️ Development Status**: This project is under active development. See [TODO.md](TODO.md) for current progress and upcoming features.

## Table of Contents

- [Overview](#overview)
- [Usage](#usage)
  - [Save Data](#save-data)
  - [Restore Data](#restore-data)
  - [Environment Variables](#environment-variables)
- [Data Format](#data-format)
- [Contributing](#contributing)
- [License](#license)

## Overview

The `github-data` container provides two main operations:
- **Save**: Extract labels, issues, subissues, and comments from a GitHub repository and save them to JSON files
- **Restore**: Read JSON data files and restore/recreate repository labels, issues, subissues, and comments

All configuration is done through environment variables, and data files are accessed by mounting a local directory into the container.

## Important Notes

- **Pull Requests**: Pull requests are not currently supported and are automatically excluded from both save and restore operations. Only regular issues are processed.

## Usage

### Save Data

Save GitHub repository labels, issues, subissues, and comments to JSON files:

```bash
docker run --rm \
  -v /path/to/data:/data \
  -e GITHUB_TOKEN=your_token_here \
  -e GITHUB_REPO=owner/repository \
  -e OPERATION=save \
  github-data
```

### Restore Data

Restore GitHub repository labels, issues, subissues, and comments from JSON files:

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

**Optional scopes:**
- `read:org` (Read org membership) - for organization repositories

#### Rate Limiting

The tool automatically handles GitHub API rate limiting with intelligent retry logic:

- **Automatic Retries**: Operations are automatically retried when rate limits are hit
- **Exponential Backoff**: Retry delays increase exponentially (1s, 2s, 4s, etc.) up to 60 seconds
- **Smart Monitoring**: Warns when rate limit is low (< 100 requests remaining)  
- **Maximum 3 Retries**: After 3 failed attempts due to rate limiting, the operation will fail

For large repositories, operations may take longer when approaching rate limits as the tool waits for the rate limit window to reset.

## Data Format

The container saves/restores data in JSON format with the following structure:

```
/data/
├── labels.json         # Repository labels
├── issues.json         # Issues, subissues, and their metadata
└── comments.json       # All issue and subissue comments
```

Each JSON file contains structured data that can be used to recreate the repository's issue management state.

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