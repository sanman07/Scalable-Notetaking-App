# Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying the Notes App using a microservices architecture.

## 📁 Structure

```
k8s/
├── base/                    # Base Kubernetes resources
│   ├── namespace.yaml
│   ├── database-*.yaml      # PostgreSQL database resources
│   ├── backend-*.yaml       # FastAPI backend resources
│   ├── frontend-*.yaml      # React frontend resources
│   ├── ingress.yaml         # Ingress configuration
│   └── kustomization.yaml   # Base kustomization
└── overlays/
    ├── development/         # Development environment
    └── production/          # Production environment
```

## 🚀 Quick Start

### Prerequisites

1. **Kubernetes cluster** (Minikube, GKE, EKS, AKS, etc.)
2. **kubectl** configured to connect to your cluster
3. **Docker** for building images
4. **kustomize** (usually included with kubectl)
5. **NGINX Ingress Controller** (optional, for ingress)

### 1. Build Images

```bash
# Build images with default 'latest' tag
./scripts/build-images.sh

# Build with specific tag
./scripts/build-images.sh v1.0.0

# Build and push to registry
./scripts/build-images.sh v1.0.0 your-registry.com/your-project
```

### 2. Deploy to Development

```bash
# Deploy to development environment
./scripts/deploy-k8s.sh development

# Or manually with kubectl
kubectl apply -k k8s/overlays/development
```

### 3. Deploy to Production

```bash
# Deploy to production environment
./scripts/deploy-k8s.sh production

# Or manually with kubectl
kubectl apply -k k8s/overlays/production
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Ingress       │    │   Frontend      │    │   Backend       │
│   (nginx)       │───▶│   (React)       │───▶│   (FastAPI)     │
│                 │    │   Port: 80      │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │   Database      │
                                               │   (PostgreSQL)  │
                                               │   Port: 5432    │
                                               └─────────────────┘
```

## 📋 Resources Created

### Base Resources
- **Namespace**: Isolates the application
- **ConfigMaps**: Non-sensitive configuration
- **Secrets**: Database credentials and connection strings
- **PersistentVolumeClaim**: Database storage
- **Deployments**: Application workloads
- **Services**: Internal networking
- **HorizontalPodAutoscaler**: Auto-scaling
- **Ingress**: External access

### Environment Differences

| Resource | Development | Production |
|----------|-------------|------------|
| Backend Replicas | 1 | 5 |
| Frontend Replicas | 1 | 3 |
| HPA Min/Max | 1-3 | 5-20 |
| Database Storage | 1Gi | 20Gi |
| Memory Requests | 128Mi | 512Mi |
| TLS | Disabled | Enabled |

## 🔧 Configuration

### Environment Variables

Database configuration is handled via ConfigMaps and Secrets:

```yaml
# ConfigMap (non-sensitive)
POSTGRES_DB: notesdb
POSTGRES_USER: notesuser

# Secret (base64 encoded)
POSTGRES_PASSWORD: bm90ZXNwYXNzd29yZA==
DATABASE_URL: cG9zdGdyZXNxbCthc3luY3BnOi8v...
```

### Customization

Modify `k8s/overlays/{environment}/kustomization.yaml` to:
- Change replica counts
- Adjust resource limits
- Update image tags
- Modify environment variables

## 🌐 Access

### Development
```bash
# Port forward to access locally
kubectl port-forward service/dev-frontend-service 8080:80 -n notes-app-dev

# Access via ingress (if configured)
echo "127.0.0.1 notes.local" >> /etc/hosts
curl http://notes.local
```

### Production
```bash
# Access via configured domain
curl https://notes.yourdomain.com
```

## 📊 Monitoring

### Health Checks
All services have liveness and readiness probes:
- **Backend**: `GET /health`
- **Frontend**: `GET /`
- **Database**: `pg_isready`

### Scaling
```bash
# Manual scaling
kubectl scale deployment/dev-backend-deployment --replicas=5 -n notes-app-dev

# View HPA status
kubectl get hpa -n notes-app-dev
```

### Logs
```bash
# Backend logs
kubectl logs -f deployment/dev-backend-deployment -n notes-app-dev

# Frontend logs
kubectl logs -f deployment/dev-frontend-deployment -n notes-app-dev

# Database logs
kubectl logs -f deployment/dev-postgres-deployment -n notes-app-dev
```

## 🔒 Security

### Secrets Management
- Database credentials stored in Kubernetes Secrets
- TLS certificates managed by cert-manager (production)
- Non-root containers for security

### Network Policies
Consider implementing NetworkPolicies for additional security:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: notes-app-network-policy
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: notes-app
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app.kubernetes.io/name: notes-app
```

## 🚨 Troubleshooting

### Common Issues

1. **Images not found**
   ```bash
   # Check if images exist
   docker images | grep notes
   
   # Build images
   ./scripts/build-images.sh
   ```

2. **Pods stuck in Pending**
   ```bash
   # Check events
   kubectl describe pod <pod-name> -n <namespace>
   
   # Check node resources
   kubectl top nodes
   ```

3. **Database connection issues**
   ```bash
   # Check database pod
   kubectl logs deployment/dev-postgres-deployment -n notes-app-dev
   
   # Test connection
   kubectl exec -it deployment/dev-backend-deployment -n notes-app-dev -- curl localhost:8000/health
   ```

### Debug Commands
```bash
# Get all resources
kubectl get all -n notes-app-dev

# Describe problematic resources
kubectl describe deployment/dev-backend-deployment -n notes-app-dev

# Access pod shell
kubectl exec -it <pod-name> -n notes-app-dev -- /bin/bash

# Port forward for debugging
kubectl port-forward pod/<pod-name> 8000:8000 -n notes-app-dev
```

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Deploy to Kubernetes
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build and push images
      run: |
        ./scripts/build-images.sh ${{ github.sha }} ${{ secrets.REGISTRY }}
    
    - name: Deploy to Kubernetes
      run: |
        ./scripts/deploy-k8s.sh production
```

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kustomize Guide](https://kustomize.io/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [cert-manager](https://cert-manager.io/) (for TLS certificates) 