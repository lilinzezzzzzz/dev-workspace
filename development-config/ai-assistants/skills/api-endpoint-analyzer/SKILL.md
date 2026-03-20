---
name: api-endpoint-analyzer
description: 分析 HTTP、REST、RPC 或 webhook API 端点的定义、实现和行为。当用户要求解释某个接口、梳理 endpoint 契约、逆向分析请求和响应结构、输出业务流程图、整理错误处理逻辑、核对 OpenAPI/Swagger 与代码实现是否一致、评审接口设计或排查接口行为时使用此 skill。
---

# API Endpoint Analyzer

## Overview

Use this skill to turn scattered endpoint artifacts into a single, structured analysis. Prefer code and executable artifacts over comments, and clearly separate observed facts from inference.

## Workflow

1. Gather the minimum artifact set before concluding.
   - Prefer route registration, handler/controller, request model, response model, service/use case, repository or gateway calls, and relevant tests.
   - If the user only provides an endpoint path or method, locate the route definition first.
   - If the user only provides OpenAPI or Swagger artifacts, state that implementation is not verified.

2. Establish the endpoint contract.
   - Record method, path, version, content type, auth requirements, idempotency expectations, sync or async semantics, and whether the endpoint supports pagination, streaming, file upload, or file download.
   - Extract every explicit parameter from path, query, headers, cookies, and body.
   - Identify implicit inputs injected by middleware, auth context, feature flags, tenant context, or server defaults.

3. Trace the execution path end to end.
   - Follow the call chain from router to handler, then to service, domain logic, persistence, events, background jobs, and external integrations.
   - Capture validation, authorization, branching, transactions, retries, fallback behavior, state transitions, side effects, and non-obvious defaults.
   - Note which steps are synchronous, which are deferred, and which rely on eventual consistency.

4. Reconstruct success and failure outputs.
   - Enumerate success status codes, response body fields, headers, pagination metadata, and conditional response variants.
   - Enumerate failure branches and map them to validation errors, auth failures, missing resources, conflicts, rate limits, dependency failures, and framework-default exceptions.
   - Distinguish between declared errors in docs and errors actually reachable from implementation.

5. Produce the final analysis in a stable shape.
   - Use [references/endpoint-analysis-template.md](./references/endpoint-analysis-template.md) as the default report format.
   - Use Mermaid for the business flow. Keep the graph readable; collapse repetitive framework details into notes or bullets instead of overloading the diagram.
   - Include file references when local code is available.

6. Call out uncertainty explicitly.
   - Mark anything not directly verified as `推断` or `未验证`.
   - If docs and code differ, report both and identify the likely source of truth.
   - Do not invent field types, status codes, validation rules, or side effects.

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

- Keep facts and inferences separate.
- Prefer tables for parameter and error enumeration.
- Mention auth, idempotency, side effects, external dependencies, and persistence changes whenever they exist.
- Explain validation and error handling at the boundary and in the domain layer.
- If the endpoint mutates data, state what is written, emitted, or queued.
- If the endpoint reads from multiple backends, mention consistency and failure propagation.

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

## References

- Read [references/endpoint-analysis-template.md](./references/endpoint-analysis-template.md) for the default report structure and Mermaid example.
- Read [references/source-tracing-checklist.md](./references/source-tracing-checklist.md) when artifacts are incomplete or the endpoint spans middleware, services, and external systems.
