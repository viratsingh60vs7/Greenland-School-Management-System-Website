import sqlite3

conn = sqlite3.connect('school_website/school.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=== ACTIVE USERS IN DB ===")
cur.execute("SELECT id, username, name, user_type, gender FROM users")
for r in cur.fetchall():
    print(f"  - ID {r['id']}: {r['username']} ({r['name']}), Role: {r['user_type']}, Gender: {r['gender']}")

print("\n=== RECORD COUNTS IN DB ===")
for tbl in ['students', 'admissions', 'credential_requests', 'payments', 'marks', 'attendance', 'leaves', 'salary_slips', 'lab_complaints']:
    cur.execute(f"SELECT COUNT(*) FROM {tbl}")
    print(f"  {tbl}: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM lab_computers WHERE status != 'Working'")
print(f"  faulty lab_computers: {cur.fetchone()[0]}")
