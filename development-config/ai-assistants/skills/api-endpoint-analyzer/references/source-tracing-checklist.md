# Source Tracing Checklist

Use this checklist when the endpoint is hard to follow or the repository is large.

## 1. Route Discovery

- Search route registration by path, method, router tag, operation id, or handler name.
- Check versioned routers, nested routers, generated routes, and framework decorators.
- Verify whether middleware rewrites the path, method, or request context.

## 2. Input Schema Discovery

- Find request DTOs, Pydantic models, serializers, protobuf messages, or form definitions.
- Trace field aliases, validators, defaults, enum constraints, and hidden server-side defaults.
- Check auth middleware, dependency injection, or context builders for implicit inputs.

## 3. Execution Path

- Trace handler to service/use case to repository or gateway.
- Identify transaction boundaries, retries, circuit breakers, and fallback paths.
- Record side effects such as DB writes, cache updates, events, tasks, or notifications.

## 4. Response Assembly

- Find response DTOs, presenters, serializers, or manual JSON assembly.
- Look for conditional fields, derived fields, and framework wrappers.
- Check response headers, cookies, pagination metadata, and content negotiation.

## 5. Error Enumeration

- Search for raised exceptions, returned error objects, and framework exception handlers.
- Check validation layers, auth failures, permission checks, not-found branches, conflicts, and rate limits.
- Verify whether infrastructure failures are mapped to user-facing status codes or bubble up as 500s.

## 6. Supporting Evidence

- Prefer tests that hit the endpoint directly.
- Use OpenAPI, Swagger, protobuf, or API docs as contract references, not sole truth when code exists.
- Check migration or schema files if the endpoint depends on specific persistence fields or state transitions.

## 7. Common Omissions

- Hidden auth or tenant scoping
- Soft-delete filters
- Feature flags and environment gates
- Async workers triggered after response
- Default framework errors such as 404, 405, and schema-validation failures
- Idempotency keys, deduplication, and replay protection
- Cache invalidation or read-after-write consistency gaps
