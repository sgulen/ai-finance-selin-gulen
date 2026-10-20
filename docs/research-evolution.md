# Research Evolution - Project 1 TSLA

## Retrospective recollection of initial thinking - not an original Edition A

**Disclosure:** The original Edition A and its Brightspace receipt are unavailable. This section is a retrospective recollection prepared for the final Project 1 submission. It is **not** presented as the original Edition A, was not submitted before AI use, and cannot establish the original submission order. Details that cannot be remembered or verified are marked unresolved rather than reconstructed as facts.

### Initial decision and intended user

The intended user was an equity-research analyst choosing one U.S. operating company for a longer-term valuation project. The initial decision was **not to select or initiate TSLA under the supplied screen**. The remembered basis was that TSLA was an operating company with filings and price history, but it failed the defined monthly maximum-drawdown and positive-month thresholds. This was a process decision, not a sell recommendation or an intrinsic-value conclusion.

### Evidence I recall having at the outset

- Tesla was a U.S.-listed operating company with current SEC filings and substantial scale/liquidity.
- The initial screen used 24 completed calendar months of month-end adjusted closes; the retained notes record a maximum drawdown of -31.8% and positive-month frequency of 52.2%, versus gates of -30.0% and 60.0%.
- The latest retained filing notes showed significant cash/investments, material capex plans, low operating income relative to revenue, and unresolved legal/regulatory and non-operating-item questions.

### Initial assumptions, unknowns, and validation plan I recall

I understood that the same screen convention had to be applied to every candidate and that a later valuation should use FCFF to value operating assets before bridging to equity. I did not have a complete ranked universe, a final peer set, a validated operating-cash policy, a current diluted-share convention, or a sustainable-margin/capex-return view. The planned next steps were to reproduce the screen, build source-linked historical financials, separate operating from non-operating items, forecast FCFF, reconcile the enterprise-to-equity bridge, and test margin, capex, WACC, terminal assumptions, and dilution.

### What I cannot verify or remember

I cannot verify the exact original wording, the exact sources opened before AI use, whether every recorded number was present in the original work, the original timestamp, or a Brightspace receipt. The local file `project1_edition_a_tsla.md` is retained as an early working artifact, but its associated local checkout explicitly calls the receipt simulated; it is not claimed to be the original checkpoint submission.

## Edition B - after research and disclosed AI assistance

### Current decision and intended user

**User:** a buy-side equity research committee with no existing TSLA position. **Action:** watch/defer; do not initiate at the retained September 10, 2026 market-price reference until operating-margin and reinvestment evidence improves. The five-year segmented-pro-forma FCFF model is anchored to FY2025 financial statements and produces a base value of **$25.80 per diluted share**. It is a range framework rather than a price target: the tested WACC/terminal-growth grid is $20.65-$34.72 per share.

### A-to-B evidence table

| Item | Edition A | Edition B | Primary driver | Evidence/test justifying the position |
|---|---|---|---|---|
| Thesis/recommendation | Retrospectively recalled: do not select/ initiate because TSLA failed the supplied screening gates. | Watch/defer; do not initiate. The decision is now supported by a segmented-pro-forma FCFF valuation and conditions, not the screen alone. | Mixed: course instruction, model build, and AI-assisted implementation | `output/visible_output.json`; DCF base $25.80/share; retained market reference $367.95; sensitivity range $20.65-$34.72. |
| Data/source choice | Latest 2026 10-Q and price-screen checkpoints. | FY2025 10-K is the base-year source; 2026 information is retained only as context. | Course instruction and own source review | `docs/evidence-ledger.csv`; FY2025 revenue reconciled to $94.827B (not the FY2024 $97.690B); single 2025-12-31 bridge date; units and share convention disclosed. |
| Assumption/model design | Proposed FCFF/EV architecture with unresolved policies. | Linked FY2026-2030 segmented income statement, balance sheet, cash flow, FCFF DCF, and bridge; bounded growth and segment-margin controls. | Course instruction, own analysis, AI-assisted code draft | `src/model.py`; articulation, bridge, known-answer, base-year reconciliation, and monotonicity checks in `output/visible_output.json`. |
| Risk/limitation | Large capex, low operating income, non-operating gains, and regulatory/legal uncertainty. | Terminal value is 90.9% of EV; forecast margin expansion and cash/investment treatment are decision-critical. Comparable results are qualified rather than averaged into the DCF. | Model output and own judgment | Visible output; `docs/validation-and-ai-use.md`; `docs/comparable-valuation-plan.md`. |

### What changed from Edition A to Edition B, and why?

The action remains negative, but its basis changed materially. Edition A correctly treated the supplied price screen as a hard gate; it did not provide the valuation evidence required for the final committee decision. Edition B uses an enterprise-value/FCFF framework, separates operating cash flows from bridge items, and exposes two bounded operating drivers. The base DCF is far below the retained market reference, but the recommendation is still conditional because the high terminal-value share, forecast margin path, AI-related capex, and peer-data gap make false precision inappropriate. The decision would be revisited if filings show a sustained, source-supported improvement in operating margins and returns on incremental investment.
