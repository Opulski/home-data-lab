# Pipelines

This directory contains batch jobs and data processing pipelines.

## Structure

Organize pipelines by purpose or domain:
- ETL jobs
- Data ingestion pipelines
- Data export jobs
- Scheduled batch processes

## Examples

```
pipelines/
├── sensor-data-ingestion/
├── daily-aggregation/
├── weekly-reports/
└── data-quality-checks/
```

## Guidelines

- Each pipeline should be idempotent
- Include retry logic and error handling
- Log processing metrics
- Document data dependencies and schedules
