import os
from datetime import datetime
from dotenv import load_dotenv
from fastapi import HTTPException, logger
import requests
from ..schemas.baggage_case import BaggageCaseCreate

# Cargar las variables de entorno
load_dotenv()

# Configuraciones de Zendesk
zendesk_url = os.getenv('ZENDESK_URL')
zendesk_email = os.getenv('ZENDESK_EMAIL')
zendesk_password = os.getenv('ZENDESK_PASSWORD')
HEADERS = {"Content-Type": "application/json"}


def create_ticket_in_zendesk(baggage_case: BaggageCaseCreate) -> int:
 
    try:
        departure_date_str = baggage_case.flight_info.departureDate  
        departure_date = datetime.strptime(departure_date_str, "%Y%m%d") 
        formatted_date = departure_date.strftime('%Y-%m-%d')
    except ValueError:
        logger.error(f"Error parsing date: {departure_date_str}")
        raise HTTPException(status_code=422, detail="La fecha de salida no es válida.")


    ticket_data = {
        "ticket": {
            "subject": baggage_case.baggage_code,
            "comment": {"body": baggage_case.description},
            "requester": {
                "email": baggage_case.contact.email,
                "name": baggage_case.passenger_name
            },
            "custom_fields": [
                {"id": 360048220671, "value": baggage_case.issue_type},
            
            ]
        }
    }


    response = requests.post(
        url=zendesk_url,
        auth=(zendesk_email, zendesk_password),
        headers=HEADERS,
        json=ticket_data
    )

    if response.status_code != 201:
        logger.error(f"Failed to create ticket: {response.text}")
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()["ticket"]["id"]
