# ==============================================================================
# 1. Update index.html
# ==============================================================================
with open('school_website/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html_norm = html.replace('\r\n', '\n')

old_lbl1 = '<label class="form-label">👑 Assigned Admin / In-Charge ID for this Common ID *</label>'
new_lbl1 = '<label class="form-label">👑 Assigned Admin / In-Charge ID for this Common ID * <small style="font-weight:600; color:#dc2626;">(Staff & Faculty only; Students & Parents ineligible)</small></label>'

old_lbl2 = '<label class="form-label">👑 Assigned Admin / In-Charge ID</label>'
new_lbl2 = '<label class="form-label">👑 Assigned Admin / In-Charge ID <small style="font-weight:600; color:#dc2626;">(Staff & Faculty only; Students & Parents ineligible)</small></label>'

old_opt = '<option value="">— Select Admin ID (e.g. Computer Teacher GS_teacher) —</option>'
new_opt = '<option value="">— Select Staff/Teacher Admin (Students & Parents ineligible) —</option>'

if old_lbl1 in html_norm:
    html_norm = html_norm.replace(old_lbl1, new_lbl1)
    print("Updated labels in index.html")

if old_lbl2 in html_norm:
    html_norm = html_norm.replace(old_lbl2, new_lbl2)

if old_opt in html_norm:
    html_norm = html_norm.replace(old_opt, new_opt)

# Bump cache buster in index.html
html_norm = html_norm.replace('js/app.js?v=20261109_common_id', 'js/app.js?v=20261109_common_id_no_student')

with open('school_website/index.html', 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(html_norm)
print("Saved patched index.html")

# ==============================================================================
# 2. Update server.py
# ==============================================================================
with open('school_website/server.py', 'r', encoding='utf-8') as f:
    server_code = f.read()

server_norm = server_code.replace('\r\n', '\n')

# Patch in /api/users/create
old_create_admin = """                if admin_user_id or admin_username:
                    cur.execute("SELECT id, username, name FROM users WHERE id = ? OR username = ?", (admin_user_id, admin_username))
                    adm_row = cur.fetchone()
                    if adm_row:
                        admin_user_id = adm_row['id']
                        admin_username = adm_row['username']
                        admin_name = adm_row['name'] or adm_row['username']"""

new_create_admin = """                if admin_user_id or admin_username:
                    cur.execute("SELECT id, username, name, user_type FROM users WHERE id = ? OR username = ?", (admin_user_id, admin_username))
                    adm_row = cur.fetchone()
                    if adm_row:
                        if adm_row['user_type'] in ('student', 'parent', 'common_id'):
                            # Policy Rule: Students and Parents cannot be Admin for Common IDs
                            admin_user_id = None
                            admin_username = None
                            admin_name = None
                        else:
                            admin_user_id = adm_row['id']
                            admin_username = adm_row['username']
                            admin_name = adm_row['name'] or adm_row['username']"""

if old_create_admin in server_norm:
    server_norm = server_norm.replace(old_create_admin, new_create_admin)
    print("Updated /api/users/create admin check in server.py")

# Patch in /api/users/assign_role
old_assign_admin = """                if admin_user_id or admin_username:
                    cur.execute("SELECT id, username, name FROM users WHERE id = ? OR username = ?", (admin_user_id, admin_username))
                    adm_row = cur.fetchone()
                    if adm_row:
                        admin_user_id = adm_row['id']
                        admin_username = adm_row['username']
                        admin_name = adm_row['name'] or adm_row['username']"""

# Replace all occurrences in server_norm
server_norm = server_norm.replace(old_create_admin, new_create_admin)

# Patch in /api/credentials/approve
old_approve_admin_chk = """                elif req['request_type'] == 'create_user':
                    is_c = req['is_common_id'] or (1 if req['proposed_role'] == 'common_id' else 0)
                    c_name = req['common_id_name']
                    adm_uid = req['admin_user_id']
                    adm_uname = req['admin_username']
                    adm_name = req['admin_name']
                    a_fleet = (req['assigned_lab_fleet'] or '').lower()"""

new_approve_admin_chk = """                elif req['request_type'] == 'create_user':
                    is_c = req['is_common_id'] or (1 if req['proposed_role'] == 'common_id' else 0)
                    c_name = req['common_id_name']
                    adm_uid = req['admin_user_id']
                    adm_uname = req['admin_username']
                    adm_name = req['admin_name']
                    a_fleet = (req['assigned_lab_fleet'] or '').lower()

                    if adm_uid or adm_uname:
                        cur.execute("SELECT user_type FROM users WHERE id = ? OR username = ?", (adm_uid, adm_uname))
                        chk_adm = cur.fetchone()
                        if chk_adm and chk_adm['user_type'] in ('student', 'parent', 'common_id'):
                            adm_uid = None
                            adm_uname = None
                            adm_name = None"""

if old_approve_admin_chk in server_norm:
    server_norm = server_norm.replace(old_approve_admin_chk, new_approve_admin_chk)
    print("Updated /api/credentials/approve in server.py")

with open('school_website/server.py', 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(server_norm)
print("Saved patched server.py")

# ==============================================================================
# 3. Update app.js
# ==============================================================================
with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

app_norm = app_js.replace('\r\n', '\n')

old_loop = """    sorted.forEach(u => {
        if (u.user_type === 'common_id' && (!selectedId || (String(u.id) !== String(selectedId) && String(u.username) !== String(selectedId)))) {
            return;
        }"""

new_loop = """    sorted.forEach(u => {
        // STRICT INSTITUTIONAL POLICY: Students and Parents cannot be assigned as Admin for a Common ID
        // (even if an Admin or Owner assigned a person name to that student/parent ID).
        // Only Faculty/Teachers, IT Support, Principal/Admin, Director/Owner, Accountant, and Librarian are permitted.
        if (['student', 'parent', 'common_id'].includes(u.user_type)) {
            return;
        }"""

if old_loop in app_norm:
    app_norm = app_norm.replace(old_loop, new_loop)
    print("Updated sorted.forEach filtering in populateAdminIdOptions in app.js")

old_ph = """let opts = '<option value="">— Select Admin / Manager for this Common ID —</option>';"""
new_ph = """let opts = '<option value="">— Select Staff/Teacher Admin (Students & Parents ineligible) —</option>';"""
if old_ph in app_norm:
    app_norm = app_norm.replace(old_ph, new_ph)

with open('school_website/js/app.js', 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(app_norm)
print("Saved patched app.js")
