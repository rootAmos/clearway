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

def get_historic_flight_positions(flight_number, timestamp=None):
    """
    Get historic flight positions for a specific flight at a specific timestamp
    
    Args:
        flight_number (str): The flight number to search for (e.g., 'BA175', 'B62220')
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
        'flights': flight_number,  # Filter for the specified flight
        'timestamp': str(timestamp)  # Convert timestamp to string
    }
    
    try:
        print(f"Requesting historic flight positions for {flight_number} at timestamp {timestamp}...")
        print(f"Date/time: {datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
        
        response = requests.get(f"{base_url}{endpoint}", headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if data is a list or a dictionary with a 'data' key
            if isinstance(data, list):
                print(f"Success! Found {len(data)} historic {flight_number} flights")
                return {"data": data}  # Convert to expected format
            elif isinstance(data, dict) and 'data' in data:
                print(f"Success! Found {len(data['data'])} historic {flight_number} flights")
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

def get_historic_route_flights(origin, destination, timestamp=None):
    """
    Get all historic flights between two airports at a specific timestamp
    
    Args:
        origin (str): Origin airport code (e.g., 'LHR')
        destination (str): Destination airport code (e.g., 'JFK')
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
        'routes': f'{origin}-{destination}',  # Filter for flights between specified airports
        'timestamp': str(timestamp)  # Convert timestamp to string
    }
    
    try:
        print(f"Requesting historic flights between {origin} and {destination} at timestamp {timestamp}...")
        print(f"Date/time: {datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
        
        response = requests.get(f"{base_url}{endpoint}", headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if data is a list or a dictionary with a 'data' key
            if isinstance(data, list):
                print(f"Success! Found {len(data)} historic flights between {origin} and {destination}")
                return {"data": data}  # Convert to expected format
            elif isinstance(data, dict) and 'data' in data:
                print(f"Success! Found {len(data['data'])} historic flights between {origin} and {destination}")
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

def format_time(timestamp):
    """Format a timestamp into a readable date/time string"""
    if not timestamp:
        return "N/A"
    try:
        dt = datetime.fromtimestamp(int(timestamp))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except:
        # If timestamp is already a formatted string, return it as is
        return timestamp

def calculate_flight_time(departure_time, eta):
    """Calculate flight time from departure timestamp and ETA"""
    if not departure_time or not eta:
        return "N/A"
    try:
        # Convert timestamps to datetime objects
        dep_time = datetime.fromtimestamp(int(departure_time))
        eta_time = datetime.fromtimestamp(int(eta))
        
        # Calculate the difference
        flight_duration = eta_time - dep_time
        
        # Convert to hours and minutes
        total_seconds = flight_duration.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        
        return f"{hours}h {minutes}m"
    except Exception as e:
        print(f"Error calculating flight time: {e}")
        return "N/A"

def main():
    # Flight number to search for (can be changed to any flight number)
    flight_number = "B62220"  # Example: JetBlue flight 2220
    
    # Use the specified timestamp - DO NOT CHANGE THIS
    specific_timestamp = 1740476334
    
    # Get historic flight positions
    flight_data = get_historic_flight_positions(flight_number, specific_timestamp)
    
    if flight_data and flight_data.get('data') and len(flight_data['data']) > 0:
        # Print basic information about each historic flight
        for flight in flight_data['data']:
            print("\nHistoric Flight Details:")
            print(f"Flight Number: {flight.get('flight', flight_number)}")
            print(f"From: {flight.get('orig_iata', 'N/A')} to {flight.get('dest_iata', 'N/A')}")
            print(f"Aircraft: {flight.get('type', 'N/A')} (Reg: {flight.get('reg', 'N/A')})")
            
            # Extract time information
            departure_time = flight.get('departure_time')
            eta = flight.get('eta')
            
            # Display departure time if available
            if departure_time:
                print(f"Departure Time: {format_time(departure_time)}")
            
            # Display ETA if available
            if eta:
                print(f"Estimated Time of Arrival (ETA): {format_time(eta)}")
            
            # Calculate and display flight time if both departure and ETA are available
            if departure_time and eta:
                flight_time = calculate_flight_time(departure_time, eta)
                print(f"Estimated Flight Time: {flight_time}")
            
            print(f"Altitude: {flight.get('alt', 'N/A')} ft")
            print(f"Speed: {flight.get('gspeed', 'N/A')} knots")
            print(f"Position: {flight.get('lat', 'N/A')}, {flight.get('lon', 'N/A')}")
    else:
        print(f"No historic {flight_number} flights found.")
        
        # Try to extract origin and destination from flight number (if possible)
        # This is just a fallback and may not work for all flight numbers
        print(f"Would you like to search for flights between specific airports instead?")
        print(f"Example: Enter 'JFK-LAX' to search for flights between JFK and LAX")
        route = input("Enter route (or press Enter to skip): ")
        
        if route and '-' in route:
            origin, destination = route.split('-')
            route_data = get_historic_route_flights(origin.strip(), destination.strip(), specific_timestamp)
            
            if route_data and route_data.get('data') and len(route_data['data']) > 0:
                print(f"\nFound {len(route_data['data'])} historic flights between {origin} and {destination}:")
                for flight in route_data['data']:
                    flight_number = flight.get('flight', 'N/A')
                    print(f"\nFlight: {flight_number}")
                    print(f"From: {flight.get('orig_iata', 'N/A')} to {flight.get('dest_iata', 'N/A')}")
                    
                    # Extract time information
                    departure_time = flight.get('departure_time')
                    eta = flight.get('eta')
                    
                    # Display departure time if available
                    if departure_time:
                        print(f"Departure Time: {format_time(departure_time)}")
                    
                    # Display ETA if available
                    if eta:
                        print(f"Estimated Time of Arrival (ETA): {format_time(eta)}")
                    
                    # Calculate and display flight time if both departure and ETA are available
                    if departure_time and eta:
                        flight_time = calculate_flight_time(departure_time, eta)
                        print(f"Estimated Flight Time: {flight_time}")
            else:
                print(f"No historic flights found between {origin} and {destination} at the specified time.")

if __name__ == "__main__":
    main() 