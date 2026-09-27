CREATE TABLE IF NOT EXISTS complaints (
    id SERIAL PRIMARY KEY,
    complaint_id TEXT NOT NULL UNIQUE,
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

CREATE TABLE IF NOT EXISTS status_history (
    id SERIAL PRIMARY KEY,
    complaint_id TEXT NOT NULL,
    old_status TEXT NOT NULL,
    new_status TEXT NOT NULL,
    changed_by TEXT DEFAULT 'System',
    comment TEXT DEFAULT '',
    changed_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_complaints_complaint_id
ON complaints(complaint_id);

CREATE INDEX IF NOT EXISTS idx_complaints_status
ON complaints(status);

CREATE INDEX IF NOT EXISTS idx_complaints_category
ON complaints(category);

CREATE INDEX IF NOT EXISTS idx_status_history_complaint_id
ON status_history(complaint_id);