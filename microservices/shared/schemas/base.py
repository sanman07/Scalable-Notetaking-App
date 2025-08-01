"""
Base schemas for microservices
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

class UserBase(BaseSchema):
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseSchema):
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserRead(UserBase):
    id: int
    created_at: datetime

class FolderBase(BaseSchema):
    name: str
    color: Optional[str] = ""
    icon: Optional[str] = "📁"
    parent_id: Optional[int] = None

class FolderCreate(FolderBase):
    pass

class FolderUpdate(FolderBase):
    pass

class FolderRead(FolderBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

class NoteBase(BaseSchema):
    title: str
    content: Optional[str] = ""
    tags: Optional[List[str]] = []
    color: Optional[str] = ""
    folder_id: Optional[int] = None

class NoteCreate(NoteBase):
    pass

class NoteUpdate(NoteBase):
    pass

class NoteRead(NoteBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

class Token(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserLogin(BaseSchema):
    username: str
    password: str

class HealthCheck(BaseSchema):
    status: str
    timestamp: datetime
    service: str
    version: str
    database: Optional[str] = None

class ErrorResponse(BaseSchema):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = datetime.utcnow() 