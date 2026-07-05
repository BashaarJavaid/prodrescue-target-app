# prodrescue-target-app

A small, intentionally-buggy Python service used as the **live demo target** for [ProdRescue](https://github.com/BashaarJavaid/ProdRescue), a self-healing SRE agent.

This repo isn't meant to be a real payments service — it's a sandbox where ProdRescue's Dev and QA agents actually operate: reading a crash, patching the source, running the test suite in an isolated Docker harness, and opening a real GitHub Pull Request against this repo with the fix.

**[See the merged AI-authored PRs](https://github.com/BashaarJavaid/prodrescue-target-app/pulls?q=is%3Apr+is%3Amerged)** — each one was diagnosed, patched, and opened autonomously by ProdRescue.

## What this app is

A toy `payments` service with a handful of classic production bugs baked in on purpose:

- `charge()` dereferencing a `None` order → `AttributeError`
- `build_request()` assuming a `currency` key always exists → `KeyError`
- `split_amount()` dividing by zero recipients → `ZeroDivisionError`
- `decode_token()` splitting a `None` token → `TypeError`
- `first_charge()` indexing into an empty order batch → `IndexError`

Each bug is exercised by a corresponding pytest test. ProdRescue ingests a crash log from this app, generates a root-cause analysis, writes a full-file patch, and validates it by running these tests inside an isolated, network-locked Docker container — only opening a PR once the patch passes and test coverage doesn't regress.

## How it fits into ProdRescue

```
Production crash (from this app) → ProdRescue Triage/Dev/QA agents → patched file
                                                                    → isolated Docker test run
                                                                    → GitHub PR opened on this repo
```

ProdRescue treats this repo as an external, real GitHub target — cloning it, applying patches, running its actual test suite in a scoped harness, and pushing branches/PRs back to it — rather than mocking any of that behavior.

## Project layout

```
src/payments/
  auth.py        # token decoding helper (AuthError on invalid/missing tokens)
  processor.py   # Order/charge/build_request/split_amount/first_charge
tests/
  test_auth.py       # covers decode_token
  test_processor.py  # covers charge, build_request, split_amount, first_charge
Dockerfile         # isolated container the QA harness execs pytest into
pyproject.toml     # pytest config (src on pythonpath, tests/ as testpaths)
requirements.txt   # pytest, pytest-cov
```

## Running the tests locally

```bash
pip install -r requirements.txt
pytest --cov=src
```

## Running in the isolated harness (as ProdRescue does)

```bash
docker build -t prodrescue-target-app .
docker run --rm --network none prodrescue-target-app pytest
```

The container is built to stay alive (`sleep infinity`) so ProdRescue's QA agent can `exec` a fresh `pytest` run into it per-patch attempt, rather than rebuilding the image each time.

## Why it exists

Most "agentic SRE" demos fake the crash-to-fix loop. This repo makes it real: an actual GitHub repository, with actual bugs, actual tests, and actual PRs opened by an agent — nothing here is scripted or mocked for the demo.
