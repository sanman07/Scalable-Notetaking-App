from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import declarative_base, relationship
from contextlib import asynccontextmanager
from typing import List, Optional
from pydantic import BaseModel
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

class Folder(Base):
    __tablename__ = "folders"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(20), nullable=True)
    icon = Column(String(10), nullable=True, default="📁")
    parent_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    notes = relationship("Note", back_populates="folder")
    parent = relationship("Folder", remote_side=[id], back_populates="children")
    children = relationship("Folder", back_populates="parent")

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    content = Column(String, nullable=True)
    tags = Column(String(250), nullable=True)
    color = Column(String(20), nullable=True)
    folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    folder = relationship("Folder", back_populates="notes")

# Pydantic models
class FolderCreate(BaseModel):
    name: str
    color: Optional[str] = ""
    icon: Optional[str] = "📁"
    parent_id: Optional[int] = None

class FolderUpdate(BaseModel):
    name: str
    color: Optional[str] = ""
    icon: Optional[str] = "📁"
    parent_id: Optional[int] = None

class FolderRead(BaseModel):
    id: int
    name: str
    color: Optional[str] = ""
    icon: Optional[str] = "📁"
    parent_id: Optional[int] = None
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
    title="Folders Service",
    description="Microservice for managing folder hierarchy",
    version="1.0.0",
    lifespan=lifespan
)

async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

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
            service="folders-service",
            version="1.0.0",
            database="connected"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )

@app.get("/folders", response_model=List[FolderRead])
async def get_folders(
    parent_id: int = None,
    session: AsyncSession = Depends(get_async_session)
):
    """Get all folders, optionally filtered by parent"""
    query = select(Folder)
    if parent_id is not None:
        query = query.filter(Folder.parent_id == parent_id)
    
    result = await session.execute(query)
    folders = result.scalars().all()
    
    return [
        FolderRead(
            id=folder.id,
            name=folder.name,
            color=folder.color or "",
            icon=folder.icon or "📁",
            parent_id=folder.parent_id,
            user_id=folder.user_id,
            created_at=folder.created_at,
            updated_at=folder.updated_at
        )
        for folder in folders
    ]

@app.post("/folders", response_model=FolderRead, status_code=status.HTTP_201_CREATED)
async def create_folder(
    folder_data: FolderCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """Create a new folder"""
    # Check if parent exists (if specified)
    if folder_data.parent_id:
        result = await session.execute(select(Folder).filter(Folder.id == folder_data.parent_id))
        parent = result.scalar_one_or_none()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent folder not found"
            )
    
    new_folder = Folder(
        name=folder_data.name,
        color=folder_data.color,
        icon=folder_data.icon,
        parent_id=folder_data.parent_id,
        user_id=1  # TODO: Get from authentication
    )
    
    session.add(new_folder)
    await session.commit()
    await session.refresh(new_folder)
    
    return FolderRead(
        id=new_folder.id,
        name=new_folder.name,
        color=new_folder.color or "",
        icon=new_folder.icon or "📁",
        parent_id=new_folder.parent_id,
        user_id=new_folder.user_id,
        created_at=new_folder.created_at,
        updated_at=new_folder.updated_at
    )

@app.get("/folders/{folder_id}", response_model=FolderRead)
async def get_folder(
    folder_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Get a specific folder by ID"""
    result = await session.execute(select(Folder).filter(Folder.id == folder_id))
    folder = result.scalar_one_or_none()
    
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    return FolderRead(
        id=folder.id,
        name=folder.name,
        color=folder.color or "",
        icon=folder.icon or "📁",
        parent_id=folder.parent_id,
        user_id=folder.user_id,
        created_at=folder.created_at,
        updated_at=folder.updated_at
    )

@app.put("/folders/{folder_id}", response_model=FolderRead)
async def update_folder(
    folder_id: int,
    folder_data: FolderUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    """Update a folder"""
    result = await session.execute(select(Folder).filter(Folder.id == folder_id))
    folder = result.scalar_one_or_none()
    
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # Check if new parent exists (if specified)
    if folder_data.parent_id:
        parent_result = await session.execute(select(Folder).filter(Folder.id == folder_data.parent_id))
        parent = parent_result.scalar_one_or_none()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent folder not found"
            )
    
    # Update fields
    folder.name = folder_data.name
    folder.color = folder_data.color
    folder.icon = folder_data.icon
    folder.parent_id = folder_data.parent_id
    
    await session.commit()
    await session.refresh(folder)
    
    return FolderRead(
        id=folder.id,
        name=folder.name,
        color=folder.color or "",
        icon=folder.icon or "📁",
        parent_id=folder.parent_id,
        user_id=folder.user_id,
        created_at=folder.created_at,
        updated_at=folder.updated_at
    )

@app.delete("/folders/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    folder_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Delete a folder"""
    result = await session.execute(select(Folder).filter(Folder.id == folder_id))
    folder = result.scalar_one_or_none()
    
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # Move notes in this folder to root (no folder)
    notes_result = await session.execute(select(Note).filter(Note.folder_id == folder_id))
    notes_in_folder = notes_result.scalars().all()
    for note in notes_in_folder:
        note.folder_id = None
    
    # Delete the folder
    await session.delete(folder)
    await session.commit()
    
    return None

@app.get("/folders/{folder_id}/children", response_model=List[FolderRead])
async def get_folder_children(
    folder_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Get all child folders of a specific folder"""
    # Check if parent folder exists
    parent_result = await session.execute(select(Folder).filter(Folder.id == folder_id))
    parent = parent_result.scalar_one_or_none()
    
    if not parent:
        raise HTTPException(status_code=404, detail="Parent folder not found")
    
    # Get child folders
    children_result = await session.execute(select(Folder).filter(Folder.parent_id == folder_id))
    children = children_result.scalars().all()
    
    return [
        FolderRead(
            id=child.id,
            name=child.name,
            color=child.color or "",
            icon=child.icon or "📁",
            parent_id=child.parent_id,
            user_id=child.user_id,
            created_at=child.created_at,
            updated_at=child.updated_at
        )
        for child in children
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 