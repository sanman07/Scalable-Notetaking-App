from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from contextlib import asynccontextmanager
from typing import List
import json
from datetime import datetime
import os

# Import shared components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

from database.models import Base, Note
from database.connection import db_manager, get_db_session
from schemas.base import NoteCreate, NoteUpdate, NoteRead, HealthCheck
from utils.monitoring import (
    instrument_fastapi_app, MetricsMiddleware, track_business_metric,
    get_metrics_handler, create_custom_span
)
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await db_manager.close()

app = FastAPI(
    title="Notes Service",
    description="Microservice for managing notes",
    version="1.0.0",
    lifespan=lifespan
)

# Setup monitoring
os.environ["SERVICE_NAME"] = "notes-service"
tracer = instrument_fastapi_app(app, "notes-service")

# Add metrics middleware
app.add_middleware(MetricsMiddleware)

def serialize_note_tags(note: Note) -> List[str]:
    """Convert tags string to list"""
    if not note.tags:
        return []
    try:
        # Try to parse as JSON first
        return json.loads(note.tags)
    except (json.JSONDecodeError, TypeError):
        # Fallback to comma-separated
        return [tag.strip() for tag in note.tags.split(',') if tag.strip()]

def deserialize_note_tags(tags: List[str]) -> str:
    """Convert tags list to JSON string"""
    return json.dumps(tags) if tags else ""

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        async with db_manager.async_session() as session:
            await session.execute(select(1))
        
        return HealthCheck(
            status="healthy",
            timestamp=datetime.utcnow(),
            service="notes-service",
            version="1.0.0"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )

@app.get("/notes", response_model=List[NoteRead])
async def get_notes(
    folder_id: int = None,
    session: AsyncSession = Depends(get_db_session)
):
    """Get all notes, optionally filtered by folder"""
    with tracer.start_as_current_span("get_notes") as span:
        span.set_attribute("folder_id", folder_id or "all")
        
        query = select(Note)
        if folder_id is not None:
            query = query.filter(Note.folder_id == folder_id)
        
        result = await session.execute(query)
        notes = result.scalars().all()
        
        span.set_attribute("notes_count", len(notes))
        
        # Convert notes to response model
        return [
            NoteRead(
                id=note.id,
                title=note.title,
                content=note.content or "",
                tags=serialize_note_tags(note),
                color=note.color or "#6366f1",
                folder_id=note.folder_id,
                created_at=note.created_at,
                updated_at=note.updated_at
            )
            for note in notes
        ]

@app.post("/notes", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_data: NoteCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new note"""
    with tracer.start_as_current_span("create_note") as span:
        span.set_attribute("note_title", note_data.title)
        span.set_attribute("folder_id", note_data.folder_id or "none")
        
        new_note = Note(
            title=note_data.title,
            content=note_data.content,
            tags=deserialize_note_tags(note_data.tags),
            color=note_data.color,
            folder_id=note_data.folder_id
        )
        
        session.add(new_note)
        await session.commit()
        await session.refresh(new_note)
        
        # Track business metric
        track_business_metric('notes_created_total')
        
        span.set_attribute("note_id", new_note.id)
        
        return NoteRead(
            id=new_note.id,
            title=new_note.title,
            content=new_note.content or "",
            tags=serialize_note_tags(new_note),
            color=new_note.color or "#6366f1",
            folder_id=new_note.folder_id,
            created_at=new_note.created_at,
            updated_at=new_note.updated_at
        )

@app.get("/notes/{note_id}", response_model=NoteRead)
async def get_note(
    note_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    """Get a specific note by ID"""
    with tracer.start_as_current_span("get_note") as span:
        span.set_attribute("note_id", note_id)
        
        note = await session.get(Note, note_id)
        if not note:
            span.set_attribute("note_found", False)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        
        span.set_attribute("note_found", True)
        span.set_attribute("note_title", note.title)
        
        return NoteRead(
            id=note.id,
            title=note.title,
            content=note.content or "",
            tags=serialize_note_tags(note),
            color=note.color or "#6366f1",
            folder_id=note.folder_id,
            created_at=note.created_at,
            updated_at=note.updated_at
        )

@app.put("/notes/{note_id}", response_model=NoteRead)
async def update_note(
    note_id: int,
    note_data: NoteUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    """Update a specific note"""
    with tracer.start_as_current_span("update_note") as span:
        span.set_attribute("note_id", note_id)
        span.set_attribute("new_title", note_data.title)
        
        note = await session.get(Note, note_id)
        if not note:
            span.set_attribute("note_found", False)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        
        span.set_attribute("note_found", True)
        span.set_attribute("old_title", note.title)
        
        # Update fields
        note.title = note_data.title
        note.content = note_data.content
        note.tags = deserialize_note_tags(note_data.tags)
        note.color = note_data.color
        note.folder_id = note_data.folder_id
        
        await session.commit()
        await session.refresh(note)
        
        # Track business metric
        track_business_metric('notes_updated_total')
        
        return NoteRead(
            id=note.id,
            title=note.title,
            content=note.content or "",
            tags=serialize_note_tags(note),
            color=note.color or "#6366f1",
            folder_id=note.folder_id,
            created_at=note.created_at,
            updated_at=note.updated_at
        )

@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    """Delete a specific note"""
    with tracer.start_as_current_span("delete_note") as span:
        span.set_attribute("note_id", note_id)
        
        note = await session.get(Note, note_id)
        if not note:
            span.set_attribute("note_found", False)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        
        span.set_attribute("note_found", True)
        span.set_attribute("note_title", note.title)
        
        await session.delete(note)
        await session.commit()
        
        # Track business metric
        track_business_metric('notes_deleted_total')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 