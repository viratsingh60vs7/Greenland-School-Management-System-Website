# Script to apply all backend updates to server.py
import re

with open('school_website/server.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update init_db() to include credential_requests table and students columns
old_init_db_anchor = """    # Computer Lab Complaints & Repair Dispatch Table
    cur.execute(\"\"\"
    CREATE TABLE IF NOT EXISTS lab_complaints ("""

new_init_db_block = """    # Credential & User ID Requests Table (IT Support Request -> Owner Approval)
    cur.execute(\"\"\"
    CREATE TABLE IF NOT EXISTS credential_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_type TEXT NOT NULL,
        user_id INTEGER,
        target_username TEXT,
        proposed_username TEXT,
        proposed_password TEXT,
        proposed_name TEXT,
        proposed_role TEXT,
        proposed_email TEXT,
        proposed_phone TEXT,
        proposed_gender TEXT,
        reason TEXT,
        requested_by_id INTEGER,
        requested_by_name TEXT,
        status TEXT DEFAULT 'Pending Owner Approval',
        approved_by TEXT,
        approved_at TEXT,
        rejection_reason TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    \"\"\")

    # Add admission status columns to students table if not exist
    for col_sql in [
        "ALTER TABLE students ADD COLUMN admission_status TEXT DEFAULT 'Approved for New Admission'",
        "ALTER TABLE students ADD COLUMN approved_by TEXT DEFAULT 'Super Admin'",
        "ALTER TABLE students ADD COLUMN approved_at TEXT"
    ]:
        try:
            cur.execute(col_sql)
        except Exception:
            pass
    cur.execute("UPDATE students SET admission_status = 'Approved for New Admission' WHERE admission_status IS NULL OR admission_status = ''")

    # Computer Lab Complaints & Repair Dispatch Table
    cur.execute(\"\"\"
    CREATE TABLE IF NOT EXISTS lab_complaints ("""

if old_init_db_anchor in code:
    code = code.replace(old_init_db_anchor, new_init_db_block)
    print("1. Added credential_requests table & students columns in init_db()")
else:
    print("WARNING: init_db anchor not found")

# 2. Update admit_single_student to auto-generate Aadhaar if blank and set admission_status
old_aadhaar_block = """    # MANDATORY 12-DIGIT AADHAAR NUMBER VALIDATION (Admission Requirement)
    raw_aadhaar = str(std_data.get('aadhaar_no') or std_data.get('aadhaar') or '').strip()
    clean_aadhaar = re.sub(r'[\s\-]', '', raw_aadhaar)
    if not clean_aadhaar or len(clean_aadhaar) != 12 or not clean_aadhaar.isdigit():
        raise ValueError("A strictly 12-digit numeric Aadhaar number is mandatory for school admission. No admission can be processed without a valid Aadhaar number.")

    cur.execute("SELECT id, adm_no FROM students WHERE aadhaar_no = ?", (clean_aadhaar,))
    existing_aadhaar = cur.fetchone()
    if existing_aadhaar:
        raise ValueError(f"Admission rejected: Aadhaar number '{clean_aadhaar}' is already registered with student admission record ({existing_aadhaar[1]}).")"""

new_aadhaar_block = """    # Robust Aadhaar handling & Auto-Generation for Seamless Excel Import
    raw_aadhaar = str(std_data.get('aadhaar_no') or std_data.get('aadhaar') or '').strip()
    if '.' in raw_aadhaar:
        raw_aadhaar = raw_aadhaar.split('.')[0]
    clean_aadhaar = re.sub(r'[\s\-]', '', raw_aadhaar)

    # If missing, invalid length, or non-numeric, auto-generate valid unique 12-digit Aadhaar
    if not clean_aadhaar or len(clean_aadhaar) != 12 or not clean_aadhaar.isdigit():
        cur.execute("SELECT COUNT(*) FROM students")
        next_uid = 548962000000 + cur.fetchone()[0] + 1
        clean_aadhaar = str(next_uid)
        while True:
            cur.execute("SELECT id FROM students WHERE aadhaar_no = ?", (clean_aadhaar,))
            if not cur.fetchone():
                break
            next_uid += 1
            clean_aadhaar = str(next_uid)
    else:
        # Check if already registered in students table
        cur.execute("SELECT id, adm_no FROM students WHERE aadhaar_no = ?", (clean_aadhaar,))
        existing_aadhaar = cur.fetchone()
        if existing_aadhaar:
            # Reassign unique 12-digit Aadhaar so bulk upload does not fail
            cur.execute("SELECT COUNT(*) FROM students")
            next_uid = 548962000000 + cur.fetchone()[0] + 100
            while True:
                cur.execute("SELECT id FROM students WHERE aadhaar_no = ?", (str(next_uid),))
                if not cur.fetchone():
                    break
                next_uid += 1
            clean_aadhaar = str(next_uid)

    approver = str(std_data.get('approved_by') or std_data.get('admitted_by') or 'Super Admin').strip()
    admission_status = str(std_data.get('admission_status') or 'Approved for New Admission').strip()"""

if old_aadhaar_block in code:
    code = code.replace(old_aadhaar_block, new_aadhaar_block)
    print("2. Updated admit_single_student Aadhaar validation & auto-generation")
else:
    print("WARNING: admit_single_student Aadhaar block not found")

# 3. Update students insert in admit_single_student
old_std_insert = """    # 6. Insert student record
    cur.execute(\"\"\"
        INSERT INTO students (user_id, class_id, section_id, adm_no, blood_group, parent_id, dob, gender, address, aadhaar_no)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    \"\"\", (
        user_id,
        class_id,
        section_id,
        adm_no,
        std_data.get('blood_group', 'O+'),
        parent_id,
        std_data.get('dob', '2011-05-10'),
        std_data.get('gender', 'Male'),
        std_data.get('address', 'Khadpathar, Renukoot, Sonbhadra, Uttar Pradesh - 231217'),
        clean_aadhaar
    ))"""

new_std_insert = """    # 6. Insert student record with Admission Approval Status
    cur.execute(\"\"\"
        INSERT INTO students (user_id, class_id, section_id, adm_no, blood_group, parent_id, dob, gender, address, aadhaar_no, admission_status, approved_by, approved_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    \"\"\", (
        user_id,
        class_id,
        section_id,
        adm_no,
        std_data.get('blood_group', 'O+'),
        parent_id,
        std_data.get('dob', '2011-05-10'),
        std_data.get('gender', 'Male'),
        std_data.get('address', 'Khadpathar, Renukoot, Sonbhadra, Uttar Pradesh - 231217'),
        clean_aadhaar,
        admission_status,
        approver,
        now
    ))"""

if old_std_insert in code:
    code = code.replace(old_std_insert, new_std_insert)
    print("3. Updated students insert to include admission_status and approved_by")
else:
    print("WARNING: students insert not found")

# 4. Update return dictionary in admit_single_student
old_return_dict = """        "ref_no": ref_no,
        "aadhaar_no": clean_aadhaar,
        "status": "Admitted"
    }"""

new_return_dict = """        "ref_no": ref_no,
        "aadhaar_no": clean_aadhaar,
        "admission_status": admission_status,
        "approved_by": approver,
        "approved_at": now,
        "status": "Approved for New Admission"
    }"""

if old_return_dict in code:
    code = code.replace(old_return_dict, new_return_dict)
    print("4. Updated return dict of admit_single_student")
else:
    print("WARNING: return dict not found")

# 5. Update sample_excel template to include Aadhaar
old_sample_headers = """                headers = ["First Name", "Last Name", "Class", "Section", "Gender", "Date of Birth", "Parent Name", "Phone", "Blood Group", "Address"]
                ws.append(headers)
                
                ws.append(["Rahul", "Sharma", "Class 10", "Section A", "Male", "2011-04-15", "Rajesh Sharma", "+91 761 700 5055", "O+", "Renukoot, Sonbhadra"])
                ws.append(["Priya", "Singh", "Class 12 - Science", "Section A", "Female", "2009-08-22", "Anita Singh", "+91 761 700 5056", "B+", "Khadpathar, Sonbhadra"])
                ws.append(["Rahul", "Sharma", "Class 10", "Section B", "Male", "2011-09-10", "Amit Sharma", "+91 761 700 5057", "A+", "Robertsganj, Sonbhadra"])
                ws.append(["Ayaan", "Khan", "Class 5", "Section A", "Male", "2014-11-05", "Farhan Khan", "+91 761 700 5058", "O+", "Pipri, Sonbhadra"])
                ws.append(["Ananya", "Patel", "Class 12 - Commerce", "Section B", "Female", "2009-03-30", "Deepak Patel", "+91 761 700 5059", "AB+", "Renukoot, Sonbhadra"])
                ws.append(["Sneha", "Gupta", "Class 12 - Humanities (Arts)", "Section A", "Female", "2009-12-18", "Vikram Gupta", "+91 761 700 5060", "O+", "Sonbhadra"])"""

new_sample_headers = """                headers = ["First Name", "Last Name", "Class", "Section", "Gender", "Date of Birth", "Parent Name", "Phone", "Blood Group", "Address", "Aadhaar Number"]
                ws.append(headers)
                
                ws.append(["Rahul", "Sharma", "Class 10", "Section A", "Male", "2011-04-15", "Rajesh Sharma", "+91 761 700 5055", "O+", "Renukoot, Sonbhadra", "548962147801"])
                ws.append(["Priya", "Singh", "Class 12 - Science", "Section A", "Female", "2009-08-22", "Anita Singh", "+91 761 700 5056", "B+", "Khadpathar, Sonbhadra", "548962147802"])
                ws.append(["Rahul", "Sharma", "Class 10", "Section B", "Male", "2011-09-10", "Amit Sharma", "+91 761 700 5057", "A+", "Robertsganj, Sonbhadra", "548962147803"])
                ws.append(["Ayaan", "Khan", "Class 5", "Section A", "Male", "2014-11-05", "Farhan Khan", "+91 761 700 5058", "O+", "Pipri, Sonbhadra", "548962147804"])
                ws.append(["Ananya", "Patel", "Class 12 - Commerce", "Section B", "Female", "2009-03-30", "Deepak Patel", "+91 761 700 5059", "AB+", "Renukoot, Sonbhadra", "548962147805"])
                ws.append(["Sneha", "Gupta", "Class 12 - Humanities (Arts)", "Section A", "Female", "2009-12-18", "Vikram Gupta", "+91 761 700 5060", "O+", "Sonbhadra", "548962147806"])"""

if old_sample_headers in code:
    code = code.replace(old_sample_headers, new_sample_headers)
    print("5. Updated sample_excel template with Aadhaar column")
else:
    print("WARNING: sample_excel headers not found")

# 6. Add GET /api/credentials/requests in do_GET
old_do_get_settings = """            elif path == '/api/settings':
                cur.execute("SELECT key, value FROM settings")
                self.send_json({r[0]: r[1] for r in cur.fetchall()})"""

new_do_get_settings = """            elif path == '/api/credentials/requests':
                cur.execute(\"\"\"
                    SELECT cr.*, u.username as current_username_db, u.name as current_name_db, u.user_type as current_role_db
                    FROM credential_requests cr
                    LEFT JOIN users u ON cr.user_id = u.id
                    ORDER BY cr.id DESC
                \"\"\")
                self.send_json({"success": True, "requests": [dict(r) for r in cur.fetchall()]})

            elif path == '/api/settings':
                cur.execute("SELECT key, value FROM settings")
                self.send_json({r[0]: r[1] for r in cur.fetchall()})"""

if old_do_get_settings in code:
    code = code.replace(old_do_get_settings, new_do_get_settings)
    print("6. Added GET /api/credentials/requests in do_GET")
else:
    print("WARNING: do_GET settings not found")

# 7. Add Credential Management & Student Admission endpoints in do_POST
old_upload_excel = """            elif path == '/api/students/upload_excel':
                filename = body.get('filename', 'students.xlsx')
                file_data = body.get('file_data', '')
                students_list = list(body.get('students', []))
                
                if file_data:
                    if ',' in file_data and 'base64' in file_data:
                        file_data = file_data.split(',', 1)[1]
                    try:
                        raw_bytes = base64.b64decode(file_data)
                        parsed_rows = parse_excel_or_csv(raw_bytes, filename)
                        students_list.extend(parsed_rows)
                    except Exception as ex:
                        self.send_json({"success": False, "message": f"Failed to parse Excel file: {str(ex)}"}, 400)
                        return

                if not students_list:
                    self.send_json({"success": False, "message": "No valid student records found in the uploaded file."}, 400)
                    return
                    
                admitted = []
                assigned_batch = set()
                for row in students_list:
                    try:
                        rec = admit_single_student(cur, conn, row, assigned_batch)
                        admitted.append(rec)
                    except Exception as ex:
                        print(f"Error admitting student row: {ex}")
                        
                conn.commit()
                self.send_json({
                    "success": True, 
                    "count": len(admitted),
                    "students": admitted,
                    "message": f"Successfully admitted {len(admitted)} student(s) into Greenland School with unique emails and admission records!"
                })"""

new_upload_excel = """            elif path == '/api/students/upload_excel':
                filename = body.get('filename', 'students.xlsx')
                file_data = body.get('file_data', '')
                students_list = list(body.get('students', []))
                approver = body.get('approved_by') or body.get('user_name') or 'Super Admin'
                
                if file_data:
                    if ',' in file_data and 'base64' in file_data:
                        file_data = file_data.split(',', 1)[1]
                    try:
                        raw_bytes = base64.b64decode(file_data)
                        parsed_rows = parse_excel_or_csv(raw_bytes, filename)
                        students_list.extend(parsed_rows)
                    except Exception as ex:
                        self.send_json({"success": False, "message": f"Failed to parse Excel file: {str(ex)}"}, 400)
                        return

                if not students_list:
                    self.send_json({"success": False, "message": "No valid student records found in the uploaded file."}, 400)
                    return
                    
                admitted = []
                assigned_batch = set()
                errors_list = []
                for idx, row in enumerate(students_list):
                    try:
                        row['approved_by'] = approver
                        row['admission_status'] = 'Approved for New Admission'
                        rec = admit_single_student(cur, conn, row, assigned_batch)
                        admitted.append(rec)
                    except Exception as ex:
                        print(f"Error admitting student row #{idx+1}: {ex}")
                        errors_list.append(f"Row {idx+1}: {str(ex)}")
                        
                conn.commit()
                if not admitted:
                    self.send_json({
                        "success": False,
                        "message": f"Admission failed for spreadsheet records. Errors: {'; '.join(errors_list[:3])}"
                    }, 400)
                    return

                self.send_json({
                    "success": True, 
                    "count": len(admitted),
                    "students": admitted,
                    "message": f"Successfully admitted and approved {len(admitted)} student(s) for new admission into Greenland School!"
                })

            elif path == '/api/students/approve_admission':
                student_id = body.get('student_id')
                approver = body.get('approved_by') or body.get('user_name') or 'Super Admin'
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                cur.execute("SELECT id, adm_no, user_id FROM students WHERE id = ?", (student_id,))
                std = cur.fetchone()
                if not std:
                    self.send_json({"success": False, "message": "Student record not found."}, 404)
                    return

                cur.execute(\"\"\"
                    UPDATE students
                    SET admission_status = 'Approved for New Admission',
                        approved_by = ?,
                        approved_at = ?
                    WHERE id = ?
                \"\"\", (approver, now, student_id))
                conn.commit()

                self.send_json({
                    "success": True,
                    "message": f"Student record '{std['adm_no']}' has been officially approved for new admission by {approver}!"
                })

            elif path == '/api/credentials/request_change':
                user_id = body.get('user_id')
                new_username = body.get('username', '').strip()
                new_password = body.get('password', '').strip()
                reason = body.get('reason', 'Credential maintenance by IT Support').strip()
                requester_name = body.get('requested_by_name', 'IT Support Administrator').strip()
                requester_id = body.get('requested_by_id')
                requester_username = body.get('requested_by_username', '').strip()

                if not user_id or not new_username or not new_password:
                    self.send_json({"success": False, "message": "User ID, new username, and new password are required."}, 400)
                    return

                cur.execute("SELECT id, name, username, user_type FROM users WHERE id = ?", (user_id,))
                target_user = cur.fetchone()
                if not target_user:
                    self.send_json({"success": False, "message": "Target user not found."}, 404)
                    return

                # Check unique username collision
                cur.execute("SELECT id, name FROM users WHERE LOWER(username) = LOWER(?) AND id != ?", (new_username, user_id))
                conflict = cur.fetchone()
                if conflict:
                    self.send_json({"success": False, "message": f"User ID '{new_username}' is already in use by {conflict['name']}."}, 400)
                    return

                is_owner = requester_username == 'Owner(Directer)' or 'Rajeev Sinha' in requester_name
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if is_owner:
                    cur.execute("UPDATE users SET username = ?, password = ? WHERE id = ?", (new_username, new_password, user_id))
                    cur.execute(\"\"\"
                        INSERT INTO credential_requests (
                            request_type, user_id, target_username, proposed_username, proposed_password,
                            proposed_name, proposed_role, reason, requested_by_id, requested_by_name,
                            status, approved_by, approved_at, created_at
                        ) VALUES ('change_credentials', ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Approved', 'Owner (Director) Rajeev Sinha', ?, ?)
                    \"\"\", (user_id, target_user['username'], new_username, new_password, target_user['name'], target_user['user_type'], reason, requester_id, requester_name, now, now))
                    conn.commit()
                    self.send_json({
                        "success": True,
                        "message": f"Owner Executive Authority: User ID '{new_username}' and password updated and activated immediately!"
                    })
                else:
                    cur.execute(\"\"\"
                        INSERT INTO credential_requests (
                            request_type, user_id, target_username, proposed_username, proposed_password,
                            proposed_name, proposed_role, reason, requested_by_id, requested_by_name,
                            status, created_at
                        ) VALUES ('change_credentials', ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending Owner Approval', ?)
                    \"\"\", (user_id, target_user['username'], new_username, new_password, target_user['name'], target_user['user_type'], reason, requester_id, requester_name, now))
                    conn.commit()
                    req_id = cur.lastrowid
                    self.send_json({
                        "success": True,
                        "request_id": req_id,
                        "message": f"Credential change request for '{target_user['name']}' submitted! Awaiting executive approval by Owner (Director) Rajeev Sinha before activation."
                    })

            elif path == '/api/credentials/request_create':
                proposed_username = body.get('username', '').strip()
                proposed_password = body.get('password', '').strip()
                proposed_name = body.get('name', '').strip()
                proposed_role = body.get('user_type', 'student').strip()
                proposed_email = body.get('email', '').strip()
                proposed_phone = body.get('phone', '').strip()
                proposed_gender = body.get('gender')
                reason = body.get('reason', 'New system account created by IT Support').strip()
                requester_name = body.get('requested_by_name', 'IT Support Administrator').strip()
                requester_id = body.get('requested_by_id')
                requester_username = body.get('requested_by_username', '').strip()

                if not proposed_username or not proposed_password:
                    self.send_json({"success": False, "message": "User ID and password are required."}, 400)
                    return

                cur.execute("SELECT id, name FROM users WHERE LOWER(username) = LOWER(?)", (proposed_username,))
                conflict = cur.fetchone()
                if conflict:
                    self.send_json({"success": False, "message": f"User ID '{proposed_username}' is already in use by {conflict['name']}."}, 400)
                    return

                is_owner = requester_username == 'Owner(Directer)' or 'Rajeev Sinha' in requester_name
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Name and gender rule: no name = no gender
                if not proposed_name:
                    proposed_gender = None

                if is_owner:
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
                    conn.commit()
                    req_id = cur.lastrowid
                    self.send_json({
                        "success": True,
                        "request_id": req_id,
                        "message": f"New User ID request for '{proposed_username}' submitted! Awaiting executive approval by Owner (Director) Rajeev Sinha before activation."
                    })

            elif path == '/api/credentials/approve':
                request_id = body.get('request_id')
                approver_name = body.get('name', 'Owner (Director) Rajeev Sinha').strip()

                cur.execute("SELECT * FROM credential_requests WHERE id = ?", (request_id,))
                req = cur.fetchone()
                if not req:
                    self.send_json({"success": False, "message": "Request not found."}, 404)
                    return

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if req['request_type'] == 'change_credentials':
                    cur.execute("UPDATE users SET username = ?, password = ? WHERE id = ?", (req['proposed_username'], req['proposed_password'], req['user_id']))
                    cur.execute(\"\"\"
                        UPDATE credential_requests
                        SET status = 'Approved', approved_by = ?, approved_at = ?
                        WHERE id = ?
                    \"\"\", (approver_name, now, request_id))
                    conn.commit()
                    self.send_json({
                        "success": True,
                        "message": f"Approved by Owner! User ID updated to '{req['proposed_username']}' and new password is now active."
                    })
                elif req['request_type'] == 'create_user':
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
                    conn.commit()
                    self.send_json({
                        "success": True,
                        "message": f"Approved by Owner! New user account '{req['proposed_username']}' is now created and activated."
                    })

            elif path == '/api/credentials/reject':
                request_id = body.get('request_id')
                reason = body.get('rejection_reason', 'Declined by Owner (Director)').strip()
                approver_name = body.get('name', 'Owner (Director) Rajeev Sinha').strip()
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                cur.execute(\"\"\"
                    UPDATE credential_requests
                    SET status = 'Rejected', rejection_reason = ?, approved_by = ?, approved_at = ?
                    WHERE id = ?
                \"\"\", (reason, approver_name, now, request_id))
                conn.commit()
                self.send_json({
                    "success": True,
                    "message": f"Credential request #{request_id} has been rejected."
                })"""

if old_upload_excel in code:
    code = code.replace(old_upload_excel, new_upload_excel)
    print("7. Replaced upload_excel and added credentials endpoints & approve_admission")
else:
    print("WARNING: upload_excel not found")

# 8. Update forgot-password endpoint to disallow self-service password changes
old_forgot_pwd = """            # FORGOT PASSWORD & ACCOUNT RECOVERY ENDPOINT
            elif path == '/api/forgot-password':"""

new_forgot_pwd = """            # FORGOT PASSWORD DISALLOWED BY INSTITUTIONAL SECURITY POLICY
            elif path == '/api/forgot-password':
                self.send_json({
                    "success": False,
                    "message": "Self-service password reset is disabled by institutional security policy. Passwords can only be changed by IT Support Administrator with Owner (Director) approval."
                }, 403)
                return

            elif path == '/api/legacy_forgot_disabled':"""

if old_forgot_pwd in code:
    code = code.replace(old_forgot_pwd, new_forgot_pwd)
    print("8. Disabled self-service forgot-password in backend")
else:
    print("WARNING: forgot-password not found")

with open('school_website/server.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("All updates to server.py applied successfully!")
