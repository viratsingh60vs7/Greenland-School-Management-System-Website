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
print("E2E VERIFICATION: DYNAMIC LOGIN USER DIRECTORY & ACCESS CONTROL")
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

# 1. Check GET /api/login_directory
code, data = req('GET', '/api/login_directory')
check("GET /api/login_directory responds 200", code == 200)
check("Users returned in directory", 'users' in data and len(data['users']) >= 2)

# Verify foundational accounts are NOT clickable
owner = next((u for u in data['users'] if u['username'] == 'Owner(Directer)'), None)
itsup = next((u for u in data['users'] if u['username'] == 'GS_itsupport'), None)
check("Owner(Directer) is in directory", bool(owner))
check("Owner(Directer) is NOT clickable (only teacher can click)", owner and owner['is_clickable'] is False)
check("GS_itsupport is NOT clickable (only teacher can click)", itsup and itsup['is_clickable'] is False)

# 2. Create new teacher User ID
teacher_uname = "GS_Teacher_Anita"
code, res = req('POST', '/api/users/create', {
    "caller_username": "Owner(Directer)",
    "new_username": teacher_uname,
    "role": "teacher",
    "name": "Anita Roy",
    "email": "anita.roy@greenlandschool.net"
})
check("Create new Teacher User ID succeeds", code == 200 and res.get('success') is True)

# Verify newly created teacher appears in login directory AND is clickable!
code, data = req('GET', '/api/login_directory')
anita = next((u for u in data['users'] if u['username'] == teacher_uname), None)
check("Newly created teacher appears in login directory", bool(anita))
check("Newly created teacher is CLICKABLE (is_clickable = True)", anita and anita['is_clickable'] is True)

# 3. Create new non-teacher User ID (e.g. Accountant)
acc_uname = "GS_Acc_Sanjay"
code, res = req('POST', '/api/users/create', {
    "caller_username": "Owner(Directer)",
    "new_username": acc_uname,
    "role": "accountant",
    "name": "Sanjay Kapoor",
    "email": "sanjay.kapoor@greenlandschool.net"
})
check("Create new Accountant User ID succeeds", code == 200 and res.get('success') is True)

# Verify newly created accountant appears in login directory BUT is NOT clickable!
code, data = req('GET', '/api/login_directory')
sanjay = next((u for u in data['users'] if u['username'] == acc_uname), None)
check("Newly created accountant appears in login directory", bool(sanjay))
check("Newly created accountant is NOT clickable (only teacher can click)", sanjay and sanjay['is_clickable'] is False)

# 4. Delete the Teacher User ID
code, del_res = req('POST', '/api/users/delete', {"username": teacher_uname})
check("Delete User ID succeeds", code == 200 and del_res.get('success') is True)

# Verify deleted teacher is NO LONGER LISTED in login directory
code, data = req('GET', '/api/login_directory')
anita_after = next((u for u in data['users'] if u['username'] == teacher_uname), None)
check("Deleted User ID is NO LONGER listed on login page", anita_after is None)

# Clean up accountant
req('POST', '/api/users/delete', {"username": acc_uname})
code, data = req('GET', '/api/login_directory')
sanjay_after = next((u for u in data['users'] if u['username'] == acc_uname), None)
check("Deleted Accountant is NO LONGER listed on login page", sanjay_after is None)

# 5. Verify protected accounts cannot be deleted
code, del_owner = req('POST', '/api/users/delete', {"username": "Owner(Directer)"})
check("Deleting Owner(Directer) is rejected with 403", code == 403 and del_owner.get('success') is False)

# 6. Verify HTML markup and JS functions exist
with open('school_website/index.html', 'r', encoding='utf-8') as f:
    html = f.read()
check("index.html contains dynamic #login-staff-directory container", 'id="login-staff-directory"' in html)

with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()
check("app.js contains loadLoginDirectory function", 'async function loadLoginDirectory' in js)
check("app.js contains handleNonTeacherClick function", 'function handleNonTeacherClick' in js)
check("app.js contains confirmDeleteUser function", 'async function confirmDeleteUser' in js)

print("="*65)
print(f"VERIFICATION SUMMARY: {passed} PASSED, {failed} FAILED")
print("="*65)
