"""
Configuration for common/shared converters.

These converters are used across multiple entities and don't belong
to any specific entity package.
"""


class CommonConvertersConfig:
    """Configuration for common converters used across entities."""

    name = "common"

    converters = {
        "convert_to_user": {
            "module": "github_data.github.converters",
            "function": "convert_to_user",
            "target_model": "GitHubUser",
        },
        "_parse_datetime": {
            "module": "github_data.github.converters",
            "function": "_parse_datetime",
            "target_model": None,  # Utility function
        },
        "_extract_pr_number_from_url": {
            "module": "github_data.github.converters",
            "function": "_extract_pr_number_from_url",
            "target_model": None,  # Utility function
        },
    }
