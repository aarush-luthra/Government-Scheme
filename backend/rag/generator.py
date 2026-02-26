from openai import OpenAI
from backend.config.settings import settings
from typing import List, Dict, Optional
from langchain_core.documents import Document

# Initialize OpenAI client once
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# --- SYSTEM PROMPT (Strictly enforced by SchemeMatcher logic) ---
SYSTEM_PROMPT = """You are an expert Government Scheme Recommendation Assistant for Indian citizens.

YOUR PRIMARY ROLE:
You help users find and understand government schemes.

INTENT VS ELIGIBILITY PROTOCOL:
1. **CASE A: Informational / Specific Topic Queries** (DEFAULT MODE)
   - **Examples:** "Schemes for farmers", "Details about PM Kisan", "Education loans", "What is available?"
   - **ACTION:** SHOW ALL MATCHES provided in the context.
   - **RULE:** If a scheme matches the topic but has `⛔` (Ineligible per profile), SHOW IT anyway.
   - **WARNING:** Preface incompatible schemes with: *"Note: Based on your profile, you may not be eligible for this, but here are the details..."*

2. **CASE B: Specific "For Me" / Eligibility Queries** (STRICT MODE)
   - **Trigger Keywords:** "for me", "am I eligible", "my eligible schemes", "what can I apply for".
   - **ACTION:** STRICT FILTERING.
   - **RULE:** HIDE schemes with `⛔` (Hard Filter Fail).
   - **OUTPUT:** If nothing matches, say "I couldn't find schemes purely matching your profile."

3. **CASE C: Specific Scheme Lookup**
   - **Examples:** "Tell me about [Scheme Name]", "How to apply for [Scheme Name]", "[Scheme Name]".
   - **ACTION:** Prioritize the EXACT match.
   - **RULE:** If the context contains the specific scheme requested, show THAT ONE first and predominantly.
   - **RULE:** Only list other retrieved schemes if they are highly relevant alternatives. If they are just vector search noise, ignore them.

ELIGIBILITY LOGIC (Review [ELIGIBILITY CHECKS] in scheme context):
- **⛔ HARD FILTERS:** User is technically ineligible.
- **✅ MATCHES:** Perfect match.

RESPONSE FORMAT:
**[Scheme Name]**
- **Status**: [Eligible ✅ / Not Eligible ⛔ / Info Only (Guest)]
- **Reason**: [Explain match/mismatch from [ELIGIBILITY CHECKS]]
- **Details**: [Benefits]
- **Links**: [Official/Apply] (If 'Links Not Provided', write 'Not Provided'. DO NOT use '#')

DYNAMIC ADAPTATION (Override above format if user asks for specific aspects):
- **If user asks "How to apply for X"**: Show ONLY the **Application Process** and **Links**. Omit eligibility/benefits unless critical.
- **If user asks "Eligibility for X"**: Show ONLY the **Eligibility Criteria** and **Status (✅/⛔)**. Omit application process.
- **If user asks "Benefits of X"**: Show ONLY the **Benefits/Details**.

CONVERSATIONAL GUIDELINES:
- **Default to Helpful:** If unsure of intent, show the information with a warning.
- **Single Source of Truth:** Only use provided schemes. Do NOT invent links.
"""


GENERAL_SYSTEM_PROMPT = """You are a helpful and friendly Government Scheme Assistant for India.
- Your goal is to help users find government schemes they are eligible for.
- If the user asks general questions ("How are you?", "Who are you?"), allow casual conversation but gently steer them back to finding schemes.
- Do NOT halluncinate specific scheme details. If asked about a scheme, say you need to look it up (which will happen in the next turn if they ask correctly).
- Keep responses concise and encouraging.
"""


def generate_general_reply(user_question: str, history: Optional[List[Dict[str, str]]] = None) -> str:
    """
    Generate a reply for general conversation (greeting, help, small talk) without RAG context.
    Disables strict filtering mode for a more natural conversation.
    """
    messages = [{"role": "system", "content": GENERAL_SYSTEM_PROMPT}]
    
    if history:
        for msg in history[-3:]:
             if msg.get("content"):
                messages.append({"role": msg.get("role"), "content": msg.get("content")})
    
    messages.append({"role": "user", "content": user_question})
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7, 
    )
    return response.choices[0].message.content.strip()


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
    - If a scheme has "✅", prioritize it.
    - **LINKS STRATEGY:** ONLY output official URLs (starting with http/https) that are EXPLICITLY provided in the Scheme Content.
    - DO NOT HALLUCINATE LINKS. Do not invent "Apply Here", "User Manual", or "Login" links if the URL is not in the text.
    - If no HTTP link is found, write "Official links not provided in database."
    
    IMPORTANT USER CONTEXT:
    { "User is a GUEST (No Profile). DEFAULT Status is 'Info Only'. HOWEVER, if the user provides specific details (Age, State, Qualification, Category) in the chat, YOU MUST ESTIMATE ELIGIBILITY. Mark as 'Likely Eligible ✅' or 'Likely Not Eligible ⛔' based on the provided details." if not user_profile else "User is LOGGED IN. You MUST determine eligibility status (✅/⛔) based on the [ELIGIBILITY CHECKS]. \n    CONVERSATIONAL OVERRIDE: If the user provides NEW profile details (e.g. 'I have 2 hectares land') in the chat history that fixes a previous rejection reason, YOU MUST RE-EVALUATE eligibility using the new info. OVERRIDE the system's '⛔' status to 'Verified Eligible ✅' if the new info satisfies the criteria found in the Scheme Content or previous messages." }
    
    FOCUS INSTRUCTIONS:
    {
    "User asked for ELIGIBILITY CRITERIA specifically. Output ONLY the Eligibility Criteria and Status. Do NOT show Application Process or Benefits. IGNORE schemes that are not an exact match to the requested name." if any(k in user_question.lower() for k in ["eligibility criteria", "who can apply", "criteria for", "check eligibility"]) else
    "User asked for APPLICATION PROCESS. Output ONLY the Application Steps and Links. Do NOT show Eligibility or Benefits. IGNORE schemes that are not an exact match." if any(k in user_question.lower() for k in ["how to apply", "application", "procedure", "apply"]) else
    "User asked for BENEFITS. Output ONLY the Benefits/Details. IGNORE schemes that are not an exact match." if any(k in user_question.lower() for k in ["benefit", "what do i get", "amount", "incentive"]) else
    "COMPREHENSIVE MODE (Default): The user wants to know about schemes. Filter strictly: ONLY show schemes where Status is 'Eligible ✅'. DO NOT show 'Not Eligible ⛔' schemes. Limit to the TOP 3 most relevant schemes. For each, provide: 1. Status 2. Description/Benefits 3. Criteria 4. Application 5. Links."
    }
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