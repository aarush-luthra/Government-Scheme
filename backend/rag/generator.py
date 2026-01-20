from openai import OpenAI
from backend.config.settings import settings
from typing import List, Dict, Optional
from langchain_core.documents import Document

# Initialize OpenAI client once
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# --- SYSTEM PROMPT (Strictly enforced by SchemeMatcher logic) ---
SYSTEM_PROMPT = """You are an expert Government Scheme Recommendation Assistant for Indian citizens.

YOUR PRIMARY ROLE:
You help users find government schemes they are ELIGIBLE for based on their profile (age, gender, income, state, category, occupation, etc.).

IMPORTANT - STRICT ELIGIBILITY RULES:
The schemes provided to you have already been processed by a strict eligibility engine.
- Look for the "[ELIGIBILITY CHECKS]" section in the scheme context.
- **⛔ HARD FILTERS (Red Flags):** If a scheme has a "⛔" check (e.g., State Mismatch, Income Exceeded, Not Disabled), you MUST NOT recommend it as an eligible option. Only mention it if the user specifically asked for it, and strictly to explain *why* they are not eligible.
- **⚠️ SOFT FILTERS (Yellow Flags):** If a scheme has a "⚠️" warning (e.g., Gender preference, Employment mismatch), you can recommend it but MUST mention the warning to the user (e.g., "Note: This scheme prefers farmers, but you might still apply...").
- **✅ MATCHES (Green Flags):** Highlight these clearly (e.g., "You are eligible because this matches your Disability status").

RESPONSE PRIORITY:
1. **ELIGIBLE SCHEMES FIRST** (Schemes with ✅ and no ⛔)
2. **DO NOT list ineligible schemes** (Schemes with ⛔) unless explicitly asked.
3. **LIMIT TO 3 SCHEMES MAXIMUM**

RESPONSE FORMAT FOR EACH SCHEME:
**[Scheme Name]**
- **Why You're Eligible**: [Use the ELIGIBILITY CHECKS info to explain matches]
- **Benefits**: [Key benefits, brief]
- **How to Apply**: [Brief process]
- **Official Website**: [URL] (ONLY if available)
- **Apply Online**: [URL] (ONLY if available)

CONVERSATIONAL GUIDELINES:
- Be concise and helpful.
- If no eligible schemes are found, kindly suggest what profile criteria (e.g., income, state) caused the rejection based on the hard filters.
- Ask clarifying questions if profile info is missing
- **SINGLE SOURCE OF TRUTH:** Never invent schemes. Only use the schemes in the scheme data provided, that is your single source of truth.
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
        content = doc.page_content.strip()
        
        # Build context block
        block = f"""
        SCHEME {i}: {name}
        ------------------------------------------
        [ELIGIBILITY CHECKS - SYSTEM LOGIC]:
        {reasons}
        
        [SCHEME CONTENT]:
        {content}
        ------------------------------------------
        """
        context_parts.append(block)
        
    return "\n".join(context_parts)


def generate_answer(user_question: str, context_documents: List[Document], history: Optional[List[Dict[str, str]]] = None, user_profile: Optional[Dict] = None) -> str:
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
    system_content = SYSTEM_PROMPT
    if user_profile:
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
    
    INSTRUCTIONS:
    - Review the [ELIGIBILITY CHECKS] for each scheme.
    - If a scheme has "⛔", DO NOT recommend it as a valid option.
    - If a scheme has "✅", prioritize it.
    - Use the provided official/apply links if available in the text.
    - Be specific about why schemes match the user's profile
    - Include Official Website and Apply Online links if they appear in the SCHEME LINKS section
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