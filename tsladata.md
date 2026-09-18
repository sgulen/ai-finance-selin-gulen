# Tesla Input Memo for Lab 5 and Lab 6

**Company:** Tesla, Inc. (TSLA)  
**Reporting base:** Fiscal year ended December 31, 2025  
**Source of record:** Tesla 2025 Form 10-K, filed January 28, 2026.  
**Units:** USD millions, except per-share data and share counts.  

## Five required DCF input rows

| Input | Value / unit | As-of date | Exact source / locator | Classification and note |
|---|---:|---|---|---|
| Starting FCFF | **$6,433.3M** | FY ended Dec. 31, 2025 | 2025 Form 10-K, Consolidated Statements of Cash Flows, p. 53: CFO $14,747M; capex $8,527M; cash interest paid $292M. Statement of Operations, p. 52: income before tax $5,278M and tax provision $1,423M. | **Calculated output.** Course convention: CFO + after-tax cash interest - capex. Tax-rate proxy = 1,423 / 5,278 = 26.96%; after-tax interest = 292 x (1 - .2696) = $213.3M. Therefore 14,747 + 213.3 - 8,527 = **$6,433.3M**. This is a mechanical starting point, not a forecast. |
| Growth, Years 1-5 | **unresolved** | Forecast period | 10-K Item 7 / MD&A, pp. 42-43, discusses 2025 operating cash flow, capex, AI and operational infrastructure investment, and production growth, but does not provide a five-year FCFF growth path. | **Forecast assumption.** You must choose and label a fading five-year path after reading the MD&A and prior history. Do not present an AI-suggested path as a filing fact. |
| WACC | **unresolved** | Valuation date | Needs a dated risk-free rate, a stated beta source/date, debt-rate evidence, tax assumption, and market-value weights. | **Estimate.** Lab 6 allows `unresolved`; do not copy the 10% training WACC. |
| Terminal growth | **unresolved; 3% is a course starting assumption** | Perpetuity after Year 5 | Lab 6 instruction: long-run economy, not company-specific growth. | **Assumption.** A terminal growth rate must be lower than WACC. If you use 3%, label it an assumption, not a Tesla-reported figure. |
| Cash and short-term investments | **$44,059M** | Dec. 31, 2025 | 10-K balance sheet, p. 49: cash and cash equivalents $16,513M; short-term investments $27,546M. MD&A, p. 42, also reports $44.06B in cash, cash equivalents, and investments. | **Reported fact, subject to policy.** The course model calls this `cash`; explain whether all of it is non-operating/excess cash rather than silently assuming it. |
| Debt | **$8,177M** unpaid principal; **$8,400M** if finance leases are included | Dec. 31, 2025 | 10-K Note 9, p. 73: total debt unpaid principal $8,177M; finance leases carrying value $223M. | **Reported fact plus bridge-policy choice.** The simple course model has one `DEBT` input. Choose $8,177M for debt only, or $8,400M only if you state that finance leases are included consistently. |
| Diluted weighted-average shares | **3,528M** | FY ended Dec. 31, 2025 | 10-K Statement of Operations, p. 52; Note 3 / EPS reconciliation, p. 61. | **Reported fact.** This is the assignment's requested diluted weighted-average convention, not the point-in-time cover-page share count. |
| Target share price | **unresolved - record yourself** | Date and exact time of observation | Use a price source you can cite, then record the date, local time/time zone, and closing or live-price convention. | **Reported market observation.** It is the target for the reverse DCF and should not be substituted with an old saved price. |



```python
# Values from FY2025 Tesla Form 10-K; USD millions except shares.
"starting_fcff": 6433.3,
"cash": 44059.0,
"debt": 8177.0,  # or 8400.0 only with documented finance-lease policy
"diluted_shares": 3528.0,

# These must remain your labeled assumptions / live observation:
"growth_rates": [ ... five rates ... ],
"wacc": ...,
"terminal_growth": ...,
"target_share_price": ...,
```

## Required verification and judgment checklist

- [ ] Open the filing and verify every page/line above yourself.
- [ ] Decide whether the $44,059M balance is all excess/non-operating cash; if not, document the adjustment.
- [ ] State whether the debt bridge includes the $223M finance leases and keep that choice consistent.
- [ ] Build a five-year FCFF growth path from MD&A and recent history; label it `forecast`.
- [ ] Estimate WACC or label it `unresolved`.
- [ ] Record today's TSLA price with date, time, source, and convention.
- [ ] Run the training case first, then the Tesla case, grid, and reverse DCF.

## Sources

- Tesla, Inc., Form 10-K for the year ended December 31, 2025, filed January 28, 2026: https://www.sec.gov/Archives/edgar/data/1318605/000162828026003952/tsla-20251231.htm
- Relevant filing locations: p. 42 (MD&A cash-flow summary); pp. 49 and 52-53 (balance sheet, statement of operations, cash flows); p. 61 (EPS); p. 73 (debt and finance leases).
## Training-case validation`python dcf.py` passed the Lab 6 training case on 9/17/2026. - Base value per diluted share: $27.4974. Sensitivity grid center: $27.50. Reverse-DCF shift at a $30.00 target: +1.78%
My base-case DCF value is $43.93 per share versus a TSLA market
price of $366.20, or about 0.12x the market price. This is outside
the course’s 0.5x–2.0x reasonableness band. I did not change the
model to make it fit the market price. The input I distrust most is
the five-year FCFF growth path because the market price appears to
reflect business outcomes much stronger than my base-case cash-flow
forecast.

## Reverse DCF

Using a target price of $366.20, the reverse DCF solved for a
uniform shift of +72.03 percentage points added to each of my five
annual FCFF growth rates.

This changes my base growth path of 14%, 12%, 10%, 8%, and 6% to
approximately 86.03%, 84.03%, 82.03%, 80.03%, and 78.03%.
I held starting FCFF, WACC, terminal growth, cash, debt, diluted
shares, and the bridge fixed. I expanded the search range from the
initial +10 percentage-point upper bound to +100 percentage points
because the target price was unreachable in the initial range.

This is not proof that TSLA is mispriced. It shows that, under this
specific model, the market price requires far stronger five-year
cash-flow growth than my base case assumes.

Then add:

# Conditional call

Watch-defer. I would reconsider if Tesla produces sourced evidence
that its autonomy, Robotaxi, AI, andenergy-storage investments can
create cash-flow growth materially above my base-case path. I will
monitor operating margin, free cash flow, capital expenditures, and
energy-storage growth.
## Output: 
Tesla (TSLA) - FY2025 base case — all dollar amounts are USD millions except per-share values.

BASE-CASE DCF
FCFF Year 1: 7333.6200
FCFF Year 2: 8213.6544
FCFF Year 3: 9035.0198
FCFF Year 4: 9757.8214
FCFF Year 5: 10343.2907
Present value of the explicit FCFF: 32883.3133
Terminal value at Year 5: 142047.8591
Present value of the terminal value: 86223.0344
Enterprise value: 119106.3476
Equity value: 154988.3476
Value per diluted share: 43.9309
Present value of the terminal value as a share of enterprise value: 0.7239

SENSITIVITY GRID: value per diluted share ($)
WACC \ terminal growth | 2.0% | 3.0% | 4.0%
-------------------------------------------
9.0%                  | 47.64 | 52.59 | 59.51
10.0%                  | 42.83 | 46.40 | 51.17
11.0%                  | 39.09 | 41.77 | 45.22

REVERSE DCF
Solved uniform growth-rate shift: +72.03%
Target share price: $366.20
Held fixed: starting FCFF, WACC, terminal growth, cash, debt, diluted shares,
and the bridge; only the uniform shift to all five explicit growth rates changes.