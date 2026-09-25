"""
Validation utilities for CivicPulse AI form inputs.
"""

import re
from typing import Tuple, Dict, Any


EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def validate_complaint_form(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validates user submitted grievance form inputs.
    Returns: (is_valid, error_message)
    """
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    location = str(data.get("location", "")).strip()
    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()

    if not name:
        return False, "Please provide your full name."
    if len(name) < 2 or len(name) > 80:
        return False, "Name must be between 2 and 80 characters."

    if not email:
        return False, "Please provide your email address."
    if not EMAIL_REGEX.match(email):
        return False, "Please enter a valid email address (e.g. user@institution.edu)."

    if not location:
        return False, "Please specify the location of the issue (e.g. EEE Lab 2, Block B Room 304)."
    if len(location) < 2 or len(location) > 100:
        return False, "Location must be between 2 and 100 characters."

    if not title:
        return False, "Please enter a concise title for your complaint."
    if len(title) < 5 or len(title) > 150:
        return False, "Complaint title must be between 5 and 150 characters."

    if not description:
        return False, "Please enter a detailed description of the problem."
    if len(description) < 10:
        return False, "Complaint description is too short. Please describe the problem in more detail (at least 10 characters)."
    if len(description) > 3000:
        return False, "Complaint description is too long (maximum 3,000 characters)."

    return True, ""
