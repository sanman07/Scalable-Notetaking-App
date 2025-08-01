from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import declarative_base, relationship
from contextlib import asynccontextmanager
from typing import List, Optional
from pydantic import BaseModel
import json
from datetime import datetime
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://notesuser:notespassword@database:5432/notesdb")
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Database models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=True)
    tags = Column(String(250), nullable=True)
    color = Column(String(20), nullable=True)
    folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic models
class NoteCreate(BaseModel):
    title: str
    content: Optional[str] = ""
    tags: Optional[List[str]] = []
    color: Optional[str] = ""
    folder_id: Optional[int] = None

class NoteUpdate(BaseModel):
    title: str
    content: Optional[str] = ""
    tags: Optional[List[str]] = []
    color: Optional[str] = ""
    folder_id: Optional[int] = None

class NoteRead(BaseModel):
    id: int
    title: str
    content: Optional[str] = ""
    tags: List[str] = []
    color: Optional[str] = ""
    folder_id: Optional[int] = None
    user_id: int
    created_at: datetime
    updated_at: datetime

class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    service: str
    version: str
    database: Optional[str] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(
    title="Notes Service",
    description="Microservice for managing notes",
    version="1.0.0",
    lifespan=lifespan
)

async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

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

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        async with AsyncSessionLocal() as session:
            await session.execute(select(1))
        
        return HealthCheck(
            status="healthy",
            timestamp=datetime.utcnow(),
            service="notes-service",
            version="1.0.0",
            database="connected"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )

@app.get("/notes", response_model=List[NoteRead])
async def get_notes(
    folder_id: int = None,
    session: AsyncSession = Depends(get_async_session)
):
    """Get all notes, optionally filtered by folder"""
    query = select(Note)
    if folder_id is not None:
        query = query.filter(Note.folder_id == folder_id)
    
    result = await session.execute(query)
    notes = result.scalars().all()
    
    return [
        NoteRead(
            id=note.id,
            title=note.title,
            content=note.content,
            tags=serialize_note_tags(note),
            color=note.color or "",
            folder_id=note.folder_id,
            user_id=note.user_id,
            created_at=note.created_at,
            updated_at=note.updated_at
        )
        for note in notes
    ]

@app.post("/notes", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_data: NoteCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """Create a new note"""
    new_note = Note(
        title=note_data.title,
        content=note_data.content,
        tags=deserialize_note_tags(note_data.tags),
        color=note_data.color,
        folder_id=note_data.folder_id,
        user_id=1  # TODO: Get from authentication
    )
    
    session.add(new_note)
    await session.commit()
    await session.refresh(new_note)
    
    return NoteRead(
        id=new_note.id,
        title=new_note.title,
        content=new_note.content,
        tags=serialize_note_tags(new_note),
        color=new_note.color or "",
        folder_id=new_note.folder_id,
        user_id=new_note.user_id,
        created_at=new_note.created_at,
        updated_at=new_note.updated_at
    )

@app.get("/notes/{note_id}", response_model=NoteRead)
async def get_note(
    note_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Get a specific note by ID"""
    result = await session.execute(select(Note).filter(Note.id == note_id))
    note = result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return NoteRead(
        id=note.id,
        title=note.title,
        content=note.content,
        tags=serialize_note_tags(note),
        color=note.color or "",
        folder_id=note.folder_id,
        user_id=note.user_id,
        created_at=note.created_at,
        updated_at=note.updated_at
    )

@app.put("/notes/{note_id}", response_model=NoteRead)
async def update_note(
    note_id: int,
    note_data: NoteUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    """Update a note"""
    result = await session.execute(select(Note).filter(Note.id == note_id))
    note = result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Update fields
    note.title = note_data.title
    note.content = note_data.content
    note.tags = deserialize_note_tags(note_data.tags)
    note.color = note_data.color
    note.folder_id = note_data.folder_id
    
    await session.commit()
    await session.refresh(note)
    
    return NoteRead(
        id=note.id,
        title=note.title,
        content=note.content,
        tags=serialize_note_tags(note),
        color=note.color or "",
        folder_id=note.folder_id,
        user_id=note.user_id,
        created_at=note.created_at,
        updated_at=note.updated_at
    )

@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Delete a note"""
    result = await session.execute(select(Note).filter(Note.id == note_id))
    note = result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    await session.delete(note)
    await session.commit()
    
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 