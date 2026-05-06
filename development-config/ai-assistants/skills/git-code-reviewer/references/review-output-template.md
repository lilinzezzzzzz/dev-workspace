# Review Output Template

Use this as the default output shape. Remove sections that are truly irrelevant, but keep findings first.

## Findings

List only concrete, actionable findings. Order by severity, then by impact.

Example:

1. `[high]` Missing idempotency guard on retry path
   Evidence: `service/payment.py:87` retries after timeout, but `create_charge()` persists before the timeout can be observed by the caller.
   Impact: A client retry can create duplicate charges.
   Recommendation: Add an idempotency key or move persistence behind a deduplicated boundary.

2. `[medium]` Validation no longer rejects empty tenant ids
   Evidence: `api/request_models.py:24` changed `min_length=1` to an unconstrained `str`.
   Impact: The handler now accepts invalid requests and pushes failure deeper into the service layer.
   Recommendation: Restore boundary validation and keep the failure at the API edge.

Preferred per-finding structure:

- `Evidence`: Confirmed facts from code, config, tests, schema, or command output you actually inspected.
- `Impact`: The direct consequence that follows from the evidence.
- `Recommendation`: The smallest reasonable correction or follow-up.
- `Confidence`: Optional. Prefer `confirmed`, `probable`, or `question`.
- `Counterexample`: Optional. A concrete failure scenario that makes the risk obvious, especially for races, retries, rollout, or stateful consistency issues.
- `Unverified assumption`: Optional. Include only when part of the impact depends on behavior you did not verify.

## Scope

Use this section in every review. Keep it brief, but make the reviewed boundary unambiguous.

Example:

- Review scope: `origin/main...HEAD`
- User-specified base: `main`
- Base ref type: `remote-tracking`
- Fetch: `executed`
- Base commit: `<sha>`
- Included: tracked staged and unstaged changes
- Excluded: untracked files

When the user provides an explicit PR, MR, commit range, or patch artifact, state that exact artifact together with the user-specified base. Do not invent or replace the base ref.

## Verification

Use this section in every review when commands, tests, lint, type checks, schema checks, or runtime probes were run or intentionally skipped.

Example:

- Ran: `pytest tests/test_payment_retry.py -q` passed
- Not run: broader test suite, not needed for this focused retry-path review
- Blocked: none

## Open Questions / Assumptions

Use this section for concerns that are plausible but not fully verified.

Example:

- I did not verify whether `user.is_admin` is normalized by middleware before this handler runs. If not, the new branch may allow a false-negative authorization result.

## Summary

Keep this short. Mention one of:

- `发现 X 个需要修复的问题，主要集中在 ...`
- `未发现明确缺陷；剩余风险在于 ...`
- `结论受限于 ...，以下分支未验证 ...`

## Output Rules

- Findings must be specific enough that the author can act without re-reading the whole diff.
- Keep confirmed facts separate from unverified assumptions. Do not present a hypothesis as a confirmed defect.
- Prefer one finding per root cause. If multiple symptoms share one defect, combine them and explain the blast radius in `Impact`.
- Explain why the issue matters, not just what changed.
- Prefer file and line references over vague location hints.
- Always state the reviewed scope. When review scope depends on a user-specified and resolved base ref, state the user-specified base, the exact ref used, and whether it was remote-tracking or local. For remote-tracking bases, follow the shared remote-base reporting rule: fetch executed with base commit SHA, or explicit downgrade with local cached freshness warning.
- Always state what verification was run. If no commands were run, say so and explain whether the review was limited to static inspection.
- Do not bury the main issue inside long prose.
- If there are no findings, say so explicitly instead of padding with praise.
