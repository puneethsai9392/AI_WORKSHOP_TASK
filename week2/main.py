
import os
from uuid import uuid4, UUID

import psycopg
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from llm_client import generate_response
from prompt_templates import create_prompt


app = FastAPI()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable is missing")

    return psycopg.connect(DATABASE_URL, connect_timeout=10)


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


@app.get("/health")
def health():
    return {"status": "ok"}


# Send message
@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    is_new_conversation = request.session_id is None

    # Generate or retrieve conversation ID
    if is_new_conversation:
        conversation_id = uuid4()
        history = []

    else:
        try:
            conversation_id = UUID(request.session_id)
        except ValueError:
            raise HTTPException(
                status_code=404,
                detail="Invalid chat session"
            )

        try:
            with get_connection() as conn:
                with conn.cursor() as cur:

                    cur.execute(
                        "SELECT id FROM conversations WHERE id = %s",
                        (conversation_id,)
                    )

                    if cur.fetchone() is None:
                        raise HTTPException(
                            status_code=404,
                            detail="Chat session not found"
                        )

                    cur.execute(
                        """
                        SELECT role, content
                        FROM messages
                        WHERE conversation_id = %s
                        ORDER BY created_at, id
                        """,
                        (conversation_id,)
                    )

                    history = [
                        {"role": row[0], "content": row[1]}
                        for row in cur.fetchall()
                    ]

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=503,
                detail="Database connection failed"
            )

    # Prepare messages for Groq
    messages = [
        {
            "role": "system",
            "content": create_prompt(
                request.message,
                request.intent
            )
        }
    ] + history + [
        {
            "role": "user",
            "content": request.message
        }
    ]

    # Generate AI response
    try:
        ai_response = generate_response(messages)

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Unable to generate AI response. Please try again."
        )

    # Save conversation and messages in Supabase
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:

                if is_new_conversation:
                    cur.execute(
                        """
                        INSERT INTO conversations (id, title)
                        VALUES (%s, %s)
                        """,
                        (conversation_id, request.message[:60])
                    )

                cur.execute(
                    """
                    INSERT INTO messages
                    (conversation_id, role, content)
                    VALUES (%s, %s, %s), (%s, %s, %s)
                    """,
                    (
                        conversation_id,
                        "user",
                        request.message,
                        conversation_id,
                        "assistant",
                        ai_response
                    )
                )

                cur.execute(
                    """
                    UPDATE conversations
                    SET updated_at = NOW()
                    WHERE id = %s
                    """,
                    (conversation_id,)
                )

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Unable to save conversation to database"
        )

    return ChatResponse(
        session_id=str(conversation_id),
        intent=request.intent,
        response=ai_response
    )


# Get chat history
@app.get("/api/chat/{session_id}/history")
def get_history(session_id: str):

    try:
        conversation_id = UUID(session_id)

        with get_connection() as conn:
            with conn.cursor() as cur:

                cur.execute(
                    "SELECT id FROM conversations WHERE id = %s",
                    (conversation_id,)
                )

                if cur.fetchone() is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Chat session not found"
                    )

                cur.execute(
                    """
                    SELECT role, content, created_at
                    FROM messages
                    WHERE conversation_id = %s
                    ORDER BY created_at, id
                    """,
                    (conversation_id,)
                )

                messages = [
                    {
                        "role": row[0],
                        "content": row[1],
                        "created_at": row[2].isoformat()
                    }
                    for row in cur.fetchall()
                ]

        return {
            "session_id": session_id,
            "messages": messages
        }

    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Invalid chat session"
        )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Unable to retrieve chat history"
        )


# Delete conversation
@app.delete("/api/chat/{session_id}")
def delete_session(session_id: str):

    try:
        conversation_id = UUID(session_id)

        with get_connection() as conn:
            with conn.cursor() as cur:

                cur.execute(
                    "DELETE FROM conversations WHERE id = %s",
                    (conversation_id,)
                )

                if cur.rowcount == 0:
                    raise HTTPException(
                        status_code=404,
                        detail="Chat session not found"
                    )

        return {
            "message": "Session deleted successfully"
        }

    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Invalid chat session"
        )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Unable to delete conversation"
        )
