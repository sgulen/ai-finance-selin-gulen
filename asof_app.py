"""Explore FRED data today and as known on an earlier date."""

from __future__ import annotations

import io
import math
import re
from datetime import date

import pandas as pd
import requests
import streamlit as st


SERIES = {
    "BAA": "Moody's Baa corporate bond yield",
    "FEDFUNDS": "Effective federal funds rate",
    "DGS10": "10-year Treasury yield",
    "MORTGAGE30US": "30-year fixed mortgage rate",
}
MONTHLY_SERIES = {"BAA", "FEDFUNDS", "PAYEMS"}
FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"
ALFRED_CSV_URL = "https://alfred.stlouisfed.org/graph/alfredgraph.csv"


def valid_series_id(series_id: str) -> str:
    """Return a safe, normalized FRED series ID."""
    normalized = series_id.strip().upper()
    if not re.fullmatch(r"[A-Z0-9_]{1,40}", normalized):
        raise ValueError("Use a FRED series ID containing only letters, numbers, or underscores.")
    return normalized


def parse_fred_csv(csv_text: str, series_id: str) -> pd.DataFrame:
    """Return usable observation dates and values from a FRED-style CSV response."""
    raw = pd.read_csv(io.StringIO(csv_text))
    if raw.empty or len(raw.columns) < 2:
        raise ValueError(f"FRED did not return observations for {series_id}.")

    date_column = raw.columns[0]
    value_column = raw.columns[1]
    data = raw[[date_column, value_column]].rename(columns={date_column: "date", value_column: "value"})
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data["value"] = pd.to_numeric(data["value"].replace(".", pd.NA), errors="coerce")
    data = data.dropna(subset=["date", "value"]).sort_values("date").reset_index(drop=True)
    if data.empty:
        raise ValueError(f"FRED returned no numeric observations for {series_id}.")
    return data


@st.cache_data(ttl="1h", max_entries=100, show_spinner=False)
def download_today_series(series_id: str) -> pd.DataFrame:
    """Download a series as FRED presents it today."""
    response = requests.get(FRED_CSV_URL, params={"id": valid_series_id(series_id)}, timeout=20)
    response.raise_for_status()
    return parse_fred_csv(response.text, series_id)


@st.cache_data(ttl="1h", max_entries=500, show_spinner=False)
def download_asof_series(series_id: str, vintage_date: str) -> pd.DataFrame:
    """Download the vintage of a series known on ``vintage_date`` from ALFRED."""
    response = requests.get(
        ALFRED_CSV_URL,
        params={"id": valid_series_id(series_id), "vintage_date": vintage_date},
        timeout=20,
    )
    response.raise_for_status()
    return parse_fred_csv(response.text, series_id)


def last_observation(data: pd.DataFrame) -> tuple[pd.Timestamp | None, float | None]:
    """Return the latest date and value, or empty values when a series has no data."""
    if data.empty:
        return None, None
    latest = data.iloc[-1]
    return latest["date"], float(latest["value"])


def display_observation_date(series_id: str, observation_date: pd.Timestamp | None) -> str | None:
    """Use a month label for monthly series and an exact date otherwise."""
    if observation_date is None:
        return None
    if series_id in MONTHLY_SERIES:
        return observation_date.strftime("%B %Y")
    return f"{observation_date.day} {observation_date.strftime('%B %Y')}"


def revised_value_count(today: pd.DataFrame, asof: pd.DataFrame) -> int:
    """Count same-date values that differ between today's and vintage downloads."""
    overlapping = today.merge(asof, on="date", how="inner", suffixes=("_today", "_asof"))
    return sum(
        not math.isclose(float(row.value_today), float(row.value_asof), rel_tol=1e-10, abs_tol=1e-10)
        for row in overlapping.itertuples()
    )


def table_row(series_id: str, today: pd.DataFrame, asof: pd.DataFrame) -> dict[str, object]:
    """Build one comparison-table record for a successfully downloaded series."""
    asof_date, asof_value = last_observation(asof)
    today_date, today_value = last_observation(today)
    values_later = int((today["date"] > asof_date).sum()) if asof_date is not None else None
    return {
        "Series ID": f"https://fred.stlouisfed.org/series/{series_id}",
        "Last date known then": display_observation_date(series_id, asof_date),
        "Value known then": asof_value,
        "Last date measured today": display_observation_date(series_id, today_date),
        "Value today": today_value,
        "Values published later": values_later,
        "Same-date values revised": revised_value_count(today, asof),
    }


st.set_page_config(page_title="FRED as-of audit", layout="wide")
st.title("FRED as-of audit")
st.caption(
    "Data from FRED and ALFRED, Federal Reserve Bank of St. Louis, downloaded today; "
    "built with AI help, a learning demonstration, not investment advice."
)
st.markdown(
    "Sources: [FRED](https://fred.stlouisfed.org/) and "
    "[ALFRED](https://alfred.stlouisfed.org/)."
)

with st.sidebar:
    st.header("Inputs")
    selected_series = st.multiselect(
        "Series",
        options=list(SERIES),
        default=list(SERIES),
        format_func=lambda series_id: f"{series_id} — {SERIES[series_id]}",
        help="Each selected series is downloaded once from FRED and once from ALFRED.",
    )
    additional_series = st.text_input(
        "Add another FRED series ID",
        placeholder="For example, T10Y2Y",
        help="The ID is the code at the end of the series' FRED page address.",
    )
    start_date = st.date_input("Start date", value=date(2020, 1, 1))
    asof_date = st.date_input("As known on", value=date.today())

if additional_series.strip():
    try:
        additional_id = valid_series_id(additional_series)
        if additional_id not in selected_series:
            selected_series.append(additional_id)
    except ValueError as error:
        st.sidebar.error(str(error))

if not selected_series:
    st.info("Select at least one FRED series to begin.")
    st.stop()

st.caption(f"Comparing information available on {asof_date.isoformat()} with the latest FRED download.")
comparison_rows = []

for series_id in selected_series:
    try:
        today_data = download_today_series(series_id)
        asof_data = download_asof_series(series_id, asof_date.isoformat())
    except (requests.RequestException, ValueError, pd.errors.ParserError) as error:
        st.error(f"{series_id}: {error}")
        continue

    display_data = today_data[today_data["date"].dt.date >= start_date]
    st.subheader(f"{series_id} — {SERIES.get(series_id, 'Custom FRED series')}")
    if display_data.empty:
        st.warning(f"{series_id} has no current observations on or after {start_date.isoformat()}.")
    else:
        st.line_chart(
            display_data,
            x="date",
            y="value",
            x_label="Observation date",
            y_label="Value",
            height=320,
            alt=f"Current FRED observations for {series_id} from {start_date.isoformat()}.",
        )
    known_date, known_value = last_observation(asof_data)
    if known_date is not None:
        st.caption(
            f"Last observation known on {asof_date.isoformat()}: "
            f"{display_observation_date(series_id, known_date)} = {known_value:.4g}"
        )
    comparison_rows.append(table_row(series_id, today_data, asof_data))

st.subheader("As-of comparison")
if comparison_rows:
    comparison = pd.DataFrame(comparison_rows)
    st.dataframe(
        comparison,
        hide_index=True,
        column_config={
            "Series ID": st.column_config.LinkColumn(
                "Series ID",
                display_text=r"https://fred\.stlouisfed\.org/series/(.*)",
            ),
            "Value known then": st.column_config.NumberColumn(format="%.4f"),
            "Value today": st.column_config.NumberColumn(format="%.4f"),
            "Values published later": st.column_config.NumberColumn(format="%d"),
            "Same-date values revised": st.column_config.NumberColumn(format="%d"),
        },
        alt="Comparison of last available FRED and ALFRED observations for each selected series.",
    )
else:
    st.warning("No selected series could be downloaded. Check the IDs and try again.")
