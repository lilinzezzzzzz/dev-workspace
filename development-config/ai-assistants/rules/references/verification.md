---
trigger: model_decision
description: Load for test planning, bug fixes, regression coverage, CI failures, lint, type-check, verification strategy, test pyramid, or reporting test results.
---
# Verification Rules

Use these rules when planning or running tests, fixing bugs, investigating CI
failures, choosing lint/type-check commands, or reporting verification status.

## Verification Strategy

- Run the smallest meaningful verification that covers changed behavior:
  targeted tests first, then broader tests, lint, or type-check when risk or
  project convention requires it.
- Use the repository's existing commands, test helpers, fixtures, and
  dependency management tools before introducing new verification tooling.
- Bug fixes should include regression coverage when the repo has a practical
  test path.
- Do not infer test results from code reading. Do not claim coverage unless
  it was measured.

## Test Scope

- Follow the test pyramid: unit tests cover isolated logic and edge cases and
  should be the largest share; integration tests cover cross-boundary behavior
  and should be fewer; system/E2E tests cover only critical end-to-end
  workflows and should be the fewest.
- Add broader tests when a change touches shared behavior, cross-module
  contracts, persistence, auth, concurrency, or external-service integration.
- Keep narrow documentation or configuration changes to lightweight
  verification unless the change affects executable behavior.

## Reporting

- Report verification commands with their results.
- If verification cannot run, state the exact command not run and the
  blocker, such as missing credentials, services, dependencies, network, or
  sandbox restrictions.
- If only targeted verification was run, state the remaining unverified risk
  when it matters.
