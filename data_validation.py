"""CSV parsing and validation shared by the dashboard and automated checks."""

from io import BytesIO

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = {
    "is_paid",
    "price",
    "num_subscribers",
    "avg_rating",
    "num_reviews",
    "num_lectures",
    "content_length_min",
    "category",
    "subcategory",
    "language",
}
NUMERIC_COLUMNS = [
    "price",
    "avg_rating",
    "num_reviews",
    "num_subscribers",
    "num_lectures",
    "content_length_min",
]
CATEGORICAL_COLUMNS = ["is_paid", "category", "subcategory", "language"]


def parse_courses(file_contents: bytes) -> tuple[pd.DataFrame, dict[str, int]]:
    """Parse CSV bytes, report dropped rows, and reject unusable course files."""
    try:
        courses = pd.read_csv(BytesIO(file_contents), encoding="utf-8")
    except pd.errors.EmptyDataError as error:
        raise ValueError("CSV is empty or has no header row.") from error

    courses.columns = courses.columns.astype(str).str.strip()
    duplicate_columns = courses.columns[courses.columns.duplicated()].unique().tolist()
    if duplicate_columns:
        raise ValueError(f"CSV has duplicate column names: {', '.join(duplicate_columns)}")

    missing_columns = sorted(REQUIRED_COLUMNS.difference(courses.columns))
    if missing_columns:
        raise ValueError(f"CSV is missing required columns: {', '.join(missing_columns)}")

    duplicate_key = "id" if "id" in courses.columns else None
    duplicate_count = int(courses.duplicated(subset=duplicate_key).sum())
    for column in NUMERIC_COLUMNS:
        courses[column] = pd.to_numeric(courses[column], errors="coerce")
    courses[NUMERIC_COLUMNS] = courses[NUMERIC_COLUMNS].replace([np.inf, -np.inf], np.nan)

    invalid_price_count = int((courses["price"].isna() | courses["price"].lt(0)).sum())
    courses = courses.drop_duplicates(subset=duplicate_key).copy()
    courses = courses.loc[courses["price"].notna() & courses["price"].ge(0)].copy()

    for column in CATEGORICAL_COLUMNS:
        courses[column] = courses[column].astype("string").fillna("Unknown")

    if courses.empty:
        raise ValueError("CSV has no courses with a valid, non-negative price.")
    return courses, {
        "duplicate_rows_removed": duplicate_count,
        "invalid_price_rows": invalid_price_count,
    }
