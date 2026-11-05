---
name: buffett-10k-analysis
description: Compute a five-year, 10-K-only EDGAR record for a public company and write a price-free business memo using its owner earnings and ROE.
---

# Buffett 10-K analysis

Use this skill for a reproducible, business-first assessment. The script computes the financial values; the model judges only the values it prints.

## Run

The SEC requires a declared user agent. Do not save a personal name or email in the project. In the current PowerShell session only, set:

```powershell
$env:SEC_USER_AGENT = "Your Name your.email@example.com"
```

Then run the script from the `finance-ai` folder:

```powershell
& ".\.venv\Scripts\python.exe" ".\.agents\skills\buffett-10k-analysis\scripts\edgar_facts.py" COST
```

## Rules

- Read keyless SEC EDGAR Company Facts data. Do not use prices or paid data.
- Admit only `form == "10-K"` and `fp == "FY"` facts. Flows must cover approximately one year.
- For each fiscal end, retain the latest filing. This handles restatements and prevents a stale comparative disclosure from winning.
- Use `RevenueFromContractWithCustomerExcludingAssessedTax`, otherwise `Revenues`; `NetIncomeLoss`; `NetCashProvidedByUsedInOperatingActivities`; `PaymentsToAcquirePropertyPlantAndEquipment`, otherwise `PaymentsToAcquireProductiveAssets`; and `StockholdersEquity`.
- Compute ROE as net income / equity only when equity is positive. Compute owner earnings as cash from operations - capex only when both inputs exist.
- Show missing facts as `not found` and derived unavailable values as `not known`.
- Report: ROE at least 15% each year, owner earnings positive each year, and owner earnings growth from first to last year.

## Memo rules

Write a short Markdown memo that reaches **own**, **watch**, or **pass**. Judge the business, not its share price, and include no price, valuation, or target.

- Cite only figures and percentages the script printed.
- If owner earnings/capex is not available, say the business cannot be judged on owner earnings from this record.

## Limits

This is a learning demonstration, not investment advice. Read the underlying 10-K when a tag is missing, unusual, or economically ambiguous.
