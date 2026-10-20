# TSLA Decision Memo

## Decision and committee ask

**Recommendation: watch/defer; do not initiate a TSLA position.** I ask the committee to keep TSLA on the monitored list and require the next two reported quarters to show evidence that incremental AI, factory, and service investment is producing durable operating-margin and cash-flow improvement before reopening an initiation decision.

This is an educational analysis for a buy-side equity-research committee, not investment advice. The financial-statement and bridge date is December 31, 2025; the retained market reference is September 10, 2026. Values are USD millions except per-share values.

## Valuation and strongest evidence

The linked five-year FCFF DCF, driven by a segmented automotive/energy/services pro-forma, produces **enterprise value of $56.1 billion**, **equity value of $91.0 billion**, and **$25.80 per diluted share** in the base case. The WACC/terminal-growth sensitivity grid spans **$20.65 to $34.72 per share** across 8.5%-12.5% WACC and 1.5%-3.0% terminal growth. It is a stress range, not a probability distribution.

FY2025 reported revenue was **$94.827 billion** and operating income was $4.355 billion. The final January 28, 2026 10-K reports $97.690 billion as FY2024 revenue; the prior model’s use of $97.690 billion as FY2025 revenue has been corrected. The initial bridge adds $44.059 billion of cash and short-term investments and deducts $8.376 billion of debt and finance leases plus $0.728 billion of redeemable/noncontrolling interests. The model uses the FY2025 diluted weighted-average share convention of 3.528 billion shares. These facts and locators appear in `docs/evidence-ledger.csv`.

The retained September 10, 2026 screen record shows a $367.95 August 2026 month-end adjusted close. It is not used to create the valuation; it is only a reference point for the conditional action. The difference between it and the DCF result is too large to be resolved by a minor change in WACC or terminal growth.

## Material assumptions and sensitivities

The forecast separately models automotive, energy, and services revenue and gross margins; it then deducts R&D and SG&A, forecasts operating working capital, and derives FCFF. It assumes $21.0 billion of FY2026 capex, 8% of revenue thereafter, a 27% operating tax rate, 10.5% WACC, and 2.5% terminal growth. These are analyst assumptions, not management guidance.

The largest tested driver is segment gross margin: a two-percentage-point lower margin path produces $19.79 per share and a two-point higher path produces $31.80. The corresponding revenue-growth shift produces $24.77-$26.62 because the incremental revenue also requires working capital and revenue-linked capex. This ranking applies only over the stated ranges; it does not assign probabilities or prove margin is always more important than growth.

### Named causal cases

The linked cases supplement, rather than replace, the one-at-a-time and WACC/growth sensitivities. **Downside: $18.58/share** assumes demand/price pressure and delayed AI/factory returns, lowering each forecast-year growth and margin by 2 points, raising WACC to 11.5%, and lowering terminal growth to 2.0%; its action is **do not initiate**. **Base: $25.80/share** retains the stated assumptions and supports watch/defer. **Upside: $37.29/share** assumes stronger energy/services mix and operating leverage, raising growth and margin by 2 points, lowering WACC to 9.5%, and using 3.0% terminal growth; it remains below the retained market reference and does not by itself justify initiation.

### Market-implied expectation

At the retained $367.95 market reference, the base operating path requires a **10.2% terminal-growth rate** to reconcile to the market price, versus the approved 1.5%-3.0% range. This reverse-DCF diagnostic does not forecast 10.2% growth; it illustrates how much value must come from assumptions outside the approved long-run range.

## Risks, failure conditions, and monitoring

The model's terminal value is 90.9% of enterprise value, so long-run margin and reinvestment assumptions dominate the conclusion. The bridge currently treats all cash and short-term investments as non-operating pending an operating-liquidity and tax analysis. AI infrastructure and factory capex could create returns not captured by this simple forecast, while regulatory-credit persistence, legal/regulatory outcomes, dilution, digital assets, and the SpaceX investment remain unresolved. The comparable cross-check is qualified: TSLA is 14.12x EV/revenue and 339.07x P/E versus GM at 0.98x and 26.49x. The saved historical-price CSV is a narrow reference, not a mechanically averaged target.

**Reversal trigger:** reconsider the action when two consecutive filings show operating margins and incremental operating cash flow consistent with a credible, source-supported path toward the model's 8%-10% FY2028-FY2030 EBIT margin range, and when the cash/investment bridge and peer data have been refreshed to one common as-of date. **Kill/escalation trigger:** withdraw the current valuation conclusion if the bridge no longer reconciles, the terminal-value share rises further without new support, or a material filing changes the operating/non-operating classification.

See `docs/validation-and-ai-use.md` for tests and disclosed AI use.
