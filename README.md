# TSLA Valuation Workbench

## Decision

For the equity-research committee, the tool recommends **watch/defer, not initiate**, at the model's base-case value range. The conclusion is conditional: it must be revisited if Tesla demonstrates sustained operating-margin expansion while AI and factory capital spending translates into operating returns.

**As of date:** December 31, 2025 for financial-statement inputs and bridge items; September 10, 2026 for the screen/market-price reference retained from the student's evidence packet. All financial inputs are USD millions except per-share amounts.

This is an educational valuation workbench, not investment advice.

## What this repository contains

- `app.py` - locally runnable semi-adjustable terminal workbench. It exposes bounded revenue-growth and EBIT-margin drivers, resets to base, shows a WACC-growth grid, and displays checks that fail loudly.
- `src/model.py` - five-year income statement, balance sheet, cash flow, FCFF DCF, bridge, checks, one-at-a-time sensitivities, and linked downside/base/upside cases.
- `output/visible_output.json` and `output/visible_output.md` - executed base output a grader can inspect without running code.
- `docs/` - Edition B research evolution, decision memo, validation and AI-use record, source/evidence ledger, video scripts, and submission manifest.
- `submission/` - PDFs prepared for Brightspace after the student completes the marked AI-off/receipt fields.

## Run

Requires Python 3.10+ and only the standard library.

```powershell
cd C:\Users\roseg\OneDrive\Desktop\Finance_AI_Selin_Gulen\TSLA_Project1_Submission_DRAFT_UPDATED
py -3 app.py --report
py -3 app.py --interactive
py -3 app.py --write-output
```

`--interactive` lets a reviewer change bounded drivers. Entering a number outside the displayed bound, or a terminal growth rate at or above WACC, produces a red `CHECK FAILED` result and no valuation. Use `r` to restore the base case.

## Data and limitations

Historical base-year figures and bridge items are traced in `docs/evidence-ledger.csv` to Tesla's FY2025 Form 10-K. The final model uses the segmented automotive/energy/services pro-forma documented in `docs/assumption-challenge-record.md`. The ledger reconciles FY2025 revenue to $94.827B; $97.690B is the 2024 comparator. The comparable workpaper is a qualified triangulation, not a mechanically averaged target; preserve its retained historical-price source evidence before freeze.

## Reproducibility

Run `py -3 app.py --write-output` to regenerate the visible output. The `validation` section of the report contains the known-answer, monotonicity, articulation, bridge, bounds, and changed-input tests. No credentials, network connection, packages, or private data are needed.

## Required student actions before submission

The course requires a real Brightspace Edition A receipt and a human-authored AI-off changed-input prediction made before execution. Neither can be fabricated. Complete the clearly marked fields in `docs/research-evolution.md`, `docs/validation-and-ai-use.md`, and `docs/project-submission-manifest.csv`; then regenerate the PDFs with `py -3 tools/build_submission_pdfs.py` and record the actual video links/durations/transcripts after recording.
