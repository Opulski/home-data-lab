# Base Kubernetes Manifests

This directory contains base Kubernetes manifests that are common across all environments.

## Structure

Organize by resource type:
```
base/
├── deployments/
├── services/
├── configmaps/
├── secrets/          # Use sealed-secrets or external-secrets
├── ingress/
└── kustomization.yaml
```

## Guidelines

- Use descriptive names for resources
- Set resource limits and requests
- Include liveness and readiness probes
- Use ConfigMaps for configuration
- Never commit plain-text secrets
- Add labels for organization and monitoring
