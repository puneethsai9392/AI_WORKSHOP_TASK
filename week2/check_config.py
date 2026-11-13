import os
from dotenv import load_dotenv

load_dotenv()

API_KEY=os.getenv('GROQ_API_KEY')
MODEL=os.getenv('GROQ_MODEL')

print('API CONFIGURED',bool(API_KEY))
print(' MODE CONFIGURED',bool(MODEL))