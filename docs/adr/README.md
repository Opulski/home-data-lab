# Architecture Decision Records (ADR)

This directory contains Architecture Decision Records documenting important architectural decisions.

## What is an ADR?

An ADR is a document that captures an important architectural decision made along with its context and consequences.

## ADR Template

```markdown
# ADR-NNN: Title

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
What is the issue that we're seeing that is motivating this decision or change?

## Decision
What is the change that we're actually proposing or doing?

## Consequences
What becomes easier or more difficult to do because of this change?
```

## Naming Convention

- Use format: `ADR-001-descriptive-title.md`
- Number sequentially
- Use lowercase with hyphens

## Examples

- `ADR-001-use-kubernetes-for-orchestration.md`
- `ADR-002-adopt-airflow-for-workflow-management.md`
- `ADR-003-select-postgresql-for-metadata-store.md`
