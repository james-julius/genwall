import io
import os
import time
import schedule
from random import randint
import requests
import inquirer
import geocoder
from PIL import Image
from dotenv import load_dotenv
from datetime import datetime
from applescript import run
from stability_sdk import client

load_dotenv()

# Switch to stability GRPC API
os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'

def update_background(style):
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
    prompt = "An incredible, beautiful, aesthetic, mesmerising 4k desktop wallpaper of"
    space_prompt = "an extraordinary astrological event"
    location_prompt = f"location: {g.city}, {g.state}, {g.country} where the time is {time}, the temperature is {temperature} centigrade."

    prompt_combo = ""
    print(style)
    match style:
        case "Space":
            prompt_combo = f"{prompt} {space_prompt}"
        case "Location-Based":
            prompt_combo = f"{prompt} {location_prompt}"
    print(f"Calling Stability AI with prompt: {prompt_combo}")
    background_file = make_stable_diffusion_background(prompt_combo)
    print("Image created successfully")
    # Create file
    filename = datetime.now().strftime("%d-%m-%Y | %I:%M:%S %p ") + random_location
    file_location = f"./wallpapers/{filename}.jpeg"
    with open(file_location, 'wb') as file:
        file.write(background_file)
    abs_filepath = os.path.abspath(file_location)

    print("Upscaling image")
    upscaled_background = upscale_stable_diffusion_background(abs_filepath)

    upscaled_file_location = f"./wallpapers/{filename}-upscaled.jpeg"
    with open(upscaled_file_location, 'wb') as file:
        file.write(upscaled_background.getbuffer())
    upscaled_abs_filepath = os.path.abspath(upscaled_file_location)
    print("Setting as background image")

    # Set as background image
    cmdTemplate = '''
    tell application "System Events" to tell every desktop to set picture to "{0}"
    '''
    set_bg = cmdTemplate.format(upscaled_abs_filepath)
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


def upscale_stable_diffusion_background(filepath):
    api_key = os.getenv("STABILITY_AI_API_KEY")
    stability_api = client.StabilityInference(
        key=api_key,  # API Key reference.
        # The name of the upscaling model we want to use.
        upscale_engine="esrgan-v1-x2plus",
        # Available Upscaling Engines: esrgan-v1-x2plus
        verbose=True,  # Print debug messages.
    )
    img = Image.open(filepath)


    answers = stability_api.upscale(
        # Pass our image to the API and call the upscaling process.
        init_image=img,
        width=2048, # Optional parameter to specify the desired output width.
    )
    # Set up our warning to print to the console if the adult content classifier is tripped.
    # If adult content classifier is not tripped, save our image.

    for resp in answers:
        for artifact in resp.artifacts:
            # if artifact.finish_reason == generation.FILTER:
            #     print(
            #         "Your request activated the API's safety filters and could not be processed."
            #         "Please submit a different image and try again.")
            big_img = io.BytesIO(artifact.binary)
            return big_img
            # big_img.save("imageupscaled" + ".png") # Save our image to a local file.

# Ask the user what style they'd like to generate
style_options = [
    inquirer.List('style',
        message="What style of background would you like to generate?",
        choices=[
            'Space',
            'Location-Based'
        ],
    ),
]
inquiry_answers = inquirer.prompt(style_options)
style_choice = inquiry_answers['style']
def scheduled_background_change():
    print("Executing background update at:- " + str(datetime.now()))
    update_background(style_choice)

# Update background when script is first run
update_background(style_choice)

# Then do it every hour
schedule.every(1).hours.do(scheduled_background_change)

while True:
    schedule.run_pending()
    time.sleep(1)
