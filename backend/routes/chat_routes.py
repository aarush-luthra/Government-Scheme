from fastapi import APIRouter
from backend.rag.retriever import VectorStoreRetriever

router = APIRouter()
retriever = VectorStoreRetriever()

@router.post("/chat-with-document")
def chat_with_document(payload: dict):
    """
    payload = {
        "message": "What schemes am I eligible for?",
        "extracted_fields": {
            "name": "...",
            "dob": "...",
            "category": "SC",
            "income": 180000
        }
    }
    """

    user_message = payload.get("message", "")
    fields = payload.get("extracted_fields", {})

    # Convert extracted fields into chatbot context
    context = (
        f"User details:\n"
        f"Category: {fields.get('category')}\n"
        f"Income: {fields.get('income')}\n"
        f"Date of Birth: {fields.get('dob')}\n"
    )

    # Combine context + user question
    final_query = context + "\nUser question: " + user_message

    response = retriever.query(final_query)

    return {
        "reply": response
    }
