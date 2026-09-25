"""
Database Schema definition for CivicPulse AI.
Defines table structures, constraints, and indexes for SQLite.
"""

CREATE_COMPLAINTS_TABLE = """
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    location TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT NOT NULL,
    priority TEXT NOT NULL,
    priority_reason TEXT DEFAULT '',
    department TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pending',
    admin_notes TEXT DEFAULT '',
    similar_count INTEGER DEFAULT 0,
    top_similar_id TEXT DEFAULT '',
    top_similarity_score REAL DEFAULT 0.0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    resolved_at TEXT DEFAULT NULL
);
"""

CREATE_STATUS_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS status_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id TEXT NOT NULL,
    old_status TEXT NOT NULL,
    new_status TEXT NOT NULL,
    changed_by TEXT DEFAULT 'System',
    comment TEXT DEFAULT '',
    changed_at TEXT NOT NULL,
    FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id) ON DELETE CASCADE
);
"""

CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_complaints_cid ON complaints(complaint_id);",
    "CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status);",
    "CREATE INDEX IF NOT EXISTS idx_complaints_priority ON complaints(priority);",
    "CREATE INDEX IF NOT EXISTS idx_complaints_category ON complaints(category);",
    "CREATE INDEX IF NOT EXISTS idx_complaints_location ON complaints(location);",
    "CREATE INDEX IF NOT EXISTS idx_complaints_created_at ON complaints(created_at);",
    "CREATE INDEX IF NOT EXISTS idx_status_history_cid ON status_history(complaint_id);"
]
