"""
Priority Engine for CivicPulse AI.
Implements a transparent, deterministic rule-based priority scoring system
with explicit signal explainability (Critical, High, Medium, Low).
"""

import re
from typing import Dict, List, Tuple, Any, Optional
from .text_processing import clean_text


# Priority Rules Taxonomy with Explanatory Reasons
CRITICAL_SIGNALS: Dict[str, str] = {
    r"\b(fire|smoke|burning smell|gas leak)\b": "Immediate Fire / Chemical Safety Hazard",
    r"\b(exposed wire|live wire|electric shock|sparking|short circuit|electrocution)\b": "Severe Electrical & Life Safety Risk",
    r"\b(burst pipe|major water leak|flooding|flood|submerged)\b": "Major Water Inundation / Infrastructure Danger",
    r"\b(structural collapse|ceiling fall|wall crack collapse|falling debris|broken glass danger)\b": "Structural Collapse Risk",
    r"\b(stuck inside lift|trapped in elevator|lift stuck)\b": "Person Trapped in Elevator",
    r"\b(security emergency|assault|theft in progress|break in|unauthorized weapon|trespassing violence)\b": "Active Security Emergency",
    r"\b(toxic|chemical spill|acid leak|suffocation)\b": "Hazardous Material / Toxicity Hazard"
}

HIGH_SIGNALS: Dict[str, str] = {
    r"\b(entire|whole|all)\s+(lab|classroom|floor|block|building|department|campus)\b": "Widespread Infrastructure Impact",
    r"\b(blackout|total power failure|no electricity in|mcb tripped)\b": "Severe Power Loss Affecting Class/Lab",
    r"\b(exam|examination|test|evaluation|lecture)\s+(affected|disrupted|scheduled|stopped)\b": "Academic / Exam Session Disruption",
    r"\b(network outage|internet down|server down|wifi down in (whole|all|entire))\b": "Critical Network / IT System Outage",
    r"\b(no water supply|water outage|tank empty)\b": "Complete Water Supply Interruption",
    r"\b(restroom flooded|sewage overflow|drainage blocked)\b": "Severe Sanitation / Health Hazard",
    r"\b(multiple (fans|lights|computers|pcs|systems)|[2-9]\s+(fans|lights|pcs|computers))\b": "Multiple Equipment Failure",
    r"\b(projector not working|projector broken)\s+(in|during)\s+(class|lecture|lab)\b": "Classroom Audio-Visual Disruption",
    r"\b(students (having difficulty|suffering|cannot work|unable to study))\b": "High Operational / Student Disruption"
}

LOW_SIGNALS: Dict[str, str] = {
    r"\b(cosmetic|minor scratch|slight squeak|aesthetic|color faded)\b": "Minor Aesthetic / Non-Functional Issue",
    r"\b(paint peeling|small stain|dust on|dirty window)\b": "Low Priority Cleaning / Cosmetic Maintenance",
    r"\b(marker empty|chalk needed|duster missing|clock battery)\b": "Low Priority Consumable Replacement",
    r"\b(loose screw|loose handle|minor noise|not urgent|whenever possible)\b": "Non-Urgent Convenience Maintenance"
}


class PriorityEngine:
    """
    Transparent rule-based priority evaluation engine.
    Produces deterministic priority ratings with human-readable rationale.
    """

    def evaluate(self, title: str, description: str, category: str = "") -> Dict[str, Any]:
        """
        Evaluates complaint text and assigns priority: Critical, High, Medium, or Low.
        Returns:
            {
                "priority": "High",
                "score": 75,
                "reasons": ["Widespread Infrastructure Impact", "Multiple Equipment Failure"],
                "primary_reason": "Multiple Equipment Failure"
            }
        """
        full_text = f"{title} {description}".strip().lower()

        # 1. Check for Critical rules first
        critical_reasons = []
        for pattern, reason in CRITICAL_SIGNALS.items():
            if re.search(pattern, full_text, re.IGNORECASE):
                critical_reasons.append(reason)

        if critical_reasons:
            return {
                "priority": "Critical",
                "score": 95,
                "reasons": critical_reasons,
                "primary_reason": critical_reasons[0]
            }

        # 2. Check for High priority rules
        high_reasons = []
        for pattern, reason in HIGH_SIGNALS.items():
            if re.search(pattern, full_text, re.IGNORECASE):
                high_reasons.append(reason)

        if high_reasons:
            return {
                "priority": "High",
                "score": 75,
                "reasons": high_reasons,
                "primary_reason": high_reasons[0]
            }

        # 3. Check for Low priority rules
        low_reasons = []
        for pattern, reason in LOW_SIGNALS.items():
            if re.search(pattern, full_text, re.IGNORECASE):
                low_reasons.append(reason)

        if low_reasons:
            return {
                "priority": "Low",
                "score": 25,
                "reasons": low_reasons,
                "primary_reason": low_reasons[0]
            }

        # 4. Default to Medium priority for standard maintenance
        default_reason = f"Standard {category} maintenance issue without critical safety or widespread disruption markers" if category else "Standard maintenance and service request"
        return {
            "priority": "Medium",
            "score": 50,
            "reasons": [default_reason],
            "primary_reason": default_reason
        }


# Singleton instance helper
_priority_instance: Optional[PriorityEngine] = None

def get_priority_engine() -> PriorityEngine:
    """Returns singleton PriorityEngine instance."""
    global _priority_instance
    if _priority_instance is None:
        _priority_instance = PriorityEngine()
    return _priority_instance
