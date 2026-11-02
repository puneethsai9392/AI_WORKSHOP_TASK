from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from fastapi.middleware.cors import CORSMiddleware 

from prompt_templates import create_prompt
from llm_client import generate_response

app = FastAPI(title="Week 2 LLM Response API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message:str=Field(min_length=2,max_length=4000)
    intent:str=Field(min_length=2)

class ChatResponce(BaseModel):
    intent:str
    response:str

@app.get('/health')
def health():
    return {'status':'ok'}

@app.post('/api/chat',response_model=ChatResponce)
def chat(request:ChatRequest):
    try:
        prompt=create_prompt(
            request.message,
            request.intent
        )
        answer=generate_response(prompt)
        answer = fix_markdown_tables(answer)

        return ChatResponce(
            intent=request.intent,
            response=answer
        )
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail="Failed to generate an LLM response."
        ) from error



    
import re


def fix_markdown_tables(text: str) -> str:
    # Convert escaped pipes into normal Markdown pipes
    text = text.replace(r"\|", "|")

    fixed_lines = []

    for line in text.splitlines():
        # Only process lines that look like collapsed Markdown tables
        if line.count("|") < 6 or not re.search(r"-{3,}", line):
            fixed_lines.append(line)
            continue

        cells = [
            cell.strip()
            for cell in line.strip().strip("|").split("|")
            if cell.strip()
        ]

        # Find the Markdown table separator cells
        separator_index = next(
            (
                i for i, cell in enumerate(cells)
                if re.fullmatch(r":?-{3,}:?", cell)
            ),
            -1
        )

        if separator_index <= 0:
            fixed_lines.append(line)
            continue

        columns = separator_index
        separators = cells[separator_index:separator_index + columns]

        if (
            len(separators) != columns
            or not all(re.fullmatch(r":?-{3,}:?", c) for c in separators)
        ):
            fixed_lines.append(line)
            continue

        data = cells[separator_index + columns:]

        # Avoid changing the line if its table rows cannot be grouped evenly
        if not data or len(data) % columns != 0:
            fixed_lines.append(line)
            continue

        rows = [cells[:columns], separators]

        for i in range(0, len(data), columns):
            rows.append(data[i:i + columns])

        for row in rows:
            fixed_lines.append("| " + " | ".join(row) + " |")

    return "\n".join(fixed_lines)

