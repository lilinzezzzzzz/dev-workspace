---
trigger: model_decision
description: Load for non-trivial code changes, reviews, bug investigations, unfamiliar modules, local instruction discovery, blast radius analysis, or tasks that may overlap with user work.
---
# Codebase Discovery Rules

Use these rules before planning, reviewing, editing, or testing non-trivial
technical work.

## Minimum Context

- Read files directly involved in the requested change, plus immediate
  callers, callees, tests, config, schemas, and local instructions that
  constrain the behavior.
- Prefer project-local instructions and conventions over global defaults
  unless correctness, security, or data safety would be weakened.
- Check workspace state before edits when changes may overlap with user work.
- Use fast local search first, such as `rg` and `rg --files`, then open the
  specific files needed for the task.

## Blast Radius

- Identify public APIs, persisted formats, message schemas, migrations,
  generated artifacts, concurrency, external services, auth, permissions,
  and performance-sensitive paths before changing behavior.
- For shared code, trace the important call paths and representative tests
  before editing.
- For configuration or workflow changes, inspect the commands, scripts, CI
  jobs, and documentation that consume the changed file.

## Decision Points

- Ask only when missing information affects correctness, data safety, or API
  compatibility.
- For low-risk gaps, choose the conservative option and state the assumption.
- If no project convention exists, use the global defaults from `AGENTS.md`.
- If a nearby issue is out of scope, mention it as a follow-up unless it
  causes incorrect behavior in the current change or is a trivial fix in the
  same function.
