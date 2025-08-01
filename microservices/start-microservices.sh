#!/bin/bash

# Microservices Startup Script

set -e

echo "🚀 Starting Notes App Microservices..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose first."
    exit 1
fi

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📦 Building and starting microservices..."
docker-compose up --build -d

echo "⏳ Waiting for services to be ready..."
sleep 20

echo "🔍 Checking service health..."

# Function to check service health
check_service_health() {
    local service_url=$1
    local service_name=$2
    
    for i in {1..10}; do
        if curl -s "$service_url/health" > /dev/null; then
            echo "✅ $service_name is healthy"
            return 0
        fi
        echo "⏳ Waiting for $service_name... (attempt $i/10)"
        sleep 5
    done
    echo "❌ $service_name failed to start"
    return 1
}

# Check all services
GATEWAY_HEALTHY=false
NOTES_HEALTHY=false
FOLDERS_HEALTHY=false

if check_service_health "http://localhost:8000" "API Gateway"; then
    GATEWAY_HEALTHY=true
fi

if check_service_health "http://localhost:8001" "Notes Service"; then
    NOTES_HEALTHY=true
fi

if check_service_health "http://localhost:8002" "Folders Service"; then
    FOLDERS_HEALTHY=true
fi

echo ""
echo "📊 Service Status:"
docker-compose ps

if $GATEWAY_HEALTHY && $NOTES_HEALTHY && $FOLDERS_HEALTHY; then
    echo ""
    echo "✅ All microservices are running successfully!"
    echo ""
    echo "🌐 Access Points:"
    echo "   Frontend:        http://localhost"
    echo "   API Gateway:     http://localhost:8000"
    echo "   Notes Service:   http://localhost:8001"
    echo "   Folders Service: http://localhost:8002"
    echo ""
    echo "📚 API Documentation:"
    echo "   Gateway Docs:    http://localhost:8000/docs"
    echo "   Notes Docs:      http://localhost:8001/docs"
    echo "   Folders Docs:    http://localhost:8002/docs"
    echo ""
    echo "🔍 Health Checks:"
    echo "   Gateway Health:  http://localhost:8000/health"
    echo "   Notes Health:    http://localhost:8001/health"
    echo "   Folders Health:  http://localhost:8002/health"
    echo "   Service Status:  http://localhost:8000/api/services"
else
    echo "❌ Some services are not healthy. Check logs with:"
    echo "   docker-compose logs"
fi 