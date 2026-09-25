"""
Sample Data Generator for CivicPulse AI.
Populates realistic educational institution & facility grievances,
including similar pairs for TF-IDF evaluation, varying priority levels,
departments, and resolution histories.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from database.database import DatabaseManager


SAMPLE_COMPLAINTS: List[Dict[str, Any]] = [
    # 1. Electrical - Fan Issue in EEE Lab 2 (Base)
    {
        "name": "Dr. Ramesh Sharma",
        "email": "ramesh.sharma@institution.edu",
        "location": "EEE Lab 2, Electrical Block 2nd Floor",
        "title": "Three ceiling fans not working in EEE Lab 2",
        "description": "Three ceiling fans are completely non-functional in EEE Lab 2. Students are having severe difficulty attending laboratory sessions due to high heat.",
        "category": "Electrical",
        "subcategory": "Fan / Ventilation",
        "priority": "High",
        "priority_reason": "Multiple Equipment Failure affecting classroom/lab session",
        "department": "Electrical Maintenance Division",
        "status": "In Progress",
        "admin_notes": "Technician Anand assigned to inspect capacitor and motor coil.",
        "days_ago": 4,
        "resolved_days_after": None,
        "history": [
            ("None", "Pending", "System", "Complaint submitted and automatically logged.", 4),
            ("Pending", "Assigned", "Admin", "Assigned to Electrical Team 2.", 3),
            ("Assigned", "In Progress", "Eng. Anand", "Inspecting coil and capacitor wiring.", 2)
        ]
    },
    # 2. Electrical - Similar Fan Complaint in EEE Lab 2 (Demonstrates TF-IDF match)
    {
        "name": "Priya Varadarajan",
        "email": "priya.v@institution.edu",
        "location": "EEE Lab 2",
        "title": "Two ceiling fans stopped working in EEE Lab 2",
        "description": "The middle two ceiling fans stopped rotating during the afternoon session in EEE Lab 2. It is too hot for 60 students.",
        "category": "Electrical",
        "subcategory": "Fan / Ventilation",
        "priority": "High",
        "priority_reason": "Multiple Equipment Failure affecting student sessions",
        "department": "Electrical Maintenance Division",
        "status": "Pending",
        "admin_notes": "Flagged by AI as potentially similar to existing active ticket.",
        "days_ago": 1,
        "resolved_days_after": None,
        "history": [
            ("None", "Pending", "System", "Complaint submitted and automatically logged.", 1)
        ]
    },
    # 3. Critical Electrical - Sparking switchboard
    {
        "name": "Arjun Sundaram",
        "email": "arjun.s@institution.edu",
        "location": "CS Lab 3, IT Block Ground Floor",
        "title": "Sparking and burning smell from power socket switchboard",
        "description": "There is visible sparking and a strong burning smell coming from the main computer power switchboard near row 4. Exposed wire seen. Electric shock risk.",
        "category": "Electrical",
        "subcategory": "Wiring & Circuit Breaker",
        "priority": "Critical",
        "priority_reason": "Severe Electrical & Life Safety Risk (sparking, burning smell, shock hazard)",
        "department": "Electrical Maintenance Division",
        "status": "Resolved",
        "admin_notes": "Emergency power isolation done. Replaced faulty 16A breaker.",
        "days_ago": 7,
        "resolved_days_after": 0.1,
        "history": [
            ("None", "Pending", "System", "Logged as Critical hazard.", 7),
            ("Pending", "In Progress", "Admin", "Dispatched rapid response electrician.", 7),
            ("In Progress", "Resolved", "Eng. Suresh", "Replaced breaker switch and insulated loose wiring.", 6.9)
        ]
    },
    # 4. Water & Plumbing - Pipe Leakage
    {
        "name": "Prof. Meenakshi Sundaram",
        "email": "meenakshi.s@institution.edu",
        "location": "Restroom Block B, 2nd Floor",
        "title": "Severe water pipe leakage and flooding in Restroom Block B",
        "description": "Major water pipe burst near the washbasin area. Water is continuously overflowing into the corridor floor and causing slipping hazard.",
        "category": "Water & Plumbing",
        "subcategory": "Pipe Leakage & Seepage",
        "priority": "Critical",
        "priority_reason": "Major Water Inundation / Slipping Hazard",
        "department": "Plumbing & Water Supply Department",
        "status": "Resolved",
        "admin_notes": "Main valve shut off within 15 minutes. Pipe replaced with UPVC joint.",
        "days_ago": 10,
        "resolved_days_after": 0.2,
        "history": [
            ("None", "Pending", "System", "Logged as Critical priority.", 10),
            ("Pending", "In Progress", "Admin", "Plumber dispatched.", 10),
            ("In Progress", "Resolved", "Plumber John", "Main pipe section replaced.", 9.8)
        ]
    },
    # 5. Network & IT - Wi-Fi Outage in Library
    {
        "name": "Karthik Raja",
        "email": "karthik.raja@institution.edu",
        "location": "Central Library, 3rd Floor Digital Section",
        "title": "Wi-Fi access point offline in Central Library 3rd Floor",
        "description": "The campus Wi-Fi network SSID 'Campus-Fast' is completely disconnected on the 3rd floor. More than 80 students unable to access research journals.",
        "category": "Network & IT",
        "subcategory": "Wi-Fi & Wireless Network",
        "priority": "High",
        "priority_reason": "Critical Network Outage affecting multiple users",
        "department": "IT Infrastructure & Network Operations",
        "status": "Resolved",
        "admin_notes": "Aruba AP rebooted and PoE switch port reconfigured.",
        "days_ago": 5,
        "resolved_days_after": 0.5,
        "history": [
            ("None", "Pending", "System", "Logged via portal.", 5),
            ("Pending", "Assigned", "Admin", "Assigned to Network admin.", 5),
            ("Assigned", "In Progress", "IT Team", "Checking PoE switch VLAN status.", 4.8),
            ("In Progress", "Resolved", "IT Team", "PoE gateway rebooted, AP operational.", 4.5)
        ]
    },
    # 6. Cleaning & Sanitation - Dustbin Overflow
    {
        "name": "Siddharth Menon",
        "email": "siddharth.m@institution.edu",
        "location": "Cafeteria Outdoor Seating Area",
        "title": "Overflowing dustbins and food waste near cafeteria",
        "description": "Multiple garbage bins near the main food court are overflowing with food waste and creating foul smell and attracting stray animals.",
        "category": "Cleaning & Sanitation",
        "subcategory": "Waste Management & Dustbins",
        "priority": "Medium",
        "priority_reason": "Standard Sanitation maintenance and waste clearing",
        "department": "Housekeeping & Facility Hygiene Services",
        "status": "Resolved",
        "admin_notes": "Housekeeping cleared all bins and installed larger 240L bins.",
        "days_ago": 8,
        "resolved_days_after": 0.3,
        "history": [
            ("None", "Pending", "System", "Logged.", 8),
            ("Pending", "In Progress", "Admin", "Sanitation supervisor notified.", 8),
            ("In Progress", "Resolved", "Supervisor Kumar", "Bins cleared and area sanitized.", 7.7)
        ]
    },
    # 7. Infrastructure - Broken Window
    {
        "name": "Anita George",
        "email": "anita.george@institution.edu",
        "location": "Lecture Hall 204, Science Block",
        "title": "Broken window glass pane rattling in Lecture Hall 204",
        "description": "One window glass pane is cracked and rattling violently in high winds. Risk of falling glass on students sitting near row 3.",
        "category": "Infrastructure & Civil",
        "subcategory": "Door, Window & Locks",
        "priority": "High",
        "priority_reason": "Classroom hazard & falling glass safety risk",
        "department": "Civil Works & Structural Maintenance",
        "status": "Assigned",
        "admin_notes": "Glazier contacted for 4mm toughened glass replacement.",
        "days_ago": 2,
        "resolved_days_after": None,
        "history": [
            ("None", "Pending", "System", "Logged.", 2),
            ("Pending", "Assigned", "Admin", "Assigned to Civil carpenter/glazier team.", 1.5)
        ]
    },
    # 8. Equipment - Elevator Malfunction
    {
        "name": "Security Guard Murugan",
        "email": "murugan.sec@institution.edu",
        "location": "Main Administrative Block Lift 1",
        "title": "Elevator Lift 1 stuck on 4th floor with abnormal jerk",
        "description": "Lift 1 made a loud grinding noise and got stuck at floor 4. Emergency alarm tested. No passengers trapped currently but lift is non-operational.",
        "category": "Equipment & Machinery",
        "subcategory": "Elevator & Lift Systems",
        "priority": "High",
        "priority_reason": "Vertical transport failure affecting multi-story building access",
        "department": "Vertical Transport / Elevator AMC Cell",
        "status": "In Progress",
        "admin_notes": "Otis AMC technician on site checking hoist brake sensors.",
        "days_ago": 1,
        "resolved_days_after": None,
        "history": [
            ("None", "Pending", "System", "Urgent ticket created.", 1),
            ("Pending", "In Progress", "Admin", "Lift shut down for AMC inspection.", 0.8)
        ]
    },
    # 9. Security & Safety - Dark Area Lighting
    {
        "name": "Kavita Nair",
        "email": "kavita.nair@institution.edu",
        "location": "Path between Girls Hostel Block C and Main Gate",
        "title": "Three street lights dark along Girls Hostel pathway",
        "description": "Three consecutive street lamps are completely dark along the primary pathway connecting Girls Hostel C and the main campus gate. Safety concern at night.",
        "category": "Security & Safety",
        "subcategory": "Campus Lighting & Night Safety",
        "priority": "High",
        "priority_reason": "Campus Night Safety & Security illumination issue",
        "department": "Campus Security & Safety Division",
        "status": "Resolved",
        "admin_notes": "Replaced two fused sodium vapor lamps and fixed timer circuit.",
        "days_ago": 12,
        "resolved_days_after": 0.8,
        "history": [
            ("None", "Pending", "System", "Logged.", 12),
            ("Pending", "In Progress", "Security Chief", "Coordinated with electrical team.", 11.8),
            ("In Progress", "Resolved", "Admin", "Lamps replaced and tested at 7 PM.", 11.2)
        ]
    },
    # 10. Low Priority - Whiteboard Marker & Eraser
    {
        "name": "Prof. David Wilson",
        "email": "david.wilson@institution.edu",
        "location": "Seminar Hall 1",
        "title": "Whiteboard markers empty and duster missing in Seminar Hall 1",
        "description": "All dry-erase whiteboard markers are dried up and duster is missing in Seminar Hall 1. Please replenish consumables whenever convenient.",
        "category": "Infrastructure & Civil",
        "subcategory": "Furniture & Desks",
        "priority": "Low",
        "priority_reason": "Non-Urgent Consumable Replacement",
        "department": "General Administration & Public Grievance Desk",
        "status": "Closed",
        "admin_notes": "Supplied pack of 4 markers and 2 magnetic dusters.",
        "days_ago": 15,
        "resolved_days_after": 1.0,
        "history": [
            ("None", "Pending", "System", "Logged.", 15),
            ("Pending", "Resolved", "Stores Admin", "Stationery issued.", 14.2),
            ("Resolved", "Closed", "Admin", "Verified.", 14.0)
        ]
    }
]


def seed_sample_data(db: DatabaseManager, force: bool = False) -> int:
    """
    Seeds the SQLite database with realistic complaint records if empty or forced.
    Returns the count of seeded complaints.
    """
    if not force:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as cnt FROM complaints")
            if cursor.fetchone()["cnt"] > 0:
                return 0

    if force:
        db.reset_db()

    now = datetime.now()
    seeded_count = 0

    for idx, item in enumerate(SAMPLE_COMPLAINTS, start=1):
        complaint_id = f"CP-{now.year}-{idx:04d}"
        days_ago = item.get("days_ago", 1)
        created_dt = now - timedelta(days=days_ago)
        created_str = created_dt.strftime("%Y-%m-%d %H:%M:%S")

        resolved_str = None
        if item.get("resolved_days_after") is not None:
            resolved_dt = created_dt + timedelta(days=item["resolved_days_after"])
            resolved_str = resolved_dt.strftime("%Y-%m-%d %H:%M:%S")

        updated_str = resolved_str if resolved_str else (now - timedelta(days=max(0, days_ago - 1))).strftime("%Y-%m-%d %H:%M:%S")

        # Similarity metadata simulation for sample pair
        sim_count = 0
        top_sim_id = ""
        top_sim_score = 0.0
        if idx == 2:
            sim_count = 1
            top_sim_id = f"CP-{now.year}-0001"
            top_sim_score = 0.88

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO complaints (
                    complaint_id, name, email, location, title, description,
                    category, subcategory, priority, priority_reason, department,
                    status, admin_notes, similar_count, top_similar_id, top_similarity_score,
                    created_at, updated_at, resolved_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    complaint_id,
                    item["name"],
                    item["email"],
                    item["location"],
                    item["title"],
                    item["description"],
                    item["category"],
                    item["subcategory"],
                    item["priority"],
                    item.get("priority_reason", "Automated priority signal"),
                    item["department"],
                    item["status"],
                    item.get("admin_notes", ""),
                    sim_count,
                    top_sim_id,
                    top_sim_score,
                    created_str,
                    updated_str,
                    resolved_str
                )
            )

            # Insert history logs
            history_entries = item.get("history", [])
            for h_old, h_new, h_by, h_comment, h_days_ago in history_entries:
                h_time = (now - timedelta(days=h_days_ago)).strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(
                    """
                    INSERT INTO status_history (
                        complaint_id, old_status, new_status, changed_by, comment, changed_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (complaint_id, h_old, h_new, h_by, h_comment, h_time)
                )
            conn.commit()
            seeded_count += 1

    return seeded_count
