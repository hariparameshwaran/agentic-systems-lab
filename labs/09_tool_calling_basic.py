from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

client = OpenAI()

def get_order_status(order_id: str):
    return {
        "order_id": order_id,
        "status": "shipped",
        "expected_delivery": "2026-09-11"
    }

tools = [
    {
        "type": "function",
        "name": "get_order_status",
        "description": "Get the current status of an order",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order identifier"
                }
            },
            "required": ["order_id"]
        }
    }
]

response = client.responses.create(
    model="gpt-5.5",
    input="Where is my order ORD-1234",
    tools=tools
)

print(response.output)