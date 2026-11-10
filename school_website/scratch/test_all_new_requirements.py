import urllib.request
import json

BASE = "http://localhost:5000"

def get(path):
    req = urllib.request.Request(BASE + path)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def post(path, data):
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(BASE + path, data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

print("=== 1. TEST IT SUPPORT ADMINISTRATOR USER ===")
users = get('/api/users')
it_user = next((u for u in users if u['username'] == 'GS_itsupport'), None)
assert it_user is not None, "GS_itsupport user not found!"
print(f"✓ Found IT Support Administrator: {it_user['name']} ({it_user['username']}), Role: {it_user['user_type']}")

print("\n=== 2. TEST LAB COMPUTERS LIST & SUMMARY ===")
lab_info = get('/api/lab/computers')
assert lab_info['success'] is True
summary = lab_info['summary']
print(f"✓ Lab Computers Total: {summary['total']}, Working: {summary['working']}, Faulty: {summary['faulty']}, In Repair: {summary['in_repair']}")
assert summary['total'] >= 35, f"Expected at least 35 computers, got {summary['total']}"

print("\n=== 3. TEST TEACHER LODGING LAB COMPLAINT ===")
complaint_payload = {
    "lab_name": "Computer Lab 1 (Main Lab)",
    "pc_number": "PC-05",
    "issue_category": "Software / OS Crash / BlueScreen",
    "problem_description": "Blue screen of death on startup during Grade 10 Python lab class.",
    "priority": "High",
    "user_id": 4,
    "username": "GS_teacher"
}
res_c = post('/api/lab/complaints', complaint_payload)
print(f"✓ Complaint response: {res_c['message']}, Ticket: {res_c.get('ticket_no')}")
complaint_id = res_c['complaint_id']

# Verify PC-05 is now Faulty
pc_check = get('/api/lab/computers')
pc05 = next(c for c in pc_check['computers'] if c['pc_number'] == 'PC-05' and c['lab_name'] == 'Computer Lab 1 (Main Lab)')
assert pc05['status'] == 'Faulty', f"Expected Faulty, got {pc05['status']}"
print(f"✓ Workstation PC-05 status updated to: {pc05['status']}")

print("\n=== 4. TEST IT SUPPORT ASSIGNING TECHNICIAN ===")
assign_payload = {
    "complaint_id": complaint_id,
    "assigned_to_name": "Suresh Verma (Network Engineer)",
    "technician_notes": "Check OS boot partition and restore system image.",
    "user_id": it_user['id'],
    "username": it_user['username']
}
res_a = post('/api/lab/complaints/assign', assign_payload)
print(f"✓ Assign response: {res_a['message']}")

# Verify PC-05 is now In Repair
pc_check2 = get('/api/lab/computers')
pc05_repair = next(c for c in pc_check2['computers'] if c['pc_number'] == 'PC-05' and c['lab_name'] == 'Computer Lab 1 (Main Lab)')
assert pc05_repair['status'] == 'In Repair', f"Expected In Repair, got {pc05_repair['status']}"
print(f"✓ Workstation PC-05 status updated to: {pc05_repair['status']}")

print("\n=== 5. TEST IT SUPPORT RESOLVING COMPLAINT & RESTORING OPERATIONAL STATUS ===")
resolve_payload = {
    "complaint_id": complaint_id,
    "resolution_notes": "Re-imaged Windows 11 Pro system partition. Stress-tested with lab software, all diagnostics passed 100%.",
    "user_id": it_user['id'],
    "username": it_user['username']
}
res_r = post('/api/lab/complaints/resolve', resolve_payload)
print(f"✓ Resolve response: {res_r['message']}")

# Verify PC-05 is now Working
pc_check3 = get('/api/lab/computers')
pc05_working = next(c for c in pc_check3['computers'] if c['pc_number'] == 'PC-05' and c['lab_name'] == 'Computer Lab 1 (Main Lab)')
assert pc05_working['status'] == 'Working', f"Expected Working, got {pc05_working['status']}"
print(f"✓ Workstation PC-05 status successfully restored to: {pc05_working['status']}")

print("\n=== 6. TEST NAME & GENDER RULE ===")
# 6a: Create unassigned ID with no name -> gender must be None
res_no_name = post('/api/users/create', {
    "name": "",
    "username": "GS_role_unassigned_test",
    "password": "Greenland@2026",
    "email": "test_role@greenlandschool.net",
    "user_type": "teacher",
    "gender": "Male"  # Must be ignored or set to NULL
})
print("Create unassigned ID:", res_no_name['message'])
all_u = get('/api/users')
u_unassigned = next(u for u in all_u if u['username'] == 'GS_role_unassigned_test')
assert u_unassigned['gender'] is None or u_unassigned['gender'] == '', f"Expected NULL gender for unassigned name, got {u_unassigned['gender']}"
print(f"✓ Unassigned ID Name: '{u_unassigned['name']}', Gender: '{u_unassigned['gender']}' (Successfully enforced as NULL / No Gender)")

# 6b: Create ID with person name -> gender is preserved
res_named = post('/api/users/create', {
    "name": "Priya Sharma",
    "username": "GS_teacher_priya",
    "password": "Greenland@2026",
    "email": "priya.sharma@greenlandschool.net",
    "user_type": "teacher",
    "gender": "Female"
})
print("Create named person ID:", res_named['message'])
all_u2 = get('/api/users')
u_priya = next(u for u in all_u2 if u['username'] == 'GS_teacher_priya')
assert u_priya['gender'] == 'Female', f"Expected Female, got {u_priya['gender']}"
print(f"✓ Named ID Name: '{u_priya['name']}', Gender: '{u_priya['gender']}' (Successfully preserved assigned person's gender)")

print("\n=== 7. TEST DIRECTOR SANCTIONING ACCOUNTANT SALARY PAYSLIP ===")
acc_slip_res = post('/api/payroll/generate_accountant', {
    "month": 11,
    "year": 2026,
    "base_salary": 56000.0,
    "special_bonus": 6000.0,
    "bonus_title": "Director Executive Performance Bonus",
    "director_name": "Owner (Director) Rajeev Sinha"
})
print(f"✓ Accountant Slip Sanction: {acc_slip_res['message']}")
slip_data = acc_slip_res['slip']
print(f"  Slip #{slip_data['slip_no']}: Gross: ₹{slip_data['gross_salary']}, Bonus: ₹{slip_data['special_bonus']}, Net: ₹{slip_data['net_salary']}, Status: {slip_data['status']}")
assert slip_data['status'] == 'Sanctioned by Director'
assert slip_data['special_bonus'] == 6000.0

# Verify Accountant endpoint retrieves it
acc_fetch = get('/api/payroll/accountant_slip?month=11&year=2026')
assert acc_fetch['success'] is True and acc_fetch['slip'] is not None
print(f"✓ Accountant successfully retrieved Director-sanctioned slip: {acc_fetch['slip']['slip_no']}")

print("\n=== 8. TEST CLEAN TEST DATA PRESERVING OWNER, IT SUPPORT & MANUAL USER DATA ===")
# Ensure manual user data (e.g. Virat Singh or manual inquiry) exists or is added
post('/api/inquiries/submit', {
    "student_name": "Virat Singh Manual Admission",
    "grade_level": "Grade 11",
    "parent_name": "Virat Singh",
    "parent_email": "vs0839265@gmail.com",
    "parent_phone": "+91 9876543210",
    "address": "Jabalpur",
    "previous_school": "Model School"
})
clean_res = post('/api/system/clean_test_data', {"requested_by": "Owner(Directer)"})
print(f"✓ Clean Test Data result: {clean_res['message']}")

users_after = get('/api/users')
usernames = [u['username'] for u in users_after]
assert 'Owner(Directer)' in usernames, "Owner(Directer) was deleted!"
assert 'GS_itsupport' in usernames, "GS_itsupport was deleted!"
print(f"✓ Confirmed core leadership accounts preserved: 'Owner(Directer)' and 'GS_itsupport'")

# Verify manual inquiry for Virat Singh was preserved
inquiries = get('/api/inquiries')
virat_inq = any('Virat' in inq.get('parent_name', '') or 'Virat' in inq.get('student_name', '') or 'vs0839265' in inq.get('parent_email', '') for inq in inquiries)
assert virat_inq is True, "Manual data for Virat Singh was not preserved!"
print(f"✓ Confirmed manual user data for Virat Singh was preserved!")

print("\n=======================================================")
print(" ALL 8 NEW REQUIREMENTS FULLY VERIFIED AND PASSING! 🎉")
print("=======================================================")
