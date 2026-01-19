"""
Scheme Matcher Agent - Profile-based scheme eligibility matching.
"""
from typing import Dict, List, Optional, Tuple


class SchemeMatcher:
    """
    Mini-agent that matches user profiles against scheme eligibility criteria.
    """
    
    @staticmethod
    def extract_search_queries(user_profile: Dict) -> List[str]:
        """
        Generate multiple search queries based on user profile characteristics.
        Returns a list of queries to maximize recall.
        """
        queries = []
        
        # Base eligibility query
        queries.append("eligibility criteria requirements")
        
        # Category-specific queries
        category = (user_profile.get("category") or "").lower()
        if category == "sc":
            queries.append("scheduled caste SC eligibility schemes")
        elif category == "st":
            queries.append("scheduled tribe ST eligibility schemes")
        elif category == "obc":
            queries.append("other backward class OBC eligibility schemes")
        elif category == "ews":
            queries.append("economically weaker section EWS eligibility")
        
        # Gender-specific queries
        gender = (user_profile.get("gender") or "").lower()
        if gender == "female":
            queries.append("women girl female eligibility schemes benefits")
        
        # Age-specific queries
        age = user_profile.get("age")
        if age:
            if age < 18:
                queries.append("child minor student youth schemes")
            elif age < 30:
                queries.append("youth young adult student schemes")
            elif age < 60:
                queries.append("adult working age schemes")
            else:
                queries.append("senior citizen elderly pension schemes")
        
        # Student queries
        if user_profile.get("is_student"):
            queries.append("student scholarship education study eligibility")
        
        # Disability queries
        if user_profile.get("is_disabled"):
            queries.append("disability disabled divyang PwD handicapped eligibility")
        
        # Minority queries
        if user_profile.get("is_minority"):
            queries.append("minority community eligibility schemes")
        
        # Employment/Occupation queries
        employment = user_profile.get("employment_status") or user_profile.get("occupation")
        if employment:
            emp_lower = str(employment).lower()
            if "farmer" in emp_lower or "agriculture" in emp_lower:
                queries.append("farmer agriculture agricultural eligibility schemes")
            elif "business" in emp_lower or "entrepreneur" in emp_lower:
                queries.append("business entrepreneur startup self employed schemes")
            elif "unemployed" in emp_lower:
                queries.append("unemployed job employment skill training schemes")
            elif "student" in emp_lower:
                queries.append("student scholarship education eligibility")
        
        # Income-based queries
        annual_income = user_profile.get("annual_income") or user_profile.get("income")
        if annual_income:
            if annual_income < 100000:
                queries.append("low income below poverty BPL eligibility")
            elif annual_income < 300000:
                queries.append("income limit 2 lakh 3 lakh eligibility")
            elif annual_income < 600000:
                queries.append("income limit 6 lakh eligibility middle")
        
        # State-specific queries
        state = user_profile.get("state")
        if state:
            state_clean = str(state).replace("_", " ")
            queries.append(f"{state_clean} state scheme eligibility")
        
        return queries
    
    @staticmethod
    def check_eligibility_match(user_profile: Dict, scheme_metadata: Dict) -> Tuple[bool, float, List[str]]:
        """
        Check if user profile matches scheme eligibility criteria using Penalty-based filters.
        
        Mandatory fields (State, Category, Employment) now apply high penalties instead of 
        throwing away the data, allowing the LLM to provide warnings.
        """
        matches = []
        mismatches = []
        confidence = 0.5  # Base neutral confidence
        is_eligible = True # Assume eligible until a penalty is applied
        
        # --- 1. PENALTY FILTERS (State, Category, Employment) ---
        
        # State Check
        user_state = (user_profile.get("state") or "").lower().replace("_", " ")
        scheme_gov = (scheme_metadata.get("government") or "").lower()
        scheme_level = (scheme_metadata.get("level") or "Central").lower()
        if scheme_level == "state" and scheme_gov:
            if user_state not in scheme_gov and scheme_gov not in user_state:
                mismatches.append(f"State: Scheme for {scheme_gov.title()}, you are in {user_state.title()}")
                confidence = 0.1
                is_eligible = False

        # Social Category Check
        user_cat = (user_profile.get("category") or "").lower()
        scheme_cat = (scheme_metadata.get("category") or "").lower()
        if scheme_cat and user_cat and scheme_cat not in ["all", "general"]:
            if scheme_cat not in user_cat and user_cat not in scheme_cat:
                mismatches.append(f"Category: Scheme for {scheme_cat.upper()}, you are {user_cat.upper()}")
                confidence = min(confidence, 0.1)
                is_eligible = False

        # Government Employee Check
        user_is_govt = user_profile.get("is_govt_employee", False)
        scheme_exclusions = (scheme_metadata.get("exclusions") or "").lower()
        if user_is_govt:
            govt_keywords = ["government employee", "govt employee", "central/state employee", "public sector", "state/central"]
            if any(k in scheme_exclusions for k in govt_keywords):
                mismatches.append("Warning: Government employees are explicitly excluded from this scheme")
                confidence = min(confidence, 0.1)
                is_eligible = False

        # --- 2. SOFT FILTERS (Eligibility/Weights) ---
        
        # Age Check
        user_age = user_profile.get("age")
        if user_age:
            age_min = scheme_metadata.get("age_min")
            age_max = scheme_metadata.get("age_max")
            if age_min is not None and age_max is not None:
                if age_min <= user_age <= age_max:
                    matches.append(f"Age {user_age} within {age_min}-{age_max} range")
                    confidence += 0.2
                else:
                    mismatches.append(f"Age {user_age} outside {age_min}-{age_max} range")
                    confidence -= 0.3
                    is_eligible = False
        
        # Income Check
        user_income = user_profile.get("annual_income") or user_profile.get("income")
        if user_income:
            income_max = scheme_metadata.get("income_max")
            if income_max:
                if user_income <= income_max:
                    matches.append(f"Income Rs.{user_income:,} within limit Rs.{income_max:,}")
                    confidence += 0.2
                else:
                    mismatches.append(f"Income Rs.{user_income:,} exceeds limit Rs.{income_max:,}")
                    confidence -= 0.4
                    is_eligible = False
        
        # Gender Check
        user_gender = (user_profile.get("gender") or "").lower()
        scheme_gender = (scheme_metadata.get("gender") or "").lower()
        if scheme_gender and scheme_gender != "all":
            if user_gender == scheme_gender:
                matches.append(f"Gender Match ({scheme_gender.title()})")
                confidence += 0.15
            else:
                mismatches.append(f"Gender Mismatch (Scheme is for {scheme_gender.title()})")
                confidence -= 0.4
                is_eligible = False

        # Clamp confidence
        confidence = max(0.0, min(1.0, confidence))
        
        # Final Decision: True if no major mismatches (confidence remains high)
        is_eligible = is_eligible and confidence > 0.3
        
        reasons = [f"✅ {m}" for m in matches] + [f"🚩 {m}" for m in mismatches]
        
        return is_eligible, confidence, reasons
    
    @staticmethod
    def rank_schemes(user_profile: Dict, documents: List) -> List[Tuple]:
        """
        Rank retrieved documents by eligibility match.
        
        Returns list of (document, confidence, reasons) tuples sorted by confidence.
        """
        ranked = []
        seen_titles = set()
        
        for doc in documents:
            title = doc.metadata.get("title", "Unknown")
            
            # Skip duplicates
            if title in seen_titles:
                continue
            seen_titles.add(title)
            
            is_eligible, confidence, reasons = SchemeMatcher.check_eligibility_match(
                user_profile, doc.metadata
            )
            
            if is_eligible or confidence > 0.3:
                ranked.append((doc, confidence, reasons))
        
        # Sort by confidence descending
        ranked.sort(key=lambda x: x[1], reverse=True)
        
        return ranked
