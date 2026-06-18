from pydantic import BaseModel, EmailStr, Field

class LoginSchema(BaseModel):
    email : EmailStr = Field(..., max_length=100)
    password: str = Field(..., min_length=8)

