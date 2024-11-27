from sqlalchemy.orm import Session
from ..schemas.role_schemas import RoleCreate
from ..model import Role

def create_role(db: Session, role: RoleCreate):
    db_role = Role(**role.dict())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def get_roles(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Role).offset(skip).limit(limit).all()

def get_roles(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Role).order_by(Role.id).offset(skip).limit(limit).all()

def update_role(db: Session, role_id: int, role: RoleCreate):
    db_role = db.query(Role).filter(Role.id == role_id).first()
    if db_role:
        for key, value in role.dict().items():
            setattr(db_role, key, value)
        db.commit()
        db.refresh(db_role)
    return db_role

def delete_role(db: Session, role_id: int):
    db_role = db.query(Role).filter(Role.id == role_id).first()
    if db_role:
        db.delete(db_role)
        db.commit()
    return db_role
