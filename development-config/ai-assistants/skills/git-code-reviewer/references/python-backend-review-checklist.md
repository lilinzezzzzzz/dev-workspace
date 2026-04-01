# Python Backend Review Checklist

Use only the sections relevant to the change. This is a thinking aid for Python services and workers, not a template to dump verbatim.

## 1. API Boundary and Validation

- Did request parsing, validation, or coercion semantics change for FastAPI, Starlette, Pydantic, dataclass, or custom transport models?
- Did the change alter omitted-vs-`null`, default, alias, enum, or serialization behavior in a way that breaks existing clients or stored payloads?
- Are status codes, error envelopes, exception handlers, or response models still aligned with the API contract?
- Does the handler now return ORM objects, lazy fields, or partially shaped dicts that may fail serialization or trigger late database access?

## 2. Dependency Injection, Auth, and Tenant Context

- Did dependency wiring, middleware ordering, or request-scoped objects such as auth context, tenant context, DB session, or trace context change?
- Are authn and authz checks preserved on every sensitive path, including background or internal helper paths?
- Could tenant filters, soft-delete filters, or row-level access checks be bypassed by moved or shared query code?

## 3. Service Logic and Error Contracts

- Are domain errors mapped to stable API-facing or job-facing error shapes instead of leaking raw exceptions?
- Do retries, partial failures, or fallback branches change state transitions or produce duplicate side effects?
- Does the change move validation or normalization deeper into the stack and make failures harder to classify or recover from?

## 4. SQLAlchemy, Transactions, and Persistence

- Is the session lifecycle clear, including commit, rollback, flush, and close boundaries?
- Could the change introduce read-modify-write races, duplicate inserts, missing uniqueness checks, or non-idempotent writes under retry?
- Does lazy loading, eager loading, relationship traversal, or serialization create N+1 queries or `DetachedInstanceError`-style failures?
- Are tenant predicates, soft-delete predicates, and pagination or ordering semantics preserved?

## 5. Migrations and Data Changes

- Is the Alembic migration safe for mixed-version rollout, or does it require an explicit expand-contract sequence?
- Do nullability changes, column drops, renames, backfills, or default changes have a rollback path and bounded lock duration?
- If data is rewritten, is the backfill idempotent, resumable, and safe under partial failure?
- Were application code, migration scripts, and tests updated together when the persisted schema or enum set changed?

## 6. Async, Background Jobs, and External I/O

- Does async code accidentally call blocking I/O such as sync DB access, filesystem work, or network clients on the event loop?
- Are timeout, retry, cancellation, and deadline semantics explicit for `httpx`, message queues, LLM calls, storage SDKs, or other external dependencies?
- Could a background task or worker run after the request fails or times out and leave the system in an inconsistent state?
- For Celery, RQ, Dramatiq, Arq, or framework-native background tasks, are retries, acknowledgements, duplicate delivery, and task ordering safe for the underlying writes and side effects?
- Are queues, tasks, and scheduled jobs idempotent and deduplicated where retries or duplicate delivery are possible?

## 7. Configuration, Settings, and Runtime Safety

- Did environment-variable parsing, feature flags, defaults, or settings precedence change?
- Could a configuration typo now fail open instead of fail closed?
- Are secrets, tokens, raw prompts, tenant identifiers, or user content exposed in logs, metrics, traces, or exceptions?

## 8. Python-Specific Security Pitfalls

- Does the change introduce unsafe deserialization such as `pickle`, `yaml.load`, or untrusted model loading?
- Are `subprocess`, file paths, URLs, templates, or dynamic imports built from untrusted input without validation?
- Could the new code allow SSRF, path traversal, command injection, template injection, or prompt leakage across trust boundaries?

## 9. Typing and Interface Precision

- Did the change make function signatures, request models, repository interfaces, or settings objects less precise in a way that hides real `None` or shape errors?
- Could the implementation now violate declared types, for example returning `None` where the annotation promises a value, widening to loose dict payloads, or breaking `TypedDict`, Pydantic, or protocol expectations?
- If the repository uses `mypy`, `pyright`, or Pylance-strict conventions, would the changed code still satisfy the intended type boundary rather than merely passing at runtime?

## 10. Tests and Verification

- Do tests cover the changed request or response contract, not just internal helpers?
- Is there a failure-path test for validation, authz, external timeouts, partial writes, or duplicate delivery where relevant?
- If persistence behavior changed, is there at least one integration-style verification of transaction boundaries, rollback, or migration compatibility?
- If type-sensitive code changed, is there a targeted type-checking signal or an explicit statement that type compatibility remains unverified?
- If no targeted validation was run, is the review output explicit about what remains unverified?

## 11. Python Severity Examples

- `critical`: auth bypass in a FastAPI dependency, tenant filter dropped from a SQLAlchemy query, irreversible Alembic data loss, or unsafe deserialization of untrusted input.
- `high`: response model or exception mapping break that changes API contract, duplicate side effects in a Celery retry path, blocking sync I/O added on an async request path, or migration rollout that is unsafe for mixed versions.
- `medium`: missing boundary validation, incomplete timeout or retry handling for `httpx` or storage calls, meaningful N+1 risk, or missing regression coverage on a changed failure path.
- `low`: maintainability issue likely to cause future backend defects, such as type precision loss or confusing persistence wiring that has not yet caused incorrect behavior.
