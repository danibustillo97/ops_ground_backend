from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    rol:str
    phone: str
    id: int

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User  

class TokenData(BaseModel):
    email: str
