from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.rag.retriever import VectorStoreRetriever
from backend.rag.generator import generate_answer
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Government Scheme Assistant")

# ✅ CORRECT CORS CONFIG
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # allow frontend
    allow_credentials=True,
    allow_methods=["*"],           # allow OPTIONS, POST, etc
    allow_headers=["*"],
)

retriever = VectorStoreRetriever()


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
async def chat(req: ChatRequest):
    docs = retriever.search(req.message, k=4)

    if not docs:
        return {
            "reply": "I do not have information about this. Please specify the scheme name."
        }

    context = "\n\n".join([doc.page_content for doc in docs])

    reply = generate_answer(
        user_question=req.message,
        context=context,
    )

    return {"reply": reply}
