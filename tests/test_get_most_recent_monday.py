import sys
import os
import unittest
from datetime import datetime

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import get_most_recent_monday

class TestGetMostRecentMonday(unittest.TestCase):
    def test_get_most_recent_monday_known_cases(self):
        """
        Check a handful of known dates against their known "most recent Monday."
        """
        test_cases = [
            # (InputDate, ExpectedMonday)
            (datetime(2024, 9, 2), datetime(2024, 9, 2)),  # Monday -> same day
            (datetime(2024, 9, 3), datetime(2024, 9, 2)),  # Tuesday -> previous Monday is 9/2
            (datetime(2024, 9, 8), datetime(2024, 9, 2)),  # Sunday -> previous Monday is 9/2
            (datetime(2024, 9, 9), datetime(2024, 9, 9)),  # Monday -> same day
            (datetime(2024, 9, 10), datetime(2024, 9, 9)), # Tuesday -> Monday is 9/9
        ]

        for input_date, expected_monday in test_cases:
            with self.subTest(date=input_date):
                result = get_most_recent_monday(input_date)
                self.assertEqual(
                    result,
                    expected_monday,
                    f"For {input_date.date()}, expected {expected_monday.date()}, got {result.date()}"
                )

if __name__ == "__main__":
    unittest.main()
