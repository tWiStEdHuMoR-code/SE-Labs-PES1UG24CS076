# Lab 7 — Fuzz Testing for Input Validation Bugs

**Student:** Anvi Srinivas  
**SRN:** PES1UG24CS076  
**Class:** 5B

## Overview

This submission applies Hypothesis-based fuzz testing to the ATM application used in Lab 6. The application exposes three functions:

- `withdraw()` — validates account type, balance, amount and bank flag before applying withdrawal rules.
- `pin_check()` — validates entered/stored PINs and the attempt count.
- `note_breakup()` — validates an amount before calculating its ₹500, ₹200 and ₹100 note breakdown.

The corrected implementation rejects malformed inputs with `ValueError` and preserves the application's normal business rules.

## Folder contents

```text
Lab7/
├── processor.py                 # corrected application
├── test_processor.py            # Hypothesis tests for all three functions
├── requirements.txt             # Python dependencies
├── README.md
├── original_buggy/
│   ├── processor.py             # original Lab 6 implementation
│   └── test_processor.py        # same fuzz tests, run against original code
└── Report/
    ├── Lab7_Report.pdf          # consolidated report and source code
    └── screenshots/
        ├── 0_setup_and_prompt.png
        ├── 1_original_run.png
        ├── 3_fixed_run.png
        └── 4_final_tests.png
```

## Setup

Use Python 3.8 or later. From this folder, install the dependencies:

```bash
python -m pip install -r requirements.txt
```

On Windows, `py` can be used instead of `python`.

## Run the original application

```bash
cd original_buggy
python processor.py
```

## Run fuzz tests against the original application

Run from inside `original_buggy`, so the test imports the original `processor.py`:

```bash
python -m pytest -q test_processor.py
```

The original implementation is expected to fail some fuzz properties. This is the defect-discovery stage.

## Run the corrected application and tests

Return to the `Lab7` folder:

```bash
cd ..
python processor.py
python -m pytest -q test_processor.py
```

The final test run shown in the supplied screenshot reports **14 passed**.

## Git submission

From the parent directory that contains `Lab7`:

```bash
git add Lab7/
git commit -m "Complete Lab 7 fuzz testing"
git push origin main
```

If this repository uses a branch other than `main`, replace `main` with that branch name.

## Evidence note

The report includes the supplied original-application screenshot, corrected-application screenshot and final passing-test screenshot. A separate terminal screenshot showing the original Hypothesis/pytest failures was not supplied; the report identifies this rather than presenting a recreated or fabricated test result. If the instructor explicitly requires that screenshot, capture it by running the original fuzz tests using the command above and add it to `Report/screenshots/`.
