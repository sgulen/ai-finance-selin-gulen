# Decision memo

AI use: I used OpenAI Codex to help organize and test code. I checked material outputs against the bundled data, code, and tests.

The analysis and decision are mine. This is for educational purposes only and is not investment advice.

## Recommendation

Reject adoption and do not allocate capital now. The base constrained portfolio meets the stated return and reserve requirements, but its allocation is too sensitive to the estimation window: it moves from 60% BIL / 40% ACWI using all 59 monthly returns to 85% BIL / 15% ACWI using the last 36. That 25-percentage-point shift exceeds the 10-percentage-point stop trigger. The loss-limit policy also remains undefined.

## Committee ask

Do not approve an allocation or pilot at this time. Authorize a redesign only after the committee defines a binding loss-limit policy and the revised process is retested under a precommitted estimation policy.

## Mandate and as-of date

- Intended user: investment committee.
- Universe: BIL, IEF, LQD, and ACWI.
- Benchmark: 40% LQD / 60% ACWI.
- Objective: historical annualized return estimate of at least 6.50%.
- Risk measure: annualized volatility.
- Constraints: long-only, fully invested, and at least 3.00% in BIL plus IEF.
- As-of date: 2026-10-22.

## Evidence

The equal-weight baseline fails the return objective (3.35% versus 6.50%). The benchmark meets the return objective (6.77%) but fails the 3.00% reserve minimum because it holds no BIL or IEF. The base constrained portfolio passes every modeled rule at 6.84% estimated return, 6.01% volatility, and 60.00% reserve-eligible allocation.

## Stress result and stop condition

The stress run changes the estimation window from all 59 available monthly returns to the latest 36. The constrained allocation changes from 60% BIL / 40% ACWI to 85% BIL / 15% ACWI. The largest 25-percentage-point shift is above the 10-percentage-point stop trigger, so the process is rejected even though the stressed portfolio still passes the modeled constraints.

## Risks and limitations

Historical adjusted-close estimates are not forecasts; the sample is short; source data can be revised; and the search uses 5-percentage-point weights. More importantly, the committee has not defined a binding loss-limit policy, so a volatility-only selection cannot establish mandate suitability.

## Monitoring and reversal triggers

If the process is redesigned, monitor monthly return estimates, volatility, reserve eligibility, and allocation changes under the fixed stress policy. Do not reconsider adoption until the loss-limit policy is defined and the stressed allocation shift is at or below 10 percentage points.

## Validation and AI-use record

See `validation-and-ai-use.md`.
