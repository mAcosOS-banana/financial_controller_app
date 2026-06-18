from pydantic import BaseModel
from pydantic_core import ErrorDetails
from typing import List

class ValidationErrorResponseSchema(BaseModel):
    message : str
    errors : List[ErrorDetails]