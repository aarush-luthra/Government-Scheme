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

def generate_answer(user_question: str, context: str, history: Optional[List[Dict[str, str]]] = None, user_profile: Optional[Dict] = None) -> str:
    # Build system prompt with user profile context if available
    system_content = SYSTEM_PROMPT
    if user_profile:
        profile_context = build_profile_context(user_profile)
        if profile_context:
            system_content += f"\n\nUser Profile Information:\n{profile_context}\n\nUse this profile information to provide personalized scheme recommendations. When the user asks about themselves or relevant schemes, refer to this profile data."
    
    messages = [{"role": "system", "content": system_content}]
    
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


def build_profile_context(profile: Dict) -> str:
    """Build a human-readable profile context string."""
    parts = []
    
    if profile.get("fullName"):
        parts.append(f"- Name: {profile['fullName']}")
    if profile.get("age"):
        parts.append(f"- Age: {profile['age']} years")
    if profile.get("gender"):
        gender_map = {"male": "Male", "female": "Female", "other": "Other"}
        parts.append(f"- Gender: {gender_map.get(profile['gender'], profile['gender'])}")
    if profile.get("state"):
        state_name = profile['state'].replace('_', ' ').title()
        parts.append(f"- State: {state_name}")
    if profile.get("category"):
        category_map = {"general": "General", "sc": "SC (Scheduled Caste)", "st": "ST (Scheduled Tribe)", "obc": "OBC (Other Backward Class)"}
        parts.append(f"- Social Category: {category_map.get(profile['category'], profile['category'])}")
    if profile.get("income"):
        parts.append(f"- Annual Income: Rs. {profile['income']:,}")
    if profile.get("occupation"):
        occupation_name = profile['occupation'].replace('_', ' ').title()
        parts.append(f"- Occupation: {occupation_name}")
    if profile.get("language"):
        lang_map = {"en": "English", "hi": "Hindi", "te": "Telugu", "ta": "Tamil", "kn": "Kannada", "ml": "Malayalam", "mr": "Marathi", "bn": "Bengali", "gu": "Gujarati", "pa": "Punjabi", "or": "Odia", "as": "Assamese"}
        parts.append(f"- Preferred Language: {lang_map.get(profile['language'], profile['language'])}")
    
    return "\n".join(parts)
