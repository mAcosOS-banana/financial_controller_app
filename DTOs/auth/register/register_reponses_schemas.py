from pydantic import BaseModel
from pydantic_core import ErrorDetails
from typing import List

class RegisterSuccessResponseSchema(BaseModel):
    message : str
    user_id : str
    access_token : str  
    
    
    class Config:
        from_attributes = True


class RegisterFailResponseSchema(BaseModel):
    message : str
    errors : List[ErrorDetails]