import os
from dotenv import  load_dotenv
from groq import Groq

load_dotenv()

api_key=os.getenv('GROQ_API_KEY')
MODEL=os.getenv('GROQ_MODEL')

if not api_key or not MODEL:
    raise ValueError(
         "Check GROQ_API_KEY and GROQ_MODEL in .env"
    )
client=Groq(api_key=api_key)

def generate_response(prompt:str)->str:
    response=client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                'role':'user',
                'content':prompt
            }
        ],
        temperature=0.2
    )

    answer = response.choices[0].message.content

    if not answer:
        raise RuntimeError('The model returned an empty response')
    return answer

if __name__ == "__main__":
    answer = generate_response(
        "Explain machine learning in two simple sentences."
    )
    print(answer)


