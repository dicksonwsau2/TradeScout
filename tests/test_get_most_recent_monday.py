import sys
import os
import unittest
from datetime import datetime, timedelta

# Add the parent directory (where utils.py exists) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import get_most_recent_monday  # Import the function from utils.py

class TestGetMostRecentMonday(unittest.TestCase):
    def test_get_most_recent_monday(self):
        # Generate all dates from 2024-09-01 to 2024-09-30
        start_date = datetime(2024, 9, 1)
        end_date = datetime(2024, 9, 30)
        delta = timedelta(days=1)

        current_date = start_date
        while current_date <= end_date:
            # Get the expected most recent Monday
            expected_monday = get_most_recent_monday(current_date)

            # Check if get_most_recent_monday returns the correct result
            with self.subTest(date=current_date.strftime("%Y-%m-%d")):
                result = get_most_recent_monday(current_date)
                self.assertEqual(result, expected_monday, 
                                 f"Failed for {current_date.strftime('%Y-%m-%d')}: expected {expected_monday.strftime('%Y-%m-%d')}, got {result.strftime('%Y-%m-%d')}")
            
            # Move to the next day
            current_date += delta

if __name__ == "__main__":
    unittest.main()
