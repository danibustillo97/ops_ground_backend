from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..models.user import User as UserModel  # Modelo de SQLAlchemy
from ..schemas.user_schemas import User, UserCreate, UserUpdate  # Modelo Pydantic
from ..security import verify_password, get_password_hash, create_access_token
from ..db import get_db
from datetime import timedelta

ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id}

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    estaciones = ",".join(user.estacion) if user.estacion else ""
    db_user = UserModel(
        email=user.email,
        name=user.name,
        phone=user.phone,
        estacion=estaciones,
        rol=user.rol,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



def get_user(db: Session, user_id: int):
    return db.query(UserModel).filter(UserModel.id == user_id).first()

def update_user(db: Session, user_id: int, user: UserUpdate):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()

    if not db_user:
        return None  

    if user.password: 
        db_user.hashed_password = get_password_hash(user.password)

    if user.estacion is not None:
        db_user.estacion = ",".join(user.estacion)

    for key, value in user.dict(exclude={"password", "estacion"}).items():
        if value is not None:
            setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return db_user
    return None

@router.post("/", response_model=User)
def create_user_route(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db=db, user=user)

@router.get("/", response_model=List[User   ])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(UserModel).order_by(UserModel.id).offset(skip).limit(limit).all()
    print(users)
    return [user for user in users] 

@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=User)
def update_user_route(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    return update_user(db, user_id, user)

@router.delete("/{user_id}", response_model=User)
def delete_user_route(user_id: int, db: Session = Depends(get_db)):
    return delete_user(db, user_id)
