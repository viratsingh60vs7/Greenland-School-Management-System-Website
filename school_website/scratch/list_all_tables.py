import sqlite3
conn = sqlite3.connect('school_website/school.db')
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("Tables in school.db:")
for t in tables:
    print(" -", t)
