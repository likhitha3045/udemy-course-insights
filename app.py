from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from data_validation import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS, parse_courses


DATA_PATH = Path("data") / "Course_info.csv"
SAMPLE_DATA_PATH = Path("data") / "sample_courses.csv"
NUMERIC_FEATURES = ["num_lectures", "content_length_min"]
CATEGORICAL_FEATURES = CATEGORICAL_COLUMNS


st.set_page_config(
    page_title="Udemy Course Insights",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #17233c;
        --muted: #64748b;
        --accent: #6b5cff;
        --surface: #ffffff;
    }

    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        color: var(--ink);
    }

    .stApp {
        background:
            radial-gradient(ellipse at 82% 0%, rgba(107, 92, 255, 0.10), transparent 34rem),
            #f6f7fb;
    }

    [data-testid="stSidebar"] {
        background: #10172a;
        color: #e8ebf5;
    }

    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #e8ebf5;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #17233c;
    }

    [data-testid="stSidebar"] [data-testid="stFileUploader"] section {
        background: rgba(255,255,255,.07);
        border: 1px dashed rgba(255,255,255,.30);
    }

    [data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid #e8eaf2;
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 5px 20px rgba(27, 38, 67, 0.045);
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted);
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: var(--ink);
        font-family: 'Segoe UI', sans-serif;
        font-weight: 800;
    }

    h1, h2, h3 {
        font-family: 'Segoe UI', sans-serif !important;
        letter-spacing: -0.035em;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: var(--accent);
        border-bottom-color: var(--accent);
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(110deg, #6b5cff, #907bff);
        border: 0;
        border-radius: 10px;
        font-weight: 700;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #e8eaf2;
        border-radius: 12px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_courses(file_contents: bytes) -> tuple[pd.DataFrame, dict[str, int]]:
    """Parse CSV bytes once, so changing dashboard controls doesn't reload the file."""
    return parse_courses(file_contents)


@st.cache_data(show_spinner=False)
def evaluate_price_model(courses: pd.DataFrame) -> tuple[Any, dict[str, float], pd.DataFrame]:
    """Train and evaluate a price model against a median-price baseline."""
    features = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    X = courses[features]
    y = courses["price"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", LinearRegression()),
        ]
    )
    baseline = DummyRegressor(strategy="median")
    model.fit(X_train, y_train)
    baseline.fit(X_train, y_train)
    model_predictions = model.predict(X_test)
    baseline_predictions = baseline.predict(X_test)

    metrics = {
        "model_mae": float(mean_absolute_error(y_test, model_predictions)),
        "model_rmse": float(np.sqrt(mean_squared_error(y_test, model_predictions))),
        "model_r2": float(r2_score(y_test, model_predictions)),
        "baseline_mae": float(mean_absolute_error(y_test, baseline_predictions)),
    }
    predictions = pd.DataFrame(
        {"Actual price": y_test.to_numpy(), "Predicted price": model_predictions}
    )
    return model, metrics, predictions


def show_data_quality(courses: pd.DataFrame) -> None:
    missing = courses[NUMERIC_COLUMNS].isna().sum()
    for column in CATEGORICAL_FEATURES:
        missing.loc[column] = courses[column].eq("Unknown").sum()
    missing_rows = missing[missing.gt(0)]
    if missing_rows.empty:
        st.success("No missing values in the analyzed fields.")
        return

    quality = pd.DataFrame(
        {
            "Field": missing_rows.index,
            "Missing values": missing_rows.values,
            "Missing %": (missing_rows.values / len(courses) * 100).round(1),
        }
    )
    st.dataframe(quality, hide_index=True, width="stretch")


st.sidebar.markdown("## 📚 Course insights")
st.sidebar.caption("Explore course pricing and learner engagement")
uploaded_file = st.sidebar.file_uploader("Upload course data", type=["csv"])

if uploaded_file is not None:
    file_contents = uploaded_file.getvalue()
    source_label = uploaded_file.name
elif DATA_PATH.is_file():
    file_contents = DATA_PATH.read_bytes()
    source_label = str(DATA_PATH)
    sample_data = False
elif SAMPLE_DATA_PATH.is_file():
    file_contents = SAMPLE_DATA_PATH.read_bytes()
    source_label = "Built-in synthetic demo data"
    sample_data = True
else:
    st.title("Udemy Course Insights")
    st.markdown("### Turn course data into a clearer picture.")
    st.info(
        "Upload a `Course_info.csv` file in the sidebar, or add it to "
        "`data/Course_info.csv` and refresh this page."
    )
    st.markdown(
        "The dashboard includes interactive category and price filters, "
        "course-market charts, data-quality checks, and an evaluated price-prediction baseline."
    )
    st.stop()

if uploaded_file is not None:
    sample_data = False

try:
    raw_courses, quality_summary = load_courses(file_contents)
except (UnicodeDecodeError, pd.errors.ParserError, ValueError) as error:
    st.error(f"Could not load course data: {error}")
    st.stop()

st.sidebar.caption(f"Source: `{source_label}`")
st.sidebar.divider()
st.sidebar.markdown("### Filter the catalog")

categories = sorted(raw_courses["category"].unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Categories",
    categories,
    default=categories,
    help="Clear the selection to show no categories.",
)

paid_options = sorted(raw_courses["is_paid"].unique().tolist())
selected_paid_status = st.sidebar.multiselect(
    "Paid status",
    paid_options,
    default=paid_options,
)

minimum_price = float(raw_courses["price"].min())
maximum_price = float(raw_courses["price"].max())
if minimum_price < maximum_price:
    selected_price_range = st.sidebar.slider(
        "Course price",
        min_value=minimum_price,
        max_value=maximum_price,
        value=(minimum_price, maximum_price),
        step=max((maximum_price - minimum_price) / 100, 0.01),
        format="%.2f",
    )
else:
    selected_price_range = (minimum_price, maximum_price)
    st.sidebar.caption(f"All courses have the same price: {minimum_price:g}")

filtered_courses = raw_courses.loc[
    raw_courses["category"].isin(selected_categories)
    & raw_courses["is_paid"].isin(selected_paid_status)
    & raw_courses["price"].between(*selected_price_range)
].copy()

st.title("Udemy Course Insights")
if sample_data:
    st.caption(
        "Demo data (synthetic) · Upload your `Course_info.csv` in the sidebar to explore "
        "the real dataset."
    )
st.markdown(
    f"**Explore the catalog. Spot the patterns.** &nbsp; · &nbsp; "
    f"Showing {len(filtered_courses):,} of {len(raw_courses):,} courses"
)

if filtered_courses.empty:
    st.warning("No courses match the current filters. Adjust the sidebar filters to continue.")
    st.stop()

total_subscribers = filtered_courses["num_subscribers"].fillna(0).sum()
average_rating = filtered_courses["avg_rating"].mean()
median_price = filtered_courses["price"].median()
average_rating_text = f"{average_rating:.2f} / 5" if pd.notna(average_rating) else "N/A"

metric_columns = st.columns(4)
metric_columns[0].metric("Courses", f"{len(filtered_courses):,}")
metric_columns[1].metric("Median price", f"{median_price:,.2f}")
metric_columns[2].metric("Average rating", average_rating_text)
metric_columns[3].metric("Subscribers", f"{total_subscribers:,.0f}")

overview_tab, catalog_tab, model_tab, quality_tab = st.tabs(
    ["Overview", "Course explorer", "Price model", "Data quality"]
)

with overview_tab:
    st.subheader("Market overview")
    left, right = st.columns(2)

    with left:
        price_data = filtered_courses.loc[filtered_courses["price"].notna()]
        price_figure = px.histogram(
            price_data,
            x="price",
            nbins=35,
            color_discrete_sequence=["#6b5cff"],
            title="How course prices are distributed",
            labels={"price": "Course price", "count": "Courses"},
        )
        price_figure.update_layout(
            bargap=0.08,
            plot_bgcolor="white",
            paper_bgcolor="white",
            title_font_size=16,
            margin=dict(l=12, r=12, t=55, b=12),
        )
        st.plotly_chart(price_figure, width="stretch")

    with right:
        rating_data = filtered_courses.loc[filtered_courses["avg_rating"].notna()]
        rating_figure = px.histogram(
            rating_data,
            x="avg_rating",
            nbins=25,
            color_discrete_sequence=["#26a69a"],
            title="Course rating distribution",
            labels={"avg_rating": "Average rating", "count": "Courses"},
        )
        rating_figure.update_layout(
            bargap=0.08,
            plot_bgcolor="white",
            paper_bgcolor="white",
            title_font_size=16,
            margin=dict(l=12, r=12, t=55, b=12),
        )
        st.plotly_chart(rating_figure, width="stretch")

    left, right = st.columns(2)
    category_subscribers = (
        filtered_courses.groupby("category", dropna=False)["num_subscribers"]
        .sum(min_count=1)
        .nlargest(10)
        .sort_values()
        .rename_axis("category")
        .reset_index(name="subscribers")
    )
    with left:
        subscribers_figure = px.bar(
            category_subscribers,
            x="subscribers",
            y="category",
            orientation="h",
            title="Top categories by subscribers",
            labels={"subscribers": "Subscribers", "category": ""},
            color_discrete_sequence=["#6b5cff"],
        )
        subscribers_figure.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            title_font_size=16,
            margin=dict(l=12, r=12, t=55, b=12),
        )
        st.plotly_chart(subscribers_figure, width="stretch")

    median_prices = (
        filtered_courses.groupby("category")["price"]
        .median()
        .nlargest(10)
        .sort_values()
        .rename_axis("category")
        .reset_index(name="median_price")
    )
    with right:
        category_price_figure = px.bar(
            median_prices,
            x="median_price",
            y="category",
            orientation="h",
            title="Categories with the highest median price",
            labels={"median_price": "Median price", "category": ""},
            color_discrete_sequence=["#ff9b62"],
        )
        category_price_figure.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            title_font_size=16,
            margin=dict(l=12, r=12, t=55, b=12),
        )
        st.plotly_chart(category_price_figure, width="stretch")

with catalog_tab:
    st.subheader("Course explorer")
    search = st.text_input("Search course titles", placeholder="Try a topic or keyword")
    catalog = filtered_courses.copy()
    if search and "title" in catalog.columns:
        catalog = catalog.loc[
            catalog["title"].astype("string").str.contains(search, case=False, na=False)
        ]

    preferred_columns = [
        "title",
        "category",
        "subcategory",
        "price",
        "avg_rating",
        "num_subscribers",
        "num_reviews",
        "num_lectures",
        "language",
    ]
    visible_columns = [column for column in preferred_columns if column in catalog.columns]
    st.caption(f"{len(catalog):,} matching courses")
    st.dataframe(
        catalog[visible_columns].sort_values("num_subscribers", ascending=False),
        hide_index=True,
        width="stretch",
        height=520,
    )

    csv_download = catalog.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered courses",
        data=csv_download,
        file_name="filtered_udemy_courses.csv",
        mime="text/csv",
    )

with model_tab:
    st.subheader("Can course metadata help estimate price?")
    st.markdown(
        "Compare a linear regression model to a median-price baseline on a held-out test set. "
        "The model uses paid status, category, subcategory, language, lecture count, and course length."
    )
    st.caption(
        "Ratings, reviews, and subscribers are intentionally excluded. "
        "Results are descriptive and are not a pricing recommendation."
    )

    if len(filtered_courses) < 10:
        st.info("At least 10 courses must match the current filters to evaluate the model.")
    else:
        model_data_key = hashlib.sha256(
            pd.util.hash_pandas_object(filtered_courses, index=True).values.tobytes()
        ).hexdigest()
        if st.button("Evaluate price model", type="primary"):
            with st.spinner("Training and evaluating on the filtered courses..."):
                try:
                    model_result = evaluate_price_model(filtered_courses)
                except ValueError as error:
                    st.error(f"Could not evaluate the model: {error}")
                else:
                    st.session_state["price_model_result"] = (
                        model_data_key,
                        model_result,
                    )

        saved_model = st.session_state.get("price_model_result")
        if saved_model is not None and saved_model[0] == model_data_key:
            model, metrics, predictions = saved_model[1]
            model_metrics = st.columns(3)
            model_metrics[0].metric("Model MAE", f"{metrics['model_mae']:,.2f}")
            model_metrics[1].metric("Model RMSE", f"{metrics['model_rmse']:,.2f}")
            model_metrics[2].metric("Model R²", f"{metrics['model_r2']:.3f}")
            st.metric("Median baseline MAE", f"{metrics['baseline_mae']:,.2f}")

            prediction_figure = px.scatter(
                predictions,
                x="Actual price",
                y="Predicted price",
                opacity=0.65,
                title="Actual vs. predicted prices",
                color_discrete_sequence=["#6b5cff"],
            )
            axis_min = min(
                float(predictions["Actual price"].min()),
                float(predictions["Predicted price"].min()),
            )
            axis_max = max(
                float(predictions["Actual price"].max()),
                float(predictions["Predicted price"].max()),
            )
            prediction_figure.add_trace(
                go.Scatter(
                    x=[axis_min, axis_max],
                    y=[axis_min, axis_max],
                    mode="lines",
                    name="Perfect estimate",
                    line=dict(color="#64748b", dash="dash"),
                )
            )
            prediction_figure.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                title_font_size=16,
            )
            st.plotly_chart(prediction_figure, width="stretch")

            st.markdown("#### Try a course profile")
            with st.form("price_prediction_form"):
                input_columns = st.columns(2)
                category_value = input_columns[0].selectbox(
                    "Category", sorted(filtered_courses["category"].unique())
                )
                subcategory_value = input_columns[1].selectbox(
                    "Subcategory", sorted(filtered_courses["subcategory"].unique())
                )
                language_value = input_columns[0].selectbox(
                    "Language", sorted(filtered_courses["language"].unique())
                )
                paid_value = input_columns[1].selectbox(
                    "Paid course", sorted(filtered_courses["is_paid"].unique())
                )
                lecture_count = input_columns[0].number_input(
                    "Number of lectures", min_value=0, value=20, step=1
                )
                course_length = input_columns[1].number_input(
                    "Content length (minutes)", min_value=0, value=300, step=30
                )
                predict_submitted = st.form_submit_button("Estimate course price")

            if predict_submitted:
                course_profile = pd.DataFrame(
                    [
                        {
                            "num_lectures": lecture_count,
                            "content_length_min": course_length,
                            "is_paid": paid_value,
                            "category": category_value,
                            "subcategory": subcategory_value,
                            "language": language_value,
                        }
                    ]
                )
                estimated_price = float(model.predict(course_profile)[0])
                st.success(
                    f"Estimated price: **{max(estimated_price, 0):,.2f}** "
                    "(dataset price units)"
                )
                if estimated_price < 0:
                    st.caption(
                        "The raw linear estimate was negative and is displayed as zero; "
                        "linear regression does not constrain predictions to valid prices."
                    )

with quality_tab:
    st.subheader("Data quality")
    st.caption(
        "Missing categorical values are labeled Unknown. Duplicate and invalid-price "
        "counts are measured before those rows are removed."
    )
    show_data_quality(filtered_courses)
    quality_left, quality_right = st.columns(2)
    with quality_left:
        st.metric("Rows with usable prices", f"{len(raw_courses):,}")
        st.metric("Duplicate entries removed", f"{quality_summary['duplicate_rows_removed']:,}")
    with quality_right:
        st.metric(
            "Rows with missing or invalid price",
            f"{quality_summary['invalid_price_rows']:,}",
        )

st.divider()
st.caption(
    "Udemy Course Insights · Explore the data, not a financial recommendation. "
    "Dataset availability and usage terms depend on its original source."
)
