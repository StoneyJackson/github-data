.PHONY: install install-dev test test-unit test-integration test-container test-containers test-fast lint format type-check clean build docker-build docker-run sync check check-all docker-compose-up-save docker-compose-up-restore docker-compose-test docker-compose-health docker-compose-down

# Install production dependencies only
install:
	pdm install --prod

# Install all dependencies (including dev)
install-dev:
	pdm install

# Sync dependencies (update lock file)
sync:
	pdm sync

# Run tests (excludes test files from coverage)
test:
	pdm run pytest --cov=src --cov-config=pytest.ini

# Run unit tests only (excludes test files from coverage)
test-unit:
	pdm run pytest --cov=src --cov-config=pytest.ini -m unit

# Run integration tests (non-container, excludes test files from coverage)
test-integration:
	pdm run pytest --cov=src --cov-config=pytest.ini -m "integration and not container"

# Run container integration tests only (excludes test files from coverage)
test-container:
	pdm run pytest --cov=src --cov-config=pytest.ini -m container

# Alias for test-container (plural form)
test-containers: test-container

# Run all tests except container tests (excludes test files from coverage)
test-fast:
	pdm run pytest --durations=0 --durations-min=1 --cov=src --cov-config=pytest.ini -m "not container and not slow"

# Run tests with coverage of test files only
test-with-test-coverage:
	pdm run pytest --cov=tests --cov-config=pytest.ini

# Run fast tests with coverage of test files only
test-fast-with-test-coverage:
	pdm run pytest --cov=tests --cov-config=pytest.ini -m "not container"

# Test commands with markers
.PHONY: test-fast test-unit test-integration test-container test-by-feature

test-fast-only:  ## Run fast tests only (< 1 second)
	pdm run python -m pytest -m fast

test-unit-only:  ## Run unit tests only
	pdm run python -m pytest -m unit

test-integration-only:  ## Run integration tests only (excluding container tests)
	pdm run python -m pytest -m "integration and not container"

test-container-only:  ## Run container tests only
	pdm run python -m pytest -m container

test-by-feature:  ## Run tests for specific feature (usage: make test-by-feature FEATURE=labels)
	pdm run python -m pytest -m $(FEATURE)

# Combined test workflows
test-dev:  ## Development test workflow (fast + integration, no container)
	pdm run python -m pytest -m "fast or (integration and not container)"

test-ci:  ## CI test workflow (all tests with coverage)
	pdm run python -m pytest --cov=src --cov-report=term-missing --cov-report=html

# Test discovery and information
test-list-markers:  ## List all available test markers
	pdm run python -m pytest --markers

test-collect-only:  ## Show test collection without running tests
	pdm run python -m pytest --collect-only

test-by-markers:  ## Run tests by custom marker expression (usage: make test-by-markers MARKERS="fast and labels")
	pdm run python -m pytest -m "$(MARKERS)"

# Run linting
lint:
	pdm run flake8 src tests

# Format code
format:
	pdm run black src tests

# Type checking
type-check:
	pdm run mypy src

# Run all quality checks (excluding container tests for speed)
check: format lint type-check test-fast

# Run all quality checks including container integration tests
check-all: format lint type-check test

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

# Docker Compose commands
docker-compose-up-save:
	docker-compose -f docker-compose.test.yml --profile save up --build github-data-save

docker-compose-up-restore:
	docker-compose -f docker-compose.test.yml --profile restore up --build github-data-restore

docker-compose-test:
	docker-compose -f docker-compose.test.yml --profile test up --build github-data-test

docker-compose-health:
	docker-compose -f docker-compose.test.yml --profile health up --build github-data-health

docker-compose-down:
	docker-compose -f docker-compose.test.yml down -v --remove-orphans
