# src/routes/role_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..schemas.role_schemas import RoleCreate, Role
from ..crud import role_crud
from ..db import get_db

router = APIRouter()

@router.post("/", response_model=Role)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    return role_crud.create_role(db=db, role=role)

@router.get("/", response_model=List[Role])
def read_roles(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return role_crud.get_roles(db, skip=skip, limit=limit)

@router.get("/{role_id}", response_model=Role)
def read_role(role_id: int, db: Session = Depends(get_db)):
    db_role = role_crud.get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role

@router.put("/{role_id}", response_model=Role)
def update_role(role_id: int, role: RoleCreate, db: Session = Depends(get_db)):
    return role_crud.update_role(db, role_id, role)

@router.delete("/{role_id}", response_model=Role)
def delete_role(role_id: int, db: Session = Depends(get_db)):
    return role_crud.delete_role(db, role_id)
