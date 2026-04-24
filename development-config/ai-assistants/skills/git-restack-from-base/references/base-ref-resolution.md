# Base Ref Resolution

Use this guide when planning, confirming, or reporting a restack.

## Default Rule

- Treat an unqualified base branch name such as `dev`, `main`, `master`, or `release/1.0` as a remote branch by default. Resolve it to the corresponding remote-tracking ref `<remote>/<branch>`.
- Use `origin` as the default remote when it exists. If `origin` is absent and exactly one remote exists, use that remote. If multiple non-`origin` remotes exist, ask which remote to use.
- If the user provides a full remote-tracking ref such as `origin/main` or `upstream/release/1.0`, use it directly.
- Use a local ref only when the user explicitly asks for local branch state or provides a full local ref such as `refs/heads/main`.
- Never silently fall back to a same-name local branch when the remote-tracking ref is missing or ambiguous.

## Freshness

- If a remote-tracking base is in use and no explicit `--base-ref` was provided, fetch the specific remote branch first unless the environment is offline or the user explicitly asks to skip fetch.
- For a full remote-tracking ref such as `origin/release/1.0`, parse the first path component as the remote and fetch the remaining branch name. For an unqualified branch with slashes such as `release/1.0`, do not treat `release` as a remote unless it is a configured git remote.
- If fetch is skipped, report that clearly instead of implying the remote-tracking ref is current.

## Confirmation and Reporting

- Before apply mode, show the base branch provided by the user, the resolved base ref, the source branch, and the new branch name.
- In the final report, state whether the base ref was a remote-tracking ref, an explicit local ref, or another explicit ref.
- In the final report, state whether fetch was executed or skipped.
