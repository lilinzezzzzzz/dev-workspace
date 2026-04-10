# Redis and Cache Review Checklist

Use only the sections relevant to the change. This is a thinking aid for Redis and cache-backed persistence, not a template to dump verbatim.

## 1. Cardinality and Query Shape

- Does the changed path call `SMEMBERS`, `HGETALL`, `ZRANGE` or `ZREVRANGE` with an unbounded end, `LRANGE 0 -1`, `SCAN`, or a wrapper that hides the same behavior?
- If the caller needs only one member, one page, or a count, does the implementation still fetch the entire collection first?
- Does the code materialize a large ID list in application memory and then issue per-ID probes such as `EXISTS`, `GET`, `LRANGE`, or deserialization work, creating linear fan-out on a request path?
- Does the code issue N pipelined commands where N grows with accumulated business data, such as one `EXISTS` per session? Pipelining reduces round trips but does not remove linear server, client, and payload cost.
- For sorted indexes, could `ZRANGE` windowing, `ZCARD`, `ZSCORE`, or a small Lua script avoid the full fetch?

## 2. Membership, Auth, and Precision

- If the code needs to answer “does this member belong to this org, device, tenant, or index”, does it use an exact membership operation such as `SISMEMBER`, `ZSCORE`, `HEXISTS`, or direct-key lookup instead of `members() + in` on the client side?
- Is the membership or authz decision checked against the authoritative structure, rather than against a derived list that may be stale, filtered, or expensive to compute?
- If the same index is used for both ordering and membership, does the chosen read pattern preserve both concerns without unnecessary collection fetches?

## 3. Atomicity and TOCTOU

- Does the change perform `EXISTS` and then `GET`, `LRANGE`, `DELETE`, `ZREM`, or another mutation in a later command, assuming the key cannot change in between?
- If a key can expire or be recreated between steps, is the resulting behavior benign and explicit, or does it create stale cleanup, wrong totals, or surprising empty reads?
- Should the sequence be combined into a transaction, Lua script, or single authoritative read instead of a separate pre-check?

## 4. Write Amplification and Hot Paths

- Does one logical user action perform repeated idempotent writes such as `ZADD`, `EXPIRE`, `SETEX`, or index refresh more than once per request or chat turn?
- Is the hot path paying the same serialization, network, or expiry-refresh cost twice when one call or deferred refresh would suffice?
- Under retries, streaming, or partial failures, does the new write pattern multiply Redis load or tail latency?
- Are cache or index keys and data keys expired with aligned TTLs, or can mismatched TTLs accumulate orphan entries and wasted follow-up probes?
- For sorted-set or secondary indexes, is lazy cleanup on read sufficient for the expected growth rate, or does the access pattern require a background purge strategy?

## 5. Tests and Validation

- Is there coverage for large-cardinality behavior or at least an explicit review note that it remains unverified?
- Are stale-index cleanup, disappearing-key races, and repeated registration or refresh behavior tested where they affect correctness or performance?
- If no targeted validation was run, does the review output say whether the risk is a confirmed defect, an inference, or a residual question?
