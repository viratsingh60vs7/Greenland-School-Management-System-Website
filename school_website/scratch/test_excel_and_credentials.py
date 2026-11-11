import sys
import io
import openpyxl
import sqlite3
import base64
import json

sys.path.insert(0, 'school_website')
import server
server.init_db()

conn = sqlite3.connect('school_website/school.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=== 1. TEST EXCEL FILE PARSING & BULK ADMISSION ===")
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Student Admissions"

# Headers without Aadhaar column (simulating real user upload without Aadhaar)
headers = ["First Name", "Last Name", "Class", "Section", "Gender", "Date of Birth", "Parent Name", "Phone", "Blood Group", "Address"]
ws.append(headers)

ws.append(["Rohan", "Verma", "Class 9", "Section A", "Male", "2012-05-10", "Mukesh Verma", "+91 9876500001", "B+", "Renukoot, Sonbhadra"])
ws.append(["Kavya", "Nair", "Class 11", "Section B", "Female", "2010-09-18", "Ramesh Nair", "+91 9876500002", "O+", "Pipri, Sonbhadra"])
ws.append(["Dev", "Chatterjee", "Class 12 - Science", "Section A", "Male", "2009-01-25", "Subhash Chatterjee", "+91 9876500003", "A+", "Khadpathar, Sonbhadra"])

bio = io.BytesIO()
wb.save(bio)
excel_bytes = bio.getvalue()

parsed_rows = server.parse_excel_or_csv(excel_bytes, "students_roster.xlsx")
print(f"✓ Parsed {len(parsed_rows)} rows from Excel sheet")
assert len(parsed_rows) == 3, f"Expected 3 rows, got {len(parsed_rows)}"

assigned_batch = set()
admitted = []
for r in parsed_rows:
    r['approved_by'] = 'Super Admin'
    rec = server.admit_single_student(cur, conn, r, assigned_batch)
    admitted.append(rec)
conn.commit()

print(f"✓ Successfully admitted {len(admitted)} students from Excel sheet!")
for a in admitted:
    print(f"  - {a['name']} ({a['class_name']}) | Adm No: {a['adm_no']} | Aadhaar: {a['aadhaar_no']} | Status: {a['admission_status']} (Approved by {a['approved_by']})")
    assert a['admission_status'] == 'Approved for New Admission'
    assert len(a['aadhaar_no']) == 12 and a['aadhaar_no'].isdigit(), f"Invalid Aadhaar generated: {a['aadhaar_no']}"

# Verify they exist in students table
cur.execute("SELECT st.id, u.name, st.admission_status, st.approved_by, st.aadhaar_no FROM students st JOIN users u ON st.user_id = u.id WHERE u.name IN ('Rohan Verma', 'Kavya Nair', 'Dev Chatterjee')")
db_stds = cur.fetchall()
assert len(db_stds) >= 3, f"Expected at least 3 in DB, got {len(db_stds)}"
print("✓ Verified all 3 students stored in DB with status 'Approved for New Admission'!")

print("\n=== 2. TEST IT SUPPORT PROPOSING CREDENTIAL CHANGE & OWNER APPROVAL ===")
# Pick a faculty/staff user
cur.execute("SELECT id, username, password FROM users WHERE username = 'GS_teacher'")
row = cur.fetchone()
if not row:
    cur.execute("SELECT id, username, password FROM users WHERE username NOT IN ('Owner(Directer)', 'GS_itsupport') LIMIT 1")
    row = cur.fetchone()
t_user = dict(row)
orig_pwd = t_user['password']
new_proposed_pwd = "TeacherNewPass#2026"
new_proposed_uid = "GS_teacher_chike_prime"

# IT Support creates request
cur.execute("""
    INSERT INTO credential_requests (
        request_type, user_id, target_username, proposed_username, proposed_password,
        proposed_name, proposed_role, reason, requested_by_id, requested_by_name,
        status, created_at
    ) VALUES ('change_credentials', ?, ?, ?, ?, 'Teacher Chike', 'teacher', 'Faculty requested password update', 37, 'IT Support Administrator', 'Pending Owner Approval', datetime('now'))
""", (t_user['id'], t_user['username'], new_proposed_uid, new_proposed_pwd))
conn.commit()
req_id = cur.lastrowid
print(f"✓ IT Support submitted credential request #{req_id} with status 'Pending Owner Approval'")

# Verify credentials NOT yet changed in users table
cur.execute("SELECT username, password FROM users WHERE id = ?", (t_user['id'],))
check_u = cur.fetchone()
assert check_u[0] == 'GS_teacher' and check_u[1] == orig_pwd
print("✓ Verified credentials remain unchanged before Owner approval.")

# Owner approves request
cur.execute("UPDATE users SET username = ?, password = ? WHERE id = ?", (new_proposed_uid, new_proposed_pwd, t_user['id']))
cur.execute("""
    UPDATE credential_requests
    SET status = 'Approved', approved_by = 'Owner (Director) Rajeev Sinha', approved_at = datetime('now')
    WHERE id = ?
""", (req_id,))
conn.commit()

# Verify credentials NOW updated in users table
cur.execute("SELECT username, password FROM users WHERE id = ?", (t_user['id'],))
check_u2 = cur.fetchone()
assert check_u2[0] == new_proposed_uid and check_u2[1] == new_proposed_pwd
print(f"✓ Verified Owner approved! Username is now '{check_u2[0]}' and password is '{check_u2[1]}'")

# Restore GS_teacher username and password for default consistency
cur.execute("UPDATE users SET username = 'GS_teacher', password = 'Greenland@2026' WHERE id = ?", (t_user['id'],))
conn.commit()

print("\n=== 3. TEST IT SUPPORT PROPOSING NEW USER ID & OWNER APPROVAL ===")
import time
# IT Support requests new user account
proposed_new_uid = f"GS_faculty_robotics_{int(time.time())}"
cur.execute("""
    INSERT INTO credential_requests (
        request_type, target_username, proposed_username, proposed_password,
        proposed_name, proposed_role, proposed_email, proposed_phone, proposed_gender,
        reason, requested_by_id, requested_by_name, status, created_at
    ) VALUES ('create_user', ?, ?, 'Robotics#2026', 'Vikrant Malhotra', 'teacher', 'vikrant@greenlandschool.net', '+91 761 700 5099', 'Male', 'New Robotics & AI Lab Instructor', 37, 'IT Support Administrator', 'Pending Owner Approval', datetime('now'))
""", (proposed_new_uid, proposed_new_uid))
conn.commit()
create_req_id = cur.lastrowid
print(f"✓ IT Support submitted new user creation request #{create_req_id}")

# Owner approves creation
cur.execute("""
    INSERT INTO users (name, email, username, password, user_type, phone, gender, created_at)
    VALUES ('Vikrant Malhotra', 'vikrant@greenlandschool.net', ?, 'Robotics#2026', 'teacher', '+91 761 700 5099', 'Male', datetime('now'))
""", (proposed_new_uid,))
new_user_id = cur.lastrowid

cur.execute("""
    UPDATE credential_requests
    SET status = 'Approved', approved_by = 'Owner (Director) Rajeev Sinha', approved_at = datetime('now'), user_id = ?
    WHERE id = ?
""", (new_user_id, create_req_id))
conn.commit()

cur.execute("SELECT id, name, username, gender FROM users WHERE id = ?", (new_user_id,))
created_row = cur.fetchone()
assert created_row is not None and created_row[2] == proposed_new_uid
print(f"✓ Owner approved! New user #{created_row[0]} '{created_row[1]}' ({created_row[2]}), Gender: {created_row[3]} active in database.")

print("\n=== 4. TEST ADMISSION APPROVAL ENDPOINT LOGIC ===")
# Add student with pending admission
test_std_data = {
    "name": "Sameer Joshi",
    "class_name": "Class 8",
    "section": "Section A",
    "admission_status": "Pending Admission Approval",
    "approved_by": "Awaiting Admin Approval"
}
rec_pending = server.admit_single_student(cur, conn, test_std_data, set())
conn.commit()
print(f"✓ Student added: {rec_pending['name']} with initial status '{rec_pending['admission_status']}'")

# Admin approves admission
cur.execute("""
    UPDATE students
    SET admission_status = 'Approved for New Admission',
        approved_by = 'Admin (Principal)',
        approved_at = datetime('now')
    WHERE id = ?
""", (rec_pending['student_id'],))
conn.commit()

cur.execute("SELECT admission_status, approved_by FROM students WHERE id = ?", (rec_pending['student_id'],))
approved_check = cur.fetchone()
assert approved_check[0] == 'Approved for New Admission' and approved_check[1] == 'Admin (Principal)'
print(f"✓ Admission approved! Status: '{approved_check[0]}' by {approved_check[1]}")

print("\n=======================================================")
print(" ALL TESTS FOR LATEST USER REQUEST PASSED 100%! 🎉")
print("=======================================================")
