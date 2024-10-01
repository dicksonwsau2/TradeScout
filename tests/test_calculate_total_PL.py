import sys
import os
import unittest
from datetime import datetime

# Add the parent directory (where PL_Summary.py exists) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PL_Summary import calculate_total_PL  

class TestCalculateTotalPL(unittest.TestCase):
    def test_calculate_total_PL(self):
        # Define the start date as 20240901
        start_date_str = "20240923"

        # Call the function with the given start date
        result = calculate_total_PL(start_date_str)

        # Check that result is not None
        self.assertIsNotNone(result, "The result should not be None")

        # Optionally, if you know the expected total PL, you can assert the exact value
        # For example:
        # expected_total_pl = 12345.67  # Replace with the expected value
        # self.assertEqual(result, expected_total_pl, f"Expected {expected_total_pl} but got {result}")

        print(f"Total PL from {start_date_str}: {result}")

if __name__ == "__main__":
    unittest.main()
