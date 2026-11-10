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

print("Testing GET /api/login_directory...")
code, data = req('GET', '/api/login_directory')
print("Status:", code)
print("Users in directory:", len(data.get('users', [])))
for u in data.get('users', []):
    print(f" - {u['username']} ({u['user_type']}): clickable={u['is_clickable']}")

# Test create new teacher
print("\nTesting creating a new teacher...")
code, create_res = req('POST', '/api/users/create', {
    "caller_username": "Owner(Directer)",
    "new_username": "Teacher_Priya",
    "role": "teacher",
    "name": "Priya Sharma",
    "email": "priya.sharma@greenlandschool.net"
})
print("Create teacher status:", code, create_res)

# Verify new teacher is now in login directory and clickable!
code, data = req('GET', '/api/login_directory')
priya = next((u for u in data.get('users', []) if u['username'] == 'Teacher_Priya'), None)
print("Priya in directory:", bool(priya))
if priya:
    print(f"Priya clickable: {priya['is_clickable']} (Expected: True)")

# Test create non-teacher (accountant)
print("\nTesting creating a new accountant...")
code, create_res2 = req('POST', '/api/users/create', {
    "caller_username": "Owner(Directer)",
    "new_username": "Accountant_Ramesh",
    "role": "accountant",
    "name": "Ramesh Gupta",
    "email": "ramesh.gupta@greenlandschool.net"
})
print("Create accountant status:", code, create_res2)

# Verify accountant is in login directory and NOT clickable!
code, data = req('GET', '/api/login_directory')
ramesh = next((u for u in data.get('users', []) if u['username'] == 'Accountant_Ramesh'), None)
print("Ramesh in directory:", bool(ramesh))
if ramesh:
    print(f"Ramesh clickable: {ramesh['is_clickable']} (Expected: False - ONLY TEACHER CAN CLICK)")

# Test delete Priya
print("\nTesting deleting Teacher_Priya...")
code, del_res = req('POST', '/api/users/delete', {"username": "Teacher_Priya"})
print("Delete status:", code, del_res)

# Verify Priya is no longer in login directory!
code, data = req('GET', '/api/login_directory')
priya_after = next((u for u in data.get('users', []) if u['username'] == 'Teacher_Priya'), None)
print("Priya in directory after delete:", bool(priya_after), "(Expected: False)")

# Clean up Ramesh
req('POST', '/api/users/delete', {"username": "Accountant_Ramesh"})
print("Cleaned up Ramesh.")
