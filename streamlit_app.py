"""Slide-deck walkthrough of the NYC Green Taxi ETL pipeline.

Reads real snippets straight out of src/data_pipeline/* and tests/* so the
deck can never drift out of sync with the actual pipeline code.
"""

from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent


def snippet(relative_path: str, start_line: int, end_line: int) -> str:
    """Return lines [start_line, end_line] (1-indexed, inclusive) of a project file."""
    lines = (ROOT / relative_path).read_text().splitlines()
    return "\n".join(lines[start_line - 1 : end_line])


def whole_file(relative_path: str) -> str:
    """Return the full contents of a project file, stripped of trailing blank lines."""
    return (ROOT / relative_path).read_text().rstrip()


st.set_page_config(
    page_title="ETL pipeline for NYC Green Taxi trip data",
    page_icon=":material/route:",
    layout="centered",
)

st.session_state.setdefault("slide", 0)


def go_previous() -> None:
    st.session_state.slide = max(0, st.session_state.slide - 1)


def go_next() -> None:
    st.session_state.slide = min(len(SLIDES) - 1, st.session_state.slide + 1)


# ---------------------------------------------------------------------------
# Slide content
# ---------------------------------------------------------------------------


def slide_title() -> None:
    st.title("ETL pipeline for NYC Green Taxi trip data", text_alignment="center")
    st.caption(
        "MOD2 data pipeline project — extract, transform, load",
        text_alignment="center",
    )
    st.space("large")
    with st.container(horizontal_alignment="center"):
        st.markdown(":material/route: :material/arrow_forward: :material/functions: :material/arrow_forward: :material/save:")
    st.space("large")
    with st.container(border=True):
        st.markdown(
            "This deck walks through how raw taxi trip records become a "
            "**daily revenue summary**, stage by stage, using the actual "
            "code and results from this project."
        )


def slide_brief() -> None:
    st.header("The project brief", icon=":material/description:")
    st.markdown(
        "Build a pipeline that processes the **Green Taxi Trips** portion "
        "of the NYC Taxi Trip dataset."
    )
    st.markdown("**Two required steps:**")
    st.markdown(
        "1. Download the first three months of 2025 into a local staging directory.\n"
        "2. Write an ETL or ELT pipeline that reads the staged files, processes "
        "the data, and calculates **revenue per day**."
    )
    st.markdown("**Bonus:** orchestrate the pipeline with Prefect.")
    st.space("medium")
    st.caption("Learning objectives")
    for objective in [
        "Download a public dataset into a local staging directory",
        "Aggregate staged Parquet files into daily metrics",
        "Separate the pipeline into distinct extract, transform, and load stages",
        "Explain ETL vs ELT, and justify the choice made here",
        "Orchestrate the pipeline with Prefect (stretch goal)",
    ]:
        st.checkbox(objective, value=True, disabled=True)


def slide_extract() -> None:
    st.header("Stage 1 — Extract", icon=":material/cloud_download:")
    st.markdown(
        "Its only job: get the raw Parquet files from the public source onto "
        "local disk, **unchanged**. It never looks at the data's contents."
    )
    st.code(snippet("src/data_pipeline/extract.py", 15, 29), language="python")
    st.markdown(
        "Streamed in 1MB chunks so large files never have to sit fully in "
        "memory, and skipped entirely if the file is already staged."
    )
    with st.container(border=True):
        st.markdown(
            "**Result:** `data/raw/green_tripdata_2025-01.parquet`, `-02`, `-03` "
            "— three untouched source files, the staging directory."
        )


def slide_transform() -> None:
    st.header("Stage 2 — Transform", icon=":material/functions:")
    st.markdown(
        "Runs entirely in memory with pandas — no network, no database. "
        "A pure function in, a pure function out, which is what makes it "
        "unit-testable without any files at all."
    )
    st.code(snippet("src/data_pipeline/transform.py", 26, 46), language="python")
    st.markdown(
        "Negative and zero `total_amount` rows (refunds, comped rides) are "
        "kept **as-is** — a documented decision, not an oversight, so daily "
        "revenue reflects *net* revenue rather than gross fares."
    )


def slide_load() -> None:
    st.header("Stage 3 — Load", icon=":material/save:")
    st.markdown(
        "Takes the already-finished daily revenue table and persists it. "
        "No computation happens here."
    )
    st.code(snippet("src/data_pipeline/load.py", 19, 41), language="python")
    with st.container(border=True):
        st.markdown(
            "**Result:** `data/processed/daily_revenue.csv`, "
            "`daily_revenue.parquet`, and `pipeline_metadata.json`."
        )


def slide_pipeline() -> None:
    st.header("Wiring it together", icon=":material/linear_scale:")
    st.markdown(
        "`pipeline.py` calls the three stages in strict order — this order "
        "is exactly what makes the pipeline **ETL**, not ELT."
    )
    st.code(snippet("src/data_pipeline/pipeline.py", 11, 15), language="python")
    st.markdown("**Folder roles:**")
    col_raw, col_processed = st.columns(2)
    with col_raw.container(border=True):
        st.markdown("**`data/raw/`**")
        st.caption("Staging area — untouched source files, boundary between Extract and Transform")
    with col_processed.container(border=True):
        st.markdown("**`data/processed/`**")
        st.caption("Destination — finished output, boundary between Load and any consumer")
    st.space("medium")
    st.caption("Entry point: `uv run python scripts/run_pipeline.py`")


def slide_etl_vs_elt() -> None:
    st.header("ETL vs ELT", icon=":material/compare_arrows:")
    st.markdown("The difference comes down to **where the transform runs**, relative to the destination.")
    st.table(
        {
            "": ["Order", "Where \"T\" runs", "What reaches the destination", "Destination needed"],
            "ETL (this pipeline)": [
                "Extract → Transform → Load",
                "In the pipeline (pandas, in memory)",
                "Already-finished, aggregated result",
                "None — flat files are enough",
            ],
            "ELT (the alternative)": [
                "Extract → Load → Transform",
                "Inside the destination (SQL / dbt)",
                "Raw, unaggregated rows",
                "A queryable store (e.g. Postgres)",
            ],
        }
    )
    st.markdown(
        "**Why ETL was chosen:** the destination here is a folder of flat "
        "files, which has no compute engine of its own — there's nowhere "
        "for a `GROUP BY` to run *after* loading. So the transform has to "
        "happen before the load, which is ETL by definition."
    )
    st.caption(
        "sqlalchemy, psycopg2-binary and dbt-postgres are already project "
        "dependencies — an ELT variant loading raw rows into Postgres and "
        "aggregating with a dbt model would be a valid extension."
    )


def slide_code_comparison() -> None:
    st.header("Python (ETL) vs SQL (ELT)", icon=":material/code_blocks:")
    st.markdown(
        "Both pipelines are real and runnable, and produce the **exact same "
        "result** — 94 rows, $3,395,595.29 total revenue, verified row by "
        "row. Only *where* the aggregation runs differs."
    )
    col_etl, col_elt = st.columns(2)
    with col_etl:
        st.markdown("**ETL — pandas, in Python**")
        st.caption("src/data_pipeline/transform.py")
        st.code(snippet("src/data_pipeline/transform.py", 35, 46), language="python")
    with col_elt:
        st.markdown("**ELT — SQL, inside the warehouse**")
        st.caption("src/data_pipeline/elt/sql/daily_revenue.sql")
        st.code(whole_file("src/data_pipeline/elt/sql/daily_revenue.sql"), language="sql")
    st.markdown(
        "The `GROUP BY` is doing identical work in both — same grouping key "
        "(pickup date), same measures (summed revenue, trip count), same "
        "policy of leaving negative/zero amounts in the sum. The pandas "
        "version runs the moment `compute_daily_revenue()` is called in "
        "Python; the SQL version only runs once the raw rows already sit in "
        "a table, executed by `connection.executescript(...)` in "
        "`src/data_pipeline/elt/pipeline.py`."
    )
    st.info(
        "This project runs the `.sql` file directly for simplicity. In a "
        "production ELT setup, that same query would normally live as a "
        "**dbt model** instead of a raw script — dbt gives it version "
        "control, `dbt test` assertions (e.g. \"total_amount is never "
        "null\"), auto-generated documentation, and a dependency graph if "
        "more models were added later. The SQL logic itself wouldn't "
        "change — dbt would just manage *how* and *when* it runs, the same "
        "role Prefect plays for the Python side on the next slides.",
        icon=":material/schema:",
    )
    with st.container(border=True):
        st.markdown(
            "**What changed to get from ETL to ELT:** `extract.py` was "
            "reused unchanged. A new `load_raw.py` writes every raw column "
            "straight into a SQLite table *before* any transform runs. The "
            "`.sql` file above replaces `compute_daily_revenue()` entirely. "
            "The original ETL files were not modified — both pipelines "
            "coexist, run independently, and can be compared directly."
        )
    st.caption("Run the ELT version with: `uv run python scripts/run_elt_pipeline.py`")


def slide_testing() -> None:
    st.header("Testing the transform stage", icon=":material/verified:")
    st.markdown(
        "Because `compute_daily_revenue` is a pure function, it can be "
        "tested against a tiny hand-built DataFrame — no downloads, no "
        "files, no database."
    )
    st.code(snippet("tests/test_transform.py", 11, 29), language="python")
    st.markdown("Run with:")
    st.code("uv run pytest tests -v", language="bash")
    st.warning(
        "Coverage note: only `transform.py` has unit tests today. "
        "`extract.py` and `load.py` are exercised only by running the full "
        "pipeline end-to-end, not by isolated tests.",
        icon=":material/info:",
    )


def slide_prefect() -> None:
    st.header("Stretch goal — orchestrating with Prefect", icon=":material/schema:")
    st.badge("Not yet built", icon=":material/schedule:", color="orange")
    st.markdown(
        "Prefect is a Python-native **workflow orchestrator** — it wraps "
        "existing functions with `@task`, groups them into a `@flow`, and "
        "in return gives you automatic retries, a run dashboard, caching, "
        "and scheduling."
    )
    st.markdown(
        "Because extract/transform/load are already separate, plain "
        "functions, adding Prefect would only mean decorating the calls "
        "already made in `pipeline.py` — no change to the logic inside them:"
    )
    st.code(
        '''@task
def extract_task(months):
    return download_months(months)

@task
def transform_task(raw_files):
    trips = read_staged_trips(raw_files)
    return compute_daily_revenue(trips)

@task
def load_task(daily_revenue):
    return write_daily_revenue(daily_revenue)

@flow(name="green-taxi-pipeline")
def pipeline_flow():
    raw_files = extract_task(MONTHS)
    daily_revenue = transform_task(raw_files)
    return load_task(daily_revenue)''',
        language="python",
    )
    st.caption("Proposed extension shown for illustration — the pipeline currently runs without an orchestrator.")


def slide_results() -> None:
    st.header("Results", icon=":material/bar_chart:")
    col1, col2, col3 = st.columns(3)
    col1.metric("Days covered", "94")
    col2.metric("Date range", "Dec 25 – Apr 1")
    col3.metric("Total revenue", "$3.40M")
    st.space("medium")
    st.markdown("**Output files in `data/processed/`:**")
    st.markdown(
        "- `daily_revenue.csv` — human-readable daily table\n"
        "- `daily_revenue.parquet` — same table, columnar format\n"
        "- `pipeline_metadata.json` — run summary (row count, date range, total revenue)"
    )
    st.space("medium")
    with st.container(border=True):
        st.markdown(
            "**Recap:** extract, transform, and load are cleanly separated; "
            "the ETL choice is justified by the destination having no "
            "compute engine of its own; the transform stage is unit-tested "
            "in isolation; and Prefect orchestration remains as the "
            "documented next step."
        )


SLIDES = [
    ("Title", slide_title),
    ("Brief", slide_brief),
    ("Extract", slide_extract),
    ("Transform", slide_transform),
    ("Load", slide_load),
    ("Pipeline", slide_pipeline),
    ("ETL vs ELT", slide_etl_vs_elt),
    ("Code comparison", slide_code_comparison),
    ("Testing", slide_testing),
    ("Prefect", slide_prefect),
    ("Results", slide_results),
]

# ---------------------------------------------------------------------------
# Render current slide + navigation
# ---------------------------------------------------------------------------

st.progress((st.session_state.slide + 1) / len(SLIDES))

with st.container(border=True):
    SLIDES[st.session_state.slide][1]()

st.space("medium")

with st.container(horizontal=True, horizontal_alignment="distribute"):
    st.button(
        "Previous",
        icon=":material/arrow_back:",
        on_click=go_previous,
        disabled=st.session_state.slide == 0,
    )
    st.caption(f"Slide {st.session_state.slide + 1} of {len(SLIDES)} — {SLIDES[st.session_state.slide][0]}")
    st.button(
        "Next",
        icon=":material/arrow_forward:",
        on_click=go_next,
        disabled=st.session_state.slide == len(SLIDES) - 1,
    )
