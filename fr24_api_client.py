import requests
import json

# API token
token = "9e4cbed7-c083-494d-b922-11a076fbea89|2OJyMD3vgMcc8vZOQpwMahFxRjv3yXsEGXPDaHOmddb34dc6"

# Base URL for FlightRadar24 API
base_url = "https://fr24api.flightradar24.com"

# Example: Get basic airport information by code
airport_code = "LHR"  # London Heathrow
endpoint = f"/api/static/airports/{airport_code}/light"

# Headers for authentication
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
    "Accept-Version": "v1"  # This is the correct header for API version
}

# Make the API request
try:
    print(f"Requesting data from: {base_url}{endpoint}")
    response = requests.get(f"{base_url}{endpoint}", headers=headers)
    
    # Check if request was successful
    if response.status_code == 200:
        data = response.json()
        print("Success! Response data:")
        print(json.dumps(data, indent=4))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Request failed: {e}")
