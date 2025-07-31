from pydantic import BaseModel, Field, GetCoreSchemaHandler
from typing import List, Optional, Any
from datetime import datetime
from bson import ObjectId
from pydantic_core import core_schema

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema: core_schema.CoreSchema, handler) -> dict[str, Any]:
        return {"type": "string"}

# Stats Model
class Stat(BaseModel):
    value: str
    label: str
    order: int = 0

# Personal Info Model
class PersonalInfo(BaseModel):
    name: str
    title: str
    bio: str = ""
    profileImage: Optional[str] = None
    location: str = ""
    email: str = ""
    linkedin: str = ""
    github: str = ""

# Portfolio Model
class Portfolio(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    userId: str
    personalInfo: PersonalInfo
    stats: List[Stat] = []
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class PortfolioUpdate(BaseModel):
    personalInfo: Optional[PersonalInfo] = None
    stats: Optional[List[Stat]] = None
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

class PortfolioCreate(BaseModel):
    userId: str
    personalInfo: PersonalInfo
    stats: List[Stat] = []