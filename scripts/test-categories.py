#!/usr/bin/env python3
"""Test execution script for different test categories."""

import subprocess
import sys
import argparse


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)

    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        print(f"❌ {description} failed with exit code {result.returncode}")
        return False
    else:
        print(f"✅ {description} completed successfully")
        return True


def main():
    parser = argparse.ArgumentParser(description="Run categorized tests")
    parser.add_argument(
        "--fast", action="store_true", help="Run only fast tests"
    )
    parser.add_argument(
        "--unit", action="store_true", help="Run only unit tests"
    )
    parser.add_argument(
        "--integration", action="store_true", help="Run only integration tests"
    )
    parser.add_argument(
        "--container", action="store_true", help="Run only container tests"
    )
    parser.add_argument(
        "--feature",
        choices=["labels", "issues", "comments", "sub_issues", "pull_requests"],
        help="Run tests for specific feature"
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Include coverage reporting"
    )

    args = parser.parse_args()

    base_cmd = ["python", "-m", "pytest"]

    if args.coverage:
        base_cmd.extend(["--cov=src", "--cov-report=term-missing"])

    if args.fast:
        base_cmd.extend(["-m", "fast"])
        success = run_command(base_cmd, "Fast tests")
    elif args.unit:
        base_cmd.extend(["-m", "unit"])
        success = run_command(base_cmd, "Unit tests")
    elif args.integration:
        base_cmd.extend(["-m", "integration"])
        success = run_command(base_cmd, "Integration tests")
    elif args.container:
        base_cmd.extend(["-m", "container"])
        success = run_command(base_cmd, "Container tests")
    elif args.feature:
        base_cmd.extend(["-m", args.feature])
        success = run_command(base_cmd, f"{args.feature.title()} feature tests")
    else:
        # Run test categories in sequence
        categories = [
            (["fast"], "Fast tests (TDD cycle)"),
            (["medium", "and", "not", "container"], "Medium integration tests"),
            (["slow", "and", "not", "container"], "Slow integration tests"),
            (["container"], "Container tests"),
        ]

        all_success = True
        for markers, description in categories:
            cmd = base_cmd + ["-m", " ".join(markers)]
            success = run_command(cmd, description)
            all_success = all_success and success

        success = all_success

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
