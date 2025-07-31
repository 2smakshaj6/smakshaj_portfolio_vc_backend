from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId
from .portfolio import PyObjectId

class Certification(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    portfolioId: PyObjectId
    name: str
    issuer: Optional[str] = None
    issueDate: Optional[datetime] = None
    expiryDate: Optional[datetime] = None
    credentialId: Optional[str] = None
    credentialUrl: Optional[str] = None
    image: Optional[str] = None
    order: int = 0
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CertificationCreate(BaseModel):
    name: str
    issuer: Optional[str] = None
    issueDate: Optional[datetime] = None
    expiryDate: Optional[datetime] = None
    credentialId: Optional[str] = None
    credentialUrl: Optional[str] = None
    image: Optional[str] = None
    order: int = 0

class CertificationUpdate(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    issueDate: Optional[datetime] = None
    expiryDate: Optional[datetime] = None
    credentialId: Optional[str] = None
    credentialUrl: Optional[str] = None
    image: Optional[str] = None
    order: Optional[int] = None
    updatedAt: datetime = Field(default_factory=datetime.utcnow)