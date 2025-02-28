import sys
import os
import unittest
import sqlite3

# Add parent directory to sys.path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import get_last_spx_value
from db_handler import load_config

class TestSPXValues(unittest.TestCase):
    def setUp(self):
        """
        Attempt to connect directly to the database file specified in config.
        If connection fails, skip the test.
        """
        self.config = load_config()
        db_path = self.config.get('db_path', 'data/data.db3')

        if not os.path.exists(db_path):
            self.skipTest(f"Database file not found at {db_path}. Tests skipped.")

        try:
            self.connection = sqlite3.connect(db_path)
        except sqlite3.OperationalError as e:
            self.skipTest(f"Cannot connect to database: {e}")

    def tearDown(self):
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()

    def test_spx_values(self):
        """
        Check SPX values for certain dates are not None.
        Adjust the dates based on your actual database contents if needed.
        """
        dates_to_test = [
            (2024, 9, 23),
            (2024, 9, 24),
            (2024, 9, 25),
            (2024, 9, 26)
        ]
        for (year, month, day) in dates_to_test:
            with self.subTest(date=f"{year}-{month}-{day}"):
                spx_last = get_last_spx_value(self.connection, year, month, day)
                # If you expect some days not to have data, update the assertion logic accordingly
                self.assertIsNotNone(
                    spx_last,
                    f"Expected an SPX value for {year}-{month}-{day}, but got None."
                )

if __name__ == "__main__":
    unittest.main()
