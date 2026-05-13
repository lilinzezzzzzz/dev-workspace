# Source Tracing Checklist

Use this checklist when endpoint artifacts are incomplete, generated, or spread across middleware, services, jobs, and external systems. Stop once the answer has enough evidence for the user's requested depth.

## 1. Route Discovery

- Search path, method, route name, router tag, operation id, handler name, RPC method, or webhook topic.
- Check versioned routers, mounted prefixes, nested routers, generated routes, decorators, and registration order.
- Verify middleware or gateway behavior that rewrites path, method, headers, body, or request context.

## 2. Input Schema Discovery

- Find request DTOs, Pydantic models, serializers, protobuf messages, form definitions, multipart fields, or file constraints.
- Trace field aliases, validators, defaults, enum constraints, coercion, required/optional semantics, and server-side defaults.
- Check auth middleware, interceptors, dependency injection, tenant resolvers, feature flags, and context builders for implicit inputs.

## 3. Execution Path

- Trace handler/controller to service/use case, domain logic, repository, gateway, external client, or async job.
- Identify authorization checks, transaction boundaries, locks, retries, circuit breakers, fallbacks, timeouts, and cancellation handling.
- Record side effects: DB writes, cache read/write/invalidation, events, tasks, notifications, object storage, and third-party calls.
- Check state transitions, idempotency keys, deduplication, replay protection, and eventual-consistency assumptions.

## 4. Response Assembly

- Find response DTOs, presenters, serializers, protobuf messages, stream event schemas, file responses, or manual JSON assembly.
- Look for conditional fields, derived fields, nullability, field masking, framework wrappers, and response envelopes.
- Check status codes, headers, cookies, pagination metadata, redirects, content negotiation, and compression.

## 5. Error Enumeration

- Search for raised exceptions, returned error objects, and framework exception handlers.
- Check validation layers, auth failures, permission/tenant checks, not-found branches, conflicts, quotas, and rate limits.
- Verify whether infrastructure failures are mapped to user-facing status/error codes or bubble up as 500s.
- Include framework defaults such as 404, 405, schema validation, unsupported media type, and payload-too-large errors when reachable.

## 6. Supporting Evidence

- Prefer tests that hit the endpoint directly.
- Use OpenAPI, Swagger, protobuf, or API docs as declared contracts, not sole truth when code exists.
- Check migrations, DB schema, ORM models, indexes, cache key builders, and message schemas when persistence or events affect behavior.
- Check fixtures and mocks for undocumented response shapes or error branches.

## 7. Common Omissions

- Hidden auth or tenant scoping
- Soft-delete filters
- Feature flags and environment gates
- Async workers triggered after response
- Default framework errors such as 404, 405, and schema-validation failures
- Idempotency keys, deduplication, and replay protection
- Cache invalidation or read-after-write consistency gaps
- File cleanup after upload failure
- External API timeout, retry, and partial-failure behavior
