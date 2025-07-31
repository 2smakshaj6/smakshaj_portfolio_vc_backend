from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from .portfolio import PyObjectId

class Skill(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    portfolioId: PyObjectId
    category: str
    icon: str
    skills: List[str] = []
    order: int = 0
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class SkillCreate(BaseModel):
    category: str
    icon: str
    skills: List[str] = []
    order: int = 0

class SkillUpdate(BaseModel):
    category: Optional[str] = None
    icon: Optional[str] = None
    skills: Optional[List[str]] = None
    order: Optional[int] = None
    updatedAt: datetime = Field(default_factory=datetime.utcnow)