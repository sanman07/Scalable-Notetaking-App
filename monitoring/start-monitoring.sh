#!/bin/bash

# Notes App Monitoring Stack Startup Script

set -e

echo "🚀 Starting Notes App with Complete Monitoring Stack..."

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

echo "📦 Building and starting all services with monitoring..."
docker-compose -f docker-compose.monitoring.yml up --build -d

echo "⏳ Waiting for services to be ready..."
sleep 30

echo "🔍 Checking service health..."

# Function to check service health
check_service_health() {
    local service_url=$1
    local service_name=$2
    
    for i in {1..15}; do
        if curl -s "$service_url" > /dev/null; then
            echo "✅ $service_name is healthy"
            return 0
        fi
        echo "⏳ Waiting for $service_name... (attempt $i/15)"
        sleep 10
    done
    echo "❌ $service_name failed to start"
    return 1
}

# Check all services
SERVICES_HEALTHY=true

# Core application services
if ! check_service_health "http://localhost:8000/health" "API Gateway"; then
    SERVICES_HEALTHY=false
fi

if ! check_service_health "http://localhost:8001/health" "Notes Service"; then
    SERVICES_HEALTHY=false
fi

if ! check_service_health "http://localhost:8002/health" "Folders Service"; then
    SERVICES_HEALTHY=false
fi

# Monitoring services
if ! check_service_health "http://localhost:9090/-/healthy" "Prometheus"; then
    SERVICES_HEALTHY=false
fi

if ! check_service_health "http://localhost:3000/api/health" "Grafana"; then
    SERVICES_HEALTHY=false
fi

if ! check_service_health "http://localhost:16686" "Jaeger"; then
    SERVICES_HEALTHY=false
fi

echo ""
echo "📊 Service Status:"
docker-compose -f docker-compose.monitoring.yml ps

if $SERVICES_HEALTHY; then
    echo ""
    echo "✅ All services are running successfully!"
    echo ""
    echo "🌐 Application Access Points:"
    echo "   Frontend:              http://localhost"
    echo "   API Gateway:           http://localhost:8000"
    echo "   Notes Service:         http://localhost:8001"
    echo "   Folders Service:       http://localhost:8002"
    echo ""
    echo "📊 Monitoring & Observability:"
    echo "   Prometheus:            http://localhost:9090"
    echo "   Grafana:               http://localhost:3000 (admin/admin123)"
    echo "   Jaeger UI:             http://localhost:16686"
    echo ""
    echo "📈 Infrastructure Monitoring:"
    echo "   PostgreSQL Exporter:   http://localhost:9187/metrics"
    echo "   Node Exporter:         http://localhost:9100/metrics"
    echo "   cAdvisor:              http://localhost:8080"
    echo "   Loki:                  http://localhost:3100"
    echo ""
    echo "📚 API Documentation:"
    echo "   Gateway Docs:          http://localhost:8000/docs"
    echo "   Notes Docs:            http://localhost:8001/docs"
    echo "   Folders Docs:          http://localhost:8002/docs"
    echo ""
    echo "🔍 Metrics Endpoints:"
    echo "   Gateway Metrics:       http://localhost:8000/metrics"
    echo "   Notes Metrics:         http://localhost:8001/metrics"
    echo "   Folders Metrics:       http://localhost:8002/metrics"
    echo ""
    echo "🎯 Quick Start Monitoring:"
    echo "   1. Open Grafana: http://localhost:3000"
    echo "   2. Login with admin/admin123"
    echo "   3. Import dashboard from: monitoring/grafana/dashboards/"
    echo "   4. View traces in Jaeger: http://localhost:16686"
    echo "   5. Query metrics in Prometheus: http://localhost:9090"
    echo ""
    echo "🚨 Alerting:"
    echo "   Alert rules are configured in: monitoring/prometheus/config/alert_rules.yml"
    echo "   View active alerts: http://localhost:9090/alerts"
    echo ""
    echo "📝 Log Aggregation:"
    echo "   Loki logs: accessible via Grafana Explore"
    echo "   Container logs: collected by Promtail"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   View service logs: docker-compose -f docker-compose.monitoring.yml logs <service-name>"
    echo "   Restart service: docker-compose -f docker-compose.monitoring.yml restart <service-name>"
    echo ""
    echo "🛑 To stop all services:"
    echo "   docker-compose -f docker-compose.monitoring.yml down"
else
    echo ""
    echo "❌ Some services are not healthy. Check logs with:"
    echo "   docker-compose -f docker-compose.monitoring.yml logs"
    echo ""
    echo "🔧 Common troubleshooting steps:"
    echo "   1. Check if all ports are available"
    echo "   2. Ensure Docker has enough resources allocated"
    echo "   3. Wait longer for services to initialize"
    echo "   4. Check individual service logs"
fi

echo ""
echo "📋 Environment Summary:"
echo "   • React Frontend with Nginx"
echo "   • FastAPI Microservices (Notes, Folders)"
echo "   • API Gateway with request routing"
echo "   • PostgreSQL Database"
echo "   • Prometheus metrics collection"
echo "   • Grafana visualization"
echo "   • Jaeger distributed tracing"
echo "   • Loki log aggregation"
echo "   • cAdvisor container monitoring"
echo "   • Node Exporter system metrics"
echo "   • PostgreSQL Exporter database metrics" 