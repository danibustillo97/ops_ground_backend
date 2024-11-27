from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user_schemas import UserCreate, UserUpdate
from ..security import verify_password, get_password_hash, create_access_token
from datetime import timedelta

ACCESS_TOKEN_EXPIRE_MINUTES = 30

def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticate a user by email and password, and return an access token if successful.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None  # No user found
    if not verify_password(password, user.hashed_password):
        return None  # Invalid password

    # Token expiration time
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Create the JWT token
    access_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id}

def create_user(db: Session, user: UserCreate):
    """
    Create a new user in the database with hashed password and optional user information.
    """
    # Hash the user's password
    hashed_password = get_password_hash(user.password)
    
    # Convert station list to a comma-separated string
    estaciones = ",".join(user.estacion) if user.estacion else ""
    
    # Create the User object
    db_user = User(
        email=user.email,
        name=user.name,
        phone=user.phone,
        estacion=estaciones,  # Store the estaciones as a comma-separated string
        rol=user.rol,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()  # Commit changes to the database
    db.refresh(db_user)  # Refresh the instance to get updated values from DB
    return db_user



def get_users(db: Session, skip: int = 0, limit: int = 10):
 
    return db.query(User).order_by(User.id).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: int, user: UserUpdate):

    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        return None  

    if user.password: 
        db_user.hashed_password = get_password_hash(user.password)

    # Convert list of stations to a comma-separated string if provided
    if user.estacion is not None:
        db_user.estacion = ",".join(user.estacion)  # Update the estaciones field as string

    # Update other fields, excluding password and estaciones
    for key, value in user.dict(exclude={"password", "estacion"}).items():
        if value is not None:
            setattr(db_user, key, value)

    db.commit()  # Commit changes to the database
    db.refresh(db_user)  # Refresh the instance to get updated values from DB
    return db_user

def delete_user(db: Session, user_id: int):
    """
    Delete a user by their user ID.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()  # Commit changes to the database to delete the user
        return db_user
    return None  # Return None if the user wasn't found
