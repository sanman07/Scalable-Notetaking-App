#!/bin/bash

# Deploy Notes App to Kubernetes

set -e

# Default values
ENVIRONMENT=${1:-development}
ACTION=${2:-apply}

# Validate environment
if [[ "$ENVIRONMENT" != "development" && "$ENVIRONMENT" != "production" ]]; then
    echo "❌ Invalid environment. Use 'development' or 'production'"
    exit 1
fi

# Validate action
if [[ "$ACTION" != "apply" && "$ACTION" != "delete" ]]; then
    echo "❌ Invalid action. Use 'apply' or 'delete'"
    exit 1
fi

echo "🚀 ${ACTION^}ing Notes App to Kubernetes ($ENVIRONMENT)..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl first."
    exit 1
fi

# Check if kustomize is available
if ! command -v kustomize &> /dev/null; then
    echo "❌ kustomize not found. Please install kustomize first."
    exit 1
fi

# Check cluster connection
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Unable to connect to Kubernetes cluster. Please check your kubeconfig."
    exit 1
fi

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Apply or delete resources
cd "$PROJECT_ROOT"
kubectl $ACTION -k "k8s/overlays/$ENVIRONMENT"

if [[ "$ACTION" == "apply" ]]; then
    echo "⏳ Waiting for deployments to be ready..."
    
    # Set namespace based on environment
    if [[ "$ENVIRONMENT" == "development" ]]; then
        NAMESPACE="notes-app-dev"
    else
        NAMESPACE="notes-app-prod"
    fi
    
    # Wait for deployments
    kubectl rollout status deployment/dev-backend-deployment -n $NAMESPACE --timeout=300s
    kubectl rollout status deployment/dev-frontend-deployment -n $NAMESPACE --timeout=300s
    kubectl rollout status deployment/dev-postgres-deployment -n $NAMESPACE --timeout=300s
    
    echo "✅ Deployment completed successfully!"
    echo ""
    echo "📊 Resource Status:"
    kubectl get all -n $NAMESPACE
    echo ""
    echo "🌐 Access Information:"
    echo "   Namespace: $NAMESPACE"
    
    # Get ingress info if available
    if kubectl get ingress -n $NAMESPACE &> /dev/null; then
        echo "   Ingress:"
        kubectl get ingress -n $NAMESPACE
    fi
    
    echo ""
    echo "💡 Useful commands:"
    echo "   View logs: kubectl logs -f deployment/dev-backend-deployment -n $NAMESPACE"
    echo "   Port forward: kubectl port-forward service/dev-frontend-service 8080:80 -n $NAMESPACE"
    echo "   Scale backend: kubectl scale deployment/dev-backend-deployment --replicas=5 -n $NAMESPACE"
    
else
    echo "✅ Resources deleted successfully!"
fi 