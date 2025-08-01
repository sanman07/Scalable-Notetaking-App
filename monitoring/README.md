# Notes App - Monitoring & Observability

This directory contains the complete monitoring and observability stack for the Notes microservices application.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Notes Service │
│   (React)       │───▶│   Port: 8000    │───▶│   Port: 8001    │
│   Port: 80      │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Folders Service│    │   Database      │
                       │   Port: 8002    │    │   PostgreSQL    │
                       │                 │    │   Port: 5432    │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
            ┌──────────────────────────────────────────────────────┐
            │                Monitoring Stack                      │
            │                                                      │
            │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
            │  │ Prometheus  │  │   Grafana   │  │   Jaeger    │  │
            │  │ Port: 9090  │  │ Port: 3000  │  │ Port: 16686 │  │
            │  └─────────────┘  └─────────────┘  └─────────────┘  │
            │                                                      │
            │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
            │  │    Loki     │  │  cAdvisor   │  │Node Exporter│  │
            │  │ Port: 3100  │  │ Port: 8080  │  │ Port: 9100  │  │
            │  └─────────────┘  └─────────────┘  └─────────────┘  │
            └──────────────────────────────────────────────────────┘
```

## 📊 Monitoring Components

### Core Application Services
- **Frontend**: React application served by Nginx
- **API Gateway**: FastAPI gateway with request routing and monitoring
- **Notes Service**: Microservice for notes CRUD operations
- **Folders Service**: Microservice for folder hierarchy management
- **Database**: PostgreSQL database

### Monitoring & Observability
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Data visualization and dashboards
- **Jaeger**: Distributed tracing
- **Loki**: Log aggregation
- **Promtail**: Log collection agent

### Infrastructure Monitoring
- **cAdvisor**: Container metrics
- **Node Exporter**: System-level metrics
- **PostgreSQL Exporter**: Database metrics

## 🚀 Quick Start

### Start Complete Stack
```bash
./start-monitoring.sh
```

### Manual Docker Compose
```bash
cd monitoring
docker-compose -f docker-compose.monitoring.yml up --build -d
```

## 🌐 Access Points

### Application
- **Frontend**: http://localhost
- **API Gateway**: http://localhost:8000
- **Notes Service**: http://localhost:8001
- **Folders Service**: http://localhost:8002

### Monitoring & Observability
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin123)
- **Jaeger UI**: http://localhost:16686

### Infrastructure Monitoring
- **PostgreSQL Exporter**: http://localhost:9187/metrics
- **Node Exporter**: http://localhost:9100/metrics
- **cAdvisor**: http://localhost:8080
- **Loki**: http://localhost:3100

### API Documentation
- **Gateway Docs**: http://localhost:8000/docs
- **Notes Docs**: http://localhost:8001/docs
- **Folders Docs**: http://localhost:8002/docs

### Metrics Endpoints
- **Gateway Metrics**: http://localhost:8000/metrics
- **Notes Metrics**: http://localhost:8001/metrics
- **Folders Metrics**: http://localhost:8002/metrics

## 📈 Metrics & KPIs

### Application Metrics
- **Request Rate**: Requests per second by service
- **Response Time**: P95 latency for each endpoint
- **Error Rate**: 5xx errors as percentage of total requests
- **Active Connections**: Current concurrent connections

### Business Metrics
- **Notes Created**: Total notes created over time
- **Notes Updated**: Total notes updated over time
- **Notes Deleted**: Total notes deleted over time
- **Folders Created**: Total folders created over time

### Infrastructure Metrics
- **CPU Usage**: Container and system CPU utilization
- **Memory Usage**: Container and system memory consumption
- **Disk Usage**: Filesystem space utilization
- **Network I/O**: Network traffic by container

### Database Metrics
- **Connection Count**: Active database connections
- **Query Performance**: Slow query detection
- **Database Size**: Table and index sizes
- **Lock Status**: Database lock monitoring

## 📊 Dashboards

### Pre-configured Dashboards
1. **Notes App Overview**: Main application dashboard
2. **Service Performance**: Detailed service metrics
3. **Infrastructure Overview**: System resource monitoring
4. **Database Performance**: PostgreSQL specific metrics

### Creating Custom Dashboards
1. Open Grafana: http://localhost:3000
2. Login with admin/admin123
3. Click "+" → "Dashboard"
4. Add panels with PromQL queries

### Sample PromQL Queries
```promql
# Request rate by service
sum(rate(http_requests_total[5m])) by (job)

# Error rate
sum(rate(http_requests_total{status=~"5.."}[5m])) by (job) / sum(rate(http_requests_total[5m])) by (job)

# Response time P95
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, job))

# Memory usage
container_memory_usage_bytes{name=~".*-service"} / 1024 / 1024
```

## 🚨 Alerting

### Alert Rules Location
- **File**: `prometheus/config/alert_rules.yml`
- **Web UI**: http://localhost:9090/alerts

### Pre-configured Alerts
- **ServiceDown**: Service unavailable for >1 minute
- **HighErrorRate**: Error rate >10% for >2 minutes
- **HighResponseTime**: P95 latency >500ms for >5 minutes
- **DatabaseConnectionFailure**: DB unreachable for >1 minute
- **HighMemoryUsage**: Memory usage >80% for >5 minutes
- **HighCPUUsage**: CPU usage >80% for >5 minutes
- **DiskSpaceRunningLow**: Disk space <10%

### Setting Up Alertmanager (Optional)
```yaml
# Add to docker-compose.monitoring.yml
alertmanager:
  image: prom/alertmanager:v0.25.0
  ports:
    - "9093:9093"
  volumes:
    - ./alertmanager/config.yml:/etc/alertmanager/config.yml
```

## 🔍 Distributed Tracing

### Jaeger Features
- **Service Map**: Visual representation of service dependencies
- **Trace Search**: Find traces by service, operation, or tags
- **Performance Analysis**: Identify bottlenecks and latency issues
- **Error Tracking**: Trace error propagation across services

### Trace Information
- **Request Flow**: Complete request journey through microservices
- **Timing**: Detailed timing for each operation
- **Tags**: Custom attributes for filtering and analysis
- **Logs**: Associated log entries for each span

### Custom Spans
```python
# Example custom span
with tracer.start_as_current_span("database_operation") as span:
    span.set_attribute("table", "notes")
    span.set_attribute("operation", "select")
    # ... database operation
    span.set_attribute("rows_returned", len(results))
```

## 📝 Log Aggregation

### Loki Setup
- **Port**: 3100
- **Storage**: Local filesystem
- **Retention**: 30 days (configurable)

### Log Sources
- **Application Logs**: FastAPI application logs
- **Container Logs**: Docker container stdout/stderr
- **System Logs**: Host system logs via Promtail

### Querying Logs
```logql
# All logs from notes-service
{container_name="notes-service"}

# Error logs only
{container_name="notes-service"} |= "ERROR"

# Logs with specific trace ID
{container_name="notes-service"} |= "trace_id=abc123"
```

## 🛠️ Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check service status
docker-compose -f docker-compose.monitoring.yml ps

# View service logs
docker-compose -f docker-compose.monitoring.yml logs <service-name>

# Restart specific service
docker-compose -f docker-compose.monitoring.yml restart <service-name>
```

#### Metrics Not Appearing
1. Verify `/metrics` endpoints are accessible
2. Check Prometheus targets: http://localhost:9090/targets
3. Verify network connectivity between containers
4. Check Prometheus configuration syntax

#### Traces Not Showing
1. Verify Jaeger is running: http://localhost:16686
2. Check service configuration for Jaeger endpoint
3. Verify OpenTelemetry instrumentation is working
4. Check for network connectivity issues

#### Grafana Dashboard Issues
1. Verify Prometheus datasource configuration
2. Check PromQL query syntax
3. Verify metric names and labels
4. Check time range and refresh intervals

### Performance Optimization

#### Prometheus
```yaml
# Adjust scrape intervals
global:
  scrape_interval: 30s  # Reduce for less load
  evaluation_interval: 30s
```

#### Grafana
```ini
# Increase query timeout
[database]
query_timeout = 30s

# Enable gzip compression
[server]
enable_gzip = true
```

### Health Checks
```bash
# Check all service health
curl http://localhost:8000/health  # API Gateway
curl http://localhost:8001/health  # Notes Service
curl http://localhost:8002/health  # Folders Service
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:3000/api/health  # Grafana
```

## 📋 Configuration Files

### Key Configuration Files
```
monitoring/
├── prometheus/
│   └── config/
│       ├── prometheus.yml      # Prometheus configuration
│       └── alert_rules.yml     # Alerting rules
├── grafana/
│   └── config/
│       ├── grafana.ini         # Grafana configuration
│       ├── datasources.yml     # Datasource configuration
│       └── dashboards/         # Dashboard definitions
├── docker-compose.monitoring.yml  # Complete stack
└── start-monitoring.sh        # Startup script
```

### Environment Variables
```bash
# Service Names
SERVICE_NAME=notes-service|folders-service|api-gateway

# Jaeger Configuration
JAEGER_ENDPOINT=http://jaeger:14268/api/traces

# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
```

## 🔒 Security Considerations

### Grafana Security
- Change default admin password
- Enable HTTPS in production
- Configure proper user roles
- Secure datasource connections

### Prometheus Security
- Secure metrics endpoints
- Use authentication for external access
- Configure proper firewall rules
- Enable TLS for external connections

### Jaeger Security
- Secure UI access
- Configure proper network policies
- Use authentication for production
- Encrypt trace data in transit

## 📚 Additional Resources

### Documentation
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)

### Best Practices
- Monitor the monitors (meta-monitoring)
- Set up proper alerting thresholds
- Use meaningful metric names and labels
- Implement proper log structure
- Regular backup of monitoring configurations

### Scaling Considerations
- Use remote storage for Prometheus in production
- Implement Grafana clustering for high availability
- Use distributed tracing sampling for high-volume services
- Consider log retention policies for cost optimization 