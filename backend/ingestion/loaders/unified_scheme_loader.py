from typing import List, Dict


class UnifiedSchemeLoader:
    """
    Authoritative, curated loader for Government Schemes
    (No scraping, no MyScheme dependency)
    """

    def load_all_schemes(self, limit: int | None = None) -> List[Dict]:
        schemes = self._central_schemes() + self._education_schemes()
        unique = {s["title"].lower(): s for s in schemes}
        schemes = list(unique.values())
        return schemes[:limit] if limit else schemes

    def _central_schemes(self) -> List[Dict]:
        return [
            {
                "title": "PM-KISAN",
                "description": "Income support of ₹6000 per year to farmer families.",
                "benefits": "₹6000 per year in three installments.",
                "eligibility": "Landholding farmer families.",
                "documents_required": "Aadhaar, land records, bank details.",
                "application_process": "Apply via PM-KISAN portal or CSC.",
                "department": "Ministry of Agriculture",
                "category": "Agriculture",
                "url": "https://pmkisan.gov.in",
                "source": "Central Government",
            },
            {
                "title": "Ayushman Bharat – PM-JAY",
                "description": "Health insurance coverage up to ₹5 lakh.",
                "benefits": "Cashless treatment in empanelled hospitals.",
                "eligibility": "SECC-listed families.",
                "documents_required": "Aadhaar, ration card.",
                "application_process": "Generate Ayushman card online.",
                "department": "Ministry of Health",
                "category": "Health",
                "url": "https://pmjay.gov.in",
                "source": "Central Government",
            },
        ]

    def _education_schemes(self) -> List[Dict]:
        return [
            {
                "title": "PM Scholarship Scheme",
                "description": "Scholarships for children of armed forces personnel.",
                "benefits": "₹2,500–₹3,000 per month.",
                "eligibility": "Children of ex-servicemen.",
                "documents_required": "Education certificates, service proof.",
                "application_process": "Apply via National Scholarship Portal.",
                "department": "Ministry of Defence",
                "category": "Education",
                "url": "https://scholarships.gov.in",
                "source": "Central Government",
            }
        ]
