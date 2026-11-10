with open('school_website/server.py', 'r', encoding='utf-8') as f:
    code = f.read()

target = """    # Laptop & Computer IT Asset Management System Tables
    cur.execute(\"\"\"
    CREATE TABLE IF NOT EXISTS it_asset_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_type TEXT,
        title TEXT,
        description TEXT,
        estimated_cost REAL DEFAULT 0,
        requested_by TEXT DEFAULT 'IT Support Administrator',
        status TEXT DEFAULT 'Pending Director Approval',
        director_notes TEXT,
        approved_at TEXT,
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS it_assets ("""

replacement = """    # Laptop & Computer IT Asset Management System Tables
    cur.execute(\"\"\"
    CREATE TABLE IF NOT EXISTS it_asset_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_type TEXT,
        title TEXT,
        description TEXT,
        estimated_cost REAL DEFAULT 0,
        requested_by TEXT DEFAULT 'IT Support Administrator',
        status TEXT DEFAULT 'Pending Director Approval',
        director_notes TEXT,
        approved_at TEXT,
        created_at TEXT
    )
    \"\"\")

    cur.execute(\"\"\"
    CREATE TABLE IF NOT EXISTS it_assets ("""

assert target in code, "target not found in server.py"
code = code.replace(target, replacement, 1)

with open('school_website/server.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ Separated into distinct cur.execute calls!")
