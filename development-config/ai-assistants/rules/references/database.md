---
trigger: model_decision
description: Load for database, ORM, SQL, SQLAlchemy, Alembic, schema, migration, backfill, pagination, N+1, bulk read/write, persistence, transaction, locking, or data-retention tasks.
---
# Database And Persistence Rules

Use these rules when work touches database access, persisted data models,
schemas, migrations, backfills, transactions, pagination, or data-retention
behavior.

## Query And Persistence Baseline

- Correctness, compatibility, and data safety take priority over change
  scope and code shape.
- Identify persisted formats, schema contracts, existing indexes, external
  readers, and deployment order before changing storage behavior.
- Prefer explicit, bounded queries. Avoid unbounded `SELECT` in user-facing
  or large-data paths; use cursor pagination and explicit `LIMIT`.
- Batch or bulk by default for reads, writes, updates, and deletes. Avoid
  N+1 query patterns; preload required data before iterating.
- Never introduce, approve, or leave ORM, query, or session calls inside
  `for`/`while` loops, comprehensions, or per-item callbacks.
- Keep transaction boundaries explicit. Avoid long transactions and avoid
  external network I/O inside transactions unless the project already has a
  safe pattern for it.

## Migrations And Backfills

- Call out blast radius, compatibility, lock duration, backfill strategy,
  rollback path, and deployment order for schema or data changes.
- Prefer additive, backward-compatible migrations before code starts
  depending on new columns, tables, indexes, or constraints.
- Avoid destructive schema changes in the same deployment as code that
  stops using the old shape unless an explicit compatibility plan exists.
- For large tables, backfill in bounded batches and make the operation
  resumable or idempotent where practical.
- Be careful with `NOT NULL`, default values, index creation, and column
  rewrites on large tables. Flag lock or rewrite risk before implementation.
- Ask before running data-mutating migrations, broad backfills, or cleanup
  commands against real environments.
