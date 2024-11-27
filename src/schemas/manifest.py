from pydantic import BaseModel, validator
from typing import List, Optional

class ManifestResponse(BaseModel):
    Flight_Num: Optional[str]
    Id_Departure_Date: Optional[str]
    Departure_Time: Optional[str]
    From_Airport: Optional[str]
    To_Airport: Optional[str]
    Pax_Name: Optional[str]
    Gender: Optional[str]
    email: Optional[str]
    id_number: Optional[str]
    residence_country: Optional[str]
    Seat: Optional[str]
    Confirmation_Num: Optional[str]
    ink_passenger_identifier: Optional[str]
    Bags: Optional[int]
    Status_Manifest: Optional[str]
    Bag_Tags: Optional[List[str]] = None

    class Config:
        from_attributes = True  # Cambio de orm_mode a from_attributes en Pydantic v2

    @validator('Id_Departure_Date', pre=True)
    def convert_date_to_string(cls, value):
        # Convertir la fecha de número a string
        return str(value)

    @validator('Bag_Tags', pre=True)
    def ensure_list_for_bag_tags(cls, value):
        # Si Bag_Tags es una cadena, conviértelo en una lista con un solo elemento
        if isinstance(value, str):
            return [value]
        return value
