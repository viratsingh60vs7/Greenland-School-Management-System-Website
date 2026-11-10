import re

# ==============================================================================
# 1. PATCH school_website/css/style.css
# ==============================================================================
with open('school_website/css/style.css', 'r', encoding='utf-8') as f:
    css_content = f.read()

if '.role-common_id' not in css_content:
    target_css = '.role-super_admin { background: #7c3aed; }'
    repl_css = '''.role-common_id { background: #0284c7; }
.role-it_admin { background: #0f172a; }
.role-super_admin { background: #7c3aed; }'''
    css_content = css_content.replace(target_css, repl_css)
    with open('school_website/css/style.css', 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(css_content)
    print("Updated style.css with .role-common_id and .role-it_admin styles")
else:
    print("style.css already contains .role-common_id")

# ==============================================================================
# 2. PATCH school_website/server.py
# ==============================================================================
with open('school_website/server.py', 'r', encoding='utf-8') as f:
    server_content = f.read()

server_norm = server_content.replace('\r\n', '\n')

# Schema migrations for users, lab_computers, and credential_requests
old_schema_part = """        if 'is_common_id' not in u_cols: cur.execute("ALTER TABLE users ADD COLUMN is_common_id INTEGER DEFAULT 0")
        if 'common_id_name' not in u_cols: cur.execute("ALTER TABLE users ADD COLUMN common_id_name TEXT")
        if 'has_mail_services' not in u_cols: cur.execute("ALTER TABLE users ADD COLUMN has_mail_services INTEGER DEFAULT 1")"""

new_schema_part = """        if 'is_common_id' not in u_cols: cur.execute("ALTER TABLE users ADD COLUMN is_common_id INTEGER DEFAULT 0")
        if 'common_id_name' not in u_cols: cur.execute("ALTER TABLE users ADD COLUMN common_id_name TEXT")
        if 'has_mail_services' not in u_cols: cur.execute("ALTER TABLE users ADD COLUMN has_mail_services INTEGER DEFAULT 1")
        if 'admin_user_id' not in u_cols: cur.execute("ALTER TABLE users ADD COLUMN admin_user_id INTEGER")
        if 'admin_username' not in u_cols: cur.execute("ALTER TABLE users ADD COLUMN admin_username TEXT")
        if 'admin_name' not in u_cols: cur.execute("ALTER TABLE users ADD COLUMN admin_name TEXT")"""

if old_schema_part in server_norm:
    server_norm = server_norm.replace(old_schema_part, new_schema_part)
    print("Updated users schema migration in server.py")

old_comp_schema = """        if 'common_id_name' not in c_cols: cur.execute("ALTER TABLE lab_computers ADD COLUMN common_id_name TEXT DEFAULT 'Computer Lab Fleet'")
        if 'has_mail_services' not in c_cols: cur.execute("ALTER TABLE lab_computers ADD COLUMN has_mail_services INTEGER DEFAULT 0")"""

new_comp_schema = """        if 'common_id_name' not in c_cols: cur.execute("ALTER TABLE lab_computers ADD COLUMN common_id_name TEXT DEFAULT 'Computer Lab Fleet'")
        if 'has_mail_services' not in c_cols: cur.execute("ALTER TABLE lab_computers ADD COLUMN has_mail_services INTEGER DEFAULT 0")
        if 'admin_user_id' not in c_cols: cur.execute("ALTER TABLE lab_computers ADD COLUMN admin_user_id INTEGER")
        if 'admin_username' not in c_cols: cur.execute("ALTER TABLE lab_computers ADD COLUMN admin_username TEXT")

        cur.execute("PRAGMA table_info(credential_requests)")
        cr_cols = [c[1] for c in cur.fetchall()]
        if 'is_common_id' not in cr_cols: cur.execute("ALTER TABLE credential_requests ADD COLUMN is_common_id INTEGER DEFAULT 0")
        if 'common_id_name' not in cr_cols: cur.execute("ALTER TABLE credential_requests ADD COLUMN common_id_name TEXT")
        if 'admin_user_id' not in cr_cols: cur.execute("ALTER TABLE credential_requests ADD COLUMN admin_user_id INTEGER")
        if 'admin_username' not in cr_cols: cur.execute("ALTER TABLE credential_requests ADD COLUMN admin_username TEXT")
        if 'admin_name' not in cr_cols: cur.execute("ALTER TABLE credential_requests ADD COLUMN admin_name TEXT")
        if 'assigned_lab_fleet' not in cr_cols: cur.execute("ALTER TABLE credential_requests ADD COLUMN assigned_lab_fleet TEXT")"""

if old_comp_schema in server_norm:
    server_norm = server_norm.replace(old_comp_schema, new_comp_schema)
    print("Updated lab_computers & credential_requests schema in server.py")

# Query in /api/users
old_users_query = """                    SELECT id, name, email, username, password, user_type, phone, photo, created_at, gender,
                           COALESCE(is_common_id, 0) as is_common_id,
                           common_id_name,
                           COALESCE(has_mail_services, 1) as has_mail_services
                    FROM users 
                    ORDER BY id ASC"""

new_users_query = """                    SELECT id, name, email, username, password, user_type, phone, photo, created_at, gender,
                           COALESCE(is_common_id, 0) as is_common_id,
                           common_id_name,
                           COALESCE(has_mail_services, 1) as has_mail_services,
                           admin_user_id,
                           admin_username,
                           admin_name
                    FROM users 
                    ORDER BY id ASC"""

if old_users_query in server_norm:
    server_norm = server_norm.replace(old_users_query, new_users_query)
    print("Updated /api/users query in server.py")

# /api/users/create implementation
old_users_create = """                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                is_common = 1 if body.get('is_common_id') or body.get('common_id_name') else 0
                common_name = (body.get('common_id_name') or '').strip() or (f"{new_role.capitalize()} Common Fleet" if is_common else None)
                # Rule: Common IDs have NO mail services
                has_mail = 0 if is_common else int(body.get('has_mail_services', 1))

                cur.execute(\"\"\"
                    INSERT INTO users (username, password, user_type, name, email, phone, gender, created_at, is_common_id, common_id_name, has_mail_services)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                \"\"\", (new_username, new_password, new_role, new_name, new_email, new_phone, new_gender, now, is_common, common_name, has_mail))
                conn.commit()
                new_uid = cur.lastrowid
                self.send_json({
                    "success": True,
                    "message": f"User ID '{new_username}' created and assigned to role '{new_role}' successfully!" + (" (Common ID - No Mail Services)" if is_common else ""),
                    "user_id": new_uid,
                    "is_common_id": is_common,
                    "common_id_name": common_name,
                    "has_mail_services": has_mail
                })"""

new_users_create = """                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                is_common = 1 if (new_role == 'common_id' or body.get('is_common_id') or body.get('common_id_name')) else 0
                common_name = (body.get('common_id_name') or '').strip() or (f"{new_username} Fleet" if is_common else None)
                has_mail = 0 if is_common else int(body.get('has_mail_services', 1))
                if is_common:
                    new_email = ''

                admin_user_id = body.get('admin_user_id')
                admin_username = (body.get('admin_username') or '').strip()
                admin_name = (body.get('admin_name') or '').strip()
                assigned_fleet = (body.get('assigned_lab_fleet') or body.get('lab_fleet') or '').strip().lower()

                if admin_user_id or admin_username:
                    cur.execute("SELECT id, username, name FROM users WHERE id = ? OR username = ?", (admin_user_id, admin_username))
                    adm_row = cur.fetchone()
                    if adm_row:
                        admin_user_id = adm_row['id']
                        admin_username = adm_row['username']
                        admin_name = adm_row['name'] or adm_row['username']

                cur.execute(\"\"\"
                    INSERT INTO users (username, password, user_type, name, email, phone, gender, created_at, is_common_id, common_id_name, has_mail_services, admin_user_id, admin_username, admin_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                \"\"\", (new_username, new_password, new_role, new_name, new_email, new_phone, new_gender, now, is_common, common_name, has_mail, admin_user_id, admin_username, admin_name))
                new_uid = cur.lastrowid

                # Link workstations fleet if selected for this Common ID
                if is_common and assigned_fleet in ('both', 'all', 'lab1_and_lab2', 'lab 1 & 2', 'computer lab 1 & 2'):
                    cur.execute(\"\"\"
                        UPDATE lab_computers 
                        SET assigned_teacher_id = ?,
                            assigned_teacher_username = ?,
                            admin_user_id = ?,
                            admin_username = ?,
                            is_common_id = 1,
                            common_id_name = ?,
                            has_mail_services = 0
                    \"\"\", (admin_user_id or new_uid, admin_username or new_username, admin_user_id, admin_username, common_name))
                elif is_common and '1' in assigned_fleet:
                    cur.execute(\"\"\"
                        UPDATE lab_computers 
                        SET assigned_teacher_id = ?,
                            assigned_teacher_username = ?,
                            admin_user_id = ?,
                            admin_username = ?,
                            is_common_id = 1,
                            common_id_name = ?,
                            has_mail_services = 0
                        WHERE lab_name LIKE '%Lab 1%'
                    \"\"\", (admin_user_id or new_uid, admin_username or new_username, admin_user_id, admin_username, common_name))
                elif is_common and '2' in assigned_fleet:
                    cur.execute(\"\"\"
                        UPDATE lab_computers 
                        SET assigned_teacher_id = ?,
                            assigned_teacher_username = ?,
                            admin_user_id = ?,
                            admin_username = ?,
                            is_common_id = 1,
                            common_id_name = ?,
                            has_mail_services = 0
                        WHERE lab_name LIKE '%Lab 2%'
                    \"\"\", (admin_user_id or new_uid, admin_username or new_username, admin_user_id, admin_username, common_name))

                conn.commit()
                self.send_json({
                    "success": True,
                    "message": f"User ID '{new_username}' created and assigned to role '{new_role}' successfully!" + (f" (Common ID: Admin is '{admin_name or admin_username}' - No Mail Services)" if is_common and (admin_name or admin_username) else (" (Common ID - No Mail Services)" if is_common else "")),
                    "user_id": new_uid,
                    "is_common_id": is_common,
                    "common_id_name": common_name,
                    "admin_user_id": admin_user_id,
                    "admin_username": admin_username,
                    "admin_name": admin_name,
                    "has_mail_services": has_mail
                })"""

if old_users_create in server_norm:
    server_norm = server_norm.replace(old_users_create, new_users_create)
    print("Updated /api/users/create in server.py")
else:
    print("Could not find old_users_create in server.py!")

# /api/users/assign_role implementation
old_assign_role = """                is_common = 1 if body.get('is_common_id') or body.get('common_id_name') else (1 if 'common' in str(body.get('common_id_name', '')).lower() else 0)
                common_name = (body.get('common_id_name') or '').strip()
                has_mail = 0 if is_common else int(body.get('has_mail_services', 1))
                assigned_fleet = (body.get('assigned_lab_fleet') or '').strip().lower()

                # Update role, common id, and name/gender according to rule
                if target_name:
                    cur.execute(\"\"\"
                        UPDATE users 
                        SET user_type = ?,
                            name = ?,
                            gender = ?,
                            is_common_id = ?,
                            common_id_name = ?,
                            has_mail_services = ?
                        WHERE id = ?
                    \"\"\", (new_role, target_name, target_gender, is_common, common_name if is_common else None, has_mail, target_id))
                else:
                    cur.execute(\"\"\"
                        UPDATE users 
                        SET user_type = ?,
                            is_common_id = ?,
                            common_id_name = ?,
                            has_mail_services = ?
                        WHERE id = ?
                    \"\"\", (new_role, is_common, common_name if is_common else None, has_mail, target_id))
                    cur.execute("UPDATE users SET gender = NULL WHERE id = ? AND (name IS NULL OR TRIM(name) = '')", (target_id,))"""

new_assign_role = """                is_common = 1 if (new_role == 'common_id' or body.get('is_common_id') or body.get('common_id_name')) else (1 if 'common' in str(body.get('common_id_name', '')).lower() else 0)
                common_name = (body.get('common_id_name') or '').strip()
                has_mail = 0 if is_common else int(body.get('has_mail_services', 1))
                assigned_fleet = (body.get('assigned_lab_fleet') or '').strip().lower()

                admin_user_id = body.get('admin_user_id')
                admin_username = (body.get('admin_username') or '').strip()
                admin_name = (body.get('admin_name') or '').strip()
                if admin_user_id or admin_username:
                    cur.execute("SELECT id, username, name FROM users WHERE id = ? OR username = ?", (admin_user_id, admin_username))
                    adm_row = cur.fetchone()
                    if adm_row:
                        admin_user_id = adm_row['id']
                        admin_username = adm_row['username']
                        admin_name = adm_row['name'] or adm_row['username']

                # Update role, common id, admin, and name/gender according to rule
                if target_name:
                    cur.execute(\"\"\"
                        UPDATE users 
                        SET user_type = ?,
                            name = ?,
                            gender = ?,
                            is_common_id = ?,
                            common_id_name = ?,
                            has_mail_services = ?,
                            admin_user_id = ?,
                            admin_username = ?,
                            admin_name = ?
                        WHERE id = ?
                    \"\"\", (new_role, target_name, target_gender, is_common, common_name if is_common else None, has_mail, admin_user_id, admin_username, admin_name, target_id))
                else:
                    cur.execute(\"\"\"
                        UPDATE users 
                        SET user_type = ?,
                            is_common_id = ?,
                            common_id_name = ?,
                            has_mail_services = ?,
                            admin_user_id = ?,
                            admin_username = ?,
                            admin_name = ?
                        WHERE id = ?
                    \"\"\", (new_role, is_common, common_name if is_common else None, has_mail, admin_user_id, admin_username, admin_name, target_id))
                    cur.execute("UPDATE users SET gender = NULL WHERE id = ? AND (name IS NULL OR TRIM(name) = '')", (target_id,))"""

if old_assign_role in server_norm:
    server_norm = server_norm.replace(old_assign_role, new_assign_role)
    print("Updated /api/users/assign_role in server.py")
else:
    print("Could not find old_assign_role in server.py!")

# /api/credentials/request_create and /api/credentials/approve in server.py
old_req_create = """                proposed_username = body.get('username', '').strip()
                proposed_password = body.get('password', '').strip()
                proposed_name = body.get('name', '').strip()
                proposed_role = body.get('user_type', 'student').strip()
                proposed_email = body.get('email', '').strip()
                proposed_phone = body.get('phone', '').strip()
                proposed_gender = body.get('gender')
                reason = body.get('reason', 'New system account created by IT Support').strip()
                requester_name = body.get('requested_by_name', 'IT Support Administrator').strip()
                requester_id = body.get('requested_by_id')
                requester_username = body.get('requested_by_username', '').strip()"""

new_req_create = """                proposed_username = body.get('username', '').strip()
                proposed_password = body.get('password', '').strip()
                proposed_name = body.get('name', '').strip()
                proposed_role = body.get('user_type', 'teacher').strip()
                proposed_email = body.get('email', '').strip()
                proposed_phone = body.get('phone', '').strip()
                proposed_gender = body.get('gender')
                reason = body.get('reason', 'New system account created by IT Support').strip()
                requester_name = body.get('requested_by_name', 'IT Support Administrator').strip()
                requester_id = body.get('requested_by_id')
                requester_username = body.get('requested_by_username', '').strip()

                is_common = 1 if (proposed_role == 'common_id' or body.get('is_common_id') or body.get('common_id_name')) else 0
                common_name = (body.get('common_id_name') or '').strip() or (f"{proposed_username} Fleet" if is_common else None)
                admin_user_id = body.get('admin_user_id')
                admin_username = (body.get('admin_username') or '').strip()
                admin_name = (body.get('admin_name') or '').strip()
                assigned_fleet = (body.get('assigned_lab_fleet') or body.get('lab_fleet') or '').strip().lower()

                if admin_user_id or admin_username:
                    cur.execute("SELECT id, username, name FROM users WHERE id = ? OR username = ?", (admin_user_id, admin_username))
                    adm_row = cur.fetchone()
                    if adm_row:
                        admin_user_id = adm_row['id']
                        admin_username = adm_row['username']
                        admin_name = adm_row['name'] or adm_row['username']"""

if old_req_create in server_norm:
    server_norm = server_norm.replace(old_req_create, new_req_create)
    print("Updated /api/credentials/request_create variables in server.py")

old_it_create_insert = """                if is_owner:
                    cur.execute(\"\"\"
                        INSERT INTO users (name, email, username, password, user_type, phone, gender, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    \"\"\", (proposed_name, proposed_email, proposed_username, proposed_password, proposed_role, proposed_phone, proposed_gender, now))
                    new_uid = cur.lastrowid
                    cur.execute(\"\"\"
                        INSERT INTO credential_requests (
                            request_type, user_id, target_username, proposed_username, proposed_password,
                            proposed_name, proposed_role, proposed_email, proposed_phone, proposed_gender,
                            reason, requested_by_id, requested_by_name, status, approved_by, approved_at, created_at
                        ) VALUES ('create_user', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Approved', 'Owner (Director) Rajeev Sinha', ?, ?)
                    \"\"\", (new_uid, proposed_username, proposed_username, proposed_password, proposed_name, proposed_role, proposed_email, proposed_phone, proposed_gender, reason, requester_id, requester_name, now, now))
                    conn.commit()
                    self.send_json({
                        "success": True,
                        "message": f"Owner Executive Authority: User account '{proposed_username}' created and activated immediately!",
                        "user_id": new_uid
                    })
                else:
                    cur.execute(\"\"\"
                        INSERT INTO credential_requests (
                            request_type, target_username, proposed_username, proposed_password,
                            proposed_name, proposed_role, proposed_email, proposed_phone, proposed_gender,
                            reason, requested_by_id, requested_by_name, status, created_at
                        ) VALUES ('create_user', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending Owner Approval', ?)
                    \"\"\", (proposed_username, proposed_username, proposed_password, proposed_name, proposed_role, proposed_email, proposed_phone, proposed_gender, reason, requester_id, requester_name, now))
                    conn.commit()"""

new_it_create_insert = """                if is_owner:
                    cur.execute(\"\"\"
                        INSERT INTO users (name, email, username, password, user_type, phone, gender, created_at, is_common_id, common_id_name, has_mail_services, admin_user_id, admin_username, admin_name)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    \"\"\", (proposed_name, '' if is_common else proposed_email, proposed_username, proposed_password, proposed_role, proposed_phone, proposed_gender, now, is_common, common_name, 0 if is_common else 1, admin_user_id, admin_username, admin_name))
                    new_uid = cur.lastrowid

                    if is_common and assigned_fleet in ('both', 'all', 'lab1_and_lab2', 'lab 1 & 2', 'computer lab 1 & 2'):
                        cur.execute(\"\"\"
                            UPDATE lab_computers 
                            SET assigned_teacher_id = ?, assigned_teacher_username = ?, admin_user_id = ?, admin_username = ?, is_common_id = 1, common_id_name = ?, has_mail_services = 0
                        \"\"\", (admin_user_id or new_uid, admin_username or proposed_username, admin_user_id, admin_username, common_name))
                    elif is_common and '1' in assigned_fleet:
                        cur.execute(\"\"\"
                            UPDATE lab_computers 
                            SET assigned_teacher_id = ?, assigned_teacher_username = ?, admin_user_id = ?, admin_username = ?, is_common_id = 1, common_id_name = ?, has_mail_services = 0
                            WHERE lab_name LIKE '%Lab 1%'
                        \"\"\", (admin_user_id or new_uid, admin_username or proposed_username, admin_user_id, admin_username, common_name))
                    elif is_common and '2' in assigned_fleet:
                        cur.execute(\"\"\"
                            UPDATE lab_computers 
                            SET assigned_teacher_id = ?, assigned_teacher_username = ?, admin_user_id = ?, admin_username = ?, is_common_id = 1, common_id_name = ?, has_mail_services = 0
                            WHERE lab_name LIKE '%Lab 2%'
                        \"\"\", (admin_user_id or new_uid, admin_username or proposed_username, admin_user_id, admin_username, common_name))

                    cur.execute(\"\"\"
                        INSERT INTO credential_requests (
                            request_type, user_id, target_username, proposed_username, proposed_password,
                            proposed_name, proposed_role, proposed_email, proposed_phone, proposed_gender,
                            reason, requested_by_id, requested_by_name, status, approved_by, approved_at, created_at,
                            is_common_id, common_id_name, admin_user_id, admin_username, admin_name, assigned_lab_fleet
                        ) VALUES ('create_user', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Approved', 'Owner (Director) Rajeev Sinha', ?, ?, ?, ?, ?, ?, ?, ?)
                    \"\"\", (new_uid, proposed_username, proposed_username, proposed_password, proposed_name, proposed_role, '' if is_common else proposed_email, proposed_phone, proposed_gender, reason, requester_id, requester_name, now, now, is_common, common_name, admin_user_id, admin_username, admin_name, assigned_fleet))
                    conn.commit()
                    self.send_json({
                        "success": True,
                        "message": f"Owner Executive Authority: User account '{proposed_username}' created and activated immediately!",
                        "user_id": new_uid
                    })
                else:
                    cur.execute(\"\"\"
                        INSERT INTO credential_requests (
                            request_type, target_username, proposed_username, proposed_password,
                            proposed_name, proposed_role, proposed_email, proposed_phone, proposed_gender,
                            reason, requested_by_id, requested_by_name, status, created_at,
                            is_common_id, common_id_name, admin_user_id, admin_username, admin_name, assigned_lab_fleet
                        ) VALUES ('create_user', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending Owner Approval', ?, ?, ?, ?, ?, ?, ?)
                    \"\"\", (proposed_username, proposed_username, proposed_password, proposed_name, proposed_role, '' if is_common else proposed_email, proposed_phone, proposed_gender, reason, requester_id, requester_name, now, is_common, common_name, admin_user_id, admin_username, admin_name, assigned_fleet))
                    conn.commit()"""

if old_it_create_insert in server_norm:
    server_norm = server_norm.replace(old_it_create_insert, new_it_create_insert)
    print("Updated credential_requests insert in server.py")

# In /api/credentials/approve:
old_approve_create = """                elif req['request_type'] == 'create_user':
                    cur.execute(\"\"\"
                        INSERT INTO users (name, email, username, password, user_type, phone, gender, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    \"\"\", (req['proposed_name'], req['proposed_email'], req['proposed_username'], req['proposed_password'], req['proposed_role'], req['proposed_phone'], req['proposed_gender'], now))
                    new_uid = cur.lastrowid
                    cur.execute(\"\"\"
                        UPDATE credential_requests
                        SET status = 'Approved', approved_by = ?, approved_at = ?, user_id = ?
                        WHERE id = ?
                    \"\"\", (approver_name, now, new_uid, request_id))
                    conn.commit()"""

new_approve_create = """                elif req['request_type'] == 'create_user':
                    is_c = req['is_common_id'] or (1 if req['proposed_role'] == 'common_id' else 0)
                    c_name = req['common_id_name']
                    adm_uid = req['admin_user_id']
                    adm_uname = req['admin_username']
                    adm_name = req['admin_name']
                    a_fleet = (req['assigned_lab_fleet'] or '').lower()

                    cur.execute(\"\"\"
                        INSERT INTO users (name, email, username, password, user_type, phone, gender, created_at, is_common_id, common_id_name, has_mail_services, admin_user_id, admin_username, admin_name)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    \"\"\", (req['proposed_name'], '' if is_c else req['proposed_email'], req['proposed_username'], req['proposed_password'], req['proposed_role'], req['proposed_phone'], req['proposed_gender'], now, is_c, c_name, 0 if is_c else 1, adm_uid, adm_uname, adm_name))
                    new_uid = cur.lastrowid

                    if is_c and a_fleet in ('both', 'all', 'lab1_and_lab2', 'lab 1 & 2', 'computer lab 1 & 2'):
                        cur.execute(\"\"\"
                            UPDATE lab_computers 
                            SET assigned_teacher_id = ?, assigned_teacher_username = ?, admin_user_id = ?, admin_username = ?, is_common_id = 1, common_id_name = ?, has_mail_services = 0
                        \"\"\", (adm_uid or new_uid, adm_uname or req['proposed_username'], adm_uid, adm_uname, c_name))
                    elif is_c and '1' in a_fleet:
                        cur.execute(\"\"\"
                            UPDATE lab_computers 
                            SET assigned_teacher_id = ?, assigned_teacher_username = ?, admin_user_id = ?, admin_username = ?, is_common_id = 1, common_id_name = ?, has_mail_services = 0
                            WHERE lab_name LIKE '%Lab 1%'
                        \"\"\", (adm_uid or new_uid, adm_uname or req['proposed_username'], adm_uid, adm_uname, c_name))
                    elif is_c and '2' in a_fleet:
                        cur.execute(\"\"\"
                            UPDATE lab_computers 
                            SET assigned_teacher_id = ?, assigned_teacher_username = ?, admin_user_id = ?, admin_username = ?, is_common_id = 1, common_id_name = ?, has_mail_services = 0
                            WHERE lab_name LIKE '%Lab 2%'
                        \"\"\", (adm_uid or new_uid, adm_uname or req['proposed_username'], adm_uid, adm_uname, c_name))

                    cur.execute(\"\"\"
                        UPDATE credential_requests
                        SET status = 'Approved', approved_by = ?, approved_at = ?, user_id = ?
                        WHERE id = ?
                    \"\"\", (approver_name, now, new_uid, request_id))
                    conn.commit()"""

if old_approve_create in server_norm:
    server_norm = server_norm.replace(old_approve_create, new_approve_create)
    print("Updated /api/credentials/approve in server.py")

with open('school_website/server.py', 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(server_norm)
print("Saved patched server.py")
