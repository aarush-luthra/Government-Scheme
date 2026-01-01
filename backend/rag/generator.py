from openai import OpenAI
from backend.config.settings import settings

# Initialize OpenAI client once
client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are a government welfare scheme assistant.
Answer only using the provided scheme information.
If information is missing, say it is not available.
Use simple language.
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
