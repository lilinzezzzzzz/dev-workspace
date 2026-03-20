---
name: code-reviewer
description: 审查 PR、MR、commit、diff 或工作区改动，识别 bug、回归、API 契约破坏、数据与迁移风险、并发问题、安全漏洞、性能退化和测试缺口。当用户要求 review、CR、PR review、MR review、代码审查、找风险、审核实现或判断改动是否可合入时使用此 skill。
---

# Code Review

Use this skill to turn a change set into a small number of high-signal review findings. Prioritize correctness, regressions, and operational risk over style.

## Core Rules

1. Review the actual change set, not the author's intent alone.
2. Base every finding on concrete evidence from code, config, tests, schema, or runtime wiring.
3. Prefer changed-code review first; read surrounding context only when needed to validate behavior.
4. Focus on issues that matter: correctness, contracts, data safety, concurrency, security, performance, observability, and test adequacy.
5. Do not spend review budget on style-only or speculative issues unless repository policy makes them blocking.
6. By default, report findings instead of fixing code. Only patch code when the user explicitly asks for fixes.

## Workflow

1. Define review scope.
   - If the user provides a PR, MR, commit range, or diff, use that as the scope.
   - Otherwise infer a reasonable base branch and review the diff from that base to `HEAD`.
   - If the base is ambiguous and correctness depends on it, state the assumption or ask.

2. Understand the change before judging it.
   - Read the diff summary first.
   - Identify the behavior that changed, the boundaries crossed, and the likely failure modes.
   - Pull in tests, config, migrations, schemas, generated artifacts, and nearby implementation only when they affect the conclusion.

3. Review by risk surface, not by file order.
   - Load [references/review-risk-checklist.md](./references/review-risk-checklist.md).
   - Use only the sections relevant to the changed behavior.
   - For large changes, prioritize the most failure-prone surfaces first.

4. Validate findings.
   - Separate `事实`, `推断`, and `未验证`.
   - Prefer evidence order: diff, implementation, tests, schema/config/migrations, docs/comments, inference.
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
- Follow unchanged code when a claim depends on shared helpers, framework hooks, middleware, serializers, migrations, or config.
- For dependency bumps, check compatibility, transitive risk, runtime defaults, and required follow-up changes.
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
