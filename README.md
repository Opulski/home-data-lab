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

## Development Setup

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for dependency management
- pre-commit for code quality hooks

### Local Development
```bash
# Install dependencies
uv sync --group dev

# Install pre-commit hooks
pre-commit install

# Run pipelines locally
make run

# Run specific pipeline stages
make ingest
make stg
make marts AS_OF=2025-12-13T10-00-00Z
```

### Code Quality
```bash
# Run linters
uv run ruff check pipelines/
uv run black --check pipelines/

# Run formatters
uv run ruff check --fix pipelines/
uv run black pipelines/

# Run pre-commit on all files
pre-commit run --all-files
```

## TODO

- [ ] Implement ENTSO-E API ingestion (waiting for API key)
- [ ] Add Renovate for automatic dependency updates (supports uv.lock)
- [ ] Extract shared utilities (timestamp parsing, partition loading) to `pipelines/utils.py`
- [ ] Add basic logging to replace print statements
- [ ] Implement ex-ante forecast model (remove ex-post features)

### Roadmap (Energy CV + Learning)
- [ ] Gate-closure helpers + `config.yaml` (AS_OF, TZ, paths)
- [ ] Forecast model zoo (LinReg, RF/GBM), walk-forward split, leaderboard vs naive
- [ ] Price spike classification (binary/quantile threshold)
- [ ] Regime clustering (KMeans on load/price profiles)
- [ ] Anomaly detection on residuals (Isolation Forest)
- [ ] Light data quality checks (pandera ranges/non-null)
- [ ] Docs: gate-closure & ex-ante feature assumptions
- [ ] Fuel/holiday proxies for merit-order & seasonality
- [ ] Optional: small DL demo (LSTM/TCN) for forecasting
- [ ] Optional: simple orchestration demo (e.g., Prefect flow)

## Contributing

See individual directory READMEs for specific contribution guidelines.
