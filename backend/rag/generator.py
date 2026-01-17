from openai import OpenAI
from backend.config.settings import settings
from typing import List, Dict, Optional

# Initialize OpenAI client once
client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """You are an expert Government Scheme Recommendation Assistant for Indian citizens.

YOUR PRIMARY ROLE:
You help users find government schemes they are ELIGIBLE for based on their profile (age, gender, income, state, category, occupation, etc.).

STRICT RULES - YOU MUST FOLLOW THESE:
1. ONLY recommend schemes that appear in the "Scheme Information" provided below.
2. NEVER invent or hallucinate schemes that are not in the provided context.
3. If asked about a scheme not in the context, say: "I don't have information about that specific scheme in my database."
4. When recommending schemes, ALWAYS check the eligibility criteria against the user's profile.
5. If a user's profile doesn't match ANY scheme's eligibility, clearly state this.
6. Quote the actual eligibility requirements from the scheme data.
7. Explain WHY a scheme matches or doesn't match the user's profile.

RESPONSE FORMAT FOR SCHEME RECOMMENDATIONS:
For each recommended scheme, provide:
- **Scheme Name**: [Title]
- **Why You're Eligible**: [Explain how user's profile matches eligibility]
- **Key Benefits**: [Brief summary]
- **How to Apply**: [Brief summary if available]

HANDLING USER QUERIES:
- If user greets you, respond warmly and ask about their needs
- If user asks general questions, answer conversationally
- If user asks "what schemes am I eligible for", analyze their profile against ALL schemes in context
- If user asks about a specific scheme, provide details ONLY if it's in the context
- If scheme is not in context, clearly state you don't have that information

IMPORTANT: The scheme eligibility data is your SINGLE SOURCE OF TRUTH. Do not make assumptions beyond what the data states.
"""


def generate_answer(user_question: str, context: str, history: Optional[List[Dict[str, str]]] = None, user_profile: Optional[Dict] = None) -> str:
    """
    Generate an answer using the LLM with strict eligibility matching.
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
