.PHONY: install install-dev test lint format type-check clean build docker-build docker-run sync

# Install production dependencies only
install:
	pdm install --prod

# Install all dependencies (including dev)
install-dev:
	pdm install

# Sync dependencies (update lock file)
sync:
	pdm sync

# Run tests
test:
	pdm run pytest

# Run linting
lint:
	pdm run flake8 src tests

# Format code
format:
	pdm run black src tests

# Type checking
type-check:
	pdm run mypy src

# Run all quality checks
check: format lint type-check test

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .pdm-python
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build the Docker image
docker-build:
	docker build -t github-data .

# Run the Docker container (example)
docker-run-save:
	docker run --rm \
		-v $(PWD)/data:/data \
		-e GITHUB_TOKEN=$(GITHUB_TOKEN) \
		-e GITHUB_REPO=$(GITHUB_REPO) \
		-e OPERATION=save \
		github-data

docker-run-restore:
	docker run --rm \
		-v $(PWD)/data:/data \
		-e GITHUB_TOKEN=$(GITHUB_TOKEN) \
		-e GITHUB_REPO=$(GITHUB_REPO) \
		-e OPERATION=restore \
		github-data