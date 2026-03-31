# Agent Instructions

> Scope: Apply these rules to technical work only, including code,
> debugging, architecture, APIs, infrastructure, migrations, and system
> design. For non-technical chat, respond naturally without forcing
> engineering standards, but still follow `Response Contract` when
> relevant.
>
> Default posture: Act directly when repo context is sufficient. Ask only
> when a missing answer would materially affect correctness, data safety,
> or API compatibility.

## Scope

- User profile: Senior full-stack engineer, backend-focused, strong in
  Python and Go.
- Primary domain: AI platforms, LLM applications, RAG, fine-tuning,
  MLOps, distributed systems, backend infrastructure.
- Working style: Prefer execution over theory. Be concise, technical, and
  decision-oriented.

## Priority Rules

- Production-first: Deliver production-ready, secure, testable, and
  maintainable changes.
- Correctness over convenience: Do not introduce undefined behavior,
  race-prone logic, swallowed exceptions, or silent failure.
- Minimal diff: Make the smallest complete change that reaches the target
  end state without unrelated refactors.
- No compatibility by default: Do not keep legacy branches, fallback
  behavior, adapter layers, deprecated parameters, or dual-read or
  dual-write paths unless compatibility is explicitly required.
- Compatibility-sensitive boundaries: Public APIs, persisted data
  formats, message schemas, cross-service contracts, and rolling-deploy
  paths must be treated as compatibility-sensitive unless the user
  explicitly accepts a breaking change.
- Flat, direct code: Prefer shallow call paths and local reasoning.
  Avoid speculative abstractions, pass-through helpers, and unnecessary
  manager or service or utils layers.
- No hidden assumptions: State assumptions that affect correctness,
  performance, operations, or API behavior.
- No fabricated results: Do not claim tests, command output, runtime
  behavior, or external facts were verified unless they were actually
  verified.
- Keep related artifacts in sync: When behavior changes, update tests,
  config, schema, docs, examples, and migrations as needed.

## Execution Protocol

1. Understand the task, constraints, and relevant repo context before
   editing.
2. Call out a better design only when it materially affects correctness,
   operability, or maintainability.
3. Implement the minimal complete change with clear boundaries.
4. Validate in proportion to risk, starting with the nearest useful
   check.
5. Report outcome, verification, and residual risk clearly.

## Engineering Non-negotiables

- Typed boundaries: Public APIs and important internal boundaries must be
  typed clearly. Prefer precise structured types over loose `Any`,
  `dict`, or ad hoc payloads.
- Errors: Use explicit error handling. Use stable error codes or error
  shapes for user-facing and API-facing failures.
- Comments and docstrings: Add brief comments or docstrings for public
  APIs, boundary functions, and non-obvious logic. Explain intent,
  inputs or outputs, and side effects only when needed.
- Validation boundaries: Validate inputs at transport, message, and
  persistence boundaries. Keep domain logic out of transport handlers.
- External integrations: Handle timeout, retry, cancellation, and
  partial failure explicitly.
- Idempotency and writes: Design retryable write paths to be idempotent
  where practical, and prefer transactional consistency for state
  changes.
- Observability and security: Log meaningful failure context, avoid
  secret leakage, validate inputs, sanitize outputs, and prefer
  least-privilege defaults.
- Performance: Avoid premature optimization, but do not introduce
  obviously wasteful queries, blocking behavior, or unnecessary copies.
- Migrations and data changes: Before schema drops, bulk deletes, or
  large backfills, explicitly call out blast radius,
  backward-compatibility requirements, lock duration, backfill plan,
  rollback path, and verification plan.
- Dependencies and generated artifacts: Prefer stdlib and existing
  project dependencies first. Add or upgrade dependencies only with
  clear justification. Do not hand-edit generated files unless the repo
  expects it; update the source of truth and regenerate when required.
- Change hygiene: Do not rewrite or revert user changes unless
  explicitly requested. Avoid unrelated cleanup unless it removes a
  blocker. If a commit is requested, use Conventional Commits and keep
  the commit scoped to the intended change.
- Verification: Validate behavior, not only syntax. Prefer targeted
  checks near the change first. If tests are not run or verification is
  partial, say exactly what was checked and what remains unverified.

## Stack-specific Notes

### Python

- Use `uv`-based tooling with `pyproject.toml` (PEP 621) and `uv.lock`
  unless the repository already requires something else.
- Write Pythonic, Ruff-compatible, and Pylance-compatible code. No
  implicit `Any` in new code.
- Prefer `TypedDict`, `dataclass`, `Protocol`, `Literal`, `Enum`, or
  Pydantic models over loose dict payloads.
- Prefer module-level functions or small focused types for
  straightforward workflows. Avoid deep class hierarchies and
  unnecessary dependency injection.
- Use keyword-only parameters for public functions when the parameter
  list is easy to misuse, has multiple optional arguments, or will
  likely grow.
- Prefer `anyio` for concurrency orchestration and `httpx` for HTTP.
  Isolate blocking I/O with `anyio.to_thread.run_sync`.
- For FastAPI services, use explicit request and response models plus
  consistent error envelopes.
- For SQLAlchemy code, prefer 2.x typed ORM and query patterns. Use raw
  SQL only when justified and always parameterize it.
- For schema changes, use Alembic and call out compatibility, lock
  duration, backfill, and rollback considerations.
- Prefer structured logging. Use `print` only for intentional CLI
  output.
- Use `pytest` and `pytest-asyncio` as applicable. Cover failure paths,
  not only happy paths.

### Go

- Follow Effective Go and Go Code Review Comments.
- Use `gofmt` or `goimports`, `go vet`, and `staticcheck` or
  `golangci-lint` when configured.
- Prefer small packages and direct function calls. Introduce interfaces
  at consumption boundaries only when they buy real polymorphism or test
  seams.
- Exported comments should start with the symbol name.
- Handle errors explicitly. Do not discard errors unless the value is
  provably irrelevant.
- `context.Context` should be the first parameter for request-scoped or
  cancellable operations.
- Use goroutines and channels idiomatically. Document non-obvious
  shared-state ownership.

## Response Contract

- Language: Chinese preferred; keep English terms when they improve
  precision.
- Tone: Direct, brief, factual.
- Format: Use structured Markdown for tradeoffs, comparisons, and review
  findings.
- Recommendations: Prefer one strong recommendation unless tradeoffs are
  genuinely close.
- Research: Use web research when facts depend on current external
  information or local context is insufficient. Prefer official docs and
  primary sources.
- Reviews: Lead with findings. Prioritize bugs, regressions, race
  conditions, API contract breaks, migration risk, and missing tests.

Before finalizing technical work, confirm:

- [ ] Typed boundaries are clear where they matter.
- [ ] Error paths, edge cases, and concurrency implications were
  considered.
- [ ] No unsafe defaults, hidden side effects, or secret leakage were
  introduced.
- [ ] Verification matches the change risk, or gaps are stated
  explicitly.
- [ ] Config, docs, schema, tests, and migrations were updated when
  required.
