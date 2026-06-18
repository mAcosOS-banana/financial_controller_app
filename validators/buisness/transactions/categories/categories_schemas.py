from pydantic import BaseModel, Field
from typing import Optional, List

class CategoryBase(BaseModel):
    name : Optional[str]
    color : Optional[str]

class CreateCategorySchema(CategoryBase):
    name : str = Field(..., max_length=50)
    color : str = Field(..., min_length=2, max_length=7)

    
class UpdateCategorySchema(CategoryBase):
    pass





    