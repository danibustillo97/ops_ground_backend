from datetime import datetime
from sqlalchemy import Column, DateTime, PrimaryKeyConstraint, String, Integer
from .db import Base

class Role(Base):
    __tablename__ = 'Tbl_Roles_Ground_Ops'
    __table_args__ = {'schema': 'bender'}

    id = Column(Integer, primary_key=True, index=True)
    rol = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    cant_user_asigned = Column(Integer, nullable=False)

class FctManifest(Base):
    __tablename__ = "Fct_Manifest"
    __table_args__ = {'schema': 'Minerva'}

    Flight_Num = Column(String)
    Id_Departure_Date = Column(String)
    Departure_Time = Column(String)
    From_Airport = Column(String)
    To_Airport = Column(String)
    Pax_Name = Column(String)
    Gender = Column(String)
    email = Column(String)
    id_number = Column(String)
    residence_country = Column(String)
    Seat = Column(String)
    Confirmation_Num = Column(String, index=True)
    ink_passenger_identifier = Column(String)
    Bags = Column(Integer)
    Status_Manifest = Column(String)
    Bag_Tags = Column(String)

    __table_args__ = (
        PrimaryKeyConstraint('Confirmation_Num', 'Seat'),
        {'schema': 'Minerva'}
    )
