from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from ..schemas.user_schemas import UserCreate, UserUpdate
from ..security import verify_password, get_password_hash, create_access_token
from datetime import timedelta

ACCESS_TOKEN_EXPIRE_MINUTES = 30



def authenticate_user(db: Session, email: str, password: str):
    result = db.execute(text("SELECT * FROM bender.Tbl_Users_Ground_Ops WHERE email = :email"), {"email": email})
    user = result.fetchone()
    
    if not user:
        return None 
    if not verify_password(password, user["hashed_password"]):
        return None 

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={"sub": user["email"]}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": user["id"]}

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)

    estaciones = ",".join(user.estacion) if user.estacion else ""

    db.execute(
        text("""
            INSERT INTO bender.Tbl_Users_Ground_Ops (email, name, phone, estacion, rol, hashed_password)
            VALUES (:email, :name, :phone, :estacion, :rol, :hashed_password)
        """),
        {
            "email": user.email,
            "name": user.name,
            "phone": user.phone,
            "estacion": estaciones,
            "rol": user.rol,
            "hashed_password": hashed_password
        }
    )
    db.commit()

    result = db.execute(text("SELECT * FROM bender.Tbl_Users_Ground_Ops WHERE email = :email"), {"email": user.email})
    db_user = result.fetchone()
    return db_user

def get_user(db: Session, email: str):

    result = db.execute(
        text("SELECT * FROM bender.Tbl_Users_Ground_Ops WHERE email = :email"),
        {"email": email}
    )
    user = result.fetchone()
    return user


def update_user(db: Session, user_id: int, user: UserUpdate):
    result = db.execute(text("SELECT * FROM bender.Tbl_Users_Ground_Ops WHERE id = :user_id"), {"user_id": user_id})
    db_user = result.fetchone()

    if not db_user:
        return None  

    if user.password: 
        db.execute(
            text("UPDATE bender.Tbl_Users_Ground_Ops SET hashed_password = :hashed_password WHERE id = :user_id"),
            {"hashed_password": get_password_hash(user.password), "user_id": user_id}
        )

    if user.estacion is not None:
        db.execute(
            text("UPDATE bender.Tbl_Users_Ground_Ops SET estacion = :estacion WHERE id = :user_id"),
            {"estacion": ",".join(user.estacion), "user_id": user_id}
        )

    for key, value in user.dict(exclude={"password", "estacion"}).items():
        if value is not None:
            db.execute(
                text(f"UPDATE bender.Tbl_Users_Ground_Ops SET {key} = :value WHERE id = :user_id"),
                {"value": value, "user_id": user_id}
            )

    db.commit()

    result = db.execute(text("SELECT * FROM bender.Tbl_Users_Ground_Ops WHERE id = :user_id"), {"user_id": user_id})
    db_user = result.fetchone()
    return db_user

def delete_user(db: Session, user_id: int):
    result = db.execute(text("SELECT * FROM bender.Tbl_Users_Ground_Ops WHERE id = :user_id"), {"user_id": user_id})
    db_user = result.fetchone()

    if db_user:
        db.execute(text("DELETE FROM bender.Tbl_Users_Ground_Ops WHERE id = :user_id"), {"user_id": user_id})
        db.commit()
        return db_user
    return None
