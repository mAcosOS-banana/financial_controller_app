from pydantic import BaseModel, Field
from pydantic_core import ErrorDetails
from typing import Optional, List
from utils.schemas.pagination import PaginationMeta


class MemberSchema(BaseModel):
    id: str
    name : str

    class Config:
        from_attributes = True


class PlanningDetailsSchema(BaseModel):
    id : str
    description : Optional[str]
    name : str
    members : List[MemberSchema] = Field(default_factory=list) 

    class Config:
        from_attributes = True

class ResponseCreatePlannigSchema(BaseModel):
    message: str
    data : PlanningDetailsSchema
    
    class Config:
        from_attributes = True

class ResponseUpdatePlannigSchema(BaseModel):
    message: str
    data : PlanningDetailsSchema
    
    class Config:
        from_attributes = True

class ResponseFailPlannigSchema(BaseModel):
    message : str
    errors : List[ErrorDetails]

class ResponseDeletePlanningSchema(BaseModel):
    message : str
    data : PlanningDetailsSchema
    
    class Config:
        from_attributes = True

class ReponseGetPlanningSchema(BaseModel):
    message : str
    data : PlanningDetailsSchema

    class Config:
        from_attributes = True

class ResponseListPlanningSchema(BaseModel):
    message : str
    data : List[PlanningDetailsSchema]
    pagination : PaginationMeta

    class Config:
        from_attributes = True