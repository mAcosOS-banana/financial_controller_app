from pydantic import BaseModel, Field
from pydantic_core import ErrorDetails
from typing import Optional, List


class CreatePlanningSchema(BaseModel):
    name : str = Field(..., min_length=2, max_length=80)
    description : Optional[str] = Field(None, max_length=250)
    members : Optional[List[str]] = Field(default_factory=list)


class UpdatePlanningSchema(BaseModel):
    name : Optional[str] = Field(None, max_length=80)
    description : Optional[str] = Field(None, max_length=250)
    members : Optional[List[str]] = Field(None)



