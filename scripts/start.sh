#!/bin/bash

# Notes App Docker Startup Script

echo "🚀 Starting Notes App with Docker..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build and start all services
echo "📦 Building and starting containers..."
docker-compose up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

if docker-compose ps | grep -q "Up (healthy)"; then
    echo "✅ All services are running!"
    echo ""
    echo "🌐 Access your Notes App:"
    echo "   Frontend: http://localhost"
    echo "   Backend API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
else
    echo "❌ Some services may not be healthy. Check logs:"
    echo "   docker-compose logs"
fi 