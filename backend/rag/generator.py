from openai import OpenAI
from backend.config.settings import settings

# Initialize OpenAI client once
client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are a helpful and friendly government welfare scheme assistant.
Your goal is to assist users with information about government schemes.

Guidelines:
1. If the user greets you or asks a general question, respond conversationally and politely.
2. If the user asks about a specific scheme, use the provided "Scheme Information" to answer.
3. If the provided context does not contain the answer to a specific question, politely state that you don't have that specific information, but offer to help with something else.
4. Do NOT simply say "not available" without explanation.
5. Use simple, easy-to-understand language.
"""

from typing import List, Dict, Optional

def generate_answer(user_question: str, context: str, history: Optional[List[Dict[str, str]]] = None) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add history if available
    if history:
        # Validate and add last 5 messages to keep context window manageable
        for msg in history[-5:]:
            role = msg.get("role")
            content = msg.get("content")
            if role in ["user", "assistant"] and content:
                messages.append({"role": role, "content": content})
    
    # Add current context and question
    messages.append({
        "role": "user",
        "content": f"""
Scheme Information:
{context}

User Question:
{user_question}
"""
    })

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()
