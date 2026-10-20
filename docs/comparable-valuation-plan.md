# Comparable Valuation Completion Plan - TSLA

## Current status

**Qualified, not dispositive.** The retained September 17, 2026 price observations and FY2025 filings now support one enterprise-value multiple and one equity-value multiple. They are deliberately not averaged with the DCF: GM Financial debt and Tesla's energy/software/autonomy exposure make this a narrow auto-manufacturing triangulation. Before final freeze, save the original historical-price downloads/screenshots and record their URLs/timestamps.

## Peer policy

Use a disclosed, consistently applied peer set of publicly traded companies with a material automotive/manufacturing operating business. Start with General Motors, Ford, BYD, and Rivian, then document any exclusions (for example, different reporting currency, persistent losses, a non-comparable business mix, or missing point-in-time data). Do not select peers solely because their resulting multiple supports the DCF conclusion. Report both the median and the range; do not treat either as a price target.

## Required point-in-time workpaper

| Company | Ticker | Price and market-cap source at common date | Latest financial filing available at that date | EV calculation | EV / revenue (enterprise-value multiple) | P / E (equity-value multiple) | Inclusion / exclusion rationale |
|---|---|---|---|---|---|---|---|
| Tesla | TSLA | 2026-09-17 regular-session close $366.20 × 3,751M 2025 period-end shares = $1,373,616M market cap; saved in `docs/source-evidence/prices/historical-prices-2026-09-17.csv` | Tesla FY2025 10-K | $1,373,616 + $8,376 debt/leases + $728 NCI - $44,059 cash/investments = $1,338,661M | 14.12x ($1,338,661 / $94,827) | 339.07x ($366.20 / $1.08 FY2025 diluted EPS) | Subject company; high multiple reflects assets/growth expectations outside a legacy-auto comparison |
| General Motors | GM | 2026-09-17 regular-session close $86.62 × 903.968M shares = $78,302M market cap; saved in `docs/source-evidence/prices/historical-prices-2026-09-17.csv` | GM FY2025 10-K | $78,302 + $130,277 consolidated debt - $27,669 cash/marketable securities = $180,910M | 0.98x ($180,910 / $185,019) | 26.49x ($86.62 / $3.27 FY2025 GAAP diluted EPS) | Included as a narrow vehicle-manufacturing peer; GM Financial debt makes EV comparison qualified |
| Rivian | RIVN | Retained 2026-09-17 close $15.40 | Rivian FY2025 10-K | Not used in median | NM | NM ($3.07 loss per diluted share) | Excluded from positive-P/E calculation; early-stage loss business |

## Reconciliation to DCF

Tesla trades at 14.12x revenue versus GM at 0.98x, and at 339.07x GAAP P/E versus GM at 26.49x. The gaps are not averaged into a target price. They are consistent with the market assigning Tesla substantially different growth, margin, mix, and optionality expectations; they also reflect leverage, GM Financial's financing business, cash treatment, and the difference between common earnings and enterprise value. The DCF remains the primary method because it makes reinvestment and operating-cash-flow assumptions explicit.

## Quality gates before use

- Historical price rows, URLs, access date, and field convention are saved in `docs/source-evidence/prices/historical-prices-2026-09-17.csv`. Add browser screenshots only if specifically required by the instructor.
- Match each peer’s market date to the latest filing available then; do not mix later financials with earlier prices without a labelled lag.
- Use the same enterprise-to-equity bridge policy across peers and disclose exceptions.
- Check arithmetic, currency conversion, units, and whether negative earnings make P/E non-meaningful.
- Update the decision memo, validation register, visible output, and final PDFs only after this workpaper is complete.
