from pydantic import BaseModel, Field
from pydantic_core import ErrorDetails
from typing import Optional, List


# Receberá o JSON com name, description e members que é uma lista de users_ids
class MemberSchema(BaseModel):
    id: str
    name : str

    class Config:
        from_attributes = True

class ResponseCreatePlannigSuccessSchema(BaseModel):
    message: str
    name: str
    description : Optional[str]
    members : Optional[MemberSchema] = Field(default_factory=list)
    
    class Config:
        from_attributes = True

class ResponseFailPlannigSuccessSchema:
    message : str
    errors : List[ErrorDetails]

class ResponseDeletePlanningSchema(BaseModel):
    message : str
    id : str
    name = str

class ReponseGetPlanningSchema(BaseModel):
    id : str
    description : str
    name : str
    members : List[MemberSchema] = Field(default_factory=list) 

    class Config:
        from_attributes = True

class ResponseMultiplePlanningSchema(BaseModel):
    message : str
    plannings : List[ReponseGetPlanningSchema]

    class Config:
        from_attributes= True