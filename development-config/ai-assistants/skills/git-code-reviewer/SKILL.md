---
name: git-code-reviewer
description: Review PRs, MRs, commits, diffs, or workspace changes for Python backend services. Use for code review, CR, PR review, MR review, 风险审查, 代码审查, 找风险, 审核实现, or 判断 Python 后端、API、worker、RAG 服务改动是否可合入. Focus on bugs, regressions, API contract breaks, FastAPI/Pydantic validation, SQLAlchemy/Alembic data risks, Redis/cache consistency, async/concurrency, LLM/RAG workflows, security, performance, and meaningful test gaps.
---

# Code Review

Use this skill to turn a change set into a small number of high-signal review findings. Prioritize correctness, regressions, and operational risk over style. Still report low-severity maintainability issues when they materially obscure behavior or leave misleading dead code on the changed path.

## Core Rules

1. Review the actual change set and its runtime path, not the author's intent alone.
2. Base every finding on concrete evidence from code, config, tests, schema, or runtime wiring.
3. Prefer changed-code review first; read surrounding context only when needed to validate behavior.
4. Trace changed behavior across request boundary, service logic, persistence, async or background execution, external calls, and rollout or config surfaces when relevant.
5. Focus on issues that matter: correctness, contracts, data safety, concurrency, security, performance, observability, and test adequacy.
6. When the change touches persisted, cached, indexed, or otherwise derived state, identify the authoritative state, the derived state, and the sync and cleanup paths before judging correctness.
7. Prefer reporting one finding per root cause. Fold downstream symptoms such as missing tests, tail-latency regressions, or stale cleanup effects into the same finding unless the remediation meaningfully differs.
8. Report missing tests as a standalone finding only when the gap hides a concrete changed risk, such as API contract breakage, state migration, security boundary, retry behavior, concurrency, or a regression-prone bug path. Otherwise mention test gaps as residual risk or fold them into the root-cause finding.
9. Include low-severity maintainability findings only when the issue is on the changed path and materially increases misuse or future defect risk, for example opaque positional tuples or flags that encode multiple semantics, dead parameters or branches, or wrappers whose behavior is no longer live.
10. Use validation to confirm or narrow ambiguous concerns when a nearby check is cheap and high-signal. Do not claim verification you did not run.
11. Do not spend review budget on style-only or speculative issues unless repository policy makes them blocking.
12. By default, report findings instead of fixing code. Only patch code when the user explicitly asks for fixes.

## Workflow

1. Define review scope.
   - If the user provides a PR, MR, commit range, or diff, use that as the scope.
   - If the user asks to review workspace changes without a narrower scope, review tracked staged and unstaged changes by default. Ignore untracked files unless the user includes them explicitly or the changed code depends on them.
   - If the user provides, or the workflow infers, a base branch or base ref, load and follow [../_shared/git-remote-base-resolution.md](../_shared/git-remote-base-resolution.md).
   - Use `origin` as the default remote when it exists. If `origin` is absent and exactly one remote exists, use that remote. If multiple non-`origin` remotes exist and correctness depends on the base, ask which remote to use.
   - Use a local base ref only when the user explicitly asks for local branch state or provides a full local ref such as `refs/heads/main`.
   - Otherwise infer the base in this order: PR or MR target branch if available; repository integration branch as a remote-tracking ref, preferring `origin/dev`, then `origin/main`, then `origin/master`; ask when multiple plausible bases remain.
   - State the exact scope used, for example `origin/dev...HEAD`, and include the base freshness details required by the shared remote-base rule.

2. Understand the change before judging it.
   - Read the diff summary first.
   - Identify the behavior that changed, the boundaries crossed, and the likely failure modes.
   - If the change affects persistence, caches, indexes, counters, status fields, or other derived state, explicitly name the authoritative state, the derived state, the sync path, the cleanup path, and the compatibility surfaces affected, such as public API, persisted format, message schema, or cross-service contract.
   - When the change introduces or modifies Redis, cache, or indexed key-value access, reason about the request-path cost at plausible cardinalities, not just the happy path for small `N`.
   - For collection-backed helpers, explicitly distinguish point lookups, page reads, counts, and full scans. Check whether the implementation fetches an entire collection when only one member, one page, or one existence check is needed.
   - For backend or API changes, trace the relevant path across request model, handler or router, service, repository or persistence layer, external calls or background jobs, and response or error mapping as needed.
   - Read the immediate callers, immediate callees, and nearest tests for changed helpers or shared utilities before concluding behavior is safe.
   - When the code follows or replaces an existing pattern, search the repository for at least one analogous implementation or test and note any intentional divergence.
   - Pull in config, migrations, schemas, generated artifacts, and nearby implementation only when they affect the conclusion.

3. Review by risk surface, not by file order.
   - Load [references/review-risk-checklist.md](./references/review-risk-checklist.md).
   - Before concluding there are no findings, do a short pass on the changed code for low-severity maintainability hazards that affect local reasoning, such as dead parameters, unreachable branches, obsolete wrappers, and opaque positional internal contracts.
   - If the change mainly touches Python backend code such as `.py` files, FastAPI or Starlette handlers, Pydantic models, SQLAlchemy ORM, Alembic migrations, Celery or worker code, settings, or API schemas, also load [references/python-backend-review-checklist.md](./references/python-backend-review-checklist.md).
   - If the change touches persisted state, caches, indexes, status transitions, denormalized data, background repair, or multi-step workflows, also load [references/stateful-systems-review-checklist.md](./references/stateful-systems-review-checklist.md).
   - If the change touches Redis, cache helpers, message history, session indexes, or other key-value persistence, also load [references/redis-cache-review-checklist.md](./references/redis-cache-review-checklist.md).
   - If the change touches LLM calls, prompts, tool/function schemas, retrieval, vector indexes, embeddings, reranking, streaming, agent workflows, or AI evaluation paths, also load [references/llm-rag-review-checklist.md](./references/llm-rag-review-checklist.md).
   - Use only the sections relevant to the changed behavior.
   - For large changes, prioritize the most failure-prone surfaces first.

4. Validate findings.
   - Separate `事实`, `推断`, and `未验证`.
   - Prefer evidence order: diff, implementation, tests, schema/config/migrations, docs/comments, inference.
   - For high-risk stateful changes, run at least two concrete counterexample passes, for example partial success then retry, read racing with delete or expiry, mixed-version rollout, or replay after cleanup, even if you do not execute code.
   - If a nearby validation step is cheap and materially clarifies a risk, run the smallest useful check, for example a targeted `pytest`, linter, type checker, schema diff, or migration inspection. Report exactly what was run, skipped, or blocked.
   - If a concern is plausible but not verified, present it as a question or residual risk, not as a confirmed defect.

5. Produce the review in a stable format.
   - Use [references/review-output-template.md](./references/review-output-template.md) as the default response shape.
   - Findings come first, ordered by severity.
   - If there are no concrete findings, say that explicitly and mention any verification gaps or residual risk.

## Severity Model

- `critical`: security breach, auth bypass, data loss/corruption, irreversible migration failure, or outage-class bug.
- `high`: user-visible bug, contract break, race condition, bad rollback story, or major failure-path gap.
- `medium`: missing validation, incomplete error handling, meaningful performance regression, observability gap, or missing regression coverage that hides a concrete changed risk.
- `low`: maintainability issue on the changed path that obscures semantics, leaves dead logic behind, or otherwise increases future defect risk.

Use severity for user impact, not for stylistic preference.

## Scope Guidance

- Treat generated files, snapshots, vendored code, and lockfiles as secondary evidence unless the change specifically targets them or changes API, SDK, OpenAPI, protobuf, message schema, or other generated contract surfaces.
- When reviewing workspace changes, state whether the scope included staged changes, unstaged changes, both, or an explicit diff artifact.
- Distinguish local branch refs from remote-tracking refs. `main` and `origin/main` may point to different commits; use the shared remote-base rule whenever review correctness depends on a base branch.
- Follow unchanged code when a claim depends on shared helpers, framework hooks, middleware, serializers, migrations, or config.
- For dependency bumps, especially changes to `pyproject.toml`, `uv.lock`, `requirements*.txt`, `poetry.lock`, or container images used by Python services, check compatibility, transitive risk, runtime defaults, packaging impact, and required follow-up changes.
- For migrations and infra changes, check rollout safety, backward compatibility, lock duration, defaults, and rollback path.
- For stateful changes, check lifecycle symmetry across create, update, delete, expire, retry, replay, and rollback paths. Mixed-version rollout and cleanup behavior matter as much as the happy path.
- For async or concurrent code, check idempotency, cancellation, retries, locking, ordering, and shared-state ownership.
- For Redis, cache, or key-value collection changes, inspect collection cardinality, query shape, point lookup vs full fetch, and whether multi-command sequences rely on atomicity they do not actually have.
- For security-sensitive code, check trust boundaries, authn/authz, input validation, secret handling, injection, SSRF, path traversal, and unsafe rendering as relevant.
- For LLM or RAG changes, check prompt and tool schema compatibility, retrieval scope and source quality, vector index lifecycle, streaming and cancellation semantics, model or embedding version changes, cost and rate-limit behavior, and leakage of user content or retrieved data.
- For PR or MR platform reviews, treat the description, title, comments, and commit messages as context only. Base findings on the diff, runtime code, tests, schemas, config, CI logs, or verified platform metadata.

## Output Rules

- Findings are the primary deliverable.
- Each finding should explain impact, evidence, and the smallest reasonable correction or follow-up.
- Include file references and line numbers when available.
- Include a concise review scope and verification summary, including the exact base ref when a base ref is used.
- Keep summary sections brief.
- Prefer one finding per root cause. If one defect causes multiple symptoms, combine them unless the fixes are meaningfully different.
- When Redis or cache-backed collections are part of the changed path and you report no findings, state whether cardinality, membership query shape, and atomicity or TOCTOU risk were checked or remain unverified.
- When a stateful path is part of the review, state which invariants, lifecycle edges, or counterexamples were checked if that context is needed to justify a no-finding result.
- Do not invent missing behavior. If something cannot be verified, say exactly what is missing.

## References

- Read [references/review-output-template.md](./references/review-output-template.md) for the default response shape.
- Read [references/review-risk-checklist.md](./references/review-risk-checklist.md) when the change spans multiple subsystems or when you need a risk-oriented review pass.
- Read [references/python-backend-review-checklist.md](./references/python-backend-review-checklist.md) when the change is centered on Python services, APIs, workers, persistence, or migrations.
- Read [references/stateful-systems-review-checklist.md](./references/stateful-systems-review-checklist.md) when the change touches persisted state, caches, indexes, denormalized data, status transitions, background repair, or multi-step workflows.
- Read [references/redis-cache-review-checklist.md](./references/redis-cache-review-checklist.md) when the change introduces or modifies Redis or cache-backed collections, indexes, or hot-path key-value access.
- Read [references/llm-rag-review-checklist.md](./references/llm-rag-review-checklist.md) when the change touches LLM calls, prompts, tool/function schemas, retrieval, vector indexes, embeddings, reranking, streaming, agent workflows, or AI evaluation paths.
