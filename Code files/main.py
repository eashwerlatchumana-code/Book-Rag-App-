from openai import OpenAI
from dotenv import load_dotenv
import os 
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
userquestion= input("Enter a question you want to ask gpt4:")
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": f"{userquestion}"}
    ]
)

print(response.choices[0].message.content)