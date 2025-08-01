from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.future import select
import os, dotenv
from pydantic import BaseModel
from typing import Optional, List, AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from auth import (
    User, UserCreate, UserRead, UserLogin, UserUpdate, Token,
    get_current_active_user, authenticate_user, create_user, get_user_by_id,
    create_access_token, create_refresh_token, verify_token, get_current_user,
    get_user_by_username, security, HTTPAuthorizationCredentials
)
from security import setup_security_middleware, validate_password_strength, validate_email, validate_username

dotenv.load_dotenv()

# Example SQL Server connection string for interactive AAD login:
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://notesuser:notespassword@localhost:5432/notesdb")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

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
    content = Column(Text, nullable=True)
    tags = Column(String(250), nullable=True)
    color = Column(String(20), nullable=True)
    folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    folder = relationship("Folder", back_populates="notes")

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
    created_at: datetime
    updated_at: datetime

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
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, note: "Note"):
        tags_list = note.tags.split(',') if note.tags else []
        return cls(
            id=note.id, 
            title=note.title, 
            content=note.content, 
            tags=tags_list, 
            color=note.color or "", 
            folder_id=note.folder_id,
            created_at=note.created_at,
            updated_at=note.updated_at
        )

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="Notes API with Authentication",
    description="A secure note-taking API with user authentication",
    version="2.0.0",
    lifespan=lifespan
)

# Setup security middleware
setup_security_middleware(app)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

# Create a dependency that provides both session and current user
async def get_current_user_with_session(
    session: AsyncSession = Depends(get_session),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> tuple[AsyncSession, User]:
    # Get current user with the session
    current_user = await get_current_user(credentials, session)
    return session, current_user

# Authentication endpoints
@app.post("/auth/register", response_model=UserRead, status_code=201)
async def register(user_data: UserCreate, session: AsyncSession = Depends(get_session)):
    """Register a new user"""
    # Validate input data
    if not validate_username(user_data.username):
        raise HTTPException(
            status_code=400,
            detail="Username must be 3-20 characters long and contain only letters, numbers, and underscores"
        )
    
    if not validate_email(user_data.email):
        raise HTTPException(
            status_code=400,
            detail="Invalid email format"
        )
    
    if not validate_password_strength(user_data.password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long and contain uppercase, lowercase, digit, and special character"
        )
    
    return await create_user(session, user_data)

@app.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin, session: AsyncSession = Depends(get_session)):
    """Login and get access token"""
    user = await authenticate_user(session, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/auth/refresh", response_model=Token)
async def refresh_token(refresh_token: str, session: AsyncSession = Depends(get_session)):
    """Refresh access token using refresh token"""
    try:
        payload = verify_token(refresh_token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        user = await get_user_by_username(session, username)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        access_token = create_access_token(data={"sub": user.username})
        new_refresh_token = create_refresh_token(data={"sub": user.username})
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@app.get("/auth/me", response_model=UserRead)
async def get_current_user_info(session_and_user: tuple[AsyncSession, User] = Depends(get_current_user_with_session)):
    """Get current user information"""
    session, current_user = session_and_user
    return current_user

@app.put("/auth/me", response_model=UserRead)
async def update_current_user(
    user_update: UserUpdate,
    session_and_user: tuple[AsyncSession, User] = Depends(get_current_user_with_session)
):
    """Update current user information"""
    session, current_user = session_and_user
    
    if user_update.email is not None:
        if not validate_email(user_update.email):
            raise HTTPException(status_code=400, detail="Invalid email format")
        current_user.email = user_update.email
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.is_active is not None:
        current_user.is_active = user_update.is_active
    
    await session.commit()
    await session.refresh(current_user)
    return current_user

# Public endpoints
@app.get("/")
async def root():
    return {"message": "FastAPI Note-taking backend is running!", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and Kubernetes"""
    try:
        # Test database connection
        async with async_session() as session:
            await session.execute(select(1))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

# Protected endpoints - require authentication
@app.get("/notes", response_model=List[NoteRead])
async def get_notes(
    session_and_user: tuple[AsyncSession, User] = Depends(get_current_user_with_session)
):
    """Get all notes for the current user"""
    session, current_user = session_and_user
    result = await session.execute(
        select(Note).filter(Note.user_id == current_user.id)
    )
    notes = result.scalars().all()
    return [NoteRead.from_orm(n) for n in notes]

@app.post("/notes", response_model=NoteRead, status_code=201)
async def create_note(
    note: NoteCreate,
    session_and_user: tuple[AsyncSession, User] = Depends(get_current_user_with_session)
):
    """Create a new note for the current user"""
    session, current_user = session_and_user
    
    # Verify folder belongs to user if folder_id is provided
    if note.folder_id:
        folder_result = await session.execute(
            select(Folder).filter(Folder.id == note.folder_id, Folder.user_id == current_user.id)
        )
        if not folder_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Folder not found or access denied")
    
    new_note = Note(
        title=note.title,
        content=note.content,
        tags=(','.join(note.tags)) if note.tags else None,
        color=note.color,
        folder_id=note.folder_id,
        user_id=current_user.id
    )
    session.add(new_note)
    await session.commit()
    await session.refresh(new_note)
    return NoteRead.from_orm(new_note)

@app.get("/notes/{note_id}", response_model=NoteRead)
async def get_note(
    note_id: int,
    session_and_user: tuple[AsyncSession, User] = Depends(get_current_user_with_session)
):
    """Get a specific note by ID (user must own the note)"""
    session, current_user = session_and_user
    result = await session.execute(
        select(Note).filter(Note.id == note_id, Note.user_id == current_user.id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteRead.from_orm(note)

@app.put("/notes/{note_id}", response_model=NoteRead)
async def update_note(
    note_id: int,
    note: NoteUpdate,
    session_and_user: tuple[AsyncSession, User] = Depends(get_current_user_with_session)
):
    """Update a note (user must own the note)"""
    session, current_user = session_and_user
    result = await session.execute(
        select(Note).filter(Note.id == note_id, Note.user_id == current_user.id)
    )
    db_note = result.scalar_one_or_none()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Verify folder belongs to user if folder_id is provided
    if note.folder_id:
        folder_result = await session.execute(
            select(Folder).filter(Folder.id == note.folder_id, Folder.user_id == current_user.id)
        )
        if not folder_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Folder not found or access denied")
    
    db_note.title = note.title
    db_note.content = note.content
    db_note.tags = ','.join(note.tags) if note.tags else None
    db_note.color = note.color
    db_note.folder_id = note.folder_id
    await session.commit()
    await session.refresh(db_note)
    return NoteRead.from_orm(db_note)

@app.delete("/notes/{note_id}", status_code=204)
async def delete_note(
    note_id: int,
    session_and_user: tuple[AsyncSession, User] = Depends(get_current_user_with_session)
):
    """Delete a note (user must own the note)"""
    session, current_user = session_and_user
    result = await session.execute(
        select(Note).filter(Note.id == note_id, Note.user_id == current_user.id)
    )
    db_note = result.scalar_one_or_none()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    await session.delete(db_note)
    await session.commit()
    return None

# Folder endpoints - require authentication
@app.get("/folders", response_model=List[FolderRead])
async def get_folders(
    session_and_user: tuple[AsyncSession, User] = Depends(get_current_user_with_session)
):
    """Get all folders for the current user"""
    session, current_user = session_and_user
    result = await session.execute(
        select(Folder).filter(Folder.user_id == current_user.id)
    )
    folders = result.scalars().all()
    return [
        FolderRead(
            id=f.id,
            name=f.name,
            color=f.color or "",
            icon=f.icon or "",
            parent_id=f.parent_id,
            created_at=f.created_at,
            updated_at=f.updated_at
        ) for f in folders
    ]

@app.post("/folders", response_model=FolderRead, status_code=201)
async def create_folder(
    folder: FolderCreate,
    session_and_user: tuple[AsyncSession, User] = Depends(get_current_user_with_session)
):
    """Create a new folder for the current user"""
    session, current_user = session_and_user
    
    # Verify parent folder belongs to user if parent_id is provided
    if folder.parent_id:
        parent_result = await session.execute(
            select(Folder).filter(Folder.id == folder.parent_id, Folder.user_id == current_user.id)
        )
        if not parent_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Parent folder not found or access denied")
    
    new_folder = Folder(
        name=folder.name,
        color=folder.color,
        icon=folder.icon,
        parent_id=folder.parent_id,
        user_id=current_user.id
    )
    session.add(new_folder)
    await session.commit()
    await session.refresh(new_folder)
    return FolderRead(
        id=new_folder.id,
        name=new_folder.name,
        color=new_folder.color or "",
        icon=new_folder.icon or "",
        parent_id=new_folder.parent_id,
        created_at=new_folder.created_at,
        updated_at=new_folder.updated_at
    )

@app.put("/folders/{folder_id}", response_model=FolderRead)
async def update_folder(
    folder_id: int,
    folder: FolderUpdate,
    session_and_user: tuple[AsyncSession, User] = Depends(get_current_user_with_session)
):
    """Update a folder (user must own the folder)"""
    session, current_user = session_and_user
    result = await session.execute(
        select(Folder).filter(Folder.id == folder_id, Folder.user_id == current_user.id)
    )
    db_folder = result.scalar_one_or_none()
    if not db_folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # Verify parent folder belongs to user if parent_id is provided
    if folder.parent_id:
        parent_result = await session.execute(
            select(Folder).filter(Folder.id == folder.parent_id, Folder.user_id == current_user.id)
        )
        if not parent_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Parent folder not found or access denied")
    
    db_folder.name = folder.name
    db_folder.color = folder.color
    db_folder.icon = folder.icon
    db_folder.parent_id = folder.parent_id
    await session.commit()
    await session.refresh(db_folder)
    return FolderRead(
        id=db_folder.id,
        name=db_folder.name,
        color=db_folder.color or "",
        icon=db_folder.icon or "",
        parent_id=db_folder.parent_id,
        created_at=db_folder.created_at,
        updated_at=db_folder.updated_at
    )

@app.delete("/folders/{folder_id}", status_code=204)
async def delete_folder(
    folder_id: int,
    session_and_user: tuple[AsyncSession, User] = Depends(get_current_user_with_session)
):
    """Delete a folder (user must own the folder)"""
    session, current_user = session_and_user
    result = await session.execute(
        select(Folder).filter(Folder.id == folder_id, Folder.user_id == current_user.id)
    )
    db_folder = result.scalar_one_or_none()
    if not db_folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # Update notes in this folder to have no folder (move to root)
    notes_result = await session.execute(
        select(Note).filter(Note.folder_id == folder_id, Note.user_id == current_user.id)
    )
    notes_in_folder = notes_result.scalars().all()
    for note in notes_in_folder:
        note.folder_id = None
    
    await session.delete(db_folder)
    await session.commit()
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
