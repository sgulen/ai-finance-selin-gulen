"""Project 2 investment-management application."""

import streamlit as st

from project_results import AS_OF_DATE, build_final_output, build_scenario


def percent(value):
    return "-" if value is None else f"{value:.2%}"


def portfolio_table(portfolios):
    return [
        {
            "Portfolio": portfolio["name"],
            "Historical return estimate": percent(portfolio["expected_return"]),
            "Annualized volatility": percent(portfolio["volatility"]),
            "Reserve-eligible": percent(portfolio["reserve_eligible_weight"]),
            "Mandate verdict": portfolio["verdict"],
            "Failed rule(s)": "; ".join(portfolio["failed_rules"]) or "None",
        }
        for portfolio in portfolios
    ]


st.set_page_config(page_title="Meridian investment-management app", layout="wide")
st.title("Meridian investment-management app")
st.caption("AI use: I used OpenAI Codex to help organize and test code. I checked material outputs against the bundled data, code, and tests.")
st.caption("The analysis and decision are mine. This is for educational purposes only and is not investment advice.")

with st.sidebar:
    st.header("Scenario inputs")
    objective = st.number_input("Objective return", value=0.065, step=0.005, format="%.3f")
    reserve_minimum = st.number_input("Minimum reserve-eligible weight", value=0.03, step=0.01, format="%.2f")
    last_36 = st.toggle("Use last 36 monthly returns", value=False)

scenario = build_scenario(last_36_months=last_36, objective=objective, reserve_minimum=reserve_minimum)
final_output = build_final_output()
constrained = scenario["portfolios"][2]

st.header("Mandate")
st.markdown(
    "**Intended user:** investment committee  \n\n"
    "**Universe:** BIL, IEF, LQD, and ACWI  \n\n"
    "**Benchmark:** 40% LQD / 60% ACWI  \n\n"
    "**Risk measure:** annualized volatility  \n\n"
    "**Hard limits:** long-only, fully invested, historical return estimate at or above the objective, and BIL + IEF at or above the reserve minimum."
)

st.header("Portfolio comparison")
st.dataframe(portfolio_table(scenario["portfolios"]), hide_index=True, width="stretch")

for portfolio in scenario["portfolios"]:
    with st.container(border=True):
        st.subheader(portfolio["name"])
        if not portfolio["weights"]:
            st.error("No feasible portfolio for the current constraints.")
            continue
        st.dataframe(
            {"Asset": list(portfolio["weights"]), "Weight": [percent(weight) for weight in portfolio["weights"].values()]},
            hide_index=True,
            width="stretch",
        )
        st.caption("Mandate checks")
        st.dataframe(
            [{"Rule": check["rule"], "Status": check["status"], "Value": percent(check["value"]), "Threshold": percent(check["threshold"])} for check in portfolio["checks"]],
            hide_index=True,
            width="stretch",
        )

st.header("Point-in-time signal and data card")
st.markdown(
    f"**As-of date:** {AS_OF_DATE}  \n\n"
    "**Source:** Yahoo Finance monthly adjusted-close prices in the bundled prices.csv file.  \n\n"
    f"**Signal:** {scenario['signal']}  \n\n"
    f"**Timing rule:** no observation later than {AS_OF_DATE} enters the result.  \n\n"
    "**Limitations:** adjusted prices may be revised; the sample is limited; historical estimates are not forecasts."
)

st.header("Required stress run")
stress_base = final_output["base_case"]["portfolios"][2]
stress_case = final_output["stress_case"]["portfolios"][2]
st.markdown(final_output["stress_description"])
st.dataframe(
    [
        {"Scenario": "Base - all available returns", "Verdict": stress_base["verdict"], "Return": percent(stress_base["expected_return"]), "Volatility": percent(stress_base["volatility"])},
        {"Scenario": "Stress - last 36 returns", "Verdict": stress_case["verdict"], "Return": percent(stress_case["expected_return"]), "Volatility": percent(stress_case["volatility"])},
    ],
    hide_index=True,
    width="stretch",
)
st.warning(final_output["stop_condition"], title="Stop condition")

st.header("Committee recommendation")
if final_output["largest_constrained_weight_change"] is not None and final_output["largest_constrained_weight_change"] >= 0.10:
    st.error("Reject adoption and do not allocate now: the 36-month stress changes the constrained allocation by at least 10 percentage points.")
elif constrained["verdict"] == "PASS":
    st.success("Pilot, not adopt. Use the constrained allocation only in a limited pilot while the loss-limit policy is formally defined.")
    st.write("Target allocation: " + ", ".join(f"{asset} {percent(weight)}" for asset, weight in constrained["weights"].items()))
else:
    st.error("Reject the current implementation: the constrained portfolio does not meet every stated mandate rule.")
st.markdown(
    "**Monitor:** monthly return-estimate changes, volatility, and reserve-eligible allocation.  \n\n"
    "**Reversal trigger:** stop the pilot if no feasible portfolio remains, the loss-limit policy remains undefined, or the 36-month stress shifts a weight by 10 percentage points or more.  \n\n"
    "**Committee ask:** do not approve an allocation until the loss-limit policy is defined and the stress sensitivity is reduced."
)
