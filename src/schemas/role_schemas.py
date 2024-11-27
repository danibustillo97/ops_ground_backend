from pydantic import BaseModel
from typing import Optional

class RoleCreate(BaseModel):
    rol: str
    description: Optional[str] = None
    cant_user_asigned: Optional[int] = 0

class Role(RoleCreate):
    id: int

    class Config:
        orm_mode = True
