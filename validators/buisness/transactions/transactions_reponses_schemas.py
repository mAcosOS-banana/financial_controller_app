from pydantic import BaseModel, Field
from pydantic_core import ErrorDetails
from decimal import Decimal
from typing import Optional, List
from datetime import date

class UserSummarySchema(BaseModel):
    id: str
    name : str

    class Config:
        from_attributes = True

class TransactionDetailSchema(BaseModel):
    id: str
    title: str
    description : Optional[str]
    value: Decimal
    type: str
    due_date: date
    paid_at: Optional[date] = None
    creator : UserSummarySchema
    updater : Optional[UserSummarySchema] = None

    class Config:
        from_attributes = True

class ResponseFailTrasaction(BaseModel):
    message: str
    errors : List[ErrorDetails]

class ResponseCreateTransaction(BaseModel):
    message : str
    data : TransactionDetailSchema

class ResponseUpdateTransaction(BaseModel):
    message : str
    data : TransactionDetailSchema

class ResponseTransactionListSchema(BaseModel):
    message : str
    data : List[TransactionDetailSchema]

class ResponseDeleteTrasactionSchema(BaseModel):
    message : str
    data : TransactionDetailSchema

    class Config:
        from_attributes = True

