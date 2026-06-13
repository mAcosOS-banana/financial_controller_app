from pydantic import BaseModel, Field
from pydantic_core import ErrorDetails

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
    value: str
    type: str
    due_date: date
    paid_at: Optional[date] = None
    creator : UserSummarySchema
    updater : Optional[UserSummarySchema] = None

    class Config:
        from_attributes = True

class FailTrasactionBase(BaseModel):
    message: str
    errors : List[ErrorDetails]

class ResponseSuccessCreateTransaction(BaseModel):
    message : str
    data : TransactionDetailSchema

class ResponseSuccessUpdateTransaction(BaseModel):
    message : str
    data : TransactionDetailSchema

class ResponseTransactionListSchema(BaseModel):
    message : str
    data : List[TransactionDetailSchema]

class ResponseFailCreateTransaction(FailTrasactionBase):
    pass

class ResponseFailUpdateTransaction(FailTrasactionBase):
    pass
