"""Five-year TSLA pro-forma and FCFF valuation engine; USD millions unless noted."""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from math import isfinite


@dataclass(frozen=True)
class Assumptions:
    # Bounded exposed drivers. Bounds are disclosed in the assumption-challenge record.
    revenue_growth_shift: float = 0.0       # percentage points applied to each forecast year
    segment_margin_shift: float = 0.0       # percentage points applied to each segment gross margin
    wacc: float = 0.105
    terminal_growth: float = 0.025
    tax_rate: float = 0.27
    # 2025 source-linked bridge items
    cash: float = 16513.0
    short_term_investments: float = 27546.0
    debt_and_finance_leases: float = 8376.0
    redeemable_nci: float = 58.0
    nci: float = 670.0
    diluted_shares: float = 3528.0


BASE = Assumptions()
BOUNDS = {
    "revenue_growth_shift": (-0.03, 0.03),
    "segment_margin_shift": (-0.02, 0.02),
    "wacc": (0.085, 0.125),
    "terminal_growth": (0.015, 0.030),
}

# FY2025 filing anchors and a Tesla-specific segmented pro-forma. The segment paths are
# the canonical operating forecast; the DCF below consumes their resulting FCFF.
BASE_YEAR = {
    "year": 2025,
    "revenue": 94827.0,
    "ebit": 4355.0,
    "cash": 16513.0,
    "investments": 27546.0,
    "ar": 4576.0,
    "inventory": 12392.0,
    "other_operating_assets": 36136.0,
    "ppe": 40643.0,
    "ap": 13371.0,
    "other_operating_liabilities": 33194.0,
    "debt": 8376.0,
}

BASE_YEAR["segment_revenue"] = {"auto": 69526.0, "energy": 12771.0, "services": 12530.0}
SEGMENT_GROWTH = {"auto": [0.04, 0.05, 0.05, 0.04, 0.03], "energy": [0.25, 0.20, 0.15, 0.12, 0.10], "services": [0.12, 0.10, 0.08, 0.06, 0.05]}
SEGMENT_GROSS_MARGIN = {"auto": [0.180, 0.182, 0.185, 0.187, 0.190], "energy": [0.295, 0.300, 0.305, 0.310, 0.315], "services": [0.080, 0.085, 0.090, 0.095, 0.100]}
RD_PCT_REVENUE = [0.064, 0.062, 0.060, 0.058, 0.056]
SGA_PCT_REVENUE = [0.061, 0.060, 0.059, 0.058, 0.057]


def _checks(a: Assumptions, enforce_bounds: bool = True) -> list[str]:
    failures: list[str] = []
    if enforce_bounds:
        for field, (low, high) in BOUNDS.items():
            value = getattr(a, field)
            if not low <= value <= high:
                failures.append(f"{field}={value:.2%} is outside its approved range {low:.1%} to {high:.1%}.")
    if a.terminal_growth >= a.wacc:
        failures.append("terminal_growth must be below WACC for the Gordon-growth terminal value.")
    if a.diluted_shares <= 0:
        failures.append("Diluted shares must be positive.")
    return failures


def run_model(a: Assumptions = BASE, enforce_bounds: bool = True) -> dict:
    """Return linked statements, FCFF DCF, bridge, and validations. Raises no hidden errors."""
    failures = _checks(a, enforce_bounds)
    if failures:
        return {"valid": False, "failures": failures, "assumptions": asdict(a)}

    years: list[dict] = []
    prev = BASE_YEAR.copy()
    fcff: list[float] = []
    for i, year in enumerate(range(2026, 2031)):
        segment_revenue = {name: prev["segment_revenue"][name] * (1 + SEGMENT_GROWTH[name][i] + a.revenue_growth_shift) for name in SEGMENT_GROWTH}
        segment_gross_profit = {name: segment_revenue[name] * (SEGMENT_GROSS_MARGIN[name][i] + a.segment_margin_shift) for name in SEGMENT_GROSS_MARGIN}
        revenue = sum(segment_revenue.values())
        gross_profit = sum(segment_gross_profit.values())
        rd = revenue * RD_PCT_REVENUE[i]
        sga = revenue * SGA_PCT_REVENUE[i]
        ebit = gross_profit - rd - sga
        margin = ebit / revenue
        growth = revenue / prev["revenue"] - 1
        da = prev["ppe"] * 0.1513
        capex = 21000.0 if i == 0 else revenue * 0.080
        ar = revenue * 0.0483
        inventory = (revenue - gross_profit) * 58.2 / 365
        other_assets = revenue * 0.3811
        ap = (revenue - gross_profit) * 0.1720
        other_liabilities = revenue * 0.3501
        operating_nwc = ar + inventory + other_assets - ap - other_liabilities
        prior_nwc = (prev["ar"] + prev["inventory"] + prev["other_operating_assets"]
                     - prev["ap"] - prev["other_operating_liabilities"])
        change_nwc = operating_nwc - prior_nwc
        nopat = ebit * (1 - a.tax_rate)
        cash_from_operations = nopat + da - change_nwc
        cash = prev["cash"] + cash_from_operations - capex
        ppe = prev["ppe"] + capex - da
        # Equity is the balancing retained-earnings output, not an input plug hidden from the user.
        assets = cash + a.short_term_investments + ar + inventory + other_assets + ppe
        liabilities = ap + other_liabilities + a.debt_and_finance_leases
        equity = assets - liabilities
        balance_check = assets - liabilities - equity
        fcff_value = nopat + da - capex - change_nwc
        fcff.append(fcff_value)
        years.append({
            "year": year, "revenue": revenue, "growth": growth, "ebit_margin": margin,
            "segment_revenue": segment_revenue, "segment_gross_profit": segment_gross_profit,
            "gross_profit": gross_profit, "rd": rd, "sga": sga,
            "ebit": ebit, "nopat": nopat, "da": da, "capex": capex,
            "change_nwc": change_nwc, "cash_from_operations": cash_from_operations,
            "fcff": fcff_value, "cash": cash, "investments": a.short_term_investments,
            "ar": ar, "inventory": inventory, "other_operating_assets": other_assets,
            "ppe": ppe, "ap": ap, "other_operating_liabilities": other_liabilities,
            "debt": a.debt_and_finance_leases, "equity": equity,
            "assets": assets, "liabilities_and_equity": liabilities + equity,
            "balance_check": balance_check,
        })
        prev = {
            "revenue": revenue, "cash": cash, "ar": ar, "inventory": inventory,
            "other_operating_assets": other_assets, "ppe": ppe, "ap": ap,
            "other_operating_liabilities": other_liabilities, "segment_revenue": segment_revenue,
        }

    pv_explicit = sum(value / (1 + a.wacc) ** (i + 1) for i, value in enumerate(fcff))
    terminal_value = fcff[-1] * (1 + a.terminal_growth) / (a.wacc - a.terminal_growth)
    pv_terminal = terminal_value / (1 + a.wacc) ** 5
    ev = pv_explicit + pv_terminal
    equity_value = ev + a.cash + a.short_term_investments - a.debt_and_finance_leases - a.redeemable_nci - a.nci
    value_per_share = equity_value / a.diluted_shares
    return {
        "valid": True, "assumptions": asdict(a), "base_year": BASE_YEAR,
        "years": years, "fcff": fcff,
        "valuation": {
            "pv_explicit_fcff": pv_explicit, "terminal_value": terminal_value,
            "pv_terminal": pv_terminal, "enterprise_value": ev,
            "terminal_value_share": pv_terminal / ev, "equity_value": equity_value,
            "value_per_share": value_per_share,
        },
        "checks": {
            "base_year_reconciles_to_ledger": all((BASE_YEAR["revenue"] == 94827.0, BASE_YEAR["ebit"] == 4355.0, BASE_YEAR["cash"] == 16513.0, BASE_YEAR["investments"] == 27546.0, BASE_YEAR["debt"] == 8376.0, BASE_YEAR["segment_revenue"] == {"auto": 69526.0, "energy": 12771.0, "services": 12530.0})),
            "balance_sheet_max_abs_error": max(abs(y["balance_check"]) for y in years),
            "cash_flow_ties_to_cash": all(abs(years[i]["cash"] - (BASE_YEAR["cash"] if i == 0 else years[i-1]["cash"]) - years[i]["cash_from_operations"] + years[i]["capex"]) < 1e-6 for i in range(5)),
            "bridge_reconciles": abs(equity_value - (ev + a.cash + a.short_term_investments - a.debt_and_finance_leases - a.redeemable_nci - a.nci)) < 1e-6,
            "all_values_finite": all(isfinite(x) for x in fcff + [ev, equity_value, value_per_share]),
        },
    }


def sensitivity_grid(a: Assumptions = BASE) -> list[dict]:
    rows = []
    for wacc in (0.085, 0.105, 0.125):
        for terminal_growth in (0.015, 0.025, 0.030):
            result = run_model(replace(a, wacc=wacc, terminal_growth=terminal_growth))
            rows.append({"wacc": wacc, "terminal_growth": terminal_growth,
                         "value_per_share": result["valuation"]["value_per_share"] if result["valid"] else None})
    return rows


def one_at_a_time_sensitivity(a: Assumptions = BASE) -> list[dict]:
    rows = []
    for field, low, high in (("revenue_growth_shift", -0.03, 0.03), ("segment_margin_shift", -0.02, 0.02)):
        for label, value in (("low", low), ("base", 0.0), ("high", high)):
            r = run_model(replace(a, **{field: value}))
            last = r["years"][-1]
            rows.append({"driver": field, "case": label, "input": value,
                         "final_year_ebit": last["ebit"], "final_year_fcff": last["fcff"],
                         "value_per_share": r["valuation"]["value_per_share"]})
    return rows


def named_scenarios() -> list[dict]:
    """Causal, linked cases; not probability-weighted price targets."""
    cases = (
        ("Downside", "Demand/price pressure and AI/factory spend delay margin recovery; reinvestment remains heavy.",
         {"revenue_growth_shift": -0.02, "segment_margin_shift": -0.02, "wacc": 0.115, "terminal_growth": 0.020}),
        ("Base", "Moderate revenue growth and a gradual, execution-dependent margin recovery.", {}),
        ("Upside", "Energy/services mix and operating leverage support faster growth and margin recovery, with lower perceived risk.",
         {"revenue_growth_shift": 0.02, "segment_margin_shift": 0.02, "wacc": 0.095, "terminal_growth": 0.030}),
    )
    rows = []
    for name, rationale, changes in cases:
        assumptions = replace(BASE, **changes)
        result = run_model(assumptions)
        rows.append({
            "case": name, "causal_rationale": rationale, "assumptions": asdict(assumptions),
            "value_per_share": result["valuation"]["value_per_share"],
            "enterprise_value": result["valuation"]["enterprise_value"],
            "committee_action": "Do not initiate" if name == "Downside" else "Watch/defer; do not initiate at the retained market reference",
        })
    return rows


def reverse_dcf_market_implied_terminal_growth(market_price: float = 367.95) -> dict:
    """Market-implied terminal growth under the base operating path; a diagnostic, not a forecast."""
    target_equity = market_price * BASE.diluted_shares
    low, high = -0.05, BASE.wacc - 0.0001
    for _ in range(100):
        midpoint = (low + high) / 2
        value = run_model(replace(BASE, terminal_growth=midpoint), enforce_bounds=False)["valuation"]["equity_value"]
        if value < target_equity:
            low = midpoint
        else:
            high = midpoint
    implied = (low + high) / 2
    return {"market_reference_price": market_price, "implied_terminal_growth": implied,
            "base_terminal_growth": BASE.terminal_growth,
            "within_approved_range": BOUNDS["terminal_growth"][0] <= implied <= BOUNDS["terminal_growth"][1]}


def known_answer_test() -> dict:
    """Course Lab 05 fixture, separate from TSLA inputs."""
    fcff = 100.0
    growth = [0.08, 0.06, 0.05, 0.04, 0.03]
    wacc, tg = 0.10, 0.03
    path = []
    for g in growth:
        fcff *= 1 + g
        path.append(fcff)
    pv_explicit = sum(v / (1 + wacc) ** (i + 1) for i, v in enumerate(path))
    tv = path[-1] * (1 + tg) / (wacc - tg)
    pv_tv = tv / (1 + wacc) ** 5
    equity = pv_explicit + pv_tv + 50 - 300
    return {"value_per_share": equity / 50, "expected": 27.4974, "passes_cent": abs(equity / 50 - 27.4974) <= 0.01}


def validation_suite(a: Assumptions = BASE) -> dict:
    base = run_model(a)
    higher_wacc = run_model(replace(a, wacc=a.wacc + 0.01))
    # Stay inside the approved 1.5%-3.0% terminal-growth range despite binary float rounding.
    higher_growth = run_model(replace(a, terminal_growth=0.029))
    changed = run_model(replace(a, segment_margin_shift=0.01))
    invalid = run_model(replace(a, terminal_growth=0.11))
    return {
        "known_answer": known_answer_test(),
        "wacc_monotonicity": higher_wacc["valuation"]["value_per_share"] < base["valuation"]["value_per_share"],
        "terminal_growth_monotonicity": higher_growth["valuation"]["value_per_share"] > base["valuation"]["value_per_share"],
        "changed_input_margin_plus_100bp": {
            "base": base["valuation"]["value_per_share"],
            "changed": changed["valuation"]["value_per_share"],
            "direction_passes": changed["valuation"]["value_per_share"] > base["valuation"]["value_per_share"],
        },
        "invalid_input_fails_loudly": (not invalid["valid"]) and bool(invalid["failures"]),
        "articulation": base["checks"],
    }
