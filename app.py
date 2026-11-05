"""Interactive portfolio search app for the Meridian exercise."""

import io

import streamlit as st

from portfolio import (
    CORRELATIONS,
    OBJECTIVE_RETURN,
    RESERVE_ELIGIBLE,
    SLEEVES,
    estimate_from_prices,
    search_lowest_risk_mix,
)


def make_sleeves(names, expected_returns, volatilities):
    return [
        {"name": name, "expected_return": expected_returns[name], "volatility": volatilities[name]}
        for name in names
    ]


def result_panel(result):
    if result is None:
        st.warning("No mix meets the objective.")
        return
    st.dataframe(
        {"Asset": list(result["weights"]), "Weight": [f"{weight:.0%}" for weight in result["weights"].values()]},
        hide_index=True,
        width="stretch",
    )
    st.metric("Historical return estimate", f"{result['expected_return']:.2%}")
    st.metric("Volatility", f"{result['volatility']:.2%}")
    st.metric("Reserve-eligible weight", f"{result['reserve_eligible_weight']:.2%}")


st.set_page_config(page_title="Meridian portfolio search", layout="wide")
st.title("Meridian portfolio search")
st.caption("Built with AI help, a learning demonstration, not investment advice.")

with st.sidebar:
    st.header("Inputs")
    objective = st.number_input("Objective return", value=OBJECTIVE_RETURN, step=0.005, format="%.3f")
    reserve_minimum = st.number_input("Minimum reserve-eligible weight", value=0.03, step=0.01, format="%.2f")
    uploaded = st.file_uploader("prices.csv", type="csv")
    last_36 = st.toggle("Use last 36 monthly returns", value=False)

try:
    if uploaded is None:
        names = [sleeve["name"] for sleeve in SLEEVES]
        loaded_expected = {sleeve["name"]: sleeve["expected_return"] for sleeve in SLEEVES}
        loaded_volatility = {sleeve["name"]: sleeve["volatility"] for sleeve in SLEEVES}
        loaded_correlations = CORRELATIONS
        current_expected = loaded_expected.copy()
        current_volatility = loaded_volatility
        current_correlations = loaded_correlations
        source_caption = "Meridian inputs as loaded"
    else:
        content = uploaded.getvalue().decode("utf-8")
        current_stats = estimate_from_prices(io.StringIO(content), last_36_months=last_36)
        loaded_stats = estimate_from_prices(io.StringIO(content), last_36_months=False)
        names = current_stats["tickers"]
        loaded_expected = loaded_stats["expected_returns"]
        loaded_volatility = loaded_stats["volatilities"]
        loaded_correlations = loaded_stats["correlations"]
        current_expected = current_stats["expected_returns"]
        current_volatility = current_stats["volatilities"]
        current_correlations = current_stats["correlations"]
        source_caption = f"CSV inputs as loaded (all {loaded_stats['observations']} monthly returns)"
except (UnicodeDecodeError, ValueError) as error:
    st.error(f"Could not read prices.csv: {error}")
    st.stop()

st.subheader("Historical annualized return estimates — not forecasts")
edited_expected = {}
reserve_eligible = set()
columns = st.columns(min(4, len(names)))
for index, name in enumerate(names):
    with columns[index % len(columns)]:
        edited_expected[name] = st.number_input(
            name,
            value=float(current_expected[name]),
            step=0.005,
            format="%.3f",
            help="Historical estimate: mean monthly return × 12. You may edit it; it is not a forecast.",
        )
        default_reserve = name in RESERVE_ELIGIBLE or name in {"BIL", "IEF"}
        if st.checkbox("Reserve eligible", value=default_reserve, key=f"reserve_{name}"):
            reserve_eligible.add(name)

current_sleeves = make_sleeves(names, edited_expected, current_volatility)
loaded_sleeves = make_sleeves(names, loaded_expected, loaded_volatility)
current_result = search_lowest_risk_mix(
    current_sleeves, current_correlations, objective, reserve_eligible, reserve_minimum
)
loaded_result = search_lowest_risk_mix(
    loaded_sleeves, loaded_correlations, objective, reserve_eligible, reserve_minimum
)

left, right = st.columns(2)
with left:
    st.subheader("Lowest-risk mix for current inputs")
    result_panel(current_result)
with right:
    st.subheader(source_caption)
    result_panel(loaded_result)

if current_result is not None and loaded_result is not None:
    largest_change = max(
        abs(current_result["weights"][name] - loaded_result["weights"][name])
        for name in names
    )
    st.info(
        "Largest weight change versus inputs as loaded: "
        f"{largest_change * 100:.1f} percentage points."
    )
