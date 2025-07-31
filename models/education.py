from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from .portfolio import PyObjectId

class Education(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    portfolioId: PyObjectId
    degree: str
    school: str
    location: str
    period: str
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    gpa: Optional[str] = None
    coursework: List[str] = []
    order: int = 0
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class EducationCreate(BaseModel):
    degree: str
    school: str
    location: str
    period: str
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    gpa: Optional[str] = None
    coursework: List[str] = []
    order: int = 0

class EducationUpdate(BaseModel):
    degree: Optional[str] = None
    school: Optional[str] = None
    location: Optional[str] = None
    period: Optional[str] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    gpa: Optional[str] = None
    coursework: Optional[List[str]] = None
    order: Optional[int] = None
    updatedAt: datetime = Field(default_factory=datetime.utcnow)