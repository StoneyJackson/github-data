# Kit Orchestrator

Complete orchestrator package that bundles all GitHub data tools for full freeze/restore workflows.

## Overview

The kit-orchestrator provides a backward-compatible interface matching the original monolithic github-data container. It coordinates operations across all subproject packages:

- **github-data-core**: Core infrastructure and base classes
- **git-repo-tools**: Git repository backup/restore
- **github-repo-manager**: Repository lifecycle management
- **github-data-tools**: GitHub data save/restore operations

## Usage

### As a Python Package

```bash
# Install the orchestrator
pdm install

# Run save operation
OPERATION=save \
GITHUB_TOKEN=your_token \
GITHUB_REPO=owner/repo \
DATA_PATH=/path/to/data \
kit-orchestrator

# Run restore operation
OPERATION=restore \
GITHUB_TOKEN=your_token \
GITHUB_REPO=owner/repo \
DATA_PATH=/path/to/data \
kit-orchestrator
```

### As a Docker Container

```bash
# Build the container
docker build -f docker/kit-orchestrator.Dockerfile -t kit-orchestrator .

# Run save operation
docker run --rm \
  -e OPERATION=save \
  -e GITHUB_TOKEN=your_token \
  -e GITHUB_REPO=owner/repo \
  -e DATA_PATH=/data \
  -v $(pwd)/data:/data \
  kit-orchestrator

# Run restore operation
docker run --rm \
  -e OPERATION=restore \
  -e GITHUB_TOKEN=your_token \
  -e GITHUB_REPO=owner/repo \
  -e DATA_PATH=/data \
  -v $(pwd)/data:/data \
  kit-orchestrator
```

## Environment Variables

All environment variables from the original github-data container are supported:

### Required Variables

- `OPERATION`: Operation to perform (`save` or `restore`)
- `GITHUB_TOKEN`: GitHub personal access token
- `GITHUB_REPO`: Repository name in format `owner/repo`

### Optional Variables

- `DATA_PATH`: Data directory path (default: `/data`)
- `INCLUDE_LABELS`: Include labels (`true`/`false`, default: `true`)
- `INCLUDE_MILESTONES`: Include milestones (`true`/`false`, default: `true`)
- `INCLUDE_ISSUES`: Include issues (`true`/`false` or comma-separated numbers, default: `true`)
- `INCLUDE_ISSUE_COMMENTS`: Include issue comments (`true`/`false`, default: `true`)
- `INCLUDE_PULL_REQUESTS`: Include pull requests (`true`/`false` or comma-separated numbers, default: `true`)
- `INCLUDE_PULL_REQUEST_COMMENTS`: Include PR comments (`true`/`false`, default: `true`)
- `INCLUDE_PULL_REQUEST_REVIEWS`: Include PR reviews (`true`/`false`, default: `true`)
- `INCLUDE_SUB_ISSUES`: Include sub-issues (`true`/`false` or comma-separated numbers, default: `true`)
- `INCLUDE_GIT_REPO`: Include git repository (`true`/`false`, default: `false`)
- `CREATE_REPOSITORY_IF_MISSING`: Create repository if it doesn't exist during restore (default: `true`)
- `REPOSITORY_VISIBILITY`: Repository visibility when creating (`public`/`private`, default: `public`)

## Backward Compatibility

The kit-orchestrator maintains 100% backward compatibility with the original monolithic github-data container:

- Same environment variable interface
- Same command-line interface
- Same output format
- Same error handling
- Same data file structure

Existing Docker Compose configurations and scripts will work without modification.

## Development

### Running Tests

```bash
# Run all tests
make test-orchestrator

# Run fast tests (excluding container tests)
make test-orchestrator-fast

# Run only container tests
pytest packages/kit-orchestrator/tests/container/ -v
```

### Building the Image

```bash
# Build orchestrator image
make docker-build-orchestrator
```

## Architecture

The kit-orchestrator follows a simple orchestration pattern:

1. **Load Configuration**: Parse environment variables
2. **Initialize Services**: Create GitHub, storage, and git services
3. **Build Registry**: Configure entity registry from environment
4. **Create Orchestrator**: Instantiate save or restore orchestrator
5. **Execute Operation**: Run the operation with all enabled entities
6. **Report Results**: Display success/failure status

All actual implementation logic resides in the subproject packages. The kit-orchestrator simply coordinates their interaction.
