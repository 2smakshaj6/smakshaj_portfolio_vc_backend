from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from .portfolio import PyObjectId

class Experience(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    portfolioId: PyObjectId
    role: str
    company: str
    location: str
    period: str
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    current: bool = False
    highlights: List[str] = []
    skills: List[str] = []
    order: int = 0
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ExperienceCreate(BaseModel):
    role: str
    company: str
    location: str
    period: str
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    current: bool = False
    highlights: List[str] = []
    skills: List[str] = []
    order: int = 0

class ExperienceUpdate(BaseModel):
    role: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    period: Optional[str] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    current: Optional[bool] = None
    highlights: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    order: Optional[int] = None
    updatedAt: datetime = Field(default_factory=datetime.utcnow)