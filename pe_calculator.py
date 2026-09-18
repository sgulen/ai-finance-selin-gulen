"""Lab 07 P/E comparable-company calculator.

Run the Asbury training case first. After the checks pass, replace only the
editable input block with your own company and sourced peer data for Lab 08.
"""

# ============================ EDITABLE INPUTS ============================
TARGET = {
    "ticker": "TSLA",
    "price": 366.2,
    "diluted_eps": 1.08,
}

PEERS = [
    {"ticker": "GM", "price": 86.59, "diluted_eps": 3.27},
    {"ticker": "RIVN", "price": 15.40, "diluted_eps": -3.07},
]
# ===========================================================================


def valid_price_and_eps(company):
    return company["price"] is not None and company["price"] > 0 and (
        company["diluted_eps"] is not None and company["diluted_eps"] > 0
    )


def pe_ratio(company):
    return company["price"] / company["diluted_eps"]


def median(values):
    ordered = sorted(values)
    count = len(ordered)
    midpoint = count // 2
    if count % 2:
        return ordered[midpoint]
    return (ordered[midpoint - 1] + ordered[midpoint]) / 2.0


def implied_price(peer, target):
    return pe_ratio(peer) * target["diluted_eps"]


def usable_peers(target, peers):
    seen = {target["ticker"]}
    usable = []
    excluded = []
    for peer in peers:
        ticker = peer["ticker"]
        if ticker in seen:
            excluded.append((ticker, "duplicate or target"))
            continue
        seen.add(ticker)
        if not valid_price_and_eps(peer):
            excluded.append((ticker, "nonpositive or missing price/EPS"))
            continue
        usable.append(peer)
    return usable, excluded


def print_estimate(label, peers, target):
    if not valid_price_and_eps(target):
        print(f"{label}: target price or diluted EPS is missing/nonpositive; not meaningful.")
        return None
    if not peers:
        print(f"{label}: no usable peers; no estimate.")
        return None

    implied = [implied_price(peer, target) for peer in peers]
    median_multiple = median([pe_ratio(peer) for peer in peers])
    if len(peers) == 1:
        print(f"{label}: one-peer reference estimate = ${implied[0]:.2f}")
    else:
        print(
            f"{label}: implied range = ${min(implied):.2f} to ${max(implied):.2f}; "
            f"median-implied price = ${median_multiple * target['diluted_eps']:.2f}"
        )
    return median_multiple * target["diluted_eps"]


def main():
    print("P/E Comparable-Company Calculator")
    print(f"Target: {TARGET['ticker']}")

    if not valid_price_and_eps(TARGET):
        print("Target price or diluted EPS is missing/nonpositive. P/E is not meaningful.")
        return

    peers, excluded = usable_peers(TARGET, PEERS)
    for ticker, reason in excluded:
        print(f"Excluded {ticker}: {reason}")

    print("\nPEER MULTIPLES")
    for peer in peers:
        print(f"{peer['ticker']} P/E: {pe_ratio(peer):.6f}x")

    full_estimate = print_estimate("Full-peer estimate", peers, TARGET)

    print("\nLEAVE-ONE-OUT CHECK")
    if full_estimate is None:
        print("No full-peer estimate available for removal checks.")
        return
    for peer_to_remove in peers:
        remaining = [peer for peer in peers if peer is not peer_to_remove]
        label = f"Remove {peer_to_remove['ticker']}"
        remaining_estimate = print_estimate(label, remaining, TARGET)
        if remaining_estimate is not None:
            print(
                f"Change from full-peer median-implied estimate: "
                f"${remaining_estimate - full_estimate:+.2f}"
            )


if __name__ == "__main__":
    main()
