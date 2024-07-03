import requests
import random

def get_current_weather_prompt(latlng):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latlng[0],
        "longitude": latlng[1],
        "current": "temperature_2m,wind_speed_10m",
    }

    response = requests.get(url, params=params)

    # Print the response in JSON format
    return response.json()


location_wildcard = [
    "Cafe",
    "Bar",
    "Park",
    "Restaurant",
    "Library",
    "Museum",
    "Theater",
    "Market",
    "Street",
    "Plaza",
    "Bridge",
    "Station",
    "Hotel",
    "Gym",
    "Mall",
    "Garden",
    "Beach",
    "Harbor",
    "Rooftop",
    "Alley",
]

def get_random_location():
    return location_wildcard[random.randint(0, len(location_wildcard) - 1)]
