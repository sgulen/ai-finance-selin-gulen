# Project 2 fund universe

| Ticker | Fund | Mandate role |
| --- | --- | --- |
| BIL | SPDR Bloomberg 1-3 Month T-Bill ETF | Cash and payout reserve proxy |
| IEF | iShares 7-10 Year Treasury Bond ETF | Government-bond allocation |
| LQD | iShares iBoxx $ Investment Grade Corporate Bond ETF | Investment-grade fixed-income allocation |
| VT | Vanguard Total World Stock ETF | Broad global equity allocation |

## Why this set makes the project easier

I deliberately used four funds—one for each required role—rather than adding overlapping choices. That keeps the allocation, monthly-return calculations, liquidity discussion, and rebalancing analysis transparent: each allocation decision has one obvious economic purpose.

- **BIL — cash and reserve:** This is a Treasury-bill ETF, so it is a practical market-priced substitute for a money-market fund. It directly fits the reserve role, is simple to describe as a short-duration government-security sleeve, and its adjusted-price history captures the return that a constant-$1 money-market NAV would hide.
- **IEF — government bonds:** IEF is a single, well-known intermediate Treasury exposure. It separates interest-rate-sensitive government bonds from credit risk, avoiding the need to disentangle several Treasury maturities or issuers in the analysis.
- **LQD — investment-grade fixed income:** LQD supplies the credit-bearing investment-grade bond role that Treasuries do not. Using it alongside IEF creates a clear comparison between government-bond and investment-grade corporate-bond exposures without introducing high-yield credit or a second equity-like risk source.
- **VT — equity:** VT is a broad global stock ETF rather than a narrow sector, country, or factor bet. It is therefore a clean equity building block with no home-country or sector preference embedded in the project choice.

All four are established exchange-traded funds with readily available Yahoo Finance monthly **Adj Close** histories, identical data treatment, and plainly differentiated roles. They are convenient research proxies; the final mandate review should still document how pooled-fund holdings are treated under Meridian's 8% single-issuer rule.

## Price-history record

The accompanying `prices.csv` contains 60 completed monthly observations, from 2021-10-01 through 2026-09-01, in oldest-to-newest order. Values are Yahoo Finance **Adj Close** prices, which incorporate distributions. The current incomplete October 2026 month is excluded.

| Ticker | Source | Frequency / field | Download date |
| --- | --- | --- | --- |
| BIL | [Yahoo Finance Historical Data](https://finance.yahoo.com/quote/BIL/history/) | Monthly / Adj Close | 2026-10-22 |
| IEF | [Yahoo Finance Historical Data](https://finance.yahoo.com/quote/IEF/history/) | Monthly / Adj Close | 2026-10-22 |
| LQD | [Yahoo Finance Historical Data](https://finance.yahoo.com/quote/LQD/history/) | Monthly / Adj Close | 2026-10-22 |
| VT | [Yahoo Finance Historical Data](https://finance.yahoo.com/quote/VT/history/) | Monthly / Adj Close | 2026-10-22 |
