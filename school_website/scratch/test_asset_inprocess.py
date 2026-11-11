import sys
import os
import json
import time
from io import BytesIO

sys.path.insert(0, os.path.abspath('school_website'))
import server
from server import SchoolHandler

class DummyServer:
    def __init__(self):
        self.server_name = "localhost"
        self.server_port = 5000

class MockSocket:
    def __init__(self, request_bytes):
        self.rfile = BytesIO(request_bytes)
        self.wfile = BytesIO()

    def makefile(self, mode, *args, **kwargs):
        if 'r' in mode:
            return self.rfile
        return self.wfile

    def sendall(self, data):
        self.wfile.write(data)

def invoke_handler(method, path, body=None):
    if body is not None and not isinstance(body, bytes):
        body = json.dumps(body).encode('utf-8')
    
    headers = f"{method} {path} HTTP/1.1\r\nHost: localhost:5000\r\n"
    if body:
        headers += f"Content-Type: application/json\r\nContent-Length: {len(body)}\r\n"
    headers += "\r\n"
    req_bytes = headers.encode('utf-8') + (body or b"")

    mock_sock = MockSocket(req_bytes)
    
    class TestHandler(SchoolHandler):
        def __init__(self, request, client_address, srv):
            self.request = request
            self.client_address = client_address
            self.server = srv
            self.setup()
            try:
                self.handle()
            finally:
                self.finish()

    try:
        h = TestHandler(mock_sock, ('127.0.0.1', 54321), DummyServer())
    except Exception as e:
        pass

    raw_response = mock_sock.wfile.getvalue().decode('utf-8', errors='ignore')
    parts = raw_response.split('\r\n\r\n', 1)
    status_line = parts[0].split('\r\n')[0] if parts else ""
    code = int(status_line.split()[1]) if len(status_line.split()) > 1 else 0
    resp_body = parts[1] if len(parts) > 1 else ""
    try:
        parsed_json = json.loads(resp_body)
    except:
        parsed_json = resp_body
    return code, parsed_json

print("="*60)
print("RUNNING IN-PROCESS E2E VERIFICATION FOR IT ASSET MANAGEMENT")
print("="*60)

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

ts = int(time.time())

# 1. Test GET /api/it_assets
code, data = invoke_handler('GET', '/api/it_assets')
check("GET /api/it_assets responds with 200", code == 200)
check("Asset inventory contains seeded units", len(data.get('assets', [])) >= 8)
check("Asset inventory metrics returned", data.get('summary', {}).get('total', 0) >= 8)

# 2. Test POST /api/it_assets/create
new_asset = {
    "asset_tag": f"E2E-LAP-{ts}",
    "serial_number": f"SN-E2E-{ts}",
    "device_name": "Asus ExpertBook B9450",
    "device_type": "laptop",
    "brand": "Asus",
    "model": "ExpertBook B9",
    "processor": "Intel Core i7-1255U",
    "ram": "16 GB LPDDR5",
    "storage": "1 TB NVMe SSD",
    "os": "Windows 11 Pro",
    "mac_address": "E4:54:E8:A1:B2:C3",
    "ip_address": "192.168.1.155",
    "ownership": "School Owned",
    "procurement_date": "2026-04-01",
    "purchase_cost": 88000,
    "current_value": 88000,
    "vendor_name": "Asus Commercial India",
    "location": "IT Support Depot",
    "department": "IT Support",
    "physical_condition": "Brand New",
    "status": "In Stock / Available",
    "notes": "Live E2E Verification Asset"
}
code, res = invoke_handler('POST', '/api/it_assets/create', new_asset)
check("POST /api/it_assets/create succeeds", code == 200 and isinstance(res, dict) and res.get('success') is True, f"Code: {code}, res: {res}")
asset_id = res.get('asset_id') if isinstance(res, dict) else None

# 3. Test GET /api/it_assets/history
if asset_id:
    code, hist = invoke_handler('GET', f'/api/it_assets/history?asset_id={asset_id}')
    check("GET /api/it_assets/history logs registration", code == 200 and len(hist.get('logs', [])) >= 1)

# 4. Test POST /api/it_allocations/handover
if asset_id:
    handover = {
        "asset_id": asset_id,
        "employee_id": 2,
        "employee_name": "Director Rajeev Sinha",
        "employee_role": "Director & Head Administrator",
        "department": "Executive Management",
        "handover_date": "2026-11-06",
        "expected_return_date": "2027-11-06",
        "accessories": "Power adapter, USB-C Dock, Carry case",
        "initial_condition": "Brand New",
        "allocated_by": "IT Support Admin",
        "remarks": "Assigned for campus inspection"
    }
    code, h_res = invoke_handler('POST', '/api/it_allocations/handover', handover)
    check("POST /api/it_allocations/handover issues slip", code == 200 and h_res.get('success') is True, f"res: {h_res}")
    alloc_id = h_res.get('allocation_id')
    slip_no = h_res.get('handover_slip_no')
    check("Handover slip number generated", bool(slip_no))

    # Check asset transitioned
    code, data = invoke_handler('GET', '/api/it_assets')
    curr = next((a for a in data.get('assets', []) if a['id'] == asset_id), None)
    check("Asset status transitioned to 'Allocated to Employee'", curr and curr['status'] == 'Allocated to Employee')

    # 5. Test POST /api/it_allocations/return
    ret_data = {
        "allocation_id": alloc_id,
        "return_date": "2026-11-06",
        "return_condition": "Like New",
        "received_by": "IT Support Admin",
        "return_remarks": "Returned in immaculate state"
    }
    code, r_res = invoke_handler('POST', '/api/it_allocations/return', ret_data)
    check("POST /api/it_allocations/return checks asset back into depot", code == 200 and r_res.get('success') is True, f"res: {r_res}")

    # Check asset returned to available
    code, data = invoke_handler('GET', '/api/it_assets')
    curr = next((a for a in data.get('assets', []) if a['id'] == asset_id), None)
    check("Asset status returned to 'In Stock / Available'", curr and curr['status'] == 'In Stock / Available')

# 6. Test Rental Agreement
rental = {
    "vendor_name": f"Acer Lease Infrastructure {ts}",
    "contact_person": "Sunil Sharma",
    "phone": "+91 98111 22334",
    "email": "leasing@acer-in.com",
    "agreement_no": f"RNT-ACER-{ts}",
    "start_date": "2026-11-01",
    "end_date": "2027-10-31",
    "monthly_cost": 30000,
    "security_deposit": 60000,
    "units_count": 6,
    "terms": "Includes preventive maintenance quarterly",
    "status": "Active"
}
code, rent_res = invoke_handler('POST', '/api/it_rentals/create', rental)
check("POST /api/it_rentals/create registers agreement", code == 200 and rent_res.get('success') is True, f"res: {rent_res}")
rental_id = rent_res.get('rental_id')

code, rdata = invoke_handler('GET', '/api/it_rentals')
check("GET /api/it_rentals lists active agreements", code == 200 and len(rdata.get('rentals', [])) >= 2)

# 7. Test Warranty & Claim
if asset_id:
    warranty = {
        "asset_id": asset_id,
        "warranty_type": "Comprehensive Care Pack",
        "provider": "Asus Support Direct",
        "policy_no": f"WAR-ASUS-{ts}",
        "start_date": "2026-04-01",
        "end_date": "2029-04-01",
        "support_contact": "+91 1800 209 0365",
        "cost": 8500,
        "sla": "4-Hour Onsite Response",
        "status": "Active"
    }
    code, w_res = invoke_handler('POST', '/api/it_warranties/create', warranty)
    check("POST /api/it_warranties/create logs policy", code == 200 and w_res.get('success') is True, f"res: {w_res}")
    wid = w_res.get('warranty_id')

    claim = {
        "warranty_id": wid,
        "issue_description": "Display hinge adjustment check",
        "resolution_notes": "Claim raised with Asus Care"
    }
    code, c_res = invoke_handler('POST', '/api/it_warranties/claim', claim)
    check("POST /api/it_warranties/claim files ticket", code == 200 and c_res.get('success') is True)

    code, warr_list = invoke_handler('GET', '/api/it_warranties')
    check("GET /api/it_warranties returns policies with live remaining days", code == 200 and len(warr_list.get('warranties', [])) >= 1)

# 8. Test Maintenance & Service
if asset_id:
    maint = {
        "asset_id": asset_id,
        "service_type": "Hardware Diagnostics",
        "vendor_name": "CompServe Care Center",
        "technician_name": "Manoj Kumar",
        "technician_contact": "+91 97766 55443",
        "issue_description": "RAM and SSD stress test benchmark",
        "estimated_cost": 1200,
        "start_date": "2026-11-06",
        "priority": "Low",
        "reported_by": "IT Support Admin"
    }
    code, m_res = invoke_handler('POST', '/api/it_maintenance/create', maint)
    check("POST /api/it_maintenance/create dispatches service ticket", code == 200 and m_res.get('success') is True, f"res: {m_res}")
    ticket_id = m_res.get('ticket_id')

    comp = {
        "ticket_id": ticket_id,
        "completion_date": "2026-11-06",
        "repair_cost": 1200,
        "parts_replaced": "None",
        "remarks": "Diagnostics clean. Passed 100% memory and SMART drive tests.",
        "return_location": "IT Support Depot"
    }
    code, mc_res = invoke_handler('POST', '/api/it_maintenance/complete', comp)
    check("POST /api/it_maintenance/complete closes ticket and restores asset", code == 200 and mc_res.get('success') is True, f"res: {mc_res}")

# 9. Test Payment Reminder & Recording
pmt = {
    "payment_category": "Rental Invoice",
    "vendor_name": "Acer Lease Infrastructure",
    "notes": "Monthly Fleet Rental Invoice - Nov 2026",
    "due_date": "2026-11-25",
    "amount": 30000,
    "related_rental_id": rental_id
}
code, p_res = invoke_handler('POST', '/api/it_payments/create', pmt)
check("POST /api/it_payments/create schedules reminder", code == 200 and p_res.get('success') is True, f"res: {p_res}")
pmt_id = p_res.get('payment_id')

rem = {"payment_id": pmt_id, "recipient": "bursar@greensprings.edu"}
code, rem_res = invoke_handler('POST', '/api/it_payments/send_reminder', rem)
check("POST /api/it_payments/send_reminder sends notification", code == 200 and rem_res.get('success') is True, f"res: {rem_res}")

rec = {
    "payment_id": pmt_id,
    "paid_date": "2026-11-06",
    "paid_amount": 30000,
    "payment_method": "Direct Bank NEFT / RTGS",
    "transaction_ref": "NEFT-SBI-4433221",
    "remarks": "Processed by Accountant Jude Bello"
}
code, rec_res = invoke_handler('POST', '/api/it_payments/record', rec)
check("POST /api/it_payments/record registers payment settlement", code == 200 and rec_res.get('success') is True, f"res: {rec_res}")

# 10. Test Analytics
code, an_data = invoke_handler('GET', '/api/it_assets/analytics')
check("GET /api/it_assets/analytics returns dashboard metrics", code == 200 and 'metrics' in an_data and 'recent_logs' in an_data)

# Clean up
if asset_id:
    invoke_handler('POST', '/api/it_assets/delete', {"asset_id": asset_id})

print("="*60)
print(f"IN-PROCESS E2E TEST SUMMARY: {passed} PASSED, {failed} FAILED")
print("="*60)
