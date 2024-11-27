# src/domain/schemas/user_schemas.py

from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    rol: Optional[str] = None
    estacion: Optional[str] = None
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    rol: Optional[str] = None
    estacion: Optional[str] = None
    password: Optional[str] = None  # La contraseña es opcional

class User(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    rol: Optional[str] = None
    estacion: Optional[str] = None

    class Config:
        orm_mode = True
