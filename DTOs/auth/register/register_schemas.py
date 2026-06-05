from pydantic import BaseModel, EmailStr, field_validator, Field
import re

class RegisterSchema(BaseModel):
    name : str = Field(...,min_length=2, max_length=50)
    email : EmailStr = Field(..., max_length=100)
    password: str = Field(..., min_length=8)


    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", v):
            raise ValueError("Nome deve conter apenas letras e espacos")
        v = v.strip()
        v = re.sub(r"\s{2,}", " ", v)
        return v.title()



    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Senha deve ter no mínimo 8 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Senha deve ter ao menos uma letra maiúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("Senha deve ter ao menos uma letra minúscula")
        if not re.search(r"\d", v):
            raise ValueError("Senha deve ter ao menos um número")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Senha deve ter ao menos um caractere especial")
        return v