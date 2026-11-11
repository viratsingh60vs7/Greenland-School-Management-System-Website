import sqlite3, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_test():
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'school.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    print("--- Testing SQL logic ---")
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
    cur.execute("DELETE FROM book_requests WHERE user_id NOT IN (SELECT id FROM users)")
    cur.execute("DELETE FROM payment_delete_requests")
    cur.execute("""
        DELETE FROM notifications_outbox 
        WHERE (recipient_email IS NULL OR recipient_email NOT LIKE '%vs0839265%')
          AND (applicant_name IS NULL OR applicant_name NOT LIKE '%Virat%')
    """)
    cur.execute("UPDATE users SET gender = NULL WHERE name IS NULL OR TRIM(name) = ''")
    conn.commit()

    cur.execute("SELECT id, username, name, user_type, gender FROM users")
    users = cur.fetchall()
    print("Remaining users:")
    for u in users:
        print(f"  {u['id']}: {u['username']} | {u['name']} | Role: {u['user_type']} | Gender: {u['gender']}")

    cur.execute("SELECT COUNT(*) FROM students")
    print(f"Remaining students: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM admissions")
    print(f"Remaining admissions: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM credential_requests")
    print(f"Remaining credential_requests: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM lab_complaints")
    print(f"Remaining lab_complaints: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM lab_computers WHERE status != 'Working'")
    print(f"Faulty computers: {cur.fetchone()[0]}")

    # Now verify that init_db does NOT re-add unwanted demo users or students!
    from server import init_db
    init_db()

    cur.execute("SELECT COUNT(*) FROM users")
    u_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM students")
    s_count = cur.fetchone()[0]
    print(f"After init_db() -> Users: {u_count}, Students: {s_count}")
    assert s_count == 0, f"Expected 0 students after clean and init_db, got {s_count}"
    assert u_count == len(users), f"Expected {len(users)} users after clean and init_db, got {u_count}"
    print("✓ All clean test assertions PASSED!")

if __name__ == '__main__':
    run_test()
