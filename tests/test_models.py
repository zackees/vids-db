"""
    Tests models
"""

# pylint: disable=invalid-name,R0801


import unittest
from typing import Any, Dict

from vids_db.date import iso_fmt, now_local
from vids_db.models import Video, parse_duration


def valid_duration(duration: str) -> bool:
    """Returns true if checking the duration doesn't raise an error"""
    try:
        parse_duration(duration)
        return True
    except ValueError:
        return False


class ModelsTester(unittest.TestCase):
    """Tester for Models"""

    def test_duration(self) -> None:
        duration = "2:59:16"
        expected_seconds = 10756
        duration_seconds = parse_duration(duration)
        self.assertEqual(duration_seconds, expected_seconds)


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
                "59:60"
            )  # With a colon, the seconds can't be 60 or higher
        )
        self.assertFalse(
            valid_duration(
                "60:01"
            )  # With a colon, the minutes can't be 60 or higher
        )

        self.assertTrue(
            valid_duration(
                "23:24:01.34"  # With a colon, the minutes can't be 60 or higher
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

        timestamp = iso_fmt(now_local())

        good_vid: Dict[str, Any] = {
            "channel_name": "channel_name",
            "title": "title",
            "date_published": timestamp,
            "date_lastupdated": timestamp,
            "channel_url": "https://example/channel",
            "source": "rumble",
            "url": "https://example/video",
            "duration": "62",
            "description": "",
            "img_src": "https://example/image.jpg",
            "iframe_src": "iframe_src",
            "views": "24",
        }

        # This should not raise an exception.
        Video(**good_vid)

        bad_vid: Dict[str, Any] = dict(good_vid)
        bad_vid["duration"] = "59:60"  # Invalid seconds

        # This should raise an exception.
        with self.assertRaises(ValueError):
            Video(**bad_vid)


if __name__ == "__main__":
    unittest.main()
