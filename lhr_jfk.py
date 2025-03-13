import requests
import json
import time
from datetime import datetime, timedelta

# API token
token = "9e4cbed7-c083-494d-b922-11a076fbea89|2OJyMD3vgMcc8vZOQpwMahFxRjv3yXsEGXPDaHOmddb34dc6"

# Base URL for FlightRadar24 API
base_url = "https://fr24api.flightradar24.com"

# Headers for authentication
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
    "Accept-Version": "v1"
}

def get_historic_flight_positions(timestamp=None):
    """
    Get historic flight positions for BA 175 at a specific timestamp
    
    Args:
        timestamp (int, optional): Unix timestamp for the historic data.
                                  If None, uses 24 hours ago.
    """
    
    # If no timestamp provided, use 24 hours ago
    if timestamp is None:
        # Get timestamp from 24 hours ago
        timestamp = int((datetime.now() - timedelta(days=1)).timestamp())
    
    # Endpoint for historic flight positions
    endpoint = "/api/historic/flight-positions/full"
    
    # Parameters for the request
    params = {
        'flights': 'B62220',  # Filter for British Airways flight 175
        'timestamp': str(timestamp)  # Convert timestamp to string
    }
    
    try:
        print(f"Requesting historic flight positions for B62220 at timestamp {timestamp}...")
        print(f"Date/time: {datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
        
        response = requests.get(f"{base_url}{endpoint}", headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if data is a list or a dictionary with a 'data' key
            if isinstance(data, list):
                print(f"Success! Found {len(data)} historic BA 175 flights")
                return {"data": data}  # Convert to expected format
            elif isinstance(data, dict) and 'data' in data:
                print(f"Success! Found {len(data['data'])} historic BA 175 flights")
                return data
            else:
                print(f"Success! Received data in unexpected format")
                return {"data": []}  # Return empty data in expected format
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return {"data": []}  # Return empty data in expected format
    except Exception as e:
        print(f"Request failed: {e}")
        return {"data": []}  # Return empty data in expected format

def get_historic_lhr_jfk_flights(timestamp=None):
    """
    Get all historic flights between LHR and JFK at a specific timestamp
    
    Args:
        timestamp (int, optional): Unix timestamp for the historic data.
                                  If None, uses 24 hours ago.
    """
    
    # If no timestamp provided, use 24 hours ago
    if timestamp is None:
        # Get timestamp from 24 hours ago
        timestamp = int((datetime.now() - timedelta(days=1)).timestamp())
    
    # Endpoint for historic flight positions
    endpoint = "/api/historic/flight-positions/full"
    
    # Parameters for the request
    params = {
        'routes': 'LHR-JFK',  # Filter for flights between LHR and JFK
        'timestamp': str(timestamp)  # Convert timestamp to string
    }
    
    try:
        print(f"Requesting historic flights between LHR and JFK at timestamp {timestamp}...")
        print(f"Date/time: {datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
        
        response = requests.get(f"{base_url}{endpoint}", headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if data is a list or a dictionary with a 'data' key
            if isinstance(data, list):
                print(f"Success! Found {len(data)} historic flights between LHR and JFK")
                return {"data": data}  # Convert to expected format
            elif isinstance(data, dict) and 'data' in data:
                print(f"Success! Found {len(data['data'])} historic flights between LHR and JFK")
                return data
            else:
                print(f"Success! Received data in unexpected format")
                return {"data": []}  # Return empty data in expected format
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return {"data": []}  # Return empty data in expected format
    except Exception as e:
        print(f"Request failed: {e}")
        return {"data": []}  # Return empty data in expected format

def main():
    # Use a specific timestamp (July 1, 2023 at 12:00 UTC)
    # You can change this to any timestamp you want to query
    specific_timestamp = 1740476334  # This is the timestamp you provided
    
    # Get historic BA 175 flights
    flight_data = get_historic_flight_positions(specific_timestamp)
    
    if flight_data and flight_data.get('data') and len(flight_data['data']) > 0:
        # Print basic information about each historic BA 175 flight
        for flight in flight_data['data']:
            print("\nHistoric Flight Details:")
            print(f"Flight Number: {flight.get('flight', 'N/A')}")
            print(f"From: {flight.get('orig_iata', 'N/A')} to {flight.get('dest_iata', 'N/A')}")
            print(f"Aircraft: {flight.get('type', 'N/A')} (Reg: {flight.get('reg', 'N/A')})")
            print(f"Altitude: {flight.get('alt', 'N/A')} ft")
            print(f"Speed: {flight.get('gspeed', 'N/A')} knots")
            print(f"Position: {flight.get('lat', 'N/A')}, {flight.get('lon', 'N/A')}")
    else:
        print("No historic BA 175 flights found. Checking all historic LHR-JFK flights...")
        route_data = get_historic_lhr_jfk_flights(specific_timestamp)
        
        if route_data and route_data.get('data') and len(route_data['data']) > 0:
            print(f"\nFound {len(route_data['data'])} historic flights between LHR and JFK:")
            for flight in route_data['data']:
                print(f"Flight: {flight.get('flight', 'N/A')} - "
                      f"From {flight.get('orig_iata', 'N/A')} to {flight.get('dest_iata', 'N/A')}")
        else:
            print("No historic flights found between LHR and JFK at the specified time.")

if __name__ == "__main__":
    main()