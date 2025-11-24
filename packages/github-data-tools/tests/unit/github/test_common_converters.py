"""Test that converters.py contains only common/shared converters."""

from github_data_tools.github import converters


class TestCommonConvertersOnly:
    """Verify converters.py only has common converters."""

    def test_has_user_converter(self):
        """Should have convert_to_user as a common converter."""
        assert hasattr(converters, "convert_to_user")
        assert callable(converters.convert_to_user)

    def test_has_datetime_utilities(self):
        """Should have datetime parsing utilities."""
        assert hasattr(converters, "_parse_datetime")
        assert callable(converters._parse_datetime)

    def test_has_pr_url_extractor(self):
        """Should have PR number extraction utility."""
        assert hasattr(converters, "_extract_pr_number_from_url")
        assert callable(converters._extract_pr_number_from_url)

    def test_no_entity_specific_converters(self):
        """Should not have entity-specific converters."""
        entity_specific = [
            "convert_to_label",
            "convert_to_issue",
            "convert_to_pull_request",
            "convert_to_comment",
            "convert_to_milestone",
            "convert_to_release",
            "convert_to_release_asset",
            "convert_to_sub_issue",
            # Add others as needed
        ]

        for converter_name in entity_specific:
            assert not hasattr(
                converters, converter_name
            ), f"{converter_name} should be in entity package, not converters.py"
