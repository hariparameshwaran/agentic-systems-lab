from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

conversation = [
    {
        "role": "user",
        "content": "My order number is ORD-1234"
    },
    {
        "role": "assistant",
        "content": "Understood, Your order number is ORD-1234"
    },
    {
        "role": "user",
        "content": "What is my order number?"
    },
]

response = client.responses.create(
    model="gpt-5.5",
    input=conversation
)

print(response.output_text)