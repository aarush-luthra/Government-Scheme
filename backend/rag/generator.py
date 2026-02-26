from openai import OpenAI
from backend.config.settings import settings
from typing import List, Dict, Optional
from langchain_core.documents import Document

# Initialize OpenAI client once
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# --- SYSTEM PROMPTS ---
SIGNED_IN_SYSTEM_PROMPT = """You are an expert Government Scheme Recommendation Assistant for Indian citizens.

You are in SIGNED-IN mode. Provide personalized and actionable guidance.

MANDATORY RULES:
1. Use ONLY the schemes present in the provided context.
2. Never invent links, deadlines, or document requirements.
3. For each scheme, provide:
   - Status: Eligible ✅ / Possibly Eligible ⚠️ / Not Eligible ❌
   - Why this status was assigned (from eligibility checks and profile)
   - Benefits (short)
   - Required documents (if available, otherwise "Not clearly listed")
   - Deadline (if available, otherwise "Not specified")
   - Official/apply link (if present, otherwise "Not Provided")
4. If user asks for one scheme specifically, prioritize that scheme and keep alternatives minimal.
5. Keep answer concise and practical.
"""

GUEST_SYSTEM_PROMPT = """You are an expert Government Scheme Recommendation Assistant for Indian citizens.

You are in GUEST mode. Keep answers exploratory, low-friction, and informational.

MANDATORY RULES:
1. Use ONLY the schemes present in context.
2. Do not claim final eligibility. Use:
   - Likely Eligible ✅
   - Possibly Eligible ⚠️
   - Might Not Be Eligible ❌
3. For each scheme include:
   - Scheme name
   - One-line description
   - Major benefits
   - High-level eligibility summary
4. Keep recommendations informational and concise. Do not output repetitive closing lines.
5. Keep it simple and avoid asking for documents or sensitive IDs.
"""


def format_docs_for_context(documents: List[Document]) -> str:
    """
    Format retrieved documents into a string for the LLM context.
    Crucially, this extracts the 'eligibility_reasons' calculated by SchemeMatcher
    and presents them to the LLM so it knows WHY a user is eligible/ineligible.
    """
    context_parts = []
    
    if not documents:
        return "No relevant schemes found matching the user's profile and query."
        
    for i, doc in enumerate(documents, 1):
        # Extract metadata and content
        name = doc.metadata.get("scheme_name") or doc.metadata.get("title") or "Unknown Scheme"
        
        # This key 'eligibility_reasons' is populated by SchemeMatcher.rank_schemes()
        reasons = doc.metadata.get("eligibility_reasons", "No automated checks performed.")
        confidence = doc.metadata.get("match_confidence")
        if confidence is None:
            status_hint = "Possibly Eligible ⚠️"
        elif float(confidence) >= 0.75:
            status_hint = "Eligible ✅"
        elif float(confidence) >= 0.4:
            status_hint = "Possibly Eligible ⚠️"
        else:
            status_hint = "Not Eligible ❌"
        content = doc.page_content.strip()
        
        # Build context block
        block = f"""
        SCHEME {i}: {name}
        ------------------------------------------
        [STATUS HINT]:
        {status_hint}

        [ELIGIBILITY CHECKS - SYSTEM LOGIC]:
        {reasons}
        
        [SCHEME CONTENT]:
        {content}
        ------------------------------------------
        """
        context_parts.append(block)
        
    return "\n".join(context_parts)


def generate_answer(user_question: str, context_documents: List[Document], history: Optional[List[Dict[str, str]]] = None, user_profile: Optional[Dict] = None, mode: str = "signed_in") -> str:
    """
    Generate an answer using the LLM with strict eligibility matching.
    
    Args:
        user_question: The user's query.
        context_documents: List of Document objects returned by the Retriever (already filtered/ranked).
        history: Chat history.
        user_profile: User's profile dict.
    """
    # 1. Format the context string with eligibility logic
    formatted_context = format_docs_for_context(context_documents)
    
    # 2. Build system prompt with user profile context
    system_content = SIGNED_IN_SYSTEM_PROMPT if mode == "signed_in" else GUEST_SYSTEM_PROMPT
    if user_profile and mode == "signed_in":
        profile_context = build_profile_context(user_profile)
        if profile_context:
            system_content += f"\n\nUSER PROFILE (For Reference):\n{profile_context}"
    
    messages = [{"role": "system", "content": system_content}]
    
    # 3. Add history if available
    if history:
        for msg in history[-5:]:
            if msg.get("content"):
                messages.append({"role": msg.get("role"), "content": msg.get("content")})
    
    # 4. Add Context and Question
    user_message = f"""
    SCHEME INFORMATION (Pre-filtered by Engine):
    {formatted_context}
    
    USER QUESTION:
    {user_question}
    
    OUTPUT INSTRUCTIONS:
    - Review [STATUS HINT] and [ELIGIBILITY CHECKS] while writing status.
    - Keep to top 3 schemes unless user asks for more.
    - For links: only include explicit http/https links from context, else "Not Provided".
    - If no relevant scheme exists, clearly say so and suggest refining by state/category.
    """
    
    messages.append({"role": "user", "content": user_message})

    # 5. Call LLM
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.1, # Keep low for strict adherence to facts
    )

    return response.choices[0].message.content.strip()


def build_profile_context(profile: Dict) -> str:
    """Build a human-readable profile context string for eligibility matching."""
    parts = []
    
    # Basic Details
    if profile.get("fullName") or profile.get("name"):
        parts.append(f"- Name: {profile.get('fullName') or profile.get('name')}")
    if profile.get("age"):
        parts.append(f"- Age: {profile['age']} years")
    if profile.get("gender"):
        parts.append(f"- Gender: {str(profile['gender']).title()}")
    if profile.get("state"):
        parts.append(f"- State: {str(profile['state']).replace('_', ' ').title()}")
    if profile.get("area"):
        parts.append(f"- Area: {str(profile['area']).title()}")
        
    # Socio-Economic Details
    if profile.get("category"):
        parts.append(f"- Category: {str(profile['category']).upper()}")
    if profile.get("annual_income"):
        parts.append(f"- Annual Income: Rs. {profile['annual_income']:,}")
    if profile.get("employment_status"):
        parts.append(f"- Occupation: {str(profile['employment_status']).title()}")
        
    # Special Status Flags (Important for Hard Filters)
    if profile.get("is_student"):
        parts.append(f"- Status: Student")
    if profile.get("is_disabled"):
        parts.append(f"- Status: Person with Disability (PwD)")
    if profile.get("is_minority"):
        parts.append(f"- Status: Minority Community")
    if profile.get("is_govt_employee"):
        parts.append(f"- Status: Government Employee")
    
    return "\n".join(parts) if parts else "No specific profile data provided."

def generate_eligibility_query(user_profile: Dict) -> str:
    """
    Generate a search query based on user profile for finding relevant schemes.
    (Kept from original file as it might be used by the orchestrator)
    """
    query_parts = ["government scheme eligibility"]
    
    if user_profile.get("category"):
        query_parts.append(f"{user_profile['category']} category")
    if user_profile.get("state"):
        query_parts.append(f"{user_profile['state']} state")
    if user_profile.get("is_disabled"):
        query_parts.append("disability pension")
    if user_profile.get("is_student"):
        query_parts.append("scholarship")
        
    return " ".join(query_parts)
