from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime



class FlightInfo(BaseModel):
    flightNumber: Optional[str] = None
    departureDate: Optional[datetime] = None
    fromAirport: Optional[str] = None
    toAirport: Optional[str] = None

class BaggageCaseCreate(BaseModel):
    baggage_code: Optional[str] = None
    PNR: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    flight_number: Optional[str] = None
    departure_date: Optional[datetime] = None
    from_airport: Optional[str] = None
    to_airport: Optional[str] = None
    passenger_name: Optional[str] = None
    description: Optional[str] = None
    issue_type: Optional[str] = None
    number_ticket_zendesk: Optional[str] = None
    pruebas_url: Optional[str] = None
    direccion_envio: Optional[str] = None
    comments: Optional[List['CommentCreate']] = []

    class Config:
        orm_mode = True

class BaggageCaseUpdate(BaseModel):
    baggage_code: Optional[str] = None
    PNR: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    flightNumber: Optional[str] = None
    departureDate: Optional[datetime] = None
    fromAirport: Optional[str] = None
    toAirport: Optional[str] = None
    passenger_name: Optional[str] = None
    description: Optional[str] = None
    issue_type: Optional[str] = None
    status: Optional[str] = None
    number_ticket_zendesk: Optional[str] = None
    pruebas_url: Optional[str] = None
    direccion_envio: Optional[str] = None
    comments: Optional[List['CommentSchema']] = []

    class Config:
        orm_mode = True

class BaggageCaseSchema(BaseModel):
    id: Optional[str] = None
    baggage_code: Optional[str] = None
    PNR: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    flight_number: Optional[str] = None
    departure_date: Optional[datetime] = None
    from_airport: Optional[str] = None
    to_airport: Optional[str] = None
    passenger_name: Optional[str] = None
    description: Optional[str] = None
    issue_type: Optional[str] = None
    status: Optional[str] = None
    date_create: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    number_ticket_zendesk: Optional[str] = None
    pruebas_url: Optional[str] = None
    direccion_envio: Optional[str] = None
    comments: Optional[List['CommentSchema']] = []

    class Config:
        orm_mode = True

class CommentCreate(BaseModel):
    text: Optional[str] = None  
    baggage_case_id: Optional[str] = None  

    class Config:
        orm_mode = True

class CommentSchema(BaseModel):
    id: Optional[str] = None
    text: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True
