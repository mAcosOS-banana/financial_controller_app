from pydantic import BaseModel, Field
from pydantic_core import ErrorDetails
from typing import Optional, List


# Receberá o JSON com name, description e members que é uma lista de users_ids
class MemberSchema(BaseModel):
    id: str
    name : str

    class Config:
        from_attributes = True


class PlanningDetails(BaseModel):
    id : str
    description : Optional[str]
    name : str
    members : List[MemberSchema] = Field(default_factory=list) 

    class Config:
        from_attributes = True

class ResponseCreatePlannigSchema(BaseModel):
    message: str
    data : PlanningDetails
    
    class Config:
        from_attributes = True

class ResponseUpdatePlannigSchema(BaseModel):
    message: str
    data : PlanningDetails
    
    class Config:
        from_attributes = True

class ResponseFailPlannigSchema(BaseModel):
    message : str
    errors : List[ErrorDetails]

class ResponseDeletePlanningSchema(BaseModel):
    message : str
    data : PlanningDetails
    
    class Config:
        from_attributes = True

class ReponseGetPlanningSchema(BaseModel):
    id : str
    description : str
    name : str
    members : List[MemberSchema] = Field(default_factory=list) 

    class Config:
        from_attributes = True

class ResponseListPlanningSchema(BaseModel):
    message : str
    plannings : List[ReponseGetPlanningSchema]

    class Config:
        from_attributes= True