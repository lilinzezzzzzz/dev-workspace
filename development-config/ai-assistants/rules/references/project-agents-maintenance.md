---
trigger: model_decision
description: Load for creating, updating, deleting, reviewing, or syncing project-level AGENTS.md files, subdirectory instructions, or durable repository-specific agent guidance.
---
# Project AGENTS.md Maintenance Rules

Use these rules when work touches project-level `AGENTS.md` files, nested
instruction files, or durable repository-specific guidance for future agents.

## When To Maintain

- Maintain project-level `AGENTS.md` files when the current technical task
  reveals a durable project convention, workflow, command, invariant, or
  local constraint that future agents need in order to work safely.
- Update instructions when code changes alter local build, test, migration,
  generation, deployment, API compatibility, security, data-safety, or
  ownership expectations.
- Do not update project instructions solely for personal preference, generic
  engineering advice, transient task notes, or observations that are already
  enforced by code, tests, tooling, or global instructions.
- If the needed update is uncertain or would change team policy, report the
  proposed wording instead of editing silently.

## Scope And Placement

- Before editing a project-level `AGENTS.md`, read the applicable instruction
  chain from the project root down to the target path.
- Also read child `AGENTS.md` files that would be affected by the proposed
  parent-level rule.
- Place new guidance in the narrowest `AGENTS.md` that covers the affected
  code. Use a parent file only for repository-wide or cross-directory rules.
- Do not duplicate parent or global rules. Child files should only
  specialize, override, or add local constraints.
- Keep cross-service contracts, public API guidance, persisted formats,
  migrations, generated artifacts, and deployment constraints at the lowest
  common ancestor that covers all affected paths.

## Content Quality

- Keep instructions factual, actionable, and specific to the repository or
  subdirectory.
- Prefer concise bullets with concrete commands, file paths, ownership
  boundaries, compatibility constraints, or verification expectations.
- Avoid vague process language that an agent cannot verify or execute.
- Mention when a rule is compatibility-sensitive, data-affecting,
  security-sensitive, or requires human confirmation.
- Keep examples minimal and project-specific. Do not add long tutorials to
  `AGENTS.md`; use project docs for detailed explanations.

## Editing Safety

- Preserve user work. Do not overwrite unrelated changes in `AGENTS.md`.
- When deleting or relaxing a project-level instruction, first verify
  references and current behavior. Preserve compatibility notes unless the
  removal is clearly in scope and the compatibility impact is understood.
- If multiple nested files conflict, prefer the more specific file for the
  affected path unless correctness, security, or data safety would be
  weakened.
- If a rule needs broad migration, deprecation, or team approval, leave a
  proposed change in the response instead of making an unsupported edit.

## Reporting

- Report project-level `AGENTS.md` changes with the same rigor as code
  changes: file changed, reason, verification performed, and remaining policy
  or compatibility risk.
- If no instruction update was made despite discovering a durable convention,
  state why it was skipped.
