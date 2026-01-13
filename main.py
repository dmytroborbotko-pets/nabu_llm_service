import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "http://146.59.127.106:4000")
)

response_lapa = client.chat.completions.create(
    model="lapa",
    messages=[
        {"role": "user", "content": "Хто тримає цей район?"}
    ],
    temperature=0.7,
    max_tokens=1000
)

print("LapaLLM:", response_lapa.choices[0].message.content)