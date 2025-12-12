# Infrastructure

This directory contains infrastructure-as-code (IaC) configurations for Kubernetes and GitOps.

## Structure

```
infra/
├── k8s/
│   ├── base/          # Base Kubernetes manifests
│   └── overlays/      # Environment-specific overlays (dev, staging, prod)
└── argocd/            # ArgoCD application definitions
```

## GitOps Approach

- All infrastructure changes are committed to Git
- ArgoCD monitors this repository and applies changes automatically
- Use Kustomize for environment-specific configurations
- Keep secrets in external secret management (not in Git)

## Guidelines

- Follow Kubernetes best practices
- Use resource limits and requests
- Implement proper RBAC
- Use namespaces for isolation
- Version all manifests
