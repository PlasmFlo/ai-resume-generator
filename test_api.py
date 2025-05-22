import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY not found in environment")

# sanitize any non‑ASCII hyphens
api_key = api_key.replace("\u2011", "-")

client = OpenAI(api_key=api_key)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are J.A.R.V.I.S., Tony Stark’s coding assistant."},
        {"role": "user",   "content": "How do I check if a Python object is an instance of a class?"}
    ]
)
print(response.choices[0].message.content)
