with open('school_website/server.py', 'r', encoding='utf-8') as f:
    code = f.read()

bad_block = """    # Laptop & Computer IT Asset Management System Tables
    cur.execute(\"\"\"
    
    # IT Asset Requests created by IT Team requiring Director Approval
    cur.execute('''
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
    ''')
CREATE TABLE IF NOT EXISTS it_assets ("""

clean_block = """    # Laptop & Computer IT Asset Management System Tables
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

assert bad_block in code, "bad_block not found in server.py"
code = code.replace(bad_block, clean_block, 1)

with open('school_website/server.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ Fixed SQL schema syntax in init_db()!")
