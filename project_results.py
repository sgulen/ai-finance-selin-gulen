"""Single source of truth for the Project 2 allocation results."""

from pathlib import Path

from portfolio import build_covariance_matrix, equal_weight_weights, estimate_from_prices, portfolio_return, portfolio_volatility, search_lowest_risk_mix

PROJECT_DIR = Path(__file__).resolve().parent
PRICES_FILE = PROJECT_DIR / "prices.csv"
AS_OF_DATE = "2026-10-22"
OBJECTIVE_RETURN = 0.065
RESERVE_MINIMUM = 0.03
RESERVE_ELIGIBLE = {"BIL", "IEF"}
BENCHMARK_DESCRIPTION = "40% LQD / 60% ACWI"


def _sleeves_from_stats(stats):
    return [{"name": name, "expected_return": stats["expected_returns"][name], "volatility": stats["volatilities"][name]} for name in stats["tickers"]]


def _portfolio_result(name, weights, sleeves, covariance, names, objective, reserve_minimum):
    expected_return = portfolio_return(weights, sleeves)
    volatility = portfolio_volatility(weights, covariance, names)
    reserve_weight = sum(weights.get(asset, 0.0) for asset in RESERVE_ELIGIBLE)
    checks = [
        {"rule": "Weights sum to 100%", "value": sum(weights.values()), "threshold": 1.0, "status": "PASS" if abs(sum(weights.values()) - 1.0) < 1e-9 else "FAIL"},
        {"rule": "Long-only weights", "value": min(weights.values()), "threshold": 0.0, "status": "PASS" if min(weights.values()) >= -1e-9 else "FAIL"},
        {"rule": "Historical return estimate meets objective", "value": expected_return, "threshold": objective, "status": "PASS" if expected_return + 1e-12 >= objective else "FAIL"},
        {"rule": "Reserve-eligible allocation meets minimum", "value": reserve_weight, "threshold": reserve_minimum, "status": "PASS" if reserve_weight + 1e-12 >= reserve_minimum else "FAIL"},
    ]
    failed_rules = [check["rule"] for check in checks if check["status"] == "FAIL"]
    return {"name": name, "weights": weights, "expected_return": expected_return, "volatility": volatility, "reserve_eligible_weight": reserve_weight, "checks": checks, "verdict": "PASS" if not failed_rules else "FAIL", "failed_rules": failed_rules}


def build_scenario(last_36_months=False, objective=OBJECTIVE_RETURN, reserve_minimum=RESERVE_MINIMUM):
    """Calculate all required Project 2 portfolios from bundled prices."""
    stats = estimate_from_prices(str(PRICES_FILE), last_36_months=last_36_months)
    sleeves = _sleeves_from_stats(stats)
    names = stats["tickers"]
    covariance = build_covariance_matrix(sleeves, stats["correlations"])
    constrained = search_lowest_risk_mix(sleeves, stats["correlations"], objective, RESERVE_ELIGIBLE, reserve_minimum)
    portfolios = [
        _portfolio_result("Equal weight", equal_weight_weights(names), sleeves, covariance, names, objective, reserve_minimum),
        _portfolio_result("Benchmark - " + BENCHMARK_DESCRIPTION, {"BIL": 0.0, "IEF": 0.0, "LQD": 0.40, "ACWI": 0.60}, sleeves, covariance, names, objective, reserve_minimum),
    ]
    if constrained is None:
        portfolios.append({"name": "Constrained lowest-volatility portfolio", "weights": {}, "expected_return": None, "volatility": None, "reserve_eligible_weight": None, "checks": [], "verdict": "FAIL", "failed_rules": ["No 5-percentage-point portfolio meets the objective and reserve constraints"]})
    else:
        portfolios.append(_portfolio_result("Constrained lowest-volatility portfolio", constrained["weights"], sleeves, covariance, names, objective, reserve_minimum))
    return {"as_of_date": AS_OF_DATE, "observations": stats["observations"], "window": "Last 36 monthly returns" if last_36_months else "All available monthly returns", "objective_return": objective, "reserve_minimum": reserve_minimum, "signal": "Arithmetic annualized historical return estimates calculated only from monthly adjusted-close prices available through the as-of date.", "portfolios": portfolios}


def build_final_output():
    base = build_scenario()
    stress = build_scenario(last_36_months=True)
    base_constrained = base["portfolios"][2]
    stress_constrained = stress["portfolios"][2]
    largest_weight_change = None
    if base_constrained["weights"] and stress_constrained["weights"]:
        largest_weight_change = max(abs(base_constrained["weights"][asset] - stress_constrained["weights"][asset]) for asset in base_constrained["weights"])
    return {"base_case": base, "stress_case": stress, "stress_description": "Estimation-window stress: replace all available monthly returns with the last 36 monthly returns.", "largest_constrained_weight_change": largest_weight_change, "stop_condition": "Do not move beyond a pilot if no feasible portfolio meets the stated constraints, if the loss-limit policy remains undefined, or if the stressed allocation changes by 10 percentage points or more."}
