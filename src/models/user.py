from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from ..db import Base

class User(Base):
    __tablename__ = 'Tbl_Users_Ground_Ops'
    __table_args__ = {'schema': 'bender'}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    phone = Column(String)
    estacion = Column(String)
    rol = Column(String)
    hashed_password = Column(String)

   
    