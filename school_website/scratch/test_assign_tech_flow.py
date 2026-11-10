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

# Test 1: Verify lab computers count
comps = req('/api/lab/computers')
computers = comps.get('computers', [])
print(f'Total lab computers in database: {len(computers)}')
assert len(computers) == 100, f'Expected 100 lab computers, got {len(computers)}'

# Test 2: Call assign endpoint directly for PC-04 with no ticket
assign_res = req('/api/lab/complaints/assign', method='POST', data={
    'complaint_id': 0,
    'pc_number': 'PC-04',
    'computer_id': 4,
    'assigned_to_name': 'Ramesh Kumar (Hardware Tech)',
    'technician_notes': 'Auto test repair assignment verification',
    'username': 'GS_itsupport'
})
print('Assign result:', assign_res)
assert assign_res.get('success') is True, 'Assign request should succeed'

# Test 3: Verify PC-04 status is now 'In Repair'
comps_after = req('/api/lab/computers')
pc4 = next((c for c in comps_after.get('computers', []) if c['pc_number'] == 'PC-04'), None)
print(f'PC-04 status after assign: {pc4.get("status")} | active_complaint_id: {pc4.get("active_complaint_id")}')
assert pc4.get('status') == 'In Repair', 'PC-04 should be In Repair'

# Test 4: Resolve complaint
resolve_res = req('/api/lab/complaints/resolve', method='POST', data={
    'complaint_id': pc4.get('active_complaint_id'),
    'pc_number': 'PC-04',
    'computer_id': 4,
    'resolution_notes': 'Verified operational and restored to lab.',
    'username': 'GS_itsupport'
})
print('Resolve result:', resolve_res)
assert resolve_res.get('success') is True, 'Resolve request should succeed'

comps_resolved = req('/api/lab/computers')
pc4_res = next((c for c in comps_resolved.get('computers', []) if c['pc_number'] == 'PC-04'), None)
print(f'PC-04 status after resolve: {pc4_res.get("status")}')
assert pc4_res.get('status') == 'Working', 'PC-04 should be Working'

# Test 5: Verify alert string does not exist in app.js
with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

assert 'Notice: Ticket for this workstation is being initialized' not in js_content, 'Old alert string still exists in app.js!'
assert 'Notice: No active ticket found to resolve' not in js_content, 'Old resolve alert string still exists in app.js!'

print('\nALL VERIFICATION CHECKS PASSED SUCCESSFULLY!')
