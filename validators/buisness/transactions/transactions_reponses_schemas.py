from pydantic import BaseModel, Field, ConfigDict, computed_field
from pydantic_core import ErrorDetails
from decimal import Decimal
from typing import Optional, List
from datetime import date

from utils.schemas.pagination import PaginationMeta

class UserSummarySchema(BaseModel):
    id: str
    name : str

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

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

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    @computed_field
    @property
    def is_paid(self) -> bool:
        return True if self.paid_at else False

class ResponseFailTrasaction(BaseModel):
    message: str
    errors : List[ErrorDetails]

class ResponseCreateTransaction(BaseModel):
    message : str
    data : TransactionDetailSchema  
    
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

class ResponseUpdateTransaction(BaseModel):
    message : str
    data : TransactionDetailSchema

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

class ResponseTransactionListSchema(BaseModel):
    message : str
    data : List[TransactionDetailSchema]
    pagination : PaginationMeta

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)
        
class ResponseDeleteTrasactionSchema(BaseModel):
    message : str
    data : TransactionDetailSchema

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

class ResponseGetTransactionSchema(BaseModel):
    message : str
    data : TransactionDetailSchema
    
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

