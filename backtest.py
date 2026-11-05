"""Lagged card-spend signal backtest; standard library only."""

# Editable inputs
MONTHLY_DATA = """month,signal_pct,equity_return_pct
2024-12,0.8,
2025-01,1.2,2.0
2025-02,0.9,1.5
2025-03,1.5,3.0
2025-04,-1.0,-2.5
2025-05,-0.7,-1.5
2025-06,-1.4,-3.0
2025-07,1.1,2.5
2025-08,0.6,1.0
2025-09,0.9,2.0
2025-10,-0.9,-2.0
2025-11,-0.5,-1.0
2025-12,1.6,3.5
2026-01,-1.1,-2.0
2026-02,0.7,1.5
2026-03,-1.3,-3.0
2026-04,0.8,2.0
2026-05,-0.6,-1.5
2026-06,0.5,1.0
"""

LAG_MONTHS = 1
SWITCH_COST = 0.001       # 0.10%
BILLS_RETURN = 0.003      # 0.3% per month
DEVELOPMENT_MONTHS = ("2025-01", "2025-12")
HOLDOUT_MONTHS = ("2026-01", "2026-06")


def parse_data(text):
    """Turn the editable CSV text into rows with decimal returns."""
    rows = []
    for line in text.strip().splitlines()[1:]:
        month, signal, equity_return = line.split(",")
        rows.append(
            {
                "month": month,
                "signal": float(signal) / 100,
                "equity_return": None if not equity_return else float(equity_return) / 100,
            }
        )
    return rows


def in_period(month, period):
    return period[0] <= month <= period[1]


def run_period(rows, period, starting_position):
    """Backtest one period and return its ending position and performance."""
    gross_value = net_value = benchmark_value = 1.0
    position = starting_position
    switches = 0

    for index, row in enumerate(rows):
        if not in_period(row["month"], period):
            continue

        # A lagged signal makes this month's position decision.
        signal_index = index - LAG_MONTHS
        if signal_index < 0:
            raise ValueError("Not enough earlier signal data for the selected lag.")
        desired_position = "equity" if rows[signal_index]["signal"] > 0 else "bills"

        # A switch happens at the start of this month, before its return is earned.
        switched = desired_position != position
        if switched:
            switches += 1
            net_value *= 1 - SWITCH_COST
        position = desired_position

        monthly_return = row["equity_return"] if position == "equity" else BILLS_RETURN
        gross_value *= 1 + monthly_return
        net_value *= 1 + monthly_return
        benchmark_value *= 1 + row["equity_return"]

    return {
        "gross": gross_value - 1,
        "net": net_value - 1,
        "benchmark": benchmark_value - 1,
        "switches": switches,
        "ending_position": position,
    }


def print_results(label, result):
    print(label)
    print(f"  Rule gross: {result['gross'] * 100:.2f}%")
    print(f"  Rule net: {result['net'] * 100:.2f}%")
    print(f"  Buy-and-hold: {result['benchmark'] * 100:.2f}%")
    print(f"  Switches: {result['switches']}")


def main():
    rows = parse_data(MONTHLY_DATA)
    development = run_period(rows, DEVELOPMENT_MONTHS, starting_position="bills")
    # Holdout deliberately inherits the final development position.
    holdout = run_period(rows, HOLDOUT_MONTHS, development["ending_position"])

    print_results("Development", development)
    print_results("Holdout", holdout)

    if holdout["net"] < holdout["benchmark"]:
        difference = (holdout["benchmark"] - holdout["net"]) * 100
        print(f"Failure rule: triggered — holdout trails buy-and-hold by {difference:.2f} points.")
    else:
        print("Failure rule: not triggered.")


if __name__ == "__main__":
    main()
