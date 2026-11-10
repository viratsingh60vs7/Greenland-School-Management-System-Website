import sqlite3
conn = sqlite3.connect('school_website/school.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT * FROM users WHERE name LIKE '%Virat%'")
for r in cur.fetchall():
    print(dict(r))
