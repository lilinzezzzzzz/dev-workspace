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
- Explain why the issue matters, not just what changed.
- Prefer file and line references over vague location hints.
- Do not bury the main issue inside long prose.
- If there are no findings, say so explicitly instead of padding with praise.
