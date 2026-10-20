# Validation and AI Use - TSLA Project 1

## Decision, version, and as-of boundary

**Decision/user:** watch/defer TSLA for a buy-side equity-research committee with no current position. **Run command:** `py -3 app.py --write-output`. **Financial-statement and bridge as-of date:** 2025-12-31. **Screen/market-reference date:** 2026-09-10, using the month-end August 2026 checkpoint retained in early local notes. **Edition A disclosure:** the original baseline and receipt are unavailable; the companion research-evolution document contains a clearly labeled retrospective recollection, not a recreated original. **Version/commit:** no Git executable or commit history was available in this workspace; create a commit before submitting and enter it here: **STUDENT MUST ENTER COMMIT ID**.

## Data and convention ledger

| Material input | Source | As-of | Definition/units | Treatment | Risk |
|---|---|---|---|---|---|
| Revenue / EBIT / segment revenue | Tesla 2025 10-K pp. 49-50 | FY2025 | $94,827M / $4,355M; auto $69,526M, energy $12,771M, services $12,530M | Segmented pro-forma opening anchors | $97,690M is FY2024 revenue; corrected from prior draft |
| Cash/investments | Tesla 2025 10-K p. 49 | 2025-12-31 | $16,513M / $27,546M | Gross addition in initial bridge | Operating-liquidity/tax policy unresolved |
| Debt/finance leases | Tesla 2025 10-K p. 49 and Note 9 | 2025-12-31 | $8,376M | Financing claim deducted | Consolidation policy must match EV |
| Diluted shares | Tesla 2025 10-K p. 50 | FY2025 | 3,528M | DCF per-share denominator | Weighted average, not current count |
| Revenue/margin paths | Analyst assumptions | FY2026-2030 | 5%-7% growth; 6%-10% margin | Bounded exposed controls | Not management guidance |
| WACC/terminal growth | Analyst assumptions | Model run | 10.5% / 2.5% | DCF discount/terminal convention | Terminal value is 90.9% of EV |

## Validation register

| Claim/output | Failure mode | Test and expected result | Actual result | Disposition | Evidence |
|---|---|---|---|---|---|
| DCF arithmetic | Terminal value discounted at wrong period | Lab 05 training fixture should equal $27.4974/share within $0.01 | $27.49737; pass | Accepted | `src/model.py:known_answer_test`, visible output JSON |
| Statements articulate | Balance sheet or cash flow does not tie | Annual BS error = 0; ending cash equals prior cash plus CFO less capex | All five years pass; max error 0.00 | Accepted | visible output JSON `checks` |
| Bridge | Incorrect claim treatment | Recompute EV + cash + investments - debt/finance leases - NCI/redeemable NCI | Pass | Accepted subject to cash policy | visible output JSON `checks` |
| DCF direction | WACC/growth sign reversal | Higher WACC lowers value; higher terminal growth raises value | Both pass | Accepted | visible output JSON `validation` |
| Highest-risk input | Incoherent terminal relation silently accepted | Set terminal growth to 11% with WACC 10.5%; expect failure | Fails loudly; no valuation | Accepted | `app.py --interactive` and JSON validation |
| Source definition | Mix current shares with weighted-average shares | Model must use one stated convention throughout | 3,528M used throughout | Qualified | evidence ledger |
| Comps/transactions | Unsupported peer multiple affects action | Require point-in-time market/financial source packet before use | Not complete; omitted from recommendation | Qualified limitation | decision memo |
| Base-year source reconciliation | Historical opening values drift from filing | Compare revenue, EBIT, segment revenue, cash, investments, and debt to evidence ledger | Pass: `base_year_reconciles_to_ledger=True` | Accepted | visible output JSON `checks`; `BASE_YEAR` |
| Cold run | Local environment masks a dependency or path problem | Clone/export to a clean folder; run `py -3 app.py --write-output`; record OS/Python/time/result | **STUDENT MUST RUN AND RECORD** | Open | add `docs/cold-run-log.md` |

## Locked Changed-Input Record - human prediction first; AI closed during execution

| 2026-10-19, 9:42 PM EDT | Repository commit | Segment gross-margin shift | 0.0pp -> +1.0pp | A higher segment gross margin is expected to increase gross profit, EBIT, FCFF, and value per share | No change from watch/defer status is expected, since value is still expected to be below market |
|---|---|---|---|---|---|

| Before/after output | Actual decision effect | Prediction reconciliation | Failure diagnosis or no-change reason | Evidence path |
|---|---|---|---|---|
| $25.80 -> $28.80 per share | Watch/defer remains unchanged because result remains far below retained market reference | Prediction direction was correct, as value per share increased by $3 while result is still below market reference of $367.95; meaning recommendation remained watch/defer | No action change because the tested improvement is insufficient | `output/visible_output.json` validation section |

## Named AI-use register

| Tool/model surface and exposed version | Interaction date | Material task | Output/claim used or considered | Independent check | Disposition | Effect on decision |
|---|---|---|---|---|---|---|
| OpenAI Codex, GPT-5 surface (UI version not exposed) | 2026-10-19 | Drafted a standard-library model and documentation structure | FCFF/three-statement implementation and document organization | Lab 05 known-answer fixture; source-linked input ledger; articulation, bridge, and monotonicity tests | Modified and accepted with limitations | Enabled reproducible tool; did not establish finance facts |
| OpenAI Codex, GPT-5 surface (UI version not exposed) | 2026-10-19 | Suggested a margin changed-input test | +100bp margin should increase FCFF/value | Independent execution after integrating the segmented pro-forma: $25.80 -> $28.80/share | Accepted as a mechanical test, not as evidence for forecast margin | No action change |

## Limitations, monitoring, and kill/escalation rules

Do not rely on the DCF as a point estimate. The FY2025 base-year inputs were reconciled to Tesla’s final January 28, 2026 10-K: revenue is $94.827B, not the $97.690B FY2024 comparator, and debt plus finance leases is $8.376B. Refresh peer and transaction evidence, define excess operating cash, reconcile a current diluted share count, and revisit regulatory-credit, legal, digital-asset, and SpaceX-investment treatment. Reopen initiation only after two consecutive filings support a credible operating-margin/cash-flow path and the bridge is refreshed. Withdraw the valuation conclusion if the bridge fails or input classifications change materially.
