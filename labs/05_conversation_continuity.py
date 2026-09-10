from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()
 
response1 = client.responses.create(
     model="gpt-5.5",
     input="My order numberis ORD-1234. Remember it."
)

print("First response:")
print(response1.output_text) 

print("\nResponse ID:", response1.id)

response2 = client.responses.create(
    model="gpt-5.5",
    previous_response_id=response1.id,
    input="What is my order number"
)

print("Second response:")
print(response2.output_text)