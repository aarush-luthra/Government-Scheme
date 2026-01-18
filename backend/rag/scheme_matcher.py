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
        Check if user profile matches scheme eligibility criteria.
        
        Returns:
            - is_eligible: Boolean indicating likely eligibility
            - confidence: Float score 0-1 indicating confidence
            - reasons: List of matching/non-matching criteria
        """
        matches = []
        mismatches = []
        confidence = 0.5  # Start neutral
        
        # Check age
        user_age = user_profile.get("age")
        if user_age:
            age_min = scheme_metadata.get("age_min")
            age_max = scheme_metadata.get("age_max")
            
            if age_min and age_max:
                if age_min <= user_age <= age_max:
                    matches.append(f"Age {user_age} within {age_min}-{age_max} range")
                    confidence += 0.15
                else:
                    mismatches.append(f"Age {user_age} outside {age_min}-{age_max} range")
                    confidence -= 0.2
        
        # Check income
        user_income = user_profile.get("annual_income") or user_profile.get("income")
        if user_income:
            income_max = scheme_metadata.get("income_max")
            if income_max:
                if user_income <= income_max:
                    matches.append(f"Income Rs.{user_income:,} within limit Rs.{income_max:,}")
                    confidence += 0.15
                else:
                    mismatches.append(f"Income Rs.{user_income:,} exceeds limit Rs.{income_max:,}")
                    confidence -= 0.25
        
        # Check gender
        user_gender = (user_profile.get("gender") or "").lower()
        scheme_gender = scheme_metadata.get("gender")
        if scheme_gender:
            if user_gender == scheme_gender:
                matches.append(f"Gender requirement ({scheme_gender}) matches")
                confidence += 0.1
            else:
                mismatches.append(f"Gender requirement is {scheme_gender}, user is {user_gender}")
                confidence -= 0.3
        
        # Check disability
        user_disabled = user_profile.get("is_disabled")
        scheme_disabled = scheme_metadata.get("is_disabled")
        if scheme_disabled and not user_disabled:
            mismatches.append("Scheme requires disability status")
            confidence -= 0.3
        elif scheme_disabled and user_disabled:
            matches.append("Disability requirement matches")
            confidence += 0.15
        
        # Check student status
        user_student = user_profile.get("is_student")
        scheme_student = scheme_metadata.get("is_student")
        if scheme_student and not user_student:
            mismatches.append("Scheme requires student status")
            confidence -= 0.2
        elif scheme_student and user_student:
            matches.append("Student requirement matches")
            confidence += 0.1
        
        # Clamp confidence
        confidence = max(0.0, min(1.0, confidence))
        
        # Determine eligibility
        is_eligible = len(mismatches) == 0 or (len(matches) > len(mismatches) and confidence > 0.4)
        
        reasons = matches + [f"⚠️ {m}" for m in mismatches]
        
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
