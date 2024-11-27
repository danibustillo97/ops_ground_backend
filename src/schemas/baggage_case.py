from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

class ContactSchema(BaseModel):
    phone: Optional[str] = None
    email: Optional[EmailStr] = None  

class FlightInfoSchema(BaseModel):
    flightNumber: Optional[str] = None
    departureDate: Optional[str] = None
    fromAirport: Optional[str] = None
    toAirport: Optional[str] = None

class BaggageCaseCreate(BaseModel):
    baggage_code: Optional[str] = None
    PNR: str
    contact: Optional[ContactSchema] = None
    flight_info: Optional[FlightInfoSchema] = None
    passenger_name: Optional[str] = None
    description: Optional[str] = None
    issue_type: Optional[str] = None
    direccion_envio: Optional[str] = None
    pruebas_url: Optional[str] = None
    created_agente_name: Optional[str] = None
   

class BaggageCaseUpdate(BaseModel):
    baggage_code: Optional[str] = None
    contact: Optional[ContactSchema] = None
    flight_info: Optional[FlightInfoSchema] = None
    passenger_name: Optional[str] = None
    description: Optional[str] = None
    issue_type: Optional[str] = None
    status: Optional[str] = None
    direccion_envio: Optional[str] = None
    pruebas_url: Optional[str] = None
    created_agente_name: Optional[str] = None
    number_ticket_zendesk: Optional[str] = None
    date_create: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    PNR: str 

class BaggageCaseSchema(BaseModel):
    id: Optional[str] = None
    baggage_code: Optional[str] = None
    PNR: str
    contact: Optional[ContactSchema] = None
    flight_info: Optional[FlightInfoSchema] = None
    passenger_name: Optional[str] = None
    description: Optional[str] = None
    issue_type: Optional[str] = None
    status: Optional[str] = None
    direccion_envio: Optional[str] = None
    pruebas_url: Optional[str] = None
    date_create: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    created_agente_name: Optional[str] = None
    number_ticket_zendesk: Optional[str] = None
    

    class Config:
        orm_mode = True

class BaggageCaseListSchema(BaseModel):
    baggage_cases: Optional[List[BaggageCaseSchema]] = None

    class Config:
        orm_mode = True
