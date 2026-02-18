# Problem Suites

This directory stores suite-level problem batches for Intake v2 automation.

Create a suite template:

```bash
python3 tools/intake/problem_suite.py init --suite-id firstproof_2026
```

Run suite phases:

```bash
python3 tools/intake/problem_suite.py run --suite suites/firstproof_2026/suite.yaml --phase research-pack
python3 tools/intake/problem_suite.py run --suite suites/firstproof_2026/suite.yaml --phase lean-commit
```
