import sqlite3

conn = sqlite3.connect('school_website/school.db')
cur = conn.cursor()

# 1. Add credential_requests table
cur.execute("""
CREATE TABLE IF NOT EXISTS credential_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_type TEXT NOT NULL,
    user_id INTEGER,
    target_username TEXT,
    proposed_username TEXT,
    proposed_password TEXT,
    proposed_name TEXT,
    proposed_role TEXT,
    proposed_email TEXT,
    proposed_phone TEXT,
    proposed_gender TEXT,
    reason TEXT,
    requested_by_id INTEGER,
    requested_by_name TEXT,
    status TEXT DEFAULT 'Pending Owner Approval',
    approved_by TEXT,
    approved_at TEXT,
    rejection_reason TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

# 2. Add admission columns to students table if not exist
for col_def in [
    "ALTER TABLE students ADD COLUMN admission_status TEXT DEFAULT 'Approved for New Admission'",
    "ALTER TABLE students ADD COLUMN approved_by TEXT DEFAULT 'Super Admin'",
    "ALTER TABLE students ADD COLUMN approved_at TEXT"
]:
    try:
        cur.execute(col_def)
    except Exception:
        pass

cur.execute("UPDATE students SET admission_status = 'Approved for New Admission' WHERE admission_status IS NULL OR admission_status = ''")
conn.commit()

print("Schema updated successfully!")
cur.execute("PRAGMA table_info(credential_requests)")
print("credential_requests cols:", [r[1] for r in cur.fetchall()])
cur.execute("PRAGMA table_info(students)")
print("students cols:", [r[1] for r in cur.fetchall()])
