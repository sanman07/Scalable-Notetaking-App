# Scalable Microservices Note-taking App

## Overview
A simple, scalable note-taking app built with:
- **Frontend:** React (Vite + TypeScript)
- **Backend:** Python (FastAPI)
- **Database:** PostgreSQL
- **Orchestration:** Docker, Kubernetes, Helm
- **Ingress:** NGINX Ingress Controller
- **Secrets:** Kubernetes Secrets

## Structure
```
frontend/   # React + Vite app
backend/    # FastAPI app
helm/       # Helm charts for K8s deployment
  frontend/
  backend/
  db/
db/        # PostgreSQL init scripts
```

## Getting Started
- See each service directory for setup instructions.
- Use Docker and Kubernetes for orchestration.
- Deploy with Helm charts.