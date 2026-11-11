with open('school_website/server.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add /api/login_directory in do_GET
target_get = """            elif path == '/api/users':
                # Full user accounts list for Director control center
                cur.execute(\"\"\"
                    SELECT id, name, email, username, password, user_type, phone, photo, created_at, gender 
                    FROM users 
                    ORDER BY id ASC
                \"\"\")
                self.send_json([dict(r) for r in cur.fetchall()])"""

replacement_get = """            elif path == '/api/users':
                # Full user accounts list for Director control center
                cur.execute(\"\"\"
                    SELECT id, name, email, username, password, user_type, phone, photo, created_at, gender 
                    FROM users 
                    ORDER BY id ASC
                \"\"\")
                self.send_json([dict(r) for r in cur.fetchall()])

            elif path == '/api/login_directory':
                # Dynamic User ID directory for Login Portal:
                # - If user ID is deleted from database, it will NOT be returned here.
                # - When new user ID is created, it will be immediately returned here.
                # - ONLY teacher user IDs have is_clickable = True (only teachers can be clicked to auto-fill).
                cur.execute(\"\"\"
                    SELECT id, username, user_type, name, email, gender
                    FROM users
                    WHERE user_type != 'student'
                    ORDER BY 
                        CASE user_type
                            WHEN 'super_admin' THEN 1
                            WHEN 'admin' THEN 2
                            WHEN 'it_admin' THEN 3
                            WHEN 'accountant' THEN 4
                            WHEN 'teacher' THEN 5
                            WHEN 'librarian' THEN 6
                            ELSE 7
                        END ASC, id ASC
                \"\"\")
                rows = cur.fetchall()
                directory = []
                for r in rows:
                    u_type = r['user_type'] or 'staff'
                    is_teacher = (u_type == 'teacher')
                    
                    role_title = "Staff"
                    icon = "👤"
                    if u_type == 'super_admin':
                        role_title = "Owner (Director)" if "direct" in (r['name'] or '').lower() or r['username'] == 'Owner(Directer)' else "Super Admin"
                        icon = "👑"
                    elif u_type == 'admin':
                        role_title = "Principal (Admin)"
                        icon = "🛡️"
                    elif u_type == 'it_admin':
                        role_title = "IT Administrator"
                        icon = "💻"
                    elif u_type == 'accountant':
                        role_title = "Accountant"
                        icon = "💰"
                    elif u_type == 'teacher':
                        first_name = (r['name'] or '').strip().split()[0] if r['name'] else ''
                        role_title = f"Teacher {first_name}".strip() if first_name else "Teacher"
                        icon = "👨‍🏫"
                    elif u_type == 'librarian':
                        role_title = "Librarian"
                        icon = "📚"
                    elif u_type == 'parent':
                        role_title = "Parent Guardian"
                        icon = "👨‍👩‍👧"
                    else:
                        role_title = u_type.replace('_', ' ').title()

                    directory.append({
                        "id": r['id'],
                        "username": r['username'],
                        "user_type": u_type,
                        "name": r['name'] or '',
                        "role_title": role_title,
                        "icon": icon,
                        "is_teacher": is_teacher,
                        "is_clickable": is_teacher  # STRICT REQUIREMENT: Only teacher can click on it
                    })
                self.send_json({"success": True, "users": directory})"""

assert target_get in code, "target_get not found in server.py"
code = code.replace(target_get, replacement_get, 1)

# 2. Update /api/users/create to support flexible payload and add /api/users/delete
target_post = """            elif path == '/api/users/create':
                # STRICT REQUIREMENT: Every ID created by Director, who assigns roles
                # STRICT NAME & GENDER RULE: In any ID having no name, there is no gender.
                # If role is assigned to a person (name provided), then assigned person's gender is shown.
                user_id = body.get('user_id')
                username = body.get('username', '').strip()
                cur.execute("SELECT id, username, user_type FROM users WHERE id = ? OR username = ?", (user_id, username))
                caller = cur.fetchone()
                if not caller or (caller['username'] != 'Owner(Directer)' and caller['user_type'] != 'super_admin'):
                    self.send_json({"success": False, "error": "Access Denied: Only the Director (Owner) can create new User IDs."}, 403)
                    return

                new_username = body.get('new_username', '').strip()
                new_password = body.get('new_password', '').strip() or 'Greenland@2026'
                new_role = body.get('role', 'teacher').strip()
                new_name = (body.get('name') or '').strip()
                new_email = (body.get('email') or '').strip() or f"{new_username.lower()}@greenlandschool.net"
                new_phone = (body.get('phone') or '').strip() or '+91 761 700 5055'

                new_gender = body.get('gender') if new_name else None

                cur.execute("SELECT id FROM users WHERE LOWER(username) = LOWER(?)", (new_username,))
                if cur.fetchone():
                    self.send_json({"success": False, "error": f"Username '{new_username}' already exists. Please choose a unique User ID."}, 400)
                    return

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur.execute(\"\"\"
                    INSERT INTO users (username, password, user_type, name, email, phone, gender, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                \"\"\", (new_username, new_password, new_role, new_name, new_email, new_phone, new_gender, now))
                conn.commit()
                new_uid = cur.lastrowid
                self.send_json({
                    "success": True,
                    "message": f"User ID '{new_username}' created and assigned to role '{new_role}' successfully!",
                    "user_id": new_uid
                })"""

replacement_post = """            elif path == '/api/users/create':
                # STRICT REQUIREMENT: Every ID created by Director or IT Support Admin, who assigns roles
                # STRICT NAME & GENDER RULE: In any ID having no name, there is no gender.
                # If role is assigned to a person (name provided), then assigned person's gender is shown.
                caller_id = body.get('user_id') or body.get('caller_id')
                caller_username = (body.get('caller_username') or body.get('created_by') or body.get('requested_by') or '').strip()
                
                # Check caller permissions
                cur.execute("SELECT id, username, user_type FROM users WHERE id = ? OR username = ? OR username = 'Owner(Directer)'", (caller_id, caller_username))
                caller = cur.fetchone()
                if not caller or (caller['username'] != 'Owner(Directer)' and caller['user_type'] not in ('super_admin', 'it_admin')):
                    self.send_json({"success": False, "error": "Access Denied: Only the Director (Owner) or IT Support Administrator can create new User IDs."}, 403)
                    return

                new_username = (body.get('new_username') or body.get('username') or '').strip()
                new_password = (body.get('new_password') or body.get('password') or 'Greenland@2026').strip()
                new_role = (body.get('role') or body.get('user_type') or 'teacher').strip()
                new_name = (body.get('name') or '').strip()
                new_email = (body.get('email') or '').strip() or f"{new_username.lower()}@greenlandschool.net"
                new_phone = (body.get('phone') or '').strip() or '+91 761 700 5055'

                if not new_username:
                    self.send_json({"success": False, "error": "New User ID (username) is required."}, 400)
                    return

                new_gender = body.get('gender') if new_name else None

                cur.execute("SELECT id FROM users WHERE LOWER(username) = LOWER(?)", (new_username,))
                if cur.fetchone():
                    self.send_json({"success": False, "error": f"Username '{new_username}' already exists. Please choose a unique User ID."}, 400)
                    return

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur.execute(\"\"\"
                    INSERT INTO users (username, password, user_type, name, email, phone, gender, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                \"\"\", (new_username, new_password, new_role, new_name, new_email, new_phone, new_gender, now))
                conn.commit()
                new_uid = cur.lastrowid
                self.send_json({
                    "success": True,
                    "message": f"User ID '{new_username}' created and assigned to role '{new_role}' successfully!",
                    "user_id": new_uid
                })

            elif path == '/api/users/delete':
                # User Deletion: Deletes user ID permanently.
                # Once deleted, user will no longer be listed on the login page directory.
                target_id = body.get('id') or body.get('user_id')
                target_username = (body.get('username') or '').strip()

                if not target_id and not target_username:
                    self.send_json({"success": False, "error": "User ID or username is required."}, 400)
                    return

                cur.execute("SELECT id, username, user_type, name FROM users WHERE id = ? OR username = ?", (target_id, target_username))
                target = cur.fetchone()
                if not target:
                    self.send_json({"success": False, "error": "User account not found."}, 404)
                    return

                # Protect essential foundational accounts
                if target['username'] in ('Owner(Directer)', 'GS_itsupport'):
                    self.send_json({"success": False, "error": f"Protected System Account: '{target['username']}' cannot be deleted."}, 403)
                    return

                uid = target['id']
                uname = target['username']
                utype = target['user_type']

                # Clean up dependencies if teacher
                if utype == 'teacher':
                    cur.execute("UPDATE sections SET class_teacher_id = NULL WHERE class_teacher_id = ?", (uid,))
                    cur.execute("UPDATE subjects SET teacher_id = NULL WHERE teacher_id = ?", (uid,))
                    cur.execute("DELETE FROM leaves WHERE user_id = ?", (uid,))

                cur.execute("DELETE FROM users WHERE id = ?", (uid,))
                conn.commit()
                self.send_json({
                    "success": True,
                    "message": f"User ID '{uname}' has been deleted permanently and will no longer appear on the login page.",
                    "deleted_id": uid,
                    "deleted_username": uname
                })"""

assert target_post in code, "target_post not found in server.py"
code = code.replace(target_post, replacement_post, 1)

with open('school_website/server.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ server.py patched successfully with /api/login_directory and /api/users/delete!")
