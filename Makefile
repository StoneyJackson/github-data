.PHONY: install install-dev test test-unit test-integration test-container test-fast lint format type-check clean build docker-build docker-run sync check check-all docker-compose-up-save docker-compose-up-restore docker-compose-test docker-compose-health docker-compose-down

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
	pdm run pytest --cov=src --cov-config=pytest.ini -m container --timeout=300

# Run all tests except container tests (excludes test files from coverage)
test-fast:
	pdm run pytest --cov=src --cov-config=pytest.ini -m "not container"

# Run tests with coverage of test files only
test-with-test-coverage:
	pdm run pytest --cov=tests --cov-config=pytest.ini

# Run fast tests with coverage of test files only  
test-fast-with-test-coverage:
	pdm run pytest --cov=tests --cov-config=pytest.ini -m "not container"

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