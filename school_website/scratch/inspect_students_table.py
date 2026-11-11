import sqlite3
conn = sqlite3.connect('school_website/school.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("Students table columns:")
cur.execute("PRAGMA table_info(students)")
for col in cur.fetchall():
    print(f" - {col['name']} ({col['type']})")

print("\nSample students:")
cur.execute("SELECT id, user_id, parent_id, admission_number, roll_number, parent_name, phone FROM students LIMIT 5")
for s in cur.fetchall():
    print(dict(s))
