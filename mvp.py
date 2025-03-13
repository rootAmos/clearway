import random
from datetime import datetime, timedelta

# Airports: name, capacity (flights/hour), connections
airports = {
    "ATL": {"cap": 20, "links": ["DFW", "MIA", "JFK", "ORD"]},
    "DEN": {"cap": 20, "links": ["DFW", "PHX", "SEA", "LAX"]},
    "LAX": {"cap": 20, "links": ["DEN", "PHX", "SFO", "SEA"]},
    "ORD": {"cap": 20, "links": ["ATL", "DFW", "JFK", "DEN"]},
    "JFK": {"cap": 20, "links": ["ATL", "ORD", "MIA", "SFO"]},
    "DFW": {"cap": 20, "links": ["ATL", "DEN", "ORD", "PHX"]},
    "SEA": {"cap": 20, "links": ["DEN", "LAX", "SFO"]},
    "MIA": {"cap": 20, "links": ["ATL", "JFK", "DFW"]},
    "PHX": {"cap": 20, "links": ["DEN", "LAX", "DFW", "SFO"]},
    "SFO": {"cap": 20, "links": ["LAX", "SEA", "JFK", "PHX"]}
}

# 50 Flights: Pre-set schedule (times in 24h "HH:MM")
flights = [
    {"id": "F01", "from": "ATL", "to": "JFK", "time": "06:00"},
    {"id": "F02", "from": "DEN", "to": "LAX", "time": "07:00"},
    {"id": "F03", "from": "ORD", "to": "DFW", "time": "08:00"},
    {"id": "F04", "from": "LAX", "to": "SFO", "time": "09:00"},
    {"id": "F05", "from": "JFK", "to": "MIA", "time": "10:00"},
    # Fill out to 50 with semi-random spread
] + [{"id": f"F{i:02d}", "from": random.choice(list(airports.keys())),
      "to": random.choice(airports[random.choice(list(airports.keys()))]["links"]),
      "time": f"{h:02d}:00"} for i, h in enumerate(range(6, 21), 6) for _ in range(3)]

# Disruptions: Time in "HH:MM", duration in minutes
disruptions = {
    "DEN": {"cap": 10, "start": "10:00", "end": "14:00"},  # Storm, 4 hours
    "ORD": {"cap": 8, "start": "10:00", "end": "12:00"},   # ATC glitch, 2 hours
    "random_cancel": "F15"  # Mechanical, MIA → ATL at 11:00
}

# Time helper: Convert "HH:MM" to minutes since midnight
def time_to_minutes(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m

# Baseline: Dumb response to disruptions
def baseline_router(flights, disruptions):
    cancels = 0
    delay_minutes = 0
    current_slots = {a: 0 for a in airports}
    
    for f in flights:
        start = time_to_minutes(f["time"])
        if f["id"] == disruptions["random_cancel"]:
            cancels += 1
            continue
        for d, info in disruptions.items():
            if d in ["DEN", "ORD"] and f["from"] == d:
                if info["start"] <= f["time"] <= info["end"]:
                    if current_slots[d] >= info["cap"]:
                        cancels += 1
                    else:
                        current_slots[d] += 1
                        delay_minutes += 60  # 1-hour delay
                    continue
        current_slots[f["from"]] += 1  # Normal slot use
    
    return {"cancellations": cancels, "delay_minutes": delay_minutes}

# AI Router: Smart rerouting
def ai_router(flights, disruptions):
    cancels = 0
    delay_minutes = 0
    reroutes = 0
    fuel_used = 0
    max_fuel = 100
    current_slots = {a: 0 for a in airports}
    
    for f in flights:
        start = time_to_minutes(f["time"])
        if f["id"] == disruptions["random_cancel"]:
            cancels += 1
            print(f"{f['id']} {f['from']}->{f['to']} at {f['time']} canceled (mechanical)")
            continue
        
        # Check disruptions
        disrupted = False
        for d, info in disruptions.items():
            if d in ["DEN", "ORD"] and f["from"] == d:
                if time_to_minutes(info["start"]) <= start <= time_to_minutes(info["end"]):
                    if current_slots[d] >= info["cap"]:
                        # Try rerouting
                        for alt in airports[d]["links"]:
                            if current_slots[alt] < airports[alt]["cap"] and fuel_used + 5 <= max_fuel:
                                reroutes += 1
                                fuel_used += 5
                                delay_minutes += 60  # Extra hop delay
                                current_slots[alt] += 1
                                print(f"{f['id']} {f['from']}->{f['to']} at {f['time']} rerouted via {alt}")
                                disrupted = True
                                break
                        if not disrupted:
                            # Delay post-disruption
                            delay = (time_to_minutes(info["end"]) - start) + 60
                            delay_minutes += delay
                            current_slots[d] += 1
                            print(f"{f['id']} {f['from']}->{f['to']} at {f['time']} delayed {delay} min")
                            disrupted = True
                    else:
                        current_slots[d] += 1
                        delay_minutes += 60
                        print(f"{f['id']} {f['from']}->{f['to']} at {f['time']} delayed 60 min")
                        disrupted = True
                    break
        
        if not disrupted:
            current_slots[f["from"]] += 1  # Normal flight
    
    return {"cancellations": cancels, "delay_minutes": delay_minutes, "reroutes": reroutes, "fuel_left": max_fuel - fuel_used}

# Run the sim
baseline_result = baseline_router(flights, disruptions)
ai_result = ai_router(flights, disruptions)

# Results
print("\nBaseline (Dumb Routing):")
print(f"Cancellations: {baseline_result['cancellations']}, Delay Minutes: {baseline_result['delay_minutes']}")
print(f"Score: {-(baseline_result['cancellations'] * 100 + baseline_result['delay_minutes'])}")

print("\nAI Router:")
print(f"Cancellations: {ai_result['cancellations']}, Delay Minutes: {ai_result['delay_minutes']}, Reroutes: {ai_result['reroutes']}, Fuel Left: {ai_result['fuel_left']}")
print(f"Score: {-(ai_result['cancellations'] * 100 + ai_result['delay_minutes']) + ai_result['fuel_left']}")