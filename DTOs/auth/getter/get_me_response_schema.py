from pydantic import BaseModel, EmailStr
from typing import List

class ResponseUserSchema(BaseModel):
    user_id : str
    name : str
    email : EmailStr

    class Config:
        from_attributes = True

class ResponseMultipleUsersSchema(BaseModel):
    user : List[ResponseUserSchema]

    class Config:
        from_attributes = True
