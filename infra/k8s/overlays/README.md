# Kubernetes Overlays

This directory contains environment-specific Kubernetes configurations using Kustomize.

## Structure

```
overlays/
├── dev/
│   └── kustomization.yaml
├── staging/
│   └── kustomization.yaml
└── prod/
    └── kustomization.yaml
```

## Guidelines

- Each overlay inherits from base manifests
- Override only what's necessary per environment
- Use different resource limits per environment
- Apply appropriate scaling configurations
- Use environment-specific ConfigMaps for settings

## Example Usage

```bash
# Apply dev environment
kubectl apply -k overlays/dev

# Apply production environment
kubectl apply -k overlays/prod
```
