from typing import Optional
from pydantic import BaseModel, EmailStr



class EmailRequest(BaseModel):
    case_id: Optional[str] = None
    to_email: EmailStr
    subject: Optional[str] = None
    body: Optional[str] = None