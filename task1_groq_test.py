import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key=os.getenv('GROQ_API_KEY')

if not api_key:
    raise ValueError('GROQ_API_KEY NOT FOUND IN .ENV')

client=Groq(api_key=api_key)
response=client.chat.completions.create(

    model="openai/gpt-oss-120b",
    messages=[
        {
            'role':"user",
            "content":'Explain llm and rag connection'
        }

        

    ],
    temperature=0.2
)
print(response.choices[0].message.content)
