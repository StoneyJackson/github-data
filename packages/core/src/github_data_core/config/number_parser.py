"""Number specification parsing for selective issue/PR processing."""

from typing import Set


class NumberSpecificationParser:
    """Parse number specifications for selective issue/PR processing."""

    @staticmethod
    def parse(specification: str) -> Set[int]:
        """Parse number specification into set of integers.

        Supports:
        - Single numbers: "5" → {5}
        - Number lists: "1 3 5", "1,3,5", "1, 3, 5" → {1, 3, 5}
        - Ranges: "1-5" → {1, 2, 3, 4, 5}
        - Combined: "1-3 5", "1-3,5", "1-3, 5" → {1, 2, 3, 5}

        Args:
            specification: Number specification string

        Returns:
            Set of integers specified

        Raises:
            ValueError: For invalid formats or ranges
        """
        if not specification or not specification.strip():
            raise ValueError("Number specification cannot be empty")

        # Normalize whitespace and split by commas and spaces
        specification = specification.strip()
        # Split by comma first, then by spaces
        parts = []
        for comma_part in specification.split(","):
            parts.extend(comma_part.split())

        numbers = set()

        for part in parts:
            part = part.strip()
            if not part:
                continue

            if "-" in part and not part.startswith("-") and not part.endswith("-"):
                # Handle range - must have valid start and end
                if part.count("-") == 1:
                    start_str, end_str = part.split("-", 1)
                    if (
                        start_str
                        and end_str
                        and not start_str.startswith("-")
                        and not end_str.startswith("-")
                    ):
                        numbers.update(NumberSpecificationParser._parse_range(part))
                    else:
                        raise ValueError(
                            f"Invalid range format: '{part}'. "
                            f"Both start and end must be specified"
                        )
                else:
                    raise ValueError(
                        f"Invalid range format: '{part}'. Expected format: 'start-end'"
                    )
            else:
                # Handle single number
                numbers.add(NumberSpecificationParser._parse_single_number(part))

        if not numbers:
            raise ValueError("Number specification resulted in empty set")

        return numbers

    @staticmethod
    def _parse_range(range_spec: str) -> Set[int]:
        """Parse a range specification like '1-5' into a set of integers.

        Args:
            range_spec: Range specification string

        Returns:
            Set of integers in the range

        Raises:
            ValueError: For invalid range formats
        """
        if range_spec.count("-") != 1:
            raise ValueError(
                f"Invalid range format: '{range_spec}'. Expected format: 'start-end'"
            )

        start_str, end_str = range_spec.split("-", 1)

        if not start_str or not end_str:
            raise ValueError(
                f"Invalid range format: '{range_spec}'. "
                f"Both start and end must be specified"
            )

        try:
            start = int(start_str)
            end = int(end_str)
        except ValueError:
            raise ValueError(
                f"Invalid range format: '{range_spec}'. Start and end must be integers"
            )

        if start <= 0 or end <= 0:
            raise ValueError(f"Range numbers must be positive integers: '{range_spec}'")

        if start > end:
            raise ValueError(f"Range start must be <= end: '{range_spec}'")

        return set(range(start, end + 1))

    @staticmethod
    def _parse_single_number(number_str: str) -> int:
        """Parse a single number string into an integer.

        Args:
            number_str: Number string to parse

        Returns:
            Parsed integer

        Raises:
            ValueError: For invalid number formats
        """
        try:
            number = int(number_str)
        except ValueError:
            raise ValueError(
                f"Invalid number format: '{number_str}'. " f"Must be a positive integer"
            )

        if number <= 0:
            raise ValueError(f"Numbers must be positive integers: '{number_str}'")

        return number

    @staticmethod
    def is_boolean_value(value: str) -> bool:
        """Check if value is a boolean specification.

        Args:
            value: String value to check

        Returns:
            True if value represents a boolean, False otherwise
        """
        if not value:
            return False

        normalized = value.lower().strip()
        boolean_values = {"true", "false", "yes", "no", "on", "off"}
        return normalized in boolean_values

    @staticmethod
    def parse_boolean_value(value: str) -> bool:
        """Parse boolean value (true/false).

        Supports case-insensitive:
        - True values: "true", "yes", "on"
        - False values: "false", "no", "off"

        Args:
            value: Boolean string to parse

        Returns:
            Boolean value

        Raises:
            ValueError: If value is not a valid boolean
        """
        if not value or not value.strip():
            raise ValueError("Boolean value cannot be empty")

        normalized = value.lower().strip()

        true_values = {"true", "yes", "on"}
        false_values = {"false", "no", "off"}

        if normalized in true_values:
            return True
        elif normalized in false_values:
            return False
        else:
            raise ValueError(
                f"Invalid boolean value: '{value}'. "
                f"Valid values are: {', '.join(sorted(true_values | false_values))}"
            )
