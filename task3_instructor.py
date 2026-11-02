import os 
import re 
import instructor

from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel , Field, EmailStr , field_validator

load_dotenv()

class UserProfile(BaseModel):
    name:str=Field(min_length=2,max_length=50)
    age:int=Field(ge=18,le=100)
    email:EmailStr
    pan:str

    @field_validator('name')
    @classmethod
    def validate_name(cls,value):
        if not value.strip():
            raise ValueError('Name cannot be empty')
        return value.strip()

    @field_validator('pan')
    @classmethod
    def validate_pan(cls,value):
        value=value.strip().upper()

        pattren=r"^[A-Z]{5}[0-9]{4}[A-Z]$"
        if not re.fullmatch(pattren,value):
            raise ValueError('Invalid Pan Format')
        return value
api_key=os.getenv('GROQ_API_KEY')

if not api_key:
    raise ValueError('Groq_api_key not found in .env')

client=instructor.from_groq(
    Groq(api_key=api_key),
    mode=instructor.Mode.JSON
)

try:
    user=client.chat.completions.create(
        model="openai/gpt-oss-120b",
        response_model=UserProfile,
        messages=[
            {
                'role':'system',
                'content':(
                    "Generate a fictional example user profile. "
                    "Use a valid example email and a syntactically "
                    "valid example PAN. Do not claim the details "
                    "belong to a real person."
                )
            },
            {
                'role':'user',
                'content':(
                     "Create a fictional profile for an adult named Rahul, "
                    "age 25, with a valid example email and PAN format."
                )
            }
        ],
        max_retries=2
    )

    print('='*60)

    print("Structured Pydantic Object")

    print('='*60)
    print()
    print(user)

    print('\nJSON Response')
    print(user.model_dump_json(indent=2))

except Exception as e:
    print("LLM request or validation failed:", e)



