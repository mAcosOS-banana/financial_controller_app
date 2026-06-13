from pydantic import BaseModel
from pydantic_core import ErrorDetails
from typing import List, Optional


class CategoryDetailSchema(BaseModel):
    id : str
    name : str
    color : str

    class Config:
        from_attributes = True

class ResponseCreateCategorySchema(BaseModel):
    message : str 
    data : CategoryDetailSchema

class ResponseUpdateCategorySchema(BaseModel):
    message: str
    data : CategoryDetailSchema

class ResponseListCategorySchema(BaseModel):
    message : str
    data : List[CategoryDetailSchema]

class ResponseDeleteCategorySchema(BaseModel):
    message : str
    data : CategoryDetailSchema

class FailCategoryBase(BaseModel):
    message : str
    errors :  List[ErrorDetails]
