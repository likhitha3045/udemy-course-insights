# Udemy Course Data Analysis

An exploratory data analysis and baseline regression project using Udemy course metadata. The notebook examines course pricing, ratings, course length, and student engagement, then evaluates a linear regression model for course price.

## Interactive dashboard

The Streamlit app adds catalog filters, interactive price and engagement charts, a searchable course explorer, data-quality summaries, and an optional linear regression price estimate compared with a median-price baseline.

Run the app from the project directory:

```bash
streamlit run app.py
```

The dashboard works immediately with clearly labeled synthetic demo data. For actual analysis, upload `Course_info.csv` in the sidebar, or put it at `data/Course_info.csv` before starting the app.

## Project highlights

- Audits missing values, duplicates, data types, and summary statistics.
- Visualizes course prices, ratings, and category-level subscriber counts.
- Compares a linear regression model with a simple median-price baseline.
- Reports MAE, RMSE, and R-squared on a held-out test set.
- Provides an interactive Streamlit dashboard for exploring and filtering the catalog.
- Includes a small synthetic sample so the dashboard can be previewed without downloading the source dataset.
- Keeps the source dataset out of the repository; provide it locally to run the notebook.

## Repository contents

| File | Description |
| --- | --- |
| [`app.py`](./app.py) | Interactive Streamlit dashboard |
| [`data_validation.py`](./data_validation.py) | CSV parsing and validation shared by the app and checks |
| [`DATA_DICTIONARY.md`](./DATA_DICTIONARY.md) | Required fields, meanings, and data handling rules |
| [`DEPLOYMENT.md`](./DEPLOYMENT.md) | Create a GitHub repository and deploy the dashboard |
| [`data/sample_courses.csv`](./data/sample_courses.csv) | Synthetic demo data for previewing the dashboard |
| [`udemy-2.ipynb`](./udemy-2.ipynb) | Data preparation, exploratory analysis, visualizations, and regression |
| [`requirements.txt`](./requirements.txt) | Python dependencies |
| [`tests/test_data_validation.py`](./tests/test_data_validation.py) | Standard-library checks for CSV validation behavior |
| [`LICENSE`](./LICENSE) | MIT license for the project code |

## Dataset

The original dataset is not included in this repository. The dashboard starts with clearly labeled synthetic demo data; the notebook expects a real `Course_info.csv`. The original [Kaggle notebook](https://www.kaggle.com/code/krishna0000007/udemy-2) is the project's dataset reference; check its current access and usage terms before downloading or redistributing data.

Create the data folder and place the CSV at:

```text
data/Course_info.csv
```

The analysis uses course price, paid status, category, subcategory, language, number of lectures, course length, ratings, reviews, and subscriber counts. The notebook checks for the columns it needs and reports any missing fields.

## Run locally

Requires Python 3.10 or newer.

1. Clone the repository and move into the project directory.
2. (Recommended) Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Add the dataset at `data/Course_info.csv`.
5. Launch Jupyter and open the notebook:

   ```bash
   jupyter notebook
   ```

6. Run all cells in `udemy-2.ipynb` from top to bottom.

## Modeling notes

The notebook uses course metadata (paid status, category, subcategory, language, lecture count, and course length) to predict price. Categorical and numeric features are preprocessed in a scikit-learn pipeline, and a fixed random seed makes the train/test split reproducible. Ratings, reviews, and subscriber counts are analyzed but excluded from the price model.

The model is a baseline for practice, not a pricing recommendation. Its performance depends on the dataset snapshot and should be interpreted alongside the held-out baseline metrics.

## CSV validation checks

The dashboard rejects empty files, missing required fields, and duplicate column names. It drops duplicate course rows and rows with invalid prices, converts other invalid numeric values to missing, and labels missing categories `Unknown`. See the [data dictionary](./DATA_DICTIONARY.md) for field details.

Run the built-in checks from the project directory with:

```bash
python -m unittest discover -s tests
```

The MIT license applies to the project code; dataset usage terms are set by the dataset's original source.
