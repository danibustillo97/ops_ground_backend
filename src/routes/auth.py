from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..security import create_access_token
from ..db import get_db
from ..crud import user_crud
from ..schemas import token as token_schemas

router = APIRouter()

@router.post("/login", response_model=token_schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):

    user = user_crud.get_user(db, form_data.username)
    

    if not user or not user_crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",  
            headers={"WWW-Authenticate": "Bearer"},
            
        )

   
    access_token = create_access_token(data={"sub": user.email}) 

    

    return {"access_token": access_token, "token_type": "bearer", "user": {"name": user.name, "email": user.email, "role": user.rol, "estacion": user.estacion, "phone": user.phone}}
