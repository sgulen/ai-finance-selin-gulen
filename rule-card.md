# Rule Card

## Training value

Month-end card-spend change, published by month-end.

## Rule

Signal above 0 â†’ hold the equity fund next month; otherwise Treasury bills.

## Lag

One month: this month's signal decides next month's position.

## Cost

0.10% in any month the position switches; start in bills.

## Bills return

0.3% a month.

## Development

2025-01 to 2025-12.

## Holdout

2026-01 to 2026-06, run once, never tuned.

## Benchmark

Buy-and-hold equity fund.

## Failure rule

Stop if the holdout net return trails buy-and-hold.

## Input data

| Month | Signal % | Equity fund % |
| --- | ---: | ---: |
| 2024-12 | 0.8 | â€” |
| 2025-01 | 1.2 | 2.0 |
| 2025-02 | 0.9 | 1.5 |
| 2025-03 | 1.5 | 3.0 |
| 2025-04 | âˆ’1.0 | âˆ’2.5 |
| 2025-05 | âˆ’0.7 | âˆ’1.5 |
| 2025-06 | âˆ’1.4 | âˆ’3.0 |
| 2025-07 | 1.1 | 2.5 |
| 2025-08 | 0.6 | 1.0 |
| 2025-09 | 0.9 | 2.0 |
| 2025-10 | âˆ’0.9 | âˆ’2.0 |
| 2025-11 | âˆ’0.5 | âˆ’1.0 |
| 2025-12 | 1.6 | 3.5 |
| 2026-01 | âˆ’1.1 | âˆ’2.0 |
| 2026-02 | 0.7 | 1.5 |
| 2026-03 | âˆ’1.3 | âˆ’3.0 |
| 2026-04 | 0.8 | 2.0 |
| 2026-05 | âˆ’0.6 | âˆ’1.5 |
| 2026-06 | 0.5 | 1.0 |

## Decision

Stop — the holdout net return trails buy-and-hold.

