from pydantic import BaseModel, Field, model_validator, field_validator
from datetime import date
from typing import Literal, Optional
from decimal import Decimal, ROUND_HALF_UP

class CreateTransactionSchema(BaseModel):
    title : str = Field(...,min_length=2, max_length=(80))
    description : Optional[str] = Field(None, max_length=250)
    category_id : str = Field(..., max_length=32)
    value : Decimal = Field(..., gt=0 ,max_digits=20, decimal_places=2)
    type : Literal["despesa", "receita"] = Field(...)
    due_date : date 
    is_paid : bool = False
    paid_at : Optional[date] = None


    @field_validator("value")
    @classmethod
    def normalize_value(cls, v : Decimal):
        return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @model_validator(mode="after")
    def check_paid_date(self):
        if self.is_paid and self.paid_at is None:
            raise ValueError("Se a conta está paga, informe a data de pagamento")
        if not self.is_paid and self.paid_at is not None:
            raise ValueError("Não envie data de pagamento para conta não paga")
        return self
    
class UpdateTransactionSchema(BaseModel):
    title : Optional[str] = Field(None, max_length=(80))
    description : Optional[str] = Field(None, max_length=250)
    category_id : Optional[str] = Field(None, max_length=32)
    value : Optional[Decimal] = Field(None, gt=0, max_digits=20, decimal_places=2)
    type : Optional[Literal["despesa", "receita"]] = None
    due_date : Optional[date] = None
    is_paid : Optional[bool] = None
    paid_at : Optional[date] = None

    #check_paid apenas checa se user marcou com paid e se o paid_at é None pois não a necessidade de conferir se o estado de pagamento é true/false pois o mesmo foi criado no Create
    @model_validator(mode="after")
    def check_paid_date(self):
        if self.is_paid and self.paid_at is None:
            raise ValueError("Se a conta está paga, informe a data de pagamento") 
        return self
    

class ResponseDeleteTrasactionSchema(BaseModel):
    message : str
    title : str 
    description : Optional[str] = None
    category_name : str
    value : str

    class Config:
        from_attributes = True
