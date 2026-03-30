# Base Ref Resolution

Use this guide when planning, confirming, or reporting a restack.

## Default Rule

- Resolve an unqualified base branch name such as `dev`, `main`, or `master` to the corresponding remote-tracking ref `<remote>/<branch>` by default.
- If the user provides a full remote ref such as `origin/main` or `upstream/master`, use it directly.
- Use a local ref only when the user explicitly asks for local branch state or provides a full local ref such as `refs/heads/main`.

## Freshness

- If the default remote-tracking behavior is in use and no explicit `--base-ref` was provided, fetch the remote branch first unless the environment is offline or the user explicitly asks to skip fetch.
- If fetch is skipped, report that clearly instead of implying the remote-tracking ref is current.

## Confirmation and Reporting

- Before apply mode, show the base branch provided by the user, the resolved base ref, the source branch, and the new branch name.
- In the final report, state whether the base ref was a remote-tracking ref or an explicit local ref.
- In the final report, state whether fetch was executed or skipped.
