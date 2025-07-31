#!/bin/bash

# Build Docker images for Kubernetes deployment

set -e

echo "🏗️  Building Docker images for Kubernetes..."

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default values
TAG=${1:-latest}
REGISTRY=${2:-""}

# If registry is provided, add trailing slash
if [[ -n "$REGISTRY" ]]; then
    REGISTRY="${REGISTRY%/}/"
fi

echo "📦 Building backend image..."
cd "$PROJECT_ROOT"
docker build -t "${REGISTRY}notes-backend:${TAG}" -f backend/Dockerfile backend/

echo "📦 Building frontend image..."
docker build -t "${REGISTRY}notes-frontend:${TAG}" -f frontend/Dockerfile frontend/

echo "✅ Images built successfully!"
echo "   Backend: ${REGISTRY}notes-backend:${TAG}"
echo "   Frontend: ${REGISTRY}notes-frontend:${TAG}"

# If registry is provided, push images
if [[ -n "$REGISTRY" ]]; then
    echo "🚀 Pushing images to registry..."
    docker push "${REGISTRY}notes-backend:${TAG}"
    docker push "${REGISTRY}notes-frontend:${TAG}"
    echo "✅ Images pushed successfully!"
fi

echo "💡 To deploy to Kubernetes:"
echo "   Development: kubectl apply -k k8s/overlays/development"
echo "   Production:  kubectl apply -k k8s/overlays/production" 