from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import httpx
import os
from datetime import datetime
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Notes App API Gateway",
    description="API Gateway for the Notes microservices application",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
NOTES_SERVICE_URL = os.getenv("NOTES_SERVICE_URL", "http://notes-service:8001")
FOLDERS_SERVICE_URL = os.getenv("FOLDERS_SERVICE_URL", "http://folders-service:8002")

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
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health", timeout=5.0)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            return False

service_registry = ServiceRegistry()

async def proxy_request(
    request: Request,
    service_name: str,
    path: str,
    method: str = "GET"
) -> JSONResponse:
    """Proxy request to the appropriate microservice"""
    import time
    start_time = time.time()
    
    service_url = service_registry.get_service_url(service_name)
    if not service_url:
        raise HTTPException(
            status_code=503,
            detail=f"Service {service_name} not available"
        )
    
    # Get request body
    body = None
    if method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
    
    # Get headers
    headers = dict(request.headers)
    # Remove host header to avoid conflicts
    headers.pop("host", None)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=f"{service_url}{path}",
                headers=headers,
                content=body,
                params=request.query_params,
                timeout=30.0
            )
            
            # Return response
            return JSONResponse(
                content=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
    except httpx.TimeoutException:
        logger.error(f"Timeout when calling {service_name} service")
        raise HTTPException(
            status_code=504,
            detail=f"Service {service_name} timeout"
        )
    except httpx.RequestError as e:
        logger.error(f"Error calling {service_name} service: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Service {service_name} unavailable"
        )

@app.get("/health")
async def gateway_health():
    """Health check for the API gateway"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "api-gateway",
        "version": "1.0.0",
        "services": {}
    }
    
    # Check downstream services
    for service_name in ["notes", "folders"]:
        is_healthy = await service_registry.health_check_service(service_name)
        health_status["services"][service_name] = {
            "status": "healthy" if is_healthy else "unhealthy",
            "url": service_registry.get_service_url(service_name)
        }
    
    # Overall status
    all_healthy = all(
        service["status"] == "healthy" 
        for service in health_status["services"].values()
    )
    
    if not all_healthy:
        health_status["status"] = "degraded"
    
    return health_status

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Notes App API Gateway",
        "version": "1.0.0",
        "services": {
            "notes": f"{NOTES_SERVICE_URL}/docs",
            "folders": f"{FOLDERS_SERVICE_URL}/docs"
        }
    }

# Notes service endpoints
@app.get("/api/notes")
async def get_notes(request: Request):
    return await proxy_request(request, "notes", "/notes")

@app.post("/api/notes")
async def create_note(request: Request):
    return await proxy_request(request, "notes", "/notes", "POST")

@app.get("/api/notes/{note_id}")
async def get_note(note_id: int, request: Request):
    return await proxy_request(request, "notes", f"/notes/{note_id}")

@app.put("/api/notes/{note_id}")
async def update_note(note_id: int, request: Request):
    return await proxy_request(request, "notes", f"/notes/{note_id}", "PUT")

@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: int, request: Request):
    return await proxy_request(request, "notes", f"/notes/{note_id}", "DELETE")

# Folders service endpoints
@app.get("/api/folders")
async def get_folders(request: Request):
    return await proxy_request(request, "folders", "/folders")

@app.post("/api/folders")
async def create_folder(request: Request):
    return await proxy_request(request, "folders", "/folders", "POST")

@app.get("/api/folders/{folder_id}")
async def get_folder(folder_id: int, request: Request):
    return await proxy_request(request, "folders", f"/folders/{folder_id}")

@app.put("/api/folders/{folder_id}")
async def update_folder(folder_id: int, request: Request):
    return await proxy_request(request, "folders", f"/folders/{folder_id}", "PUT")

@app.delete("/api/folders/{folder_id}")
async def delete_folder(folder_id: int, request: Request):
    return await proxy_request(request, "folders", f"/folders/{folder_id}", "DELETE")

@app.get("/api/folders/{folder_id}/children")
async def get_folder_children(folder_id: int, request: Request):
    return await proxy_request(request, "folders", f"/folders/{folder_id}/children")

@app.get("/api/services")
async def get_services():
    """Get available services"""
    return {
        "services": {
            name: {
                "url": url,
                "health": await service_registry.health_check_service(name)
            }
            for name, url in service_registry.services.items()
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 