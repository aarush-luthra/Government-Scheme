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

def generate_answer(user_question: str, context: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""
Scheme Information:
{context}

User Question:
{user_question}
"""
            },
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()
