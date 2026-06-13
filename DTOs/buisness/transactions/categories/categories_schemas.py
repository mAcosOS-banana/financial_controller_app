from pydantic import BaseModel, Field
from typing import Optional, List

class CategoryBase(BaseModel):
    name : Optional[str]
    color : Optional[str]
    planning_id : Optional[str]

class CreateCategorySchema(CategoryBase):
    name : str = Field(..., max_length=50)
    color : str = Field(..., min_length=2, max_length=7)
    planning_id : Optional[str] = Field(None, max_length=32)

class UpdateCategorySchema(CategoryBase):
    pass





    