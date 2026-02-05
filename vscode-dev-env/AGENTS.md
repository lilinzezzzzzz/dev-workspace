# Agent Instructions

## Role & Context

* **User Role:** Senior Python & Golang Backend Development Engineer.
* **Tech Stack:**
  * AI: LLMs, GenAI, Multi-modal Models, RAG, Fine-tuning, Inference Optimization, MLOps.
  * Backend: AI Platform / Middle-end Development, Distributed Systems.


## Coding Standards

### General

* **Quality:**
  * High performance, production-ready.
  * Prioritize security, avoid undefined behavior, and minimize logical flaws.
  * Do NOT include instructions to run linters; compliance is assumed at generation time.
* **Architecture:**
  * Modular, scalable, and clean code structure suitable for AI enterprise applications.
* **Type Safety:**
  * Ensure public APIs are fully type-annotated.
  * Prefer explicit, precise types over permissive or ambiguous typing.

### Python

* **Style:**
  * Pythonic, Pydantic v2, PEP 8 compliant.
  * Ensure compatibility with ruff and basedpyright (basic mode).
  * Avoid implicit Any.
* **Database:**
  * Prefer SQLAlchemy ORM over raw SQL.
  * Use SQLAlchemy 2.0 style with type annotations.
* **Async:**
  * Prefer anyio over raw asyncio for async primitives (tasks, locks, events).
  * Use httpx for async HTTP requests; avoid aiohttp.
  * Use anyio.create_task_group for structured concurrency.
  * Avoid mixing sync and async code; use anyio.to_thread.run_sync or anyio.to_process.run_sync for blocking calls.
* **Logging:**
  * Use structlog for structured logging; avoid print statements.
  * Log levels: DEBUG for development, INFO for operations, WARNING/ERROR for issues.
* **API Design:**
  * Use FastAPI for REST APIs; prefer Pydantic V2 models for request/response schemas.
  * Prefer GET and POST methods; use PUT/DELETE/PATCH only when explicitly required.
  * Implement consistent error responses with error codes and messages.
* **Runtime & Environment:**
  * Use uv (Astral) for project environment and dependency management.
  * Define dependencies via pyproject.toml (PEP 621), resolve with uv.lock.
  * Do not assume requirements.txt, pip, pip-tools, poetry, or conda.
  * Ensure compatibility with uv run and uv pip.

### Golang

* **Style:**
  * Follow Effective Go and Go Code Review Comments.
  * Ensure code passes go vet, staticcheck, and golangci-lint.
  * Use gofmt / goimports for formatting.
* **Runtime & Environment:**
  * Use Go Modules (go.mod / go.sum) for dependency management.
  * Prefer standard library; minimize third-party dependencies.
  * Ensure compatibility with go build and go run.
* **Conventions:**
  * Error handling: Check and handle errors explicitly; avoid _ for error returns.
  * Concurrency: Use goroutines and channels idiomatically; prefer sync primitives for shared state.
  * Naming: Use MixedCaps (exported) and mixedCaps (unexported); avoid underscores.
  * Context: Pass context.Context as the first parameter; propagate cancellation and deadlines.

## Git Workflow

* **Branch Naming:**
  * feature/<description>, bugfix/<description>, hotfix/<description>, release/<version>.
* **Commit Message:**
  * Format: `<type>(<scope>): <subject>` (Conventional Commits).
  * Types: feat, fix, docs, style, refactor, perf, test, chore, ci.
  * Subject: imperative mood, lowercase, no period, max 50 chars.
  * Body (optional): explain "what" and "why", wrap at 72 chars.
* **Merge Strategy:**
  * feature → develop: Squash or rebase.
  * develop → main: Merge commit (preserve history).


## Response Preferences

* **Conciseness:**
  * Be direct and brief. Prefer responding in Chinese.
  * When professional terminology is involved, provide both Chinese and English terms.
  * Focus on the "Why" and "How" of complex architectural decisions.
* **Solution-Oriented:**
  * When providing code, prioritize robustness and edge-case handling over quick-and-dirty scripts.
* **Format:**
  * Use structured Markdown for technical comparisons or pros/cons analysis.


## Analysis & Verification Protocol

* **Challenge Assumptions:**
  * Rigorously stress-test and critique all proposed designs, technical solutions, and underlying assumptions.
  * Flag suboptimal instructions before executing.
* **Identify Risks:**
  * Proactively highlight potential logical flaws, scalability bottlenecks, concurrency issues, or security vulnerabilities.
* **Constructive Feedback Loop:**
  * If a proposed solution is suboptimal or an anti-pattern, propose superior, industry-standard alternatives before proceeding.


## Timeliness & Web Search

* **Web Search:**
  * Enabled and performed actively.
  * For queries involving frequently updated libraries, technologies, or current events, use web search to ensure answers reflect the latest versions and practices.
* **Information Freshness:**
  * Prioritize the latest official documentation over internal training data.
