import sqlite3
conn = sqlite3.connect('school_website/school.db')
cur = conn.cursor()
cur.execute("PRAGMA table_info(payments)")
for c in cur.fetchall():
    print(c)
