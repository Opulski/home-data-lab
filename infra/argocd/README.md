# ArgoCD Applications

This directory contains ArgoCD Application definitions for GitOps-based deployments.

## Structure

```
argocd/
├── apps/              # Individual application definitions
├── projects/          # ArgoCD projects for grouping apps
└── app-of-apps.yaml   # Root application (app of apps pattern)
```

## Guidelines

- Each application should have its own YAML definition
- Use the "app of apps" pattern for managing multiple apps
- Configure auto-sync for automated deployments
- Set up proper sync policies and health checks
- Use different ArgoCD projects for different environments

## Example Application

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: data-ingestion
  namespace: argocd
spec:
  project: home-data-lab
  source:
    repoURL: https://github.com/Opulski/home-data-lab
    targetRevision: main
    path: infra/k8s/overlays/prod
  destination:
    server: https://kubernetes.default.svc
    namespace: data-platform
```
