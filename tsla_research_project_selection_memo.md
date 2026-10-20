# TSLA Research Project — Decision Memo

**Decision user:** Equity research analyst choosing one public company for a long-term, in-depth valuation project.  
**Company:** Tesla, Inc. (NASDAQ: TSLA)  
**Screen/valuation date:** September 10, 2026. Latest filed financial information reviewed: Form 10-Q for the quarter ended June 30, 2026.  
**Screen lookback:** 24 completed calendar months, September 30, 2024 through August 31, 2026, using month-end adjusted-close returns in USD.

## Decision: Do not initiate under the stated screen

TSLA satisfies the universe requirements: it is a U.S.-listed operating company with more than two years of market history and current SEC filings. It is not a fund, shell, bank, or non-operating vehicle. However, it **fails both required return-screen thresholds** on the stated 24-month method:

| Criterion | Threshold | TSLA result | Pass? |
|---|---:|---:|---|
| Maximum drawdown | >= −30.0% | **−31.8%** | No |
| Positive-month frequency | >= 60.0% | **52.2%** (12 positive months / 23 month-to-month returns) | No |
| SEC eligibility check | Suitable operating company; no exclusion | Passes base eligibility, but adds material valuation complexity | Yes, not sufficient |

**Initial thesis:** TSLA is a research-rich but screen-ineligible candidate. Do not select it as the single detailed valuation project unless the screening list is rerun under a pre-specified alternative rule that TSLA passes and its rank is first. This is a process decision, not a sell recommendation and not an intrinsic-value conclusion.

## Screen evidence and method

**Price source:** [Yahoo Finance historical prices](https://finance.yahoo.com/quote/TSLA/history/), downloaded September 10, 2026. Yahoo reports adjusted closes; TSLA paid no cash dividend during this window, so split/dividend adjustment does not alter the economic conclusion.

**Method:**

- Use the last trading-day adjusted close of each completed calendar month from September 2024 through August 2026.
- Monthly return: `P_t / P_(t−1) − 1` (23 observations).
- Positive-month frequency: count of returns > 0 divided by 23.
- Maximum drawdown: minimum of `P_t / max(P_0…P_t) − 1`, calculated from the same monthly adjusted-close series.

| Checkpoint | Adjusted close | Why it matters |
|---|---:|---|
| September 2024 | $261.63 | Start of 24-month price-level series |
| Peak: October 2025 | $456.56 | Running high used for drawdown |
| Trough after peak: July 2026 | $311.21 | Maximum drawdown = 311.21 / 456.56 − 1 = **−31.8%** |
| August 2026 | $367.95 | Final completed month |

The screen is reproducible but must be rerun with the same provider and end-of-month convention before a final company list is submitted. Daily prices would produce a different drawdown; that is why this memo specifies monthly data rather than mixing frequencies.

## Known evidence with sources

| Evidence | What is known | Source |
|---|---|---|
| Current SEC availability | Tesla filed a Form 10-Q for June 30, 2026; interim results are unaudited and the December 31, 2025 balance sheet derives from audited FY2025 statements. | [Tesla Q2 2026 10-Q](https://www.sec.gov/Archives/edgar/data/1318605/000162828026049270/tsla-20260630.htm) (Note 1, pp. 10–11) |
| Scale and revenue mix | Q2 2026 revenue was $28.236B; six-month revenue was $50.623B, up 26% and 21% year over year, respectively. | [Q2 2026 10-Q](https://www.sec.gov/Archives/edgar/data/1318605/000162828026049270/tsla-20260630.htm) (statement of operations, p. 5; MD&A) |
| Operating-profit volatility | Q2 2026 income from operations was $398M; six-month operating income was $1.339B. | [Q2 2026 10-Q](https://www.sec.gov/Archives/edgar/data/1318605/000162828026049270/tsla-20260630.htm) (statement of operations, p. 5) |
| Investment intensity | Six-month 2026 capex was $8.282B versus $3.886B a year earlier; management expected 2026 capex above $25B. | [Q2 2026 10-Q](https://www.sec.gov/Archives/edgar/data/1318605/000162828026049270/tsla-20260630.htm) (MD&A, pp. 30 and 35) |
| Liquidity and cash generation | Cash flow from operations was $8.634B for the first six months of 2026; cash and short-term investments were $43.52B at June 30. | [Q2 2026 10-Q](https://www.sec.gov/Archives/edgar/data/1318605/000162828026049270/tsla-20260630.htm) (cash-flow statement, p. 9; MD&A, p. 34) |
| Accounting / valuation complexity | The 10-Q reports a $1.005B unrealized gain on a SpaceX equity investment in six-month operating cash-flow reconciliation; the investment is fair-valued through other income. | [Q2 2026 10-Q](https://www.sec.gov/Archives/edgar/data/1318605/000162828026049270/tsla-20260630.htm) (Note 2 / related-party disclosure and cash-flow statement) |
| Legal/regulatory uncertainty | Tesla discloses product, FSD/Robotaxi-related litigation and regulatory inquiries; it cannot reasonably estimate many potential losses. | [Q2 2026 10-Q](https://www.sec.gov/Archives/edgar/data/1318605/000162828026049270/tsla-20260630.htm) (Legal Proceedings, pp. 24–25) |

## Consequential assumptions

These are decisions required to run the screen or eventual valuation; they are not established facts.

| Assumption | Why it is consequential | Treatment |
|---|---|---|
| A 24-completed-month monthly-return window is the intended lookback | It determines both numerical screen outcomes; a daily series could worsen maximum drawdown. | Freeze this definition for every candidate in the ranking. |
| Adjusted close is the correct return field | Ensures stock splits and distributions are handled consistently. | Use one provider/field for the whole universe and retain the downloaded file. |
| Thresholds are hard gates | TSLA misses both, so it cannot be selected on subjective appeal. | Do not waive without changing the written screen before comparing companies. |
| The 10-Q does not itself make TSLA a prohibited issuer | Tesla is an operating industrial/technology company, although its investment and legal disclosures complicate valuation. | Record as eligible-but-complex, not automatically disqualified. |
| Future valuation would use FCFF/EV | Tesla has material debt, leases, minority interests, cash/investments and non-operating/investment items. | Apply the Week 2 valuation contract and bridge policy if TSLA later becomes eligible. |

## Unknowns that prevent selection now

- The full ranked screening-company list and TSLA’s rank have not been provided; therefore the success test (“remains on top”) cannot be certified.
- The source download and calculation file must be preserved for audit; this memo records checkpoints and formulas, not all 24 month-end observations.
- The economically sustainable level of automotive regulatory credits, EV margins, Robotaxi/FSD economics, AI-infrastructure returns, and terminal reinvestment is unknown.
- The required operating cash balance versus excess cash/investments is unknown, as are the valuation treatment and tax consequences of the SpaceX equity investment and digital assets.
- Potential legal/regulatory outcomes and the final dilution impact of equity awards cannot be treated as known cash flows.

## Research plan

1. **Reproduce the screen for every candidate.** Save raw monthly adjusted-close data, calculate both metrics in one worksheet/script, apply hard gates, then rank survivors. Do not begin valuation before this step identifies the winner.
2. **Complete an SEC eligibility review for the winner.** Confirm operating-company status, filing continuity, accounting restatements, material going-concern or control issues, and whether complex investments make the issuer unsuitable.
3. **If TSLA becomes eligible, rebuild history.** Use FY2023–FY2025 audited 10-K data plus 2026 10-Qs; reconcile revenue by segment, EBIT, D&A, capex, working capital, debt, leases, NCI, cash, and dilution.
4. **Normalize carefully.** Separate discrete restructuring, non-operating fair-value gains/losses, tax benefits, regulatory-credit persistence, and stock-compensation effects. Each adjustment needs a filing-note locator and a tax treatment.
5. **Value operating assets first.** Forecast segment revenue/margins, reinvestment and NWC, then discount FCFF to EV; separately bridge to common equity using a single valuation date and stated share convention.
6. **Run decision sensitivities.** Stress auto margin, regulatory credits, AI capex/return on capital, FSD/Robotaxi timing, terminal margin, WACC, and dilution. State what result would reverse the thesis.

## Decision checkpoint

**Current status: reject for selection.** TSLA fails the explicit drawdown and positive-month gates. Reconsider only if a uniformly applied rerun changes the result or if the assignment owner formally changes the screening policy before the ranking is performed.
