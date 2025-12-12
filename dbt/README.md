# DBT (Data Build Tool)

This directory contains dbt projects for data modeling and transformation.

## Structure

Follow dbt best practices:
```
dbt/
├── models/
│   ├── staging/
│   ├── intermediate/
│   └── marts/
├── macros/
├── tests/
├── snapshots/
└── dbt_project.yml
```

## Guidelines

- Use staging models for raw data ingestion
- Create intermediate models for business logic
- Build marts for final analytics-ready datasets
- Add data quality tests for all models
- Document all models and columns
