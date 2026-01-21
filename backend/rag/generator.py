from openai import OpenAI
from backend.config.settings import settings
from typing import List, Dict, Optional

# Initialize OpenAI client once
client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """You are an expert Government Scheme Recommendation Assistant for Indian citizens.

YOUR PRIMARY ROLE:
You help users find government schemes they are ELIGIBLE for based on their profile (age, gender, income, state, category, occupation, etc.).

STRICT RULES:
1. ONLY recommend schemes from the "Scheme Information" provided below.
2. NEVER invent or hallucinate schemes not in the context.
3. Check eligibility criteria against the user's profile before recommending.

RESPONSE PRIORITY (Follow this order):
1. **ELIGIBLE SCHEMES FIRST** - Start with schemes the user clearly qualifies for
2. **POTENTIALLY RELEVANT** - Schemes with partial matches or unclear criteria
3. **DO NOT list schemes user is clearly NOT eligible for** unless they specifically ask
4. **LIMIT TO 3 SCHEMES MAXIMUM** - Only show the top 3 most relevant schemes, never more

RESPONSE FORMAT FOR EACH SCHEME:
**[Scheme Name]**
- **Why You're Eligible**: [Specific profile matches]
- **Benefits**: [Key benefits, brief]
- **How to Apply**: [Brief process]
- **Official Website**: [URL] (ONLY include this line if a URL is available, otherwise omit entirely)
- **Apply Online**: [URL] (ONLY include this line if a URL is available, otherwise omit entirely)

CONVERSATIONAL GUIDELINES:
- Be concise and helpful
- If no schemes match, suggest what profile changes might help
- Ask clarifying questions if profile info is missing

IMPORTANT: The scheme data is your SINGLE SOURCE OF TRUTH. Never assume eligibility without evidence.
"""


def generate_answer(user_question: str, context: str, history: Optional[List[Dict[str, str]]] = None, user_profile: Optional[Dict] = None) -> str:
    """
    Generate an answer using the LLM with strict eligibility matching.
    Includes scheme links (official_site and apply_link) when available.
    """
    # Build system prompt with user profile context if available
    system_content = SYSTEM_PROMPT
    if user_profile:
        profile_context = build_profile_context(user_profile)
        if profile_context:
            system_content += f"""

USER PROFILE (Use this for eligibility matching):
{profile_context}

When the user asks about schemes they're eligible for, carefully match their profile against the eligibility criteria in the scheme information. Only recommend schemes where the user clearly meets the requirements."""
    
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
    # Note: Links are now embedded directly in the context from document metadata
    user_message = f"""
SCHEME INFORMATION FROM DATABASE:
{context if context.strip() else "No relevant schemes found in database for this query."}

---

USER QUESTION:
{user_question}

INSTRUCTIONS:
- If recommending schemes, verify user eligibility against the criteria above
- Only mention schemes that are in the SCHEME INFORMATION section
- Be specific about why schemes match or don't match the user's profile
- Include Official Website and Apply Online links if they appear in the SCHEME LINKS section
"""
    
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.1,  # Lower temperature for more factual responses
    )

    return response.choices[0].message.content.strip()


def build_profile_context(profile: Dict) -> str:
    """Build a human-readable profile context string for eligibility matching."""
    parts = []
    
    if profile.get("fullName") or profile.get("name"):
        name = profile.get("fullName") or profile.get("name")
        parts.append(f"- Name: {name}")
    if profile.get("age"):
        parts.append(f"- Age: {profile['age']} years")
    if profile.get("gender"):
        gender_map = {"male": "Male", "female": "Female", "other": "Other"}
        parts.append(f"- Gender: {gender_map.get(profile['gender'], profile['gender'])}")
    if profile.get("state"):
        state_name = str(profile['state']).replace('_', ' ').title()
        parts.append(f"- State: {state_name}")
    if profile.get("area"):
        parts.append(f"- Area Type: {profile['area'].title()}")
    if profile.get("category"):
        category_map = {
            "general": "General", 
            "sc": "SC (Scheduled Caste)", 
            "st": "ST (Scheduled Tribe)", 
            "obc": "OBC (Other Backward Class)",
            "ews": "EWS (Economically Weaker Section)"
        }
        parts.append(f"- Social Category: {category_map.get(profile['category'], profile['category'])}")
    if profile.get("annual_income") or profile.get("income"):
        income = profile.get("annual_income") or profile.get("income")
        parts.append(f"- Annual Income: Rs. {income:,}")
    if profile.get("family_income"):
        parts.append(f"- Family Income: Rs. {profile['family_income']:,}")
    if profile.get("employment_status") or profile.get("occupation"):
        occupation = profile.get("employment_status") or profile.get("occupation")
        occupation_name = str(occupation).replace('_', ' ').title()
        parts.append(f"- Occupation/Employment: {occupation_name}")
    if profile.get("is_student"):
        parts.append(f"- Student Status: {'Yes, currently a student' if profile['is_student'] else 'No'}")
    if profile.get("is_disabled"):
        parts.append(f"- Disability Status: {'Yes, person with disability' if profile['is_disabled'] else 'No'}")
    if profile.get("is_minority"):
        parts.append(f"- Minority Status: {'Yes, belongs to minority community' if profile['is_minority'] else 'No'}")
    if profile.get("is_govt_employee"):
        parts.append(f"- Government Employee: {'Yes' if profile['is_govt_employee'] else 'No'}")
    if profile.get("language"):
        lang_map = {
            "en": "English", "hi": "Hindi", "te": "Telugu", "ta": "Tamil", 
            "kn": "Kannada", "ml": "Malayalam", "mr": "Marathi", "bn": "Bengali", 
            "gu": "Gujarati", "pa": "Punjabi", "or": "Odia", "as": "Assamese"
        }
        parts.append(f"- Preferred Language: {lang_map.get(profile['language'], profile['language'])}")
    
    return "\n".join(parts) if parts else ""


def generate_eligibility_query(user_profile: Dict) -> str:
    """
    Generate a search query based on user profile for finding relevant schemes.
    """
    query_parts = []
    
    # Add category-based queries
    if user_profile.get("category"):
        cat = user_profile.get("category", "").lower()
        if cat in ["sc", "st", "obc"]:
            query_parts.append(f"{cat.upper()} category schemes")
    
    # Add gender-based queries
    if user_profile.get("gender") == "female":
        query_parts.append("women schemes girl")
    
    # Add student-based queries
    if user_profile.get("is_student"):
        query_parts.append("student scholarship education")
    
    # Add disability-based queries
    if user_profile.get("is_disabled"):
        query_parts.append("disability disabled divyang")
    
    # Add employment-based queries
    employment = user_profile.get("employment_status") or user_profile.get("occupation")
    if employment:
        if "farmer" in str(employment).lower():
            query_parts.append("farmer agriculture")
        elif "business" in str(employment).lower() or "entrepreneur" in str(employment).lower():
            query_parts.append("business entrepreneur startup")
        elif "unemployed" in str(employment).lower():
            query_parts.append("employment skill training job")
    
    # Add state-specific queries
    if user_profile.get("state"):
        query_parts.append(f"{user_profile['state']} state")
    
    # Default query
    if not query_parts:
        query_parts.append("government scheme eligibility")
    
    return " ".join(query_parts)


GENERAL_SYSTEM_PROMPT = """You are a helpful Government Scheme Assistant for India.
Your primary purpose is to help people find and understand government schemes.

However, the user has asked a general question that doesn't seem to be about looking up specific schemes.
1. Answer their question specifically and helpfully.
2. If appropriate, gently guide them back to your main purpose (finding government schemes).
3. Do NOT invent government schemes or try to force a scheme recommendation if it doesn't make sense.
4. Keep the tone professional, kind, and helpful.
"""

def generate_general_reply(user_question: str, history: Optional[List[Dict[str, str]]] = None, user_profile: Optional[Dict] = None) -> str:
    """
    Generate a reply for general conversation without scheme context.
    """
    messages = [{"role": "system", "content": GENERAL_SYSTEM_PROMPT}]
    
    # Add profile context if available (just for personalization)
    if user_profile:
        name = user_profile.get("fullName") or user_profile.get("name")
        if name:
            messages.append({"role": "system", "content": f"The user's name is {name}."})
    
    # Add history
    if history:
        for msg in history[-3:]: # Keep history short for general chat
            role = msg.get("role")
            content = msg.get("content")
            if role in ["user", "assistant"] and content:
                messages.append({"role": role, "content": content})
                
    messages.append({"role": "user", "content": user_question})
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7, # Slightly higher temperature for more natural conversation
    )

    return response.choices[0].message.content.strip()
