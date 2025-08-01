import time
import logging
from functools import wraps
from typing import Callable, Any
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
import os

# Prometheus Metrics
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

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

DATABASE_CONNECTIONS = Gauge(
    'database_connections_active',
    'Number of active database connections'
)

BUSINESS_METRICS = {
    'notes_created_total': Counter(
        'notes_created_total',
        'Total number of notes created'
    ),
    'notes_updated_total': Counter(
        'notes_updated_total',
        'Total number of notes updated'
    ),
    'notes_deleted_total': Counter(
        'notes_deleted_total',
        'Total number of notes deleted'
    ),
    'folders_created_total': Counter(
        'folders_created_total',
        'Total number of folders created'
    ),
    'folders_updated_total': Counter(
        'folders_updated_total',
        'Total number of folders updated'
    ),
    'folders_deleted_total': Counter(
        'folders_deleted_total',
        'Total number of folders deleted'
    )
}

logger = logging.getLogger(__name__)

def setup_tracing(service_name: str, jaeger_endpoint: str = None):
    """Setup OpenTelemetry tracing"""
    if not jaeger_endpoint:
        jaeger_endpoint = os.getenv("JAEGER_ENDPOINT", "http://jaeger:14268/api/traces")
    
    # Create resource
    resource = Resource.create({
        "service.name": service_name,
        "service.version": "1.0.0"
    })
    
    # Setup tracer provider
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer_provider = trace.get_tracer_provider()
    
    # Setup Jaeger exporter
    jaeger_exporter = JaegerExporter(
        endpoint=jaeger_endpoint,
    )
    
    # Add span processor
    span_processor = BatchSpanProcessor(jaeger_exporter)
    tracer_provider.add_span_processor(span_processor)
    
    return trace.get_tracer(service_name)

def setup_metrics():
    """Setup Prometheus metrics"""
    # Setup metrics provider
    resource = Resource.create({
        "service.name": os.getenv("SERVICE_NAME", "unknown-service"),
        "service.version": "1.0.0"
    })
    
    # Use PrometheusMetricReader
    metric_reader = PrometheusMetricReader()
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))
    
    return metrics.get_meter(__name__)

def instrument_fastapi_app(app, service_name: str):
    """Instrument FastAPI app with OpenTelemetry"""
    # Setup tracing
    tracer = setup_tracing(service_name)
    
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app, tracer_provider=trace.get_tracer_provider())
    
    # Instrument SQLAlchemy
    SQLAlchemyInstrumentor().instrument()
    
    # Instrument HTTPX (for API Gateway)
    HTTPXClientInstrumentor().instrument()
    
    return tracer

def track_request_metrics(func: Callable) -> Callable:
    """Decorator to track request metrics"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        # Extract request info
        request = kwargs.get('request') or (args[0] if args else None)
        method = getattr(request, 'method', 'unknown') if request else 'unknown'
        endpoint = getattr(request, 'url', {}).path if request else 'unknown'
        
        try:
            # Execute the function
            result = await func(*args, **kwargs)
            status = getattr(result, 'status_code', 200) if hasattr(result, 'status_code') else 200
            
            # Record metrics
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
            REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(time.time() - start_time)
            
            return result
            
        except Exception as e:
            # Record error metrics
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=500).inc()
            REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(time.time() - start_time)
            raise
            
    return wrapper

def track_business_metric(metric_name: str, labels: dict = None):
    """Track business metrics"""
    if metric_name in BUSINESS_METRICS:
        if labels:
            BUSINESS_METRICS[metric_name].labels(**labels).inc()
        else:
            BUSINESS_METRICS[metric_name].inc()

def get_metrics_handler():
    """Get Prometheus metrics handler for FastAPI"""
    async def metrics():
        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
    return metrics

class MetricsMiddleware:
    """Middleware for automatic request tracking"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        method = scope["method"]
        path = scope["path"]
        
        # Increment active connections
        ACTIVE_CONNECTIONS.inc()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status = message["status"]
                REQUEST_COUNT.labels(method=method, endpoint=path, status=status).inc()
                REQUEST_DURATION.labels(method=method, endpoint=path).observe(time.time() - start_time)
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            # Decrement active connections
            ACTIVE_CONNECTIONS.dec()

def create_custom_span(tracer, name: str, attributes: dict = None):
    """Create a custom span for tracing"""
    span = tracer.start_span(name)
    if attributes:
        for key, value in attributes.items():
            span.set_attribute(key, value)
    return span 