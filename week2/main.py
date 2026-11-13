
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from uuid import uuid4

from llm_client import generate_response
from prompt_templates import create_prompt

app = FastAPI()

# React frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://rino-ai-rust.vercel.app"
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# In-memory chat storage
chat_sessions = {}


# Request model
class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=4000)
    intent: str = "general_question"
    session_id: str | None = None


# Response model
class ChatResponse(BaseModel):
    session_id: str
    intent: str
    response: str


# Create new session
def create_session():
    session_id = str(uuid4())
    chat_sessions[session_id] = []
    return session_id


@app.get("/health")
def health():
    return {"status": "ok"}


# Send message
@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    # Task 1: Generate or retrieve session
    if request.session_id is None:
        session_id = create_session()
    else:
        session_id = request.session_id

        if session_id not in chat_sessions:
            raise HTTPException(
                status_code=404,
                detail="Chat session not found"
            )

    history = chat_sessions[session_id]

    # Task 2: Store user message
    history.append({
        "role": "user",
        "content": request.message
    })

    # Task 3: Send history to Groq
    messages = [
    {
        "role": "system",
        "content": create_prompt(
            request.message,
            request.intent
        )
    }
] + history.copy()

    try:
        ai_response = generate_response(messages)

        # Store AI response
        history.append({
            "role": "assistant",
            "content": ai_response
        })

        return ChatResponse(
            session_id=session_id,
            intent=request.intent,
            response=ai_response
        )

    except Exception:
        # Remove failed user message
        history.pop()

        raise HTTPException(
            status_code=502,
            detail="Unable to generate AI response. Please try again."
        )


# Get chat history
@app.get("/api/chat/{session_id}/history")
def get_history(session_id: str):

    if session_id not in chat_sessions:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found"
        )

    return {
        "session_id": session_id,
        "messages": chat_sessions[session_id]
    }


# Delete chat session
@app.delete("/api/chat/{session_id}")
def delete_session(session_id: str):

    if session_id not in chat_sessions:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found"
        )

    del chat_sessions[session_id]

    return {
        "message": "Session deleted successfully"
    }
