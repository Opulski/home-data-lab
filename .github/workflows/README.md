# GitHub Actions Workflows

This directory contains CI/CD workflows for automated testing, building, and deployment.

## Common Workflows

- **CI**: Continuous Integration (linting, testing, building)
- **CD**: Continuous Deployment (deploy to environments)
- **Security**: Dependency scanning, vulnerability checks
- **Release**: Automated releases and versioning

## Example Workflows

```
workflows/
├── ci.yml              # Run tests and linters on PR
├── build-images.yml    # Build and push Docker images
├── deploy-dev.yml      # Deploy to dev environment
├── deploy-prod.yml     # Deploy to production
└── security-scan.yml   # Security scanning
```

## Guidelines

- Use workflow templates for consistency
- Cache dependencies to speed up builds
- Use secrets for sensitive data
- Add status badges to README
- Set up branch protection rules
- Use manual approval for production deployments
