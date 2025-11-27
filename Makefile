.PHONY: help install-dev sync clean
.PHONY: test test-all test-fast test-unit test-integration test-container
.PHONY: test-core test-git test-github-manager test-github-data test-orchestrator
.PHONY: test-changed test-fast-changed
.PHONY: test-with-test-coverage test-fast-with-test-coverage
.PHONY: lint format type-check check check-all
.PHONY: docker-build-all docker-build-base docker-build-git-base
.PHONY: docker-build-git docker-build-github-manager docker-build-github-data docker-build-orchestrator

# Default target
help:
	@echo "GitHub Data Monorepo Makefile"
	@echo ""
	@echo "Installation:"
	@echo "  make install-dev              Install all packages with dev dependencies"
	@echo "  make sync                     Sync dependencies (update lock file)"
	@echo ""
	@echo "Testing:"
	@echo "  make test                     All tests with source code coverage"
	@echo "  make test-all                 Alias for 'test'"
	@echo "  make test-fast                All tests except container tests (recommended for dev)"
	@echo "  make test-unit                Unit tests only (fastest)"
	@echo "  make test-integration         Integration tests excluding container tests"
	@echo "  make test-container           Container integration tests only"
	@echo ""
	@echo "Per-package testing:"
	@echo "  make test-core                Core tests only"
	@echo "  make test-git                 Git repo tools tests only"
	@echo "  make test-github-manager      GitHub repo manager tests only"
	@echo "  make test-github-data         GitHub data tools tests only"
	@echo "  make test-orchestrator        Kit orchestrator tests only"
	@echo ""
	@echo "Selective testing:"
	@echo "  make test-changed             Test only packages with changes on current branch"
	@echo "  make test-fast-changed        Fast tests for changed packages only"
	@echo ""
	@echo "Coverage:"
	@echo "  make test-with-test-coverage       Coverage analysis of test files"
	@echo "  make test-fast-with-test-coverage  Fast tests with test file coverage"
	@echo ""
	@echo "Quality checks:"
	@echo "  make lint                     Run flake8 linting"
	@echo "  make format                   Format code with black"
	@echo "  make type-check               Run mypy type checking"
	@echo "  make check                    All quality checks excluding container tests (fast)"
	@echo "  make check-all                Complete quality validation including container tests"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build-all         Build all containers (base + all subprojects)"
	@echo "  make docker-build-base        Build base image only"
	@echo "  make docker-build-git-base    Build git base image"
	@echo "  make docker-build-git         Build git-repo-tools container"
	@echo "  make docker-build-github-manager  Build github-repo-manager container"
	@echo "  make docker-build-github-data     Build github-data-tools container"
	@echo "  make docker-build-orchestrator    Build kit-orchestrator container"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean                    Clean build artifacts"

# Installation
install-dev:
	pdm install

sync:
	pdm sync

# Testing - All tests
test:
	pdm run pytest --cov=packages --cov-config=pyproject.toml

test-all: test

# Testing - Fast (excluding container tests)
test-fast:
	pdm run pytest --durations=0 --durations-min=1 --cov=packages --cov-config=pyproject.toml -m "not container and not slow"

# Testing - By type
test-unit:
	pdm run pytest --cov=packages --cov-config=pyproject.toml -m unit

test-integration:
	pdm run pytest --cov=packages --cov-config=pyproject.toml -m "integration and not container"

test-container:
	pdm run pytest --cov=packages --cov-config=pyproject.toml -m container

# Testing - Per package
test-core:
	pdm run pytest packages/core/tests --cov=packages/core/src --cov-config=pyproject.toml

test-git:
	pdm run pytest packages/git-repo-tools/tests --cov=packages/git-repo-tools/src --cov-config=pyproject.toml

test-github-manager:
	pdm run pytest packages/github-repo-manager/tests --cov=packages/github-repo-manager/src --cov-config=pyproject.toml

test-github-data:
	pdm run pytest packages/github-data-tools/tests --cov=packages/github-data-tools/src --cov-config=pyproject.toml

test-orchestrator:
	pdm run pytest packages/kit-orchestrator/tests --cov=packages/kit-orchestrator/src --cov-config=pyproject.toml

# Testing - Selective (based on git changes)
test-changed:
	@bash scripts/test-changed.sh

test-fast-changed:
	@bash scripts/test-changed.sh --fast

# Testing - Coverage of test files
test-with-test-coverage:
	pdm run pytest --cov=packages/*/tests --cov-config=pyproject.toml

test-fast-with-test-coverage:
	pdm run pytest --cov=packages/*/tests --cov-config=pyproject.toml -m "not container and not slow"

# Quality checks
lint:
	pdm run flake8 packages/*/src packages/*/tests

format:
	pdm run black packages/*/src packages/*/tests

type-check:
	pdm run mypy packages/core/src packages/git-repo-tools/src packages/github-repo-manager/src packages/github-data-tools/src packages/kit-orchestrator/src

check: format lint type-check test-fast

check-all: format lint type-check test-all

# Docker builds
docker-build-base:
	docker build -t github-data-base:latest -f docker/base.Dockerfile .

docker-build-git-base: docker-build-base
	docker build -t github-data-git-base:latest -f docker/git-base.Dockerfile .

docker-build-git: docker-build-git-base
	docker build -t git-repo-tools:1.0.0 -f packages/git-repo-tools/Dockerfile .

docker-build-github-manager: docker-build-base
	docker build -t github-repo-manager:1.0.0 -f packages/github-repo-manager/Dockerfile .

docker-build-github-data: docker-build-base
	docker build -t github-data-tools:1.0.0 -f packages/github-data-tools/Dockerfile .

docker-build-orchestrator:
	docker build -t kit-orchestrator:1.0.0 -f docker/kit-orchestrator.Dockerfile .

docker-build-all: docker-build-base docker-build-git-base docker-build-git docker-build-github-manager docker-build-github-data docker-build-orchestrator

# Clean
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf coverage_html_report/
	rm -rf .pdm-python
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
