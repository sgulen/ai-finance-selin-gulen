# Meridian investment-management application

AI use: I used OpenAI Codex to help organize and test code. I checked material outputs against the bundled price data, the calculation code, and automated tests.

The analysis and decision are mine. This is for educational purposes only and is not investment advice.

## Committee decision

Reject adoption and do not allocate now. The base constrained portfolio is 60% BIL and 40% ACWI, but reducing the estimation window to the last 36 monthly returns changes the constrained allocation to 85% BIL and 15% ACWI: a 25-percentage-point shift that exceeds the stated 10-percentage-point stop trigger.

## What the app does

The app compares equal weight, a 40% LQD / 60% ACWI benchmark, and the lowest-volatility long-only portfolio that meets the stated return and reserve constraints. It uses only monthly adjusted-close prices in `prices.csv` through the displayed as-of date.

## Run the app

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
py -m venv .venv
& .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run .\app.py
```

## Run the tests and reproduce visible output

```powershell
python -m unittest discover -s tests -v
python export_results.py
```

## Repository map

- `app.py` — Streamlit application.
- `project_results.py` — single source of truth for portfolio, baseline, mandate, and stress results.
- `portfolio.py` — return, volatility, covariance, and constrained-search engine.
- `prices.csv` — bundled monthly adjusted-close input data.
- `prices_sources.md` — sources and data limitations.
- `export_results.py` — writes the reproducible JSON result.
- `tests/test_project_results.py` — automated known-answer and failure tests.
- `docs/` — final submission artifacts.

## Data and as-of boundary

The application uses BIL, IEF, LQD, and ACWI monthly adjusted-close prices downloaded from Yahoo Finance. The final input observation and as-of date are 2026-10-22. Historical annualized return estimates are not forecasts. See `prices_sources.md`.

## Limitations

- The 59-return sample is short and historical estimates are unstable.
- Adjusted-close data and provider revisions can affect results.
- The optimizer searches weights in 5-percentage-point increments.
- The loss-limit policy is not formally defined, which independently prevents adoption.

## Final evidence

- `docs/visible-output.md`
- `docs/visible-output.json`
- `docs/decision-memo.md`
- `docs/validation-and-ai-use.md`
- `docs/cold-run-log.md`
