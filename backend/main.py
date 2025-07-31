from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.future import select
import os, dotenv
from pydantic import BaseModel
from typing import Optional, List, AsyncGenerator
from contextlib import asynccontextmanager

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

    @classmethod
    def from_orm(cls, note: "Note"):
        tags_list = note.tags.split(',') if note.tags else []
        return cls(id=note.id, title=note.title, content=note.content, tags=tags_list, color=note.color or "", folder_id=note.folder_id)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

@app.get("/")
async def root():
    return {"message": "FastAPI Note-taking backend is running!"}

@app.get("/notes", response_model=List[NoteRead])
async def get_notes(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Note))
    notes = result.scalars().all()
    return [NoteRead.from_orm(n) for n in notes]

@app.post("/notes", response_model=NoteRead, status_code=201)
async def create_note(note: NoteCreate, session: AsyncSession = Depends(get_session)):
    new_note = Note(title=note.title, content=note.content, tags=(','.join(note.tags)) if note.tags else None, color=note.color, folder_id=note.folder_id)
    session.add(new_note)
    await session.commit()
    await session.refresh(new_note)
    return NoteRead.from_orm(new_note)

@app.get("/notes/{note_id}", response_model=NoteRead)
async def get_note(note_id: int, session: AsyncSession = Depends(get_session)):
    note = await session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteRead.from_orm(note)

@app.put("/notes/{note_id}", response_model=NoteRead)
async def update_note(note_id: int, note: NoteUpdate, session: AsyncSession = Depends(get_session)):
    db_note = await session.get(Note, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    db_note.title = note.title
    db_note.content = note.content
    db_note.tags = ','.join(note.tags) if note.tags else None
    db_note.color = note.color
    db_note.folder_id = note.folder_id
    await session.commit()
    await session.refresh(db_note)
    return NoteRead.from_orm(db_note)

@app.delete("/notes/{note_id}", status_code=204)
async def delete_note(note_id: int, session: AsyncSession = Depends(get_session)):
    db_note = await session.get(Note, note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    await session.delete(db_note)
    await session.commit()
    return None

# Folder endpoints
@app.get("/folders", response_model=List[FolderRead])
async def get_folders(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Folder))
    folders = result.scalars().all()
    return [FolderRead(id=f.id, name=f.name, color=f.color or "", icon=f.icon or "", parent_id=f.parent_id) for f in folders]

@app.post("/folders", response_model=FolderRead, status_code=201)
async def create_folder(folder: FolderCreate, session: AsyncSession = Depends(get_session)):
    new_folder = Folder(name=folder.name, color=folder.color, icon=folder.icon, parent_id=folder.parent_id)
    session.add(new_folder)
    await session.commit()
    await session.refresh(new_folder)
    return FolderRead(id=new_folder.id, name=new_folder.name, color=new_folder.color or "", icon=new_folder.icon or "", parent_id=new_folder.parent_id)

@app.put("/folders/{folder_id}", response_model=FolderRead)
async def update_folder(folder_id: int, folder: FolderUpdate, session: AsyncSession = Depends(get_session)):
    db_folder = await session.get(Folder, folder_id)
    if not db_folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    db_folder.name = folder.name
    db_folder.color = folder.color
    db_folder.icon = folder.icon
    db_folder.parent_id = folder.parent_id
    await session.commit()
    await session.refresh(db_folder)
    return FolderRead(id=db_folder.id, name=db_folder.name, color=db_folder.color or "", icon=db_folder.icon or "", parent_id=db_folder.parent_id)

@app.delete("/folders/{folder_id}", status_code=204)
async def delete_folder(folder_id: int, session: AsyncSession = Depends(get_session)):
    db_folder = await session.get(Folder, folder_id)
    if not db_folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # Update notes in this folder to have no folder (move to root)
    result = await session.execute(select(Note).filter(Note.folder_id == folder_id))
    notes_in_folder = result.scalars().all()
    for note in notes_in_folder:
        note.folder_id = None
    
    await session.delete(db_folder)
    await session.commit()
    return None

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
