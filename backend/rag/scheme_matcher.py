"""
Scheme Matcher Agent - Profile-based scheme eligibility matching.
Prioritized Hard Filters: State > Dis/Min > Cat/Area > Income > Age > Student
"""
from typing import Dict, List, Optional, Tuple


class SchemeMatcher:
    """
    Mini-agent that matches user profiles against scheme eligibility criteria.
    """
    
    @staticmethod
    def extract_search_queries(user_profile: Dict) -> List[str]:
        """
        Generate multiple search queries based on user profile DB columns.
        """
        queries = []
        queries.append("eligibility criteria benefits")
        
        # 1. CATEGORY
        category = (user_profile.get("category") or "").lower()
        if category in ["sc", "scheduled caste"]:
            queries.append("scheduled caste SC schemes")
        elif category in ["st", "scheduled tribe"]:
            queries.append("scheduled tribe ST schemes")
        elif category in ["obc", "other backward class"]:
            queries.append("OBC other backward class schemes")
        elif category in ["ews", "economically weaker section"]:
            queries.append("EWS economically weaker section schemes")
        
        # 2. GENDER
        gender = (user_profile.get("gender") or "").lower()
        if gender == "female":
            queries.append("women girl female maternity schemes")
        elif gender == "transgender":
            queries.append("transgender schemes")
        
        # 3. AGE
        age = user_profile.get("age")
        if age:
            if age < 18:
                queries.append("child student minor schemes")
            elif age < 35:
                queries.append("youth young adult schemes")
            elif age > 60:
                queries.append("senior citizen pension elderly schemes")

        # 4. AREA (Rural/Urban)
        area = (user_profile.get("area") or "").lower()
        if area == "rural":
            queries.append("rural gram panchayat agriculture village schemes")
        elif area == "urban":
            queries.append("urban housing municipal city schemes")

        # 5. DISABILITY
        if user_profile.get("is_disabled"):
            queries.append("disability disabled divyang PwD handicapped pension aids")

        # 6. MINORITY
        if user_profile.get("is_minority"):
            queries.append("minority community muslim christian sikh jain schemes")

        # 7. STUDENT STATUS
        if user_profile.get("is_student"):
            queries.append("student scholarship education fellowship")

        # 8. EMPLOYMENT STATUS
        emp_status = (user_profile.get("employment_status") or "").lower()
        if "farmer" in emp_status or "agriculture" in emp_status:
            queries.append("farmer kisan agriculture subsidy")
        elif "unemployed" in emp_status:
            queries.append("unemployed youth skill development employment")
        elif "self_employed" in emp_status or "business" in emp_status:
            queries.append("entrepreneur startup msme loan business")
        elif "artisan" in emp_status:
            queries.append("artisan handicraft vishwakarma")

        # 9. GOVERNMENT EMPLOYEE
        if user_profile.get("is_govt_employee"):
            queries.append("government employee housing welfare")

        # 10. INCOME
        inc_val = user_profile.get("annual_income") or user_profile.get("family_income")
        if inc_val:
            if inc_val < 200000:
                queries.append("BPL below poverty line low income housing ration")
            elif inc_val < 800000:
                queries.append("EWS middle income group schemes")

        # 11. STATE
        state = user_profile.get("state")
        if state:
            state_clean = str(state).replace("_", " ")
            queries.append(f"{state_clean} state government schemes")
        
        return queries
    
    @staticmethod
    def check_eligibility_match(user_profile: Dict, scheme_metadata: Dict) -> Tuple[bool, float, List[str]]:
        """
        Check if user profile matches scheme eligibility criteria.
        
        HARD FILTERS (Strict - sets is_eligible=False):
        1. State
        2. Disability OR Minority
        3. Category OR Area
        4. Income
        5. Age
        6. Student Status
        
        SOFT FILTERS (Lenient - reduces confidence):
        1. Gender
        2. Employment Status
        3. Govt Employee Exclusion
        """
        matches = []
        mismatches = []
        confidence = 0.5
        is_eligible = True 
        
        # Helper: Get Scheme Tags
        scheme_tags = (str(scheme_metadata.get("tags", [])) + " " + 
                       str(scheme_metadata.get("scheme_name", "")) + " " + 
                       str(scheme_metadata.get("beneficiary_type", ""))).lower()

        # ==========================================
        # 🔴 SECTION 1: HARD FILTERS
        # ==========================================

        # 1. STATE CHECK (Critical)
        user_state = (user_profile.get("state") or "").lower().replace("_", " ")
        scheme_level = (scheme_metadata.get("level") or "Central").lower()
        scheme_gov = (scheme_metadata.get("government") or "").lower()
        
        if scheme_level == "state":
            if scheme_gov and user_state and user_state not in scheme_gov and scheme_gov not in user_state:
                mismatches.append(f"⛔ State Mismatch: Scheme for {scheme_gov.title()}, you are in {user_state.title()}")
                confidence = 0.0
                is_eligible = False

        # 2A. DISABILITY CHECK (High Priority)
        user_disabled = user_profile.get("is_disabled", False)
        is_disability_scheme = any(x in scheme_tags for x in ["disability", "disabled", "divyang", "handicap", "pwd"])
        
        if is_disability_scheme and not user_disabled:
            mismatches.append("⛔ Requirement: Scheme is exclusively for Persons with Disabilities")
            confidence = 0.0
            is_eligible = False
        elif is_disability_scheme and user_disabled:
            matches.append("Eligibility: Matches Disability status")
            confidence += 0.2

        # 2B. MINORITY CHECK (High Priority)
        user_minority = user_profile.get("is_minority", False)
        is_minority_scheme = "minority" in scheme_tags or "minority" in (scheme_metadata.get("category") or "").lower()
        
        if is_minority_scheme and not user_minority:
            mismatches.append("⛔ Requirement: Scheme is exclusively for Minority communities")
            confidence = 0.0
            is_eligible = False
        elif is_minority_scheme and user_minority:
            matches.append("Eligibility: Matches Minority status")
            confidence += 0.2

        # 3A. CATEGORY CHECK (New Hard Filter)
        user_cat = (user_profile.get("category") or "").lower()
        scheme_cat = (scheme_metadata.get("category") or "all").lower()
        
        if scheme_cat not in ["all", "general", "any"] and user_cat:
            # e.g., Scheme is for "SC", User is "General" -> Block
            # But if Scheme is "SC", User is "SC" -> Pass
            if user_cat not in scheme_cat:
                mismatches.append(f"⛔ Category Mismatch: Scheme for {scheme_cat.upper()}, you are {user_cat.upper()}")
                confidence = 0.0
                is_eligible = False

        # 3B. AREA (Rural/Urban) CHECK (New Hard Filter)
        user_area = (user_profile.get("area") or "").lower()
        scheme_residence = (scheme_metadata.get("residence_type") or "all").lower()
        
        # Fallback to tags if metadata missing
        if scheme_residence == "all":
            if "rural" in scheme_tags and "urban" not in scheme_tags:
                scheme_residence = "rural"
            elif "urban" in scheme_tags and "rural" not in scheme_tags:
                scheme_residence = "urban"
        
        if scheme_residence not in ["all", "any", "both"] and user_area:
            if user_area != scheme_residence:
                mismatches.append(f"⛔ Area Mismatch: Scheme for {scheme_residence.title()}, you are {user_area.title()}")
                confidence = 0.0
                is_eligible = False

        # 4. INCOME CHECK (Medium Priority)
        user_income = user_profile.get("annual_income") or user_profile.get("family_income")
        scheme_income_max = scheme_metadata.get("income_max")
        
        if user_income and scheme_income_max:
            if user_income > scheme_income_max:
                mismatches.append(f"⛔ Income: Rs.{user_income:,} exceeds limit Rs.{scheme_income_max:,}")
                confidence = 0.0
                is_eligible = False
            else:
                matches.append(f"Income: Rs.{user_income:,} is within limit")
                confidence += 0.1

        # 5. AGE CHECK (Medium Priority)
        user_age = user_profile.get("age")
        if user_age:
            age_min = scheme_metadata.get("age_min")
            age_max = scheme_metadata.get("age_max")
            
            if age_min is not None or age_max is not None:
                lower = age_min if age_min is not None else 0
                upper = age_max if age_max is not None else 100
                
                if not (lower <= user_age <= upper):
                    mismatches.append(f"⛔ Age: {user_age} is outside range {lower}-{upper}")
                    confidence = 0.0
                    is_eligible = False
                else:
                    matches.append(f"Age: {user_age} is within range")
                    confidence += 0.1

        # 6. STUDENT CHECK (Lower Priority Hard Filter)
        user_student = user_profile.get("is_student", False)
        is_student_scheme = any(x in scheme_tags for x in ["scholarship", "student", "tuition", "fellowship"])
        
        if is_student_scheme and not user_student:
             mismatches.append("⛔ Requirement: Scheme is exclusively for Students")
             confidence = 0.0
             is_eligible = False
        elif is_student_scheme and user_student:
             matches.append("Eligibility: Matches Student status")
             confidence += 0.15

        # STOP IF HARD FILTERS FAILED
        if not is_eligible:
            return False, 0.0, mismatches

        # ==========================================
        # 🟡 SECTION 2: SOFT FILTERS (Penalties)
        # ==========================================

        # 7. GENDER CHECK (Soft)
        user_gender = (user_profile.get("gender") or "").lower()
        scheme_gender = (scheme_metadata.get("gender") or "all").lower()
        
        if scheme_gender not in ["all", "any", "both"] and user_gender:
            if user_gender != scheme_gender:
                mismatches.append(f"⚠️ Gender Warning: Scheme prefers {scheme_gender.title()}")
                confidence -= 0.3

        # 8. EMPLOYMENT STATUS CHECK (Soft)
        user_emp = (user_profile.get("employment_status") or "").lower()
        if "farmer" in scheme_tags and "farmer" not in user_emp and "agriculture" not in user_emp:
             mismatches.append("⚠️ Employment Warning: Scheme appears to be for Farmers")
             confidence -= 0.2

        # 9. GOVT EMPLOYEE EXCLUSION (Soft)
        user_govt = user_profile.get("is_govt_employee", False)
        exclusions = (scheme_metadata.get("exclusions") or "").lower()
        
        if user_govt:
            if "government employee" in exclusions or "govt employee" in exclusions:
                mismatches.append("⚠️ Exclusion Warning: Govt employees might be excluded")
                confidence -= 0.4

        # --- Final Scoring ---
        confidence = max(0.0, min(1.0, confidence))
        
        reasons = [f"✅ {m}" for m in matches] + [f"🚩 {m}" for m in mismatches]
        
        return is_eligible, confidence, reasons

    @staticmethod
    def rank_schemes(user_profile: Dict, documents: List) -> List[Tuple]:
        """
        Rank retrieved documents by eligibility match.
        Returns list of (document, confidence, reasons) sorted by confidence.
        """
        ranked = []
        seen_titles = set()
        
        for doc in documents:
            title = doc.metadata.get("scheme_name") or doc.metadata.get("title", "Unknown")
            
            if title in seen_titles:
                continue
            seen_titles.add(title)
            
            is_eligible, confidence, reasons = SchemeMatcher.check_eligibility_match(
                user_profile, doc.metadata
            )
            
            # Default behavior: Keep everything, just rank lower if ineligible
            # This allows the LLM to see "Why it wasn't valid" and explain it
            ranked.append((doc, confidence, reasons))
        
        # Sort by confidence descending
        ranked.sort(key=lambda x: x[1], reverse=True)
        
        return ranked