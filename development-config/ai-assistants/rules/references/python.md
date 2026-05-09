---
trigger: model_decision
description: Must be loaded before any Python-related implementation, review, refactor, dependency, test, packaging, FastAPI, Pydantic, SQLAlchemy, Alembic, worker, RAG, or LLM service task.
---
# Python Rules

Use these rules for Python implementation, review, refactor, dependency,
test, packaging, FastAPI, Pydantic, SQLAlchemy, Alembic, worker, or LLM/RAG
service work.

## Baseline

- When the project has no conflicting convention:
  Python 3.11+, `uv`, `pyproject.toml` (PEP 621). For service work,
  prefer FastAPI, Pydantic v2, SQLAlchemy 2.x, and Alembic unless the
  project already standardizes otherwise.
- Ruff/Pylance-compatible; no implicit `Any`.
- New code should add type annotations wherever practical,
  especially for function parameters, return values, module-level
  constants, data models, and variables whose inferred type is unclear.

## Environment And Commands

- Prefer `uv` for Python environment creation, dependency management,
  locking, packaging, and command execution. Avoid invoking bare
  `python`, `pip`, `pytest`, `ruff`, or type checkers when the command
  should run inside the project environment; use `uv run ...` instead.
- New environments should use the project-declared Python version when
  present. Common commands:
  - `uv python install <version>` to install a missing interpreter.
  - `uv python pin <version>` to pin the project interpreter when the
    repository intentionally owns `.python-version`.
  - `uv sync` to create or update the environment from `pyproject.toml`
    and `uv.lock`.
  - `uv add <package>` / `uv remove <package>` for dependency changes.
  - `uv lock` when dependency metadata changed but installation is not
    otherwise required.
  - `uv run pytest ...`, `uv run ruff check ...`, and
    `uv run <type-checker> ...` for verification.
- For legacy requirements-only projects, use `uv venv` plus
  `uv pip install -r requirements.txt`. Do not introduce
  `pyproject.toml` or `uv.lock` solely to run a small task unless the
  user asked to migrate dependency management.

## Imports And Typing

- Imports: isort order, one import per line for top-level packages, all
  imports at module top level. Local imports are allowed only to break a
  circular dependency; document the reason inline.
- New code uses lowercase built-in generics and `collections.abc`
  generics. Do not introduce deprecated `typing` aliases such as `Dict`,
  `List`, `Optional`, `Union`, or `AsyncGenerator`.
- Use PEP 604 syntax: `A | B` and `T | None`.
- Container parameter types follow variance: read-only inputs use
  covariant `collections.abc` types (`Sequence`, `Mapping`, `Set`,
  `Iterable`) so subtypes pass without friction; use concrete mutable
  generics (`list`, `dict`, `set`) only when the function mutates the
  argument or the concrete type is part of the contract. Returns may
  stay concrete when ownership is handed to the caller.

## Data And Interfaces

- Prefer explicit data models over loose dicts: `TypedDict` for typed
  mappings, `dataclass` for plain data carriers, Pydantic v2 for
  validated I/O models.
- Prefer `Protocol` for interface dependencies and test seams. Use `ABC`
  only when shared implementation, enforced inheritance, or runtime
  nominal checks are required.
- Prefer module-level functions. Use instance methods only when behavior
  depends on `self`; `@classmethod` for alternate constructors;
  `@staticmethod` only when type ownership is clear.
- Prefer keyword-only parameters unless positional calls clearly improve
  readability. Use `def` over lambda assignment and f-strings over
  `.format()`.

## Errors And Runtime

- Prefer built-in exceptions that match the failure semantics for
  programming errors, such as `ValueError`, `TypeError`, `KeyError`,
  `IndexError`, `AttributeError`, `RuntimeError`, or
  `NotImplementedError`. Do not use programming-error exceptions for
  business logic. Keep custom business exception hierarchy flat.
- Use `anyio` + `TaskGroup` for concurrency, `httpx` for HTTP, and
  `anyio.to_thread` for blocking I/O.

## Frameworks And Persistence

- FastAPI: explicit request/response models, `Depends` for DI, and
  consistent error envelopes.
- Pydantic: v2 patterns only; avoid v1 compatibility shims.
- SQLAlchemy: 2.x typed patterns; Alembic for migrations.

## Documentation And Tests

- Docstrings are required for public API. Use Google style, imperative
  mood, and one-line summary. Add `Args`/`Returns`/`Raises` only when
  non-obvious. Inline comments explain why.
- Tests: use `pytest`; unit tests for logic and edges, integration tests
  for cross-boundary flows. Mock only external I/O. Critical paths need
  explicit happy, error, and edge cases.
