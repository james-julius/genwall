import os
import pytz
import time
import pywal
import random
import schedule
import geocoder
from dotenv import load_dotenv
from datetime import datetime
from applescript import run
from services.location import get_current_weather_prompt, get_random_country, get_random_location
from services.open_ai import wrap_prompt
from services.setup_inquiry import run_setup_inquiry
from services.stability_ai import (
    make_stable_diffusion_background,
    upscale_stable_diffusion_background,
)

load_dotenv()

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
    random_location = get_random_location()
    prompt = "An incredible, beautiful, aesthetic, mesmerising 4k desktop wallpaper of"

    # Style prompts
    abstract_prompt = prompt + " abstract shapes"
    random_country_prompt = prompt + f"---one instance--- of somewhere specific or emblematic of {get_random_country()}"
    japan_prompt = prompt + "---one instance--- of somewhere specific in Japan, or something Japanese"
    space_prompt = prompt + " an extraordinary astrological event"
    location_prompt = (
        prompt
        + f" location: {g.city}, {g.state}, {g.country}, place: {random_location} where the time is {time}, the temperature is {temperature} centigrade."
    )

    prompt_combo = ""

    match style:
        case "Abstract":
            prompt_combo = abstract_prompt
        case "Random Country":
            prompt_combo = random_country_prompt
        case "Japan":
            prompt_combo = japan_prompt
        case "Space":
            prompt_combo = space_prompt
        case "Location-Based":
            prompt_combo = location_prompt
        case "Mixed":
            random_choice = random.randint(0, 2)
            prompt_list = [abstract_prompt, space_prompt, location_prompt]
            prompt_combo = prompt_list[random_choice]

    print(f"Initial prompt: {prompt_combo}")
    print("Calling OpenAI to get a more creative prompt from the initial generation")
    improved_prompt = wrap_prompt(prompt_combo)


    print(f"Calling Stability AI with prompt: {improved_prompt}")
    background_file = make_stable_diffusion_background(improved_prompt)
    print("Image created successfully")

    # Create file
    filename = datetime.now().strftime("%d-%m-%Y-%I:%M:%S%p-") + (
       style
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

    print(f"Saved file to: {abs_filepath}")
    # Remove non-upscaled image
    os.remove(file_location)

    print("Setting as background image")

    pywal.wallpaper.change(img=upscaled_abs_filepath)
    # Set as background image
    cmdTemplate = """
    tell application "System Events" to tell every desktop to set picture to "{0}"
    """
    set_bg = cmdTemplate.format(upscaled_abs_filepath)
    run(set_bg)
    print("✨ Enjoy your beautiful background ✨")


style, cadence = run_setup_inquiry()


def scheduled_background_change():
    print("Executing background update at:- " + str(datetime.now()))
    # Set a more unpredictable random seed
    random.seed(datetime.now().timestamp())
    update_background(style)


# Update background when script is first run
update_background(style)


# Then do it regularly
schedule.every(cadence).minutes.do(scheduled_background_change)

while True:
    schedule.run_pending()
    time.sleep(1)
