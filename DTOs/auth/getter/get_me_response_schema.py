from pydantic import BaseModel, EmailStr

class UserResponseSchema(BaseModel):
    user_id : str
    name : str
    email : EmailStr

    class Config:
        from_attributes = True