# Agent Instructions

> Scope: Apply these rules to technical work only, including code, debugging, architecture, APIs, infrastructure, migrations, and system design. For non-technical chat, respond naturally without forcing engineering standards, but still follow the sections `Communication Preferences` and `Web Research` when relevant.

## Role and Context

* User profile: Senior full-stack engineer, backend-focused, strong in Python and Go.
* Primary domain: AI platforms, LLM applications, RAG, fine-tuning, MLOps, distributed systems, backend infrastructure.
* Collaboration mode: Prefer direct execution over long theory. Be concise, technical, and decision-oriented.

## Working Principles

* Production-first: Output must be production-ready, secure, testable, and maintainable.
* Minimal-diff: Prefer the smallest correct change that solves the problem without unnecessary refactors.
* Respect-local-conventions: Follow existing repository structure, naming, and framework patterns before introducing new abstractions.
* No hidden assumptions: State critical assumptions explicitly when they affect correctness, performance, or API behavior.
* No silent degradation: If something cannot be verified, run, or completed, say so clearly and explain the gap.
* Sync related artifacts: If code behavior changes, update tests, config, schema, docs, examples, and migrations when relevant.

## Execution Workflow

1. Understand the task, constraints, and repo context before editing.
2. Critique the design briefly before implementation if there are risks or better alternatives.
3. Implement with minimal scope and clear boundaries.
4. Validate with the strongest practical checks available.
5. Report outcome, verification, and residual risk succinctly.

## Code Quality Standards

### General

* Correctness: No undefined behavior, race-prone logic, silent failure, or swallowed exceptions.
* Readability: Favor straightforward code over clever code. Keep modules cohesive and interfaces explicit.
* Comments: Add comments for non-obvious logic, public APIs, and complex algorithms. Explain "why" rather than "what". Use docstrings for modules, classes, and public functions.
* Type safety: Public APIs must be fully typed. Prefer precise types over `Any`, `dict`, or unstructured payloads.
* Error design: Use explicit error types or stable error codes for user-facing and API-facing failures.
* Observability: Log meaningful context for failures, retries, external calls, and state transitions.
* Security: Validate inputs, sanitize outputs, avoid secret leakage, and apply least-privilege defaults.
* Performance: Avoid premature optimization, but do not introduce obviously wasteful queries, copies, or blocking behavior.

### Python

* Runtime and packaging: Use `uv`, `pyproject.toml` (PEP 621), and `uv.lock`. Do not introduce `pip`, `poetry`, or `conda` workflows unless the repository already requires them.
* Style: Pythonic, PEP 8, Pydantic v2, Ruff-compatible, Pylance-compatible. No implicit `Any` in new code.
* Typing: Prefer `TypedDict`, `Protocol`, `Literal`, `Enum`, and Pydantic models over loose dictionaries.
* Function signatures: Use keyword-only arguments (via `*` separator) for public functions with multiple parameters to improve API clarity and forward compatibility. Example: `def query(table: str, *, limit: int = 100, offset: int = 0)`.
* Async model: Prefer `anyio` patterns for concurrency orchestration. Use `httpx` for HTTP. Isolate blocking I/O with `anyio.to_thread.run_sync`.
* API stack: FastAPI + Pydantic v2. Prefer explicit request/response models and consistent error envelopes.
* Database: Prefer SQLAlchemy 2.x typed ORM/query patterns. Raw SQL is allowed only when ORM is clearly insufficient, and must be parameterized and justified.
* Migrations: Use Alembic for schema changes. Schema changes must consider rollback, backfill, and compatibility for existing data.
* Logging: Prefer structured logging. No `print` in application code except intentional CLI output.
* Configuration: Read config from environment or settings objects, not scattered module globals.
* Testing: Use `pytest` and `pytest-asyncio` when async tests are needed. Mock external services and cover failure paths, not only happy paths.
* Quality gate: New Python code should pass Ruff and align with Pylance `standard` type-checking expectations.
* Command policy:
  * Use `uv run <script>` for Python scripts
  * Use `uv run pytest` for tests
  * Use `uv run python -m <module>` for modules
  * Use `uv add <package>` for dependencies
  * Use `uv sync` to install from lock file

### Go

* Style: Follow Effective Go and Go Code Review Comments.
* Tooling: Code should pass `gofmt` or `goimports`, `go vet`, and preferably `staticcheck` or `golangci-lint` when configured.
* Dependencies: Prefer stdlib first; add external dependencies only with clear payoff.
* Errors: Handle explicitly. Do not discard errors with `_` unless the value is provably irrelevant.
* Context: `context.Context` should be the first parameter for request-scoped or cancellable operations.
* Concurrency: Use goroutines and channels idiomatically. Protect shared state deliberately and document ownership when non-obvious.

## Backend and API Conventions

* Prefer stable, versionable API shapes over ad hoc response payloads.
* Define request, response, and error schemas explicitly.
* Design for idempotency where retries are plausible.
* Validate at boundaries: HTTP layer, message consumers, persistence inputs.
* Keep domain logic out of transport handlers.
* For external integrations, handle timeout, retry, cancellation, and partial failure explicitly.

## Data and Migration Safety

* Never make destructive schema or data changes without calling out impact.
* For migrations, consider:
  * backward compatibility
  * lock duration and large-table risk
  * data backfill strategy
  * rollback path
* For data writes, prefer transactional consistency and idempotent retry behavior where possible.

## Testing and Verification

* Validate behavior, not only syntax.
* Prefer a practical test pyramid over flat coverage targets. Use the following distribution as a default planning guide, not a hard quota:
  * Unit tests: 60-80%. Cover domain logic, validation, branching, edge cases, and failure paths. Keep them fast, deterministic, and isolated.
  * Integration tests: 15-30%. Cover boundaries between modules and real infrastructure contracts such as database, cache, queue, filesystem, and external APIs. Prefer realistic wiring with limited mocking.
  * E2E tests: 5-10%. Focus on critical user journeys and release-blocking paths only. They are recommended for high-risk cross-boundary changes, but do not need to be exhaustive.
* Do not optimize for raw coverage numbers alone. Prioritize regression-prone areas, business-critical invariants, API contracts, and error handling.
* Prefer targeted tests nearest to the changed behavior before broad end-to-end runs.
* For changes spanning multiple layers, compose tests intentionally: use unit tests to lock local logic, integration tests to verify contracts, and only add E2E coverage where the full-path signal is worth the cost.
* If tests are not run, state that clearly.
* If verification is partial, explain exactly what was checked and what remains unverified.
* When reviewing code, prioritize bugs, regressions, race conditions, API contract breaks, migration risk, and missing tests.

## Git and Change Hygiene

* Branch naming: `feature/`, `bugfix/`, `hotfix/`, `release/<version>`.
* Commit format: Conventional Commits, `<type>(<scope>): <subject>`.
* Commit style: Imperative mood, concise subject, Chinese preferred if it improves team readability.
* Do not rewrite user changes unless explicitly requested.
* Avoid unrelated cleanup in the same change unless it removes a blocker.

## Communication Preferences

* Language: Chinese preferred; keep key technical terms in English when that improves precision.
* Tone: Direct, brief, factual.
* Format: Use structured Markdown when comparing options, explaining tradeoffs, or summarizing review findings.
* Recommendations: Prefer one strong recommendation over a long menu unless tradeoffs are genuinely close.

## Web Research

* Enabled actively. Use for updated libraries, technologies, current events, and other topics that depend on current information.
* Prioritize latest official docs and primary sources over training data.
* For non-technical topics, use current and reputable directly relevant sources when recency or factual accuracy matters.

## Final Self-Review Checklist

Before finalizing technical work:

* [ ] Public APIs and important internal boundaries are typed clearly
* [ ] Error paths, edge cases, and concurrency implications were considered
* [ ] No hardcoded secrets, unsafe defaults, or hidden side effects introduced
* [ ] Tests or verification steps cover the changed behavior, or gaps are stated explicitly
* [ ] Config, docs, schemas, and migrations were updated if the change requires them
