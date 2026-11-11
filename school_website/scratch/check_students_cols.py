import sqlite3

conn = sqlite3.connect('school_website/school.db')
cur = conn.cursor()
cur.execute("PRAGMA table_info(students)")
print("=== STUDENTS COLUMNS ===")
for col in cur.fetchall():
    print(col)

cur.execute("PRAGMA table_info(admissions)")
print("\n=== ADMISSIONS COLUMNS ===")
for col in cur.fetchall():
    print(col)
