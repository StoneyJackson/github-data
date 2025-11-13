"""Tests for main entry point with EntityRegistry."""

import pytest
import os


@pytest.mark.unit
def test_no_operation():
    try:
        setup_environment()
        delete_from_environment("OPERATION")
        assert_main_errors()
    finally:
        cleanup_environment()


@pytest.mark.unit
def test_bad_operation():
    try:
        setup_environment()
        set_environment("OPERATION", "bad")
        assert_main_errors()
    finally:
        cleanup_environment()


@pytest.mark.unit
def test_no_github_token():
    try:
        setup_environment()
        delete_from_environment("GITHUB_TOKEN")
        assert_main_errors()
    finally:
        cleanup_environment()


@pytest.mark.unit
def test_no_github_repo():
    try:
        setup_environment()
        delete_from_environment("GITHUB_REPO")
        assert_main_errors()
    finally:
        cleanup_environment()


@pytest.mark.unit
def test_bad_boolean():
    try:
        setup_environment()
        set_environment("INCLUDE_ISSUES", "not_a_valid_bool")
        assert_main_errors()
    finally:
        cleanup_environment("INCLUDE_ISSUES")


def assert_main_errors():
    from github_data.main import main

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1


def setup_environment():
    params = {
        "OPERATION": "SAVE",
        "GITHUB_TOKEN": "test_token",
        "GITHUB_REPO": "owner/repo",
    }
    for key, value in params.items():
        set_environment(key, value)


def set_environment(key, value):
    os.environ[key] = value


def delete_from_environment(key):
    if key in os.environ:
        del os.environ[key]


def cleanup_environment(*args):
    for key in ["OPERATION", "GITHUB_TOKEN", "GITHUB_REPO"] + list(args):
        delete_from_environment(key)
