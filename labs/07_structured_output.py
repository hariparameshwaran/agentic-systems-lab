from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

client = OpenAI()

class OrderIntent(BaseModel):
    order_id: str
    intent: str
    urgency: str
    requires_action: bool
    
response = client.responses.parse(
    model="gpt-5.5",
    input="""
    Customer message:
    
    My order ORD-1234 was supposed to arrive yesterday.
    It still hasn't arrived and I need it urgently
    """,
    text_format=OrderIntent,
)

result = response.output_parsed

print(result)
print()
print("Order ID:", result.order_id)
print("Inten:", result.intent)
print("Urgency:", result.urgency)
print("Requires action:", result.requires_action)