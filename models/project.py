from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from .portfolio import PyObjectId

class Project(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    portfolioId: PyObjectId
    title: str
    status: str
    icon: str
    description: str
    tech: List[str] = []
    github: bool = False
    githubUrl: Optional[str] = None
    demo: bool = False
    demoUrl: Optional[str] = None
    featured: bool = False
    order: int = 0
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ProjectCreate(BaseModel):
    title: str
    status: str
    icon: str
    description: str
    tech: List[str] = []
    github: bool = False
    githubUrl: Optional[str] = None
    demo: bool = False
    demoUrl: Optional[str] = None
    featured: bool = False
    order: int = 0

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    tech: Optional[List[str]] = None
    github: Optional[bool] = None
    githubUrl: Optional[str] = None
    demo: Optional[bool] = None
    demoUrl: Optional[str] = None
    featured: Optional[bool] = None
    order: Optional[int] = None
    updatedAt: datetime = Field(default_factory=datetime.utcnow)