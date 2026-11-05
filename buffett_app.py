"""Display one five-year 10-K record through three investor screens."""

from __future__ import annotations

import io
import os
import re
import sys
from contextlib import redirect_stdout
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parent
SKILL_SCRIPT_DIR = ROOT / ".agents" / "skills" / "buffett-10k-analysis" / "scripts"
sys.path.insert(0, str(SKILL_SCRIPT_DIR))

from edgar_facts import (  # noqa: E402
    EdgarError,
    USER_AGENT_ENV,
    analyze_company_facts,
    format_percent,
    format_ratio,
    print_analysis,
)


st.set_page_config(page_title="10-K investor panel")

DATA_SCHEMA_VERSION = "three-investor-panel-v2"
INVESTOR_ORDER = ("Buffett", "Cathie Wood", "Burry")
NUMBER = re.compile(r"(?<![A-Za-z0-9_])\$?[-+]?\d[\d,]*(?:\.\d+)?%?(?![A-Za-z0-9_])")


@st.cache_data(ttl="6h", max_entries=20, show_spinner=False)
def load_analysis(ticker: str, schema_version: str) -> dict[str, Any]:
    """Cache public source facts, never the caller's user-agent string."""

    del schema_version
    return analyze_company_facts(ticker, os.environ.get(USER_AGENT_ENV, ""))


def script_output(analysis: dict[str, Any]) -> str:
    """Capture the values printed by the reproducible script."""

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        print_analysis(analysis)
    return buffer.getvalue()


def normalize_number(token: str) -> str | None:
    """Normalize spelling variants such as 5,844 and $5844 for comparison."""

    text = token.strip().replace("$", "")
    percent = text.endswith("%")
    if percent:
        text = text[:-1]
    try:
        number = Decimal(text.replace(",", ""))
    except InvalidOperation:
        return None
    normalized = format(number.normalize(), "f")
    if "." in normalized:
        normalized = normalized.rstrip("0").rstrip(".")
    if normalized in {"", "-0"}:
        normalized = "0"
    return normalized + ("%" if percent else "")


def unprinted_numbers(memo: str, analysis: dict[str, Any]) -> list[str]:
    """Return numeric tokens in a memo that are absent from the script output."""

    allowed = {
        normalized
        for token in NUMBER.findall(script_output(analysis))
        if (normalized := normalize_number(token)) is not None
    }
    flagged: list[str] = []
    for token in NUMBER.findall(memo):
        normalized = normalize_number(token)
        if normalized is not None and normalized not in allowed and token not in flagged:
            flagged.append(token)
    return flagged


def table_from_analysis(analysis: dict[str, Any]) -> pd.DataFrame:
    """Make the shared five-year record readable in the app."""

    return pd.DataFrame(
        [
            {
                "Fiscal end": row["fiscal_end"],
                "Revenue ($m)": row["revenue"],
                "Net income ($m)": row["net_income"],
                "Cash from operations ($m)": row["cash_from_operations"],
                "Capex ($m)": row["capex"],
                "Equity ($m)": row["equity"],
                "Liabilities ($m)": row["liabilities"],
                "R&D ($m)": row["research_and_development"],
                "ROE (%)": None if row["roe"] is None else row["roe"] * 100,
                "Owner earnings ($m)": row["owner_earnings"],
            }
            for row in analysis["rows"]
        ]
    )


def panel_rows(analysis: dict[str, Any]) -> pd.DataFrame:
    """Flatten the shared investor checks for the required panel table."""

    rows: list[dict[str, str]] = []
    for investor in INVESTOR_ORDER:
        for check, result in analysis["panel_checks"][investor].items():
            result_text = result
            if investor == "Cathie Wood" and check.startswith("Revenue"):
                growth = analysis["revenue_growth_per_year"]
                if growth is not None:
                    result_text = f"{result} ({format_percent(growth, digits=2)})"
            if investor == "Burry" and check.startswith("Liabilities"):
                ratio = analysis["rows"][-1]["liabilities_to_equity"]
                if ratio is not None:
                    result_text = f"{result} ({format_ratio(ratio)})"
            rows.append({"Investor": investor, "Check": check, "Result": result_text})
    return pd.DataFrame(rows)


def verdict(checks: dict[str, str]) -> str:
    """Turn only the stated screen results into a transparent default verdict."""

    results = list(checks.values())
    if results and all(result == "pass" for result in results):
        return "Own"
    if any(result == "fail" for result in results):
        return "Pass"
    return "Watch"


def result_for(checks: dict[str, str], starts_with: str) -> str:
    """Get one check without coupling a memo to a hard-coded threshold label."""

    for label, result in checks.items():
        if label.startswith(starts_with):
            return result
    return "not known"


def default_buffett_memo(ticker: str, analysis: dict[str, Any]) -> str:
    memo_path = ROOT / "memos" / f"{ticker.lower()}_buffett_memo.md"
    if memo_path.exists():
        return memo_path.read_text(encoding="utf-8")
    if all(row["owner_earnings"] is None for row in analysis["rows"]):
        return (
            "**Verdict: Watch.** I cannot judge owner earnings from this record because capital "
            "spending is not found and owner earnings is not known. A business judgment needs the "
            "missing annual cash-investment evidence rather than an estimate."
        )
    return (
        f"**Verdict: {verdict(analysis['panel_checks']['Buffett'])}.** The Buffett checks are "
        "a business-quality screen based only on the printed 10-K record. I would verify the "
        "underlying filing before treating it as a durable-moat conclusion."
    )


def default_cathie_memo(analysis: dict[str, Any]) -> str:
    checks = analysis["panel_checks"]["Cathie Wood"]
    growth = analysis["revenue_growth_per_year"]
    latest_r_and_d = analysis["rows"][-1]["r_and_d_to_revenue"]
    thresholds = analysis["thresholds"]
    growth_threshold = format_percent(thresholds["cathie_revenue_growth"], digits=0)
    r_and_d_threshold = format_percent(thresholds["cathie_r_and_d_to_revenue"], digits=0)
    return (
        f"**Verdict: {verdict(checks)}.** Revenue growth was "
        f"{format_percent(growth, digits=2)}; the {growth_threshold} growth screen is "
        f"{result_for(checks, 'Revenue grew')}. Latest-year R&D "
        f"divided by revenue was {format_percent(latest_r_and_d)}, so the R&D screen is "
        f"{result_for(checks, 'R&D')} at the {r_and_d_threshold} threshold. This record alone does not prove "
        "a disruptive-innovation thesis."
    )


def default_burry_memo(analysis: dict[str, Any]) -> str:
    checks = analysis["panel_checks"]["Burry"]
    liabilities_ratio = analysis["rows"][-1]["liabilities_to_equity"]
    return (
        f"**Verdict: {verdict(checks)}.** Operating cash flow was at least net income in every "
        f"reported year: {result_for(checks, 'Operating cash flow')}. Latest "
        f"liabilities divided by equity was {format_ratio(liabilities_ratio)}, so the balance-sheet "
        f"screen is {result_for(checks, 'Liabilities')}. These screens "
        "do not replace a read of the 10-K footnotes and risks."
    )


def default_memos(ticker: str, analysis: dict[str, Any]) -> dict[str, str]:
    return {
        "Buffett": default_buffett_memo(ticker, analysis),
        "Cathie Wood": default_cathie_memo(analysis),
        "Burry": default_burry_memo(analysis),
    }


st.title("10-K investor panel")
st.caption(
    "Data from SEC EDGAR; built with AI help, a learning demonstration, not investment advice."
)

st.session_state.setdefault("edgar_analysis", None)

with st.sidebar:
    st.header("Company")
    with st.form("company_form", border=False):
        ticker = st.text_input("Ticker", value="COST", max_chars=10).strip().upper()
        submitted = st.form_submit_button("Fetch 10-K facts", icon=":material/download:")
    st.caption(
        f"Set `{USER_AGENT_ENV}` in this PowerShell session before fetching. It is never saved "
        "in the app or project."
    )
    st.link_button(
        "SEC EDGAR API",
        "https://www.sec.gov/search-filings/edgar-application-programming-interfaces",
    )
    st.link_button(
        "Cathie Wood framework",
        "https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/cathie_wood.md",
    )
    st.link_button(
        "Michael Burry framework",
        "https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/michael_burry.md",
    )

if submitted:
    try:
        st.session_state["edgar_analysis"] = load_analysis(ticker, DATA_SCHEMA_VERSION)
        for investor, memo in default_memos(
            ticker, st.session_state["edgar_analysis"]
        ).items():
            st.session_state[f"{investor.lower().replace(' ', '_')}_memo"] = memo
    except EdgarError as error:
        st.session_state["edgar_analysis"] = None
        st.error(str(error), title="EDGAR download unavailable")

analysis = st.session_state["edgar_analysis"]
if analysis is None:
    st.info(
        "Set your temporary SEC user-agent in PowerShell, enter a ticker, and select 'Fetch 10-K facts.'",
        title="Ready for an audited 10-K record",
    )
    st.stop()
if "panel_checks" not in analysis:
    st.info(
        "This app has new panel fields. Select 'Fetch 10-K facts' once to refresh this session.",
        title="Refresh the 10-K record",
    )
    st.stop()

data = table_from_analysis(analysis)
st.subheader(f"{analysis['company']} ({analysis['ticker']})")
st.caption("USD millions except ratios. For each fiscal end, the latest 10-K filing wins.")

with st.container(border=True):
    st.subheader("Owner earnings and net income")
    chart_data = data[["Fiscal end", "Net income ($m)", "Owner earnings ($m)"]]
    st.line_chart(
        chart_data,
        x="Fiscal end",
        y=["Net income ($m)", "Owner earnings ($m)"],
        x_label="Fiscal end",
        y_label="USD millions",
        alt="Net income and owner earnings across the five annual 10-K fiscal ends.",
    )

st.subheader("Five-year 10-K panel")
st.dataframe(
    data,
    hide_index=True,
    column_config={
        "Revenue ($m)": st.column_config.NumberColumn(format="%,.0f"),
        "Net income ($m)": st.column_config.NumberColumn(format="%,.0f"),
        "Cash from operations ($m)": st.column_config.NumberColumn(format="%,.0f"),
        "Capex ($m)": st.column_config.NumberColumn(format="%,.0f"),
        "Equity ($m)": st.column_config.NumberColumn(format="%,.0f"),
        "Liabilities ($m)": st.column_config.NumberColumn(format="%,.0f"),
        "R&D ($m)": st.column_config.NumberColumn(format="%,.0f"),
        "ROE (%)": st.column_config.NumberColumn(format="%.1f%%"),
        "Owner earnings ($m)": st.column_config.NumberColumn(format="%,.0f"),
    },
    alt="Five-year annual 10-K record shared by all three investor screens.",
)

with st.container(border=True):
    st.subheader("Tags and screen inputs")
    st.table(
        {
            "Revenue": analysis["tags"]["revenue"],
            "Net income": analysis["tags"]["net_income"],
            "Cash from operations": analysis["tags"]["cash_from_operations"],
            "Capex": analysis["tags"]["capex"],
            "Equity": analysis["tags"]["equity"],
            "Liabilities": analysis["tags"]["liabilities"],
            "Research and development": analysis["tags"]["research_and_development"],
            "Revenue growth a year": analysis["tags"]["revenue_growth_per_year"],
        },
        border="horizontal",
        width="stretch",
        alt="XBRL tags and formula used to make the shared investor screens.",
    )
    latest = analysis["rows"][-1]
    metrics = pd.DataFrame(
        [
            {
                "Metric": "Revenue growth a year, first year to last",
                "Value": format_percent(analysis["revenue_growth_per_year"], digits=2),
            },
            {
                "Metric": "R&D / revenue, latest year",
                "Value": format_percent(latest["r_and_d_to_revenue"]),
            },
            {
                "Metric": "Liabilities / equity, latest year",
                "Value": format_ratio(latest["liabilities_to_equity"]),
            },
        ]
    )
    st.dataframe(
        metrics,
        hide_index=True,
        alt="Latest and first-to-last inputs used in the Cathie Wood and Burry checks.",
    )

st.subheader("Investor panel")
st.dataframe(
    panel_rows(analysis),
    hide_index=True,
    alt="Each investor's checks and pass, fail, or not known result for the shared 10-K record.",
)

st.subheader("Three evidence-based memos")
st.caption(
    "Each memo may use only values printed by the script. The evidence audit checks all three."
)
memos: dict[str, str] = {}
columns = st.columns(3)
for column, investor in zip(columns, INVESTOR_ORDER, strict=True):
    memo_key = f"{investor.lower().replace(' ', '_')}_memo"
    with column:
        st.markdown(f"#### {investor}: {verdict(analysis['panel_checks'][investor])}")
        memos[investor] = st.text_area(
            f"{investor} memo",
            key=memo_key,
            height=320,
        )

audit_rows = []
for investor in INVESTOR_ORDER:
    flagged = unprinted_numbers(memos[investor] or "", analysis)
    audit_rows.append(
        {
            "Investor": investor,
            "Unprinted numbers": ", ".join(flagged) if flagged else "none",
        }
    )
evidence_audit = pd.DataFrame(audit_rows)
st.subheader("Memo evidence audit")
st.dataframe(
    evidence_audit,
    hide_index=True,
    alt="Unprinted-number results for Buffett, Cathie Wood, and Burry memos.",
)
if evidence_audit["Unprinted numbers"].ne("none").any():
    st.warning(
        "Revise every flagged memo number so it exactly matches the script output.",
        title="Memo needs an evidence check",
    )
else:
    st.success("Every numeral across all three memos appears in the script output.")
