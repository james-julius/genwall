import os
import requests

def make_stable_diffusion_background(prompt):
    api_key = os.getenv("STABILITY_AI_API_KEY")
    response = requests.post(
        "https://api.stability.ai/v2beta/stable-image/generate/ultra",
        headers={"authorization": f"Bearer {api_key}", "accept": "image/*"},
        files={"none": ""},
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


def upscale_stable_diffusion_background(filepath, prompt):
    api_key = os.getenv("STABILITY_AI_API_KEY")

    response = requests.post(
        f"https://api.stability.ai/v2beta/stable-image/upscale/conservative",
        headers={
            "authorization": f"Bearer {api_key}",
            "accept": "image/*"
        },
        files={
            "image": open(filepath, "rb"),
        },
        data={
            "output_format": "webp",
            "prompt": prompt
        },
    )

    if response.status_code == 200:
        return response.content
    else:
        raise Exception(str(response.json()))