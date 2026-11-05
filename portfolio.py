"""Calculate return, volatility, and reserve liquidity for three portfolios."""

import csv
import math
import statistics
import sys


# ================================ INPUTS =================================
# Rates and volatilities are decimals: 3.5% is entered as 0.035.
SLEEVES = [
    {"name": "Treasury bills", "expected_return": 0.035, "volatility": 0.005},
    {"name": "Treasury 10-year note", "expected_return": 0.043, "volatility": 0.070},
    {"name": "Investment-grade bond fund", "expected_return": 0.050, "volatility": 0.060},
    {"name": "Global equity index fund", "expected_return": 0.080, "volatility": 0.160},
]

CORRELATIONS = {
    "Treasury bills": {
        "Treasury bills": 1.00,
        "Treasury 10-year note": 0.10,
        "Investment-grade bond fund": 0.05,
        "Global equity index fund": 0.00,
    },
    "Treasury 10-year note": {
        "Treasury bills": 0.10,
        "Treasury 10-year note": 1.00,
        "Investment-grade bond fund": 0.80,
        "Global equity index fund": -0.10,
    },
    "Investment-grade bond fund": {
        "Treasury bills": 0.05,
        "Treasury 10-year note": 0.80,
        "Investment-grade bond fund": 1.00,
        "Global equity index fund": 0.25,
    },
    "Global equity index fund": {
        "Treasury bills": 0.00,
        "Treasury 10-year note": -0.10,
        "Investment-grade bond fund": 0.25,
        "Global equity index fund": 1.00,
    },
}

OBJECTIVE_RETURN = 0.065
RESERVE_ELIGIBLE = {"Treasury bills", "Treasury 10-year note"}
TICKERS = {
    "Treasury bills": "BIL",
    "Treasury 10-year note": "IEF",
    "Investment-grade bond fund": "LQD",
    "Global equity index fund": "ACWI",
}
# ===========================================================================


def sleeve_names(sleeves):
    """Return sleeve names in the order used for all portfolios and matrices."""
    return [sleeve["name"] for sleeve in sleeves]


def validate_correlations(correlations, names):
    """Raise ValueError if the correlation table is incomplete, invalid, or asymmetric."""
    for row_name in names:
        if row_name not in correlations:
            raise ValueError(f"correlation table is missing row: {row_name}")
        for column_name in names:
            if column_name not in correlations[row_name]:
                raise ValueError(f"correlation table is missing {row_name}/{column_name}")
            value = correlations[row_name][column_name]
            if not -1.0 <= value <= 1.0:
                raise ValueError(
                    f"correlation for {row_name}/{column_name} is {value}; it must be between -1 and 1"
                )
            opposite = correlations.get(column_name, {}).get(row_name)
            if opposite is None or not math.isclose(value, opposite, abs_tol=1e-12):
                raise ValueError(f"correlation table is not symmetric at {row_name}/{column_name}")


def build_covariance_matrix(sleeves, correlations):
    """Return covariance[name][name] = correlation × volatility × volatility."""
    volatilities = {sleeve["name"]: sleeve["volatility"] for sleeve in sleeves}
    names = sleeve_names(sleeves)
    return {
        left: {
            right: correlations[left][right] * volatilities[left] * volatilities[right]
            for right in names
        }
        for left in names
    }


def benchmark_weights(names):
    """Return the stated 40% IG-bond / 60% global-equity benchmark weights."""
    weights = {name: 0.0 for name in names}
    weights["Investment-grade bond fund"] = 0.40
    weights["Global equity index fund"] = 0.60
    return weights


def equal_weight_weights(names):
    """Return equal weights across all sleeves."""
    return {name: 1.0 / len(names) for name in names}


def inverse_volatility_weights(sleeves):
    """Return weights proportional to 1 divided by each sleeve's volatility."""
    inverse_volatilities = {
        sleeve["name"]: 1.0 / sleeve["volatility"] for sleeve in sleeves
    }
    total_inverse_volatility = sum(inverse_volatilities.values())
    return {
        name: inverse_volatility / total_inverse_volatility
        for name, inverse_volatility in inverse_volatilities.items()
    }


def portfolio_return(weights, sleeves):
    """Return the weighted expected return."""
    returns = {sleeve["name"]: sleeve["expected_return"] for sleeve in sleeves}
    return sum(weights[name] * returns[name] for name in weights)


def portfolio_variance(weights, covariance, names):
    """Return w'Covw, including every cross-sleeve covariance term."""
    return sum(
        weights[left] * covariance[left][right] * weights[right]
        for left in names
        for right in names
    )


def portfolio_volatility(weights, covariance, names):
    """Return the square root of portfolio variance."""
    return math.sqrt(portfolio_variance(weights, covariance, names))


def reserve_eligible_weight(weights, reserve_eligible):
    """Return the combined weight of the reserve-eligible sleeves."""
    return sum(weights[name] for name in reserve_eligible)


def search_lowest_risk_mix(
    sleeves,
    correlations,
    objective_return,
    reserve_eligible,
    minimum_reserve_eligible,
    step=0.05,
):
    """Search long-only step-size mixes and return the eligible one with lowest volatility.

    The result is a dictionary containing weights and portfolio measures, or None
    when no evaluated mix meets both constraints.
    """
    if step <= 0 or not math.isclose(1.0 / step, round(1.0 / step)):
        raise ValueError("step must divide evenly into 100%")
    names = sleeve_names(sleeves)
    validate_correlations(correlations, names)
    covariance = build_covariance_matrix(sleeves, correlations)
    total_steps = round(1.0 / step)
    best = None

    def try_weights(position, remaining, units):
        nonlocal best
        if position == len(names) - 1:
            candidate_units = units + [remaining]
            weights = {
                name: unit_count * step
                for name, unit_count in zip(names, candidate_units)
            }
            expected = portfolio_return(weights, sleeves)
            reserve_weight = reserve_eligible_weight(weights, reserve_eligible)
            if expected + 1e-12 < objective_return or reserve_weight + 1e-12 < minimum_reserve_eligible:
                return
            volatility = portfolio_volatility(weights, covariance, names)
            result = {
                "weights": weights,
                "expected_return": expected,
                "volatility": volatility,
                "reserve_eligible_weight": reserve_weight,
            }
            if best is None or volatility < best["volatility"] - 1e-12:
                best = result
            return
        for unit_count in range(remaining + 1):
            try_weights(position + 1, remaining - unit_count, units + [unit_count])

    try_weights(0, total_steps, [])
    return best


def estimate_from_prices(csv_source, last_36_months=False):
    """Estimate annualized return, volatility, and correlations from monthly prices.

    Expected returns are historical annualized estimates (mean monthly return times
    12), not forecasts. ``csv_source`` may be a file path or a text file object.
    """
    close_after_read = False
    if isinstance(csv_source, (str, bytes)):
        source = open(csv_source, "r", newline="", encoding="utf-8")
        close_after_read = True
    else:
        source = csv_source
        if hasattr(source, "seek"):
            source.seek(0)
    try:
        rows = list(csv.DictReader(source))
    finally:
        if close_after_read:
            source.close()
    if not rows or not rows[0] or "date" not in rows[0]:
        raise ValueError("CSV must have a date column followed by one or more tickers")
    tickers = [column for column in rows[0] if column != "date"]
    if not tickers:
        raise ValueError("CSV must contain at least one price column")
    try:
        prices = {ticker: [float(row[ticker]) for row in rows] for ticker in tickers}
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("all price cells must be numeric") from error
    if any(price <= 0 for series in prices.values() for price in series):
        raise ValueError("prices must be positive")
    monthly_returns = {
        ticker: [series[index] / series[index - 1] - 1.0 for index in range(1, len(series))]
        for ticker, series in prices.items()
    }
    if last_36_months:
        monthly_returns = {ticker: series[-36:] for ticker, series in monthly_returns.items()}
    observations = len(next(iter(monthly_returns.values())))
    if observations < 2:
        raise ValueError("CSV needs at least three monthly prices (37 for a 36-month estimate)")
    expected_returns = {
        ticker: statistics.fmean(series) * 12.0 for ticker, series in monthly_returns.items()
    }
    volatilities = {
        ticker: statistics.stdev(series) * math.sqrt(12.0) for ticker, series in monthly_returns.items()
    }
    correlations = {}
    for left in tickers:
        correlations[left] = {}
        for right in tickers:
            if left == right:
                correlations[left][right] = 1.0
                continue
            left_deviations = [value - statistics.fmean(monthly_returns[left]) for value in monthly_returns[left]]
            right_deviations = [value - statistics.fmean(monthly_returns[right]) for value in monthly_returns[right]]
            covariance = sum(a * b for a, b in zip(left_deviations, right_deviations)) / (observations - 1)
            denominator = statistics.stdev(monthly_returns[left]) * statistics.stdev(monthly_returns[right])
            correlations[left][right] = covariance / denominator if denominator else 0.0
    return {
        "tickers": tickers,
        "expected_returns": expected_returns,
        "volatilities": volatilities,
        "correlations": correlations,
        "observations": observations,
    }


def format_weights(weights, names):
    """Format portfolio weights in the fixed sleeve order."""
    return " / ".join(f"{weights[name] * 100:.1f}" for name in names)


def print_portfolio(name, weights, sleeves, covariance, names):
    """Print all requested portfolio measures."""
    expected_return = portfolio_return(weights, sleeves)
    volatility = portfolio_volatility(weights, covariance, names)
    reserve_weight = reserve_eligible_weight(weights, RESERVE_ELIGIBLE)
    meets_objective = expected_return >= OBJECTIVE_RETURN

    print(f"\n{name}")
    print(f"Weights (bills / 10-year / IG / equity): {format_weights(weights, names)}%")
    print(f"Expected return: {expected_return * 100:.2f}%")
    print(f"Volatility: {volatility * 100:.2f}%")
    print(f"Reserve-eligible weight: {reserve_weight * 100:.1f}%")
    print(f"Meets {OBJECTIVE_RETURN * 100:.1f}% objective: {'yes' if meets_objective else 'no'}")


def main():
    names = sleeve_names(SLEEVES)
    validate_correlations(CORRELATIONS, names)
    covariance = build_covariance_matrix(SLEEVES, CORRELATIONS)
    portfolios = {
        "Benchmark": benchmark_weights(names),
        "Equal weight": equal_weight_weights(names),
        "Inverse volatility": inverse_volatility_weights(SLEEVES),
    }
    for name, weights in portfolios.items():
        print_portfolio(name, weights, SLEEVES, covariance, names)


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        print(f"Input error: {error}", file=sys.stderr)
        sys.exit(1)
