"""Terminal interface for the TSLA Valuation Workbench."""
import argparse
import json
from dataclasses import replace
from pathlib import Path

from src.model import BASE, BOUNDS, named_scenarios, one_at_a_time_sensitivity, reverse_dcf_market_implied_terminal_growth, run_model, sensitivity_grid, validation_suite


ROOT = Path(__file__).resolve().parent


def money(value):
    return f"${value:,.1f}M"


def show(result):
    if not result["valid"]:
        print("\nCHECK FAILED - valuation not calculated")
        for failure in result["failures"]:
            print(f"  - {failure}")
        return
    v = result["valuation"]
    print("\nTSLA VALUATION WORKBENCH | USD millions except per share")
    print(f"Enterprise value: {money(v['enterprise_value'])}")
    print(f"Equity value:     {money(v['equity_value'])}")
    print(f"Value per share:  ${v['value_per_share']:,.2f}")
    print(f"Terminal value share of EV: {v['terminal_value_share']:.1%}")
    print("\nYear    Revenue     EBIT       FCFF       Cash       BS check")
    for y in result["years"]:
        print(f"{y['year']}  {money(y['revenue']):>10} {money(y['ebit']):>10} {money(y['fcff']):>10} {money(y['cash']):>10} {y['balance_check']:>10.2f}")
    print("\nCHECKS")
    for k, value in result["checks"].items():
        print(f"  {'PASS' if value is True or value == 0 else value} - {k.replace('_', ' ')}")


def report():
    result = run_model(BASE)
    show(result)
    print("\nWACC / terminal-growth sensitivity ($ per share)")
    for row in sensitivity_grid():
        print(f"  WACC {row['wacc']:.1%}; g {row['terminal_growth']:.1%}: ${row['value_per_share']:,.2f}")
    print("\nOne-at-a-time sensitivities")
    for row in one_at_a_time_sensitivity():
        print(f"  {row['driver']} {row['case']}: EBIT {money(row['final_year_ebit'])}, FCFF {money(row['final_year_fcff'])}, value ${row['value_per_share']:,.2f}")
    print("\nNamed causal scenarios")
    for row in named_scenarios():
        print(f"  {row['case']}: ${row['value_per_share']:,.2f} per share | {row['causal_rationale']}")
    reverse = reverse_dcf_market_implied_terminal_growth()
    print(f"\nMarket-implied terminal growth at ${reverse['market_reference_price']:,.2f}: {reverse['implied_terminal_growth']:.1%} (outside approved range: {not reverse['within_approved_range']})")
    print("\nValidation")
    for key, value in validation_suite().items():
        print(f"  {key}: {value}")


def write_output():
    result = run_model(BASE)
    scenarios = named_scenarios()
    reverse = reverse_dcf_market_implied_terminal_growth()
    payload = {"as_of": "2025-12-31", "currency_and_scale": "USD millions except per share", "decision": "Watch/defer; do not initiate at the retained 2026-09-10 market reference without stronger operating-return evidence.", "base_result": result, "sensitivity_grid": sensitivity_grid(), "one_at_a_time": one_at_a_time_sensitivity(), "named_scenarios": scenarios, "reverse_dcf": reverse, "validation": validation_suite()}
    out = ROOT / "output"
    out.mkdir(exist_ok=True)
    (out / "visible_output.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    v = result["valuation"]
    lines = ["# TSLA Valuation Workbench - Visible Executed Output", "", "**Run:** `py -3 app.py --write-output`", "**As of:** 2025-12-31 (financial statements/bridge); USD millions except per share.", "", "## Decision", "Watch/defer; do not initiate at the retained September 10, 2026 market reference until margin and reinvestment evidence improves.", "", "## Base DCF", f"- Enterprise value: {money(v['enterprise_value'])}", f"- Equity value: {money(v['equity_value'])}", f"- Value per diluted share: ${v['value_per_share']:,.2f}", f"- Terminal value share of EV: {v['terminal_value_share']:.1%}", "", "## Named causal scenarios"]
    lines.extend([f"- {row['case']}: ${row['value_per_share']:,.2f} per share; action: {row['committee_action']} — {row['causal_rationale']}" for row in scenarios])
    lines.extend(["", "## Market-implied expectation", f"- At the retained ${reverse['market_reference_price']:,.2f} market reference, the base operating path requires a {reverse['implied_terminal_growth']:.1%} terminal growth rate, versus the approved 1.5%-3.0% range. This is a diagnostic, not a forecast."])
    lines.extend(["", "## Check results", f"- Balance-sheet maximum error: {result['checks']['balance_sheet_max_abs_error']:.2f}", f"- Cash-flow tie: {result['checks']['cash_flow_ties_to_cash']}", f"- Bridge reconciliation: {result['checks']['bridge_reconciles']}", f"- Course known-answer test: {validation_suite()['known_answer']['passes_cent']}", "", "## Important limitation", "The DCF is primary evidence. The saved TSLA/GM comparable workpaper is a qualified triangulation, not an averaged target."])
    (out / "visible_output.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out / 'visible_output.json'} and {out / 'visible_output.md'}")


def interactive():
    a = BASE
    print("TSLA Valuation Workbench. Exposed drivers are bounded; enter r to reset or q to quit.")
    while True:
        print("\nCurrent drivers:")
        for field, (low, high) in BOUNDS.items():
            print(f"  {field}: {getattr(a, field):.2%} (approved range {low:.1%} to {high:.1%})")
        show(run_model(a))
        choice = input("\nChange driver name, r, or q: ").strip()
        if choice.lower() == "q":
            return
        if choice.lower() == "r":
            a = BASE
            continue
        if choice not in BOUNDS:
            print("Unknown driver. Choose a displayed driver.")
            continue
        try:
            value = float(input("Enter decimal (e.g., 0.01 for 1%): ").strip())
        except ValueError:
            print("CHECK FAILED - enter a decimal number.")
            continue
        a = replace(a, **{choice: value})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--write-output", action="store_true")
    parser.add_argument("--interactive", action="store_true")
    args = parser.parse_args()
    if args.write_output:
        write_output()
    elif args.interactive:
        interactive()
    else:
        report()
