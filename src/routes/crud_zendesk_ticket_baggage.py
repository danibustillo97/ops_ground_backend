from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()


zendesk_url = "https://arajet.zendesk.com"
make_request = "/api/v2/tickets"
get_locales = "/api/v2/locales"
email = 'jean.fontanillas@arajet.com/token'
password = '4Pyi8J2wqOVTQyoJr0sYuEftG6FRLmJ0IlE0aFRW'


payload = {
    "ticket": {
        "subject": "Solicitud de prueba",
        "comment": {
            "body": "Este es un comentario de prueba desde FastAPI."
        }
    }
}


headers = {
    "Content-Type": "application/json"
}

@app.post("/create_ticket/")
def create_ticket():
    try:
        response = requests.post(
            url=zendesk_url + make_request,
            auth=(email, password),
            headers=headers,
            json=payload
        )
        
        if response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        return {"message": "Ticket creado con éxito", "data": response.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
