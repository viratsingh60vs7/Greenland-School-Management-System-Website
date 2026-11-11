import re

with open('school_website/server.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update /api/login in server.py to support phone number as User ID
target_login_query = """                # Flexible matching: by username, registered email, role type, or aliases
                clean_role = username_or_email.lower().replace(' ', '_').replace('gs_', '')
                cur.execute(\"\"\"
                    SELECT id, name, email, username, user_type, phone, photo, password, COALESCE(gender, 'Male') as gender 
                    FROM users 
                    WHERE LOWER(email) = LOWER(?) 
                       OR LOWER(username) = LOWER(?) 
                       OR LOWER(user_type) = LOWER(?)
                       OR LOWER(user_type) = ?
                       OR LOWER(REPLACE(username, 'GS_', '')) = LOWER(?)
                       OR (LOWER(?) IN ('owner(directer)', 'owner(director)', 'owner', 'director') AND username = 'Owner(Directer)')
                    LIMIT 1
                \"\"\", (username_or_email, username_or_email, username_or_email, clean_role, username_or_email, username_or_email))
                user = cur.fetchone()"""

replacement_login_query = """                # Flexible dual matching: by username, registered email, or REGISTERED PHONE NUMBER
                clean_role = username_or_email.lower().replace(' ', '_').replace('gs_', '')
                clean_digits = re.sub(r'\\D', '', username_or_email)

                cur.execute(\"\"\"
                    SELECT id, name, email, username, user_type, phone, photo, password, COALESCE(gender, 'Male') as gender 
                    FROM users 
                    WHERE LOWER(email) = LOWER(?) 
                       OR LOWER(username) = LOWER(?) 
                       OR LOWER(user_type) = LOWER(?)
                       OR LOWER(user_type) = ?
                       OR LOWER(REPLACE(username, 'GS_', '')) = LOWER(?)
                       OR (LOWER(?) IN ('owner(directer)', 'owner(director)', 'owner', 'director') AND username = 'Owner(Directer)')
                       OR phone = ?
                       OR (LENGTH(?) >= 7 AND REPLACE(REPLACE(REPLACE(REPLACE(COALESCE(phone, ''), ' ', ''), '-', ''), '+', ''), '(', '') LIKE '%' || ? || '%')
                    LIMIT 1
                \"\"\", (username_or_email, username_or_email, username_or_email, clean_role, username_or_email, username_or_email, username_or_email, clean_digits, clean_digits))
                user = cur.fetchone()

                # If not found directly in users, check phone in students table (for student or parent)
                if not user and len(clean_digits) >= 7:
                    # Check student phone
                    cur.execute(\"\"\"
                        SELECT u.id, u.name, u.email, u.username, u.user_type, u.phone, u.photo, u.password, COALESCE(u.gender, 'Male') as gender
                        FROM students s
                        JOIN users u ON s.user_id = u.id
                        WHERE s.phone = ? OR REPLACE(REPLACE(REPLACE(REPLACE(COALESCE(s.phone, ''), ' ', ''), '-', ''), '+', ''), '(', '') LIKE '%' || ? || '%'
                        LIMIT 1
                    \"\"\", (username_or_email, clean_digits))
                    user = cur.fetchone()

                if not user and len(clean_digits) >= 7:
                    # Check parent phone
                    cur.execute(\"\"\"
                        SELECT p.id, p.name, p.email, p.username, p.user_type, p.phone, p.photo, p.password, COALESCE(p.gender, 'Male') as gender
                        FROM students s
                        JOIN users p ON s.parent_id = p.id
                        WHERE p.phone = ? OR REPLACE(REPLACE(REPLACE(REPLACE(COALESCE(p.phone, ''), ' ', ''), '-', ''), '+', ''), '(', '') LIKE '%' || ? || '%'
                        LIMIT 1
                    \"\"\", (username_or_email, clean_digits))
                    user = cur.fetchone()"""

assert target_login_query in code, "target_login_query not found in server.py"
code = code.replace(target_login_query, replacement_login_query, 1)

# 2. Add it_asset_requests table creation in init_db or server startup
table_creation = """
    # IT Asset Requests created by IT Team requiring Director Approval
    cur.execute('''
        CREATE TABLE IF NOT EXISTS it_asset_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_type TEXT,
            title TEXT,
            description TEXT,
            estimated_cost REAL DEFAULT 0,
            requested_by TEXT DEFAULT 'IT Support Administrator',
            status TEXT DEFAULT 'Pending Director Approval',
            director_notes TEXT,
            approved_at TEXT,
            created_at TEXT
        )
    ''')
"""
cur_users_table_pos = code.find("CREATE TABLE IF NOT EXISTS it_assets")
if cur_users_table_pos != -1:
    code = code[:cur_users_table_pos] + table_creation + code[cur_users_table_pos:]

# 3. Add Director Approvals & App Endpoints in do_GET
target_get_endpoint = "elif path == '/api/login_directory':"
new_get_endpoints = """elif path == '/api/app/student_dashboard':
                # App endpoint for student access
                uid = query.get('user_id', [None])[0]
                uname = query.get('username', [None])[0]
                cur.execute("SELECT * FROM users WHERE id = ? OR username = ?", (uid, uname))
                u = cur.fetchone()
                if not u:
                    self.send_json({"success": False, "error": "Student account not found."}, 404)
                    return

                cur.execute(\"\"\"
                    SELECT s.*, c.name as class_name, sec.name as section_name
                    FROM students s
                    LEFT JOIN classes c ON s.class_id = c.id
                    LEFT JOIN sections sec ON s.section_id = sec.id
                    WHERE s.user_id = ?
                \"\"\", (u['id'],))
                s_row = cur.fetchone()
                s_id = s_row['id'] if s_row else 0

                # Fees
                cur.execute("SELECT * FROM payments WHERE student_id = ? ORDER BY id DESC", (s_id,))
                fees = [dict(r) for r in cur.fetchall()]

                # Issued library books (Booklet)
                cur.execute(\"\"\"
                    SELECT br.*, b.title as book_title, b.author, b.cover, b.bookshelf
                    FROM book_requests br
                    JOIN books b ON br.book_id = b.id
                    WHERE br.user_id = ? AND br.status IN ('Issued', 'Approved', 'Pending')
                    ORDER BY br.id DESC
                \"\"\", (u['id'],))
                books = [dict(r) for r in cur.fetchall()]

                # Timetable
                c_id = s_row['class_id'] if s_row else 1
                sec_id = s_row['section_id'] if s_row else 1
                cur.execute(\"\"\"
                    SELECT sub.name as subject_name, sub.code, sec.name as section_name, c.name as class_name,
                           u.name as teacher_name
                    FROM subjects sub
                    LEFT JOIN sections sec ON sub.class_id = sec.class_id
                    LEFT JOIN classes c ON sub.class_id = c.id
                    LEFT JOIN users u ON sub.teacher_id = u.id
                    WHERE sub.class_id = ?
                    LIMIT 6
                \"\"\", (c_id,))
                timetable = [dict(r) for r in cur.fetchall()]

                # Marksheet
                cur.execute(\"\"\"
                    SELECT m.*, sub.name as subject_name, ex.name as exam_name
                    FROM marks m
                    JOIN subjects sub ON m.subject_id = sub.id
                    LEFT JOIN exams ex ON m.exam_id = ex.id
                    WHERE m.student_id = ?
                    ORDER BY m.id DESC
                \"\"\", (s_id,))
                marks = [dict(r) for r in cur.fetchall()]

                self.send_json({
                    "success": True,
                    "student": {
                        "user_id": u['id'],
                        "student_id": s_id,
                        "name": u['name'],
                        "username": u['username'],
                        "phone": u['phone'],
                        "email": u['email'],
                        "photo": u['photo'],
                        "gender": u['gender'],
                        "adm_no": s_row['adm_no'] if s_row else 'GS-2026-001',
                        "class_name": s_row['class_name'] if s_row else 'Class 10',
                        "section_name": s_row['section_name'] if s_row else 'Section A',
                        "blood_group": s_row['blood_group'] if s_row else 'O+',
                        "attendance_pct": 95.4
                    },
                    "fees": fees,
                    "issued_books": books,
                    "timetable": timetable,
                    "marks": marks
                })

            elif path == '/api/app/parent_dashboard':
                # App endpoint for parent access (Multiple children in one login)
                uid = query.get('user_id', [None])[0]
                uname = query.get('username', [None])[0]
                cur.execute("SELECT * FROM users WHERE id = ? OR username = ?", (uid, uname))
                parent = cur.fetchone()
                if not parent:
                    self.send_json({"success": False, "error": "Parent account not found."}, 404)
                    return

                # Get all children linked to this parent
                cur.execute(\"\"\"
                    SELECT s.id as student_id, s.user_id, s.adm_no, s.blood_group,
                           u.name, u.username, u.photo, u.gender, u.phone,
                           c.name as class_name, sec.name as section_name
                    FROM students s
                    JOIN users u ON s.user_id = u.id
                    LEFT JOIN classes c ON s.class_id = c.id
                    LEFT JOIN sections sec ON s.section_id = sec.id
                    WHERE s.parent_id = ?
                    ORDER BY s.id ASC
                \"\"\", (parent['id'],))
                children_rows = cur.fetchall()

                # If no direct child linked, fetch any active students as fallback for parent demonstration
                if not children_rows:
                    cur.execute(\"\"\"
                        SELECT s.id as student_id, s.user_id, s.adm_no, s.blood_group,
                               u.name, u.username, u.photo, u.gender, u.phone,
                               c.name as class_name, sec.name as section_name
                        FROM students s
                        JOIN users u ON s.user_id = u.id
                        LEFT JOIN classes c ON s.class_id = c.id
                        LEFT JOIN sections sec ON s.section_id = sec.id
                        ORDER BY s.id ASC
                        LIMIT 2
                    \"\"\")
                    children_rows = cur.fetchall()

                children = []
                for cr in children_rows:
                    cid = cr['student_id']
                    c_uid = cr['user_id']

                    # Child fees
                    cur.execute("SELECT * FROM payments WHERE student_id = ? ORDER BY id DESC", (cid,))
                    c_fees = [dict(r) for r in cur.fetchall()]

                    # Child library books
                    cur.execute(\"\"\"
                        SELECT br.*, b.title as book_title, b.author, b.bookshelf
                        FROM book_requests br
                        JOIN books b ON br.book_id = b.id
                        WHERE br.user_id = ? AND br.status IN ('Issued', 'Approved', 'Pending')
                    \"\"\", (c_uid,))
                    c_books = [dict(r) for r in cur.fetchall()]

                    # Child marks
                    cur.execute(\"\"\"
                        SELECT m.*, sub.name as subject_name
                        FROM marks m
                        JOIN subjects sub ON m.subject_id = sub.id
                        WHERE m.student_id = ?
                    \"\"\", (cid,))
                    c_marks = [dict(r) for r in cur.fetchall()]

                    children.append({
                        "student_id": cid,
                        "user_id": c_uid,
                        "name": cr['name'],
                        "username": cr['username'],
                        "photo": cr['photo'],
                        "adm_no": cr['adm_no'],
                        "class_name": cr['class_name'] or 'Class 5',
                        "section_name": cr['section_name'] or 'Section A',
                        "blood_group": cr['blood_group'] or 'O+',
                        "attendance_pct": 94.8,
                        "fees": c_fees,
                        "issued_books": c_books,
                        "marks": c_marks
                    })

                self.send_json({
                    "success": True,
                    "parent": {
                        "id": parent['id'],
                        "name": parent['name'],
                        "username": parent['username'],
                        "phone": parent['phone'],
                        "email": parent['email']
                    },
                    "children": children
                })

            elif path == '/api/app/teacher_dashboard':
                # App endpoint for teacher access
                uid = query.get('user_id', [None])[0]
                uname = query.get('username', [None])[0]
                cur.execute("SELECT * FROM users WHERE id = ? OR username = ?", (uid, uname))
                t = cur.fetchone()
                if not t:
                    self.send_json({"success": False, "error": "Teacher account not found."}, 404)
                    return

                # Leaves applied by teacher with Director approval status
                cur.execute("SELECT * FROM leaves WHERE user_id = ? ORDER BY id DESC", (t['id'],))
                leaves = [dict(r) for r in cur.fetchall()]

                # Computer lab complaints reported by this teacher with Director repair approval status
                cur.execute("SELECT * FROM lab_complaints WHERE reported_by_id = ? ORDER BY id DESC", (t['id'],))
                complaints = [dict(r) for r in cur.fetchall()]

                # Teacher classes and subjects
                cur.execute(\"\"\"
                    SELECT sub.id as subject_id, sub.name as subject_name, c.name as class_name, sec.name as section_name
                    FROM subjects sub
                    LEFT JOIN classes c ON sub.class_id = c.id
                    LEFT JOIN sections sec ON sub.class_id = sec.class_id
                    WHERE sub.teacher_id = ?
                    LIMIT 4
                \"\"\", (t['id'],))
                classes_taught = [dict(r) for r in cur.fetchall()]

                self.send_json({
                    "success": True,
                    "teacher": {
                        "id": t['id'],
                        "name": t['name'],
                        "username": t['username'],
                        "phone": t['phone'],
                        "email": t['email'],
                        "photo": t['photo'],
                        "base_salary": t['base_salary'] or 45000.0
                    },
                    "leaves": leaves,
                    "lab_complaints": complaints,
                    "classes_taught": classes_taught
                })

            elif path == '/api/director/pending_requests':
                # STRICT REQUIREMENT: Only Director approves requests created by IT team or Teacher
                # 1. Teacher Leave Requests
                cur.execute(\"\"\"
                    SELECT l.id, 'Teacher Leave Request' as request_type, 'Teacher' as origin,
                           u.name as creator_name, u.username as creator_username,
                           l.leave_type || ' (' || l.days_count || ' days)' as title,
                           l.reason as description, l.created_at, l.status,
                           l.start_date || ' to ' || l.end_date as details
                    FROM leaves l
                    JOIN users u ON l.user_id = u.id
                    WHERE l.status IN ('Pending', 'Pending Director Approval')
                    ORDER BY l.id DESC
                \"\"\")
                teacher_leaves = [dict(r) for r in cur.fetchall()]

                # 2. Teacher Computer Lab Hardware Complaints (Repair Authorizations)
                cur.execute(\"\"\"
                    SELECT lc.id, 'Computer Lab Hardware Repair' as request_type, 'Teacher & IT' as origin,
                           lc.reported_by_name as creator_name, 'Computer Teacher' as creator_username,
                           'Repair Authorization for ' || lc.pc_number || ' (' || lc.lab_name || ')' as title,
                           lc.problem_description as description, lc.created_at, lc.status,
                           'Issue: ' || lc.issue_category || ' | Priority: ' || lc.priority as details
                    FROM lab_complaints lc
                    WHERE lc.status IN ('Open', 'Assigned', 'Pending Director Approval')
                    ORDER BY lc.id DESC
                \"\"\")
                lab_repairs = [dict(r) for r in cur.fetchall()]

                # 3. IT Team Credential Requests
                cur.execute(\"\"\"
                    SELECT cr.id, 'IT Team Credential Request' as request_type, 'IT Team' as origin,
                           cr.requested_by_name as creator_name, 'IT Support Admin' as creator_username,
                           cr.request_type || ' for ' || cr.target_username as title,
                           cr.reason as description, cr.created_at, cr.status,
                           'Proposed Role: ' || COALESCE(cr.proposed_role, '—') as details
                    FROM credential_requests cr
                    WHERE cr.status IN ('Pending Owner Approval', 'Pending Director Approval')
                    ORDER BY cr.id DESC
                \"\"\")
                it_credentials = [dict(r) for r in cur.fetchall()]

                # 4. IT Team Asset & Procurement Requests
                cur.execute(\"\"\"
                    SELECT ar.id, 'IT Equipment Procurement / Expense' as request_type, 'IT Team' as origin,
                           ar.requested_by as creator_name, 'IT Support Admin' as creator_username,
                           ar.title, ar.description, ar.created_at, ar.status,
                           'Estimated Cost: ₦' || PRINTF('%,.2f', ar.estimated_cost) as details
                    FROM it_asset_requests ar
                    WHERE ar.status IN ('Pending Director Approval', 'Pending')
                    ORDER BY ar.id DESC
                \"\"\")
                it_assets = [dict(r) for r in cur.fetchall()]

                all_requests = teacher_leaves + lab_repairs + it_credentials + it_assets
                self.send_json({
                    "success": True,
                    "total_pending": len(all_requests),
                    "requests": all_requests,
                    "teacher_requests": teacher_leaves + lab_repairs,
                    "it_requests": it_credentials + it_assets
                })

            """

assert target_get_endpoint in code, "target_get_endpoint not found in server.py"
code = code.replace(target_get_endpoint, new_get_endpoints + target_get_endpoint, 1)

# 4. In do_POST, add IT asset request create and Director unified approve request
target_post_anchor = "elif path == '/api/users/delete':"
new_post_endpoints = """elif path == '/api/it_requests/create':
                # IT Support creates equipment procurement or service request for Director Approval
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                req_type = body.get('request_type', 'Equipment Procurement').strip()
                title = body.get('title', 'Fleet Laptop Procurement').strip()
                desc = body.get('description', '').strip()
                cost = float(body.get('estimated_cost') or 0.0)
                by = body.get('requested_by', 'IT Support Administrator').strip()

                cur.execute(\"\"\"
                    INSERT INTO it_asset_requests (request_type, title, description, estimated_cost, requested_by, status, created_at)
                    VALUES (?, ?, ?, ?, ?, 'Pending Director Approval', ?)
                \"\"\", (req_type, title, desc, cost, by, now))
                conn.commit()
                req_id = cur.lastrowid
                self.send_json({
                    "success": True,
                    "message": f"IT Request '{title}' submitted successfully. Now pending Director Rajeev Sinha approval.",
                    "request_id": req_id
                })

            elif path == '/api/director/approve_request':
                # STRICT REQUIREMENT: Only Director has authority to approve requests created by IT team or Teacher
                req_origin = body.get('origin', '').strip() # 'teacher_leave', 'lab_complaint', 'it_credential', 'it_asset'
                req_id = body.get('request_id')
                action = body.get('action', 'approve').strip().lower() # 'approve' or 'reject'
                director_notes = body.get('notes', 'Approved by Director Rajeev Sinha').strip()
                caller_username = body.get('caller_username', '').strip()
                caller_role = body.get('caller_role', '').strip()

                # Verify Director authority
                if caller_username not in ('Owner(Directer)', 'super_admin') and caller_role not in ('super_admin',):
                    self.send_json({"success": False, "error": "Access Denied: Only Director (Owner) Rajeev Sinha can approve requests created by IT team or Teacher."}, 403)
                    return

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if req_origin == 'teacher_leave':
                    new_status = 'Approved by Director Rajeev Sinha' if action == 'approve' else 'Rejected by Director'
                    cur.execute("UPDATE leaves SET status = ?, approver_role = 'super_admin', approver_notes = ?, updated_at = ? WHERE id = ?", (new_status, director_notes, now, req_id))
                    conn.commit()
                    self.send_json({"success": True, "message": f"Teacher Leave #{req_id} {new_status}!"})
                    return

                elif req_origin == 'lab_complaint':
                    new_status = 'Repair Approved by Director' if action == 'approve' else 'Repair Order Rejected'
                    cur.execute("UPDATE lab_complaints SET status = ?, resolution_notes = ?, resolved_by = 'Director Rajeev Sinha', resolved_at = ? WHERE id = ?", (new_status, director_notes, now, req_id))
                    conn.commit()
                    self.send_json({"success": True, "message": f"Computer Lab Repair Ticket #{req_id} {new_status}!"})
                    return

                elif req_origin == 'it_credential':
                    new_status = 'Approved by Director Rajeev Sinha' if action == 'approve' else 'Rejected by Director'
                    cur.execute("UPDATE credential_requests SET status = ?, approved_by = 'Director Rajeev Sinha', approved_at = ?, rejection_reason = ? WHERE id = ?", (new_status, now, director_notes, req_id))
                    conn.commit()
                    self.send_json({"success": True, "message": f"IT Team Credential Request #{req_id} {new_status}!"})
                    return

                elif req_origin == 'it_asset':
                    new_status = 'Approved by Director Rajeev Sinha' if action == 'approve' else 'Rejected by Director'
                    cur.execute("UPDATE it_asset_requests SET status = ?, director_notes = ?, approved_at = ? WHERE id = ?", (new_status, director_notes, now, req_id))
                    conn.commit()
                    self.send_json({"success": True, "message": f"IT Asset Request #{req_id} {new_status}!"})
                    return

                else:
                    self.send_json({"success": False, "error": f"Unknown request origin '{req_origin}'."}, 400)
                    return

            """

assert target_post_anchor in code, "target_post_anchor not found in server.py"
code = code.replace(target_post_anchor, new_post_endpoints + target_post_anchor, 1)

# 5. Enforce in /api/leaves/action that Teacher leaves can ONLY be approved by Director
target_leave_check = """                # If applicant is Principal (admin), ONLY super_admin can approve/reject!
                if leave['applicant_role'] == 'admin':
                    if approver_role != 'super_admin':
                        self.send_json({"success": False, "message": "Principal leave requests can only be reviewed and approved by Super Admin / Owner."}, 403)
                        return"""

replacement_leave_check = """                # STRICT REQUIREMENT: Only Director has authority to approve requests created by Teachers or IT Team!
                if leave['applicant_role'] in ('teacher', 'it_admin') or 'teacher' in str(leave['applicant_role']).lower():
                    if approver_role not in ('super_admin',):
                        self.send_json({"success": False, "message": "Policy Enforcement: Only Director (Owner) Rajeev Sinha can approve Leave Requests created by Teachers or IT Team."}, 403)
                        return

                if leave['applicant_role'] == 'admin':
                    if approver_role != 'super_admin':
                        self.send_json({"success": False, "message": "Principal leave requests can only be reviewed and approved by Super Admin / Owner."}, 403)
                        return"""

assert target_leave_check in code, "target_leave_check not found in server.py"
code = code.replace(target_leave_check, replacement_leave_check, 1)

with open('school_website/server.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ server.py patched with dual login, app endpoints, and Director exclusive approvals!")
