from pydantic import BaseModel, ConfigDict
from pydantic_core import ErrorDetails
from typing import List

class ResgisterAuthDataSchema(BaseModel):
    user_id : str
    access_token : str

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class RegisterSuccessResponseSchema(BaseModel):
    message : str
    data : ResgisterAuthDataSchema
    
    
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class RegisterFailResponseSchema(BaseModel):
    message : str
    errors : List[ErrorDetails]