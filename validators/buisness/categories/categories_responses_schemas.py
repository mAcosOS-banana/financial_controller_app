from pydantic import BaseModel, ConfigDict
from pydantic_core import ErrorDetails
from typing import List, Optional


class CategoryDetailSchema(BaseModel):
    id : str
    name : str
    color : str

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

class ResponseCreateCategorySchema(BaseModel):
    message : str 
    data : CategoryDetailSchema

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class ResponseUpdateCategorySchema(BaseModel):
    message: str
    data : CategoryDetailSchema

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class ResponseListCategorySchema(BaseModel):
    message : str
    data : List[CategoryDetailSchema]

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class ResponseDeleteCategorySchema(BaseModel):
    message : str
    data : CategoryDetailSchema

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class ResponseGetCategorySchema(BaseModel):
    message: str
    data : CategoryDetailSchema

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class FailCategoryBase(BaseModel):
    message : str
    errors :  List[ErrorDetails]

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)
