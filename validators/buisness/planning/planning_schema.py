from pydantic import BaseModel, Field, EmailStr
from pydantic_core import ErrorDetails
from typing import Optional, List


class MemberSchema(BaseModel):
    id : str
    name : str
    email : EmailStr
    
    class Config:
        from_attributes : True


class CreatePlanningSchema(BaseModel):
    name : str = Field(..., min_length=2, max_length=80)
    description : Optional[str] = Field(None, max_length=250)
    members : Optional[MemberSchema] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class UpdatePlanningSchema(BaseModel):
    name : Optional[str] = Field(None, max_length=80)
    description : Optional[str] = Field(None, max_length=250)
    members : Optional[MemberSchema] = Field(None)

    class Config:
        from_attributes = True

