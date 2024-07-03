from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


client = OpenAI()

def wrap_prompt(starter_prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"make the ultimate text prompt for a 4k wallpaper that begins from this initial prompt: {starter_prompt}. Be specific. If the prompt is subjective, convert it to a specific objective visual example that satisfies the prompt criteria",
            }
        ],
        model="gpt-3.5-turbo",
        temperature=0.9
    )

    return chat_completion.choices[0].message.content
