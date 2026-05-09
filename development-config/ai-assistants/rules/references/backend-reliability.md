---
trigger: model_decision
description: Load for backend service, API, handler, worker, auth, permission, validation, error handling, timeout, retry, idempotency, logging, observability, or security-sensitive tasks.
---
# Backend Reliability And Security Rules

Use these rules when work touches backend services, APIs, workers, message
handlers, validation boundaries, authorization, error handling, retries,
timeouts, idempotency, logging, or security-sensitive behavior.

## Boundaries And Validation

- Use clear types at public and important internal boundaries. Avoid loose
  `Any` and ad hoc dicts when a structured model or typed mapping is
  practical.
- Validate at transport, message, and persistence boundaries. Keep domain
  logic out of handlers, routers, controllers, and framework glue.
- Preserve public API contracts, message schemas, persisted formats, SDK
  surfaces, and cross-service compatibility unless the task explicitly
  includes a migration or deprecation plan.
- Prefer existing project helpers for request parsing, dependency
  injection, error responses, logging, metrics, and configuration.

## Failure Handling

- Handle errors explicitly. Do not swallow exceptions, hide partial
  failures, or convert unknown failures into success.
- Use stable error codes or envelopes for API failures when the project has
  an existing contract.
- Consider timeout, retry, cancellation, partial failure, and idempotency
  for network calls, workers, queue consumers, and external services.
- Retries should be bounded and safe for the operation. Non-idempotent
  writes need an idempotency key, uniqueness guard, or explicit reason why
  retry is safe.
- Preserve cancellation behavior in async code. Avoid blocking I/O in async
  hot paths unless offloaded through the project-standard mechanism.

## Security And Operations

- Prefer least privilege and existing dependencies. Do not add secrets,
  credentials, tokens, cookies, or private keys to source files.
- Log useful failure context without leaking secrets, credentials, PII, or
  full request/response payloads unless the project has an approved redaction
  path.
- For auth and permission changes, identify who can call the path, what
  resource is protected, and whether default behavior should deny access.
- Ask before destructive commands, force push, broad removal operations,
  data-mutating migrations, or dependency upgrades with large lockfile churn.
