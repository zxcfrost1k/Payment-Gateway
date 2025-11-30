from typing import Optional, Dict, List
from pydantic import BaseModel, Field



class CancelTransactionErrorResponse(BaseModel):
    code: int
    message: str


class ErrorResponse(BaseModel):
    code: Optional[str] = None
    message: str
    errors: Optional[Dict[str, List[str]]] = None


class PaginationParams(BaseModel):
    page_size: int = Field(default=10, ge=10, le=100)
    page_number: int = Field(default=1, ge=1)
