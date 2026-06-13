# SADS Testing Guide

## 1. Running Tests

Run all unit, integration, and validation tests using:
```bash
python -m pytest
```

## 2. Writing New Tests
* Unit tests belong in `tests/unit/`.
* Subsystem tests belong in `tests/module/`.
* Acceptance tests belong in `tests/acceptance/`.
Ensure all math and physics calculations match analytical values. Refer to [TestSuites.md](file:///c:/Users/User/Documents/Sattelite%20Architecure%20Design/TestSuites.md) for more details.
