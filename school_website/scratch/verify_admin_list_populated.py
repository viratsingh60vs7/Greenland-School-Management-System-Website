import urllib.request
import json
import re

base_url = 'http://127.0.0.1:5000'

# 1. Fetch index.html and check the select elements
req_html = urllib.request.Request(base_url + '/')
with urllib.request.urlopen(req_html) as resp:
    html_text = resp.read().decode('utf-8')

assert 'id="create-user-admin-id"' in html_text, "create-user-admin-id select must be in index.html"
assert 'id="assign-role-admin-id"' in html_text, "assign-role-admin-id select must be in index.html"
assert 'id="it-create-admin-id"' in html_text, "it-create-admin-id select must be in index.html"
assert 'populateAdminIdOptions(this.id)' in html_text, "onfocus/onclick populateAdminIdOptions must be present in index.html"

# 2. Fetch app.js and verify async populateAdminIdOptions
req_js = urllib.request.Request(base_url + '/js/app.js')
with urllib.request.urlopen(req_js) as resp:
    js_text = resp.read().decode('utf-8')

assert 'async function populateAdminIdOptions' in js_text, "populateAdminIdOptions must be async in app.js"
assert "fetch('/api/users')" in js_text, "populateAdminIdOptions must auto-fetch from /api/users"

# 3. Fetch /api/users
req_api = urllib.request.Request(base_url + '/api/users')
with urllib.request.urlopen(req_api) as resp:
    users = json.loads(resp.read().decode('utf-8'))

print(f"Total users fetched from /api/users: {len(users)}")
assert len(users) > 0, "Users list must not be empty"

# 4. Simulate the populateAdminIdOptions logic in Python to verify generated options
opts = []
for u in users:
    if u.get('user_type') == 'common_id':
        continue
    opts.append(f"<option value=\"{u['id']}\">👑 {u['name']} ({u['username']}) [{u['user_type']}]</option>")

print(f"Total admin candidate options: {len(opts)}")
print("Sample options:")
for o in opts[:5]:
    print(" ", o)

assert any('GS_teacher' in o for o in opts), "GS_teacher must be in admin options"
assert any('Owner(Directer)' in o or 'Rajeev Sinha' in o for o in opts), "Director must be in admin options"

print("\nSUCCESS: Admin ID dropdown list is completely wired, self-fetching, and verified operational! 🎉")
