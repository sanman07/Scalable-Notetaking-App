"""
Monitoring utilities for microservices
Provides Prometheus metrics and OpenTelemetry tracing
"""

import os
from typing import Optional

# Try to import monitoring libraries, with fallbacks
try:
    import prometheus_client
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Don't print warning here to avoid spam

try:
    import opentelemetry
    from opentelemetry import trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.exporter.prometheus import PrometheusExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.resources import Resource
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    # Don't print warning here to avoid spam

# Metrics (only if prometheus_client is available)
if PROMETHEUS_AVAILABLE:
    # Request metrics
    REQUEST_COUNT = Counter(
        'http_requests_total',
        'Total HTTP requests',
        ['method', 'endpoint', 'status']
    )
    
    REQUEST_DURATION = Histogram(
        'http_request_duration_seconds',
        'HTTP request duration in seconds',
        ['method', 'endpoint']
    )
    
    # Database metrics
    DB_CONNECTION_GAUGE = Gauge(
        'database_connections_active',
        'Number of active database connections'
    )
    
    DB_QUERY_DURATION = Histogram(
        'database_query_duration_seconds',
        'Database query duration in seconds',
        ['operation']
    )
    
    # Business metrics
    NOTES_CREATED = Counter(
        'notes_created_total',
        'Total number of notes created'
    )
    
    FOLDERS_CREATED = Counter(
        'folders_created_total',
        'Total number of folders created'
    )
    
    USERS_REGISTERED = Counter(
        'users_registered_total',
        'Total number of users registered'
    )
else:
    # Dummy metrics for when prometheus_client is not available
    class DummyMetric:
        def inc(self, *args, **kwargs): pass
        def observe(self, *args, **kwargs): pass
        def set(self, *args, **kwargs): pass
    
    REQUEST_COUNT = DummyMetric()
    REQUEST_DURATION = DummyMetric()
    DB_CONNECTION_GAUGE = DummyMetric()
    DB_QUERY_DURATION = DummyMetric()
    NOTES_CREATED = DummyMetric()
    FOLDERS_CREATED = DummyMetric()
    USERS_REGISTERED = DummyMetric()

def setup_monitoring(app, service_name: str):
    """Setup monitoring for a FastAPI application"""
    
    # Setup OpenTelemetry tracing
    if OPENTELEMETRY_AVAILABLE:
        setup_tracing(service_name)
        FastAPIInstrumentor.instrument_app(app)
    
    # Setup Prometheus metrics endpoint
    if PROMETHEUS_AVAILABLE:
        from prometheus_client import make_asgi_app
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)

def setup_tracing(service_name: str):
    """Setup OpenTelemetry tracing"""
    if not OPENTELEMETRY_AVAILABLE:
        return
    
    # Create tracer provider
    resource = Resource.create({"service.name": service_name})
    tracer_provider = TracerProvider(resource=resource)
    
    # Setup Jaeger exporter
    jaeger_endpoint = os.getenv("JAEGER_ENDPOINT", "http://localhost:14268/api/traces")
    jaeger_exporter = JaegerExporter(
        collector_endpoint=jaeger_endpoint
    )
    
    # Add span processor
    tracer_provider.add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )
    
    # Set global tracer provider
    trace.set_tracer_provider(tracer_provider)

def instrument_database(engine):
    """Instrument SQLAlchemy engine for monitoring"""
    if OPENTELEMETRY_AVAILABLE:
        SQLAlchemyInstrumentor().instrument(engine=engine)

def instrument_http_client():
    """Instrument HTTP client for monitoring"""
    if OPENTELEMETRY_AVAILABLE:
        HTTPXClientInstrumentor().instrument()

def record_request_metrics(method: str, endpoint: str, status_code: int, duration: float):
    """Record HTTP request metrics"""
    REQUEST_COUNT.inc(method=method, endpoint=endpoint, status=str(status_code))
    REQUEST_DURATION.observe(duration, method=method, endpoint=endpoint)

def record_database_metrics(operation: str, duration: float):
    """Record database operation metrics"""
    DB_QUERY_DURATION.observe(duration, operation=operation)

def record_business_metrics(metric_type: str, value: int = 1):
    """Record business metrics"""
    if metric_type == "notes_created":
        NOTES_CREATED.inc(value)
    elif metric_type == "folders_created":
        FOLDERS_CREATED.inc(value)
    elif metric_type == "users_registered":
        USERS_REGISTERED.inc(value)

def update_db_connection_count(count: int):
    """Update database connection count"""
    DB_CONNECTION_GAUGE.set(count) 