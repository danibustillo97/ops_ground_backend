def construct_baggage_case_response(baggage_case):
    response = {
        "id": baggage_case.id,
        "baggage_code": baggage_case.baggage_code,
        "PNR": baggage_case.PNR,
        "contact_phone": baggage_case.contact_phone,
        "contact_email": baggage_case.contact_email,
        "flight_number": baggage_case.flight_number,
        "departure_date": baggage_case.departure_date,
        "from_airport": baggage_case.from_airport,
        "to_airport": baggage_case.to_airport,    
        "passenger_name": baggage_case.passenger_name,
        "description": baggage_case.description,
        "issue_type": baggage_case.issue_type,
        "status": baggage_case.status,
        "date_create": baggage_case.date_create,
        "last_updated": baggage_case.last_updated,
        "number_ticket_zendesk": baggage_case.number_ticket_zendesk,
        "pruebas_url": baggage_case.pruebas_url,
        "direccion_envio": baggage_case.direccion_envio,
        "comments": [
            {
                "id": comment.id,
                "text": comment.text,
                "createdAt": comment.created_at
            }
            for comment in baggage_case.comments
        ]
    }
    return response
        