# Cold-run log

- Tester name: Selin Gulen
- Date: 2026-11-23 (evening, Eastern Time)
- Fresh-clone method: cloned the repository with GitHub Desktop into a separate local folder and created a new `.venv` there.

## Commands run

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m streamlit run .\app.py
```

## First failure and resolution

The first failure was PowerShell blocking `Activate.ps1` because script execution was disabled. The process-scoped command `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` resolved it for that PowerShell session only.

The process also exposed repository completeness issues: the runnable Project 2 source and test files were not initially present in the cloned branch, and Python 3.14 required the `tests` folder to be importable. The missing Project 2 files were added to the branch, and `tests/__init__.py` and `tests/test_project_results.py` were added before rerunning the test command.

## Result after fixes

- Dependency installation: completed successfully with `pip install -r requirements.txt`.
- Automated tests: four tests passed.
- App launch: Streamlit started successfully and the Meridian investment-management app opened at its local URL.
- Committee decision location: the **Committee recommendation** section at the bottom of the app.
- Supporting evidence: `cold-run-tests.png` and `cold-run-app.png`.
- Fix commit URL: add the final GitHub commit URL after pushing the reproducibility fixes.
