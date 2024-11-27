from sqlalchemy.orm import Session
import requests

url = "https://api-dm.radixxgo.com/api/1.8/flight/get_list?"
headers = {
    "X-api-key": "P08UbAN6lr1MZzmDlJLQTXQV6UULfIn9nNs0Vj04", 
    "Authorization": "Basic username=forthcodeapiuser, password=Aqg5u!ELh#g8sgwG"
    
}
params = {
    "station_iata": "SDQ",
    "start_date": "2024-10-08",
    "pend_date": "2024-10-08"
}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()  
    print("Datos recibidos:", data)
else:
    print(f"Error {response.status_code}: {response.text}")
    