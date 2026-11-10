import urllib.request
import json
import sqlite3

# Clean up any previous test accounts in DB
conn = sqlite3.connect('school_website/school.db')
cur = conn.cursor()
cur.execute("DELETE FROM users WHERE username IN ('GS_lab1_fleet', 'GS_lab2_fleet')")
cur.execute("DELETE FROM credential_requests WHERE proposed_username IN ('GS_lab1_fleet', 'GS_lab2_fleet')")
conn.commit()
conn.close()

base_url = 'http://127.0.0.1:5000'

def req(path, method='GET', data=None):
    url = base_url + path
    headers = {'Content-Type': 'application/json'}
    body = json.dumps(data).encode('utf-8') if data else None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(r, timeout=10) as resp:
        return json.loads(resp.read().decode('utf-8'))

# 1. Fetch current users to find Computer Teacher GS_teacher
users = req('/api/users')
teacher = next((u for u in users if u['username'] == 'GS_teacher'), None)
assert teacher is not None, "GS_teacher must exist"
print(f"Found Teacher: ID={teacher['id']}, Name={teacher['name']}, Username={teacher['username']}")

# 2. Test Direct Creation of Common ID (e.g. by Director or IT Admin)
lab1_payload = {
    'username': 'GS_lab1_fleet',
    'password': 'Greenland@2026',
    'role': 'common_id',
    'user_type': 'common_id',
    'name': 'Computer Lab 1 Workstation Fleet',
    'is_common_id': 1,
    'common_id_name': 'Computer Lab 1 Fleet (Common ID)',
    'admin_user_id': teacher['id'],
    'admin_username': teacher['username'],
    'admin_name': teacher['name'],
    'assigned_lab_fleet': 'lab1',
    'caller_username': 'GS_itsupport',
    'caller_id': 2
}
create_res = req('/api/users/create', method='POST', data=lab1_payload)
print("Create Common ID response:", create_res)
assert create_res.get('success') is True, f"Failed to create common ID: {create_res}"
assert create_res.get('is_common_id') == 1, "Should be flagged is_common_id=1"
assert create_res.get('has_mail_services') == 0, "Common ID should have 0 mail services"
assert create_res.get('admin_username') == 'GS_teacher', "Admin should be GS_teacher"

# 3. Verify in /api/users
updated_users = req('/api/users')
lab1_user = next((u for u in updated_users if u['username'] == 'GS_lab1_fleet'), None)
assert lab1_user is not None, "GS_lab1_fleet should exist in /api/users"
print(f"Verified Lab 1 User: ID={lab1_user['id']}, Role={lab1_user['user_type']}, Admin={lab1_user['admin_username']} ({lab1_user['admin_name']}), Mail={lab1_user['has_mail_services']}")
assert lab1_user['is_common_id'] == 1, "is_common_id must be 1"
assert lab1_user['admin_username'] == 'GS_teacher', "admin_username must be GS_teacher"
assert lab1_user['has_mail_services'] == 0, "has_mail_services must be 0"

# 4. Verify Lab 1 Computers have assigned teacher / admin GS_teacher
comps = req('/api/lab/computers')
lab1_pcs = [c for c in comps.get('computers', []) if 'Lab 1' in c['lab_name']]
print(f"Total Lab 1 PCs: {len(lab1_pcs)}")
for pc in lab1_pcs[:3]:
    print(f"  {pc['pc_number']}: Assigned Teacher={pc.get('assigned_teacher_username')}, Admin={pc.get('admin_username')}")
assert all(pc.get('assigned_teacher_username') == 'GS_teacher' for pc in lab1_pcs), "Lab 1 PCs must be assigned to GS_teacher"

# 5. Test IT Support Proposal for Lab 2 Common ID with Admin Computer Teacher
it_propose_payload = {
    'username': 'GS_lab2_fleet',
    'password': 'Greenland@2026',
    'user_type': 'common_id',
    'name': 'Computer Lab 2 Senior Workstation Fleet',
    'is_common_id': 1,
    'common_id_name': 'Computer Lab 2 Fleet (Common ID)',
    'admin_user_id': teacher['id'],
    'admin_username': teacher['username'],
    'admin_name': teacher['name'],
    'assigned_lab_fleet': 'lab2',
    'reason': 'Shared lab account for senior computer lab with Computer Teacher as Admin',
    'requested_by_username': 'GS_itsupport',
    'requested_by_name': 'IT Support Administrator'
}
it_res = req('/api/credentials/request_create', method='POST', data=it_propose_payload)
print("IT Support Propose Common ID response:", it_res)
assert it_res.get('success') is True, f"Failed to propose user ID: {it_res}"

# 6. Approve the request via /api/credentials/approve
req_list = req('/api/credentials/requests')
pending_lab2 = next((r for r in req_list.get('requests', []) if r['proposed_username'] == 'GS_lab2_fleet' and r['status'] == 'Pending Owner Approval'), None)
assert pending_lab2 is not None, "Pending request for GS_lab2_fleet must exist"
print(f"Found Pending Request #{pending_lab2['id']} for GS_lab2_fleet")

approve_res = req('/api/credentials/approve', method='POST', data={
    'request_id': pending_lab2['id'],
    'name': 'Owner (Director) Rajeev Sinha'
})
print("Approve response:", approve_res)
assert approve_res.get('success') is True, f"Failed to approve request: {approve_res}"

# 7. Verify GS_lab2_fleet was created and activated with admin GS_teacher
users_after_approval = req('/api/users')
lab2_user = next((u for u in users_after_approval if u['username'] == 'GS_lab2_fleet'), None)
assert lab2_user is not None, "GS_lab2_fleet must exist after Director approval"
print(f"Verified Lab 2 User: ID={lab2_user['id']}, Admin={lab2_user['admin_username']}, Mail={lab2_user['has_mail_services']}")
assert lab2_user['is_common_id'] == 1
assert lab2_user['admin_username'] == 'GS_teacher'
assert lab2_user['has_mail_services'] == 0

# 8. Test Excel export
excel_url = base_url + '/api/it/export_credentials_excel'
with urllib.request.urlopen(excel_url, timeout=10) as resp:
    assert resp.status == 200, "Excel export must return 200 OK"
    content = resp.read()
    assert len(content) > 1000, "Excel export should contain data"
    print(f"Verified Excel credentials export: {len(content)} bytes received")

print("\nALL COMMON ID & ADMIN VERIFICATION TESTS PASSED SUCCESSFULLY! 🚀")
