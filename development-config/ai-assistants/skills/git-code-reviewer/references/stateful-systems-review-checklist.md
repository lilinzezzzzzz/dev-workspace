# Stateful Systems Review Checklist

Use only the sections relevant to the change. This is a thinking aid for changes that touch persisted state, caches, indexes, denormalized data, status transitions, repair jobs, or other multi-step workflows.

## 1. State Model

- What is the authoritative state for the behavior under review?
- What derived or secondary state exists, such as caches, indexes, counters, denormalized rows, search documents, or status fields?
- Which operations create, refresh, delete, expire, or repair each derived artifact?
- Can the derived state be reconstructed safely from the authoritative source if it becomes stale or missing?

## 2. Lifecycle Symmetry

- When the main entity is created, updated, deleted, expired, retried, replayed, or rolled back, do all secondary states stay consistent?
- Are failure and partial-success paths symmetric with the happy path, or can one side effect succeed while another is skipped?
- Does lazy cleanup merely defer work, or can it hide a correctness problem until scale or concurrency makes it visible?

## 3. Counterexamples

- Counterexample: the authoritative write succeeds, but the index or cache update fails. What stale state remains and who repairs it?
- Counterexample: a read races with delete, expiry, or recreation. What can the caller observe?
- Counterexample: old and new versions run together during rollout. Can producers and consumers interoperate safely?
- Counterexample: a retry or replay happens after partial success. Can the operation duplicate work, regress state, or mask data loss?

Choose at least two concrete counterexamples for high-risk stateful changes, even if no code is executed.

## 4. Compatibility and Rollout

- Does the change affect public API, persisted format, message schema, or cross-service contract?
- Can old and new readers and writers coexist during mixed-version rollout?
- Is rollback safe, or does the new state become unreadable, unrepairable, or semantically ambiguous to older code?

## 5. Evidence and Coverage

- Did you read the immediate callers, immediate callees, and nearest tests for the changed helper or workflow?
- Is there an analogous implementation or older pattern elsewhere in the repository, and if so, does this change intentionally diverge from it?
- If no targeted validation was run, which invariants, counterexamples, or lifecycle edges remain unverified?
