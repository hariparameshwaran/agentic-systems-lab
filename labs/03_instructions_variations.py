from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

response = client.responses.create(
    model="gpt-5.5",
    instructions="""
    You are an order support assistant for an e-commerce company.
    Explain things clearly and concisely.
    Do not invent order information.
    """,
    input="My order hasn't arrived and I'm angry. Give me a refund immediately."
)

print(response.output_text)