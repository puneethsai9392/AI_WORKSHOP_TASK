from prompt_templates import create_prompt
from llm_client       import generate_response

message=" paid, but my order is not confirmed."

intent = "payment_issue"

prompt=create_prompt(message,intent)

answer=generate_response(prompt)

print('\n Assistant Response:')
print(answer)