---
name: git-code-reviewer
description: 审查 PR、MR、commit、diff 或工作区改动，识别 Python 服务端与通用后端改动中的 bug、回归、API 契约破坏、FastAPI/Pydantic 边界验证缺失、SQLAlchemy/Alembic 数据与迁移风险、async 并发与阻塞 I/O、安全漏洞、性能退化和测试缺口。当用户要求 review、CR、PR review、MR review、代码审查、找风险、审核实现，或判断 Python、后端、API 服务改动是否可合入时使用此 skill。
---

# Code Review

Use this skill to turn a change set into a small number of high-signal review findings. Prioritize correctness, regressions, and operational risk over style.

## Core Rules

1. Review the actual change set and its runtime path, not the author's intent alone.
2. Base every finding on concrete evidence from code, config, tests, schema, or runtime wiring.
3. Prefer changed-code review first; read surrounding context only when needed to validate behavior.
4. Trace changed behavior across request boundary, service logic, persistence, async or background execution, external calls, and rollout or config surfaces when relevant.
5. Focus on issues that matter: correctness, contracts, data safety, concurrency, security, performance, observability, and test adequacy.
6. Use validation to confirm or narrow ambiguous concerns when a nearby check is cheap and high-signal. Do not claim verification you did not run.
7. Do not spend review budget on style-only or speculative issues unless repository policy makes them blocking.
8. By default, report findings instead of fixing code. Only patch code when the user explicitly asks for fixes.

## Workflow

1. Define review scope.
   - If the user provides a PR, MR, commit range, or diff, use that as the scope.
   - If the user asks to review workspace changes without a narrower scope, review tracked staged and unstaged changes by default. Ignore untracked files unless the user includes them explicitly or the changed code depends on them.
   - Otherwise infer a reasonable base branch and review the diff from that base to `HEAD`.
   - Resolve an unqualified base branch name such as `dev`, `main`, or `master` to the corresponding remote-tracking ref `<remote>/<branch>` by default.
   - Use a local base ref only when the user explicitly asks for local branch state or provides a full local ref such as `refs/heads/main`.
   - If the user wants review against the latest base branch, sync the remote-tracking ref first, for example `git fetch origin main`, then review against `origin/main`. Do not assume a local branch ref is current.
   - If the base is ambiguous and correctness depends on it, state the assumption or ask. Also state the exact ref used for review when it matters, whether it was a remote-tracking or local ref, and whether fetch was executed or skipped.

2. Understand the change before judging it.
   - Read the diff summary first.
   - Identify the behavior that changed, the boundaries crossed, and the likely failure modes.
   - For backend or API changes, trace the relevant path across request model, handler or router, service, repository or persistence layer, external calls or background jobs, and response or error mapping as needed.
   - Pull in tests, config, migrations, schemas, generated artifacts, and nearby implementation only when they affect the conclusion.

3. Review by risk surface, not by file order.
   - Load [references/review-risk-checklist.md](./references/review-risk-checklist.md).
   - If the change mainly touches Python backend code such as `.py` files, FastAPI or Starlette handlers, Pydantic models, SQLAlchemy ORM, Alembic migrations, Celery or worker code, settings, or API schemas, also load [references/python-backend-review-checklist.md](./references/python-backend-review-checklist.md).
   - Use only the sections relevant to the changed behavior.
   - For large changes, prioritize the most failure-prone surfaces first.

4. Validate findings.
   - Separate `事实`, `推断`, and `未验证`.
   - Prefer evidence order: diff, implementation, tests, schema/config/migrations, docs/comments, inference.
   - If a nearby validation step is cheap and materially clarifies a risk, run the smallest useful check, for example a targeted `pytest`, linter, type checker, schema diff, or migration inspection. Report exactly what was run, skipped, or blocked.
   - If a concern is plausible but not verified, present it as a question or residual risk, not as a confirmed defect.

5. Produce the review in a stable format.
   - Use [references/review-output-template.md](./references/review-output-template.md) as the default response shape.
   - Findings come first, ordered by severity.
   - If there are no concrete findings, say that explicitly and mention any verification gaps or residual risk.

## Severity Model

- `critical`: security breach, auth bypass, data loss/corruption, irreversible migration failure, or outage-class bug.
- `high`: user-visible bug, contract break, race condition, bad rollback story, or major failure-path gap.
- `medium`: missing validation, incomplete error handling, meaningful performance regression, observability gap, or missing regression test.
- `low`: maintainability issue likely to cause future defects.

Use severity for user impact, not for stylistic preference.

## Scope Guidance

- Treat generated files, snapshots, vendored code, and lockfiles as secondary evidence unless the change specifically targets them.
- When reviewing workspace changes, state whether the scope included staged changes, unstaged changes, both, or an explicit diff artifact.
- Distinguish local branch refs from remote-tracking refs. `main` and `origin/main` may point to different commits; if review correctness depends on the latest integration branch, prefer the fetched remote-tracking ref and say which ref was used.
- Follow unchanged code when a claim depends on shared helpers, framework hooks, middleware, serializers, migrations, or config.
- For dependency bumps, especially changes to `pyproject.toml`, `uv.lock`, `requirements*.txt`, `poetry.lock`, or container images used by Python services, check compatibility, transitive risk, runtime defaults, packaging impact, and required follow-up changes.
- For migrations and infra changes, check rollout safety, backward compatibility, lock duration, defaults, and rollback path.
- For async or concurrent code, check idempotency, cancellation, retries, locking, ordering, and shared-state ownership.
- For security-sensitive code, check trust boundaries, authn/authz, input validation, secret handling, injection, SSRF, path traversal, and unsafe rendering as relevant.

## Output Rules

- Findings are the primary deliverable.
- Each finding should explain impact, evidence, and the smallest reasonable correction or follow-up.
- Include file references and line numbers when available.
- Keep summary sections brief.
- Do not invent missing behavior. If something cannot be verified, say exactly what is missing.

## References

- Read [references/review-output-template.md](./references/review-output-template.md) for the default response shape.
- Read [references/review-risk-checklist.md](./references/review-risk-checklist.md) when the change spans multiple subsystems or when you need a risk-oriented review pass.
- Read [references/python-backend-review-checklist.md](./references/python-backend-review-checklist.md) when the change is centered on Python services, APIs, workers, persistence, or migrations.
