import urllib.request
import json

base_url = 'http://127.0.0.1:5000'

def req(path, method='GET', data=None):
    url = base_url + path
    headers = {'Content-Type': 'application/json'}
    body = json.dumps(data).encode('utf-8') if data else None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(r, timeout=10) as resp:
        return json.loads(resp.read().decode('utf-8'))

# 1. Fetch users
users = req('/api/users')
print(f"Total system users: {len(users)}")

students = [u for u in users if u['user_type'] == 'student']
parents = [u for u in users if u['user_type'] == 'parent']
staff = [u for u in users if u['user_type'] in ('teacher', 'it_admin', 'super_admin', 'admin', 'accountant', 'librarian')]

print(f"Found {len(students)} student(s), {len(parents)} parent(s), and {len(staff)} staff/faculty member(s).")

# Simulate client populateAdminIdOptions
eligible_admins = [u for u in users if u['user_type'] not in ('student', 'parent', 'common_id')]

print("\nEligible Admins for Common ID:")
for a in eligible_admins:
    print(f"  • {a['name']} ({a['username']}) - [{a['user_type']}]")

assert not any(a['user_type'] in ('student', 'parent') for a in eligible_admins), "CRITICAL: Student or parent found in eligible admins!"
assert any(a['username'] == 'GS_teacher' for a in eligible_admins), "GS_teacher must be in eligible admins"

# 2. Test backend enforcement: Attempt to create a Common ID passing a student ID as admin
if students:
    student_u = students[0]
    print(f"\nTesting backend protection: Attempting to assign student '{student_u['name']}' ({student_u['username']}) as Admin for Common ID...")
    
    test_res = req('/api/users/create', method='POST', data={
        'username': 'GS_test_sec_lab',
        'password': 'Greenland@2026',
        'role': 'common_id',
        'name': 'Security Lab Test Fleet',
        'is_common_id': 1,
        'common_id_name': 'Security Lab Test Fleet',
        'admin_user_id': student_u['id'],
        'admin_username': student_u['username'],
        'caller_username': 'GS_itsupport',
        'caller_id': 2
    })
    print("Backend create response:", test_res)
    assert test_res.get('success') is True
    # Verify student was rejected as admin!
    assert test_res.get('admin_username') is None, "Student must NOT be accepted as admin for Common ID"
    assert test_res.get('admin_user_id') is None, "Student ID must NOT be accepted as admin for Common ID"
    print("SUCCESS: Backend properly rejected student account from being assigned as admin!")

    # Clean up test user
    import sqlite3
    conn = sqlite3.connect('school_website/school.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE username = 'GS_test_sec_lab'")
    conn.commit()
    conn.close()

# 3. Test assigning Computer Teacher (GS_teacher)
teacher_u = next((u for u in staff if u['username'] == 'GS_teacher'), None)
if teacher_u:
    print(f"\nTesting assigning Teacher '{teacher_u['name']}' ({teacher_u['username']}) as Admin for Common ID...")
    test_t_res = req('/api/users/create', method='POST', data={
        'username': 'GS_test_teacher_lab',
        'password': 'Greenland@2026',
        'role': 'common_id',
        'name': 'Teacher Verified Lab Fleet',
        'is_common_id': 1,
        'common_id_name': 'Teacher Verified Lab Fleet',
        'admin_user_id': teacher_u['id'],
        'admin_username': teacher_u['username'],
        'caller_username': 'GS_itsupport',
        'caller_id': 2
    })
    print("Backend create response with teacher:", test_t_res)
    assert test_t_res.get('admin_username') == 'GS_teacher', "Teacher must be accepted as admin"
    print("SUCCESS: Teacher successfully accepted as admin!")

    # Clean up test user
    import sqlite3
    conn = sqlite3.connect('school_website/school.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE username = 'GS_test_teacher_lab'")
    conn.commit()
    conn.close()

print("\nALL VERIFICATIONS PASSED: Students & Parents strictly excluded from Common ID Admin role! 🎯")
