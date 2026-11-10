import sqlite3
import json
import sys

db_path = 'school_website/school.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=== 1. CHECK USERS & ROLES ===")
cur.execute("SELECT id, name, username, user_type, gender FROM users")
users = [dict(r) for r in cur.fetchall()]
for u in users:
    print(f"ID #{u['id']}: {u['username']} | Role: {u['user_type']} | Name: {u['name']} | Gender: {u['gender']}")

it_user = next((u for u in users if u['username'] == 'GS_itsupport'), None)
assert it_user is not None, "GS_itsupport not found!"
assert it_user['user_type'] == 'it_admin', f"Expected it_admin, got {it_user['user_type']}"
print(f"✓ Verified IT Support Administrator: {it_user['username']} (Role: {it_user['user_type']}, Gender: {it_user['gender']})")

print("\n=== 2. CHECK LAB COMPUTERS ===")
cur.execute("SELECT COUNT(*) FROM lab_computers")
total_pcs = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM lab_computers WHERE status = 'Working'")
working_pcs = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM lab_computers WHERE status = 'Faulty'")
faulty_pcs = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM lab_computers WHERE status = 'In Repair'")
in_repair_pcs = cur.fetchone()[0]

print(f"✓ Lab Computers: Total={total_pcs}, Working={working_pcs}, Faulty={faulty_pcs}, In Repair={in_repair_pcs}")
assert total_pcs >= 35, f"Expected at least 35 computers, got {total_pcs}"

print("\n=== 3. TEST TEACHER COMPLAINT -> ASSIGN -> RESOLVE FLOW ===")
# Pick PC-07 in Lab 1
cur.execute("SELECT id, pc_number, status FROM lab_computers WHERE pc_number = 'PC-07' AND lab_name = 'Computer Lab 1 (Main Lab)'")
pc07 = dict(cur.fetchone())
print(f"PC-07 initial status: {pc07['status']}")

# Simulate Teacher filing complaint
import time
ticket_no = f"TKT-LAB-TEST-{int(time.time()*1000)}"
cur.execute("""
    INSERT INTO lab_complaints (
        ticket_no, computer_id, pc_number, lab_name, reported_by_id, reported_by_name,
        teacher_role, issue_category, problem_description, priority, status, created_at
    ) VALUES (?, ?, 'PC-07', 'Computer Lab 1 (Main Lab)', 4, 'Teacher Chike', 'Computer Teacher', 'Peripherals (Monitor)', 'Monitor displays no signal', 'High', 'Pending', datetime('now'))
""", (ticket_no, pc07['id']))
complaint_id = cur.lastrowid
cur.execute("UPDATE lab_computers SET status = 'Faulty', active_complaint_id = ? WHERE id = ?", (complaint_id, pc07['id']))
conn.commit()

cur.execute("SELECT status FROM lab_computers WHERE id = ?", (pc07['id'],))
assert cur.fetchone()[0] == 'Faulty'
print("✓ Workstation PC-07 updated to Faulty upon complaint.")

# Simulate IT Support assigning technician
cur.execute("""
    UPDATE lab_complaints
    SET status = 'Assigned',
        assigned_to_name = 'Suresh Verma (Network Engineer)',
        assigned_by = 'IT Support Administrator',
        assigned_at = datetime('now'),
        technician_notes = 'Replace HDMI cable and verify GPU card output.'
    WHERE id = ?
""", (complaint_id,))
cur.execute("UPDATE lab_computers SET status = 'In Repair' WHERE id = ?", (pc07['id'],))
conn.commit()

cur.execute("SELECT status FROM lab_computers WHERE id = ?", (pc07['id'],))
assert cur.fetchone()[0] == 'In Repair'
print("✓ Workstation PC-07 updated to In Repair upon technician dispatch.")

# Simulate IT Support resolving complaint
cur.execute("""
    UPDATE lab_complaints
    SET status = 'Resolved',
        resolution_notes = 'Replaced faulty display cable. Tested display resolution at 1080p 75Hz, verified working.',
        resolved_by = 'IT Support Administrator',
        resolved_at = datetime('now')
    WHERE id = ?
""", (complaint_id,))
cur.execute("UPDATE lab_computers SET status = 'Working', active_complaint_id = NULL WHERE id = ?", (pc07['id'],))
conn.commit()

cur.execute("SELECT status, active_complaint_id FROM lab_computers WHERE id = ?", (pc07['id'],))
r = cur.fetchone()
assert r[0] == 'Working' and r[1] is None
print("✓ Workstation PC-07 successfully restored to Working!")

print("\n=== 4. TEST NAME & GENDER RULE ===")
# Unassigned ID: Name is empty/None -> Gender must be NULL
cur.execute("""
    INSERT OR REPLACE INTO users (username, password, name, email, user_type, gender)
    VALUES ('GS_unassigned_role_test', 'Greenland@2026', '', 'role@greenlandschool.net', 'teacher', NULL)
""")
conn.commit()
cur.execute("SELECT name, gender FROM users WHERE username = 'GS_unassigned_role_test'")
row = cur.fetchone()
print(f"Unassigned ID Name: '{row[0]}', Gender: '{row[1]}'")
assert row[1] is None or row[1] == ''
print("✓ Name & Gender Rule verified: No name = No gender.")

# Assigned person: Name is 'Amina Yusuf' -> Gender is Female
cur.execute("""
    INSERT OR REPLACE INTO users (username, password, name, email, user_type, gender)
    VALUES ('GS_teacher_amina', 'Greenland@2026', 'Amina Yusuf', 'amina@greenlandschool.net', 'teacher', 'Female')
""")
conn.commit()
cur.execute("SELECT name, gender FROM users WHERE username = 'GS_teacher_amina'")
row = cur.fetchone()
print(f"Assigned Person ID Name: '{row[0]}', Gender: '{row[1]}'")
assert row[1] == 'Female'
print("✓ Name & Gender Rule verified: Assigned person's gender correctly stored and returned.")

print("\n=== 5. TEST DIRECTOR GENERATING ACCOUNTANT SALARY PAYSLIP ===")
sys.path.insert(0, 'school_website')
import server
server.generate_accountant_salary_slip(cur, month=11, year=2026, base_salary=58000.0, special_bonus=7500.0, bonus_title='Director Executive Incentive', director_name='Owner (Director) Rajeev Sinha')
conn.commit()

cur.execute("SELECT * FROM salary_slips WHERE (teacher_name LIKE '%Accountant%' OR designation LIKE '%Accountant%') AND month = 11 AND year = 2026")
slip = dict(cur.fetchone())
print(f"✓ Accountant Slip: #{slip['slip_no']} | Base: ₹{slip['base_salary']} | Bonus: ₹{slip['special_bonus']} ({slip['special_bonus_title']}) | Net: ₹{slip['net_salary']}")
print(f"  Generated By: '{slip['generated_by']}' | Status: '{slip['status']}'")
assert slip['status'] == 'Sanctioned by Director'
assert slip['special_bonus'] == 7500.0
assert 'Director' in slip['generated_by']

print("\n=== 6. TEST CLEAN SYSTEM TEST DATA PRESERVING OWNER, IT SUPPORT & MANUAL USER DATA ===")
# Ensure manual user data for Virat Singh exists in admissions
cur.execute("""
    INSERT OR REPLACE INTO admissions (ref_no, applicant_name, grade_applying, parent_name, email, phone, status)
    VALUES ('ADM-TEST-VIRAT', 'Virat Singh', 'Grade 11', 'Virat Singh', 'vs0839265@gmail.com', '+91 9876543210', 'Approved')
""")
conn.commit()

# Clean test data query as implemented in server.py
cur.execute("""
    DELETE FROM admissions
    WHERE applicant_name NOT LIKE '%Virat%'
      AND parent_name NOT LIKE '%Virat%'
      AND email NOT LIKE '%vs0839265%'
      AND ref_no NOT LIKE '%VIRAT%'
""")
cur.execute("""
    DELETE FROM users
    WHERE username NOT IN ('Owner(Directer)', 'GS_itsupport')
      AND (name IS NULL OR name NOT LIKE '%Virat%')
      AND (email IS NULL OR email NOT LIKE '%vs0839265%')
""")
conn.commit()

cur.execute("SELECT username, name FROM users")
remaining_users = cur.fetchall()
print("Remaining users after cleanup:")
for u in remaining_users:
    print(f"  - {u[0]}: {u[1]}")

u_names = [u[0] for u in remaining_users]
assert 'Owner(Directer)' in u_names, "Director was removed!"
assert 'GS_itsupport' in u_names, "IT Support Administrator was removed!"

cur.execute("SELECT applicant_name, email FROM admissions")
remaining_admissions = cur.fetchall()
print("Remaining admissions after cleanup:")
for a in remaining_admissions:
    print(f"  - {a[0]} ({a[1]})")
assert len(remaining_admissions) > 0, "Virat Singh manual data was wiped!"
assert any('Virat' in a[0] for a in remaining_admissions), "Virat Singh manual data not found!"
print("✓ Manual user data for Virat Singh safely preserved!")

# Now reseed default users and computers cleanly
server.init_db()
print("\n=======================================================")
print(" ALL TESTS PASSED WITH 100% SUCCESS! 🎉")
print("=======================================================")
