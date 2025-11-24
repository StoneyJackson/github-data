"""Root conftest.py for monorepo pytest configuration.

This conftest uses pytest_plugins to register shared test utilities
from each package's tests directory, making fixtures available across
the monorepo while avoiding import path conflicts.
"""

import sys
from pathlib import Path

# Add test directories to sys.path for shared utilities
# This allows tests to import from tests.shared.* within their package
repo_root = Path(__file__).parent
test_dirs = [
    repo_root / "packages/core/tests",
    repo_root / "packages/git-repo-tools/tests",
    repo_root / "packages/github-data-tools/tests",
]

for test_dir in test_dirs:
    test_dir_str = str(test_dir)
    if test_dir.exists() and test_dir_str not in sys.path:
        sys.path.insert(0, test_dir_str)

# Note: Shared fixtures from github-data-tools/tests/shared are registered
# through a conftest.py in that package's tests directory, using the
# @pytest.fixture decorator. The sys.path manipulation above allows
# tests to import from these shared modules using relative imports.
