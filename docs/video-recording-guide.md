# Project 1 Video Recording Guide

Record three separate **Unlisted or Public** videos; do not use Private. Keep a small webcam view on screen, share the terminal/workbench, enable captions, and replace the transcript headers with the actual URLs, durations, and commit ID after recording. Avoid reading the scripts word-for-word if that makes you sound unnatural, but do not change the finance claims unless you also update the written artifacts.

## Before recording

1. Run `py -3 app.py --write-output`, then open `output/visible_output.md`, `docs/research-evolution.md`, and `docs/validation-and-ai-use.md`.
2. Run `py -3 app.py --interactive` in a terminal. Have these decimal inputs ready: `ebit_margin_shift`, then `0.01`; type `r` to restore; then `terminal_growth`, then `0.11` to show the failing check; type `r` again.
3. Make and save the human AI-off prediction required in the locked changed-input record **before** recording the changed-input test. Enter the real time and commit ID.
4. Open the named 2025 Tesla 10-K source and keep the evidence ledger accessible. Do not claim that the incomplete comps/transaction cross-check has been completed.
5. Test an unlisted-video link in an incognito/logged-out window, then correct the platform captions for `TSLA`, `FCFF`, `WACC`, `EBIT`, `NCI`, dates, and every material dollar/per-share figure.

## Video 1 - research evolution and AI-output check (max 3:00)

Show `docs/research-evolution.md`, the original Edition A file, `docs/validation-and-ai-use.md`, and the visible output. The unique proof is the before/after research decision and an independently checked AI output.

**Required evidence to show:** the Edition A status truthfully; A-to-B table; $25.80 base result; the 90.9% terminal-value share; one AI-use row; known-answer/monotonicity/base-year-reconciliation check; actual receipt status.

## Video 2 - codebase walkthrough and validation (max 5:00)

Show the repository tree, `src/model.py`, `app.py`, `output/visible_output.md`, and a terminal. Explain `run_model`, how forecast drivers flow through all statements, FCFF, the bridge, the bounded driver panel, and the validation suite. Demonstrate the +100bp margin run and the terminal-growth failure. State the peer/transaction limitation and show where it is documented.

**Required evidence to show:** code path; visible executed output; the Lab 05 known-answer result; balance-sheet/cash-flow/bridge checks; changed-input result; invalid-input failure; README reproduction command.

## Video 3 - committee presentation with live product demo (max 5:00)

Start with the live tool, not slides. In roughly the first minute, change a bounded driver, read the resulting sensitivity, reset base, deliberately enter the incoherent terminal-growth input, show the red failure, and recover. Then present the decision with the product still visible. Lead with watch/defer, not with model-building history.

**Required evidence to show:** live bounded driver; base reset; red check failure and recovery; $25.80 base result/range; named downside/base/upside cases; reverse-DCF expectation; conditional action; risks; reversal trigger; committee ask.

## Immediately after recording

1. Correct the captions and copy the corrected text into the matching `docs/transcript-video-*.txt` file.
2. Replace each transcript's URL, duration, and `STUDENT MUST ENTER` fields. Adjust timestamps to match your actual video.
3. Put the stable links, titles, durations, transcript locations, and exact evidence timestamps into `docs/project-submission-manifest.csv`.
4. Regenerate PDFs only after your receipt and locked-record fields are complete: `py -3 tools/build_submission_pdfs.py`.
