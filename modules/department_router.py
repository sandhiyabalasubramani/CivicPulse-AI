"""
Department Router Module for CivicPulse AI.
Intelligently routes complaints to the appropriate campus/facility department
based on category, subcategory, keywords, and location context.
"""

from typing import Dict, List, Any, Optional


DEPARTMENT_MAP: Dict[str, Dict[str, Any]] = {
    "Electrical": {
        "primary": "Electrical Maintenance Division",
        "email": "electrical-helpdesk@civicpulse.edu",
        "sla_hours": 24,
        "sub_routing": {
            "Power Backup & UPS": "Substation & High-Voltage Operations",
            "Air Conditioner & HVAC": "HVAC & Climate Control Unit"
        }
    },
    "Water & Plumbing": {
        "primary": "Plumbing & Water Supply Department",
        "email": "water-support@civicpulse.edu",
        "sla_hours": 24,
        "sub_routing": {
            "Drinking Water & RO": "Water Quality & RO Maintenance Team"
        }
    },
    "Network & IT": {
        "primary": "IT Infrastructure & Network Operations",
        "email": "it-helpdesk@civicpulse.edu",
        "sla_hours": 12,
        "sub_routing": {
            "Lab Computers & Peripherals": "Desktop Support & Hardware Cell",
            "Projector & AV Systems": "Media & AV Systems Unit",
            "Portal & Server Systems": "ERP & Cloud Applications Team"
        }
    },
    "Cleaning & Sanitation": {
        "primary": "Housekeeping & Facility Hygiene Services",
        "email": "sanitation@civicpulse.edu",
        "sla_hours": 8,
        "sub_routing": {
            "Pest Control": "Pest & Environment Management Cell"
        }
    },
    "Infrastructure & Civil": {
        "primary": "Civil Works & Structural Maintenance",
        "email": "civil-works@civicpulse.edu",
        "sla_hours": 48,
        "sub_routing": {
            "Furniture & Desks": "Carpentry & Furniture Workshop"
        }
    },
    "Equipment & Machinery": {
        "primary": "Instrumentation & Equipment Cell",
        "email": "equipment-lab@civicpulse.edu",
        "sla_hours": 36,
        "sub_routing": {
            "Elevator & Lift Systems": "Vertical Transport / Elevator AMC Cell",
            "Office Printing & Scanning": "Reprographics & Printing Unit"
        }
    },
    "Security & Safety": {
        "primary": "Campus Security & Safety Division",
        "email": "security-chief@civicpulse.edu",
        "sla_hours": 4,
        "sub_routing": {
            "CCTV & Surveillance": "CCTV Surveillance & Control Room",
            "Fire Safety Equipment": "Fire Safety & Emergency Response Unit"
        }
    },
    "Other": {
        "primary": "General Administration & Public Grievance Desk",
        "email": "grievance-admin@civicpulse.edu",
        "sla_hours": 48,
        "sub_routing": {}
    }
}


class DepartmentRouter:
    """
    Assigns department and calculates SLA response targets
    based on taxonomy rules.
    """

    def __init__(self, mapping: Dict[str, Dict[str, Any]] = DEPARTMENT_MAP):
        self.mapping = mapping

    def route(
        self,
        category: str,
        subcategory: str = "",
        user_department: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Determines the designated department, contact email, and target SLA.
        """
        # If user explicitly supplied a department selection other than auto
        if user_department and user_department != "Auto-Assign" and user_department.strip():
            return {
                "department": user_department.strip(),
                "routing_type": "Manual User Selection",
                "sla_hours": 24,
                "contact_email": "admin@civicpulse.edu"
            }

        dept_info = self.mapping.get(category, self.mapping["Other"])
        primary_dept = dept_info["primary"]
        sla = dept_info.get("sla_hours", 24)
        contact = dept_info.get("email", "admin@civicpulse.edu")

        # Check subcategory-specific routing
        sub_routes = dept_info.get("sub_routing", {})
        if subcategory in sub_routes:
            return {
                "department": sub_routes[subcategory],
                "routing_type": f"Specialized Sub-Routing ({subcategory})",
                "sla_hours": sla,
                "contact_email": contact
            }

        return {
            "department": primary_dept,
            "routing_type": f"Category Match ({category})",
            "sla_hours": sla,
            "contact_email": contact
        }

    def get_all_departments(self) -> List[str]:
        """Returns a flat list of all primary and specialized departments."""
        departments = set()
        for _, info in self.mapping.items():
            departments.add(info["primary"])
            for sub_dept in info.get("sub_routing", {}).values():
                departments.add(sub_dept)
        return sorted(list(departments))


# Singleton helper
_router_instance: Optional[DepartmentRouter] = None

def get_department_router() -> DepartmentRouter:
    """Returns singleton DepartmentRouter instance."""
    global _router_instance
    if _router_instance is None:
        _router_instance = DepartmentRouter()
    return _router_instance
