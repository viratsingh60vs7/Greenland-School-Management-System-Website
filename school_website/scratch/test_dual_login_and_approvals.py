import sys, os, json
from io import BytesIO
sys.path.insert(0, os.path.abspath('school_website'))
from server import SchoolHandler

class DummyServer:
    server_name = "localhost"
    server_port = 5000

class MockSocket:
    def __init__(self, data):
        self.rfile = BytesIO(data)
        self.wfile = BytesIO()
    def makefile(self, mode, *a, **k):
        return self.rfile if 'r' in mode else self.wfile
    def sendall(self, d):
        self.wfile.write(d)

def req(method, path, body=None):
    b = json.dumps(body).encode('utf-8') if body else b""
    h = f"{method} {path} HTTP/1.1\r\nHost: localhost:5000\r\n"
    if b: h += f"Content-Type: application/json\r\nContent-Length: {len(b)}\r\n"
    h += "\r\n"
    sock = MockSocket(h.encode('utf-8') + b)
    class TH(SchoolHandler):
        def __init__(self, s, c, srv):
            self.request, self.client_address, self.server = s, c, srv
            self.setup(); self.handle(); self.finish()
    try: TH(sock, ('127.0.0.1', 5000), DummyServer())
    except: pass
    raw = sock.wfile.getvalue().decode('utf-8', errors='ignore')
    parts = raw.split('\r\n\r\n', 1)
    code = int(parts[0].split('\r\n')[0].split()[1]) if parts and len(parts[0].split('\r\n')[0].split()) > 1 else 0
    try: js = json.loads(parts[1])
    except: js = parts[1] if len(parts) > 1 else ""
    return code, js

print("="*65)
print("TESTING DUAL LOGIN (PHONE NUMBER & USER ID) & DIRECTOR APPROVALS")
print("="*65)

passed = 0
failed = 0

def check(name, cond, details=""):
    global passed, failed
    if cond:
        print(f" [PASS] {name}")
        passed += 1
    else:
        print(f"![FAIL] {name} - {details}")
        failed += 1

# 1. Student Login via Phone Number
code, res = req('POST', '/api/login', {"username": "8004125223", "password": "Viratsingh@2004"})
check("Student logs in using Phone Number (8004125223)", code == 200 and res.get('success') is True and res.get('user', {}).get('username') == 'Viratsingh60vs7', f"res: {res}")
virat_id = res.get('user', {}).get('id')

# 2. Student Login via User ID
code, res = req('POST', '/api/login', {"username": "Viratsingh60vs7", "password": "Viratsingh@2004"})
check("Student logs in using User ID (Viratsingh60vs7)", code == 200 and res.get('success') is True)

# 3. Teacher Login via Phone Number
code, res = req('POST', '/api/login', {"username": "9876543210", "password": "Greenland@2026"})
check("Teacher logs in using Phone Number (9876543210)", code == 200 and res.get('success') is True and res.get('user', {}).get('username') == 'GS_teacher')
teacher_id = res.get('user', {}).get('id')

# 4. Teacher Login via User ID
code, res = req('POST', '/api/login', {"username": "GS_teacher", "password": "Greenland@2026"})
check("Teacher logs in using User ID (GS_teacher)", code == 200 and res.get('success') is True)

# 5. Parent Login via Phone Number
code, res = req('POST', '/api/login', {"username": "9812345678", "password": "Greenland@2026"})
check("Parent logs in using Phone Number (9812345678)", code == 200 and res.get('success') is True and res.get('user', {}).get('user_type') == 'parent')
parent_id = res.get('user', {}).get('id')

# 6. Parent Login via User ID
code, res = req('POST', '/api/login', {"username": "GS_parent_Alex_and_Clara", "password": "Greenland@2026"})
check("Parent logs in using User ID (GS_parent_Alex_and_Clara)", code == 200 and res.get('success') is True)

# 7. Student App Dashboard API
code, s_dash = req('GET', f'/api/app/student_dashboard?user_id={virat_id}')
check("Student App Dashboard returns profile, fees, timetable, library booklet", code == 200 and 'fees' in s_dash and 'issued_books' in s_dash and 'timetable' in s_dash)

# 8. Parent App Dashboard API (Multi-child access)
code, p_dash = req('GET', f'/api/app/parent_dashboard?user_id={parent_id}')
check("Parent App Dashboard returns multi-child list", code == 200 and len(p_dash.get('children', [])) >= 1)

# 9. Teacher App Dashboard API
code, t_dash = req('GET', f'/api/app/teacher_dashboard?user_id={teacher_id}')
check("Teacher App Dashboard returns leaves, complaints, classes", code == 200 and 'leaves' in t_dash and 'lab_complaints' in t_dash)

# 10. IT Request Creation
code, it_req = req('POST', '/api/it_requests/create', {
    "request_type": "Equipment Procurement",
    "title": "5x Dell Latitude Laptops for Computer Lab Upgrade",
    "description": "Required for higher secondary AI curriculum.",
    "estimated_cost": 325000,
    "requested_by": "IT Support Administrator"
})
check("IT Team creates procurement request pending Director approval", code == 200 and it_req.get('success') is True)
req_id = it_req.get('request_id')

# 11. Director Unified Approvals Desk
code, p_reqs = req('GET', '/api/director/pending_requests')
check("Director can see all pending requests from Teachers and IT Team", code == 200 and p_reqs.get('total_pending', 0) >= 1)

# 12. Non-Director attempts approval -> Rejected
code, rej = req('POST', '/api/director/approve_request', {
    "origin": "it_asset",
    "request_id": req_id,
    "action": "approve",
    "caller_username": "GS_admin",
    "caller_role": "admin"
})
check("Principal (admin) CANNOT approve IT/Teacher request (rejected with 403)", code == 403)

# 13. Director approves request -> Success!
code, app_res = req('POST', '/api/director/approve_request', {
    "origin": "it_asset",
    "request_id": req_id,
    "action": "approve",
    "caller_username": "Owner(Directer)",
    "caller_role": "super_admin",
    "notes": "Approved for lab procurement by Director Rajeev Sinha"
})
check("Director (Owner) successfully approves IT/Teacher request", code == 200 and app_res.get('success') is True)

print("="*65)
print(f"VERIFICATION SUMMARY: {passed} PASSED, {failed} FAILED")
print("="*65)
