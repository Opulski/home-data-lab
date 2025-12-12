# Apps

This directory contains microservices and applications that make up the home-data-lab platform.

## Structure

Each application should be in its own subdirectory with:
- Source code
- Dockerfile
- Local development configuration
- Application-specific documentation

## Examples

```
apps/
├── api-gateway/
├── data-ingestion-service/
├── metrics-collector/
└── web-dashboard/
```

## Guidelines

- Each app should be independently deployable
- Use consistent naming conventions
- Include health check endpoints
- Follow 12-factor app principles
