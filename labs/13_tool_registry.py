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


def cancel_order(order_id: str):
    return {
        "order_id": order_id,
        "status": "cancelled"
    }
    
tools = [
    {
        "type": "function",
        "name": "get_order_status",
        "description": "Get the current status of an order",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"}
            },
            "required": ["order_id"]
        }
    },
    {
        "type": "function",
        "name": "cancel_order",
        "description": "Cancel an order",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"}
            },
            "required": ["order_id"]
        }
    }
]    

tool_registry = {
    "get_order_status": get_order_status,
    "cancel_order": cancel_order
}

response = client.responses.create(
    model="gpt-5.5",
    input="Where is my order ORD-1234?",
    tools=tools
)

max_iterations = 5
iteration = 0

while iteration < max_iterations:
    iteration += 1
    print(f"\n --- Iterations {iteration}")
    tool_calls = [
        item
        for item in response.output
        if item.type == "function_call"
    ]

    if not tool_calls:
        print("\nFinal answer:")
        print(response.output_text)
        break

    tool_outputs = []

    for tool_call in tool_calls:

        arguments = json.loads(tool_call.arguments)

        tool_function = tool_registry.get(tool_call.name)

        if tool_function is None:
            raise ValueError(f"Unknown tool: {tool_call.name}")

        print(f"\nExecuting {tool_call.name}")
        print("Arguments:", arguments)

        result = tool_function(**arguments)

        print("Result:", result)

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
    
else:
    print("\nAgent stopped: maximum iterations reached.")