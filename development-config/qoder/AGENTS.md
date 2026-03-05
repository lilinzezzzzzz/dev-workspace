# Agent Instructions

> **Scope:** Technical tasks involve code, debugging, architecture, APIs, or system design. For other topics (creative writing, general Q&A, casual chat), respond naturally without applying coding standards.

## Role & Context

* **User Role:** Senior Full-Stack Engineer (Backend-focused, Python & Golang).
* **Tech Stack:** AI (LLMs, GenAI, RAG, Fine-tuning, MLOps) + Backend (Distributed Systems).

## Coding Standards

### General

* **Quality:** Production-ready, secure, no undefined behavior. Linter compliance assumed at generation time.
* **Architecture:** Modular, scalable, clean code for AI enterprise applications.
* **Type Safety:** Public APIs fully type-annotated. Explicit types over permissive typing.

### Python

* **Style:** Pythonic, PEP 8, Pydantic v2. Compatible with ruff + pylance (basic mode). No implicit `Any`.
* **Function Signature:** Prefer keyword-only arguments (use `*` separator) for clarity and safety.
* **Database:** SQLAlchemy 2.0+ ORM with type annotations (no raw SQL).
* **Async:** Use anyio (not asyncio). Use httpx for HTTP, anyio.create_task_group for concurrency. Isolate I/O blocking via anyio.to_thread.run_sync, CPU-bound via anyio.to_process.run_sync.
* **Error Handling:** Custom exceptions with error codes. Never bare `except:`. Log with context before re-raising.
* **Logging:** loguru for structured logging. Levels: DEBUG (dev), INFO (ops), WARNING/ERROR (issues). No print.
* **API Design:** FastAPI + Pydantic v2. Prefer GET/POST. Consistent error responses with codes and messages.
* **Testing:** pytest + pytest-asyncio. >80% coverage on critical paths. Mock external services.
* **Runtime:** uv for dependency management and script execution. pyproject.toml (PEP 621) + uv.lock. No pip/poetry/conda.
  * Use `uv run <script>` to execute Python scripts (handles virtualenv automatically)
  * Use `uv run pytest` instead of `pytest` directly
  * Use `uv run python -m <module>` for module execution
  * Use `uv add <package>` for dependency installation
  * Use `uv sync` to sync dependencies from lock file

### Golang

* **Style:** Effective Go + Go Code Review Comments. Pass go vet, staticcheck, golangci-lint. Use gofmt/goimports.
* **Runtime:** Go Modules (go.mod/go.sum). Prefer stdlib, minimize dependencies.
* **Conventions:**
  * Errors: Handle explicitly, no `_` for error returns.
  * Concurrency: Idiomatic goroutines/channels; sync primitives for shared state.
  * Naming: MixedCaps (exported), mixedCaps (unexported), no underscores.
  * Context: First parameter, propagate cancellation/deadlines.

## Git

* **Branches:** `feature/`, `bugfix/`, `hotfix/`, `release/<version>`
* **Commits:** `<type>(<scope>): <subject>` (Conventional Commits, imperative mood, <50 chars)
* **Merge:** feature→develop: squash/rebase; develop→main: merge commit
* **Language:** Chinese preferred for readability

## Response Preferences

* **Conciseness:** Direct, brief, Chinese preferred. Technical terms in both Chinese + English.
* **Solution-Oriented:** Robust code with edge-case handling. No quick-and-dirty scripts.
* **Format:** Structured Markdown for comparisons and analysis.

## Verification

* Critique all designs before executing. Flag risks (security, scalability, concurrency).
* Propose industry-standard alternatives for anti-patterns.

## Web Search

* Enabled actively. Use for updated libraries, technologies, current events.
* Prioritize latest official docs over training data.

## Self-Review Checklist

Before finalizing code:
* [ ] All public functions have type hints and docstrings
* [ ] No hardcoded secrets or magic numbers
* [ ] Edge cases handled (empty inputs, None, concurrent access)
