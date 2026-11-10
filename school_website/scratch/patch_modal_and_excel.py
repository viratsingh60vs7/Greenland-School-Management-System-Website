with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

app_norm = app_js.replace('\r\n', '\n')

old_open_modal = """async function openModal(id) {
    const el = document.getElementById(id);
    if (el) el.style.display = 'flex';"""

new_open_modal = """async function openModal(id) {
    const el = document.getElementById(id);
    if (el) el.style.display = 'flex';

    if (id === 'modal-create-user') {
        populateAdminIdOptions('create-user-admin-id');
    }
    if (id === 'modal-it-request-create-user') {
        populateAdminIdOptions('it-create-admin-id');
    }"""

if old_open_modal in app_norm:
    app_norm = app_norm.replace(old_open_modal, new_open_modal)
    with open('school_website/js/app.js', 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(app_norm)
    print("Updated openModal in app.js to auto-populate admin dropdowns")
else:
    print("old_open_modal not found in app.js!")

with open('school_website/server.py', 'r', encoding='utf-8') as f:
    server_code = f.read()

server_norm = server_code.replace('\r\n', '\n')

old_excel = """                headers = [
                    "S.No", 
                    "User ID (Username)", 
                    "Login Password", 
                    "Full Name", 
                    "Assigned Role", 
                    "Role Key",
                    "Registered Phone (Dual Login)", 
                    "Registered Email", 
                    "Gender", 
                    "Account Created"
                ]"""

new_excel = """                headers = [
                    "S.No", 
                    "User ID (Username)", 
                    "Login Password", 
                    "Full Name", 
                    "Assigned Role", 
                    "Role Key",
                    "Common ID Fleet",
                    "Assigned Admin ID",
                    "Registered Phone (Dual Login)", 
                    "Registered Email", 
                    "Gender", 
                    "Account Created"
                ]"""

if old_excel in server_norm:
    server_norm = server_norm.replace(old_excel, new_excel)
    server_norm = server_norm.replace("ws.merge_cells('A1:J1')", "ws.merge_cells('A1:L1')")
    server_norm = server_norm.replace("ws.merge_cells('A2:J2')", "ws.merge_cells('A2:L2')")
    
    old_excel_sel = """                cur.execute(\"\"\"
                    SELECT id, username, password, name, user_type, phone, email, gender, created_at 
                    FROM users"""
    new_excel_sel = """                cur.execute(\"\"\"
                    SELECT id, username, password, name, user_type, phone, email, gender, created_at,
                           COALESCE(is_common_id, 0) as is_common_id, common_id_name, admin_username, admin_name
                    FROM users"""
    server_norm = server_norm.replace(old_excel_sel, new_excel_sel)

    old_row_data = """                    row_data = [
                        s_no,
                        r['username'],
                        r['password'],
                        user_name,
                        role_title,
                        role_key,
                        r['phone'] or '—',
                        r['email'] or '—',
                        gender,
                        r['created_at'] or '—'
                    ]"""

    new_row_data = """                    is_c = r['is_common_id'] or r['user_type'] == 'common_id'
                    c_fleet = r['common_id_name'] or ('Common ID' if is_c else 'Individual')
                    adm_lbl = f"{r['admin_name']} ({r['admin_username']})" if r['admin_username'] else ('Computer Teacher (Self)' if r['username'] == 'GS_teacher' else '—')
                    mail_lbl = '📭 No Mail Service' if is_c else (r['email'] or '—')

                    row_data = [
                        s_no,
                        r['username'],
                        r['password'],
                        user_name,
                        role_title,
                        role_key,
                        c_fleet,
                        adm_lbl,
                        r['phone'] or '—',
                        mail_lbl,
                        gender,
                        r['created_at'] or '—'
                    ]"""
    server_norm = server_norm.replace(old_row_data, new_row_data)

    with open('school_website/server.py', 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(server_norm)
    print("Updated export_credentials_excel in server.py")
else:
    print("old_excel not found in server.py!")
