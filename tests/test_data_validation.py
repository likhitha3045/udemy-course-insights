import unittest

import pandas as pd

from data_validation import parse_courses


class ParseCoursesTests(unittest.TestCase):
    def setUp(self):
        self.valid_row = {
            "id": 1,
            "title": "Course",
            "is_paid": True,
            "price": 49,
            "num_subscribers": 10,
            "avg_rating": 4.5,
            "num_reviews": 2,
            "num_lectures": 5,
            "content_length_min": 60,
            "category": "Development",
            "subcategory": "Programming",
            "language": "English",
        }

    def as_csv(self, rows):
        return pd.DataFrame(rows).to_csv(index=False).encode("utf-8")

    def test_rejects_missing_required_columns(self):
        with self.assertRaisesRegex(ValueError, "missing required columns: avg_rating"):
            parse_courses(b"price,category\n10,Development\n")

    def test_rejects_duplicate_column_names_after_trimming(self):
        csv = self.as_csv([self.valid_row]).decode("utf-8").replace(
            "num_subscribers", " price "
        )
        with self.assertRaisesRegex(ValueError, "duplicate column names: price"):
            parse_courses(csv.encode("utf-8"))

    def test_removes_duplicate_ids_and_invalid_prices(self):
        invalid_price = {**self.valid_row, "id": 2, "price": -1}
        courses, summary = parse_courses(self.as_csv([self.valid_row, self.valid_row, invalid_price]))
        self.assertEqual(len(courses), 1)
        self.assertEqual(summary, {"duplicate_rows_removed": 1, "invalid_price_rows": 1})

    def test_coerces_bad_optional_numeric_values_and_fills_categories(self):
        row = {**self.valid_row, "avg_rating": "unknown", "language": None}
        courses, _ = parse_courses(self.as_csv([row]))
        self.assertTrue(pd.isna(courses.loc[0, "avg_rating"]))
        self.assertEqual(courses.loc[0, "language"], "Unknown")

    def test_rejects_empty_file_and_file_without_valid_prices(self):
        with self.assertRaisesRegex(ValueError, "CSV is empty"):
            parse_courses(b"")
        row = {**self.valid_row, "price": "not a price"}
        with self.assertRaisesRegex(ValueError, "no courses with a valid"):
            parse_courses(self.as_csv([row]))


if __name__ == "__main__":
    unittest.main()
