"""
Container tests package.

This package contains full Docker workflow integration tests that validate
complete containerized operations and end-to-end scenarios.

Tests in this package should:
- Test complete Docker workflows
- Validate container interactions
- Be marked with appropriate container markers
- Expect longer execution times (30+ seconds)
"""

import pytest

pytestmark = [
    pytest.mark.container,
    pytest.mark.integration,
    pytest.mark.slow,
]
