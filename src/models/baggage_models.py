from datetime import datetime
from sqlalchemy import Column, DateTime, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BaggageCase(Base):
    __tablename__ = "Tbl_Baggage_Case_Ground_Ops"
    __table_args__ = {'schema': 'bender'}

    id = Column(String, primary_key=True, index=True)
    baggage_code = Column(String, nullable=False, index=True)
    PNR = Column(String, nullable=False, index=True)
    contact_phone = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    flight_number = Column(String, nullable=False)
    departure_date = Column(String, nullable=False)
    from_airport = Column(String, nullable=False)
    to_airport = Column(String, nullable=False)
    passenger_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    issue_type = Column(String, nullable=False)
    status = Column(String, default='Abierto', nullable=False)
    direccion_envio = Column(String, nullable=True)
    pruebas_url = Column(String, nullable=True)
    date_create = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_agente_name = Column(String, nullable=False)
    number_ticket_zendesk = Column(String, nullable=True)



class TblGroundOpsComments(Base):
    __tablename__ = "Tbl_Ground_ops_comments"
    __table_args__ = {'schema': 'bender'}

    id = Column(Integer, primary_key=True, index=True)
    baggage_case_id = Column(String, nullable=False)  
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
