"""Filter a vintage data table to the information known on a decision date."""

from datetime import date


# ================================ INPUTS =================================
# Edit these records and DECISION_DATE for another point-in-time question.
DECISION_DATE = "2026-03-31"
ROWS = [
    {"row": 1, "ticker": "AAA", "month": "2026-01", "published_on": "2026-02-10", "price": 101.0},
    {"row": 2, "ticker": "AAA", "month": "2026-02", "published_on": "2026-03-10", "price": 104.0},
    {"row": 3, "ticker": "AAA", "month": "2026-03", "published_on": "2026-04-10", "price": 109.0},
    {"row": 4, "ticker": "AAA", "month": "2026-02", "published_on": "2026-03-25", "price": 103.0},
    {"row": 5, "ticker": "BBB", "month": "2026-01", "published_on": "2026-02-10", "price": 98.0},
    {"row": 6, "ticker": "BBB", "month": "2026-02", "published_on": "2026-03-10", "price": 97.0},
    {"row": 7, "ticker": "BBB", "month": "2026-02", "published_on": "2026-03-10", "price": 97.0},
    {"row": 8, "ticker": "BBB", "month": "2026-03", "published_on": "2026-04-10", "price": 92.0},
    {"row": 9, "ticker": "CCC", "month": "2026-01", "published_on": "2026-02-10", "price": 110.0},
    {"row": 10, "ticker": "CCC", "month": "2026-02", "published_on": "2026-04-05", "price": 112.0},
    {"row": 11, "ticker": "", "month": "2026-02", "published_on": "2026-03-10", "price": 99.0},
    {"row": 12, "ticker": "CCC", "month": "2026-02", "published_on": "2026-03-10", "price": 111.0},
]
# ===========================================================================


def parse_day(value):
    """Return an ISO date so publication dates can be compared safely."""
    return date.fromisoformat(value)


def row_numbers(rows):
    """Return the source row numbers in their original order."""
    return [record["row"] for record in rows]


def remove_missing_tickers(rows):
    """Quarantine records that cannot be assigned to a ticker."""
    removed = [record for record in rows if not record["ticker"].strip()]
    kept = [record for record in rows if record not in removed]
    return kept, removed


def remove_exact_duplicates(rows):
    """Keep the first record for each identical observation, excluding row number."""
    seen = set()
    kept, removed = [], []
    for record in rows:
        signature = (record["ticker"], record["month"], record["published_on"], record["price"])
        if signature in seen:
            removed.append(record)
        else:
            seen.add(signature)
            kept.append(record)
    return kept, removed


def remove_after_decision_date(rows, decision_date):
    """Remove observations whose publication date was after the trade date."""
    kept = [record for record in rows if parse_day(record["published_on"]) <= decision_date]
    removed = [record for record in rows if record not in kept]
    return kept, removed


def keep_latest_known_revision(rows):
    """Keep the latest publication for every ticker/month in an as-of panel."""
    latest = {}
    for record in rows:
        key = (record["ticker"], record["month"])
        if key not in latest or parse_day(record["published_on"]) > parse_day(latest[key]["published_on"]):
            latest[key] = record
    kept = [record for record in rows if latest[(record["ticker"], record["month"])] is record]
    removed = [record for record in rows if record not in kept]
    return kept, removed


def asof_panel(rows, decision_date):
    """Apply the four provenance rules in their required order."""
    funnel = []
    remaining, removed = remove_missing_tickers(rows)
    funnel.append(("Quarantined: no ticker", removed))
    remaining, removed = remove_exact_duplicates(remaining)
    funnel.append(("Exact duplicate", removed))
    remaining, removed = remove_after_decision_date(remaining, decision_date)
    funnel.append((f"Published after {decision_date.isoformat()}", removed))
    remaining, removed = keep_latest_known_revision(remaining)
    funnel.append(("Older vintage replaced by a revision", removed))
    return remaining, funnel


def naive_panel(rows):
    """Keep each ticker/month's latest publication without applying a trade-date cutoff."""
    remaining, _ = remove_missing_tickers(rows)
    remaining, _ = remove_exact_duplicates(remaining)
    return keep_latest_known_revision(remaining)[0]


def signals(panel):
    """Calculate each ticker's last-month return from the two latest observations."""
    by_ticker = {}
    for record in panel:
        by_ticker.setdefault(record["ticker"], []).append(record)

    results = []
    for ticker in sorted(by_ticker):
        observations = sorted(by_ticker[ticker], key=lambda record: record["month"])
        if len(observations) < 2:
            continue
        previous, latest = observations[-2:]
        percent_change = (latest["price"] / previous["price"] - 1.0) * 100.0
        results.append((ticker, latest["month"], percent_change))
    return results


def print_funnel(funnel):
    """Print each provenance rule's count and source row numbers."""
    print("Row funnel")
    for label, removed in funnel:
        numbers = ", ".join(map(str, row_numbers(removed))) or "none"
        print(f"- {label}: {len(removed)} removed (rows {numbers})")


def print_panel(panel):
    """Print the surviving records in source-row order."""
    print("\nAs-of panel")
    for record in sorted(panel, key=lambda item: item["row"]):
        print(
            f"- row {record['row']}: {record['ticker']} {record['month']} "
            f"published {record['published_on']}, price {record['price']:.1f}"
        )


def print_signals(title, panel):
    """Print each calculated return with the month it represents."""
    print(f"\n{title}")
    for ticker, month, percent_change in signals(panel):
        print(f"- {ticker}: {percent_change:+.2f}% ({month})")


def main():
    decision_date = parse_day(DECISION_DATE)
    panel, funnel = asof_panel(ROWS, decision_date)
    print(f"Decision date: {DECISION_DATE}")
    print_funnel(funnel)
    print_panel(panel)
    print_signals("As-of signals", panel)
    print_signals("Naive signals (latest publications, ignoring decision date)", naive_panel(ROWS))


if __name__ == "__main__":
    main()
