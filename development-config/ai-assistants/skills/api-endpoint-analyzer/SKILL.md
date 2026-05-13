---
name: api-endpoint-analyzer
description: 分析 HTTP、REST、RPC 或 webhook API 端点的定义、实现和行为。当用户要求解释某个接口、梳理 endpoint 契约、逆向分析请求和响应结构、输出业务流程图、整理错误处理逻辑、核对 OpenAPI/Swagger 与代码实现是否一致、评审接口设计或排查接口行为时使用此 skill。
---

# API Endpoint Analyzer

## Purpose

Turn scattered endpoint artifacts into a concise, evidence-backed analysis of request contract, response contract, execution flow, side effects, and error behavior. Prefer runnable code and generated contracts over comments or prose docs. Separate verified facts from inference.

This is an analysis skill by default: read and explain. Do not edit code, schemas, tests, or docs unless the user explicitly asks for changes.

## Analysis Depth

- If the user asks for a quick explanation, provide a compact summary with request, response, main flow, and notable errors.
- If the user asks for a full analysis, compatibility check, OpenAPI comparison, review, or troubleshooting, use the full template in [references/endpoint-analysis-template.md](./references/endpoint-analysis-template.md).
- If artifacts are incomplete or the call path is unclear, use [references/source-tracing-checklist.md](./references/source-tracing-checklist.md).
- If only docs/specs are available, analyze the declared contract and mark implementation behavior as `未验证`.

## Workflow

1. Locate the endpoint entry.
   - Search by path, method, route name, operation id, handler name, RPC method, or webhook topic.
   - Confirm versioned routers, decorators, generated routes, middleware, and mounted prefixes before naming the final endpoint.

2. Establish the contract.
   - Record method/path, content type, auth, permissions, idempotency, sync/async behavior, pagination, streaming, uploads/downloads, and version constraints.
   - Extract explicit inputs from path, query, headers, cookies, body, form/multipart fields, and files.
   - Identify implicit inputs from auth context, tenant context, dependency injection, middleware, feature flags, environment defaults, and server-generated values.

3. Trace the implementation.
   - Follow router -> handler/controller -> service/use case -> domain logic -> repository/gateway/external clients.
   - Capture validation, authorization, branching, transactions, retries, fallbacks, state transitions, side effects, async jobs, events, and cache behavior.
   - Note consistency semantics: immediate write/read, eventual consistency, compensation, timeout, cancellation, and partial failure behavior.

4. Reconstruct outputs.
   - Enumerate success status codes, response schemas, conditional fields, wrappers, headers, cookies, pagination metadata, redirects, files, or stream events.
   - Enumerate reachable failures: validation, auth, permission, not found, conflict, rate limit, dependency failure, timeout, cancellation, and framework defaults.
   - Distinguish documented errors from implementation-reachable errors.

5. Report with evidence.
   - Include local file/function references when code is available.
   - Mark unverified conclusions as `推断` or `未验证`.
   - If docs/specs and code disagree, report both and identify the likely source of truth.

## Evidence Order

Use this priority order when sources disagree:

1. Runtime route configuration and handler code
2. Request and response schema definitions
3. Service, domain, repository, and integration code
4. Automated tests and fixtures
5. OpenAPI, Swagger, protobuf, or other generated specs
6. Comments, README files, and issue discussions
7. Inference from framework conventions

## Output Rules

- Match the output depth to the user's request; do not force the full template for a small question.
- Keep facts, inference, and open questions separate.
- Prefer tables for parameter and error enumeration.
- Include Mermaid only when explaining a non-trivial flow; keep diagrams focused on business branches, not framework boilerplate.
- Always call out auth, idempotency, side effects, external dependencies, persistence changes, and cache behavior when present.
- For mutating endpoints, state what is written, emitted, queued, invalidated, or called externally.
- For multi-backend reads, state consistency expectations and failure propagation.
- Do not invent field types, status codes, validation rules, side effects, or security behavior.
- Avoid generic advice unless tied to evidence from the endpoint.

## Special Cases

### OpenAPI or Swagger only

- Analyze the declared contract.
- Call out that implementation paths, hidden side effects, and real exception branches are not verified.

### File upload or multipart endpoints

- Record content type, file field names, size and type validation, storage destination, and cleanup behavior.

### Streaming, SSE, websocket, or async-job endpoints

- Explain connection lifecycle, event payload shape, completion semantics, retry behavior, and timeout or cancellation handling.

### Webhooks

- Explain signature verification, replay protection, idempotency strategy, downstream fan-out, and failure acknowledgement semantics.

### RPC or protobuf APIs

- Identify service/method, request and response messages, field presence/default semantics, metadata, auth interceptors, deadlines, streaming mode, and mapped error codes.

### API reviews

- Lead with concrete findings: contract breaks, auth or tenant gaps, unsafe side effects, data consistency risks, missing error mapping, N+1/unbounded reads, and meaningful test gaps.
- Separate design suggestions from correctness issues.

## References

- Read [references/endpoint-analysis-template.md](./references/endpoint-analysis-template.md) for the default report structure and Mermaid example.
- Read [references/source-tracing-checklist.md](./references/source-tracing-checklist.md) when artifacts are incomplete or the endpoint spans middleware, services, and external systems.
