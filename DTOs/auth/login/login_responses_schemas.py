from pydantic import BaseModel
from typing import List
from pydantic_core import ErrorDetails


class LoginSuccessResponseSchema(BaseModel):
    message : str
    access_token : str
    refresh_token: str
    
    class Config:
        from_attributes = True

class LoginFailResponseSchema(BaseModel):
    message : str
    errors: List[ErrorDetails]