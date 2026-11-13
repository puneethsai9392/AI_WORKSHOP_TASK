
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL")

if not api_key or not MODEL:
    raise ValueError(
        "Check GROQ_API_KEY and GROQ_MODEL in .env"
    )

client = Groq(api_key=api_key)


# Generate context-aware response
def generate_response(messages: list[dict]) -> str:

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.2
    )

    answer = response.choices[0].message.content

    if not answer:
        raise RuntimeError(
            "The model returned an empty response"
        )

    return answer


if __name__ == "__main__":

    messages = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant."
        },
        {
            "role": "user",
            "content": "What is Python?"
        },
        {
            "role": "assistant",
            "content": "Python is a programming language."
        },
        {
            "role": "user",
            "content": "What are its advantages?"
        }
    ]

    answer = generate_response(messages)
    print(answer)
