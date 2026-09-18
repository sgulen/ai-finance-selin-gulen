"""Lab 06 FCFF DCF: base case, sensitivity grid, and reverse DCF.

Run with the training case first. After it matches the Lab 6 checkpoints, change
ACTIVE_CASE to "company" and personally replace/verify every company input and source.
All dollar inputs are USD millions; shares are millions; per-share values are USD.
"""

# ========================= LAB 6 CONTROLS =========================
ACTIVE_CASE = "company"  
WACC_VALUES = [0.09, 0.10, 0.11]
TERMINAL_GROWTH_VALUES = [0.02, 0.03, 0.04]
SHIFT_LOWER_BOUND = -0.05
SHIFT_UPPER_BOUND = 1.00
# ===================================================================

TRAINING_INPUTS = {
    "name": "Training case",
    "starting_fcff": 100.0,
    "growth_rates": [0.08, 0.06, 0.05, 0.04, 0.03],
    "wacc": 0.10,
    "terminal_growth": 0.03,
    "cash": 50.0,
    "debt": 300.0,
    "diluted_shares": 50.0,
    "target_share_price": 30.00,
}

# These are the values previously in this file. They are not independently
# verified by this script; check every one against your own filed-source table.
COMPANY_INPUTS = {
    "name": "Tesla (TSLA) - FY2025 base case",
    "starting_fcff": 6433.0,
    "growth_rates": [0.14, 0.12, 0.10, 0.08, 0.06],
    "wacc": 0.105,
    "terminal_growth": 0.03,
    "cash": 44059.0,
    "debt": 8177.0,
    "diluted_shares": 3528.0,
    "target_share_price": 366.20,
}


def validate_inputs(inputs):
    growth_rates = inputs["growth_rates"]
    if len(growth_rates) != 5:
        raise ValueError("Exactly five explicit annual growth rates are required.")
    if inputs["wacc"] <= 0:
        raise ValueError("WACC must be positive.")
    if inputs["terminal_growth"] >= inputs["wacc"]:
        raise ValueError("Terminal growth must be less than WACC.")
    if inputs["diluted_shares"] <= 0:
        raise ValueError("Diluted shares must be positive.")
    if any(growth <= -1.0 for growth in growth_rates):
        raise ValueError("No annual growth rate may be -100% or lower.")


def value_dcf(inputs, wacc=None, terminal_growth=None, growth_rates=None):
    """Return the core DCF output calculated from one consistent input set."""
    working = dict(inputs)
    working["wacc"] = inputs["wacc"] if wacc is None else wacc
    working["terminal_growth"] = (
        inputs["terminal_growth"] if terminal_growth is None else terminal_growth
    )
    working["growth_rates"] = (
        list(inputs["growth_rates"]) if growth_rates is None else list(growth_rates)
    )
    validate_inputs(working)

    fcff = []
    current_fcff = working["starting_fcff"]
    for growth in working["growth_rates"]:
        current_fcff *= 1.0 + growth
        fcff.append(current_fcff)

    pv_explicit_fcff = sum(
        cash_flow / ((1.0 + working["wacc"]) ** year)
        for year, cash_flow in enumerate(fcff, start=1)
    )
    terminal_value_year_5 = (
        fcff[-1] * (1.0 + working["terminal_growth"])
        / (working["wacc"] - working["terminal_growth"])
    )
    pv_terminal_value = terminal_value_year_5 / ((1.0 + working["wacc"]) ** 5)
    enterprise_value = pv_explicit_fcff + pv_terminal_value
    equity_value = enterprise_value + working["cash"] - working["debt"]
    value_per_share = equity_value / working["diluted_shares"]

    return {
        "fcff": fcff,
        "pv_explicit_fcff": pv_explicit_fcff,
        "terminal_value_year_5": terminal_value_year_5,
        "pv_terminal_value": pv_terminal_value,
        "enterprise_value": enterprise_value,
        "equity_value": equity_value,
        "value_per_share": value_per_share,
        "terminal_value_share_of_ev": pv_terminal_value / enterprise_value,
    }


def print_twelve_lines(results):
    print("BASE-CASE DCF")
    for year, cash_flow in enumerate(results["fcff"], start=1):
        print(f"FCFF Year {year}: {cash_flow:.4f}")
    print(f"Present value of the explicit FCFF: {results['pv_explicit_fcff']:.4f}")
    print(f"Terminal value at Year 5: {results['terminal_value_year_5']:.4f}")
    print(f"Present value of the terminal value: {results['pv_terminal_value']:.4f}")
    print(f"Enterprise value: {results['enterprise_value']:.4f}")
    print(f"Equity value: {results['equity_value']:.4f}")
    print(f"Value per diluted share: {results['value_per_share']:.4f}")
    print(
        "Present value of the terminal value as a share of enterprise value: "
        f"{results['terminal_value_share_of_ev']:.4f}"
    )


def print_sensitivity_grid(inputs):
    print("\nSENSITIVITY GRID: value per diluted share ($)")
    header = "WACC \\ terminal growth | " + " | ".join(
        f"{growth:.1%}" for growth in TERMINAL_GROWTH_VALUES
    )
    print(header)
    print("-" * len(header))
    for wacc in WACC_VALUES:
        cells = []
        for terminal_growth in TERMINAL_GROWTH_VALUES:
            if terminal_growth >= wacc:
                cells.append("invalid")
            else:
                per_share = value_dcf(inputs, wacc, terminal_growth)["value_per_share"]
                cells.append(f"{per_share:.2f}")
        print(f"{wacc:.1%}                  | " + " | ".join(cells))


def solve_growth_shift(inputs):
    """Use bisection to find a uniform shift to all five explicit growth rates."""
    target = inputs["target_share_price"]

    def price_at(shift):
        shifted_rates = [rate + shift for rate in inputs["growth_rates"]]
        if any(rate <= -1.0 for rate in shifted_rates):
            raise ValueError("Shift makes an annual growth rate -100% or lower.")
        return value_dcf(inputs, growth_rates=shifted_rates)["value_per_share"]

    try:
        lower_price = price_at(SHIFT_LOWER_BOUND)
        upper_price = price_at(SHIFT_UPPER_BOUND)
    except ValueError as error:
        return None, str(error), None, None

    if not min(lower_price, upper_price) <= target <= max(lower_price, upper_price):
        return None, "Target is outside the stated bracket.", lower_price, upper_price

    low, high = SHIFT_LOWER_BOUND, SHIFT_UPPER_BOUND
    increasing = upper_price > lower_price
    for _ in range(200):
        midpoint = (low + high) / 2.0
        midpoint_price = price_at(midpoint)
        if abs(midpoint_price - target) < 0.000001:
            return midpoint, None, lower_price, upper_price
        if (midpoint_price < target) == increasing:
            low = midpoint
        else:
            high = midpoint
    return (low + high) / 2.0, None, lower_price, upper_price


def print_reverse_dcf(inputs):
    shift, error, lower_price, upper_price = solve_growth_shift(inputs)
    print("\nREVERSE DCF")
    if error:
        print("No solution in the stated bracket; no bound is reported as the answer.")
        print(f"Reason: {error}")
        print(f"Target share price: ${inputs['target_share_price']:.2f}")
        if lower_price is not None:
            print(f"Reachable prices: ${lower_price:.2f} to ${upper_price:.2f}")
        return
    print(f"Solved uniform growth-rate shift: {shift:+.2%}")
    print(f"Target share price: ${inputs['target_share_price']:.2f}")
    print("Held fixed: starting FCFF, WACC, terminal growth, cash, debt, diluted shares,")
    print("and the bridge; only the uniform shift to all five explicit growth rates changes.")


def main():
    if ACTIVE_CASE not in {"training", "company"}:
        raise ValueError('ACTIVE_CASE must be "training" or "company".')
    inputs = TRAINING_INPUTS if ACTIVE_CASE == "training" else COMPANY_INPUTS
    print(f"{inputs['name']} — all dollar amounts are USD millions except per-share values.\n")
    print_twelve_lines(value_dcf(inputs))
    print_sensitivity_grid(inputs)
    print_reverse_dcf(inputs)


if __name__ == "__main__":
    main()
