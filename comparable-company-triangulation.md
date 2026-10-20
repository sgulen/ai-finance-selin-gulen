# Superseded Lab 08 P/E Triangulation - Do Not Submit Alone

> The canonical comparable workpaper is `TSLA_Project1_Submission_DRAFT_UPDATED/docs/comparable-valuation-plan.md`, which adds an EV/revenue comparison and documents why results are not averaged with the DCF. This retained lab artifact provides the original P/E calculation only.

# Lab 08 - Tesla P/E Comparable-Company Triangulation

**Target:** Tesla, Inc. (TSLA)  
**Comparison date:** September 17, 2026  
**Question:** What would one Tesla share be worth at defensible peer P/E multiples, and how does that compare with the DCF?

## Peer policy

The comparison includes publicly traded vehicle manufacturers with public FY2025 GAAP diluted EPS by the comparison date. A company is excluded from a positive P/E calculation when annual GAAP diluted EPS is zero or negative. This is a narrow test of Tesla's vehicle-manufacturing earnings; it is not a complete valuation of Tesla's energy, software, autonomy, or Robotaxi opportunities.

## Candidates, sources, and decisions

| Company | Source / comparison input | Decision |
|---|---|---|
| TSLA | Tesla FY2025 Form 10-K; September 17, 2026 close $366.20; FY2025 GAAP diluted EPS $1.08 | Target |
| GM | GM FY2025 Form 10-K: [investor filing](https://investor.gm.com/static-files/36170429-ef23-4ad5-97dd-6a523c3f8deb); September 17, 2026 close $86.59; FY2025 GAAP diluted EPS $3.27 | Use. GM is a large vehicle manufacturer, but ICE mix and business-model differences are material. |
| RIVN | Rivian FY2025 Form 10-K; September 17, 2026 close $15.40; FY2025 GAAP diluted EPS -$3.07 | Exclude. A normal positive P/E is not meaningful with negative diluted EPS. |

## Calculation and validation

`GM P/E = $86.59 / $3.27 = 26.4801x`  
`TSLA implied value = 26.4801x * $1.08 = $28.60 per share`

| Check | Result |
|---|---|
| GM P/E recomputed by hand | 26.4801x; pass |
| One-peer TSLA P/E reference | $28.60/share |
| Leave-one-out check | Removing GM leaves no usable positive-EPS peer; no estimate. |
| Definition consistency | Price and annual GAAP diluted EPS are used for both TSLA and GM. |

## Interpretation and limitation

The P/E reference is far below the September 17, 2026 TSLA market price of $366.20. It supports the current watch/defer decision but is not sufficient as a standalone valuation. GM does not capture Tesla's energy, software, autonomy, Robotaxi, or different growth expectations. This is a one-peer reference rather than a peer range.

The existing Week 3 DCF records $43.93 per share, while the current workbench runs $22.09 per share. These results must be reconciled to their actual FCFF paths, WACC, terminal growth, bridge date, and share conventions before the final project is submitted. They must not be averaged mechanically.

## AI review and disposition

An AI counterquestion asked why a legacy ICE truck/SUV manufacturer was used rather than a broader, weighted peer set. The concern is accepted in part: automotive sales were Tesla's majority revenue source in the FY2025 materials, making GM relevant as a narrow vehicle-manufacturing reference; however, GM is not a complete business-model match. The analysis therefore uses GM only as a qualified triangulation and prominently retains the limitation.
