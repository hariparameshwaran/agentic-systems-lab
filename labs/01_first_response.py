from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

response = client.responses.create(
    model="gpt-5.5",
    input="Explain what an order management system is in one sentence."
)

print("Response ID:", response.id)
print("Model:", response.model)
print("Status:", response.status)
print("Input tokens:", response.usage.input_tokens)
print("Output tokens:", response.usage.output_tokens)
print("Total tokens:", response.usage.total_tokens)
print("Answer:", response.output_text)