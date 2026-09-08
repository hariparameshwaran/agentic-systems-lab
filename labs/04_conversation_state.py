from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

# First request
response1 = client.responses.create(
    model="gpt-5.5",
    input="My order number is ORD-1234. Remember it."
)

print("First response:")
print(response1.output_text)

print("\n-------------------------\n")

# Second, independent request
response2 = client.responses.create(
    model="gpt-5.5",
    input="What is my order number?"
)

print("Second response:")
print(response2.output_text)