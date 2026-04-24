# LLM and RAG Review Checklist

Use only the sections relevant to the change. This is a thinking aid for Python backend changes that touch LLM calls, prompts, tools, retrieval, vector indexes, embeddings, reranking, streaming, agent workflows, or AI evaluation paths.

## 1. Prompt, Tool, and Message Contracts

- Did system, developer, user, or tool-message structure change in a way that breaks stored conversations, retries, or downstream parsers?
- Did function or tool schemas change, including required fields, enum values, default behavior, or strictness?
- Can old and new producers and consumers coexist during rollout when tool payloads, event payloads, or message schemas change?
- Are prompt templates, rendered variables, and fallback branches validated before they reach the model call?
- Does the code distinguish omitted values, explicit `null`, empty strings, and default values where the model or parser behavior differs?

## 2. Retrieval Scope and Source Quality

- Did query construction, filters, top-k, score thresholds, deduplication, or ordering semantics change?
- Does reranking, hybrid search, query expansion, or post-filtering preserve the intended retrieval scope and ranking behavior?
- Could stale, deleted, duplicate, wrong-version, or irrelevant chunks enter the prompt, response, log, trace, or evaluation artifact?
- If metadata filters are optional or fallback-based, can a failed filter silently broaden the search scope beyond the intended corpus?
- Are citations, source ids, and chunk metadata still consistent with the retrieved text that influenced the answer?

## 3. Embeddings, Vector Indexes, and Derived State

- Did embedding model, dimension, normalization, distance metric, chunking, metadata schema, or index naming change?
- Can old and new embeddings coexist safely, or is a versioned index, backfill, or reindex required?
- Are create, update, delete, expire, retry, replay, and rollback paths symmetric across authoritative documents and vector or search indexes?
- Is the reindex or backfill idempotent, resumable, and bounded for large corpora?
- Can stale vectors, orphan chunks, or partially indexed documents be detected and repaired?

## 4. Streaming, Cancellation, and Partial Output

- If responses stream, what happens when the client disconnects, the request is cancelled, or the model call times out?
- Can partial output be persisted, billed, emitted to callbacks, or shown to users in an inconsistent state?
- Are background continuations, retries, callbacks, and webhook deliveries idempotent after a timeout or partial success?
- Does the code preserve ordering and final-state transitions for streamed chunks, tool calls, and completion events?

## 5. External Model Calls and Runtime Controls

- Are timeout, retry, rate-limit, circuit-breaker, and cancellation semantics explicit for model, embedding, reranking, or moderation calls?
- Could retry behavior duplicate tool side effects, chargeable calls, messages, or stored outputs?
- Did model name, provider, endpoint, API version, region, or runtime default change, and are settings and deployment defaults updated together?
- Are cost, token budget, max output, context length, batching, and concurrency limits bounded on request or worker hot paths?
- Is fallback behavior explicit, bounded, and safe for the caller-visible contract?

## 6. Safety, Privacy, and Observability

- Are raw prompts, user content, retrieved documents, secrets, tool outputs, or PII exposed in logs, traces, metrics, errors, or test fixtures?
- Could prompt injection or untrusted retrieved content control tool calls, URLs, file paths, SQL, shell commands, or privileged actions?
- Are moderation, policy, or privacy checks still applied at the right boundary when prompts, retrieval, or streaming paths move?
- Do audit records contain enough context to diagnose failures without leaking sensitive content?

## 7. Evaluation and Regression Coverage

- Are there targeted tests or eval cases for changed prompt rendering, tool schema parsing, retrieval filters, streaming state transitions, and fallback behavior?
- If embedding or retrieval ranking changed, is there a practical regression signal for recall, source quality, and stale-index behavior?
- If no eval or targeted test was run, state which behavior remains unverified instead of treating model behavior as deterministic.
