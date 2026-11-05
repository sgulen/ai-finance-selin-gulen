# Provenance gate — 31 March 2026

The decision date is **2026-03-31**. A row is usable only if it was published on or before that date; when multiple usable publications exist for the same ticker and month, the latest usable one is retained.

## Row funnel

| Rule | Rows removed | Count |
| --- | --- | ---: |
| Quarantined: no ticker | 11 | 1 |
| Exact duplicate | 7 | 1 |
| Published after 31 March 2026 | 3, 8, 10 | 3 |
| Older vintage replaced by a revision | 2 | 1 |
| As-of panel retained | 1, 4, 5, 6, 9, 12 | 6 |

## As-of panel

| Row | Ticker | Month measured | Published on | Price |
| ---: | --- | --- | --- | ---: |
| 1 | AAA | 2026-01 | 2026-02-10 | 101.0 |
| 4 | AAA | 2026-02 | 2026-03-25 | 103.0 |
| 5 | BBB | 2026-01 | 2026-02-10 | 98.0 |
| 6 | BBB | 2026-02 | 2026-03-10 | 97.0 |
| 9 | CCC | 2026-01 | 2026-02-10 | 110.0 |
| 12 | CCC | 2026-02 | 2026-03-10 | 111.0 |

## Signals

The as-of signal is `(latest knowable price / previous-month price) - 1`. The naïve signal uses each ticker/month's latest publication without the decision-date cutoff.

| Ticker | As-of signal | Naïve signal | What arrived later |
| --- | ---: | ---: | --- |
| AAA | +1.98% (February) | +5.83% (March) | March observation (row 3) |
| BBB | −1.02% (February) | −5.15% (March) | March observation (row 8) |
| CCC | +0.91% (February) | +1.82% (February) | Later February revision (row 10) |

## Sanity check

For each one-year zero-coupon fund, the yield is `100 / price - 1`. A price above 100 creates a negative yield; at the same maturity, riskier credit should have a higher yield and therefore a lower price than safer credit.

| Row | Fund | Month | Price | Yield | Breaks |
| ---: | --- | --- | ---: | ---: | --- |
| 1 | AAA | Jan | 101.0 | −0.99% | Negative yield |
| 4 | AAA | Feb | 103.0 | −2.91% | Negative yield |
| 5 | BBB | Jan | 98.0 | +2.04% | Nothing |
| 6 | BBB | Feb | 97.0 | +3.09% | Nothing |
| 9 | CCC | Jan | 110.0 | −9.09% | Negative yield; priced above BBB and AAA |
| 12 | CCC | Feb | 111.0 | −9.91% | Negative yield; priced above BBB and AAA |

The provenance gate admits only information available on the trade date, but it does not establish that the information is economically plausible. A sanity gate is therefore needed after the provenance gate to quarantine impossible yields and price ordering.
