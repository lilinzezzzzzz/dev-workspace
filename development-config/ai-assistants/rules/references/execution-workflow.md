---
trigger: model_decision
description: Load for non-trivial, multi-file, risky, data-affecting, API-affecting, ambiguous, blocked, or verification-heavy technical tasks.
---
# Execution Workflow Rules

Use this workflow for non-trivial technical work, especially multi-file,
risky, data-affecting, API-affecting, ambiguous, or verification-heavy tasks.

## Workflow

1. **Understand**: Read the relevant code, contracts, local instructions,
   and tests before editing.
2. **Plan**: List files to modify and the one-line intent for each. Flag
   compatibility, migration, security, or data-safety concerns.
3. **Implement**: Make one logical change per edit. Keep call paths shallow
   and avoid speculative abstractions.
4. **Verify & Report**: Run the smallest meaningful tests, linter, or
   type-checker for the changed behavior. Report what changed, what passed,
   what was not run, and why.

## Planning Visibility

- Show a visible plan for non-trivial, multi-file, risky, data-affecting,
  API-affecting, or ambiguous tasks.
- Keep the plan scoped to the requested outcome and update it when the task
  materially changes.
- Do not stop at a proposal when the user clearly expects implementation and
  repo context is sufficient.

## Fallbacks

- If blocked by environment, credentials, network, services, or missing
  dependencies, report the blocker and a practical alternative.
- If rules conflict, apply: correctness > security and data safety > scope >
  code shape.
- If verification cannot run, state the exact command not run and the
  blocker.
