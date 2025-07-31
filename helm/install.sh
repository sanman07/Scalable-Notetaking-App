#!/bin/bash

# Notes App Helm Chart Installation Script
set -e

RELEASE_NAME=${1:-"notes-app"}
NAMESPACE=${2:-"default"}
CHART_PATH="./notes-app"

echo "🚀 Installing Notes App Helm Chart..."
echo "Release Name: $RELEASE_NAME"
echo "Namespace: $NAMESPACE"
echo "Chart Path: $CHART_PATH"
echo ""

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    echo "❌ Helm is not installed. Please install Helm first."
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Create namespace if it doesn't exist
if [ "$NAMESPACE" != "default" ]; then
    echo "📦 Creating namespace: $NAMESPACE"
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
fi

# Update dependencies
echo "📥 Updating Helm dependencies..."
helm dependency update "$CHART_PATH"

# Lint the chart
echo "🔍 Linting Helm chart..."
helm lint "$CHART_PATH" --strict

# Install or upgrade the chart
echo "⚡ Installing/Upgrading Helm chart..."
helm upgrade --install "$RELEASE_NAME" "$CHART_PATH" \
    --namespace "$NAMESPACE" \
    --wait \
    --timeout 10m

echo ""
echo "✅ Notes App has been successfully deployed!"
echo ""
echo "📋 Next steps:"
echo "1. Check the status: kubectl get pods -n $NAMESPACE -l app.kubernetes.io/instance=$RELEASE_NAME"
echo "2. View the notes: helm get notes $RELEASE_NAME -n $NAMESPACE"
echo "3. Run tests: helm test $RELEASE_NAME -n $NAMESPACE"
echo ""
echo "🌐 Access the application:"
echo "   kubectl port-forward -n $NAMESPACE svc/$RELEASE_NAME-notes-app-frontend 8080:80"
echo "   Then visit: http://localhost:8080"
