"""Compute a five-year annual 10-K record from SEC EDGAR."""

from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
import zlib
from dataclasses import dataclass
from datetime import date
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
USER_AGENT_ENV = "SEC_USER_AGENT"
ANNUAL_MIN_DAYS = 330
ANNUAL_MAX_DAYS = 400
CATHIE_REVENUE_GROWTH_THRESHOLD = 0.15
CATHIE_R_AND_D_TO_REVENUE_THRESHOLD = 0.05
BURRY_LIABILITIES_TO_EQUITY_MAX = 2.0


class EdgarError(RuntimeError):
    """A clear, user-facing failure while retrieving or parsing EDGAR data."""


@dataclass(frozen=True)
class Fact:
    """A selected SEC fact."""

    value: float | None


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _request_json(url: str, user_agent: str, timeout: int = 30) -> dict[str, Any]:
    """Read one public SEC JSON document with the caller's declared user agent."""

    if not user_agent.strip():
        raise EdgarError(
            f"Set {USER_AGENT_ENV} to your name and email before requesting SEC data."
        )
    request = Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept-Encoding": "gzip, deflate",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = response.read()
            content_encoding = response.headers.get("Content-Encoding", "").lower()
        if "gzip" in content_encoding:
            payload = gzip.decompress(payload)
        elif "deflate" in content_encoding:
            payload = zlib.decompress(payload)
        return json.loads(payload.decode("utf-8"))
    except HTTPError as error:
        raise EdgarError(f"SEC returned HTTP {error.code} for {url}.") from error
    except URLError as error:
        raise EdgarError(f"Could not reach the SEC: {error.reason}.") from error


def ticker_to_cik(ticker: str, user_agent: str) -> int:
    """Resolve a public ticker to its SEC central index key."""

    target = ticker.strip().upper()
    if not target:
        raise EdgarError("Enter a ticker symbol.")
    records = _request_json(TICKERS_URL, user_agent)
    for record in records.values():
        if str(record.get("ticker", "")).upper() == target:
            return int(record["cik_str"])
    raise EdgarError(f"SEC did not find a CIK for ticker {target}.")


def _usd_units(facts: dict[str, Any], tag: str) -> list[dict[str, Any]]:
    concept = facts.get(tag, {})
    units = concept.get("units", {})
    values = units.get("USD", [])
    return [value for value in values if isinstance(value, dict)]


def _latest_by_end(
    facts: dict[str, Any], tag: str, *, flow: bool
) -> dict[str, Fact]:
    """Keep the latest-filed 10-K fact for every fiscal end.

    Flows must cover approximately one year.  Instant facts (equity) have no
    start date.  The form and duration filters prevent 10-Q and YTD values from
    leaking into the five-year table.
    """

    selected: dict[str, tuple[tuple[str, str, str], Fact]] = {}
    for item in _usd_units(facts, tag):
        if item.get("form") != "10-K" or item.get("fp") != "FY":
            continue
        end = item.get("end")
        if not isinstance(end, str) or _parse_date(end) is None:
            continue

        if flow:
            start = _parse_date(item.get("start"))
            end_date = _parse_date(end)
            if start is None or end_date is None:
                continue
            duration = (end_date - start).days
            if duration < ANNUAL_MIN_DAYS or duration > ANNUAL_MAX_DAYS:
                continue

        value = item.get("val")
        if not isinstance(value, (int, float)):
            continue
        filed = str(item.get("filed", ""))
        accession = str(item.get("accn", ""))
        frame = str(item.get("frame", ""))
        sort_key = (filed, accession, frame)
        candidate = Fact(float(value))
        current = selected.get(end)
        if current is None or sort_key > current[0]:
            selected[end] = (sort_key, candidate)
    return {end: fact for end, (_, fact) in selected.items()}


def _metric_map(
    facts: dict[str, Any], primary_tag: str, fallback_tag: str | None, *, flow: bool
) -> tuple[dict[str, Fact], str | None]:
    """Use the required primary XBRL tag, falling back only when it has no facts."""

    primary = _latest_by_end(facts, primary_tag, flow=flow)
    if primary:
        return primary, primary_tag
    if fallback_tag:
        fallback = _latest_by_end(facts, fallback_tag, flow=flow)
        if fallback:
            return fallback, fallback_tag
    return {}, None


def _millions(fact: Fact | None) -> float | None:
    return None if fact is None or fact.value is None else fact.value / 1_000_000


def _all_known(values: list[float | None]) -> bool:
    return bool(values) and all(value is not None for value in values)


def _buffett_checks(rows: list[dict[str, Any]]) -> dict[str, str]:
    roe = [row["roe"] for row in rows]
    owner_earnings = [row["owner_earnings"] for row in rows]
    return {
        "ROE at least 15% every year": (
            "pass"
            if _all_known(roe) and all(value >= 0.15 for value in roe if value is not None)
            else "not known"
            if not _all_known(roe)
            else "fail"
        ),
        "Owner earnings positive every year": (
            "pass"
            if _all_known(owner_earnings)
            and all(value > 0 for value in owner_earnings if value is not None)
            else "not known"
            if not _all_known(owner_earnings)
            else "fail"
        ),
        "Owner earnings grew from first to last year": (
            "pass"
            if _all_known(owner_earnings)
            and owner_earnings[-1] > owner_earnings[0]
            else "not known"
            if not _all_known(owner_earnings)
            else "fail"
        ),
    }


def _revenue_growth_per_year(rows: list[dict[str, Any]]) -> float | None:
    """Return the Lab 19 first-to-last revenue growth rate over four years."""

    if len(rows) != 5:
        return None
    first_revenue = rows[0]["revenue"]
    last_revenue = rows[-1]["revenue"]
    if (
        first_revenue is None
        or last_revenue is None
        or first_revenue <= 0
        or last_revenue <= 0
    ):
        return None
    return (last_revenue / first_revenue) ** (1 / 4) - 1


def _panel_checks(rows: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    """Apply the three investors' stated screens to one shared five-year record."""

    revenue_growth = _revenue_growth_per_year(rows)
    latest = rows[-1] if rows else {}
    latest_r_and_d_ratio = latest.get("r_and_d_to_revenue")
    latest_liabilities_ratio = latest.get("liabilities_to_equity")
    cfo = [row["cash_from_operations"] for row in rows]
    net_income = [row["net_income"] for row in rows]
    growth_label = (
        "Revenue grew "
        f"{CATHIE_REVENUE_GROWTH_THRESHOLD * 100:g}% or more a year, first year to last"
    )
    r_and_d_label = (
        "R&D "
        f"{CATHIE_R_AND_D_TO_REVENUE_THRESHOLD * 100:g}% or more of revenue, latest year"
    )

    return {
        "Buffett": _buffett_checks(rows),
        "Cathie Wood": {
            growth_label: (
                "pass"
                if revenue_growth is not None
                and revenue_growth >= CATHIE_REVENUE_GROWTH_THRESHOLD
                else "not known"
                if revenue_growth is None
                else "fail"
            ),
            r_and_d_label: (
                "pass"
                if latest_r_and_d_ratio is not None
                and latest_r_and_d_ratio >= CATHIE_R_AND_D_TO_REVENUE_THRESHOLD
                else "not known"
                if latest_r_and_d_ratio is None
                else "fail"
            ),
        },
        "Burry": {
            "Operating cash flow at least net income every year": (
                "pass"
                if _all_known(cfo)
                and _all_known(net_income)
                and all(
                    cash >= income
                    for cash, income in zip(cfo, net_income, strict=True)
                    if cash is not None and income is not None
                )
                else "not known"
                if not _all_known(cfo) or not _all_known(net_income)
                else "fail"
            ),
            "Liabilities no more than twice equity, latest year": (
                "pass"
                if latest_liabilities_ratio is not None
                and latest_liabilities_ratio <= BURRY_LIABILITIES_TO_EQUITY_MAX
                else "not known"
                if latest_liabilities_ratio is None
                else "fail"
            ),
        },
    }


def analyze_company_facts(ticker: str, user_agent: str) -> dict[str, Any]:
    """Return the strict five-year annual 10-K panel and its reproducible checks."""

    clean_ticker = ticker.strip().upper()
    cik = ticker_to_cik(clean_ticker, user_agent)
    company_facts = _request_json(FACTS_URL.format(cik=cik), user_agent)
    facts = company_facts.get("facts", {}).get("us-gaap", {})
    if not isinstance(facts, dict):
        raise EdgarError(f"SEC returned no US-GAAP facts for {clean_ticker}.")

    revenue, revenue_tag = _metric_map(
        facts, "RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", flow=True
    )
    net_income, net_income_tag = _metric_map(facts, "NetIncomeLoss", None, flow=True)
    cfo, cfo_tag = _metric_map(
        facts, "NetCashProvidedByUsedInOperatingActivities", None, flow=True
    )
    capex, capex_tag = _metric_map(
        facts,
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets",
        flow=True,
    )
    equity, equity_tag = _metric_map(facts, "StockholdersEquity", None, flow=False)
    liabilities, liabilities_tag = _metric_map(facts, "Liabilities", None, flow=False)
    research_and_development, research_and_development_tag = _metric_map(
        facts, "ResearchAndDevelopmentExpense", None, flow=True
    )

    # Take fiscal periods from the union.  A missing revenue tag must not make
    # an otherwise valid 10-K year disappear from the panel.
    fiscal_ends = sorted(
        set().union(
            revenue,
            net_income,
            cfo,
            capex,
            equity,
            liabilities,
            research_and_development,
        )
    )[-5:]
    if not fiscal_ends:
        raise EdgarError(f"SEC returned no annual 10-K facts for {clean_ticker}.")

    rows: list[dict[str, Any]] = []
    for fiscal_end in fiscal_ends:
        revenue_value = _millions(revenue.get(fiscal_end))
        net_income_value = _millions(net_income.get(fiscal_end))
        cfo_value = _millions(cfo.get(fiscal_end))
        capex_value = _millions(capex.get(fiscal_end))
        equity_value = _millions(equity.get(fiscal_end))
        liabilities_value = _millions(liabilities.get(fiscal_end))
        research_and_development_value = _millions(research_and_development.get(fiscal_end))
        roe = (
            net_income_value / equity_value
            if net_income_value is not None
            and equity_value is not None
            and equity_value > 0
            else None
        )
        owner_earnings = (
            cfo_value - capex_value
            if cfo_value is not None and capex_value is not None
            else None
        )
        r_and_d_to_revenue = (
            research_and_development_value / revenue_value
            if research_and_development_value is not None
            and revenue_value is not None
            and revenue_value > 0
            else None
        )
        liabilities_to_equity = (
            liabilities_value / equity_value
            if liabilities_value is not None and equity_value is not None and equity_value > 0
            else None
        )
        rows.append(
            {
                "fiscal_end": fiscal_end,
                "revenue": revenue_value,
                "net_income": net_income_value,
                "cash_from_operations": cfo_value,
                "capex": capex_value,
                "equity": equity_value,
                "liabilities": liabilities_value,
                "research_and_development": research_and_development_value,
                "roe": roe,
                "owner_earnings": owner_earnings,
                "r_and_d_to_revenue": r_and_d_to_revenue,
                "liabilities_to_equity": liabilities_to_equity,
            }
        )

    tags = {
        "revenue": revenue_tag or "not found",
        "net_income": net_income_tag or "not found",
        "cash_from_operations": cfo_tag or "not found",
        "capex": capex_tag or "not found",
        "equity": equity_tag or "not found",
        "liabilities": liabilities_tag or "not found",
        "research_and_development": research_and_development_tag or "not found",
        "roe": "NetIncomeLoss / StockholdersEquity",
        "owner_earnings": "NetCashProvidedByUsedInOperatingActivities - capex",
        "r_and_d_to_revenue": "ResearchAndDevelopmentExpense / revenue",
        "liabilities_to_equity": "Liabilities / StockholdersEquity",
        "revenue_growth_per_year": "(last revenue / first revenue)^(1/4) - 1",
    }
    return {
        "ticker": clean_ticker,
        "company": company_facts.get("entityName", clean_ticker),
        "cik": cik,
        "units": "USD millions except ROE",
        "rows": rows,
        "tags": tags,
        "checks": _buffett_checks(rows),
        "panel_checks": _panel_checks(rows),
        "revenue_growth_per_year": _revenue_growth_per_year(rows),
        "thresholds": {
            "cathie_revenue_growth": CATHIE_REVENUE_GROWTH_THRESHOLD,
            "cathie_r_and_d_to_revenue": CATHIE_R_AND_D_TO_REVENUE_THRESHOLD,
            "burry_liabilities_to_equity_max": BURRY_LIABILITIES_TO_EQUITY_MAX,
        },
    }


def format_millions(value: float | None) -> str:
    return "not found" if value is None else f"{value:,.0f}"


def format_percent(value: float | None, digits: int = 1) -> str:
    return "not known" if value is None else f"{value * 100:.{digits}f}%"


def format_ratio(value: float | None) -> str:
    return "not known" if value is None else f"{value:.2f}"


def print_analysis(analysis: dict[str, Any]) -> None:
    """Print the five-year record, its tags, and its checks."""

    print(f"{analysis['company']} ({analysis['ticker']}; CIK {analysis['cik']:010d})")
    print("10-K annual facts; latest filing for each fiscal end; USD millions except ROE")
    print()
    print("XBRL tags and formulas")
    for label, key in (
        ("Revenue", "revenue"),
        ("Net income", "net_income"),
        ("Cash from operations", "cash_from_operations"),
        ("Capital expenditure", "capex"),
        ("Equity", "equity"),
        ("Liabilities", "liabilities"),
        ("Research and development", "research_and_development"),
        ("ROE", "roe"),
        ("Owner earnings", "owner_earnings"),
        ("R&D / revenue", "r_and_d_to_revenue"),
        ("Liabilities / equity", "liabilities_to_equity"),
        ("Revenue growth a year", "revenue_growth_per_year"),
    ):
        print(f"- {label}: {analysis['tags'][key]}")
    print()
    print(
        "Fiscal end | Revenue | Net income | CFO | Capex | Equity | Liabilities | R&D | ROE | Owner earnings"
    )
    for row in analysis["rows"]:
        print(
            " | ".join(
                (
                    row["fiscal_end"],
                    format_millions(row["revenue"]),
                    format_millions(row["net_income"]),
                    format_millions(row["cash_from_operations"]),
                    format_millions(row["capex"]),
                    format_millions(row["equity"]),
                    format_millions(row["liabilities"]),
                    format_millions(row["research_and_development"]),
                    format_percent(row["roe"]),
                    format_millions(row["owner_earnings"]),
                )
            )
        )
    print()
    print()
    print("Panel facts")
    print("Fiscal end | R&D / revenue | Liabilities / equity")
    for row in analysis["rows"]:
        print(
            f"{row['fiscal_end']} | {format_percent(row['r_and_d_to_revenue'])} | "
            f"{format_ratio(row['liabilities_to_equity'])}"
        )
    print(
        "Revenue growth a year, "
        f"{analysis['rows'][0]['fiscal_end']} to {analysis['rows'][-1]['fiscal_end']}: "
        f"{format_percent(analysis['revenue_growth_per_year'], digits=2)}"
    )
    print()
    print("Panel checks")
    for investor, checks in analysis["panel_checks"].items():
        for label, result in checks.items():
            print(f"- {investor} | {label}: {result}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute 10-K fundamentals from SEC EDGAR.")
    parser.add_argument("ticker", help="Public-company ticker, for example COST or JPM")
    args = parser.parse_args()
    try:
        analysis = analyze_company_facts(args.ticker, os.environ.get(USER_AGENT_ENV, ""))
    except EdgarError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    print_analysis(analysis)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
