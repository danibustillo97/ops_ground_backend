from fastapi import APIRouter, Depends, HTTPException, Query
import requests
from datetime import datetime

router = APIRouter()

url = "https://api-dm.radixxgo.com/api/1.8/flight/get_list?"
date = datetime.today().strftime('%Y-%m-%d')

headers = {
    "X-api-key": "P08UbAN6lr1MZzmDlJLQTXQV6UULfIn9nNs0Vj04", 
    "Authorization": "Basic username=forthcodeapiuser, password=Aqg5u!ELh#g8sgwG"
}

station_iata= 'SDQ'

@router.get("/flights")
def get_flights():    
    params = {
        "station_iata": station_iata, 
        "start_date": date,
        "end_date": date
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status() 
        return response.json()  
    except requests.exceptions.HTTPError as err:
        raise HTTPException(status_code=500, detail=str(err))
