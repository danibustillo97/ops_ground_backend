# src/crud/manifest_crud.py

from sqlalchemy.orm import Session
from ..model import FctManifest

def get_manifest_by_confirmation_num(db: Session, confirmation_num: str):
    manifests = db.query(FctManifest).filter(FctManifest.Confirmation_Num == confirmation_num).all()
    
    response_data = []
    for manifest in manifests:
        response_data.append({
            "Flight_Num": manifest.Flight_Num,
            "Id_Departure_Date": manifest.Id_Departure_Date,
            "Departure_Time": manifest.Departure_Time,
            "From_Airport": manifest.From_Airport,
            "To_Airport": manifest.To_Airport,
            "Pax_Name": manifest.Pax_Name,
            "Gender": manifest.Gender,
            "email": manifest.email,
            "id_number": manifest.id_number,
            "residence_country": manifest.residence_country,
            "Seat": manifest.Seat,
            "Confirmation_Num": manifest.Confirmation_Num,
            "ink_passenger_identifier": manifest.ink_passenger_identifier,
            "Bags": manifest.Bags,
            "Status_Manifest": manifest.Status_Manifest,
            "Bag_Tags": manifest.Bag_Tags.split(",") if manifest.Bag_Tags else None  # Manejar None adecuadamente
        })
    
    return response_data
