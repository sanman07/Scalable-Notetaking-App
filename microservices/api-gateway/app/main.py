from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import httpx
import os
from datetime import datetime
from typing import Dict, Any
import logging

# Import shared monitoring components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

from utils.monitoring import (
    instrument_fastapi_app, MetricsMiddleware, track_business_metric,
    create_custom_span
)
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Notes App API Gateway",
    description="API Gateway for the Notes microservices application",
    version="1.0.0"
)

# Setup monitoring
os.environ["SERVICE_NAME"] = "api-gateway"
tracer = instrument_fastapi_app(app, "api-gateway")

# Add metrics middleware
app.add_middleware(MetricsMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
NOTES_SERVICE_URL = os.getenv("NOTES_SERVICE_URL", "http://localhost:8001")
FOLDERS_SERVICE_URL = os.getenv("FOLDERS_SERVICE_URL", "http://localhost:8002")

class ServiceRegistry:
    """Simple service registry for microservices"""
    
    def __init__(self):
        self.services = {
            "notes": NOTES_SERVICE_URL,
            "folders": FOLDERS_SERVICE_URL
        }
    
    def get_service_url(self, service_name: str) -> str:
        return self.services.get(service_name)
    
    async def health_check_service(self, service_name: str) -> bool:
        """Check if a service is healthy"""
        url = self.get_service_url(service_name)
        if not url:
            return False
        
        with tracer.start_as_current_span(f"health_check_{service_name}") as span:
            span.set_attribute("service_name", service_name)
            span.set_attribute("service_url", url)
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{url}/health", timeout=5.0)
                    is_healthy = response.status_code == 200
                    span.set_attribute("is_healthy", is_healthy)
                    return is_healthy
            except Exception as e:
                logger.error(f"Health check failed for {service_name}: {e}")
                span.set_attribute("is_healthy", False)
                span.set_attribute("error", str(e))
                return False

service_registry = ServiceRegistry()

async def proxy_request(
    request: Request,
    service_name: str,
    path: str,
    method: str = "GET"
) -> JSONResponse:
    """Proxy request to the appropriate microservice"""
    with tracer.start_as_current_span(f"proxy_to_{service_name}") as span:
        span.set_attribute("service_name", service_name)
        span.set_attribute("path", path)
        span.set_attribute("method", method)
        
        service_url = service_registry.get_service_url(service_name)
        if not service_url:
            span.set_attribute("service_available", False)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service {service_name} not available"
            )
        
        span.set_attribute("service_available", True)
        url = f"{service_url}{path}"
        span.set_attribute("target_url", url)
        
        # Extract request data
        headers = dict(request.headers)
        # Remove host header to avoid conflicts
        headers.pop("host", None)
        
        try:
            async with httpx.AsyncClient() as client:
                if method.upper() == "GET":
                    response = await client.get(
                        url,
                        headers=headers,
                        params=request.query_params,
                        timeout=30.0
                    )
                elif method.upper() == "POST":
                    body = await request.body()
                    response = await client.post(
                        url,
                        headers=headers,
                        content=body,
                        timeout=30.0
                    )
                elif method.upper() == "PUT":
                    body = await request.body()
                    response = await client.put(
                        url,
                        headers=headers,
                        content=body,
                        timeout=30.0
                    )
                elif method.upper() == "DELETE":
                    response = await client.delete(
                        url,
                        headers=headers,
                        timeout=30.0
                    )
                else:
                    span.set_attribute("unsupported_method", True)
                    raise HTTPException(
                        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                        detail=f"Method {method} not supported"
                    )
                
                span.set_attribute("response_status", response.status_code)
                span.set_attribute("response_size", len(response.content))
                
                # Return response
                return JSONResponse(
                    content=response.json() if response.content else {},
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
                
        except httpx.TimeoutException:
            span.set_attribute("timeout", True)
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=f"Service {service_name} timeout"
            )
        except httpx.RequestError as e:
            logger.error(f"Request error to {service_name}: {e}")
            span.set_attribute("request_error", True)
            span.set_attribute("error", str(e))
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service {service_name} unavailable"
            )
        except Exception as e:
            logger.error(f"Unexpected error proxying to {service_name}: {e}")
            span.set_attribute("unexpected_error", True)
            span.set_attribute("error", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Gateway health check
@app.get("/health")
async def gateway_health():
    """Health check for the API Gateway"""
    with tracer.start_as_current_span("gateway_health_check") as span:
        service_health = {}
        
        for service_name in service_registry.services.keys():
            service_health[service_name] = await service_registry.health_check_service(service_name)
        
        all_healthy = all(service_health.values())
        span.set_attribute("all_services_healthy", all_healthy)
        span.set_attribute("healthy_services", sum(service_health.values()))
        span.set_attribute("total_services", len(service_health))
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.utcnow(),
            "service": "api-gateway",
            "version": "1.0.0",
            "services": service_health
        }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Notes App API Gateway",
        "version": "1.0.0",
        "services": list(service_registry.services.keys())
    }

# Notes service routes
@app.get("/api/notes")
async def get_notes(request: Request):
    return await proxy_request(request, "notes", "/notes", "GET")

@app.post("/api/notes")
async def create_note(request: Request):
    return await proxy_request(request, "notes", "/notes", "POST")

@app.get("/api/notes/{note_id}")
async def get_note(note_id: int, request: Request):
    return await proxy_request(request, "notes", f"/notes/{note_id}", "GET")

@app.put("/api/notes/{note_id}")
async def update_note(note_id: int, request: Request):
    return await proxy_request(request, "notes", f"/notes/{note_id}", "PUT")

@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: int, request: Request):
    return await proxy_request(request, "notes", f"/notes/{note_id}", "DELETE")

# Folders service routes
@app.get("/api/folders")
async def get_folders(request: Request):
    return await proxy_request(request, "folders", "/folders", "GET")

@app.post("/api/folders")
async def create_folder(request: Request):
    return await proxy_request(request, "folders", "/folders", "POST")

@app.get("/api/folders/{folder_id}")
async def get_folder(folder_id: int, request: Request):
    return await proxy_request(request, "folders", f"/folders/{folder_id}", "GET")

@app.put("/api/folders/{folder_id}")
async def update_folder(folder_id: int, request: Request):
    return await proxy_request(request, "folders", f"/folders/{folder_id}", "PUT")

@app.delete("/api/folders/{folder_id}")
async def delete_folder(folder_id: int, request: Request):
    return await proxy_request(request, "folders", f"/folders/{folder_id}", "DELETE")

@app.get("/api/folders/{folder_id}/children")
async def get_folder_children(folder_id: int, request: Request):
    return await proxy_request(request, "folders", f"/folders/{folder_id}/children", "GET")

# Service discovery endpoint
@app.get("/api/services")
async def get_services():
    """Get available services and their health status"""
    with tracer.start_as_current_span("service_discovery") as span:
        services_info = {}
        
        for service_name, service_url in service_registry.services.items():
            is_healthy = await service_registry.health_check_service(service_name)
            services_info[service_name] = {
                "url": service_url,
                "healthy": is_healthy,
                "status": "up" if is_healthy else "down"
            }
        
        span.set_attribute("total_services", len(services_info))
        span.set_attribute("healthy_services", sum(1 for s in services_info.values() if s["healthy"]))
        
        return {
            "services": services_info,
            "timestamp": datetime.utcnow()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 