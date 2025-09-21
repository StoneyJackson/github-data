"""
Unit tests package.

This package contains fast, isolated unit tests that test individual components
in isolation using mocks and fixtures.

Tests in this package should:
- Execute quickly (< 1 second each)
- Use mocks for external dependencies
- Focus on single units of functionality
- Be marked with @pytest.mark.unit and @pytest.mark.fast
"""
import pytest

pytestmark = [pytest.mark.unit, pytest.mark.fast]