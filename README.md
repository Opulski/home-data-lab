# home-data-lab

Data platform running on Raspberry PIs for home data collection, processing, and analytics.

## Project Structure

This repository follows GitOps and data platform best practices with a flat, readable structure:

```
home-data-lab/
├── apps/                    # Microservices and applications
├── pipelines/               # Batch jobs and data processing pipelines
├── dbt/                     # Data modeling and transformation (dbt)
├── orchestration/           # Workflow orchestration (Airflow DAGs)
├── infra/                   # Infrastructure as Code
│   ├── k8s/
│   │   ├── base/           # Base Kubernetes manifests
│   │   └── overlays/       # Environment-specific overlays (dev, staging, prod)
│   └── argocd/             # ArgoCD application definitions
├── docs/                    # Documentation
│   ├── architecture/        # Architecture diagrams and design docs
│   └── adr/                # Architecture Decision Records
├── scripts/                 # Utility scripts for dev, deploy, and maintenance
└── .github/workflows/       # CI/CD workflows (GitHub Actions)
```

## Getting Started

Each directory contains its own README with specific guidelines and examples. Start by exploring:

1. [Apps](./apps/README.md) - For microservices and applications
2. [Pipelines](./pipelines/README.md) - For data processing jobs
3. [Infrastructure](./infra/README.md) - For Kubernetes and GitOps setup
4. [Documentation](./docs/README.md) - For architecture and ADRs

## Development Principles

- **GitOps**: All infrastructure and configuration managed through Git
- **Infrastructure as Code**: Kubernetes manifests, no manual cluster changes
- **Automation**: CI/CD pipelines for testing and deployment
- **Documentation**: Keep docs close to code, use ADRs for decisions
- **Modularity**: Independent, deployable components

## Contributing

See individual directory READMEs for specific contribution guidelines.
