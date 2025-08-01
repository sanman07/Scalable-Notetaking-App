from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# Note Schemas
class NoteBase(BaseSchema):
    title: str
    content: Optional[str] = ""
    tags: Optional[List[str]] = []
    color: Optional[str] = "#6366f1"
    folder_id: Optional[int] = None

class NoteCreate(NoteBase):
    pass

class NoteUpdate(NoteBase):
    pass

class NoteRead(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime

# Folder Schemas
class FolderBase(BaseSchema):
    name: str
    color: Optional[str] = "#6366f1"
    icon: Optional[str] = "📁"
    parent_id: Optional[int] = None

class FolderCreate(FolderBase):
    pass

class FolderUpdate(FolderBase):
    pass

class FolderRead(FolderBase):
    id: int
    created_at: datetime
    updated_at: datetime

# Health Check Schema
class HealthCheck(BaseSchema):
    status: str
    timestamp: datetime
    service: str
    version: str 