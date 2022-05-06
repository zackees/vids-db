"""
    Tests models
"""

# pylint: disable=invalid-name,R0801


import unittest

from vid_db.models import check_duration


def valid_duration(duration: str) -> bool:
    """Returns true if checking the duration doesn't raise an error"""
    try:
        check_duration(duration)
        return True
    except ValueError:
        return False


class ModelsTester(unittest.TestCase):
    """Tester for Models"""

    def test_check_duration(self) -> None:
        """Test the full text search database."""
        # Assert that the call does not throw an exception.
        self.assertTrue(valid_duration("59"))
        self.assertTrue(
            valid_duration(
                "60"  # Without a colon, the duration is assumed to be seconds and can be any value.
            )
        )
        self.assertFalse(
            valid_duration(
                "59:60"  # With a colon, the seconds can't be 60 or higher
            )
        )
        self.assertFalse(
            valid_duration(
                "60:01"  # With a colon, the minutes can't be 60 or higher
            )
        )

        ok_durations = [
            "",
            "?",
            "0",
            "00",
            "06",
            "6",
            "61",
            "23:24",
            "23:24:01.34",
        ]
        for dur in ok_durations:
            self.assertTrue(valid_duration(dur), f"{dur} should be valid")

        bad_durations = ["-7", "61:01", "-1:01", "25:24:01.34"]
        for dur in bad_durations:
            self.assertFalse(valid_duration(dur), f"{dur} should be invalid")


if __name__ == "__main__":
    unittest.main()
