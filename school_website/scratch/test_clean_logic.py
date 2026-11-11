import sqlite3

conn = sqlite3.connect('school_website/school.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=== BEFORE CLEAN TEST DATA ===")
for tbl in ['users', 'students', 'admissions', 'credential_requests', 'payments', 'marks', 'attendance', 'leaves', 'salary_slips', 'lab_complaints']:
    cur.execute(f"SELECT COUNT(*) FROM {tbl}")
    print(f"  {tbl}: {cur.fetchone()[0]}")

# Execute full clean test data logic
cur.execute("""
    DELETE FROM users
    WHERE username NOT IN ('Owner(Directer)', 'GS_itsupport')
      AND (name IS NULL OR name NOT LIKE '%Virat%')
      AND (email IS NULL OR email NOT LIKE '%vs0839265%')
      AND (username NOT LIKE '%virat%')
""")

cur.execute("""
    DELETE FROM students
    WHERE user_id NOT IN (SELECT id FROM users)
      AND (adm_no NOT LIKE '%VIRAT%')
""")

cur.execute("""
    DELETE FROM admissions
    WHERE (applicant_name IS NULL OR applicant_name NOT LIKE '%Virat%')
      AND (parent_name IS NULL OR parent_name NOT LIKE '%Virat%')
      AND (email IS NULL OR email NOT LIKE '%vs0839265%')
      AND (ref_no IS NULL OR ref_no NOT LIKE '%VIRAT%')
""")

cur.execute("DELETE FROM credential_requests")
cur.execute("DELETE FROM payments WHERE student_id NOT IN (SELECT id FROM students)")
cur.execute("DELETE FROM marks WHERE student_id NOT IN (SELECT id FROM students)")
cur.execute("DELETE FROM attendance WHERE student_id NOT IN (SELECT id FROM students)")
cur.execute("DELETE FROM leaves WHERE user_id NOT IN (SELECT id FROM users)")
cur.execute("DELETE FROM salary_slips WHERE teacher_id NOT IN (SELECT id FROM users)")
cur.execute("DELETE FROM special_bonuses")
cur.execute("DELETE FROM lab_complaints")
cur.execute("UPDATE lab_computers SET status = 'Working', active_complaint_id = NULL")
cur.execute("DELETE FROM book_requests WHERE student_id NOT IN (SELECT id FROM students)")
cur.execute("DELETE FROM payment_delete_requests")
cur.execute("DELETE FROM notifications_outbox WHERE recipient NOT LIKE '%vs0839265%' AND recipient NOT LIKE '%Virat%'")
cur.execute("UPDATE users SET gender = NULL WHERE name IS NULL OR TRIM(name) = ''")
conn.commit()

print("\n=== AFTER CLEAN TEST DATA ===")
for tbl in ['users', 'students', 'admissions', 'credential_requests', 'payments', 'marks', 'attendance', 'leaves', 'salary_slips', 'lab_complaints']:
    cur.execute(f"SELECT COUNT(*) FROM {tbl}")
    print(f"  {tbl}: {cur.fetchone()[0]}")

cur.execute("SELECT id, username, name, user_type FROM users")
print("\nRemaining active users:")
for u in cur.fetchall():
    print(f"  - {u['id']}: {u['username']} ({u['name']}), Role: {u['user_type']}")

cur.execute("SELECT id, applicant_name, email FROM admissions")
print("\nRemaining admissions:")
for a in cur.fetchall():
    print(f"  - {a['id']}: {a['applicant_name']} ({a['email']})")

print("\n✓ Clean test data logic executed with 0 errors!")
