import os
import time
import schedule
from random import randint
import requests
import geocoder
from dotenv import load_dotenv
from datetime import datetime
from applescript import run

load_dotenv()

def update_background():
    # Get location and weather info
    g = geocoder.ip('me')
    location = get_current_weather_prompt(g.latlng)
    temperature = location["current"]["temperature_2m"]
    time = location["current"]["time"]

    # Make image
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
        "Alley"
    ]
    random_location = location_wildcard[randint(0, len(location_wildcard) - 1)]
    prompt = f"An incredible, beautiful, aesthetic, mesmerising 4k desktop wallpaper in location: {g.city}, {g.state}, {g.country} where the time is {time}, the temperature is {temperature} centigrade. Pay attention to the time of day and make sure the image reflects if it is morning, evening or night time."
    print(f"Calling Stability AI with prompt: {prompt}")
    background_file = make_stable_diffusion_background(prompt)
    print("Image created successfully")

    # Create file
    filename = datetime.now().strftime("%d-%m-%Y | %I:%M:%S %p ") + random_location
    file_location = f"./wallpapers/{filename}.jpeg"
    with open(file_location, 'wb') as file:
        file.write(background_file)
    abs_filepath = os.path.abspath(file_location)
    print("Setting as background image")

    # Set as background image
    cmdTemplate = '''
    tell application "System Events" to tell every desktop to set picture to "{0}"
    '''
    set_bg = cmdTemplate.format(abs_filepath)
    run(set_bg)
    print("Boom! Enjoy your beautiful background")


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


def make_stable_diffusion_background(prompt):
    api_key = os.getenv("STABILITY_AI_API_KEY")
    response = requests.post(
            "https://api.stability.ai/v2beta/stable-image/generate/ultra",
            headers={
                "authorization": f"Bearer {api_key}",
                "accept": "image/*"
            },
            files={"none": ''},
            data={
                "prompt": prompt,
                "aspect_ratio": "16:9",
                "output_format": "webp",
            },
        )

    if response.status_code == 200:
        return response.content
    else:
        raise Exception(str(response.json()))

def scheduled_background_change():
    print("Executing background update at:- " + str(datetime.now()))
    update_background()

schedule.every(1).hours.do(scheduled_background_change)

while True:
    schedule.run_pending()
    time.sleep(1)
