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
                    "type": "string"
                }
            },
            "required": ["order_id"]
        }
    }
]


response = client.responses.create(
    model="gpt-5.5",
    input="Where is my order ORD-1234?",
    tools=tools
)


while True:

    print("\nModel output:")
    print(response.output)

    tool_calls = [
        item for item in response.output
        if item.type == "function_call"
    ]

    if not tool_calls:
        print("\nFinal answer:")
        print(response.output_text)
        break

    tool_outputs = []

    for tool_call in tool_calls:

        arguments = json.loads(tool_call.arguments)

        print("\nExecuting:")
        print(tool_call.name, arguments)

        if tool_call.name == "get_order_status":
            result = get_order_status(**arguments)

        tool_outputs.append(
            {
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": json.dumps(result)
            }
        )

    response = client.responses.create(
        model="gpt-5.5",
        previous_response_id=response.id,
        input=tool_outputs,
        tools=tools
    )