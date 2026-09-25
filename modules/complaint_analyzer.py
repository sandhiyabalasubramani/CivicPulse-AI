"""
Complaint Analyzer Module for CivicPulse AI.
Performs modular text classification, subcategory detection, keyword extraction,
and returns structured analysis objects.
"""

import re
from typing import Dict, List, Tuple, Any, Optional
from .text_processing import clean_text, tokenize, extract_keywords


# Modular Category & Subcategory Knowledge Graph
CATEGORY_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "Electrical": {
        "keywords": [
            "fan", "fans", "light", "lights", "bulb", "tube", "tubelight", "socket",
            "switch", "switchboard", "power", "electricity", "current", "shock",
            "wire", "wiring", "spark", "sparking", "short circuit", "mcb", "fuse",
            "ac", "air conditioner", "air conditioning", "cooling", "heater",
            "inverter", "generator", "ups", "voltage", "blackout", "tripped", "plug"
        ],
        "subcategories": {
            "Fan / Ventilation": ["fan", "fans", "exhaust", "ceiling fan", "ventilation", "blower"],
            "Lighting & Tube Lights": ["light", "lights", "bulb", "tubelight", "tube", "dark", "flickering", "choke"],
            "Power Socket & Switches": ["socket", "switch", "switchboard", "plug", "outlet", "extension"],
            "Wiring & Circuit Breaker": ["wire", "wiring", "spark", "sparking", "shock", "short circuit", "mcb", "fuse", "tripped"],
            "Air Conditioner & HVAC": ["ac", "air conditioner", "hvac", "cooling", "thermostat", "compressor"],
            "Power Backup & UPS": ["ups", "inverter", "generator", "backup", "blackout", "battery"],
            "General Electrical": []
        }
    },
    "Water & Plumbing": {
        "keywords": [
            "water", "leak", "leaking", "leakage", "pipe", "pipeline", "tap",
            "faucet", "drain", "drainage", "clog", "clogged", "overflow",
            "overflowing", "seepage", "flush", "toilet", "washbasin", "sink",
            "purifier", "drinking water", "ro", "tank", "plumbing", "sewage", "restroom water"
        ],
        "subcategories": {
            "Pipe Leakage & Seepage": ["pipe", "pipeline", "leak", "leaking", "leakage", "burst", "seepage"],
            "Tap & Faucet Damage": ["tap", "taps", "faucet", "valve", "broken tap", "handle"],
            "Drainage & Clog": ["drain", "drainage", "clog", "clogged", "blocked", "overflow", "sink", "washbasin", "sewage"],
            "Drinking Water & RO": ["drinking water", "purifier", "ro", "dispenser", "water cooler", "filter", "smelly water"],
            "Toilet & Flush System": ["flush", "toilet", "urinal", "flush tank", "commode", "cistern"],
            "Water Supply Shortage": ["no water", "shortage", "supply", "low pressure", "empty tank"],
            "General Plumbing": []
        }
    },
    "Network & IT": {
        "keywords": [
            "wifi", "wi-fi", "internet", "network", "lan", "ethernet", "router",
            "modem", "connection", "disconnected", "offline", "slow speed",
            "broadband", "projector", "hdmi", "computer", "pc", "desktop",
            "monitor", "keyboard", "mouse", "server", "portal", "printer", "portal login"
        ],
        "subcategories": {
            "Wi-Fi & Wireless Network": ["wifi", "wi-fi", "wireless", "ssid", "signal", "access point", "hotspot"],
            "LAN & Ethernet Connection": ["lan", "ethernet", "cable", "port", "rj45", "jack", "switch port"],
            "Internet Connectivity / Outage": ["internet", "offline", "down", "disconnected", "outage", "bandwidth", "speed", "no connection"],
            "Lab Computers & Peripherals": ["computer", "pc", "desktop", "monitor", "keyboard", "mouse", "cpu", "ram", "os"],
            "Projector & AV Systems": ["projector", "screen", "hdmi", "vga", "audio", "speaker", "mic", "display"],
            "Portal & Server Systems": ["portal", "login", "server", "lms", "website", "erp", "database"],
            "General IT": []
        }
    },
    "Cleaning & Sanitation": {
        "keywords": [
            "clean", "cleaning", "dirty", "garbage", "trash", "dustbin", "waste",
            "smell", "stink", "foul", "odor", "litter", "dust", "sweep",
            "mop", "mopping", "spill", "unhygienic", "pest", "cockroach",
            "rodent", "rat", "mosquito", "washroom", "restroom cleaning"
        ],
        "subcategories": {
            "Restroom Cleanliness": ["restroom", "washroom", "toilet", "urinal", "smell", "stink", "dirty toilet", "foul"],
            "Classroom & Lab Litter": ["classroom", "lab", "benches", "board", "duster", "litter", "waste paper"],
            "Waste Management & Dustbins": ["dustbin", "garbage", "trash", "waste", "overflowing bin", "bins"],
            "Spill & Floor Maintenance": ["spill", "mop", "mopping", "mud", "stain", "slippery", "sweep"],
            "Pest Control": ["pest", "cockroach", "rat", "rodent", "mosquito", "insects", "bugs", "lizards"],
            "General Sanitation": []
        }
    },
    "Infrastructure & Civil": {
        "keywords": [
            "door", "window", "lock", "handle", "glass", "pane", "wall", "ceiling",
            "crack", "plaster", "paint", "tile", "tiles", "flooring", "furniture",
            "desk", "bench", "chair", "table", "board", "whiteboard", "blackboard",
            "staircase", "stairs", "railing", "balcony", "roof", "pothole", "gate"
        ],
        "subcategories": {
            "Door, Window & Locks": ["door", "window", "lock", "handle", "glass", "hinge", "latch", "broken glass"],
            "Walls, Ceiling & Flooring": ["wall", "ceiling", "crack", "plaster", "paint", "tile", "tiles", "flooring", "slab"],
            "Furniture & Desks": ["desk", "chair", "bench", "table", "furniture", "podium", "whiteboard", "blackboard"],
            "Staircase & Safety Railings": ["staircase", "stairs", "railing", "steps", "handrail", "balcony"],
            "Civil & Structural Works": ["roof", "road", "pathway", "pothole", "gate", "boundary", "compound"],
            "General Civil": []
        }
    },
    "Equipment & Machinery": {
        "keywords": [
            "equipment", "machine", "machinery", "instrument", "apparatus",
            "printer", "photocopier", "xerox", "scanner", "lift", "elevator",
            "fire extinguisher", "drill", "lathe", "oscilloscope", "meter", "pump"
        ],
        "subcategories": {
            "Elevator & Lift Systems": ["lift", "elevator", "stuck", "lift door", "elevator button"],
            "Laboratory Instruments": ["instrument", "apparatus", "oscilloscope", "multimeter", "microscope", "spectrometer"],
            "Office Printing & Scanning": ["printer", "photocopier", "xerox", "scanner", "cartridge", "toner", "paper jam"],
            "Workshop & Heavy Machinery": ["lathe", "drill", "motor", "pump", "compressor", "machine", "apparatus"],
            "Fire Safety Equipment": ["fire extinguisher", "fire hose", "smoke detector", "fire alarm"],
            "General Equipment": []
        }
    },
    "Security & Safety": {
        "keywords": [
            "security", "guard", "cctv", "camera", "theft", "stolen", "lost",
            "unauthorized", "trespass", "trespassing", "id card", "rfid", "gate",
            "barrier", "emergency", "dark area", "street light", "harassment", "danger"
        ],
        "subcategories": {
            "CCTV & Surveillance": ["cctv", "camera", "footage", "surveillance", "blind spot"],
            "Access Control & Gates": ["turnstile", "rfid", "id card", "gate barrier", "boom barrier", "biometric"],
            "Incident & Theft Report": ["theft", "stolen", "missing", "unauthorized", "trespass", "break-in", "fight"],
            "Campus Lighting & Night Safety": ["street light", "dark area", "corridor light", "pathway light", "night safety"],
            "General Security": []
        }
    },
    "Other": {
        "keywords": ["other", "misc", "miscellaneous", "general", "inquiry", "noise", "announcement"],
        "subcategories": {
            "General Request": [],
            "Miscellaneous": []
        }
    }
}


class ComplaintAnalyzer:
    """
    Intelligent NLP analyzer for complaints.
    Provides category classification, subcategory assignment,
    keyword extraction, and structured confidence scoring.
    """

    def __init__(self, taxonomy: Dict[str, Dict[str, Any]] = CATEGORY_TAXONOMY):
        self.taxonomy = taxonomy

    def classify_category(self, text: str) -> Tuple[str, float, Dict[str, float]]:
        """
        Classifies the text into one of the known categories using keyword match scoring.
        Returns: (best_category, confidence_score, all_category_scores)
        """
        cleaned = clean_text(text)
        tokens = set(tokenize(cleaned, remove_stopwords=False))
        
        scores: Dict[str, float] = {}
        
        for category, cat_data in self.taxonomy.items():
            if category == "Other":
                scores[category] = 0.05
                continue

            score = 0.0
            keywords = cat_data.get("keywords", [])
            
            for kw in keywords:
                if " " in kw:
                    # Multi-word phrase matching
                    if kw in cleaned:
                        score += 3.0
                else:
                    if kw in tokens:
                        score += 1.5
                    elif kw in cleaned:
                        score += 0.8
            
            scores[category] = score

        max_cat = max(scores, key=lambda k: scores[k])
        max_score = scores[max_cat]

        # Normalize confidence to 0.0 - 1.0 range
        total = sum(scores.values())
        confidence = round((max_score / total), 2) if total > 0 else 0.0

        if max_score <= 0.5:
            return "Other", 0.30, scores

        return max_cat, confidence, scores

    def detect_subcategory(self, category: str, text: str) -> str:
        """
        Detects specific subcategory within the selected category.
        """
        if category not in self.taxonomy:
            return "General Maintenance"

        subcats = self.taxonomy[category].get("subcategories", {})
        if not subcats:
            return "General Maintenance"

        cleaned = clean_text(text)
        tokens = set(tokenize(cleaned, remove_stopwords=False))

        best_subcat = None
        best_score = 0

        for subcat_name, subcat_kws in subcats.items():
            if not subcat_kws:
                continue
            
            score = 0
            for kw in subcat_kws:
                if " " in kw:
                    if kw in cleaned:
                        score += 3
                else:
                    if kw in tokens:
                        score += 2
                    elif kw in cleaned:
                        score += 1

            if score > best_score:
                best_score = score
                best_subcat = subcat_name

        if best_subcat and best_score > 0:
            return best_subcat

        # Default fallback to the first or General subcategory
        fallback = [s for s in subcats.keys() if "General" in s]
        return fallback[0] if fallback else list(subcats.keys())[0]

    def analyze(self, title: str, description: str, user_category: Optional[str] = None) -> Dict[str, Any]:
        """
        Full analysis pipeline combining title and description.
        """
        full_text = f"{title} {description}".strip()
        cleaned = clean_text(full_text)
        keywords = extract_keywords(full_text, max_keywords=5)

        detected_category, confidence, scores = self.classify_category(full_text)

        # If user explicitly provided a category and it is valid, respect user's manual selection
        final_category = user_category if (user_category and user_category != "Auto-Detect" and user_category in self.taxonomy) else detected_category
        
        detected_subcategory = self.detect_subcategory(final_category, full_text)

        return {
            "category": final_category,
            "detected_category": detected_category,
            "subcategory": detected_subcategory,
            "confidence": confidence,
            "keywords": keywords,
            "category_scores": scores,
            "cleaned_text": cleaned
        }


# Singleton instance helper
_analyzer_instance: Optional[ComplaintAnalyzer] = None

def get_analyzer() -> ComplaintAnalyzer:
    """Returns singleton ComplaintAnalyzer instance."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = ComplaintAnalyzer()
    return _analyzer_instance
