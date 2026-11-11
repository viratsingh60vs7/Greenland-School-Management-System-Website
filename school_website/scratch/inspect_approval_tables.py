import sqlite3
conn = sqlite3.connect('school_website/school.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

for tbl in ['leaves', 'lab_complaints', 'credential_change_requests']:
    print(f"\nTable {tbl}:")
    cur.execute(f"PRAGMA table_info({tbl})")
    for c in cur.fetchall():
        print(f" - {c['name']} ({c['type']})")
