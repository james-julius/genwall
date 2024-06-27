import os
import pytz
import time
import random
import schedule
import inquirer
import geocoder
from dotenv import load_dotenv
from datetime import datetime
from applescript import run
from services.location import get_current_weather_prompt
from services.stability_ai import (
    make_stable_diffusion_background,
    upscale_stable_diffusion_background,
)

load_dotenv()

# Set a more unpredictable random seed
random.seed(datetime.now().timestamp() + os.getpid())


def update_background(style):
    print("💻 Updating background...")
    # Get location and weather info
    g = geocoder.ip("me")
    location = get_current_weather_prompt(g.latlng)
    temperature = location["current"]["temperature_2m"]

    def get_local_time():
        # Check for a time zone environment variable or default to system time zone
        time_zone = os.environ.get('TZ', 'America/Los_Angeles')

        # Set the local time zone
        local_timezone = pytz.timezone(time_zone)

        # Get the current time in the local time zone
        local_time = datetime.now(local_timezone)

        # Format the time for the prompt
        formatted_time = local_time.strftime("%Y-%m-%dT%H:%M")
        return formatted_time

    time = get_local_time()

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
        "Alley",
    ]

    random_location = location_wildcard[random.randint(0, len(location_wildcard) - 1)]
    prompt = "An incredible, beautiful, aesthetic, mesmerising 4k desktop wallpaper of"

    # Style prompts
    space_prompt = prompt + " an extraordinary astrological event"
    abstract_prompt = prompt + " abstract shapes"
    location_prompt = (
        prompt
        + f" location: {g.city}, {g.state}, {g.country} where the time is {time}, the temperature is {temperature} centigrade."
    )

    prompt_combo = ""

    match style:
        case "Abstract":
            prompt_combo = abstract_prompt
        case "Space":
            prompt_combo = space_prompt
        case "Location-Based":
            prompt_combo = location_prompt
        case "Mixed":
            random_choice = random.randint(0, 2)
            prompt_list = [abstract_prompt, space_prompt, location_prompt]
            prompt_combo = prompt_list[random_choice]

    print(f"Calling Stability AI with prompt: {prompt_combo}")
    background_file = make_stable_diffusion_background(prompt_combo)
    print("Image created successfully")

    # Create file
    filename = datetime.now().strftime("%d-%m-%Y | %I:%M:%S %p ") + (
        random_location if style == "Location-Based" else "space"
    )
    file_location = f"./wallpapers/{filename}.jpeg"
    with open(file_location, "wb") as file:
        file.write(background_file)
    abs_filepath = os.path.abspath(file_location)

    print("Upscaling image")
    upscaled_background = upscale_stable_diffusion_background(abs_filepath)
    print("Successfully upscaled image")

    print("Writing file")
    upscaled_file_location = f"./wallpapers/{filename}-upscaled.jpeg"
    with open(upscaled_file_location, "wb") as file:
        file.write(upscaled_background.getbuffer())
    upscaled_abs_filepath = os.path.abspath(upscaled_file_location)

    print("Setting as background image")

    # Set as background image
    cmdTemplate = """
    tell application "System Events" to tell every desktop to set picture to "{0}"
    """
    set_bg = cmdTemplate.format(upscaled_abs_filepath)
    run(set_bg)
    print("✨ Enjoy your beautiful background ✨")


# Ask the user what style they'd like to generate
run_options = [
    inquirer.List(
        "style",
        message="What style of background would you like to generate?",
        choices=[
            "Space",
            "Location-Based",
            "Abstract",
            "Mixed",
        ],
    ),
    inquirer.List(
        "cadence",
        message="How often would you like it to change?",
        choices=[
            "Daily",
            "Every 8 hours",
            "Every 4 hours",
            "Every 2 hours",
            "Hourly",
            "Every 30 minutes",
            "Every 15 minutes",
            "Every 5 minutes",
            "Every minute",
        ],
    ),
]

inquiry_answers = inquirer.prompt(run_options)
style_choice = inquiry_answers["style"]
cadence_choice = inquiry_answers["cadence"]

cadence_choice_map = {
    "Daily": 1440,
    "Every 8 hours": 480,
    "Every 4 hours": 240,
    "Every 2 hours": 120,
    "Hourly": 60,
    "Every 30 minutes": 30,
    "Every 15 minutes": 30,
    "Every 5 minutes": 5,
    "Every minute": 1
}

cadence = cadence_choice_map[cadence_choice]


def scheduled_background_change():
    print("Executing background update at:- " + str(datetime.now()))
    update_background(style_choice)


# Update background when script is first run
update_background(style_choice)

# Then do it regularly
schedule.every(cadence).minutes.do(scheduled_background_change)

while True:
    schedule.run_pending()
    time.sleep(1)
