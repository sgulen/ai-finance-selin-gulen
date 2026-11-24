# Validation and AI use

## Sources and as-of boundary

The application uses monthly adjusted-close prices for BIL, IEF, LQD, and ACWI in `prices.csv`. The download date and final observation date are 2026-10-22. The app excludes any later observation. Sources, proxy definitions, and limitations appear in `prices_sources.md`.

## Validation performed

- Automated tests: `python -m unittest discover -s tests -v`.
- Known answer: the bundled 59-return base case produces a 60% BIL / 40% ACWI constrained portfolio under a 6.50% objective and 3.00% reserve minimum.
- Loud failure: a 100% return objective produces no feasible constrained portfolio.
- Baseline comparison: equal weight fails the return objective; the 40% LQD / 60% ACWI benchmark fails the reserve minimum.
- Estimation-window stress: reducing the window to 36 returns changes the constrained portfolio to 85% BIL / 15% ACWI, a 25-percentage-point shift that triggers the stated stop condition.

## Limitations

- Historical annualized estimates are not forecasts.
- The available sample is limited.
- The optimization grid is 5 percentage points.
- The committee has not defined a binding loss-limit policy.

## Locked Changed-Input Record 

- Date and time of prediction: 11/23/2026 10:13 PM, Eastern Time
- GitHub commit URL created before the run: https://github.com/sgulen/ai-finance-selin-gulen/commit/ee531db2c349f0a296749bef6377bd304e572240
- Input changed: Objective return
- Old value and units: 6.50% annualized historical return estimate
- New value and units: 7.00% annualized historical return estimate
- Finance mechanism: A higher historical return requirement will narrow the set of feasible portfolios. While BIL is the reserve-eligible Treasury bill fund, ACWI has a higher historical return estimate in the baseline BIL/ACWI allocation. In order to meet the higher target, the app will need more ACWI and less BIL. Neither of the fund's historical return estimate will be changed by adjusting the target.
- Prediction of the direction and magnitude of return change: Annualized historical return estimate will increase from about 6.84% to 7.3% (0.46 percentage points). 
- Prediction of the direction and magnitude of volatility change: Annualized volatility will increase from 6.01% to 6.8%. An increase in equity exposure and decrease in Treasury bill exposure is expected to increase volatility.
- Prediction of the weight change: ACWI will increase from 40% to around 45% and BIL will decrease from 60% to about 55%. IEF and LQD will remain around zero.
- Prediction of the committee-decision effect: Committee decision will remain rejection. Increasing the higher estimated return will not resolve the percentage point estimation window stress failure or missing loss-limit policy.

### Result after the run 

- Before result: At the 6.50% objective, the constrained portfolio
  was 60% BIL / 40% ACWI, with a 6.84% historical annualized return
  estimate, 6.01% annualized volatility, 60.00% reserve-eligible
  weight, and a PASS verdict.
- After result: At the 7.00% objective, the constrained portfolio
  was 55% BIL / 45% ACWI, with a 7.24% historical annualized return
  estimate, 6.74% annualized volatility, 55.00% reserve-eligible
  weight, and a PASS verdict. IEF and LQD remained at 0.00%.
- Actual effect on return, volatility, weights, and decision: The
  return estimate increased by about 0.40 percentage points,
  volatility increased by about 0.73 percentage points, ACWI increased
  by 5 percentage points, and BIL/reserve-eligible allocation
  decreased by 5 percentage points. The committee decision remained
  Reject adoption and do not allocate now because the separate 36-
  month stress sensitivity and missing loss-limit policy remain
  unresolved.
- Did the result match your prediction? : The results matched my prediction, as ACWI increased from 40% to 45% and BIL decreased from 60% to 55%. Historical annualized return estimate increased from 6.84% to 7.24%, close to my 7.3% prediction. Annualized volatility increased from 6.01% to 6.74%, close to my 6.8% prediction.
- Reconciliation or failure diagnosis: Return exceeded 7% due to the 5 percentage point optimizer search increments. All four implemented mandate checks passed. This portfolio PASS does not resolve stress or loss-limit policy. Since the output does not show a new stress result or a new committee decision, it does not resolve reasons for rejection.

## AI-use disclosure

- Tool/model: OpenAI Codex.
- Interaction date: 2026-11-23.
- Material uses: code organization, app structure, test scaffolding, document structure, and consistency checks.
- Checks performed: results are generated from `project_results.py`, exported to `visible-output.json`, and covered by automated baseline, known-answer, and failure tests.
- Disposition: AI-proposed structure was used only after checking the executable calculations and output. The final recommendation and the locked prediction are the student's responsibility.
