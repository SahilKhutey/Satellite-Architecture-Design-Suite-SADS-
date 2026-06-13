# Contributing to SADS

Welcome to the Satellite Architecture Design Suite (SADS) project! We follow standard systems engineering review processes to ensure flight-simulation-grade scientific correctness.

## 1. Code Style and Linters
We use `black` and `ruff` for code formatting and style. Run them before committing:
```bash
poetry run black mbse/ ai/ digital_twin/ simulation/ engines/
poetry run ruff check mbse/ ai/ digital_twin/ simulation/ engines/
```

## 2. Pull Request Quality Gates
Every pull request must pass the SADS quality checks:
1. **Compilation**: Run syntax compile check:
   ```bash
   python -m py_compile mbse/*.py ai/*.py digital_twin/*.py simulation/*.py
   ```
2. **Tests**: Ensure the pytest suite completes with 100% success:
   ```bash
   python -m pytest
   ```
3. **Physics & Mathematics Bounds**: Changes to dynamics, orbits, or thermal solvers must preserve energy conservation and numerical convergence.

## 3. Pull Request Guidelines
* Branch from `main` with prefix `feature/` or `bugfix/`.
* Complete the Pull Request Template checklist in `.github/PULL_REQUEST_TEMPLATE.md`.
* Request review from the corresponding Subsystem Maintainer (see `GOVERNANCE.md`).
