---
name: git-commit
description: Generate concise Git commit messages following Conventional Commits specification with branch naming conventions and merge strategies
---

* **Branch Naming:**
  * feature/<description>, bugfix/<description>, hotfix/<description>, release/<version>.

* **Commit Message Specification:**
  * **Format:** `<type>(<scope>): <subject>` (Conventional Commits)
  * **Types:** feat, fix, chore, docs, style, refactor, test, perf, ci
  * **Subject Rules:**
    * Use imperative mood (e.g., "add" not "added")
    * Lowercase, no period at the end
    * Keep within 50 characters
  * **Body (optional):**
    * Explain "what" changes were made
    * Keep within 72 characters per line when possible

* **Merge Strategy:**
  * feature → develop: Squash or rebase.
  * develop → main: Merge commit (preserve history).
