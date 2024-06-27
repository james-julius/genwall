import io
import os
import requests
from PIL import Image
from stability_sdk import client

# Switch to stability GRPC API
os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'


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
        width=2048,  # Optional parameter to specify the desired output width.
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
