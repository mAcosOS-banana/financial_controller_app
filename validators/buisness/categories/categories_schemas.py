from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

class CategoryBase(BaseModel):
    name : Optional[str]
    color : Optional[str]

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)
class CreateCategorySchema(CategoryBase):
    name : str = Field(..., max_length=50)
    color : str = Field(..., min_length=2, max_length=7)

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)
    
class UpdateCategorySchema(CategoryBase):
    pass

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)







    