import os
import requests
import geocoder
from dotenv import load_dotenv
from datetime import datetime
from applescript import asrun

load_dotenv()

def main():
    # Get location and weather info
    g = geocoder.ip('me')
    location = get_current_weather_prompt(g.latlng)
    temperature = location["current"]["temperature_2m"]
    time = location["current"]["time"]

    # Make image
    background_file = make_stable_diffusion_background(f"An incredible, beautiful, aesthetic, mesmerising 4k desktop wallpaper of location: {g.city}, {g.state}, {g.country} where the time is {time}, the temperature is {temperature} centigrade.")

    # Create file
    filename = datetime.now().strftime("%d-%m-%Y | %H:%M:S")
    file_location = f"./wallpapers/{filename}.webp"
    with open(file_location, 'wb') as file:
        file.write(background_file)

    # Set as background image
    cmdTemplate = '''
    tell application "System Events" to tell every desktop to set picture to "{0}"
    '''
    set_bg = cmdTemplate.format(file_location)
    asrun(set_bg)


def get_current_weather_prompt(latlng):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latlng[0],
        "longitude": latlng[1],
        "current": "temperature_2m,wind_speed_10m",
        "aspect_ratio": "16:9",
        # "output_format": "jpeg"
    }

    response = requests.get(url, params=params)

    # Print the response in JSON format
    return response.json()


def make_stable_diffusion_background(prompt):
    api_key = os.getenv("STABILITY_AI_API_KEY")
    response = requests.post(
            f"https://api.stability.ai/v2beta/stable-image/generate/ultra",
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
main()