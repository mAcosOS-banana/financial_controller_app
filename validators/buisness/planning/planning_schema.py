from pydantic import BaseModel, Field, EmailStr, ConfigDict
from pydantic_core import ErrorDetails
from typing import Optional, List


class MemberSchema(BaseModel):
    id : str
    name : str
    email : EmailStr
    
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class CreatePlanningSchema(BaseModel):
    name : str = Field(..., min_length=2, max_length=80)
    description : Optional[str] = Field(None, max_length=250)
    members : Optional[List[str]] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class UpdatePlanningSchema(BaseModel):
    name : Optional[str] = Field(None, max_length=80)
    description : Optional[str] = Field(None, max_length=250)
    members : Optional[MemberSchema] = Field(None)

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

