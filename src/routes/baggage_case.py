import os
import uuid
from datetime import datetime, timezone
import logging
import requests
from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from typing import List
from ..models.baggage_models import BaggageCase
from ..schemas.baggage_case import BaggageCaseCreate, BaggageCaseUpdate, BaggageCaseSchema
from ..db import get_db
from ..security import get_current_user
from ..models.user import User

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

router = APIRouter()

ZENDESK_URL = "https://arajet.zendesk.com/api/v2/tickets"
ZENDESK_EMAIL = os.getenv('ZENDESK_EMAIL')  
ZENDESK_PASSWORD = os.getenv('ZENDESK_PASSWORD')  
HEADERS = {"Content-Type": "application/json"}

class ConsoleColors:
    HEADER = "\033[95m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"

def construct_baggage_case_response(baggage_case: BaggageCase) -> dict:
    response = {
        "id": baggage_case.id,
        "baggage_code": baggage_case.baggage_code,
        "PNR": baggage_case.PNR,
        "contact": {
            "phone": baggage_case.contact_phone,
            "email": baggage_case.contact_email
        },
        "flight_info": {
            "flightNumber": baggage_case.flight_number,
            "departureDate": baggage_case.departure_date,
            "fromAirport": baggage_case.from_airport,
            "toAirport": baggage_case.to_airport
        },
        "passenger_name": baggage_case.passenger_name,
        "description": baggage_case.description,
        "issue_type": baggage_case.issue_type,
        "status": baggage_case.status,
        "date_create": baggage_case.date_create,
        "last_updated": baggage_case.last_updated,
        "number_ticket_zendesk": baggage_case.number_ticket_zendesk,
        "pruebas_url": baggage_case.pruebas_url,
        "direccion_envio": baggage_case.direccion_envio
    }
    logger.debug(f"Response object: {response['PNR']}")
    return response

def create_ticket_in_zendesk(baggage_case: BaggageCaseCreate) -> int:
    ticket_data = {
        "ticket": {
            "comment": {
                "html_body": baggage_case.description
            },
            "requester": {
                "locale_id": 1551,
                "email": baggage_case.contact.email,
                "name": baggage_case.passenger_name
            },
            "group_id": 5460119544980,
            "subject": baggage_case.baggage_code,
            "ticket_form_id": 10041179330708,
            "custom_fields": [
                {"id": 360048220671, "value": baggage_case.issue_type},
            ]
        }
    }

    logger.info(f"Creating ticket in Zendesk with data: {ticket_data}")
    try:
        response = requests.post(
            url=ZENDESK_URL,
            auth=(ZENDESK_EMAIL, ZENDESK_PASSWORD),
            json=ticket_data
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to create ticket: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al crear el ticket en Zendesk.")

    ticket_id = response.json()["ticket"]["id"]
    # logger.info(f"Ticket created in Zendesk with ID: {ticket_id}")
    return ticket_id

@router.post("/", response_model=List[BaggageCaseSchema])
def create_baggage_cases(
    baggage_cases: List[BaggageCaseCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    created_baggage_cases = []

    for baggage_case in baggage_cases:
        logger.info(f"Processing baggage case with PNR: {baggage_case.PNR} and Baggage Code: {baggage_case.baggage_code}")

        if not baggage_case.PNR:
            error_message = "PNR no puede ser nulo o vacío."
            logger.error(f"{ConsoleColors.FAIL}{error_message}{ConsoleColors.ENDC}")
            raise HTTPException(status_code=400, detail=error_message)

        existing_case = db.query(BaggageCase).filter(
            BaggageCase.PNR == baggage_case.PNR,
            BaggageCase.baggage_code == baggage_case.baggage_code
        ).first()

        if existing_case:
            error_message = f"El caso ya existe PNR: {baggage_case.PNR} - Baggage Code: {baggage_case.baggage_code}"
            logger.warning(f"{ConsoleColors.WARNING}{error_message}{ConsoleColors.ENDC}")
            raise HTTPException(status_code=400, detail=error_message)

        try:
            ticket_number = create_ticket_in_zendesk(baggage_case)

            baggage_case_data = BaggageCase(
                id=str(uuid.uuid4()),
                baggage_code=baggage_case.baggage_code,
                PNR=baggage_case.PNR,
                contact_phone=baggage_case.contact.phone,
                contact_email=baggage_case.contact.email,
                flight_number=baggage_case.flight_info.flightNumber,
                departure_date=baggage_case.flight_info.departureDate,
                from_airport=baggage_case.flight_info.fromAirport,
                to_airport=baggage_case.flight_info.toAirport,
                passenger_name=baggage_case.passenger_name,
                description=baggage_case.description,
                issue_type=baggage_case.issue_type,
                status='Abierto',
                date_create=datetime.now(timezone.utc),
                last_updated=datetime.now(timezone.utc),
                number_ticket_zendesk=ticket_number,
                pruebas_url=baggage_case.pruebas_url if baggage_case.issue_type == "Daño" else None,
                direccion_envio=baggage_case.direccion_envio if baggage_case.issue_type == "Retraso" else None
            )

            db.add(baggage_case_data)
            db.commit()
            db.refresh(baggage_case_data)

            created_baggage_cases.append(construct_baggage_case_response(baggage_case_data))
            logger.info(f"Baggage case created: ID={baggage_case_data.id}, User={current_user.email}")

        except HTTPException as http_exc:
            logger.error(f"HTTP error while creating baggage case for {baggage_case}: {str(http_exc)}")
            raise http_exc  
        except Exception as e:
            logger.error(f"Error creating baggage case for {baggage_case}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error al crear los casos de equipaje.")
    
    logger.info(f"Created {len(created_baggage_cases)} baggage cases successfully.")
    return created_baggage_cases

@router.get("/", response_model=List[BaggageCaseSchema])
def read_baggage_cases(
    skip: int = 0,
    limit: int = 300,
    db: Session = Depends(get_db),
):
    try:
        logger.info(f"Fetching baggage cases, skip={skip}, limit={limit}")
        baggage_cases = db.query(BaggageCase).order_by(BaggageCase.id).offset(skip).limit(limit).all()

        if not baggage_cases:
            logger.warning("No baggage cases found.")
        else:
            logger.info(f"Found {len(baggage_cases)} baggage cases.")

        for baggage_case in baggage_cases:
            logger.debug(f"Consultando caso con PNR: {baggage_case.PNR}")
        
        baggage_cases_response = [construct_baggage_case_response(baggage_case) for baggage_case in baggage_cases]
        logger.info(f"Baggage cases response: {baggage_cases_response}")

        return baggage_cases_response
    
    except Exception as e:
        logger.error(f"Error while fetching baggage cases: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener los casos de equipaje.")

@router.get("/{baggage_case_id}", response_model=BaggageCaseSchema)
def read_baggage_case(
    baggage_case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    baggage_case = db.query(BaggageCase).filter(BaggageCase.id == baggage_case_id).first()
    
    if baggage_case is None:
        error_message = f"Baggage case with ID {baggage_case_id} not found."
        logger.error(f"{ConsoleColors.FAIL}{error_message}{ConsoleColors.ENDC}")
        raise HTTPException(status_code=404, detail=error_message)

    logger.info(f"Baggage case found: ID={baggage_case_id}")
    return construct_baggage_case_response(baggage_case)

@router.put("/{baggage_case_id}", response_model=BaggageCaseSchema)
def update_baggage_case(
    baggage_case_id: str,
    baggage_case_update: BaggageCaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    baggage_case = db.query(BaggageCase).filter(BaggageCase.id == baggage_case_id).first()
    
    if baggage_case is None:
        error_message = f"Baggage case with ID {baggage_case_id} not found."
        logger.error(f"{ConsoleColors.FAIL}{error_message}{ConsoleColors.ENDC}")
        raise HTTPException(status_code=404, detail=error_message)

    logger.info(f"Updating baggage case with ID: {baggage_case_id}")

    for key, value in baggage_case_update.dict(exclude_unset=True).items():
        setattr(baggage_case, key, value)

    baggage_case.last_updated = datetime.now(timezone.utc)
    db.commit()
    db.refresh(baggage_case)
    
    logger.info(f"Baggage case updated: ID={baggage_case_id}")
    return construct_baggage_case_response(baggage_case)


@router.delete("/{baggage_case_id}", response_model=dict)
def delete_baggage_case(
    baggage_case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    baggage_case = db.query(BaggageCase).filter(BaggageCase.id == baggage_case_id).first()
    
    if baggage_case is None:
        error_message = f"Baggage case with ID '{baggage_case_id}' not found."
        logger.warning(error_message)
        raise HTTPException(status_code=404, detail={"error": error_message})

    db.delete(baggage_case)
    db.commit()

    logger.info(f"Baggage case deleted: ID={baggage_case_id}, User={current_user.email}")
    return {"detail": f"Baggage case with ID '{baggage_case_id}' deleted successfully."}
