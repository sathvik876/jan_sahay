# backend/app/schemas.py

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from fastapi import UploadFile

class ChatRequest(BaseModel):
    message: str = Field(..., description="User question/message")
    language: Optional[str] = Field("en", description="Language code (en, hi, te)")

class SchemeSearchRequest(BaseModel):
    state: Optional[str] = None
    category: Optional[str] = None

class SchemeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: Optional[str] = None
    department: Optional[str] = None
    state: Optional[str] = None
    status: Optional[str] = None

class EligibilityCheckRequest(BaseModel):
    scheme_id: int
    user_data: Dict[str, Any] = Field(..., description="Key‑value pairs for user attributes, e.g., {\"state\": \"Telangana\", \"income\": 150000}")

class EligibilityResult(BaseModel):
    scheme_id: int
    status: str = Field(..., description="eligible | not_eligible | needs_more_info")
    missing_fields: List[str] = []
    matched_fields: List[str] = []

# For file upload endpoint
class UploadFileDependency:
    def __call__(self, file: UploadFile):
        return file
