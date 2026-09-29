"""Tesla FY2025 to FY2026E-FY2030E segmented pro-forma (USD millions).

Educational model only; assumptions are documented in lab10_tsla_submission.md.
"""

from copy import deepcopy
from math import isfinite

YEARS = [2026, 2027, 2028, 2029, 2030]

# Tesla FY2025 10-K, pp. 49-50 and MD&A p. 31 (USD millions).
OPENING = {
    "cash": 16513.0, "investments": 27546.0, "ar": 4576.0,
    "inventory": 12392.0, "ppe": 40643.0, "other_assets": 36136.0,
    "ap": 13371.0, "other_liabilities": 33194.0, "debt": 8376.0,
    "equity": 82865.0, "revolver": 0.0,
    "segment_revenue": {"auto": 69526.0, "energy": 12771.0, "services": 12530.0},
}

ASSUMPTIONS = {
    # The company-specific line: segments grow and earn different margins.
    "segment_growth": {
        "auto": [0.04, 0.05, 0.05, 0.04, 0.03],
        "energy": [0.25, 0.20, 0.15, 0.12, 0.10],
        "services": [0.12, 0.10, 0.08, 0.06, 0.05],
    },
    "segment_margin": {
        "auto": [0.180, 0.182, 0.185, 0.187, 0.190],
        "energy": [0.295, 0.300, 0.305, 0.310, 0.315],
        "services": [0.080, 0.085, 0.090, 0.095, 0.100],
    },
    "rd_pct_revenue": [0.064, 0.062, 0.060, 0.058, 0.056],
    "sga_pct_revenue": [0.061, 0.060, 0.059, 0.058, 0.057],
    "da_pct_opening_ppe": 0.1513, "sbc_pct_revenue": 0.030,
     # Total base capex remains $21bn in 2026 and8% of revenue thereafter.
  "base_capex": [16000.0, None, None, None,None],
  "base_capex_pct_later": 0.06,

  # Independent AI/autonomy operating driver.
  "ai_autonomy_capex": [5000.0, None, None,
  None, None],
  "ai_autonomy_capex_pct_later": 0.02,
    "tax_rate": 0.2696, "ar_pct_revenue": 0.0483, "inventory_days": 58.2,
    "other_assets_pct_revenue": 0.3811, "ap_pct_cogs": 0.1720,
    "other_liabilities_pct_revenue": 0.3501,
    "minimum_cash": 5000.0, "revolver_limit": 6430.0, "revolver_rate": 0.0404,
    "scheduled_debt_repayment": 1580.0, "buyback": 0.0,
    "debt_rate": 0.0404, "cash_yield": 0.0381,
    "cost_of_equity": 0.105, "terminal_growth": 0.030,
}
SHARES_OUTSTANDING = 3751.0


def project():
    state, rows = dict(OPENING), []
    for i, year in enumerate(YEARS):
        segment_revenue = {
            name: prior * (1 + ASSUMPTIONS["segment_growth"][name][i])
            for name, prior in state["segment_revenue"].items()
        }
        segment_gp = {
            name: segment_revenue[name] * ASSUMPTIONS["segment_margin"][name][i]
            for name in segment_revenue
        }
        revenue, gross_profit = sum(segment_revenue.values()), sum(segment_gp.values())
        cogs = revenue - gross_profit
        rd, sga = revenue * ASSUMPTIONS["rd_pct_revenue"][i], revenue * ASSUMPTIONS["sga_pct_revenue"][i]
        depreciation = state["ppe"] * ASSUMPTIONS["da_pct_opening_ppe"]
        # D&A is already in segment cost of revenue, so it is not deducted again here.
        operating_income = gross_profit - rd - sga
        interest_expense = state["debt"] * ASSUMPTIONS["debt_rate"] + state["revolver"] * ASSUMPTIONS["revolver_rate"]
        interest_income = (state["cash"] + state["investments"]) * ASSUMPTIONS["cash_yield"]
        pretax_income = operating_income + interest_income - interest_expense
        tax = max(0.0, pretax_income) * ASSUMPTIONS["tax_rate"]
        net_income, sbc = pretax_income - tax, revenue * ASSUMPTIONS["sbc_pct_revenue"]

        ar = revenue * ASSUMPTIONS["ar_pct_revenue"]
        inventory = cogs * ASSUMPTIONS["inventory_days"] / 365
        other_assets = revenue * ASSUMPTIONS["other_assets_pct_revenue"]
        ap, other_liabilities = cogs * ASSUMPTIONS["ap_pct_cogs"], revenue * ASSUMPTIONS["other_liabilities_pct_revenue"]
        base_capex = (ASSUMPTIONS["base_capex"][i] or revenue * ASSUMPTIONS["base_capex_pct_later"])
        ai_autonomy_capex = (ASSUMPTIONS["ai_autonomy_capex"][i] or revenue * ASSUMPTIONS["ai_autonomy_capex_pct_later"])
        capex = base_capex + ai_autonomy_capex
        ppe = state["ppe"] + capex - depreciation
        repayment = min(ASSUMPTIONS["scheduled_debt_repayment"], state["debt"])
        debt, equity = state["debt"] - repayment, state["equity"] + net_income + sbc - ASSUMPTIONS["buyback"]

        fcfe_before_revolver = (net_income + depreciation + sbc - capex
            - (ar - state["ar"]) - (inventory - state["inventory"])
            - (other_assets - state["other_assets"]) + (ap - state["ap"])
            + (other_liabilities - state["other_liabilities"]) - repayment - ASSUMPTIONS["buyback"])
        cash_before_revolver = state["cash"] + fcfe_before_revolver
        revolver_change = 0.0
        revolver = state["revolver"]
        if cash_before_revolver < ASSUMPTIONS["minimum_cash"]:
            revolver_change = ASSUMPTIONS["minimum_cash"] - cash_before_revolver
            if revolver + revolver_change > ASSUMPTIONS["revolver_limit"]:
                raise ValueError(f"FY{year}E needs more than the $6.43bn revolver limit.")
            revolver += revolver_change
        elif revolver:
            revolver_change = -min(revolver, cash_before_revolver - ASSUMPTIONS["minimum_cash"])
            revolver += revolver_change
        cash, fcfe = cash_before_revolver + revolver_change, fcfe_before_revolver + revolver_change
        assets = cash + state["investments"] + ar + inventory + other_assets + ppe
        liabilities = ap + other_liabilities + debt + revolver
        gap = assets - liabilities - equity
        if abs(gap) > 0.05 or cash < ASSUMPTIONS["minimum_cash"] - 0.05:
            raise ValueError(f"FY{year}E check failed: balance gap {gap:,.1f}; cash {cash:,.1f}.")
        row = locals().copy()
        row.update({"auto_rev": segment_revenue["auto"], "energy_rev": segment_revenue["energy"],
                    "services_rev": segment_revenue["services"]})
        rows.append(row)
        state = {"cash": cash, "investments": state["investments"], "ar": ar, "inventory": inventory,
                 "ppe": ppe, "other_assets": other_assets, "ap": ap, "other_liabilities": other_liabilities,
                 "debt": debt, "equity": equity, "revolver": revolver, "segment_revenue": segment_revenue}
    return rows


def show(title, rows, lines):
    print("\n" + title)
    print(f"{'USD millions':<33} | " + " | ".join(map(str, YEARS)))
    print("-" * 90)
    for label, key in lines:
        print(f"{label:<33} | " + " | ".join(f"{r[key]:,.1f}" for r in rows))


def proforma_main():
    rows = project()
    print("Tesla FY2025 to FY2026E-FY2030E segmented pro-forma")
    show("SEGMENT REVENUE", rows, [("Automotive", "auto_rev"), ("Energy generation & storage", "energy_rev"), ("Services & other", "services_rev"), ("Total revenue", "revenue")])
    show("INCOME STATEMENT", rows, [("Gross profit", "gross_profit"), ("R&D", "rd"), ("SG&A", "sga"), ("Operating income", "operating_income"), ("Net income", "net_income")])
    show("CHECKS", rows, [("Assets - liabilities - equity", "gap"), ("Cash", "cash"), ("Revolver", "revolver"), ("FCFE", "fcfe")])
    ke, growth = ASSUMPTIONS["cost_of_equity"], ASSUMPTIONS["terminal_growth"]
    pv_explicit = sum(r["fcfe"] / (1 + ke) ** (i + 1) for i, r in enumerate(rows))
    terminal_fcfe = rows[-1]["fcfe"] + rows[-1]["repayment"]
    pv_terminal = terminal_fcfe * (1 + growth) / (ke - growth) / (1 + ke) ** len(rows)
    equity_value = pv_explicit + pv_terminal
    print("\nVALUATION")
    print(f"Equity value: ${equity_value:,.1f}m")
    print(f"Value per share: ${equity_value / SHARES_OUTSTANDING:,.2f}")
    print(f"Share of value after 2030: {pv_terminal / equity_value:.1%}")


# The stated scenario paths; only one selected independent driver changes per run.
SENSITIVITIES = {
    "AI/autonomy capex": {
        "unit": "USD millions",
        "low": [4000.0, 1657.7, 1776.3, 1878.8, 1966.4],
        "high": [6000.0, 2762.9, 2960.5, 3131.3, 3277.3],
    },
    "Automotive gross margin": {
        "unit": "% of automotive revenue",
        "low": [0.165, 0.167, 0.170, 0.172, 0.175],
        "high": [0.195, 0.197, 0.200, 0.202, 0.205],
    },
}
BASE_ASSUMPTIONS = deepcopy(ASSUMPTIONS)


def value_per_share(rows, assumptions):
    """Return the existing FCFE valuation or a reason it is unavailable."""
    ke, g, shares = (assumptions["cost_of_equity"], assumptions["terminal_growth"],
                     SHARES_OUTSTANDING)
    if not all(isfinite(x) for x in (ke, g, shares)):
        return None, "discount rate, terminal growth, or share count is not finite"
    if ke <= g:
        return None, "cost of equity must exceed terminal growth"
    if shares <= 0:
        return None, "share count must be positive"
    pv_explicit = sum(row["fcfe"] / (1 + ke) ** (i + 1) for i, row in enumerate(rows))
    terminal_fcfe = rows[-1]["fcfe"] + rows[-1]["repayment"]
    equity_value = pv_explicit + (terminal_fcfe * (1 + g) / (ke - g)
                                  / (1 + ke) ** len(rows))
    return equity_value / shares, None


def apply_driver(assumptions, driver, values):
    if driver == "AI/autonomy capex":
        # Fixed dollar inputs make the specified annual values directly visible.
        assumptions["ai_autonomy_capex"] = list(values)
    elif driver == "Automotive gross margin":
        assumptions["segment_margin"]["auto"] = list(values)


def actual_inputs(driver, rows, assumptions):
    if driver == "AI/autonomy capex":
        return [row["ai_autonomy_capex"] for row in rows]
    return list(assumptions["segment_margin"]["auto"])


def run_case(driver, values=None):
    global ASSUMPTIONS
    """Fresh, independent run: reset every nonselected assumption to base."""
    assumptions = deepcopy(BASE_ASSUMPTIONS)
    ASSUMPTIONS = assumptions
    try:
        if values is not None:
            apply_driver(assumptions, driver, values)
        rows = project()
        max_gap = max(abs(row["gap"]) for row in rows)
        if max_gap > 0.05:
            raise ValueError(f"maximum balance-sheet gap is ${max_gap:,.2f}m")
        per_share, limitation = value_per_share(rows, assumptions)
        final = rows[-1]
        return {
            "valid": True, "error": None, "valuation_limitation": limitation,
            "inputs": actual_inputs(driver, rows, assumptions), "rows": rows,
            "operating_income": final["operating_income"], "fcfe": final["fcfe"],
            "value_per_share": per_share, "max_gap": max_gap,
        }
    except Exception as error:
        # Invalid scenarios remain visible, but are excluded from spans/ranking.
        return {
            "valid": False, "error": str(error), "valuation_limitation": None,
            "inputs": list(values) if values is not None else None, "rows": [],
            "operating_income": None, "fcfe": None, "value_per_share": None,
            "max_gap": None,
        }
    finally:
        ASSUMPTIONS = deepcopy(BASE_ASSUMPTIONS)


def inputs_text(driver, values):
    if values is None:
        return "not available"
    if driver == "AI/autonomy capex":
        return ", ".join(f"${value:,.1f}m" for value in values)
    return ", ".join(f"{value:.1%}" for value in values)


def money(value):
    return "N/A" if value is None else f"${value:,.1f}m"


def per_share(value):
    return "N/A" if value is None else f"${value:,.2f}"


def change(value, base, suffix="m", dollar=True):
    if value is None or base is None:
        return "N/A"
    prefix = "$" if dollar else ""
    return f"{prefix}{value - base:+,.2f}{suffix}"


def case_line(label, result, base):
    if not result["valid"]:
        print(f"{label:<6} | INVALID | {result['error']}")
        return
    print(
        f"{label:<6} | {money(result['operating_income']):>14} | "
        f"{change(result['operating_income'], base['operating_income']):>13} | "
        f"{money(result['fcfe']):>14} | "
        f"{change(result['fcfe'], base['fcfe']):>13} | "
        f"{per_share(result['value_per_share']):>11} | "
        f"{change(result['value_per_share'], base['value_per_share'], suffix='', dollar=True):>9} | "
        f"{result['max_gap']:>7.2f}"
    )


def span(cases, key):
    values = [result[key] for _, result in cases
              if result["valid"] and result[key] is not None]
    return None if not values else max(values) - min(values)


def print_trace(label, result):
    """Final-year linked statement detail retained for tracing a selected case."""
    if not result["valid"]:
        return
    row = result["rows"][-1]
    print(
        f"  {label} FY{row['year']}E trace (USD millions): revenue ${row['revenue']:,.1f}; "
        f"gross profit ${row['gross_profit']:,.1f}; R&D ${row['rd']:,.1f}; "
        f"SG&A ${row['sga']:,.1f}; operating profit ${row['operating_income']:,.1f}; "
        f"net income ${row['net_income']:,.1f}; capex ${row['capex']:,.1f}; "
        f"FCFE ${row['fcfe']:,.1f}; cash ${row['cash']:,.1f}; revolver "
        f"${row['revolver']:,.1f}; balance gap ${row['gap']:,.2f}."
    )


def sensitivity_main():
    print("Tesla Lab 11 - One-at-a-Time Sensitivity Analysis")
    print("Outputs: FY2030E operating profit, FCFE, and FCFE value per share when valid.")

    for driver, setting in SENSITIVITIES.items():
        # Every lower, base, and higher case is a separate fresh model run.
        lower = run_case(driver, setting["low"])
        base = run_case(driver)
        higher = run_case(driver, setting["high"])
        cases = [("Lower", lower), ("Base", base), ("Higher", higher)]

        print("\n" + driver)
        print("Years:", " - ".join(f"FY{year}E" for year in YEARS))
        print("Unit:", setting["unit"])
        for label, result in cases:
            print(f"  {label} actual inputs: {inputs_text(driver, result['inputs'])}")
        print("Case   | Op. profit     | Change base        | FCFE           | Change base        | Value/share | Change base   | Max gap")
        print("-" * 116)
        for label, result in cases:
            case_line(label, result, base)

        print("Spans across valid lower/base/higher cases:")
        print(f"  Operating profit: {money(span(cases, 'operating_income'))}")
        print(f"  FCFE: {money(span(cases, 'fcfe'))}")
        valuation_span = span(cases, "value_per_share")
        if valuation_span is None:
            limitation = next((result["valuation_limitation"] for _, result in cases
                               if result["valuation_limitation"]),
                              "valuation unavailable in valid cases")
            print(f"  Value per share: unavailable - {limitation}")
        else:
            print(f"  Value per share: ${valuation_span:,.2f}")
        for label, result in cases:
            if result["valid"] and result["valuation_limitation"]:
                print(f"  {label} valuation unavailable - {result['valuation_limitation']}")
            print_trace(label, result)

    # Restore the stored base inputs and rerun them as a final control.
    reference_base = run_case("AI/autonomy capex")
    restored = run_case("AI/autonomy capex")
    restored_match = reference_base["valid"] and restored["valid"] and all(abs(restored[key] - reference_base[key]) < 0.005 for key in ("operating_income", "fcfe", "value_per_share"))
    print("\nRESTORED-BASE CHECK:", "PASS" if restored_match else "FAIL")
    if restored["valid"]:
        print_trace("Restored base", restored)
    else:
        print("  Restored base invalid:", restored["error"])




if __name__ == "__main__":
    proforma_main()
    sensitivity_main()