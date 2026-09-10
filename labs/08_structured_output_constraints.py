from enum import Enum 

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

client = OpenAI()

class Intent(str, Enum):
    TRACK_ORDER = "track_order"
    CANCEL_ORDER = "cancel_order"
    RETURN_ORDER = "return_order"
    OTHER = "other"
    
class Urgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    
class OrderIntent(BaseModel):
    order_id: str
    intent: Intent
    urgency: Urgency
    requires_action: bool
    
response = client.responses.parse(
    model="gpt-5.5",
    input="""
    My order is ORD-5678 was supposed to arrive yesterday,
    I need it for an event tomorrow.
    Can you tell me where it is?
    """,
    text_format=OrderIntent,
    
)

result = response.output_parsed

print(result)
print()
print("Order ID:", result.order_id)
print("Intent:", result.intent)
print("Urgency:", result.urgency)
print("Requires action:", result.requires_action)