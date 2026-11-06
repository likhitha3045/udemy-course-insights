# Data dictionary

The dashboard expects a CSV with the required fields below. Extra columns are kept and may appear in the course explorer. Column names are trimmed before validation.

| Column | Type | Meaning / handling |
| --- | --- | --- |
| `id` | Optional identifier | When present, repeated IDs are treated as duplicate rows; the first row is kept. Without it, identical full rows are treated as duplicates. |
| `title` | Optional text | Course title; used by the explorer's title search when present. |
| `is_paid` | Required category | Whether the course is paid; values are retained as supplied and used as a dashboard filter/model feature. |
| `price` | Required number | Course price in the dataset's units. Rows with missing, nonnumeric, infinite, or negative prices are removed. |
| `num_subscribers` | Required number | Subscriber count. Nonnumeric values become missing; the dashboard treats missing counts as zero when totaling subscribers. |
| `avg_rating` | Required number | Average course rating. Nonnumeric values become missing; displayed as an average when available. |
| `num_reviews` | Required number | Number of reviews. Nonnumeric values become missing. |
| `num_lectures` | Required number | Number of course lectures. Nonnumeric values become missing and are imputed for modeling. |
| `content_length_min` | Required number | Total course content length in minutes. Nonnumeric values become missing and are imputed for modeling. |
| `category` | Required category | Broad course topic; missing values are labeled `Unknown`. |
| `subcategory` | Required category | More specific course topic; missing values are labeled `Unknown`. |
| `language` | Required category | Course language; missing values are labeled `Unknown`. |

Required columns must be present even when a particular chart does not use every field. Invalid values in required numeric columns other than `price` are retained as missing and reported in the dashboard's Data quality tab. The price model uses paid status, category, subcategory, language, lecture count, and course length; ratings, reviews, and subscribers are excluded.
