# Review Risk Checklist

Use only the sections relevant to the change. This is a thinking aid, not a template to dump verbatim.

## 0. Review Basis and Freshness

- What exact review scope am I using, for example `origin/main...HEAD` or a PR patch?
- If a base branch name was unqualified, was it resolved with the shared remote-base rule?
- Did I intentionally review against local branch state, and if so, is that called out explicitly?
- If a remote-tracking base was used, did fetch succeed and was the base commit SHA recorded, or did the user explicitly allow downgrade?

## 1. Correctness and Control Flow

- Does the new behavior actually match the intended behavior?
- Are all important branches covered, including failure paths and partial-success paths?
- Did the change alter defaults, fallbacks, or state transitions in a way that breaks existing callers?
- Are `None`, empty, falsy, sentinel, and omitted-value cases handled explicitly where needed?
- Did the change leave a parameter, branch, fallback, or wrapper behaviorally dead, or preserve logic that no longer influences runtime behavior?
- Does any tuple, list, dict, flag combination, or numeric priority now encode semantics so opaquely that the changed code is easy to misread or misuse?

## 2. API and Contract Compatibility

- Did request or response shape change?
- Did serialized fields, enum values, headers, status codes, or event payloads change?
- For service code, did request models, response models, exception mapping, middleware effects, or dependency wiring semantics change?
- Which compatibility surface changed: public API, persisted format, message schema, cross-service contract, or mixed-version rollout behavior?
- Can old and new readers, writers, producers, or consumers coexist safely during rollout and rollback?
- Does the change break backward compatibility for existing clients, workers, or stored data?
- If a contract changed intentionally, were dependent tests, docs, examples, and generated specs updated?

## 3. Data Safety and Migration Risk

- Does the change introduce destructive writes, data loss risk, or state corruption risk?
- If the change introduces or updates derived state such as caches, indexes, counters, status rows, or denormalized records, is the authoritative source explicit and are synchronization and cleanup paths complete?
- Are create, update, delete, expire, retry, replay, and rollback paths symmetric, or can one path leave stale or contradictory secondary state behind?
- Are migrations backward compatible during rollout?
- Is there a safe backfill story, lock-duration consideration, and rollback path?
- Could retries, partial failures, or duplicate delivery make writes non-idempotent?

## 4. Concurrency, Async, and Distributed Behavior

- Is shared state protected with a clear ownership or synchronization model?
- Are retries, cancellation, deadlines, and timeouts propagated correctly?
- Could work be duplicated, reordered, or applied after the caller times out?
- Does the change rely on eventual consistency without documenting or testing the gap?
- Does the code check key or row existence and then read, delete, or clean it up in a later operation, creating a TOCTOU window on mutable shared storage such as Redis?
- Can cleanup or eviction race with concurrent refresh or recreation of the same index entry?

## 5. Security and Trust Boundaries

- Are authn and authz checks preserved on every sensitive path?
- Is input validated at the boundary before reaching deeper layers?
- Could the change introduce injection, SSRF, path traversal, unsafe deserialization, XSS, or CSRF?
- Are secrets, tokens, tenant context, or sensitive fields exposed in logs or responses?

## 6. Performance and Resource Lifecycle

- Does the change introduce obvious `O(n^2)` work, N+1 queries, unbounded loops, or large unnecessary copies?
- Does the changed path fetch an entire Redis, cache, or key-value collection when only one member, one page, or a count is needed?
- Does it materialize all IDs and then issue per-ID probes such as `EXISTS`, `GET`, or `LRANGE`, creating linear command fan-out and memory growth on the request path?
- Is membership or authz implemented by fetching all members and using `in` locally instead of an exact server-side lookup such as `SISMEMBER`, `ZSCORE`, or `HEXISTS`?
- Are connections, files, streams, tasks, threads, or worker processes released correctly?
- Is blocking work accidentally executed on an async or latency-sensitive path?
- Does retry logic multiply load under failure?

## 7. Observability and Operability

- Are failures logged with enough context to debug, without leaking secrets?
- Are metrics, traces, audit records, or alerts affected?
- Did config defaults, feature flags, or rollout controls change?
- Will operators be able to detect and safely roll back a bad deployment?

## 8. Tests and Verification

- Do tests cover the changed behavior, not just adjacent code?
- Are failure paths, edge cases, and regression-prone branches exercised?
- If the change spans boundaries, is there at least one integration-style check where it matters?
- For shared helpers or stateful changes, were the immediate callers, immediate callees, and nearest tests inspected before concluding there are no defects?
- Was at least one concrete counterexample considered, such as retry after partial success, delete during read, mixed-version rollout, or replay of stale state?
- If tests were not updated, is the existing suite genuinely sufficient?

## 9. What Not to Report as Findings

- Pure style differences with no correctness, readability, or policy impact
- Readability nits that do not materially obscure semantics, hide dead behavior, or weaken a changed internal contract
- Multiple findings that are only different symptoms of the same root cause; combine them unless the remediations are meaningfully different
- Broad refactor suggestions unrelated to the changed risk surface
- Speculation without code evidence
- Issues outside the review scope unless the current change makes them worse or depends on them
