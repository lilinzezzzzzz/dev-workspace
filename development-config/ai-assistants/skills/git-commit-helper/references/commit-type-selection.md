# Commit Type Selection

Use this guide to classify the staged change set. Pick the smallest accurate type that explains the user-visible intent of the change.

## Type Mapping

- `feat`: introduces a new user-facing or developer-facing capability.
- `fix`: corrects incorrect behavior, regression, data bug, validation gap, or runtime failure.
- `refactor`: changes structure without changing intended behavior.
- `perf`: materially improves latency, throughput, memory, query shape, or resource usage.
- `docs`: changes documentation only.
- `test`: adds or updates tests without changing production behavior.
- `ci`: changes CI workflows, pipelines, or automation config.
- `build`: changes build system, packaging, bundling, or dependency build tooling.
- `chore`: repository maintenance that does not fit better elsewhere.
- `style`: formatting or non-semantic code style changes only.
- `revert`: explicitly reverts a prior commit.

## Scope Selection

- Use a scope only when it adds real signal, such as `auth`, `api`, `db`, `ui`, `config`, `vector`, or a bounded module name.
- Prefer the narrowest stable module or subsystem name.
- Omit scope when the change spans many modules or when any chosen scope would be misleading.

## Subject Rules

- Use imperative mood.
- Keep it short and concrete.
- Describe what changed, not why the person changed it.
- Prefer Chinese by default, but keep domain terms such as `JWT`, `OpenAI API`, `Milvus`, or `CI` in English when clearer.
- Do not end the subject with punctuation.

## Body Rules

Add a body only when one line is not enough. Good reasons include:

- the diff has two or three tightly related subchanges
- rollout or compatibility detail matters
- the subject alone would hide an important behavior change

Body guidance:

- format the body as a bulleted list using `- ` prefixes
- each bullet should capture one subchange or one piece of critical context
- keep bullets concise
- do not restate the subject verbatim

## Footer Rules

- Use `BREAKING CHANGE: ...` when existing callers, configs, schemas, or workflows must change.
- Use issue references such as `Closes #123` only when they are known.
- For reverts, include the reverted commit reference when available.

## Edge Cases

### Mixed staged changes

- If multiple unrelated concerns are staged, do not force one misleading message.
- Recommend splitting the commit or restaging before committing.

### Dependency updates

- Use `build` when the change is packaging or build-tool related.
- Use `chore` for routine dependency maintenance when no better type applies.
- Use `fix` or `feat` if the dependency change is part of a functional fix or feature and the diff clearly shows that intent.

### Generated files

- Classify by the source change, not by the generated artifact alone.
- If only generated output changed and source intent is unknown, say that confidence is limited.

### Test and docs with code changes

- Choose the type based on the primary production change, not the supporting tests or docs.

## Recommended Output Bias

- Prefer one strong recommendation over several equally plausible messages.
- If ambiguity remains, state the assumption in one short sentence instead of emitting many options.
