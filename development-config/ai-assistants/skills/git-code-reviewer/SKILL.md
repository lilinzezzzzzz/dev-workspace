---
name: git-code-reviewer
description: Review PRs, MRs, commits, diffs, or workspace changes for Python backend services. Requires an explicit base branch before proceeding. Use for code review, CR, PR/MR review, 风险审查, 代码审查, 找风险, 审核实现. Focus on bugs, regressions, contract breaks, data risks, concurrency, security, performance, and meaningful test gaps.
---

# Code Review

Turn a change set into high-signal review findings. Prioritize correctness, regressions, and operational risk over style.

## Core Rules

1. **Base branch gate**: Require an explicit base branch or base ref before doing anything. If missing, ask `基础分支是什么？` and stop. Do not infer from PR metadata, repo defaults, or local context.
2. When base is provided, visibly show it (e.g. `基础分支：dev`) before any further action.
3. Review the actual change set and runtime path, not author intent alone.
4. Base findings on concrete evidence: code, config, tests, schema, or runtime wiring.
5. Review changed code first; read surrounding context only when needed to validate behavior.
6. Trace changes across request boundary, service logic, persistence, async/background, external calls, and config surfaces when relevant.
7. For derived state (persisted, cached, indexed), identify authoritative state, sync path, and cleanup path before judging.
8. One finding per root cause. Fold downstream symptoms unless remediation meaningfully differs.
9. Report missing tests standalone only when the gap hides a concrete risk (contract break, migration, security, concurrency). Otherwise fold into root-cause finding or mention as residual risk.
10. Low-severity maintainability findings only when on the changed path and materially increasing future defect risk.
11. Use validation to narrow concerns when cheap and high-signal. Never claim verification not run.
12. Do not spend budget on style-only or speculative issues.
13. Report findings by default; only patch code when explicitly asked.

## Workflow

### 1. Define Scope

- Use user-provided PR, MR, commit range, or diff as scope. For workspace reviews, use tracked staged+unstaged changes by default.
- Load and follow [../_shared/git-remote-base-resolution.md](../_shared/git-remote-base-resolution.md) for base resolution.
- Default remote: `origin`. If absent and one remote exists, use it. Multiple non-origin remotes → ask.
- Local base ref only when user explicitly requests it or provides `refs/heads/...`.
- State exact scope (e.g. `origin/dev...HEAD`) with base freshness details.

### 2. Understand Before Judging

- Read diff summary → identify changed behavior, boundaries crossed, failure modes.
- For stateful changes: name authoritative state, derived state, sync/cleanup paths, compatibility surfaces.
- For Redis/cache: reason about cost at plausible cardinalities; distinguish point lookups vs full scans.
- For API changes: trace request model → handler → service → persistence → response/error mapping.
- Read callers, callees, and nearest tests for changed shared utilities before concluding safety.
- Search for analogous patterns when code follows or replaces an existing pattern.

### 3. Review by Risk Surface

- Load [references/review-risk-checklist.md](./references/review-risk-checklist.md) always.
- Conditionally load based on change content:
  - Python backend (.py, FastAPI, Pydantic, SQLAlchemy, Alembic, workers) → [references/python-backend-review-checklist.md](./references/python-backend-review-checklist.md)
  - Stateful (persistence, caches, indexes, status transitions, workflows) → [references/stateful-systems-review-checklist.md](./references/stateful-systems-review-checklist.md)
  - Redis/cache (key-value, session indexes, message history) → [references/redis-cache-review-checklist.md](./references/redis-cache-review-checklist.md)
  - LLM/RAG (prompts, tool schemas, retrieval, embeddings, streaming, agents) → [references/llm-rag-review-checklist.md](./references/llm-rag-review-checklist.md)
- Use only relevant sections. Prioritize failure-prone surfaces first.
- Final pass: check for dead params, unreachable branches, obsolete wrappers on changed path.

### 4. Validate Findings

- Classify evidence: `事实` / `推断` / `未验证`.
- Evidence priority: diff > implementation > tests > schema/config > docs > inference.
- For high-risk stateful changes: run ≥2 counterexample passes (partial retry, race, mixed-version rollout, replay after cleanup).
- Run cheap validation (pytest, linter, type-check) when it materially clarifies risk. Report what ran and what was skipped.
- Unverified concerns → present as questions or residual risk, not confirmed defects.

### 5. Output

- Use [references/review-output-template.md](./references/review-output-template.md) as response shape.
- Findings first, ordered by severity. Each includes: impact, evidence, suggested fix.
- Include file refs + line numbers. Include review scope and verification summary.
- No findings → state explicitly with verification gaps and residual risk.
- For Redis/stateful no-finding results: state what was checked (cardinality, atomicity, lifecycle edges).

## Severity Model

| Level | Scope |
|-------|-------|
| `critical` | Security breach, auth bypass, data loss/corruption, irreversible migration failure, outage |
| `high` | User-visible bug, contract break, race condition, bad rollback, major failure-path gap |
| `medium` | Missing validation, error handling gap, performance regression, observability gap, test gap hiding concrete risk |
| `low` | Changed-path maintainability issue that obscures semantics or increases future defect risk |

Severity reflects user impact, not stylistic preference.

## Scope Guidance

- Generated files, vendored code, lockfiles → secondary evidence unless change targets contract surfaces.
- Follow unchanged code when claims depend on shared helpers, middleware, migrations, or config.
- Dependency bumps: check compatibility, transitive risk, runtime defaults, packaging impact.
- Migrations/infra: rollout safety, backward compat, lock duration, rollback path.
- Stateful: lifecycle symmetry (create/update/delete/expire/retry/replay/rollback), mixed-version rollout.
- Async/concurrent: idempotency, cancellation, retries, locking, ordering, shared-state ownership.
- Redis/cache: cardinality, query shape, point vs full fetch, atomicity assumptions.
- Security: trust boundaries, authn/authz, input validation, secrets, injection, SSRF.
- LLM/RAG: prompt/tool compat, retrieval quality, vector index lifecycle, streaming, cost, data leakage.
- PR/MR platform: description/title/comments are context only; base findings on diff and runtime code.
