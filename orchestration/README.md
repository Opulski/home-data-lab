# Orchestration

This directory contains workflow orchestration configurations, primarily Airflow DAGs.

## Structure

```
orchestration/
├── dags/
│   ├── sensor_data_pipeline.py
│   ├── daily_aggregation.py
│   └── weekly_reports.py
├── plugins/
├── config/
└── tests/
```

## Guidelines

- One DAG per file
- Use meaningful DAG IDs
- Set appropriate schedules and SLAs
- Include task documentation
- Implement proper error handling and alerts
- Test DAGs before deployment
