from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from contextlib import asynccontextmanager
from typing import List
from datetime import datetime

# Import shared components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

from database.models import Base, Folder, Note
from database.connection import db_manager, get_db_session
from schemas.base import FolderCreate, FolderUpdate, FolderRead, HealthCheck

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await db_manager.close()

app = FastAPI(
    title="Folders Service",
    description="Microservice for managing folder hierarchy",
    version="1.0.0",
    lifespan=lifespan
)

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
            service="folders-service",
            version="1.0.0"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )

@app.get("/folders", response_model=List[FolderRead])
async def get_folders(
    parent_id: int = None,
    session: AsyncSession = Depends(get_db_session)
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
            color=folder.color or "#6366f1",
            icon=folder.icon or "📁",
            parent_id=folder.parent_id,
            created_at=folder.created_at,
            updated_at=folder.updated_at
        )
        for folder in folders
    ]

@app.post("/folders", response_model=FolderRead, status_code=status.HTTP_201_CREATED)
async def create_folder(
    folder_data: FolderCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new folder"""
    # Check if parent exists (if specified)
    if folder_data.parent_id:
        parent = await session.get(Folder, folder_data.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent folder not found"
            )
    
    new_folder = Folder(
        name=folder_data.name,
        color=folder_data.color,
        icon=folder_data.icon,
        parent_id=folder_data.parent_id
    )
    
    session.add(new_folder)
    await session.commit()
    await session.refresh(new_folder)
    
    return FolderRead(
        id=new_folder.id,
        name=new_folder.name,
        color=new_folder.color or "#6366f1",
        icon=new_folder.icon or "📁",
        parent_id=new_folder.parent_id,
        created_at=new_folder.created_at,
        updated_at=new_folder.updated_at
    )

@app.get("/folders/{folder_id}", response_model=FolderRead)
async def get_folder(
    folder_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    """Get a specific folder by ID"""
    folder = await session.get(Folder, folder_id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )
    
    return FolderRead(
        id=folder.id,
        name=folder.name,
        color=folder.color or "#6366f1",
        icon=folder.icon or "📁",
        parent_id=folder.parent_id,
        created_at=folder.created_at,
        updated_at=folder.updated_at
    )

@app.put("/folders/{folder_id}", response_model=FolderRead)
async def update_folder(
    folder_id: int,
    folder_data: FolderUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    """Update a specific folder"""
    folder = await session.get(Folder, folder_id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )
    
    # Check if new parent exists (if specified)
    if folder_data.parent_id and folder_data.parent_id != folder.parent_id:
        if folder_data.parent_id == folder_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Folder cannot be its own parent"
            )
        parent = await session.get(Folder, folder_data.parent_id)
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
        color=folder.color or "#6366f1",
        icon=folder.icon or "📁",
        parent_id=folder.parent_id,
        created_at=folder.created_at,
        updated_at=folder.updated_at
    )

@app.delete("/folders/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    folder_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    """Delete a specific folder and move its notes to root"""
    folder = await session.get(Folder, folder_id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found"
        )
    
    # Move notes to root (set folder_id to None)
    result = await session.execute(
        select(Note).filter(Note.folder_id == folder_id)
    )
    notes_in_folder = result.scalars().all()
    for note in notes_in_folder:
        note.folder_id = None
    
    # Move child folders to root
    result = await session.execute(
        select(Folder).filter(Folder.parent_id == folder_id)
    )
    child_folders = result.scalars().all()
    for child in child_folders:
        child.parent_id = None
    
    await session.delete(folder)
    await session.commit()

@app.get("/folders/{folder_id}/children", response_model=List[FolderRead])
async def get_folder_children(
    folder_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    """Get all direct children of a folder"""
    # Verify parent folder exists
    parent = await session.get(Folder, folder_id)
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent folder not found"
        )
    
    result = await session.execute(
        select(Folder).filter(Folder.parent_id == folder_id)
    )
    children = result.scalars().all()
    
    return [
        FolderRead(
            id=folder.id,
            name=folder.name,
            color=folder.color or "#6366f1",
            icon=folder.icon or "📁",
            parent_id=folder.parent_id,
            created_at=folder.created_at,
            updated_at=folder.updated_at
        )
        for folder in children
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 