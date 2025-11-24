"""Root conftest.py for monorepo pytest configuration."""

import sys
from pathlib import Path

# Add test directories to sys.path immediately (before pytest loads)
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
