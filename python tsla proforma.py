"""Tesla FY2025 to FY2026E-FY2030E segmented pro-forma (USD millions).

Educational model only; assumptions are documented in lab10_tsla_submission.md.
"""

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
    "capex": [21000.0, None, None, None, None], "capex_pct_later": 0.08,
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
        capex = ASSUMPTIONS["capex"][i] or revenue * ASSUMPTIONS["capex_pct_later"]
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


def main():
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


if __name__ == "__main__":
    main()
