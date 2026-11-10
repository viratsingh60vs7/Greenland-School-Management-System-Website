import sqlite3
conn = sqlite3.connect('school_website/school.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("PRAGMA table_info(credential_change_requests)")
for c in cur.fetchall():
    print(f" - {c['name']} ({c['type']})")
