from pydantic import BaseModel, Field, ConfigDict
from pydantic_core import ErrorDetails
from typing import Optional, List
from utils.schemas.pagination import PaginationMeta


class MemberSchema(BaseModel):
    id: str
    name : str

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class PlanningDetailsSchema(BaseModel):
    id : str
    description : Optional[str]
    name : str
    members : List[MemberSchema] = Field(default_factory=list) 
    creator : MemberSchema
    updater : MemberSchema
    
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

class ResponseCreatePlannigSchema(BaseModel):
    message: str
    data : PlanningDetailsSchema
    
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

class ResponseUpdatePlannigSchema(BaseModel):
    message: str
    data : PlanningDetailsSchema
    
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

class ResponseFailPlannigSchema(BaseModel):
    message : str
    errors : List[ErrorDetails]

class ResponseDeletePlanningSchema(BaseModel):
    message : str
    data : PlanningDetailsSchema
    
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

class ReponseGetPlanningSchema(BaseModel):
    message : str
    data : PlanningDetailsSchema

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

class ResponseListPlanningSchema(BaseModel):
    message : str
    data : List[PlanningDetailsSchema]
    pagination : PaginationMeta

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)