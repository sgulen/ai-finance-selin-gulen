"""Check candidate allocations against the stated, checkable mandate rules.

Edit only the INPUTS section.  Each candidate's weights are percentages and
must have one entry for every holding listed in HOLDINGS.
"""

# ================================ INPUTS =================================
HOLDINGS = [
    {
        "holding": "Cash",
        "issuer": "none",
        "business_days_to_redeem": 0,
        "reserve_eligible": True,
    },
    {
        "holding": "Treasury bills",
        "issuer": "U.S. Treasury",
        "business_days_to_redeem": 1,
        "reserve_eligible": True,
    },
    {
        "holding": "Treasury 10-year note",
        "issuer": "U.S. Treasury",
        "business_days_to_redeem": 1,
        "reserve_eligible": True,
    },
    {
        "holding": "Global equity index fund",
        "issuer": "diversified fund",
        "business_days_to_redeem": 2,
        "reserve_eligible": False,
    },
    {
        "holding": "Investment-grade bond fund",
        "issuer": "diversified fund",
        "business_days_to_redeem": 3,
        "reserve_eligible": False,
    },
    {
        "holding": "Private real estate fund",
        "issuer": "diversified fund",
        "business_days_to_redeem": 90,
        "reserve_eligible": False,
    },
    {
        "holding": "Acme Corp bonds",
        "issuer": "Acme Corp",
        "business_days_to_redeem": 4,
        "reserve_eligible": False,
    },
    {
        "holding": "Acme Corp stock",
        "issuer": "Acme Corp",
        "business_days_to_redeem": 1,
        "reserve_eligible": False,
    },
]

CANDIDATES = {
    "A": {
        "Cash": 2.0,
        "Treasury bills": 2.0,
        "Treasury 10-year note": 10.0,
        "Global equity index fund": 60.0,
        "Investment-grade bond fund": 26.0,
        "Private real estate fund": 0.0,
        "Acme Corp bonds": 0.0,
        "Acme Corp stock": 0.0,
    },
    "B": {
        "Cash": 1.0,
        "Treasury bills": 0.0,
        "Treasury 10-year note": 0.0,
        "Global equity index fund": 55.0,
        "Investment-grade bond fund": 20.0,
        "Private real estate fund": 15.0,
        "Acme Corp bonds": 5.0,
        "Acme Corp stock": 4.0,
    },
    "C": {
        "Cash": 1.0,
        "Treasury bills": 1.0,
        "Treasury 10-year note": 0.0,
        "Global equity index fund": 70.0,
        "Investment-grade bond fund": 20.0,
        "Private real estate fund": 0.0,
        "Acme Corp bonds": 0.0,
        "Acme Corp stock": 8.0,
    },
    "D": {
        "Cash": 3.0,
        "Treasury bills": 0.0,
        "Treasury 10-year note": 0.0,
        "Global equity index fund": 97.0,
        "Investment-grade bond fund": 0.0,
        "Private real estate fund": 0.0,
        "Acme Corp bonds": 0.0,
        "Acme Corp stock": 0.0,
    },
}

RESERVE_SIZE = 100.0  # USD millions
QUARTERLY_DISTRIBUTION = 0.75  # USD millions
QUARTERS_TO_COVER = 4
LIQUIDITY_WINDOW = 5  # business days
MINIMUM_LIQUID_SHARE = 90.0  # percent
ISSUER_LIMIT = 8.0  # percent
# ===========================================================================

EPSILON = 1e-9
EXEMPT_ISSUERS = {
    "cash",
    "u.s. treasury",
    "us treasury",
    "united states treasury",
    "diversified fund",
    "diversified funds",
}


def is_exempt_issuer(holding, issuer):
    """Return whether the issuer has the mandate's issuer-limit exemption."""
    return holding.strip().lower() == "cash" or issuer.strip().lower() in EXEMPT_ISSUERS


def status(passes):
    return "pass" if passes else "FAIL"


def validate_inputs(candidate):
    holding_names = {row["holding"] for row in HOLDINGS}
    candidate_names = set(candidate)
    if candidate_names != holding_names:
        missing = sorted(holding_names - candidate_names)
        extra = sorted(candidate_names - holding_names)
        details = []
        if missing:
            details.append("missing: " + ", ".join(missing))
        if extra:
            details.append("unknown: " + ", ".join(extra))
        raise ValueError("candidate weights do not match HOLDINGS (" + "; ".join(details) + ")")


def check_candidate(name, weights, reserve_minimum):
    validate_inputs(weights)
    by_holding = {row["holding"]: row for row in HOLDINGS}
    total_weight = sum(weights.values())
    lowest_weight = min(weights.values())
    reserve_eligible_weight = sum(
        weights[holding] for holding, row in by_holding.items() if row["reserve_eligible"]
    )
    liquid_weight = sum(
        weights[holding]
        for holding, row in by_holding.items()
        if row["business_days_to_redeem"] <= LIQUIDITY_WINDOW
    )

    issuer_weights = {}
    for holding, row in by_holding.items():
        if not is_exempt_issuer(holding, row["issuer"]):
            issuer_weights[row["issuer"]] = issuer_weights.get(row["issuer"], 0.0) + weights[holding]
    largest_company_weight = max(issuer_weights.values(), default=0.0)

    checks = [
        ("weights sum to 100", total_weight, abs(total_weight - 100.0) <= EPSILON),
        ("lowest weight not negative (long-only)", lowest_weight, lowest_weight >= -EPSILON),
        ("reserve-eligible weight at least reserve minimum", reserve_eligible_weight,
         reserve_eligible_weight + EPSILON >= reserve_minimum),
        ("weight redeemable within liquidity window at least minimum liquid share", liquid_weight,
         liquid_weight + EPSILON >= MINIMUM_LIQUID_SHARE),
        ("largest single company at most issuer limit", largest_company_weight,
         largest_company_weight <= ISSUER_LIMIT + EPSILON),
    ]

    print(f"\nCandidate {name}")
    failures = 0
    for label, value, passes in checks:
        print(f"{label}: {value:.1f}% — {status(passes)}")
        failures += not passes
    print("calendar-year loss rule: requires CIO clarification")
    if failures:
        print(f"fails {failures} rule(s)")
    else:
        print("passes every checkable rule")


def main():
    reserve_minimum = QUARTERS_TO_COVER * QUARTERLY_DISTRIBUTION / RESERVE_SIZE * 100.0
    print(f"Reserve minimum: {reserve_minimum:.1f}%")
    for name, weights in CANDIDATES.items():
        check_candidate(name, weights, reserve_minimum)


if __name__ == "__main__":
    main()
