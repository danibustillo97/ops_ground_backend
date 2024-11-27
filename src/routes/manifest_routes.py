from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..schemas.manifest import ManifestResponse
from ..crud.manifest_crud import get_manifest_by_confirmation_num
from ..db import get_db

router = APIRouter()

@router.get("/{confirmation_num}", response_model=List[ManifestResponse])
def read_manifest_by_confirmation_num(confirmation_num: str, db: Session = Depends(get_db)):
    manifests = get_manifest_by_confirmation_num(db, confirmation_num=confirmation_num)
    if not manifests:
        raise HTTPException(status_code=404, detail="Manifests not found")
    return manifests
