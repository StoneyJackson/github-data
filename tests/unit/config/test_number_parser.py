"""Unit tests for NumberSpecificationParser."""

import pytest
from src.config.number_parser import NumberSpecificationParser


class TestNumberSpecificationParser:
    """Test suite for NumberSpecificationParser."""

    def test_parse_single_number(self):
        """Test parsing single numbers."""
        assert NumberSpecificationParser.parse("5") == {5}
        assert NumberSpecificationParser.parse("1") == {1}
        assert NumberSpecificationParser.parse("999") == {999}
        assert NumberSpecificationParser.parse("  42  ") == {42}  # with whitespace

    def test_parse_multiple_numbers_space_separated(self):
        """Test parsing multiple numbers separated by spaces."""
        assert NumberSpecificationParser.parse("1 3 5") == {1, 3, 5}
        assert NumberSpecificationParser.parse("10 20 30") == {10, 20, 30}
        assert NumberSpecificationParser.parse("  1   3   5  ") == {
            1,
            3,
            5,
        }  # extra whitespace

    def test_parse_multiple_numbers_comma_separated(self):
        """Test parsing multiple numbers separated by commas."""
        assert NumberSpecificationParser.parse("1,3,5") == {1, 3, 5}
        assert NumberSpecificationParser.parse("10,20,30") == {10, 20, 30}

    def test_parse_multiple_numbers_mixed_delimiters(self):
        """Test parsing multiple numbers with mixed delimiters."""
        assert NumberSpecificationParser.parse("1, 3, 5") == {1, 3, 5}
        assert NumberSpecificationParser.parse("1 , 3 , 5") == {1, 3, 5}
        assert NumberSpecificationParser.parse("1,3 5") == {1, 3, 5}
        assert NumberSpecificationParser.parse("1 3,5") == {1, 3, 5}

    def test_parse_simple_range(self):
        """Test parsing simple ranges."""
        assert NumberSpecificationParser.parse("1-5") == {1, 2, 3, 4, 5}
        assert NumberSpecificationParser.parse("3-7") == {3, 4, 5, 6, 7}
        assert NumberSpecificationParser.parse("100-103") == {100, 101, 102, 103}

    def test_parse_single_number_range(self):
        """Test parsing ranges with same start and end."""
        assert NumberSpecificationParser.parse("5-5") == {5}
        assert NumberSpecificationParser.parse("1-1") == {1}

    def test_parse_large_range(self):
        """Test parsing large ranges."""
        result = NumberSpecificationParser.parse("100-105")
        expected = {100, 101, 102, 103, 104, 105}
        assert result == expected

    def test_parse_range_plus_numbers(self):
        """Test parsing combinations of ranges and numbers."""
        assert NumberSpecificationParser.parse("1-3 5") == {1, 2, 3, 5}
        assert NumberSpecificationParser.parse("1-3,5") == {1, 2, 3, 5}
        assert NumberSpecificationParser.parse("1-3, 5") == {1, 2, 3, 5}
        assert NumberSpecificationParser.parse("5 1-3") == {1, 2, 3, 5}

    def test_parse_multiple_ranges(self):
        """Test parsing multiple ranges."""
        assert NumberSpecificationParser.parse("1-3 8-10") == {1, 2, 3, 8, 9, 10}
        assert NumberSpecificationParser.parse("1-3,8-10") == {1, 2, 3, 8, 9, 10}
        assert NumberSpecificationParser.parse("1-3, 8-10") == {1, 2, 3, 8, 9, 10}

    def test_parse_complex_combinations(self):
        """Test parsing complex combinations of ranges and numbers."""
        assert NumberSpecificationParser.parse("1-3, 5, 8-10") == {1, 2, 3, 5, 8, 9, 10}
        assert NumberSpecificationParser.parse("1, 3-5, 7, 9-11") == {
            1,
            3,
            4,
            5,
            7,
            9,
            10,
            11,
        }
        assert NumberSpecificationParser.parse("10-12 5 1-3") == {
            1,
            2,
            3,
            5,
            10,
            11,
            12,
        }

    def test_parse_duplicate_numbers(self):
        """Test that duplicate numbers are handled correctly."""
        assert NumberSpecificationParser.parse("1 1 2") == {1, 2}
        assert NumberSpecificationParser.parse("1-3 2") == {1, 2, 3}
        assert NumberSpecificationParser.parse("1,1,2,2") == {1, 2}

    def test_parse_whitespace_handling(self):
        """Test various whitespace scenarios."""
        assert NumberSpecificationParser.parse(" 1 , 2 , 3 ") == {1, 2, 3}
        assert NumberSpecificationParser.parse("  1-3  ") == {1, 2, 3}
        assert NumberSpecificationParser.parse("1   3   5") == {1, 3, 5}

    def test_parse_large_numbers(self):
        """Test parsing large numbers."""
        assert NumberSpecificationParser.parse("999999") == {999999}
        assert NumberSpecificationParser.parse("100000-100002") == {
            100000,
            100001,
            100002,
        }

    # Error handling tests
    def test_parse_empty_string(self):
        """Test that empty strings raise ValueError."""
        with pytest.raises(ValueError, match="Number specification cannot be empty"):
            NumberSpecificationParser.parse("")

        with pytest.raises(ValueError, match="Number specification cannot be empty"):
            NumberSpecificationParser.parse("   ")

    def test_parse_invalid_range_end_less_than_start(self):
        """Test that invalid ranges raise ValueError."""
        with pytest.raises(ValueError, match="Range start must be <= end"):
            NumberSpecificationParser.parse("5-1")

        with pytest.raises(ValueError, match="Range start must be <= end"):
            NumberSpecificationParser.parse("10-5")

    def test_parse_zero_numbers(self):
        """Test that zero numbers raise ValueError."""
        with pytest.raises(ValueError, match="Numbers must be positive integers"):
            NumberSpecificationParser.parse("0")

        with pytest.raises(ValueError, match="Range numbers must be positive integers"):
            NumberSpecificationParser.parse("1-0")

        with pytest.raises(ValueError, match="Range numbers must be positive integers"):
            NumberSpecificationParser.parse("0-5")

    def test_parse_negative_numbers(self):
        """Test that negative numbers raise ValueError."""
        with pytest.raises(ValueError, match="Numbers must be positive integers"):
            NumberSpecificationParser.parse("-1")

        with pytest.raises(ValueError, match="Invalid range format"):
            NumberSpecificationParser.parse("1--3")

    def test_parse_non_numeric(self):
        """Test that non-numeric values raise ValueError."""
        with pytest.raises(ValueError, match="Invalid number format"):
            NumberSpecificationParser.parse("abc")

        with pytest.raises(ValueError, match="Invalid range format"):
            NumberSpecificationParser.parse("1-abc")

        with pytest.raises(ValueError, match="Invalid range format"):
            NumberSpecificationParser.parse("abc-5")

    def test_parse_empty_ranges(self):
        """Test that empty ranges raise ValueError."""
        with pytest.raises(ValueError, match="Invalid number format"):
            NumberSpecificationParser.parse("1-")

        with pytest.raises(ValueError, match="Numbers must be positive integers"):
            NumberSpecificationParser.parse("-5")

    def test_parse_multiple_dashes(self):
        """Test that multiple dashes in ranges raise ValueError."""
        with pytest.raises(ValueError, match="Invalid range format"):
            NumberSpecificationParser.parse("1-2-3")

    def test_parse_single_character_inputs(self):
        """Test single character inputs."""
        with pytest.raises(ValueError, match="Invalid number format"):
            NumberSpecificationParser.parse("a")

    # Boolean detection tests
    def test_is_boolean_value_true_values(self):
        """Test detection of true boolean values."""
        assert NumberSpecificationParser.is_boolean_value("true")
        assert NumberSpecificationParser.is_boolean_value("True")
        assert NumberSpecificationParser.is_boolean_value("TRUE")
        assert NumberSpecificationParser.is_boolean_value("yes")
        assert NumberSpecificationParser.is_boolean_value("YES")
        assert NumberSpecificationParser.is_boolean_value("on")
        assert NumberSpecificationParser.is_boolean_value("ON")

    def test_is_boolean_value_false_values(self):
        """Test detection of false boolean values."""
        assert NumberSpecificationParser.is_boolean_value("false")
        assert NumberSpecificationParser.is_boolean_value("False")
        assert NumberSpecificationParser.is_boolean_value("FALSE")
        assert NumberSpecificationParser.is_boolean_value("no")
        assert NumberSpecificationParser.is_boolean_value("NO")
        assert NumberSpecificationParser.is_boolean_value("off")
        assert NumberSpecificationParser.is_boolean_value("OFF")

    def test_is_boolean_value_with_whitespace(self):
        """Test boolean detection with whitespace."""
        assert NumberSpecificationParser.is_boolean_value(" true ")
        assert NumberSpecificationParser.is_boolean_value("  false  ")

    def test_is_boolean_value_non_boolean_values(self):
        """Test that non-boolean values are correctly identified."""
        assert not NumberSpecificationParser.is_boolean_value("1")
        assert not NumberSpecificationParser.is_boolean_value("0")
        assert not NumberSpecificationParser.is_boolean_value("5")
        assert not NumberSpecificationParser.is_boolean_value("1-5")
        assert not NumberSpecificationParser.is_boolean_value("abc")
        assert not NumberSpecificationParser.is_boolean_value("")
        assert not NumberSpecificationParser.is_boolean_value("   ")

    # Boolean parsing tests
    def test_parse_boolean_value_true_values(self):
        """Test parsing true boolean values."""
        assert NumberSpecificationParser.parse_boolean_value("true") is True
        assert NumberSpecificationParser.parse_boolean_value("True") is True
        assert NumberSpecificationParser.parse_boolean_value("TRUE") is True
        assert NumberSpecificationParser.parse_boolean_value("yes") is True
        assert NumberSpecificationParser.parse_boolean_value("YES") is True
        assert NumberSpecificationParser.parse_boolean_value("on") is True
        assert NumberSpecificationParser.parse_boolean_value("ON") is True

    def test_parse_boolean_value_false_values(self):
        """Test parsing false boolean values."""
        assert NumberSpecificationParser.parse_boolean_value("false") is False
        assert NumberSpecificationParser.parse_boolean_value("False") is False
        assert NumberSpecificationParser.parse_boolean_value("FALSE") is False
        assert NumberSpecificationParser.parse_boolean_value("no") is False
        assert NumberSpecificationParser.parse_boolean_value("NO") is False
        assert NumberSpecificationParser.parse_boolean_value("off") is False
        assert NumberSpecificationParser.parse_boolean_value("OFF") is False

    def test_parse_boolean_value_with_whitespace(self):
        """Test boolean parsing with whitespace."""
        assert NumberSpecificationParser.parse_boolean_value(" true ") is True
        assert NumberSpecificationParser.parse_boolean_value("  false  ") is False

    def test_parse_boolean_value_invalid(self):
        """Test that invalid boolean values raise ValueError."""
        with pytest.raises(ValueError, match="Invalid boolean value"):
            NumberSpecificationParser.parse_boolean_value("1")

        with pytest.raises(ValueError, match="Invalid boolean value"):
            NumberSpecificationParser.parse_boolean_value("0")

        with pytest.raises(ValueError, match="Invalid boolean value"):
            NumberSpecificationParser.parse_boolean_value("abc")

        with pytest.raises(ValueError, match="Boolean value cannot be empty"):
            NumberSpecificationParser.parse_boolean_value("")

        with pytest.raises(ValueError, match="Boolean value cannot be empty"):
            NumberSpecificationParser.parse_boolean_value("   ")
