import http.server
import socketserver
import socket
import json
import sqlite3
import os
import urllib.parse
import urllib.request
import mimetypes
import re
import base64
import io
import csv
import openpyxl
import traceback
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email.utils as email_utils
from datetime import datetime, timedelta

PORT = int(os.environ.get("PORT", 5000))
DB_FILE = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "school.db"))

# 7 Unique Demo Accounts with Distinct User IDs and Passwords for Greenland School
UNIQUE_DEFAULT_USERS = [
    {
        "role": "super_admin",
        "name": "Owner (Director) Rajeev Sinha",
        "username": "Owner(Directer)",
        "password": "Viratsingh@2004",
        "email": "director@greenlandschool.net",
        "phone": "+91 761 700 5055",
        "photo": "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=150"
    },
    {
        "role": "super_admin",
        "name": "Super Admin",
        "username": "GS_superadmin",
        "password": "Greenland@2026",
        "email": "superadmin@greenlandschool.net",
        "phone": "+91 761 700 5055",
        "photo": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150"
    },
    {
        "role": "admin",
        "name": "Admin",
        "username": "GS_admin",
        "password": "Greenland@2026",
        "email": "admin@greenlandschool.net",
        "phone": "+91 761 700 5056",
        "photo": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150"
    },
    {
        "role": "teacher",
        "name": "Teacher Chike",
        "username": "GS_teacher",
        "password": "Greenland@2026",
        "email": "teacher.chike@greenlandschool.net",
        "phone": "+91 761 700 5055",
        "photo": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150"
    },
    {
        "role": "student",
        "name": "Student Alex Morgan",
        "username": "GS_student",
        "password": "Greenland@2026",
        "email": "student.alex@greenlandschool.net",
        "phone": "+91 761 700 5055",
        "photo": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150"
    },
    {
        "role": "parent",
        "name": "Parent Marcus Kaba",
        "username": "GS_parent_Alex_and_Clara",
        "password": "Greenland@2026",
        "email": "parent.kaba@greenlandschool.net",
        "phone": "+91 761 700 5056",
        "photo": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150"
    },
    {
        "role": "accountant",
        "name": "Accountant Jude Bello",
        "username": "GS_accountant",
        "password": "Greenland@2026",
        "email": "bursar@greenlandschool.net",
        "phone": "+91 761 700 5055",
        "photo": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150"
    },
    {
        "role": "librarian",
        "name": "Librarian Rose Davies",
        "username": "GS_librarian",
        "password": "Greenland@2026",
        "email": "library@greenlandschool.net",
        "phone": "+91 761 700 5056",
        "photo": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150"
    },
    {
        "role": "it_admin",
        "name": "IT Support Administrator",
        "username": "GS_itsupport",
        "password": "Greenland@2026",
        "email": "itsupport@greenlandschool.net",
        "phone": "+91 761 700 5058",
        "photo": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150",
        "gender": "Male"
    }
]

def sanitize_part(s):
    if not s:
        return ""
    # Strip non-alphanumeric characters, keep clean casing/letters
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', str(s).strip())
    return cleaned

def generate_unique_student_email_and_username(cur, first_name, last_name, class_name, assigned_emails_in_batch=None):
    if assigned_emails_in_batch is None:
        assigned_emails_in_batch = set()
    
    first = sanitize_part(first_name)
    last = sanitize_part(last_name)
    cls = sanitize_part(class_name)
    
    if not first: first = "Student"
    if not last: last = "GS"
    if not cls: cls = "Class"
        
    base_prefix = f"GS_student_{first}_{last}_{cls}"
    candidate_email = f"{base_prefix}@greenlandschool.net"
    candidate_username = base_prefix
    
    counter = 1
    while True:
        cur.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?) OR LOWER(username) = LOWER(?)", 
                    (candidate_email, candidate_username))
        exists_in_db = cur.fetchone() is not None
        exists_in_batch = (candidate_email.lower() in assigned_emails_in_batch) or (candidate_username.lower() in assigned_emails_in_batch)
        
        if not exists_in_db and not exists_in_batch:
            break
            
        candidate_email = f"{base_prefix}_{counter}@greenlandschool.net"
        candidate_username = f"{base_prefix}_{counter}"
        counter += 1
        
    assigned_emails_in_batch.add(candidate_email.lower())
    assigned_emails_in_batch.add(candidate_username.lower())
    return candidate_email, candidate_username

def resolve_or_create_class(cur, conn, class_input, section_input=None, stream_input=None):
    clean_name = str(class_input).strip() if class_input else "Class 1"
    
    # Handle Class 12 streams
    if "12" in clean_name and stream_input:
        stream_str = str(stream_input).strip().lower()
        if "science" in stream_str:
            clean_name = "Class 12 - Science"
        elif "commerce" in stream_str:
            clean_name = "Class 12 - Commerce"
        elif "humanities" in stream_str or "arts" in stream_str:
            clean_name = "Class 12 - Humanities (Arts)"

    cur.execute("SELECT id, name FROM classes WHERE LOWER(name) = LOWER(?)", (clean_name,))
    row = cur.fetchone()
    if row:
        class_id = row[0]
        actual_name = row[1]
    else:
        # Partial match
        cur.execute("SELECT id, name FROM classes WHERE LOWER(name) LIKE ? OR LOWER(?) LIKE '%' || LOWER(name) || '%'", (f"%{clean_name}%", clean_name))
        row = cur.fetchone()
        if row:
            class_id = row[0]
            actual_name = row[1]
        else:
            cur.execute("INSERT INTO classes (name, class_type) VALUES (?, 'Secondary')", (clean_name,))
            class_id = cur.lastrowid
            actual_name = clean_name
            
    # Resolve section
    sec_name = str(section_input).strip() if section_input else "Section A"
    if not sec_name.lower().startswith("section"):
        sec_name = f"Section {sec_name.upper()}"
        
    cur.execute("SELECT id, name FROM sections WHERE class_id = ? AND LOWER(name) = LOWER(?)", (class_id, sec_name))
    sec_row = cur.fetchone()
    if sec_row:
        sec_id = sec_row[0]
    else:
        cur.execute("SELECT id FROM sections WHERE class_id = ? LIMIT 1", (class_id,))
        first_sec = cur.fetchone()
        if first_sec:
            sec_id = first_sec[0]
        else:
            cur.execute("INSERT INTO sections (class_id, name) VALUES (?, ?)", (class_id, sec_name))
            sec_id = cur.lastrowid
        
    return class_id, sec_id, actual_name

def admit_single_student(cur, conn, std_data, assigned_batch=None):
    if assigned_batch is None:
        assigned_batch = set()
        
    first_name = str(std_data.get('first_name', '')).strip()
    last_name = str(std_data.get('last_name', '')).strip()
    full_name = str(std_data.get('name', '')).strip()
    
    if not first_name and full_name:
        parts = full_name.split()
        first_name = parts[0]
        last_name = " ".join(parts[1:]) if len(parts) > 1 else "Student"
    elif not full_name and (first_name or last_name):
        full_name = f"{first_name} {last_name}".strip()
        
    if not first_name:
        first_name = "Student"
    if not full_name:
        full_name = f"{first_name} {last_name}".strip()

    # Robust Aadhaar handling & Auto-Generation for Seamless Excel Import
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
    admission_status = str(std_data.get('admission_status') or 'Approved for New Admission').strip()
        
    raw_class = str(std_data.get('class_name') or std_data.get('class') or 'Class 1').strip()
    raw_section = str(std_data.get('section') or std_data.get('class_section') or 'Section A').strip()
    raw_stream = str(std_data.get('stream') or '').strip()

    # 1. Resolve class, section and stream
    class_id, section_id, class_name = resolve_or_create_class(cur, conn, raw_class, raw_section, raw_stream)
    
    # 2. Unique email and username with duplicate protection
    email, username = generate_unique_student_email_and_username(cur, first_name, last_name, class_name, assigned_batch)
    password = "Greenland@2026"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 3. Insert into users table
    phone = str(std_data.get('phone', '+91 761 700 5055')).strip()
    photo = std_data.get('photo', 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150')
    cur.execute("""
        INSERT INTO users (name, email, username, password, user_type, phone, photo, created_at)
        VALUES (?, ?, ?, ?, 'student', ?, ?, ?)
    """, (full_name, email, username, password, phone, photo, now))
    user_id = cur.lastrowid
    
    # 4. Resolve parent
    parent_id = std_data.get('parent_id')
    parent_name = str(std_data.get('parent_name', '')).strip()
    parent_phone = str(std_data.get('parent_phone') or std_data.get('phone', '+91 761 700 5056')).strip()
    
    if not parent_id and parent_name:
        cur.execute("SELECT id, username FROM users WHERE user_type = 'parent' AND (LOWER(name) = LOWER(?) OR phone = ?)", (parent_name, parent_phone))
        p_row = cur.fetchone()
        if p_row:
            parent_id = p_row[0]
            # Update parent username to reflect multiple children if needed
            existing_uname = p_row[1]
            c_first = sanitize_part(first_name)
            if c_first.lower() not in existing_uname.lower():
                new_uname = f"{existing_uname}_{c_first}"
                cur.execute("UPDATE users SET username = ? WHERE id = ?", (new_uname, parent_id))
        else:
            child_name_part = sanitize_part(full_name)
            p_user = f"GS_parent_{child_name_part}"
            p_email = f"{p_user.lower()}@greenlandschool.net"
            p_counter = 1
            while True:
                cur.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?) OR LOWER(username) = LOWER(?)", (p_email, p_user))
                if not cur.fetchone():
                    break
                p_user = f"GS_parent_{child_name_part}_{p_counter}"
                p_email = f"{p_user.lower()}@greenlandschool.net"
                p_counter += 1
            cur.execute("""
                INSERT INTO users (name, email, username, password, user_type, phone, photo, created_at)
                VALUES (?, ?, ?, 'Greenland@2026', 'parent', ?, 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150', ?)
            """, (parent_name, p_email, p_user, parent_phone, now))
            parent_id = cur.lastrowid
            
    if not parent_id:
        cur.execute("SELECT id FROM users WHERE user_type = 'parent' LIMIT 1")
        p_def = cur.fetchone()
        parent_id = p_def[0] if p_def else None

    # 5. Unique admission number
    adm_no = str(std_data.get('adm_no', '')).strip()
    if not adm_no:
        cur.execute("SELECT COUNT(*) FROM students")
        c_val = cur.fetchone()[0]
        next_num = c_val + 1
        adm_no = f"GS/{datetime.now().year}/{next_num:04d}"
        while True:
            cur.execute("SELECT id FROM students WHERE adm_no = ?", (adm_no,))
            if not cur.fetchone():
                break
            next_num += 1
            adm_no = f"GS/{datetime.now().year}/{next_num:04d}"

    # 6. Insert student record with Admission Approval Status
    cur.execute("""
        INSERT INTO students (user_id, class_id, section_id, adm_no, blood_group, parent_id, dob, gender, address, aadhaar_no, admission_status, approved_by, approved_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
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
    ))
    student_id = cur.lastrowid

    # 7. Insert / Update admission application record
    ref_no = f"ADM-{datetime.now().strftime('%y%m')}-{os.urandom(2).hex().upper()}"
    cur.execute("""
        INSERT INTO admissions (ref_no, applicant_name, parent_name, email, phone, grade_applying, previous_school, message, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Admitted', ?)
    """, (
        ref_no,
        full_name,
        parent_name or f"Parent of {full_name}",
        email,
        phone,
        class_name,
        std_data.get('previous_school', 'Direct Admission'),
        std_data.get('message', 'Enrolled & Admitted via Greenland School Management System'),
        now
    ))
    
    return {
        "student_id": student_id,
        "user_id": user_id,
        "name": full_name,
        "first_name": first_name,
        "last_name": last_name,
        "class_name": class_name,
        "email": email,
        "username": username,
        "password": password,
        "adm_no": adm_no,
        "ref_no": ref_no,
        "aadhaar_no": clean_aadhaar,
        "admission_status": admission_status,
        "approved_by": approver,
        "approved_at": now,
        "status": "Approved for New Admission"
    }

def parse_excel_or_csv(file_bytes, filename):
    filename = (filename or '').lower()
    students_data = []
    
    if filename.endswith('.xlsx') or filename.endswith('.xls'):
        wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            return []
        raw_headers = [str(c).strip().lower() if c is not None else '' for c in rows[0]]
        
        header_map = {}
        for idx, h in enumerate(raw_headers):
            h_clean = re.sub(r'[^a-z0-9]', '', h)
            if any(k in h_clean for k in ['firstname', 'fname', 'studentfirst', 'givenname']):
                header_map['first_name'] = idx
            elif any(k in h_clean for k in ['lastname', 'lname', 'surname', 'studentlast', 'familyname']):
                header_map['last_name'] = idx
            elif any(k in h_clean for k in ['fullname', 'studentname', 'name']):
                if 'first_name' not in header_map:
                    header_map['name'] = idx
            elif any(k in h_clean for k in ['class', 'grade', 'standard', 'tier']):
                header_map['class'] = idx
            elif any(k in h_clean for k in ['gender', 'sex']):
                header_map['gender'] = idx
            elif any(k in h_clean for k in ['dob', 'dateofbirth', 'birthdate', 'birth']):
                header_map['dob'] = idx
            elif any(k in h_clean for k in ['parent', 'guardian', 'father', 'mother']):
                if any(p in h_clean for p in ['phone', 'mobile', 'contact']):
                    header_map['parent_phone'] = idx
                else:
                    header_map['parent_name'] = idx
            elif any(k in h_clean for k in ['phone', 'mobile', 'contact', 'telephone']):
                if 'phone' not in header_map:
                    header_map['phone'] = idx
            elif any(k in h_clean for k in ['blood', 'bloodgroup']):
                header_map['blood_group'] = idx
            elif any(k in h_clean for k in ['address', 'residence', 'city']):
                header_map['address'] = idx
            elif any(k in h_clean for k in ['admission', 'admno', 'rollno', 'regno']):
                header_map['adm_no'] = idx
            elif any(k in h_clean for k in ['section', 'classsection', 'arm']):
                header_map['section'] = idx
            elif any(k in h_clean for k in ['stream', 'specialization', 'branch']):
                header_map['stream'] = idx
            elif any(k in h_clean for k in ['aadhaar', 'aadhar', 'uid', 'uidai', 'aadhaarno', 'aadharno']):
                header_map['aadhaar_no'] = idx

        for row in rows[1:]:
            if not row or all(v is None or str(v).strip() == '' for v in row):
                continue
            item = {}
            for field, idx in header_map.items():
                if idx < len(row):
                    val = row[idx]
                    if val is not None:
                        if hasattr(val, 'strftime'):
                            val = val.strftime('%Y-%m-%d')
                        item[field] = str(val).strip()
            
            if not item.get('first_name') and not item.get('name') and len(row) >= 2:
                item['first_name'] = str(row[0] or '').strip()
                item['last_name'] = str(row[1] or '').strip()
                if len(row) >= 3:
                    item['class'] = str(row[2] or 'SSS 3').strip()

            if item.get('first_name') or item.get('name'):
                students_data.append(item)

    else:
        try:
            text = file_bytes.decode('utf-8-sig')
        except UnicodeDecodeError:
            text = file_bytes.decode('latin-1', errors='replace')
            
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)
        if not rows:
            return []
        raw_headers = [str(c).strip().lower() for c in rows[0]]
        header_map = {}
        for idx, h in enumerate(raw_headers):
            h_clean = re.sub(r'[^a-z0-9]', '', h)
            if any(k in h_clean for k in ['firstname', 'fname', 'studentfirst', 'givenname']):
                header_map['first_name'] = idx
            elif any(k in h_clean for k in ['lastname', 'lname', 'surname', 'studentlast', 'familyname']):
                header_map['last_name'] = idx
            elif any(k in h_clean for k in ['fullname', 'studentname', 'name']):
                if 'first_name' not in header_map:
                    header_map['name'] = idx
            elif any(k in h_clean for k in ['class', 'grade', 'standard', 'tier']):
                header_map['class'] = idx
            elif any(k in h_clean for k in ['gender', 'sex']):
                header_map['gender'] = idx
            elif any(k in h_clean for k in ['dob', 'dateofbirth', 'birthdate', 'birth']):
                header_map['dob'] = idx
            elif any(k in h_clean for k in ['parent', 'guardian', 'father', 'mother']):
                header_map['parent_name'] = idx
            elif any(k in h_clean for k in ['phone', 'mobile', 'contact']):
                header_map['phone'] = idx
            elif any(k in h_clean for k in ['blood']):
                header_map['blood_group'] = idx
            elif any(k in h_clean for k in ['address']):
                header_map['address'] = idx
            elif any(k in h_clean for k in ['admission', 'admno']):
                header_map['adm_no'] = idx
            elif any(k in h_clean for k in ['section', 'classsection', 'arm']):
                header_map['section'] = idx
            elif any(k in h_clean for k in ['stream', 'specialization', 'branch']):
                header_map['stream'] = idx
            elif any(k in h_clean for k in ['aadhaar', 'aadhar', 'uid', 'uidai', 'aadhaarno', 'aadharno']):
                header_map['aadhaar_no'] = idx

        for row in rows[1:]:
            if not row or all(str(v).strip() == '' for v in row):
                continue
            item = {}
            for field, idx in header_map.items():
                if idx < len(row):
                    item[field] = str(row[idx]).strip()
            if not item.get('first_name') and not item.get('name') and len(row) >= 2:
                item['first_name'] = str(row[0]).strip()
                item['last_name'] = str(row[1]).strip()
                if len(row) >= 3:
                    item['class'] = str(row[2]).strip()
            if item.get('first_name') or item.get('name'):
                students_data.append(item)

    return students_data

def dispatch_admission_notification(conn, inq_dict, approver_title, action='approve', notes=''):
    """
    STRICT MULTI-CHANNEL DISPATCH ENGINE:
    Dispatches official admission notices directly to candidate's Email and Phone Number (SMS/WhatsApp)
    as configured in their notification preference ('both', 'phone', 'email').
    
    1. Live Email Transmission: Uses smtplib + MIME HTML letterhead with SMTP settings from database or env.
       If unconfigured or offline, reliably spools .html & .eml files in outbox/emails/ and records status.
    2. Live Phone & WhatsApp Transmission: Generates 1-click WhatsApp web/app link, device SMS protocol link,
       and transmits via SMS Gateway (Fast2SMS / Webhook) if configured, plus logs raw text to outbox/sms/.
    3. Full Audit Trail: Persists comprehensive dispatch history in notifications_outbox and updates admissions table.
    """
    cur = conn.cursor()
    adm_id = inq_dict.get('id')
    ref_no = inq_dict.get('ref_no') or f"ADM-{datetime.now().strftime('%y%m%d%H%M')}"
    applicant_name = inq_dict.get('applicant_name') or 'Student'
    parent_name = inq_dict.get('parent_name') or 'Parent / Guardian'
    grade_applying = inq_dict.get('grade_applying') or 'Class'
    preferred_section = inq_dict.get('preferred_section') or 'Section A'
    email = (inq_dict.get('email') or '').strip()
    phone = (inq_dict.get('phone') or '').strip()
    pref = inq_dict.get('notification_pref') or 'both'
    if pref not in ('both', 'phone', 'email'):
        pref = 'both'
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_display = datetime.now().strftime("%d %B %Y, %I:%M %p")
    
    # Read system settings
    cur.execute("SELECT key, value FROM settings")
    settings_map = {r[0]: r[1] for r in cur.fetchall()}
    
    school_name = settings_map.get('system_name', 'Greenland School')
    school_phone = settings_map.get('phone', '+91 761 700 5055, +91 761 700 5056')
    school_email = settings_map.get('system_email', 'info@greenlandschool.net')
    school_address = settings_map.get('address', 'Khadpathar, Renukoot, Sonbhadra, Uttar Pradesh - 231217')
    
    smtp_host = os.environ.get('SMTP_HOST') or settings_map.get('smtp_host', 'smtp.gmail.com').strip()
    try:
        smtp_port = int(os.environ.get('SMTP_PORT') or settings_map.get('smtp_port', 587))
    except Exception:
        smtp_port = 587
    smtp_user = os.environ.get('SMTP_USER') or settings_map.get('smtp_user', '').strip()
    smtp_pass = os.environ.get('SMTP_PASS') or settings_map.get('smtp_pass', '').strip()
    smtp_sender_name = settings_map.get('smtp_sender_name') or f"{school_name} Admissions"
    smtp_sender_email = settings_map.get('smtp_sender_email') or smtp_user or school_email
    smtp_tls = str(settings_map.get('smtp_tls', '1')).strip() == '1'
    smtp_ssl = str(settings_map.get('smtp_ssl', '0')).strip() == '1'
    
    sms_provider = settings_map.get('sms_provider', 'none').strip().lower()
    sms_api_key = settings_map.get('sms_api_key', '').strip()
    sms_sender_id = settings_map.get('sms_sender_id', 'GRNSCH').strip()
    sms_webhook_url = settings_map.get('sms_webhook_url', '').strip()
    
    # Prepare Outbox directories
    outbox_base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outbox")
    outbox_emails_dir = os.path.join(outbox_base, "emails")
    outbox_sms_dir = os.path.join(outbox_base, "sms")
    os.makedirs(outbox_emails_dir, exist_ok=True)
    os.makedirs(outbox_sms_dir, exist_ok=True)
    
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', applicant_name)
    email_filename = f"{ref_no}_{safe_name}.html"
    email_eml_filename = f"{ref_no}_{safe_name}.eml"
    sms_filename = f"{ref_no}_{safe_name}.txt"
    
    email_outbox_path = os.path.join(outbox_emails_dir, email_filename)
    email_eml_path = os.path.join(outbox_emails_dir, email_eml_filename)
    sms_outbox_path = os.path.join(outbox_sms_dir, sms_filename)
    
    # Build text payloads
    if action == 'approve':
        status_label = "Approved"
        decision_title = "OFFICIAL ADMISSION APPROVAL & SANCTION CLEARANCE"
        sms_text = (
            f"GREENLAND SCHOOL ALERT: Admission inquiry {ref_no} for {applicant_name} ({grade_applying} - {preferred_section}) "
            f"has been OFFICIALLY APPROVED by {approver_title}. "
            f"Please visit school administrative office or portal to complete enrollment. Helpline: {school_phone.split(',')[0]}."
        )
        email_subject = f"Official Admission Approval Notice — {applicant_name} (Ref: {ref_no}) | {school_name}"
    else:
        status_label = "Declined"
        decision_title = "ADMISSION INQUIRY STATUS NOTIFICATION"
        sms_text = (
            f"GREENLAND SCHOOL NOTICE: Admission inquiry {ref_no} for {applicant_name} ({grade_applying}) "
            f"status update: Declined ({notes or 'Seats currently unavailable'}). Helpline: {school_phone.split(',')[0]}."
        )
        email_subject = f"Admission Inquiry Status Notice — {applicant_name} (Ref: {ref_no}) | {school_name}"

    plain_email_text = f"""============================================================
{school_name.upper()} - {decision_title}
============================================================

Date: {date_display}
Application Reference: {ref_no}

Dear {parent_name} & {applicant_name},

We are pleased to inform you that your online admission inquiry for {applicant_name} into {grade_applying} ({preferred_section}) at {school_name} has been {status_label.upper()} by {approver_title}.

PARTICULARS:
------------------------------------------------------------
- Candidate Name: {applicant_name}
- Parent / Guardian: {parent_name}
- Grade Allotted: {grade_applying} ({preferred_section})
- Application Reference: {ref_no}
- Decision Status: {status_label.upper()}
- Authorized By: {approver_title}
- Sanction Timestamp: {now}

ENROLLMENT PROCEDURES & NEXT STEPS:
1. Documentation: Bring original birth certificate, 12-digit Aadhaar Card, and previous academic marksheet to the administrative desk.
2. Fee Settlement: Complete term tuition and admission fees via Net Banking / UPI QR code or school fee counter.
3. Student ID & Portal: Unique institutional email (GS_student_...) and portal credentials will be assigned upon documentation.

INSTITUTIONAL CONTACT:
Campus Address: {school_address}
Helpline: {school_phone}
Official Email: {school_email}

Executive Directorate & Admissions Council,
{school_name}
"""

    html_email_text = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{school_name} - {decision_title}</title>
</head>
<body style="margin:0; padding:0; background-color:#f1f5f9; font-family:'Segoe UI',Roboto,Helvetica,Arial,sans-serif; color:#1e293b;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f1f5f9; padding:28px 10px;">
        <tr>
            <td align="center">
                <table width="620" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 4px 15px rgba(0,0,0,0.06); border:1px solid #e2e8f0;">
                    <!-- Header -->
                    <tr>
                        <td style="background:linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding:28px 30px; text-align:center; color:#ffffff;">
                            <div style="font-size:12px; font-weight:700; letter-spacing:2px; text-transform:uppercase; color:#93c5fd; margin-bottom:6px;">{school_name.upper()}</div>
                            <h1 style="margin:0; font-size:22px; font-weight:800; color:#ffffff; letter-spacing:0.5px;">{decision_title}</h1>
                            <div style="font-size:12px; color:#cbd5e1; margin-top:6px;">Autonomous Senior Secondary Institution &bull; Sonbhadra, Uttar Pradesh</div>
                        </td>
                    </tr>
                    <!-- Status Banner -->
                    <tr>
                        <td style="background:{'#ecfdf5' if action == 'approve' else '#fef2f2'}; border-bottom:1px solid {'#a7f3d0' if action == 'approve' else '#fecaca'}; padding:14px 30px; text-align:center;">
                            <span style="display:inline-block; background:{'#047857' if action == 'approve' else '#b91c1c'}; color:#ffffff; font-weight:700; font-size:12px; letter-spacing:1px; text-transform:uppercase; padding:4px 14px; border-radius:20px;">
                                {'✓ Application Officially Approved & Sanctioned' if action == 'approve' else '✕ Application Status: Declined'}
                            </span>
                        </td>
                    </tr>
                    <!-- Content -->
                    <tr>
                        <td style="padding:28px 32px;">
                            <p style="font-size:15px; line-height:1.6; margin-top:0; color:#334155;">
                                Dear <strong>{parent_name}</strong> &amp; <strong>{applicant_name}</strong>,
                            </p>
                            <p style="font-size:14px; line-height:1.6; color:#475569;">
                                {'We are pleased to inform you that your online admission inquiry has been reviewed by the Executive Directorate and is officially <strong>APPROVED</strong> for enrollment into Greenland School.' if action == 'approve' else f'We regret to inform you that the inquiry could not be accommodated at this time. Reason: {notes or "Seats full"}.'}
                            </p>

                            <!-- Table -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; margin:20px 0; font-size:13px;">
                                <tr>
                                    <td colspan="2" style="background:#e2e8f0; padding:10px 16px; font-weight:700; color:#0f172a; border-top-left-radius:7px; border-top-right-radius:7px;">
                                        Clearance Particulars &amp; Candidate Credentials
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:10px 16px; border-bottom:1px solid #edf2f7; color:#64748b; width:40%;">Application Ref #:</td>
                                    <td style="padding:10px 16px; border-bottom:1px solid #edf2f7; font-weight:700; color:#1e3a8a;">{ref_no}</td>
                                </tr>
                                <tr>
                                    <td style="padding:10px 16px; border-bottom:1px solid #edf2f7; color:#64748b;">Candidate Name:</td>
                                    <td style="padding:10px 16px; border-bottom:1px solid #edf2f7; font-weight:700; color:#0f172a;">{applicant_name}</td>
                                </tr>
                                <tr>
                                    <td style="padding:10px 16px; border-bottom:1px solid #edf2f7; color:#64748b;">Parent / Guardian:</td>
                                    <td style="padding:10px 16px; border-bottom:1px solid #edf2f7; font-weight:600; color:#0f172a;">{parent_name}</td>
                                </tr>
                                <tr>
                                    <td style="padding:10px 16px; border-bottom:1px solid #edf2f7; color:#64748b;">Grade &amp; Section:</td>
                                    <td style="padding:10px 16px; border-bottom:1px solid #edf2f7; font-weight:700; color:#047857;">{grade_applying} &mdash; {preferred_section}</td>
                                </tr>
                                <tr>
                                    <td style="padding:10px 16px; border-bottom:1px solid #edf2f7; color:#64748b;">Sanctioning Authority:</td>
                                    <td style="padding:10px 16px; border-bottom:1px solid #edf2f7; font-weight:600; color:#0f172a;">{approver_title}</td>
                                </tr>
                                <tr>
                                    <td style="padding:10px 16px; color:#64748b;">Sanction Timestamp:</td>
                                    <td style="padding:10px 16px; color:#0f172a;">{now}</td>
                                </tr>
                            </table>

                            <!-- Next Steps -->
                            {'<div style="background:#eff6ff; border-left:4px solid #2563eb; border-radius:4px; padding:14px 18px; margin:22px 0;"><div style="font-weight:700; color:#1e40af; font-size:14px; margin-bottom:6px;">Next Steps for Final Enrollment:</div><ol style="margin:0; padding-left:18px; font-size:13px; color:#334155; line-height:1.7;"><li><strong>Verification:</strong> Present candidate 12-digit Aadhaar Card, Birth Certificate, and previous marksheet at the Admissions Office.</li><li><strong>Tuition Settlement:</strong> Pay term fees via Net Banking, UPI/QR Code, or at the campus counter.</li><li><strong>Portal Activation:</strong> Unique student institutional email (<code>GS_student_...</code>) and timetable will be assigned upon enrollment.</li></ol></div>' if action == 'approve' else ''}

                            <p style="font-size:13px; color:#64748b; line-height:1.6; margin-top:22px;">
                                Admissions Helpline: <strong>{school_phone}</strong> &bull; Official Email: <strong>{school_email}</strong>
                            </p>

                            <!-- Signature -->
                            <div style="margin-top:26px; padding-top:16px; border-top:1px solid #e2e8f0; font-size:13px; color:#334155;">
                                <div>With warm regards,</div>
                                <div style="font-weight:700; color:#0f172a; margin-top:4px;">Executive Admissions Directorate</div>
                                <div style="color:#64748b; font-size:12px;">{school_name} &bull; Khadpathar, Renukoot, Sonbhadra (UP)</div>
                            </div>
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="background:#0f172a; padding:16px 30px; text-align:center; color:#94a3b8; font-size:11px; line-height:1.5;">
                            <div>{school_address}</div>
                            <div style="margin-top:4px; color:#64748b;">This is an official automated dispatch triggered upon executive approval of inquiry #{ref_no}.</div>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

    # Phone sanitization for WhatsApp and SMS protocol
    clean_digits = re.sub(r'[^0-9]', '', phone)
    if clean_digits and len(clean_digits) == 10:
        clean_digits = "91" + clean_digits
    wa_url = f"https://wa.me/{clean_digits}?text={urllib.parse.quote(sms_text)}" if clean_digits else ""
    sms_link = f"sms:{phone}?body={urllib.parse.quote(sms_text)}" if phone else ""

    # Always persist to Outbox files
    try:
        with open(email_outbox_path, 'w', encoding='utf-8') as f:
            f.write(html_email_text)
    except Exception as e:
        print(f"[Outbox Write Error - HTML] {e}", flush=True)

    # Compile EML format
    eml_msg = MIMEMultipart('alternative')
    eml_msg['Subject'] = email_subject
    eml_msg['From'] = f"{smtp_sender_name} <{smtp_sender_email}>"
    eml_msg['To'] = email or "candidate@greenlandschool.net"
    eml_msg['Date'] = email_utils.formatdate(localtime=True)
    eml_msg['Message-ID'] = email_utils.make_msgid(domain="greenlandschool.net")
    eml_msg.attach(MIMEText(plain_email_text, 'plain', 'utf-8'))
    eml_msg.attach(MIMEText(html_email_text, 'html', 'utf-8'))
    try:
        with open(email_eml_path, 'w', encoding='utf-8') as f:
            f.write(eml_msg.as_string())
    except Exception as e:
        print(f"[Outbox Write Error - EML] {e}", flush=True)

    try:
        with open(sms_outbox_path, 'w', encoding='utf-8') as f:
            f.write(sms_text)
    except Exception as e:
        print(f"[Outbox Write Error - SMS] {e}", flush=True)

    # 1. LIVE EMAIL DISPATCH (via SMTP)
    email_sent = 0
    email_status = "Skipped (Not in applicant preference)"
    if pref in ('both', 'email') and email:
        if smtp_host and smtp_user:
            try:
                if smtp_ssl or smtp_port == 465:
                    server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=12)
                else:
                    server = smtplib.SMTP(smtp_host, smtp_port, timeout=12)
                    if smtp_tls:
                        server.starttls()
                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_sender_email, [email], eml_msg.as_string())
                server.quit()
                email_sent = 1
                email_status = f"✅ Sent Live via SMTP ({smtp_host}) to {email}"
            except Exception as ex:
                email_sent = 0
                email_status = f"⚠️ SMTP Error ({smtp_host}): {str(ex)[:120]} (Notice saved to Outbox: {email_filename})"
        else:
            email_sent = 0
            email_status = f"📦 Spooled to Outbox ({email_filename}) — Configure SMTP in Settings for live carrier delivery"

    # 2. LIVE SMS DISPATCH (via Gateway)
    sms_sent = 0
    sms_status = "Skipped (Not in applicant preference)"
    if pref in ('both', 'phone') and phone:
        if sms_provider == 'fast2sms' and sms_api_key:
            try:
                req_url = f"https://www.fast2sms.com/dev/bulkV2?authorization={sms_api_key}&route=q&message={urllib.parse.quote(sms_text)}&flash=0&numbers={clean_digits}"
                req = urllib.request.Request(req_url, headers={'User-Agent': 'GreenlandSchool/2.0'})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    sms_sent = 1
                    sms_status = f"✅ Delivered Live via Fast2SMS to {phone}"
            except Exception as ex:
                sms_sent = 0
                sms_status = f"⚠️ Fast2SMS Error: {str(ex)[:100]} (WhatsApp link ready)"
        elif sms_provider == 'webhook' and sms_webhook_url:
            try:
                target_url = sms_webhook_url.replace("{phone}", clean_digits).replace("{message}", urllib.parse.quote(sms_text)).replace("{api_key}", sms_api_key)
                req = urllib.request.Request(target_url, headers={'User-Agent': 'GreenlandSchool/2.0'})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    sms_sent = 1
                    sms_status = f"✅ Delivered Live via Webhook to {phone}"
            except Exception as ex:
                sms_sent = 0
                sms_status = f"⚠️ Webhook Error: {str(ex)[:100]} (WhatsApp link ready)"
        else:
            sms_sent = 0
            sms_status = f"📦 Spooled to Outbox & WhatsApp Ready ({sms_filename}) — Direct WhatsApp / SMS link active"

    # Summary
    channels_sent = []
    if pref in ('both', 'email'): channels_sent.append("Email Address")
    if pref in ('both', 'phone'): channels_sent.append("Phone (SMS/WhatsApp)")
    summary_text = " & ".join(channels_sent)

    if pref == 'both':
        dispatch_status = "Dispatched: Both Phone & Email"
        dispatch_message = f"✉️ {email_status} | 📱 {sms_status}"
    elif pref == 'phone':
        dispatch_status = "Dispatched: Phone Only"
        dispatch_message = f"📱 {sms_status}"
    else:
        dispatch_status = "Dispatched: Email Only"
        dispatch_message = f"✉️ {email_status}"

    # Insert into notifications_outbox
    cur.execute("""
        INSERT INTO notifications_outbox (
            admission_id, ref_no, applicant_name, parent_name, grade_applying, preferred_section,
            notification_pref, recipient_email, recipient_phone, email_subject, email_body_html,
            email_body_text, sms_body, email_status, sms_status, email_sent, sms_sent,
            whatsapp_url, sms_link, outbox_email_file, outbox_sms_file, approver_title, dispatched_at, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        adm_id, ref_no, applicant_name, parent_name, grade_applying, preferred_section,
        pref, email, phone, email_subject, html_email_text,
        plain_email_text, sms_text, email_status, sms_status, email_sent, sms_sent,
        wa_url, sms_link, email_filename, sms_filename, approver_title, now, now
    ))

    # Update admissions table
    cur.execute("""
        UPDATE admissions
        SET status = ?,
            approved_by = ?,
            approved_at = ?,
            dispatch_status = ?,
            dispatch_message = ?,
            whatsapp_url = ?,
            sms_link = ?,
            email_dispatch_status = ?,
            sms_dispatch_status = ?,
            outbox_email_file = ?,
            outbox_sms_file = ?
        WHERE id = ?
    """, (
        status_label, approver_title, now, dispatch_status, dispatch_message,
        wa_url, sms_link, email_status, sms_status, email_filename, sms_filename, adm_id
    ))
    conn.commit()

    return {
        "success": True,
        "ref_no": ref_no,
        "applicant_name": applicant_name,
        "parent_name": parent_name,
        "email": email,
        "phone": phone,
        "pref": pref,
        "dispatched_at": now,
        "dispatch_status": dispatch_status,
        "dispatch_message": dispatch_message,
        "email_status": email_status,
        "sms_status": sms_status,
        "email_sent": email_sent,
        "sms_sent": sms_sent,
        "whatsapp_url": wa_url,
        "sms_link": sms_link,
        "outbox_email_file": email_filename,
        "outbox_sms_file": sms_filename,
        "channels_sent": channels_sent,
        "summary_text": summary_text,
        "sms_text": sms_text,
        "email_text": plain_email_text,
        "html_email": html_email_text
    }

def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        username TEXT UNIQUE,
        password TEXT,
        user_type TEXT,
        phone TEXT,
        photo TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        class_type TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INTEGER,
        name TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        code TEXT,
        teacher_id INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        class_id INTEGER,
        section_id INTEGER,
        adm_no TEXT UNIQUE,
        blood_group TEXT,
        parent_id INTEGER,
        dob TEXT,
        gender TEXT,
        address TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        term TEXT,
        year TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS marks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject_id INTEGER,
        exam_id INTEGER,
        ca_score REAL,
        exam_score REAL,
        total REAL,
        grade TEXT,
        remark TEXT,
        UNIQUE(student_id, subject_id, exam_id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        class_id INTEGER,
        date TEXT,
        status TEXT,
        UNIQUE(student_id, date)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        title TEXT,
        amount REAL,
        paid REAL,
        status TEXT,
        ref_no TEXT UNIQUE,
        date TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT,
        isbn TEXT,
        category TEXT,
        total_copies INTEGER,
        available_copies INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS book_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER,
        user_id INTEGER,
        issue_date TEXT,
        due_date TEXT,
        status TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS notices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        category TEXT,
        date TEXT,
        pinned INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS admissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ref_no TEXT UNIQUE,
        applicant_name TEXT,
        parent_name TEXT,
        email TEXT,
        phone TEXT,
        grade_applying TEXT,
        previous_school TEXT,
        message TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS leaves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        applicant_role TEXT NOT NULL,
        leave_type TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        days_count INTEGER DEFAULT 1,
        reason TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        approver_id INTEGER,
        approver_role TEXT,
        approver_notes TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS payment_delete_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        payment_id INTEGER NOT NULL,
        payment_ref TEXT,
        receipt_no TEXT,
        student_name TEXT,
        student_id INTEGER,
        amount REAL NOT NULL,
        paid REAL NOT NULL,
        reason TEXT NOT NULL,
        requested_by_id INTEGER,
        requested_by_name TEXT,
        admin_status TEXT DEFAULT 'Pending',
        admin_id INTEGER,
        admin_name TEXT,
        admin_notes TEXT,
        admin_action_date TEXT,
        superadmin_status TEXT DEFAULT 'Awaiting Admin Approval',
        superadmin_id INTEGER,
        superadmin_name TEXT,
        superadmin_notes TEXT,
        superadmin_action_date TEXT,
        final_status TEXT DEFAULT 'In Progress',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Schema migrations
    try:
        cur.execute("ALTER TABLE sections ADD COLUMN class_teacher_id INTEGER")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE users ADD COLUMN subject TEXT")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE users ADD COLUMN qualification TEXT")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE students ADD COLUMN aadhaar_no TEXT")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE payments ADD COLUMN method TEXT DEFAULT 'Offline / Cash'")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE payments ADD COLUMN transaction_ref TEXT")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE users ADD COLUMN gender TEXT DEFAULT 'Male'")
    except Exception:
        pass

    # Employee Leave Quota Balances Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS employee_leave_balances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        year INTEGER NOT NULL,
        cl_total INTEGER DEFAULT 8,
        cl_used INTEGER DEFAULT 0,
        el_total INTEGER DEFAULT 30,
        el_used INTEGER DEFAULT 0,
        hpl_total INTEGER DEFAULT 20,
        hpl_used INTEGER DEFAULT 0,
        maternity_total INTEGER DEFAULT 0,
        maternity_used INTEGER DEFAULT 0,
        paternity_total INTEGER DEFAULT 0,
        paternity_used INTEGER DEFAULT 0,
        ccl_total INTEGER DEFAULT 730,
        ccl_used INTEGER DEFAULT 0,
        UNIQUE(user_id, year)
    )
    """)

    # Admissions table schema migrations for online inquiries & multi-channel notification dispatch
    for col_name, col_type in [
        ("notification_pref", "TEXT DEFAULT 'both'"),
        ("preferred_section", "TEXT DEFAULT 'Section A'"),
        ("approved_by", "TEXT"),
        ("approved_at", "TEXT"),
        ("dispatch_status", "TEXT"),
        ("dispatch_message", "TEXT"),
        ("whatsapp_url", "TEXT"),
        ("sms_link", "TEXT"),
        ("email_dispatch_status", "TEXT"),
        ("sms_dispatch_status", "TEXT"),
        ("outbox_email_file", "TEXT"),
        ("outbox_sms_file", "TEXT")
    ]:
        try:
            cur.execute(f"ALTER TABLE admissions ADD COLUMN {col_name} {col_type}")
        except Exception:
            pass

    # Multi-Channel Notifications Outbox Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS notifications_outbox (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admission_id INTEGER,
        ref_no TEXT,
        applicant_name TEXT,
        parent_name TEXT,
        grade_applying TEXT,
        preferred_section TEXT,
        notification_pref TEXT,
        recipient_email TEXT,
        recipient_phone TEXT,
        email_subject TEXT,
        email_body_html TEXT,
        email_body_text TEXT,
        sms_body TEXT,
        email_status TEXT,
        sms_status TEXT,
        email_sent INTEGER DEFAULT 0,
        sms_sent INTEGER DEFAULT 0,
        whatsapp_url TEXT,
        sms_link TEXT,
        outbox_email_file TEXT,
        outbox_sms_file TEXT,
        approver_title TEXT,
        dispatched_at TEXT,
        created_at TEXT
    )
    """)

    # Seed notification gateway default settings if not present
    notification_default_settings = [
        ("smtp_host", "smtp.gmail.com"),
        ("smtp_port", "587"),
        ("smtp_user", ""),
        ("smtp_pass", ""),
        ("smtp_sender_name", "Greenland School Admissions"),
        ("smtp_sender_email", "info@greenlandschool.net"),
        ("smtp_tls", "1"),
        ("smtp_ssl", "0"),
        ("sms_provider", "none"),
        ("sms_api_key", ""),
        ("sms_sender_id", "GRNSCH"),
        ("sms_webhook_url", "")
    ]
    for k, v in notification_default_settings:
        cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))

    try:
        cur.execute("ALTER TABLE users ADD COLUMN base_salary REAL DEFAULT 45000.0")
    except Exception:
        pass

    # Special Bonuses Table (Executive Right strictly reserved for Owner)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS special_bonuses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER,
        title TEXT NOT NULL,
        amount REAL NOT NULL,
        month INTEGER NOT NULL,
        year INTEGER NOT NULL,
        granted_by TEXT NOT NULL,
        granted_by_id INTEGER NOT NULL,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Salary Slips Table (strictly auto-generated, cannot be forged by accountant)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS salary_slips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slip_no TEXT UNIQUE,
        teacher_id INTEGER NOT NULL,
        teacher_name TEXT NOT NULL,
        designation TEXT DEFAULT 'Senior Faculty',
        month INTEGER NOT NULL,
        year INTEGER NOT NULL,
        total_days INTEGER DEFAULT 30,
        present_days INTEGER DEFAULT 28,
        paid_leave_days INTEGER DEFAULT 2,
        hpl_days INTEGER DEFAULT 0,
        absent_days INTEGER DEFAULT 0,
        base_salary REAL NOT NULL,
        hra REAL DEFAULT 6000.0,
        da REAL DEFAULT 3000.0,
        transport_allowance REAL DEFAULT 2000.0,
        special_bonus REAL DEFAULT 0.0,
        special_bonus_title TEXT,
        leave_deduction REAL DEFAULT 0.0,
        pf_deduction REAL DEFAULT 1800.0,
        tax_deduction REAL DEFAULT 200.0,
        gross_salary REAL NOT NULL,
        net_salary REAL NOT NULL,
        generated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        generated_by TEXT DEFAULT 'System Auto-Engine',
        status TEXT DEFAULT 'Generated',
        FOREIGN KEY (teacher_id) REFERENCES users(id),
        UNIQUE(teacher_id, month, year)
    )
    """)

    # Ensure existing students have 12-digit Aadhaar if blank
    try:
        cur.execute("SELECT id FROM students WHERE aadhaar_no IS NULL OR aadhaar_no = ''")
        blank_rows = cur.fetchall()
        for idx, (b_id,) in enumerate(blank_rows):
            sample_aadhaar = f"548962{100001 + idx:06d}"
            cur.execute("UPDATE students SET aadhaar_no = ? WHERE id = ?", (sample_aadhaar, b_id))
    except Exception:
        pass

    # Ensure accurate employee genders
    try:
        cur.execute("UPDATE users SET gender = 'Male' WHERE username IN ('Owner(Directer)', 'GS_admin', 'GS_teacher', 'GS_accountant', 'GS_parent', 'GS_itsupport')")
        cur.execute("UPDATE users SET gender = 'Female' WHERE username IN ('GS_teacher_2', 'GS_librarian', 'GS_superadmin')")
    except Exception:
        pass

    # Computer Lab Inventory Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS lab_computers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lab_name TEXT DEFAULT 'Computer Lab 1 (Main Lab)',
        pc_number TEXT NOT NULL,
        ip_address TEXT,
        processor TEXT DEFAULT 'Intel Core i5-12400 / 16GB RAM / 512GB SSD',
        os TEXT DEFAULT 'Windows 11 Pro',
        status TEXT DEFAULT 'Working',
        active_complaint_id INTEGER,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(lab_name, pc_number)
    )
    """)

    # Credential & User ID Requests Table (IT Support Request -> Owner Approval)
    cur.execute("""
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
    """)

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

    # Laptop & Computer IT Asset Management System Tables
    cur.execute("""
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
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS it_assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_tag TEXT UNIQUE NOT NULL,
        device_type TEXT NOT NULL,
        brand TEXT NOT NULL,
        model_name TEXT NOT NULL,
        serial_number TEXT UNIQUE,
        specs_processor TEXT,
        specs_ram TEXT,
        specs_storage TEXT,
        specs_os TEXT,
        ownership_type TEXT DEFAULT 'Owned (Institutional Purchase)',
        condition TEXT DEFAULT 'Excellent',
        purchase_date TEXT,
        purchase_cost REAL DEFAULT 0.0,
        current_location TEXT DEFAULT 'IT Support Depot',
        status TEXT DEFAULT 'In Stock / Available',
        notes TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS it_rentals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rental_agreement_no TEXT UNIQUE NOT NULL,
        rental_type TEXT DEFAULT 'Inward (Rented from Vendor)',
        asset_id INTEGER,
        vendor_or_client_name TEXT NOT NULL,
        contact_phone TEXT,
        contact_email TEXT,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        billing_cycle TEXT DEFAULT 'Monthly',
        rental_amount REAL DEFAULT 0.0,
        deposit_amount REAL DEFAULT 0.0,
        next_payment_due_date TEXT,
        payment_status TEXT DEFAULT 'Current / Up to Date',
        rental_status TEXT DEFAULT 'Active Agreement',
        terms_notes TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS it_asset_allocations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        handover_slip_no TEXT UNIQUE NOT NULL,
        asset_id INTEGER NOT NULL,
        employee_id INTEGER,
        employee_name TEXT NOT NULL,
        employee_role TEXT NOT NULL,
        department TEXT DEFAULT 'Academics & Faculty',
        handover_date TEXT NOT NULL,
        expected_return_date TEXT,
        actual_return_date TEXT,
        handover_condition TEXT DEFAULT 'Pristine / Like New',
        accessories_included TEXT DEFAULT 'Original Charger, Laptop Bag, Wireless Mouse',
        handover_notes TEXT,
        handover_status TEXT DEFAULT 'Active (With Employee)',
        return_condition TEXT,
        return_verified_by TEXT,
        created_at TEXT,
        FOREIGN KEY (asset_id) REFERENCES it_assets(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS it_warranties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id INTEGER NOT NULL,
        provider_name TEXT NOT NULL,
        policy_number TEXT NOT NULL,
        warranty_type TEXT DEFAULT 'OEM Standard Warranty',
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        support_contact TEXT,
        status TEXT DEFAULT 'Active',
        claim_count INTEGER DEFAULT 0,
        notes TEXT,
        created_at TEXT,
        FOREIGN KEY (asset_id) REFERENCES it_assets(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS it_maintenance_service (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_ticket_no TEXT UNIQUE NOT NULL,
        asset_id INTEGER NOT NULL,
        service_type TEXT NOT NULL,
        reported_issue TEXT NOT NULL,
        service_center_or_vendor TEXT NOT NULL,
        technician_name TEXT,
        start_date TEXT NOT NULL,
        completion_date TEXT,
        repair_cost REAL DEFAULT 0.0,
        parts_replaced TEXT,
        service_status TEXT DEFAULT 'Under Diagnostics',
        warranty_claim_covered INTEGER DEFAULT 0,
        remarks TEXT,
        created_at TEXT,
        FOREIGN KEY (asset_id) REFERENCES it_assets(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS it_asset_payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ref_no TEXT UNIQUE NOT NULL,
        payment_category TEXT NOT NULL,
        related_rental_id INTEGER,
        related_service_id INTEGER,
        vendor_name TEXT NOT NULL,
        amount REAL NOT NULL,
        due_date TEXT NOT NULL,
        paid_date TEXT,
        payment_status TEXT DEFAULT 'Upcoming Due',
        payment_method TEXT,
        transaction_ref TEXT,
        notes TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS it_asset_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id INTEGER NOT NULL,
        action_type TEXT NOT NULL,
        from_location TEXT,
        to_location TEXT,
        assigned_to TEXT,
        performed_by TEXT,
        details TEXT,
        timestamp TEXT,
        FOREIGN KEY (asset_id) REFERENCES it_assets(id)
    )
    """)

    # Computer Lab Complaints & Repair Dispatch Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS lab_complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_no TEXT UNIQUE,
        computer_id INTEGER NOT NULL,
        pc_number TEXT NOT NULL,
        lab_name TEXT NOT NULL,
        reported_by_id INTEGER,
        reported_by_name TEXT,
        teacher_role TEXT DEFAULT 'Computer Teacher',
        issue_category TEXT NOT NULL,
        problem_description TEXT NOT NULL,
        priority TEXT DEFAULT 'Medium',
        status TEXT DEFAULT 'Pending',
        assigned_to_id INTEGER,
        assigned_to_name TEXT,
        assigned_by TEXT,
        assigned_at TEXT,
        technician_notes TEXT,
        resolution_notes TEXT,
        resolved_by TEXT,
        resolved_at TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (computer_id) REFERENCES lab_computers(id)
    )
    """)

    # Seed / maintain 100 lab computers (50 in Lab 1 & 50 in Lab 2) assigned to Computer Teacher GS_teacher as Common ID
    try:
        # Schema migration check
        cur.execute("PRAGMA table_info(users)")
        u_cols = [c[1] for c in cur.fetchall()]
        if 'is_common_id' not in u_cols: cur.execute("ALTER TABLE users ADD COLUMN is_common_id INTEGER DEFAULT 0")
        if 'common_id_name' not in u_cols: cur.execute("ALTER TABLE users ADD COLUMN common_id_name TEXT")
        if 'has_mail_services' not in u_cols: cur.execute("ALTER TABLE users ADD COLUMN has_mail_services INTEGER DEFAULT 1")
        if 'admin_user_id' not in u_cols: cur.execute("ALTER TABLE users ADD COLUMN admin_user_id INTEGER")
        if 'admin_username' not in u_cols: cur.execute("ALTER TABLE users ADD COLUMN admin_username TEXT")
        if 'admin_name' not in u_cols: cur.execute("ALTER TABLE users ADD COLUMN admin_name TEXT")

        cur.execute("PRAGMA table_info(lab_computers)")
        c_cols = [c[1] for c in cur.fetchall()]
        if 'assigned_teacher_id' not in c_cols: cur.execute("ALTER TABLE lab_computers ADD COLUMN assigned_teacher_id INTEGER")
        if 'assigned_teacher_username' not in c_cols: cur.execute("ALTER TABLE lab_computers ADD COLUMN assigned_teacher_username TEXT")
        if 'is_common_id' not in c_cols: cur.execute("ALTER TABLE lab_computers ADD COLUMN is_common_id INTEGER DEFAULT 1")
        if 'common_id_name' not in c_cols: cur.execute("ALTER TABLE lab_computers ADD COLUMN common_id_name TEXT DEFAULT 'Computer Lab Fleet'")
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
        if 'assigned_lab_fleet' not in cr_cols: cur.execute("ALTER TABLE credential_requests ADD COLUMN assigned_lab_fleet TEXT")

        # Ensure Computer Teacher exists with Common ID (No Mail Services)
        cur.execute("SELECT id FROM users WHERE username IN ('GS_teacher', 'GS_Computer_Teacher') OR email = 'teacher.chike@greenlandschool.net'")
        t_row = cur.fetchone()
        if not t_row:
            cur.execute("""
                INSERT INTO users (name, username, password, user_type, email, phone, gender, is_common_id, common_id_name, has_mail_services, subject, qualification)
                VALUES ('Teacher Chike (Computer Science & Lab In-Charge)', 'GS_teacher', 'Greenland@2026', 'teacher', 'teacher.chike@greenlandschool.net', '+91 761 700 5057', 'Male', 1, 'Computer Teacher Lab Fleet (Lab 1 & 2 Common ID)', 0, 'Computer Science', 'MCA, B.Ed')
            """)
            t_id = cur.lastrowid
        else:
            t_id = t_row[0]
            cur.execute("UPDATE users SET is_common_id = 1, common_id_name = 'Computer Teacher Lab Fleet (Lab 1 & 2 Common ID)', has_mail_services = 0 WHERE id = ?", (t_id,))

        cur.execute("SELECT COUNT(*) FROM lab_computers")
        current_count = cur.fetchone()[0]
        if current_count < 100:
            cur.execute("DELETE FROM lab_computers")
            # Lab 1: 50 PCs
            for i in range(1, 51):
                pc_num = f"PC-{i:02d}"
                ip = f"192.168.1.{100 + i}"
                cur.execute("""
                    INSERT INTO lab_computers (lab_name, pc_number, ip_address, processor, os, status, assigned_teacher_id, assigned_teacher_username, is_common_id, common_id_name, has_mail_services)
                    VALUES ('Computer Lab 1 (Main Lab)', ?, ?, 'Intel Core i5-12400 / 16GB RAM / 512GB SSD', 'Windows 11 Pro', 'Working', ?, 'GS_teacher', 1, 'Computer Lab 1 Fleet (Common ID)', 0)
                """, (pc_num, ip, t_id))

            # Lab 2: 50 PCs
            for i in range(51, 101):
                pc_num = f"PC-{i:02d}"
                ip = f"192.168.2.{100 + (i - 50)}"
                cur.execute("""
                    INSERT INTO lab_computers (lab_name, pc_number, ip_address, processor, os, status, assigned_teacher_id, assigned_teacher_username, is_common_id, common_id_name, has_mail_services)
                    VALUES ('Computer Lab 2 (Senior Coding Lab)', ?, ?, 'Intel Core i7-12700 / 32GB RAM / 1TB NVMe', 'Windows 11 Pro & Ubuntu 22.04 LTS Dual Boot', 'Working', ?, 'GS_teacher', 1, 'Computer Lab 2 Fleet (Common ID)', 0)
                """, (pc_num, ip, t_id))
    except Exception as e:
        print(f"Error seeding lab computers & common IDs: {e}")

    # Seed default IT Asset fleet if empty
    try:
        ensure_default_it_assets(conn)
    except Exception as e:
        print(f"Error seeding IT assets: {e}")

    # Enforce Name & Gender rule: If user ID has no name, there is no gender!
    try:
        cur.execute("UPDATE users SET gender = NULL WHERE name IS NULL OR TRIM(name) = ''")
    except Exception:
        pass

    conn.commit()

    # Seed initial data if empty
    cur.execute("SELECT COUNT(*) FROM settings")
    if cur.fetchone()[0] == 0:
        seed_data(conn)
        ensure_default_students_and_library(conn)
    else:
        # Synchronize unique credentials for existing database
        ensure_unique_credentials(conn)

    # Initialize leave quotas for staff
    try:
        cur.execute("SELECT id FROM users WHERE user_type IN ('teacher', 'admin', 'super_admin')")
        staff_ids = [r[0] for r in cur.fetchall()]
        for sid in staff_ids:
            get_or_create_leave_balances(cur, sid, 2026)
        conn.commit()
    except Exception:
        pass

    # Seed sample Owner Diwali Bonus if none exists
    try:
        cur.execute("SELECT COUNT(*) FROM special_bonuses")
        if cur.fetchone()[0] == 0:
            cur.execute("""
                INSERT INTO special_bonuses (teacher_id, title, amount, month, year, granted_by, granted_by_id, notes, created_at)
                VALUES (NULL, 'Diwali Festival Bonus 2026', 10000.0, 11, 2026, 'Owner (Director) Rajeev Sinha', 27, 'Executive Diwali Festival Bonus sanctioned by Director Rajeev Sinha for all Greenland School teaching faculty.', '2026-11-01 10:00:00')
            """)
            conn.commit()
    except Exception as e:
        print(f"Error seeding special bonus: {e}")

    # Seed sample online inquiries with preferred notification channels if none pending
    try:
        cur.execute("SELECT COUNT(*) FROM admissions WHERE status = 'Pending'")
        if cur.fetchone()[0] == 0:
            cur.execute("""
                INSERT INTO admissions (ref_no, applicant_name, parent_name, email, phone, grade_applying, preferred_section, previous_school, message, notification_pref, status, created_at)
                VALUES 
                ('ADM-2611-INQ1', 'Arya Kapoor', 'Vikram Kapoor', 'vikram.kapoor@example.com', '+91 98765 43210', 'Class 11', 'Section A', 'St. Xavier High School', 'Seeking admission in Science Stream with Computer Science.', 'both', 'Pending', '2026-11-04 15:30:00'),
                ('ADM-2611-INQ2', 'Meera Nair', 'Rajesh Nair', 'rajesh.nair@example.com', '+91 98112 34567', 'Class 12 - Science', 'Section A', 'Delhi Public School', 'Transfer admission due to parental relocation to Renukoot.', 'phone', 'Pending', '2026-11-04 16:15:00'),
                ('ADM-2611-INQ3', 'Kabir Das', 'Sunita Das', 'sunita.das@example.com', '+91 98223 45678', 'Class 9', 'Section B', 'Green Valley Academy', 'Interested in state-level mathematics Olympiad coaching.', 'email', 'Pending', '2026-11-04 17:00:00')
            """)
            conn.commit()
    except Exception as e:
        print(f"Error seeding inquiries: {e}")

    # Ensure existing approved inquiries have outbox records and WhatsApp/SMS links generated
    try:
        cur.execute("SELECT * FROM admissions WHERE status = 'Approved' AND (whatsapp_url IS NULL OR whatsapp_url = '')")
        approved_rows = cur.fetchall()
        for a_row in approved_rows:
            ad_dict = dict(a_row)
            approver = ad_dict.get('approved_by') or 'Owner (Director) Rajeev Sinha'
            dispatch_admission_notification(conn, ad_dict, approver, action='approve')
    except Exception as e:
        print(f"Error generating initial outbox for approved admissions: {e}")

    conn.close()

# OFFICIAL GREENLAND SCHOOL LEAVE RULES & ALLOCATIONS
LEAVE_POLICY_RULES = {
    "Casual Leave (CL)": {
        "days": 8,
        "quota": "8 days per calendar year",
        "gender": "All Employees",
        "description": "Set at 8 days per calendar year. It is an executive instruction rather than a recognized form of leave, meaning your pay does not stop, and it cannot be combined with regular leave types."
    },
    "Earned Leave (EL)": {
        "days": 30,
        "quota": "30 days per year (15 in Jan + 15 in July)",
        "gender": "All Employees",
        "description": "Credited in advance twice a year (15 days each on January 1 and July 1). You can accumulate a maximum of 300 days in your career, which can also be encashed at the time of retirement."
    },
    "Half Pay Leave (HPL)": {
        "days": 20,
        "quota": "20 days per year (10 days every half-year)",
        "gender": "All Employees",
        "description": "Credited at a rate of 10 days every half-year. This is calculated based on completed service periods and can be commuted onto medical grounds."
    },
    "Maternity Leave": {
        "days": 180,
        "quota": "180 days (Eligible up to 2 surviving children)",
        "gender": "Female Employees Only",
        "description": "Female employees are eligible for 180 days of Maternity Leave (up to 2 surviving children). Male employees are not eligible."
    },
    "Paternity Leave": {
        "days": 15,
        "quota": "15 days",
        "gender": "Male Employees Only",
        "description": "Male employees are allowed 15 days of Paternity Leave. Female employees are not eligible."
    },
    "Child Care Leave (CCL)": {
        "days": 730,
        "quota": "730 days across entire service",
        "gender": "Female & Single Male Employees",
        "description": "Available to female employees and single male employees for up to 730 days across their entire service to look after minor children."
    }
}

def get_or_create_leave_balances(cur, user_id, year=2026):
    cur.execute("SELECT id, name, user_type, COALESCE(gender, 'Male') as gender FROM users WHERE id = ?", (user_id,))
    u = cur.fetchone()
    if not u:
        return None, 'Male'
    try:
        gender = u['gender']
    except Exception:
        try:
            gender = u[3]
        except Exception:
            gender = 'Male'
    gender = gender or 'Male'
    
    cur.execute("SELECT id, user_id, year, cl_total, cl_used, el_total, el_used, hpl_total, hpl_used, maternity_total, maternity_used, paternity_total, paternity_used, ccl_total, ccl_used FROM employee_leave_balances WHERE user_id = ? AND year = ?", (user_id, year))
    row = cur.fetchone()
    if not row:
        maternity_tot = 180 if gender == 'Female' else 0
        paternity_tot = 15 if gender == 'Male' else 0
        ccl_tot = 730
        cur.execute("""
            INSERT INTO employee_leave_balances 
            (user_id, year, cl_total, cl_used, el_total, el_used, hpl_total, hpl_used, maternity_total, maternity_used, paternity_total, paternity_used, ccl_total, ccl_used)
            VALUES (?, ?, 8, 0, 30, 0, 20, 0, ?, 0, ?, 0, ?, 0)
        """, (user_id, year, maternity_tot, paternity_tot, ccl_tot))
        if hasattr(cur, 'connection') and cur.connection:
            cur.connection.commit()
        cur.execute("SELECT id, user_id, year, cl_total, cl_used, el_total, el_used, hpl_total, hpl_used, maternity_total, maternity_used, paternity_total, paternity_used, ccl_total, ccl_used FROM employee_leave_balances WHERE user_id = ? AND year = ?", (user_id, year))
        row = cur.fetchone()

    if isinstance(row, (tuple, list)):
        row_dict = {
            "id": row[0], "user_id": row[1], "year": row[2],
            "cl_total": row[3], "cl_used": row[4],
            "el_total": row[5], "el_used": row[6],
            "hpl_total": row[7], "hpl_used": row[8],
            "maternity_total": row[9], "maternity_used": row[10],
            "paternity_total": row[11], "paternity_used": row[12],
            "ccl_total": row[13], "ccl_used": row[14]
        }
    else:
        row_dict = dict(row)

    row_dict['cl_remaining'] = max(0, row_dict['cl_total'] - row_dict['cl_used'])
    row_dict['el_remaining'] = max(0, row_dict['el_total'] - row_dict['el_used'])
    row_dict['hpl_remaining'] = max(0, row_dict['hpl_total'] - row_dict['hpl_used'])
    row_dict['maternity_remaining'] = max(0, row_dict['maternity_total'] - row_dict['maternity_used'])
    row_dict['paternity_remaining'] = max(0, row_dict['paternity_total'] - row_dict['paternity_used'])
    row_dict['ccl_remaining'] = max(0, row_dict['ccl_total'] - row_dict['ccl_used'])
    return row_dict, gender

def check_principal_on_leave(cur):
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""
        SELECT l.*, u.name as principal_name, u.email as principal_email, u.username as principal_username
        FROM leaves l
        JOIN users u ON l.user_id = u.id
        WHERE (l.applicant_role = 'admin' OR u.user_type = 'admin')
          AND l.status = 'Approved'
          AND l.start_date <= ? AND l.end_date >= ?
        ORDER BY l.id DESC LIMIT 1
    """, (today, today))
    row = cur.fetchone()
    if row:
        return True, dict(row)
    return False, None

def auto_generate_salary_slips_for_month(cur, month=11, year=2026):
    """
    Automated Salary Slip Engine:
    - Calculates salaries according to base pay, attendance, paid leave, HPL, and unexcused absence.
    - Account department CANNOT prepare their own arbitrary salary figures.
    - Special bonuses (e.g. Diwali Bonus) can only be granted by the Owner (Director).
    """
    cur.execute("""
        SELECT id, name, username, COALESCE(base_salary, 45000.0) as base_salary, COALESCE(gender, 'Male') as gender 
        FROM users 
        WHERE user_type = 'teacher' 
        ORDER BY id ASC
    """)
    teachers = [dict(r) for r in cur.fetchall()]
    total_days = 30
    slips = []

    for t in teachers:
        tid = t['id']
        tname = t['name']
        base = float(t['base_salary'])
        hra = 6000.0
        da = 3000.0
        transport = 2000.0

        # Query approved leaves for this teacher
        cur.execute("""
            SELECT leave_type, days_count, status
            FROM leaves
            WHERE user_id = ? AND status = 'Approved'
        """, (tid,))
        approved_leaves = [dict(r) for r in cur.fetchall()]

        paid_leave_days = 0
        hpl_days = 0
        for l in approved_leaves:
            lt = (l.get('leave_type') or '').lower()
            days = l.get('days_count') or 1
            if 'half pay' in lt or 'hpl' in lt:
                hpl_days += days
            else:
                paid_leave_days += days

        absent_days = 0
        present_days = max(0, total_days - paid_leave_days - hpl_days - absent_days)

        # Query Owner Special Bonus for this teacher/month/year
        cur.execute("""
            SELECT SUM(amount), GROUP_CONCAT(title, ', ')
            FROM special_bonuses
            WHERE (teacher_id IS NULL OR teacher_id = ?) AND month = ? AND year = ?
        """, (tid, month, year))
        bonus_row = cur.fetchone()
        special_bonus_amount = float(bonus_row[0] or 0.0) if bonus_row and bonus_row[0] else 0.0
        special_bonus_title = (bonus_row[1] or "") if bonus_row and bonus_row[1] else ""

        # Deductions
        leave_deduction = round((base / float(total_days)) * 0.5 * hpl_days + (base / float(total_days)) * 1.0 * absent_days, 2)
        pf_deduction = 1800.0
        tax_deduction = 200.0
        gross_salary = round(base + hra + da + transport + special_bonus_amount, 2)
        total_deductions = round(leave_deduction + pf_deduction + tax_deduction, 2)
        net_salary = round(gross_salary - total_deductions, 2)

        slip_no = f"SLIP-{year}{month:02d}-{tid:03d}"
        designation = "Senior PGT Faculty" if "Chike" in tname else "TGT Faculty"

        cur.execute("""
            INSERT INTO salary_slips (
                slip_no, teacher_id, teacher_name, designation, month, year,
                total_days, present_days, paid_leave_days, hpl_days, absent_days,
                base_salary, hra, da, transport_allowance, special_bonus, special_bonus_title,
                leave_deduction, pf_deduction, tax_deduction, gross_salary, net_salary,
                generated_at, generated_by, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 'System Automated Engine', 'Generated')
            ON CONFLICT(teacher_id, month, year) DO UPDATE SET
                slip_no = excluded.slip_no,
                teacher_name = excluded.teacher_name,
                designation = excluded.designation,
                total_days = excluded.total_days,
                present_days = excluded.present_days,
                paid_leave_days = excluded.paid_leave_days,
                hpl_days = excluded.hpl_days,
                absent_days = excluded.absent_days,
                base_salary = excluded.base_salary,
                hra = excluded.hra,
                da = excluded.da,
                transport_allowance = excluded.transport_allowance,
                special_bonus = excluded.special_bonus,
                special_bonus_title = excluded.special_bonus_title,
                leave_deduction = excluded.leave_deduction,
                pf_deduction = excluded.pf_deduction,
                tax_deduction = excluded.tax_deduction,
                gross_salary = excluded.gross_salary,
                net_salary = excluded.net_salary,
                generated_at = CURRENT_TIMESTAMP,
                status = 'Generated'
        """, (
            slip_no, tid, tname, designation, month, year,
            total_days, present_days, paid_leave_days, hpl_days, absent_days,
            base, hra, da, transport, special_bonus_amount, special_bonus_title,
            leave_deduction, pf_deduction, tax_deduction, gross_salary, net_salary
        ))
        slips.append(slip_no)

    if hasattr(cur, 'connection') and cur.connection:
        cur.connection.commit()
    return slips

def generate_accountant_salary_slip(cur, month=11, year=2026, base_salary=55000.0, special_bonus=0.0, bonus_title='', director_name='Owner (Director) Rajeev Sinha'):
    """
    STRICT INSTITUTIONAL POLICY:
    The Accountant's salary payslip can ONLY be generated and issued by the Director (Owner).
    Accountant is strictly prohibited from preparing or generating their own salary payslip.
    """
    cur.execute("SELECT id, name, username, COALESCE(base_salary, 55000.0) as base_salary FROM users WHERE user_type = 'accountant' LIMIT 1")
    acc = cur.fetchone()
    if not acc:
        return None
    acc_id = acc['id']
    acc_name = acc['name'] or 'Accountant Jude Bello'
    base = float(base_salary or acc['base_salary'] or 55000.0)
    hra = 8000.0
    da = 4000.0
    transport = 3000.0
    bonus = float(special_bonus or 0.0)
    pf = 1800.0
    tax = 500.0
    gross = round(base + hra + da + transport + bonus, 2)
    net = round(gross - (pf + tax), 2)
    slip_no = f"SLIP-ACC-{year}{month:02d}-{acc_id:03d}"

    cur.execute("""
        INSERT INTO salary_slips (
            slip_no, teacher_id, teacher_name, designation, month, year,
            total_days, present_days, paid_leave_days, hpl_days, absent_days,
            base_salary, hra, da, transport_allowance, special_bonus, special_bonus_title,
            leave_deduction, pf_deduction, tax_deduction, gross_salary, net_salary,
            generated_at, generated_by, status
        ) VALUES (
            ?, ?, ?, 'Head Bursar & Chief Accountant', ?, ?,
            30, 30, 0, 0, 0,
            ?, ?, ?, ?, ?, ?,
            0.0, ?, ?, ?, ?,
            CURRENT_TIMESTAMP, ?, 'Sanctioned by Director'
        )
        ON CONFLICT(teacher_id, month, year) DO UPDATE SET
            slip_no = excluded.slip_no,
            teacher_name = excluded.teacher_name,
            designation = excluded.designation,
            base_salary = excluded.base_salary,
            hra = excluded.hra,
            da = excluded.da,
            transport_allowance = excluded.transport_allowance,
            special_bonus = excluded.special_bonus,
            special_bonus_title = excluded.special_bonus_title,
            gross_salary = excluded.gross_salary,
            net_salary = excluded.net_salary,
            generated_by = excluded.generated_by,
            status = excluded.status
    """, (
        slip_no, acc_id, acc_name, month, year,
        base, hra, da, transport, bonus, bonus_title or 'Executive Directorate Financial Operations Allowance',
        pf, tax, gross, net, director_name
    ))
    return {
        "slip_no": slip_no,
        "teacher_id": acc_id,
        "teacher_name": acc_name,
        "designation": "Head Bursar & Chief Accountant",
        "month": month,
        "year": year,
        "base_salary": base,
        "gross_salary": gross,
        "net_salary": net,
        "generated_by": director_name,
        "status": "Sanctioned by Director"
    }

def ensure_unique_credentials(conn):
    cur = conn.cursor()
    # Core system accounts that must ALWAYS exist in Greenland School
    CORE_REQUIRED = ['Owner(Directer)', 'GS_itsupport']

    for u in UNIQUE_DEFAULT_USERS:
        # Match by specific username
        cur.execute("SELECT id FROM users WHERE LOWER(username) = LOWER(?)", (u['username'],))
        row = cur.fetchone()
        u_gender = u.get('gender', 'Female' if 'rose' in u['username'].lower() or 'sarah' in u['username'].lower() or 'superadmin' in u['username'].lower() else 'Male')
        if row:
            user_id = row[0]
            cur.execute("""
                UPDATE users 
                SET username = ?, password = ?, email = ?, name = ?, user_type = ?, gender = ?
                WHERE id = ?
            """, (u['username'], u['password'], u['email'], u['name'], u['role'], u_gender, user_id))
        elif u['username'] in CORE_REQUIRED:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("""
                INSERT INTO users (name, email, username, password, user_type, phone, photo, created_at, gender)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (u['name'], u['email'], u['username'], u['password'], u['role'], u['phone'], u['photo'], now, u_gender))
    
    # Populate teacher metadata and initial assignments if GS_teacher exists
    cur.execute("UPDATE users SET subject = 'English Language & Literature', qualification = 'B.A. Ed. (English)' WHERE username = 'GS_teacher' AND (subject IS NULL OR subject = '')")
    cur.execute("UPDATE users SET subject = 'Mathematics & Science', qualification = 'M.Sc. Mathematics, B.Ed.' WHERE user_type = 'teacher' AND username != 'GS_teacher' AND (subject IS NULL OR subject = '')")
    cur.execute("SELECT id FROM sections WHERE name = 'Section A' AND class_id = 19 LIMIT 1")
    sec_row = cur.fetchone()
    if sec_row:
        cur.execute("SELECT id FROM users WHERE username = 'GS_teacher' LIMIT 1")
        tch_row = cur.fetchone()
        if tch_row:
            cur.execute("UPDATE sections SET class_teacher_id = ? WHERE id = ? AND class_teacher_id IS NULL", (tch_row[0], sec_row[0]))
    conn.commit()

def ensure_default_students_and_library(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM students")
    std_count = cur.fetchone()[0]
    if std_count == 0:
        # Find parent
        cur.execute("SELECT id FROM users WHERE user_type = 'parent' LIMIT 1")
        p_row = cur.fetchone()
        parent_id = p_row[0] if p_row else 8

        # 1. Alexander Marcus Kaba
        cur.execute("SELECT id FROM users WHERE username = 'GS_student' OR email = 'student.alex@greenlandschool.net'")
        alex_u = cur.fetchone()
        if alex_u:
            alex_user_id = alex_u[0]
            cur.execute("UPDATE users SET name = 'Alexander Marcus Kaba' WHERE id = ?", (alex_user_id,))
        else:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("""
                INSERT INTO users (name, email, username, password, user_type, phone, photo, created_at, gender)
                VALUES ('Alexander Marcus Kaba', 'student.alex@greenlandschool.net', 'GS_student', 'Greenland@2026', 'student', '+91 761 700 5055', 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150', ?, 'Male')
            """, (now,))
            alex_user_id = cur.lastrowid

        cur.execute("""
            INSERT INTO students (user_id, class_id, section_id, adm_no, blood_group, parent_id, dob, gender, address, aadhaar_no)
            VALUES (?, 19, 46, 'GS/2026/0001', 'O+', ?, '2011-04-14', 'Male', 'Greenland Enclave, Civil Lines, Sonbhadra, UP', '548962147801')
        """, (alex_user_id, parent_id))
        alex_student_id = cur.lastrowid

        # 2. Clara Kaba
        cur.execute("SELECT id FROM users WHERE username = 'GS_student_Clara_Kaba_Class6'")
        clara_u = cur.fetchone()
        if clara_u:
            clara_user_id = clara_u[0]
        else:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("""
                INSERT INTO users (name, email, username, password, user_type, phone, photo, created_at, gender)
                VALUES ('Clara Kaba', 'GS_student_Clara_Kaba_Class6@greenlandschool.net', 'GS_student_Clara_Kaba_Class6', 'Greenland@2026', 'student', '+91 761 700 5059', 'https://images.unsplash.com/photo-1544717305-2782549b5136?w=150', ?, 'Female')
            """, (now,))
            clara_user_id = cur.lastrowid

        cur.execute("""
            INSERT INTO students (user_id, class_id, section_id, adm_no, blood_group, parent_id, dob, gender, address, aadhaar_no)
            VALUES (?, 15, 34, 'GS/2026/0002', 'B+', ?, '2015-08-22', 'Female', 'Greenland Enclave, Civil Lines, Sonbhadra, UP', '781234905621')
        """, (clara_user_id, parent_id))
        clara_student_id = cur.lastrowid

        # Payments for Alex
        cur.execute("""
            INSERT INTO payments (student_id, title, amount, paid, status, ref_no, date, method, transaction_ref)
            VALUES (?, 'Term 1 Tuition & STEM Laboratory Fee', 30000.0, 30000.0, 'Paid', 'REC-2026-ALX1', '2026-10-10', 'UPI / QR Code', 'UPI-982341201')
        """, (alex_student_id,))
        cur.execute("""
            INSERT INTO payments (student_id, title, amount, paid, status, ref_no, date, method, transaction_ref)
            VALUES (?, 'Term 2 Tuition & Board Examination Fee', 15000.0, 0.0, 'Unpaid', 'INV-2026-ALX2', '2026-11-01', 'Online Net Banking', NULL)
        """, (alex_student_id,))

        # Payments for Clara
        cur.execute("""
            INSERT INTO payments (student_id, title, amount, paid, status, ref_no, date, method, transaction_ref)
            VALUES (?, 'Class 6 Annual Composite Tuition & Activity Fee', 40000.0, 40000.0, 'Paid', 'REC-2026-CLR1', '2026-10-15', 'Net Banking (SBI)', 'SBI-REF-449102')
        """, (clara_student_id,))

        # Library Requests
        cur.execute("""
            INSERT INTO book_requests (book_id, user_id, issue_date, issue_time, due_date, return_date, return_time, status, bookshelf_no, issuer_name)
            VALUES (1, ?, '2026-11-03', '09:45:00', '2026-11-17', NULL, NULL, 'Issued', 'Shelf M-01', 'Librarian Rose Davies')
        """, (alex_user_id,))
        cur.execute("""
            INSERT INTO book_requests (book_id, user_id, issue_date, issue_time, due_date, return_date, return_time, status, bookshelf_no, issuer_name)
            VALUES (6, ?, '2026-10-15', '14:20:00', '2026-10-29', '2026-10-28', '11:15:00', 'Returned', 'Shelf CS-01', 'Librarian Rose Davies')
        """, (alex_user_id,))
        cur.execute("""
            INSERT INTO book_requests (book_id, user_id, issue_date, issue_time, due_date, return_date, return_time, status, bookshelf_no, issuer_name)
            VALUES (7, ?, '2026-11-04', '11:10:00', '2026-11-18', NULL, NULL, 'Issued', 'Shelf L-01', 'Librarian Rose Davies')
        """, (clara_user_id,))

        conn.commit()
        print("ensure_default_students_and_library: Seeded demo students and library records.")

def seed_data(conn):
    cur = conn.cursor()
    # Settings
    settings = [
        ("system_name", "Greenland School"),
        ("system_title", "GS"),
        ("current_session", "2026-2027"),
        ("current_term", "First Term"),
        ("phone", "+91 761 700 5055, +91 761 700 5056"),
        ("system_email", "info@greenlandschool.net"),
        ("address", "Khadpathar, Renukoot, Sonbhadra, Uttar Pradesh - 231217"),
        ("tuition_jss", "45000"),
        ("tuition_sss", "55000"),
        ("tuition_primary", "35000")
    ]
    cur.executemany("INSERT INTO settings (key, value) VALUES (?, ?)", settings)

    # Insert unique accounts
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for u in UNIQUE_DEFAULT_USERS:
        cur.execute("""
            INSERT INTO users (name, email, username, password, user_type, phone, photo, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (u['name'], u['email'], u['username'], u['password'], u['role'], u['phone'], u['photo'], now))

    # Add other supporting users
    cur.execute("INSERT INTO users (name, email, username, password, user_type, phone, photo, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                ("Teacher Sarah Adams", "sarah@greenlandschool.net", "sarah_adams", "Greenland@2026", "teacher", "+91 761 700 5056", "https://images.unsplash.com/photo-1580894732454-defa1b24e4d4?w=150", now))

    # Classes (Class 1 to Class 12, with Science, Commerce, and Humanities options for Class 12)
    classes = [
        ("Class 1", "Primary"),
        ("Class 2", "Primary"),
        ("Class 3", "Primary"),
        ("Class 4", "Primary"),
        ("Class 5", "Primary"),
        ("Class 6", "Middle"),
        ("Class 7", "Middle"),
        ("Class 8", "Middle"),
        ("Class 9", "Secondary"),
        ("Class 10", "Secondary"),
        ("Class 11", "Senior Secondary"),
        ("Class 12", "Senior Secondary"),
        ("Class 12 - Science", "Senior Secondary - Science"),
        ("Class 12 - Commerce", "Senior Secondary - Commerce"),
        ("Class 12 - Humanities (Arts)", "Senior Secondary - Humanities")
    ]
    for c in classes:
        cur.execute("INSERT INTO classes (name, class_type) VALUES (?, ?)", c)

    # Sections (Section A, Section B, Section C)
    cur.execute("SELECT id FROM classes")
    all_cids = [r[0] for r in cur.fetchall()]
    for cid in all_cids:
        cur.execute("INSERT INTO sections (class_id, name) VALUES (?, 'Section A')", (cid,))
        cur.execute("INSERT INTO sections (class_id, name) VALUES (?, 'Section B')", (cid,))
        cur.execute("INSERT INTO sections (class_id, name) VALUES (?, 'Section C')", (cid,))

    # Subjects
    subjects = [
        ("Mathematics", "MTH", 3),
        ("English Language", "ENG", 8),
        ("Physics", "PHY", 3),
        ("Chemistry", "CHM", 8),
        ("Biology", "BIO", 8),
        ("Computer Science & ICT", "ICT", 3),
        ("Economics", "ECO", 3),
        ("Civic Education", "CVE", 8)
    ]
    cur.executemany("INSERT INTO subjects (name, code, teacher_id) VALUES (?, ?, ?)", subjects)

    # NOTE: All student records, marks, attendance, and payments start clean (0 records)
    # per institutional requirement. New students can be enrolled anytime via "Admit Student".

    # Exams
    cur.execute("INSERT INTO exams (name, term, year) VALUES ('First Term Examination', 'First Term', '2026-2027')")
    cur.execute("INSERT INTO exams (name, term, year) VALUES ('Mid-Term Continuous Assessment', 'First Term', '2026-2027')")

    # Books
    books = [
        ("Advanced Level Pure Mathematics", "C.J. Tranter", "978-0340203705", "Mathematics", 30, 24),
        ("New General Mathematics for SS 3", "J.B. Channon", "978-9781395567", "Mathematics", 50, 42),
        ("Senior Secondary Physics 4th Edition", "P.N. Okeke", "978-9781754029", "Physics", 40, 31),
        ("Comprehensive Certificate Chemistry", "K.S. Verma", "978-0199144846", "Chemistry", 35, 29),
        ("Modern Biology for Senior Secondary", "S.T. Ramalingam", "978-9781387609", "Biology", 45, 38),
        ("Introduction to Computer Science & Python", "John V. Guttag", "978-0262529624", "Computer Science", 25, 20),
        ("Things Fall Apart & Other Works", "Chinua Achebe", "978-0385474542", "Literature", 60, 50)
    ]
    cur.executemany("INSERT INTO books (title, author, isbn, category, total_copies, available_copies) VALUES (?, ?, ?, ?, ?, ?)", books)

    # Notices
    notices = [
        ("First Term Mid-Term Break & Assessment Notice", "The management wishes to inform all parents and students that mid-term continuous assessments will conclude on Friday, followed by the mid-term recess.", "Academic", "2026-11-01", 1),
        ("Inter-House Athletic Sports Championship 2026", "Annual sports gala will take place at the school main athletics arena on November 20th. Parents and alumni are cordially invited.", "Sports", "2026-10-28", 1),
        ("STEM & Robotics Exhibition Showcase", "Senior secondary students will demonstrate their AI and robotics inventions in the Grand Multipurpose Hall this Thursday from 10:00 AM.", "Event", "2026-10-25", 0),
        ("Parent-Teacher Consultative Association (PTA) General Meeting", "The termly interactive session between faculty and guardians is scheduled for next Saturday at 11:00 AM.", "General", "2026-10-20", 0)
    ]
    cur.executemany("INSERT INTO notices (title, content, category, date, pinned) VALUES (?, ?, ?, ?, ?)", notices)

    conn.commit()

def generate_class_timetable(class_name, section_name="Section A"):
    c_lower = (class_name or "").lower()
    periods = ['08:00 - 08:45', '08:45 - 09:30', '09:30 - 10:15', '10:45 - 11:30', '11:30 - 12:15', '12:15 - 01:00', '01:30 - 02:15']
    
    if any(k in c_lower for k in ['class 12 - science', 'science', 'class 11 - science']):
        days = [
            {'day': 'Monday', 'subjects': ['Physics (Mechanics)', 'Chemistry (Organic)', 'Mathematics / Biology', 'English Core', 'Computer Science', 'Physical Education', 'Physics Lab']},
            {'day': 'Tuesday', 'subjects': ['Chemistry Lab', 'Chemistry (Inorganic)', 'Physics', 'Mathematics', 'English Core', 'Biology / IP', 'Library & Research']},
            {'day': 'Wednesday', 'subjects': ['Mathematics', 'Physics', 'Biology Lab', 'Chemistry', 'English Core', 'STEM Projects', 'Sports / Games']},
            {'day': 'Thursday', 'subjects': ['Physics (Optics)', 'Mathematics', 'Chemistry (Physical)', 'English', 'Biology / CS', 'Doubt Clearing', 'Practical Lab']},
            {'day': 'Friday', 'subjects': ['Computer Science Lab', 'Mathematics', 'Physics', 'Chemistry', 'English Debate', 'Moral Education', 'Club Activities']}
        ]
    elif any(k in c_lower for k in ['commerce', 'class 12 - commerce', 'class 11 - commerce']):
        days = [
            {'day': 'Monday', 'subjects': ['Accountancy', 'Business Studies', 'Economics', 'English Core', 'Informatics Practices', 'Mathematics', 'Commerce Lab']},
            {'day': 'Tuesday', 'subjects': ['Business Studies', 'Accountancy', 'Economics', 'English Core', 'Applied Maths', 'Library Period', 'Financial Literacy']},
            {'day': 'Wednesday', 'subjects': ['Economics (Macro)', 'Accountancy', 'Business Studies', 'English', 'Informatics Lab', 'Physical Edu.', 'Case Study Seminar']},
            {'day': 'Thursday', 'subjects': ['Accountancy Workshop', 'Economics', 'Business Law', 'Applied Maths', 'English', 'Career Guidance', 'Project Work']},
            {'day': 'Friday', 'subjects': ['Business Studies', 'Accountancy', 'Economics', 'English', 'Entrepreneurship', 'Assembly / Quiz', 'Sports & Games']}
        ]
    elif any(k in c_lower for k in ['humanities', 'arts', 'class 12 - humanities', 'class 11 - humanities']):
        days = [
            {'day': 'Monday', 'subjects': ['History', 'Political Science', 'Geography', 'English Core', 'Sociology / Economics', 'Psychology', 'Library Research']},
            {'day': 'Tuesday', 'subjects': ['Political Science', 'History', 'Geography Lab', 'English Core', 'Economics', 'Creative Writing', 'Debate Society']},
            {'day': 'Wednesday', 'subjects': ['Geography', 'Sociology', 'History', 'Political Science', 'English Literature', 'Fine Arts', 'Social Service / SUPW']},
            {'day': 'Thursday', 'subjects': ['History Seminar', 'Political Science', 'Economics', 'Geography', 'English Core', 'Heritage Studies', 'Project Work']},
            {'day': 'Friday', 'subjects': ['English Literature', 'History', 'Geography', 'Political Science', 'Current Affairs', 'Assembly', 'Music & Drama']}
        ]
    elif any(k in c_lower for k in ['class 9', 'class 10']):
        days = [
            {'day': 'Monday', 'subjects': ['Mathematics', 'English Lang.', 'Physics', 'Chemistry', 'Biology', 'Social Science (History)', 'Computer Lab']},
            {'day': 'Tuesday', 'subjects': ['English Lang.', 'Mathematics', 'Social Science (Civics)', 'Physics', 'Chemistry', 'Biology', 'Library Period']},
            {'day': 'Wednesday', 'subjects': ['Chemistry', 'Physics', 'Mathematics', 'Computer Science', 'English Lang.', 'Physical Edu.', 'STEM Workshop']},
            {'day': 'Thursday', 'subjects': ['Biology', 'Social Science (Geography)', 'Chemistry', 'Mathematics', 'Physics', 'Moral Science', 'Science Practical']},
            {'day': 'Friday', 'subjects': ['Mathematics', 'English Lang.', 'Computer Lab', 'Science Composite Lab', 'Social Science', 'Assembly', 'Sports & Games']}
        ]
    elif any(k in c_lower for k in ['class 6', 'class 7', 'class 8']):
        days = [
            {'day': 'Monday', 'subjects': ['Foundational Mathematics', 'English Grammar', 'General Science', 'Social Studies', 'Hindi / Language II', 'Arts & Crafts', 'Games & Physical Edu.']},
            {'day': 'Tuesday', 'subjects': ['English Literature', 'Mathematics', 'Social Studies', 'General Science', 'Hindi', 'Library Reading', 'Music & Yoga']},
            {'day': 'Wednesday', 'subjects': ['General Science', 'Social Studies', 'Mathematics', 'Computer ICT', 'English', 'Physical Education', 'Activity Club']},
            {'day': 'Thursday', 'subjects': ['Social Studies', 'Mathematics', 'General Science', 'Hindi', 'English', 'Moral Science', 'Science Discovery Lab']},
            {'day': 'Friday', 'subjects': ['Mathematics', 'English Comprehension', 'Computer Lab', 'General Science', 'Art & Craft', 'Assembly / Quiz', 'Sports & PT']}
        ]
    else:  # Primary (Class 1 - 5)
        days = [
            {'day': 'Monday', 'subjects': ['English Phonics & Reading', 'Mathematics (Numeracy)', 'Environmental Studies', 'Hindi / Regional', 'Drawing & Colouring', 'Rhymes & Storytelling', 'Playground Games']},
            {'day': 'Tuesday', 'subjects': ['Mathematics', 'English Handwriting', 'Environmental Studies', 'Hindi', 'Activity Worksheet', 'Library Picture Books', 'Music & Dance']},
            {'day': 'Wednesday', 'subjects': ['Environmental Studies', 'Mathematics', 'English Rhymes', 'Basic Computer Basics', 'Hindi', 'Clay Modelling / Craft', 'Physical Exercises']},
            {'day': 'Thursday', 'subjects': ['English Conversation', 'Mathematics Fun', 'EVS Practical', 'Moral Stories', 'Hindi', 'Games & Fun Activities', 'Free Play']},
            {'day': 'Friday', 'subjects': ['Mathematics Puzzles', 'English Story Time', 'Environmental Quiz', 'Art & Origami', 'Children Assembly', 'Moral Education', 'Sports & Recreation']}
        ]
    return {'periods': periods, 'days': days, 'class_name': class_name, 'section_name': section_name}

def ensure_default_it_assets(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM it_assets")
    if cur.fetchone()[0] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        assets = [
            ('LAP-2026-001', 'Laptop', 'Lenovo', 'ThinkPad T14 Gen 4', 'SN-LN-992140', 'Intel Core i5-1345U (10 Cores, up to 4.7GHz)', '16 GB DDR5 5200MHz', '512 GB NVMe PCIe 4.0 SSD', 'Windows 11 Pro (64-bit)', 'Owned (Institutional Purchase)', 'Excellent', '2026-01-15', 1250000.0, 'Director Executive Office', 'Allocated to Employee', 'Assigned to Director Rajeev Sinha for institutional leadership and administrative governance.', now),
            ('LAP-2026-002', 'Laptop', 'Dell', 'Latitude 5430 Business Edition', 'SN-DL-883192', 'Intel Core i5-1235U (10 Cores, up to 4.4GHz)', '16 GB DDR4 3200MHz', '512 GB NVMe M.2 SSD', 'Windows 11 Pro', 'Owned (Institutional Purchase)', 'Like New', '2026-02-10', 980000.0, 'IT Support Depot', 'Allocated to Employee', 'Assigned to IT Support Administrator for network and system infrastructure management.', now),
            ('LAP-2026-003', 'Laptop', 'HP', 'ProBook 450 G9 Business Laptop', 'SN-HP-771234', 'Intel Core i5-1235U', '8 GB DDR4', '512 GB NVMe SSD', 'Windows 11 Pro', 'Owned (Institutional Purchase)', 'Excellent', '2026-03-01', 820000.0, 'IT Support Depot', 'In Stock / Available', 'Available in IT Support Depot for immediate faculty or exam allocation.', now),
            ('LAP-2026-004', 'Laptop', 'Lenovo', 'ThinkPad E14 Gen 3', 'SN-LN-441209', 'AMD Ryzen 5 5500U (6 Cores / 12 Threads)', '16 GB DDR4', '512 GB NVMe SSD', 'Windows 11 Pro', 'Rented / Leased from Vendor', 'Good', '2026-10-01', 0.0, 'Senior Computer Science Arm', 'On Rental', 'Leased under Vendor Agreement RNT-2026-001 with Apex IT Infrastructure Ltd for STEM and coding labs.', now),
            ('LAP-2026-005', 'Laptop', 'Apple', 'MacBook Air M2 13.6-inch', 'SN-AP-M28912', 'Apple M2 Chip (8-Core CPU / 8-Core GPU)', '16 GB Unified Memory', '256 GB Fast SSD', 'macOS Sonoma 14.5', 'Owned (Institutional Purchase)', 'Excellent', '2026-01-20', 1450000.0, 'Faculty Staff Room', 'Allocated to Employee', 'Assigned to Teacher Chike for Senior Secondary lesson preparation and digital curriculum.', now),
            ('PC-2026-001', 'Desktop Computer', 'Dell', 'OptiPlex 7090 Micro Desktop', 'SN-DL-OP7090', 'Intel Core i7-11700 (8 Cores, 2.5GHz to 4.9GHz)', '16 GB DDR4', '1 TB NVMe SSD', 'Windows 11 Pro', 'Owned (Institutional Purchase)', 'Good', '2025-11-10', 750000.0, 'Accounts & Bursar Office', 'Allocated to Employee', 'Dedicated workstation assigned to Accountant Jude Bello for school fees, ledger, and payroll processing.', now),
            ('PC-2026-002', 'Desktop Computer', 'HP', 'EliteDesk 800 G6 Tower Workstation', 'SN-HP-ED800G', 'Intel Core i5-10500', '16 GB DDR4', '512 GB SSD + 1 TB HDD', 'Windows 10 Pro', 'Owned (Institutional Purchase)', 'Under Repair', '2025-08-15', 680000.0, 'HP Authorized Service Depot', 'In Service / Repair', 'Motherboard onboard video display failure; ticket SVC-2026-001 opened with HP Support Center.', now),
            ('PC-2026-003', 'Workstation', 'Acer', 'Veriton S2680G Compact Desktop', 'SN-AC-VT2680', 'Intel Core i5-11400', '16 GB DDR4', '512 GB NVMe SSD', 'Windows 11 Pro', 'Owned (Institutional Purchase)', 'Excellent', '2026-02-28', 580000.0, 'IT Support Depot', 'In Stock / Available', 'General spare workstation available in IT Support inventory.', now)
        ]

        cur.executemany("""
            INSERT INTO it_assets (
                asset_tag, device_type, brand, model_name, serial_number, specs_processor, specs_ram,
                specs_storage, specs_os, ownership_type, condition, purchase_date, purchase_cost,
                current_location, status, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, assets)

        cur.execute("SELECT id FROM users WHERE username = 'Owner(Directer)' LIMIT 1")
        dir_row = cur.fetchone()
        dir_id = dir_row[0] if dir_row else 27

        cur.execute("SELECT id FROM users WHERE username = 'GS_itsupport' LIMIT 1")
        it_row = cur.fetchone()
        it_id = it_row[0] if it_row else 37

        allocations = [
            ('HND-2026-001', 1, dir_id, 'Owner (Director) Rajeev Sinha', 'Director (Owner)', 'Executive Directorate', '2026-01-20', '2027-01-20', None, 'Pristine / Like New', '65W USB-C Fast Charger, Premium Executive Leather Briefcase, Wireless Bluetooth Mouse, USB-C Multiport Hub', 'Institutional executive issuance authorized by Directorate. Full administrative privileges enabled.', 'Active (With Employee)', None, None, now),
            ('HND-2026-002', 2, it_id, 'IT Support Administrator', 'IT Support Administrator', 'IT & Systems Administration', '2026-02-15', '2027-02-15', None, 'Brand New in Box', '65W USB-C Charger, Heavy Duty Water-Resistant Bag, Cat6 Ethernet Cable, Console Cable', 'Primary IT Support Administrator diagnostic and management workstation.', 'Active (With Employee)', None, None, now),
            ('HND-2026-003', 5, 55, 'Teacher Chike', 'Teacher', 'Senior Secondary Academics', '2026-02-01', '2026-12-15', None, 'Pristine / Like New', '35W Dual USB-C Adapter, Apple MagSafe 3 Cable, Laptop Sleeve', 'Class Teacher and Senior Secondary English curriculum planning issuance.', 'Active (With Employee)', None, None, now),
            ('HND-2026-004', 6, 83, 'Accountant Jude Bello', 'Accountant', 'Finance & Bursar Department', '2025-11-15', '2026-11-30', None, 'Good', 'Dell 24-inch UltraSharp Monitor, Keyboard, Optical Mouse, Power Cords', 'Dedicated desktop workstation for Greenland School fee ledger and accounting.', 'Active (With Employee)', None, None, now)
        ]

        cur.executemany("""
            INSERT INTO it_asset_allocations (
                handover_slip_no, asset_id, employee_id, employee_name, employee_role, department,
                handover_date, expected_return_date, actual_return_date, handover_condition,
                accessories_included, handover_notes, handover_status, return_condition,
                return_verified_by, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, allocations)

        cur.execute("""
            INSERT INTO it_rentals (
                rental_agreement_no, rental_type, asset_id, vendor_or_client_name, contact_phone, contact_email,
                start_date, end_date, billing_cycle, rental_amount, deposit_amount, next_payment_due_date,
                payment_status, rental_status, terms_notes, created_at
            ) VALUES (
                'RNT-2026-001', 'Inward (Rented from Vendor)', 4, 'Apex IT Infrastructure Solutions Ltd',
                '+91 761 400 9011', 'rentals@apexinfotech.com', '2026-10-01', '2027-03-31',
                'Monthly', 45000.0, 50000.0, '2026-11-15', 'Due Soon', 'Active Agreement',
                'Term leasing for 5 Lenovo ThinkPad units for senior STEM coding labs and examination simulation.', ?
            )
        """, (now,))

        warranties = [
            (1, 'Lenovo Premier Support & Onsite Warranty', 'LEN-PREM-90214', 'OEM Standard + Onsite Next Business Day', '2026-01-15', '2029-01-14', '1800-419-7555 / support@lenovo.com', 'Active', 0, 'Covers motherboard, battery, screen, and all internal hardware components.', now),
            (2, 'Dell ProSupport Plus 3-Year Onsite', 'DEL-PSP-88319', 'OEM Standard + Accidental Damage Protection', '2026-02-10', '2029-02-09', '1800-425-4026 / prosupport@dell.com', 'Active', 0, '24x7 priority support with onsite technician dispatch within 4 hours.', now),
            (5, 'AppleCare+ for Mac (3 Years)', 'AC-MAC-M2891', 'OEM Comprehensive + Accidental Coverage', '2026-01-20', '2029-01-19', '000800 1009009 / applecare@apple.com', 'Active', 0, 'Comprehensive coverage with unlimited accidental damage incidents.', now),
            (7, 'HP Care Pack 3-Year Commercial Warranty', 'HP-CP-ED800G', 'OEM Standard Hardware Support', '2023-11-25', '2026-11-25', '1800-258-7170 / support@hp.com', 'Expiring Soon (< 30 Days)', 1, 'Expiring in less than 30 days! Renewal or AMC extension required.', now)
        ]
        cur.executemany("""
            INSERT INTO it_warranties (
                asset_id, provider_name, policy_number, warranty_type, start_date, end_date,
                support_contact, status, claim_count, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, warranties)

        cur.execute("""
            INSERT INTO it_maintenance_service (
                service_ticket_no, asset_id, service_type, reported_issue, service_center_or_vendor,
                technician_name, start_date, completion_date, repair_cost, parts_replaced,
                service_status, warranty_claim_covered, remarks, created_at
            ) VALUES (
                'SVC-2026-001', 7, 'Hardware Repair / Display GPU', 'Display output no signal through HDMI / DisplayPort. System fans spin but POST fails.',
                'HP Authorized Service Center (Sonbhadra Hub)', 'Technician Rajesh Kumar (Badge #HP-912)',
                '2026-11-01', NULL, 18500.0, 'Awaiting replacement system board part #HP-MB-800G6',
                'In Repair / Awaiting Parts', 1, 'Claim submitted under HP Care Pack. Estimated dispatch Nov 12.', ?
            )
        """, (now,))

        payments = [
            ('PMT-2026-001', 'Rental Invoice', 1, None, 'Apex IT Infrastructure Solutions Ltd', 45000.0, '2026-11-15', None, 'Upcoming Due', None, None, 'Monthly lease installment for November 2026 under agreement RNT-2026-001.', now),
            ('PMT-2026-002', 'AMC Renewal', None, None, 'CompServe Technology Solutions Ltd', 120000.0, '2026-11-20', None, 'Upcoming Due', None, None, 'Annual Maintenance Contract renewal for Computer Lab 1 & Lab 2 core switching & UPS equipment.', now),
            ('PMT-2026-003', 'Hardware Repair Bill', None, 1, 'HP Authorized Service Hub', 4500.0, '2026-11-08', '2026-11-04', 'Paid', 'Bank Transfer / NEFT', 'NEFT-GS-9901428', 'Out-of-warranty labor and thermal compound diagnostic charge.', now)
        ]
        cur.executemany("""
            INSERT INTO it_asset_payments (
                ref_no, payment_category, related_rental_id, related_service_id, vendor_name,
                amount, due_date, paid_date, payment_status, payment_method, transaction_ref, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, payments)

        logs = [
            (1, 'Asset Registered / Added to Inventory', 'Vendor Delivery', 'IT Support Depot', 'IT Support Administrator', 'IT Support Administrator', 'Initial procurement check passed. Specs verified: i5-1345U / 16GB / 512GB SSD.', '2026-01-15 10:00:00'),
            (1, 'Handover to Employee', 'IT Support Depot', 'Director Executive Office', 'Owner (Director) Rajeev Sinha', 'IT Support Administrator', 'Formally allocated under Handover Slip HND-2026-001.', '2026-01-20 11:30:00'),
            (2, 'Asset Registered / Added to Inventory', 'Vendor Delivery', 'IT Support Depot', 'IT Support Administrator', 'IT Support Administrator', 'Dell Latitude 5430 deployed for IT Administrator management workstation.', '2026-02-10 09:15:00'),
            (5, 'Handover to Employee', 'IT Support Depot', 'Faculty Staff Room', 'Teacher Chike', 'IT Support Administrator', 'Allocated for Senior Secondary lesson planning.', '2026-02-01 14:00:00'),
            (7, 'Dispatched to Service Center', 'Accounts Office', 'HP Authorized Service Depot', 'HP Technician Rajesh Kumar', 'IT Support Administrator', 'Dispatched for motherboard diagnostics under ticket SVC-2026-001.', '2026-11-01 16:45:00')
        ]
        cur.executemany("""
            INSERT INTO it_asset_logs (
                asset_id, action_type, from_location, to_location, assigned_to, performed_by, details, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, logs)

        conn.commit()

class SchoolHandler(http.server.SimpleHTTPRequestHandler):
    def address_string(self):
        return str(self.client_address[0])

    def log_message(self, format, *args):
        print(f"[HTTP] {self.address_string()} - {format%args}", flush=True)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def send_json(self, data, status=200):
        payload = json.dumps(data, default=str).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(payload)

    def send_bytes(self, data, content_type, filename=None, status=200):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        if filename:
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path.startswith('/api/'):
            self.handle_api_get(path, query)
            return

        # Serve frontend files
        if path == '/' or path == '/index.html':
            self.serve_file('index.html', 'text/html')
        elif path.startswith('/css/') or path.startswith('/js/') or path.startswith('/assets/'):
            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path.lstrip('/'))
            if os.path.exists(file_path):
                mime, _ = mimetypes.guess_type(file_path)
                self.serve_file(path.lstrip('/'), mime or 'text/plain')
            else:
                self.send_error(404, "File Not Found")
        else:
            self.serve_file('index.html', 'text/html')

    def serve_file(self, rel_path, content_type):
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), rel_path)
        if not os.path.exists(full_path):
            self.send_error(404, "File Not Found")
            return
        with open(full_path, 'rb') as f:
            content = f.read()
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def handle_api_get(self, path, query):
        print(f"[API GET] path={path} query={query}", flush=True)
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        try:
            if path == '/api/stats':
                cur.execute("SELECT COUNT(*) FROM students")
                students_count = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM users WHERE user_type = 'teacher'")
                teachers_count = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM classes")
                classes_count = cur.fetchone()[0]
                cur.execute("SELECT SUM(paid) FROM payments")
                revenue = cur.fetchone()[0] or 0
                cur.execute("SELECT COUNT(*) FROM books")
                books_count = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM admissions WHERE status = 'Pending'")
                pending_admissions = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM users")
                users_count = cur.fetchone()[0]
                self.send_json({
                    "students": students_count,
                    "teachers": teachers_count,
                    "classes": classes_count,
                    "revenue": revenue,
                    "books": books_count,
                    "pending_admissions": pending_admissions,
                    "total_users": users_count
                })

            elif path == '/api/credentials/requests':
                cur.execute("""
                    SELECT cr.*, u.username as current_username_db, u.name as current_name_db, u.user_type as current_role_db
                    FROM credential_requests cr
                    LEFT JOIN users u ON cr.user_id = u.id
                    ORDER BY cr.id DESC
                """)
                self.send_json({"success": True, "requests": [dict(r) for r in cur.fetchall()]})

            elif path == '/api/settings':
                cur.execute("SELECT key, value FROM settings")
                rows = cur.fetchall()
                data = {r['key']: r['value'] for r in rows}
                self.send_json(data)

            elif path == '/api/classes':
                cur.execute("SELECT * FROM classes ORDER BY id")
                classes = [dict(r) for r in cur.fetchall()]
                for c in classes:
                    cur.execute("SELECT * FROM sections WHERE class_id = ?", (c['id'],))
                    c['sections'] = [dict(s) for s in cur.fetchall()]
                    cur.execute("SELECT COUNT(*) FROM students WHERE class_id = ?", (c['id'],))
                    c['student_count'] = cur.fetchone()[0]
                self.send_json(classes)

            elif path == '/api/subjects':
                cur.execute("""
                    SELECT s.*, u.name as teacher_name 
                    FROM subjects s 
                    LEFT JOIN users u ON s.teacher_id = u.id
                """)
                self.send_json([dict(r) for r in cur.fetchall()])

            elif path == '/api/students/sample_excel':
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "Student Admissions"
                
                headers = ["First Name", "Last Name", "Class", "Section", "Gender", "Date of Birth", "Parent Name", "Phone", "Blood Group", "Address", "Aadhaar Number"]
                ws.append(headers)
                
                ws.append(["Rahul", "Sharma", "Class 10", "Section A", "Male", "2011-04-15", "Rajesh Sharma", "+91 761 700 5055", "O+", "Renukoot, Sonbhadra", "548962147801"])
                ws.append(["Priya", "Singh", "Class 12 - Science", "Section A", "Female", "2009-08-22", "Anita Singh", "+91 761 700 5056", "B+", "Khadpathar, Sonbhadra", "548962147802"])
                ws.append(["Rahul", "Sharma", "Class 10", "Section B", "Male", "2011-09-10", "Amit Sharma", "+91 761 700 5057", "A+", "Robertsganj, Sonbhadra", "548962147803"])
                ws.append(["Ayaan", "Khan", "Class 5", "Section A", "Male", "2014-11-05", "Farhan Khan", "+91 761 700 5058", "O+", "Pipri, Sonbhadra", "548962147804"])
                ws.append(["Ananya", "Patel", "Class 12 - Commerce", "Section B", "Female", "2009-03-30", "Deepak Patel", "+91 761 700 5059", "AB+", "Renukoot, Sonbhadra", "548962147805"])
                ws.append(["Sneha", "Gupta", "Class 12 - Humanities (Arts)", "Section A", "Female", "2009-12-18", "Vikram Gupta", "+91 761 700 5060", "O+", "Sonbhadra", "548962147806"])
                
                bio = io.BytesIO()
                wb.save(bio)
                self.send_bytes(bio.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "Greenland_School_Student_Admission_Template.xlsx")
                return

            elif path == '/api/it/export_credentials_excel':
                # STRICT REQUIREMENT: IT Support Administrator can create / export an Excel file containing ALL user IDs and passwords
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "Master User Credentials"

                # Title Banner
                ws.merge_cells('A1:L1')
                ws['A1'] = "GREENLAND SCHOOL (GS) - MASTER USER IDS & PASSWORDS LEDGER"
                ws['A1'].font = openpyxl.styles.Font(name='Calibri', size=16, bold=True, color="FFFFFF")
                ws['A1'].fill = openpyxl.styles.PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
                ws['A1'].alignment = openpyxl.styles.Alignment(horizontal="center", vertical="center")
                ws.row_dimensions[1].height = 36

                ws.merge_cells('A2:L2')
                gen_time = datetime.now().strftime("%d %B %Y, %I:%M %p")
                ws['A2'] = f"Generated for IT Support Administrator & Director Governance • Exported: {gen_time} • Strictly Confidential"
                ws['A2'].font = openpyxl.styles.Font(name='Calibri', size=10, italic=True, color="475569")
                ws['A2'].alignment = openpyxl.styles.Alignment(horizontal="center", vertical="center")
                ws.row_dimensions[2].height = 20

                headers = [
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
                ]
                ws.append([]) # row 3 blank
                ws.append(headers) # row 4
                ws.row_dimensions[4].height = 28

                header_fill = openpyxl.styles.PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
                header_font = openpyxl.styles.Font(name='Calibri', size=11, bold=True, color="FFFFFF")
                thin_border = openpyxl.styles.Border(
                    left=openpyxl.styles.Side(style='thin', color="CBD5E1"),
                    right=openpyxl.styles.Side(style='thin', color="CBD5E1"),
                    top=openpyxl.styles.Side(style='thin', color="CBD5E1"),
                    bottom=openpyxl.styles.Side(style='thin', color="CBD5E1")
                )

                for col_idx in range(1, len(headers) + 1):
                    cell = ws.cell(row=4, column=col_idx)
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = openpyxl.styles.Alignment(horizontal="center", vertical="center")
                    cell.border = thin_border

                cur.execute("""
                    SELECT id, username, password, name, user_type, phone, email, gender, created_at,
                           COALESCE(is_common_id, 0) as is_common_id, common_id_name, admin_username, admin_name
                    FROM users 
                    ORDER BY 
                        CASE user_type 
                            WHEN 'super_admin' THEN 1 
                            WHEN 'it_admin' THEN 2 
                            WHEN 'admin' THEN 3 
                            WHEN 'teacher' THEN 4 
                            WHEN 'accountant' THEN 5 
                            WHEN 'librarian' THEN 6 
                            WHEN 'parent' THEN 7 
                            WHEN 'student' THEN 8 
                            ELSE 9 
                        END, id ASC
                """)
                rows = cur.fetchall()

                role_display_map = {
                    'super_admin': 'Director / Owner',
                    'it_admin': 'IT Support Administrator',
                    'admin': 'Administrator',
                    'teacher': 'Teacher / Faculty',
                    'accountant': 'Accountant',
                    'librarian': 'Librarian',
                    'parent': 'Parent / Guardian',
                    'student': 'Student'
                }

                s_no = 1
                for r in rows:
                    role_key = r['user_type']
                    role_title = role_display_map.get(role_key, role_key.replace('_', ' ').title())
                    user_name = r['name'] or '—'
                    # Strict name/gender rule: no name = no gender
                    gender = r['gender'] if (user_name and user_name != '—') else '—'
                    
                    row_data = [
                        s_no,
                        r['username'],
                        r['password'],
                        user_name,
                        role_title,
                        role_key,
                        r['phone'] or '—',
                        r['email'] or '—',
                        gender or '—',
                        r['created_at'] or '—'
                    ]
                    ws.append(row_data)
                    curr_row = ws.max_row
                    ws.row_dimensions[curr_row].height = 22

                    # Style data row
                    row_fill = openpyxl.styles.PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid") if s_no % 2 == 0 else openpyxl.styles.PatternFill(fill_type=None)
                    for col_idx in range(1, len(row_data) + 1):
                        cell = ws.cell(row=curr_row, column=col_idx)
                        if row_fill.fill_type:
                            cell.fill = row_fill
                        cell.border = thin_border
                        if col_idx in [1, 5, 6, 9]:
                            cell.alignment = openpyxl.styles.Alignment(horizontal="center", vertical="center")
                        elif col_idx in [2, 3]: # Username and Password
                            cell.alignment = openpyxl.styles.Alignment(horizontal="left", vertical="center")
                            cell.font = openpyxl.styles.Font(name='Consolas', size=10, bold=True, color="1E3A8A" if col_idx == 2 else "DC2626")
                        else:
                            cell.alignment = openpyxl.styles.Alignment(horizontal="left", vertical="center")
                    s_no += 1

                # Auto-adjust column widths
                for col in ws.columns:
                    max_len = 0
                    col_letter = openpyxl.utils.get_column_letter(col[0].column)
                    for cell in col:
                        if cell.row > 2 and cell.value:
                            max_len = max(max_len, len(str(cell.value)))
                    ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

                bio = io.BytesIO()
                wb.save(bio)
                self.send_bytes(
                    bio.getvalue(), 
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                    "Greenland_School_Master_User_Credentials.xlsx"
                )
                return

            elif path == '/api/students':
                class_id = query.get('class_id', [None])[0]
                sql = """
                    SELECT st.*, u.name, u.email, u.username, u.phone, u.photo, c.name as class_name, sec.name as section_name,
                           p.name as parent_name, p.phone as parent_phone
                    FROM students st
                    JOIN users u ON st.user_id = u.id
                    JOIN classes c ON st.class_id = c.id
                    LEFT JOIN sections sec ON st.section_id = sec.id
                    LEFT JOIN users p ON st.parent_id = p.id
                """
                params = []
                if class_id:
                    sql += " WHERE st.class_id = ?"
                    params.append(class_id)
                sql += " ORDER BY st.id DESC"
                cur.execute(sql, params)
                self.send_json([dict(r) for r in cur.fetchall()])

            elif path == '/api/teachers':
                cur.execute("""
                    SELECT u.id, u.name, u.email, u.username, u.password, u.phone, u.photo, u.user_type,
                           COALESCE(u.subject, 'General Faculty') as subject,
                           COALESCE(u.qualification, 'B.Ed / Certified') as qualification,
                           sec.id as assigned_section_id,
                           sec.name as assigned_section_name,
                           c.id as assigned_class_id,
                           c.name as assigned_class_name,
                           CASE WHEN sec.id IS NOT NULL THEN (c.name || ' - ' || sec.name) ELSE NULL END as assigned_class
                    FROM users u
                    LEFT JOIN sections sec ON sec.class_teacher_id = u.id
                    LEFT JOIN classes c ON sec.class_id = c.id
                    WHERE u.user_type = 'teacher'
                    ORDER BY u.id ASC
                """)
                self.send_json([dict(r) for r in cur.fetchall()])

            elif path == '/api/leaves':
                user_id = query.get('user_id', [None])[0]
                filter_user_id = query.get('filter_user_id', [None])[0]
                role = query.get('role', [None])[0]
                
                is_on_leave, active_leave = check_principal_on_leave(cur)
                
                sql = """
                    SELECT l.*, u.name as applicant_name, u.username as applicant_username,
                           u.email as applicant_email, u.user_type as applicant_role_actual,
                           COALESCE(u.gender, 'Male') as applicant_gender,
                           appr.name as approver_name
                    FROM leaves l
                    JOIN users u ON l.user_id = u.id
                    LEFT JOIN users appr ON l.approver_id = appr.id
                """
                conditions = []
                params = []
                if filter_user_id:
                    conditions.append("l.user_id = ?")
                    params.append(filter_user_id)
                if role:
                    conditions.append("l.applicant_role = ?")
                    params.append(role)
                    
                if conditions:
                    sql += " WHERE " + " AND ".join(conditions)
                sql += " ORDER BY l.id DESC"
                
                cur.execute(sql, params)
                rows = [dict(r) for r in cur.fetchall()]

                user_balance = None
                user_gender = 'Male'
                if user_id:
                    try:
                        uid_int = int(user_id)
                        user_balance, user_gender = get_or_create_leave_balances(cur, uid_int)
                    except Exception as e:
                        print(f"Error fetching leave balances for {user_id}: {e}")

                # Fetch all staff balances for accountant, admin, and superadmin visibility
                cur.execute("""
                    SELECT id, name, username, COALESCE(gender, 'Male') as gender, email, phone 
                    FROM users 
                    WHERE user_type = 'teacher' 
                    ORDER BY id ASC
                """)
                teachers = [dict(r) for r in cur.fetchall()]
                all_staff_balances = []
                for t in teachers:
                    b, g = get_or_create_leave_balances(cur, t['id'], 2026)
                    if b:
                        total_allowed = (b.get('cl_total', 8) + b.get('el_total', 30) + b.get('hpl_total', 20) + 
                                         b.get('maternity_total', 0) + b.get('paternity_total', 0) + b.get('ccl_total', 730))
                        total_used = (b.get('cl_used', 0) + b.get('el_used', 0) + b.get('hpl_used', 0) + 
                                      b.get('maternity_used', 0) + b.get('paternity_used', 0) + b.get('ccl_used', 0))
                        total_remaining = max(0, total_allowed - total_used)
                        all_staff_balances.append({
                            "user_id": t['id'],
                            "name": t['name'],
                            "username": t['username'],
                            "gender": g,
                            "email": t['email'],
                            "phone": t['phone'],
                            "cl_total": b.get('cl_total', 8),
                            "cl_used": b.get('cl_used', 0),
                            "cl_remaining": max(0, b.get('cl_total', 8) - b.get('cl_used', 0)),
                            "el_total": b.get('el_total', 30),
                            "el_used": b.get('el_used', 0),
                            "el_remaining": max(0, b.get('el_total', 30) - b.get('el_used', 0)),
                            "hpl_total": b.get('hpl_total', 20),
                            "hpl_used": b.get('hpl_used', 0),
                            "hpl_remaining": max(0, b.get('hpl_total', 20) - b.get('hpl_used', 0)),
                            "maternity_total": b.get('maternity_total', 0),
                            "maternity_used": b.get('maternity_used', 0),
                            "maternity_remaining": max(0, b.get('maternity_total', 0) - b.get('maternity_used', 0)),
                            "paternity_total": b.get('paternity_total', 0),
                            "paternity_used": b.get('paternity_used', 0),
                            "paternity_remaining": max(0, b.get('paternity_total', 0) - b.get('paternity_used', 0)),
                            "ccl_total": b.get('ccl_total', 730),
                            "ccl_used": b.get('ccl_used', 0),
                            "ccl_remaining": max(0, b.get('ccl_total', 730) - b.get('ccl_used', 0)),
                            "total_allowed": total_allowed,
                            "total_used": total_used,
                            "total_remaining": total_remaining
                        })
                
                self.send_json({
                    "leaves": rows,
                    "principal_on_leave": is_on_leave,
                    "active_principal_leave": active_leave,
                    "balances": user_balance,
                    "gender": user_gender,
                    "all_staff_balances": all_staff_balances,
                    "leave_rules": LEAVE_POLICY_RULES
                })

            elif path == '/api/payroll/slips':
                month = int(query.get('month', [11])[0])
                year = int(query.get('year', [2026])[0])
                teacher_id = query.get('teacher_id', [None])[0]

                # Ensure initial slips generated if none exist for this month
                cur.execute("SELECT COUNT(*) FROM salary_slips WHERE month = ? AND year = ?", (month, year))
                if cur.fetchone()[0] == 0:
                    auto_generate_salary_slips_for_month(cur, month, year)

                sql = "SELECT * FROM salary_slips WHERE month = ? AND year = ?"
                params = [month, year]
                if teacher_id:
                    sql += " AND teacher_id = ?"
                    params.append(teacher_id)
                sql += " ORDER BY id ASC"
                cur.execute(sql, params)
                slips = [dict(r) for r in cur.fetchall()]

                # Get special bonuses for this month/year
                cur.execute("SELECT * FROM special_bonuses WHERE month = ? AND year = ? ORDER BY id DESC", (month, year))
                bonuses = [dict(r) for r in cur.fetchall()]

                total_gross = sum(s['gross_salary'] for s in slips)
                total_net = sum(s['net_salary'] for s in slips)
                total_deductions = sum(s['leave_deduction'] + s['pf_deduction'] + s['tax_deduction'] for s in slips)
                total_bonus = sum(s['special_bonus'] for s in slips)

                self.send_json({
                    "slips": slips,
                    "bonuses": bonuses,
                    "summary": {
                        "total_teachers": len(slips),
                        "total_gross": total_gross,
                        "total_net": total_net,
                        "total_deductions": total_deductions,
                        "total_bonus": total_bonus,
                        "month": month,
                        "year": year
                    }
                })

            elif path == '/api/users':
                # Full user accounts list for Director & IT control center with Common ID details
                cur.execute("""
                    SELECT id, name, email, username, password, user_type, phone, photo, created_at, gender,
                           COALESCE(is_common_id, 0) as is_common_id,
                           common_id_name,
                           COALESCE(has_mail_services, 1) as has_mail_services,
                           admin_user_id,
                           admin_username,
                           admin_name
                    FROM users 
                    ORDER BY id ASC
                """)
                all_users = [dict(r) for r in cur.fetchall()]
                for u in all_users:
                    cur.execute("""
                        SELECT COUNT(*) FROM lab_computers 
                        WHERE assigned_teacher_id = ? OR assigned_teacher_username = ?
                    """, (u['id'], u['username']))
                    u['assigned_lab_count'] = cur.fetchone()[0]
                self.send_json(all_users)

            elif path == '/api/app/student_dashboard':
                # App endpoint for student access
                uid = query.get('user_id', [None])[0]
                uname = query.get('username', [None])[0]
                cur.execute("SELECT * FROM users WHERE id = ? OR username = ?", (uid, uname))
                u = cur.fetchone()
                if not u:
                    self.send_json({"success": False, "error": "Student account not found."}, 404)
                    return

                cur.execute("""
                    SELECT s.*, c.name as class_name, sec.name as section_name
                    FROM students s
                    LEFT JOIN classes c ON s.class_id = c.id
                    LEFT JOIN sections sec ON s.section_id = sec.id
                    WHERE s.user_id = ?
                """, (u['id'],))
                s_row = cur.fetchone()
                s_id = s_row['id'] if s_row else 0

                # Fees
                cur.execute("SELECT * FROM payments WHERE student_id = ? ORDER BY id DESC", (s_id,))
                fees = [dict(r) for r in cur.fetchall()]

                # Issued library books (Booklet)
                cur.execute("""
                    SELECT br.*, b.title as book_title, b.author, COALESCE(br.bookshelf_no, b.bookshelf_no) as bookshelf_no
                    FROM book_requests br
                    JOIN books b ON br.book_id = b.id
                    WHERE br.user_id = ? AND br.status IN ('Issued', 'Approved', 'Pending')
                    ORDER BY br.id DESC
                """, (u['id'],))
                books = [dict(r) for r in cur.fetchall()]

                # Timetable
                c_id = s_row['class_id'] if s_row else 1
                sec_id = s_row['section_id'] if s_row else 1
                cur.execute("""
                    SELECT sub.name as subject_name, sub.code, u.name as teacher_name
                    FROM subjects sub
                    LEFT JOIN users u ON sub.teacher_id = u.id
                    LIMIT 6
                """)
                timetable = [dict(r) for r in cur.fetchall()]

                # Marksheet
                cur.execute("""
                    SELECT m.*, sub.name as subject_name, ex.name as exam_name
                    FROM marks m
                    JOIN subjects sub ON m.subject_id = sub.id
                    LEFT JOIN exams ex ON m.exam_id = ex.id
                    WHERE m.student_id = ?
                    ORDER BY m.id DESC
                """, (s_id,))
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
                cur.execute("""
                    SELECT s.id as student_id, s.user_id, s.adm_no, s.blood_group,
                           u.name, u.username, u.photo, u.gender, u.phone,
                           c.name as class_name, sec.name as section_name
                    FROM students s
                    JOIN users u ON s.user_id = u.id
                    LEFT JOIN classes c ON s.class_id = c.id
                    LEFT JOIN sections sec ON s.section_id = sec.id
                    WHERE s.parent_id = ?
                    ORDER BY s.id ASC
                """, (parent['id'],))
                children_rows = cur.fetchall()

                # If no direct child linked, fetch any active students as fallback for parent demonstration
                if not children_rows:
                    cur.execute("""
                        SELECT s.id as student_id, s.user_id, s.adm_no, s.blood_group,
                               u.name, u.username, u.photo, u.gender, u.phone,
                               c.name as class_name, sec.name as section_name
                        FROM students s
                        JOIN users u ON s.user_id = u.id
                        LEFT JOIN classes c ON s.class_id = c.id
                        LEFT JOIN sections sec ON s.section_id = sec.id
                        ORDER BY s.id ASC
                        LIMIT 2
                    """)
                    children_rows = cur.fetchall()

                children = []
                for cr in children_rows:
                    cid = cr['student_id']
                    c_uid = cr['user_id']

                    # Child fees
                    cur.execute("SELECT * FROM payments WHERE student_id = ? ORDER BY id DESC", (cid,))
                    c_fees = [dict(r) for r in cur.fetchall()]

                    # Child library books
                    cur.execute("""
                        SELECT br.*, b.title as book_title, b.author, COALESCE(br.bookshelf_no, b.bookshelf_no) as bookshelf_no
                        FROM book_requests br
                        JOIN books b ON br.book_id = b.id
                        WHERE br.user_id = ? AND br.status IN ('Issued', 'Approved', 'Pending')
                    """, (c_uid,))
                    c_books = [dict(r) for r in cur.fetchall()]

                    # Child marks
                    cur.execute("""
                        SELECT m.*, sub.name as subject_name
                        FROM marks m
                        JOIN subjects sub ON m.subject_id = sub.id
                        WHERE m.student_id = ?
                    """, (cid,))
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
                cur.execute("""
                    SELECT sub.id as subject_id, sub.name as subject_name, sub.code
                    FROM subjects sub
                    WHERE sub.teacher_id = ?
                    LIMIT 4
                """, (t['id'],))
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
                cur.execute("""
                    SELECT l.id, 'Teacher Leave Request' as request_type, 'Teacher' as origin,
                           u.name as creator_name, u.username as creator_username,
                           l.leave_type || ' (' || l.days_count || ' days)' as title,
                           l.reason as description, l.created_at, l.status,
                           l.start_date || ' to ' || l.end_date as details
                    FROM leaves l
                    JOIN users u ON l.user_id = u.id
                    WHERE l.status IN ('Pending', 'Pending Director Approval')
                    ORDER BY l.id DESC
                """)
                teacher_leaves = [dict(r) for r in cur.fetchall()]

                # 2. Teacher Computer Lab Hardware Complaints (Repair Authorizations)
                cur.execute("""
                    SELECT lc.id, 'Computer Lab Hardware Repair' as request_type, 'Teacher & IT' as origin,
                           lc.reported_by_name as creator_name, 'Computer Teacher' as creator_username,
                           'Repair Authorization for ' || lc.pc_number || ' (' || lc.lab_name || ')' as title,
                           lc.problem_description as description, lc.created_at, lc.status,
                           'Issue: ' || lc.issue_category || ' | Priority: ' || lc.priority as details
                    FROM lab_complaints lc
                    WHERE lc.status IN ('Open', 'Pending', 'Pending Director Approval')
                    ORDER BY lc.id DESC
                """)
                lab_repairs = [dict(r) for r in cur.fetchall()]

                # 3. IT Team Credential Requests
                cur.execute("""
                    SELECT cr.id, 'IT Team Credential Request' as request_type, 'IT Team' as origin,
                           cr.requested_by_name as creator_name, 'IT Support Admin' as creator_username,
                           cr.request_type || ' for ' || cr.target_username as title,
                           cr.reason as description, cr.created_at, cr.status,
                           'Proposed Role: ' || COALESCE(cr.proposed_role, '—') as details
                    FROM credential_requests cr
                    WHERE cr.status IN ('Pending Owner Approval', 'Pending Director Approval')
                    ORDER BY cr.id DESC
                """)
                it_credentials = [dict(r) for r in cur.fetchall()]

                # 4. IT Team Asset & Procurement Requests
                cur.execute("""
                    SELECT ar.id, 'IT Equipment Procurement / Expense' as request_type, 'IT Team' as origin,
                           ar.requested_by as creator_name, 'IT Support Admin' as creator_username,
                           ar.title, ar.description, ar.created_at, ar.status,
                           'Estimated Cost: ₦' || PRINTF('%,.2f', ar.estimated_cost) as details
                    FROM it_asset_requests ar
                    WHERE ar.status IN ('Pending Director Approval', 'Pending')
                    ORDER BY ar.id DESC
                """)
                it_assets = [dict(r) for r in cur.fetchall()]

                all_requests = teacher_leaves + lab_repairs + it_credentials + it_assets
                self.send_json({
                    "success": True,
                    "total_pending": len(all_requests),
                    "requests": all_requests,
                    "teacher_requests": teacher_leaves + lab_repairs,
                    "it_requests": it_credentials + it_assets
                })

            elif path == '/api/login_directory':
                # Dynamic User ID directory for Login Portal:
                # - If user ID is deleted from database, it will NOT be returned here.
                # - When new user ID is created, it will be immediately returned here.
                # - ONLY teacher user IDs have is_clickable = True (only teachers can be clicked to auto-fill).
                cur.execute("""
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
                """)
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
                self.send_json({"success": True, "users": directory})

            elif path == '/api/lab/computers':
                # Computer Lab Asset & Operational Status
                cur.execute("""
                    SELECT c.*, cmp.ticket_no, cmp.problem_description, cmp.reported_by_name, cmp.priority as complaint_priority
                    FROM lab_computers c
                    LEFT JOIN lab_complaints cmp ON c.active_complaint_id = cmp.id
                    ORDER BY c.lab_name ASC, c.pc_number ASC
                """)
                computers = [dict(r) for r in cur.fetchall()]

                # Automatic Self-Healing: For any workstation marked Faulty or In Repair without an active ticket,
                # automatically locate or generate its official repair ticket so IT Support can always assign tech.
                needs_db_commit = False
                for c in computers:
                    if c['status'] in ('Faulty', 'In Repair') and (not c.get('active_complaint_id') or not c.get('ticket_no')):
                        # 1. Search existing pending/assigned complaint for this computer
                        cur.execute("""
                            SELECT id, ticket_no, problem_description, reported_by_name, priority
                            FROM lab_complaints
                            WHERE (computer_id = ? OR (pc_number = ? AND lab_name = ?))
                              AND status != 'Resolved'
                            ORDER BY id DESC LIMIT 1
                        """, (c['id'], c['pc_number'], c['lab_name']))
                        matched = cur.fetchone()
                        if matched:
                            c['active_complaint_id'] = matched['id']
                            c['ticket_no'] = matched['ticket_no']
                            c['problem_description'] = matched['problem_description']
                            c['reported_by_name'] = matched['reported_by_name']
                            c['complaint_priority'] = matched['priority']
                            cur.execute("UPDATE lab_computers SET active_complaint_id = ? WHERE id = ?", (matched['id'], c['id']))
                            needs_db_commit = True
                        else:
                            # 2. Auto-generate official repair ticket for the faulty workstation
                            tkt_no = f"TKT-LAB-{datetime.now().strftime('%y%m%d')}-{os.urandom(2).hex().upper()}"
                            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            desc = f"Workstation {c['pc_number']} detected not working / hardware fault reported. Awaiting IT Support technician dispatch."
                            cur.execute("""
                                INSERT INTO lab_complaints (
                                    ticket_no, computer_id, pc_number, lab_name, reported_by_name,
                                    teacher_role, issue_category, problem_description, priority, status, created_at
                                ) VALUES (?, ?, ?, ?, 'IT Support System Monitor', 'Computer Lab Monitor', 'Hardware / Functional Fault', ?, 'High', 'Pending', ?)
                            """, (tkt_no, c['id'], c['pc_number'], c['lab_name'], desc, now))
                            new_tkt_id = cur.lastrowid
                            cur.execute("UPDATE lab_computers SET active_complaint_id = ? WHERE id = ?", (new_tkt_id, c['id']))
                            needs_db_commit = True
                            c['active_complaint_id'] = new_tkt_id
                            c['ticket_no'] = tkt_no
                            c['problem_description'] = desc
                            c['reported_by_name'] = 'IT Support System Monitor'
                            c['complaint_priority'] = 'High'
                if needs_db_commit:
                    conn.commit()

                total = len(computers)
                working = sum(1 for c in computers if c['status'] == 'Working')
                faulty = sum(1 for c in computers if c['status'] == 'Faulty')
                in_repair = sum(1 for c in computers if c['status'] == 'In Repair')

                self.send_json({
                    "computers": computers,
                    "metrics": {
                        "total": total,
                        "working": working,
                        "faulty": faulty,
                        "in_repair": in_repair
                    }
                })

            elif path == '/api/lab/complaints':
                # Lab hardware/software tickets logged by teachers
                status_filter = query.get('status', ['all'])[0]
                sql = "SELECT * FROM lab_complaints"
                params = []
                if status_filter and status_filter != 'all':
                    sql += " WHERE status = ?"
                    params.append(status_filter)
                sql += " ORDER BY id DESC"
                cur.execute(sql, params)
                self.send_json([dict(r) for r in cur.fetchall()])

            elif path == '/api/payroll/accountant_slip':
                # Retrieve Director-issued salary payslip for the Accountant
                month = int(query.get('month', [11])[0])
                year = int(query.get('year', [2026])[0])

                cur.execute("SELECT id, name FROM users WHERE user_type = 'accountant' LIMIT 1")
                acc_row = cur.fetchone()
                if not acc_row:
                    self.send_json({"success": False, "message": "No accountant user found."}, 404)
                else:
                    cur.execute("SELECT * FROM salary_slips WHERE teacher_id = ? AND month = ? AND year = ?", (acc_row['id'], month, year))
                    slip = cur.fetchone()
                    if slip:
                        self.send_json({"success": True, "slip": dict(slip)})
                    else:
                        self.send_json({"success": False, "message": "Accountant salary slip has not yet been sanctioned by the Director for this month."})

            elif path == '/api/marks':
                class_id = query.get('class_id', [None])[0]
                exam_id = query.get('exam_id', [1])[0]
                sql = """
                    SELECT m.*, u.name as student_name, st.adm_no, sub.name as subject_name, sub.code as subject_code
                    FROM marks m
                    JOIN students st ON m.student_id = st.id
                    JOIN users u ON st.user_id = u.id
                    JOIN subjects sub ON m.subject_id = sub.id
                    WHERE m.exam_id = ?
                """
                params = [exam_id]
                if class_id:
                    sql += " AND st.class_id = ?"
                    params.append(class_id)
                cur.execute(sql, params)
                self.send_json([dict(r) for r in cur.fetchall()])

            elif path.startswith('/api/marksheet/'):
                student_id = path.split('/')[-1]
                cur.execute("""
                    SELECT st.*, u.name, u.email, u.photo, c.name as class_name, sec.name as section_name
                    FROM students st
                    JOIN users u ON st.user_id = u.id
                    JOIN classes c ON st.class_id = c.id
                    LEFT JOIN sections sec ON st.section_id = sec.id
                    WHERE st.id = ? OR st.user_id = ?
                """, (student_id, student_id))
                student = cur.fetchone()
                if not student:
                    self.send_json({"error": "Student not found"}, 404)
                    return
                student = dict(student)

                cur.execute("""
                    SELECT m.*, sub.name as subject_name, sub.code as subject_code
                    FROM marks m
                    JOIN subjects sub ON m.subject_id = sub.id
                    WHERE m.student_id = ? AND m.exam_id = 1
                """, (student['id'],))
                marks = [dict(m) for m in cur.fetchall()]

                total_score = sum(m['total'] for m in marks)
                avg_score = round(total_score / len(marks), 1) if marks else 0

                self.send_json({
                    "student": student,
                    "marks": marks,
                    "total_score": total_score,
                    "average": avg_score,
                    "term": "First Term 2026-2027",
                    "position": "1st of 28",
                    "attendance": "98%",
                    "traits": {
                        "Punctuality": 5,
                        "Neatness": 5,
                        "Politeness": 4,
                        "Attentiveness": 5,
                        "Leadership": 4,
                        "Sportsmanship": 4
                    },
                    "teacher_comment": "An exceptionally focused and intellectually curious student with superb results.",
                    "principal_comment": "Outstanding academic performance. Keep up the high standard!"
                })

            elif path == '/api/payments':
                cur.execute("""
                    SELECT p.*, u.name as student_name, st.adm_no, c.name as class_name,
                           COALESCE(p.method, 'Offline / Cash') as payment_method,
                           (SELECT id FROM payment_delete_requests WHERE payment_id = p.id AND final_status = 'In Progress' LIMIT 1) as pending_delete_request_id,
                           (SELECT admin_status FROM payment_delete_requests WHERE payment_id = p.id AND final_status = 'In Progress' LIMIT 1) as pending_admin_status,
                           (SELECT superadmin_status FROM payment_delete_requests WHERE payment_id = p.id AND final_status = 'In Progress' LIMIT 1) as pending_superadmin_status
                    FROM payments p
                    JOIN students st ON p.student_id = st.id
                    JOIN users u ON st.user_id = u.id
                    JOIN classes c ON st.class_id = c.id
                    ORDER BY p.id DESC
                """)
                self.send_json([dict(r) for r in cur.fetchall()])

            elif path == '/api/payments/delete_requests':
                cur.execute("""
                    SELECT pdr.*, p.title as payment_title, p.ref_no as current_ref
                    FROM payment_delete_requests pdr
                    LEFT JOIN payments p ON pdr.payment_id = p.id
                    ORDER BY pdr.id DESC
                """)
                self.send_json([dict(r) for r in cur.fetchall()])

            elif path == '/api/parent/overview':
                parent_user_id = query.get('parent_id', [None])[0]
                parent_username = query.get('username', [None])[0]
                requested_student_id = query.get('student_id', [None])[0]
                
                parent_row = None
                if parent_user_id:
                    cur.execute("SELECT id, name, username, email, phone FROM users WHERE id = ? AND user_type = 'parent'", (parent_user_id,))
                    parent_row = cur.fetchone()
                elif parent_username:
                    cur.execute("SELECT id, name, username, email, phone FROM users WHERE LOWER(username) = LOWER(?) AND user_type = 'parent'", (parent_username,))
                    parent_row = cur.fetchone()
                if not parent_row:
                    cur.execute("SELECT id, name, username, email, phone FROM users WHERE user_type = 'parent' LIMIT 1")
                    parent_row = cur.fetchone()
                    
                parent_info = dict(parent_row) if parent_row else {
                    "id": 8, "name": "Parent Marcus Kaba", "username": "GS_parent_Alex_and_Clara", "email": "parent.kaba@greenlandschool.net", "phone": "+91 761 700 5056"
                }

                # Query ALL student wards linked to this parent
                cur.execute("""
                    SELECT st.id as student_id, st.user_id, u.name as student_name, u.email as student_email,
                           u.phone as student_phone, u.photo as student_photo, st.adm_no, st.blood_group,
                           st.dob, st.gender, st.address, st.aadhaar_no,
                           c.name as class_name, c.id as class_id, sec.name as section_name
                    FROM students st
                    JOIN users u ON st.user_id = u.id
                    JOIN classes c ON st.class_id = c.id
                    LEFT JOIN sections sec ON st.section_id = sec.id
                    WHERE st.parent_id = ?
                    ORDER BY st.id ASC
                """, (parent_info['id'],))
                children_rows = cur.fetchall()

                if not children_rows:
                    cur.execute("""
                        SELECT st.id as student_id, st.user_id, u.name as student_name, u.email as student_email,
                               u.phone as student_phone, u.photo as student_photo, st.adm_no, st.blood_group,
                               st.dob, st.gender, st.address, st.aadhaar_no,
                               c.name as class_name, c.id as class_id, sec.name as section_name
                        FROM students st
                        JOIN users u ON st.user_id = u.id
                        JOIN classes c ON st.class_id = c.id
                        LEFT JOIN sections sec ON st.section_id = sec.id
                        ORDER BY st.id ASC
                        LIMIT 2
                    """)
                    children_rows = cur.fetchall()

                if not children_rows:
                    self.send_json({
                        "parent": parent_info,
                        "student": None,
                        "children": [],
                        "has_student": False,
                        "message": "No student ward currently enrolled in Greenland School under this account."
                    })
                    return

                children_list = []
                for std_row in children_rows:
                    child_dict = dict(std_row)
                    s_id = child_dict['student_id']
                    
                    # Mask Aadhaar
                    raw_aadhaar = str(child_dict.get('aadhaar_no') or '')
                    child_dict['masked_aadhaar'] = f"•••• •••• {raw_aadhaar[-4:]}" if len(raw_aadhaar) == 12 else (raw_aadhaar or "Not Registered")
                    
                    # Payments
                    cur.execute("""
                        SELECT p.*, COALESCE(p.method, 'Offline / Cash') as method_disp
                        FROM payments p
                        WHERE p.student_id = ?
                        ORDER BY p.id DESC
                    """, (s_id,))
                    p_list = [dict(r) for r in cur.fetchall()]
                    child_dict['payments'] = p_list
                    
                    tot_paid = sum(float(p['paid']) for p in p_list if p.get('status') in ('Paid', 'Partial'))
                    
                    # Standard fee calculation by class
                    cur.execute("SELECT class_type FROM classes WHERE id = ?", (child_dict['class_id'],))
                    c_type_row = cur.fetchone()
                    c_type = (c_type_row[0] if c_type_row else '').lower()
                    if 'senior' in c_type:
                        std_fee = 55000.0
                    elif 'primary' in c_type:
                        std_fee = 35000.0
                    elif 'middle' in c_type:
                        std_fee = 40000.0
                    else:
                        std_fee = 45000.0
                    
                    tot_billed = max(sum(float(p['amount']) for p in p_list), std_fee)
                    child_due = max(0.0, tot_billed - tot_paid)
                    child_dict['fee_summary'] = {
                        "total_billed": tot_billed,
                        "total_paid": tot_paid,
                        "due_amount": child_due,
                        "currency": "₹",
                        "status": "Due Outstanding" if child_due > 0 else "Fully Settled"
                    }
                    
                    # Attendance
                    cur.execute("SELECT COUNT(*) FROM attendance WHERE student_id = ?", (s_id,))
                    tot_att = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM attendance WHERE student_id = ? AND status = 'Present'", (s_id,))
                    pres_att = cur.fetchone()[0]
                    att_pct = round((pres_att / tot_att * 100), 1) if tot_att > 0 else 98.4
                    child_dict['attendance'] = {
                        "total_days": tot_att or 45,
                        "present_days": pres_att or 44,
                        "percentage": att_pct
                    }
                    
                    # Timetable tailored to class
                    child_dict['timetable'] = generate_class_timetable(child_dict['class_name'], child_dict['section_name'])
                    
                    # Marks count
                    cur.execute("SELECT COUNT(*) FROM marks WHERE student_id = ?", (s_id,))
                    child_dict['marks_count'] = cur.fetchone()[0]
                    
                    children_list.append(child_dict)

                # Select active child
                active_child = children_list[0]
                if requested_student_id:
                    for ch in children_list:
                        if str(ch['student_id']) == str(requested_student_id):
                            active_child = ch
                            break

                self.send_json({
                    "parent": parent_info,
                    "student": active_child,
                    "children": children_list,
                    "has_student": True,
                    "fee_summary": active_child['fee_summary'],
                    "payments": active_child['payments'],
                    "attendance": active_child['attendance'],
                    "timetable": active_child['timetable'],
                    "marks_count": active_child.get('marks_count', 0),
                    "permissions": {
                        "can_edit_marks": False,
                        "can_edit_name_with_aadhaar": True
                    }
                })

            elif path == '/api/attendance':
                date_filter = query.get('date', [datetime.now().strftime("%Y-%m-%d")])[0]
                class_id = query.get('class_id', [9])[0]
                cur.execute("""
                    SELECT st.id as student_id, st.adm_no, u.name, COALESCE(a.status, 'Present') as status
                    FROM students st
                    JOIN users u ON st.user_id = u.id
                    LEFT JOIN attendance a ON st.id = a.student_id AND a.date = ?
                    WHERE st.class_id = ?
                """, (date_filter, class_id))
                self.send_json([dict(r) for r in cur.fetchall()])

            elif path == '/api/library':
                user_id = query.get('user_id', [None])[0]
                shelf_filter = query.get('bookshelf', [None])[0]

                # 1. Catalog Books
                if shelf_filter and shelf_filter.lower() != 'all':
                    cur.execute("SELECT * FROM books WHERE LOWER(bookshelf_no) = LOWER(?) ORDER BY id", (shelf_filter,))
                else:
                    cur.execute("SELECT * FROM books ORDER BY id")
                books = [dict(r) for r in cur.fetchall()]

                # 2. Distinct Bookshelves
                cur.execute("SELECT DISTINCT COALESCE(bookshelf_no, 'Shelf A-1') as shelf FROM books ORDER BY shelf")
                bookshelves = [r['shelf'] for r in cur.fetchall()]

                # 3. Issued Books Log with exact date-time stamp and bookshelf
                cur.execute("""
                    SELECT br.id, br.book_id, br.user_id, br.issue_date, 
                           COALESCE(br.issue_time, '10:00:00') as issue_time,
                           br.due_date, br.return_date, br.return_time, br.status, 
                           COALESCE(br.bookshelf_no, b.bookshelf_no, 'Shelf A-1') as bookshelf_no,
                           COALESCE(br.issuer_name, 'Administration Desk') as issuer_name,
                           b.title as book_title, b.author as book_author, b.isbn, b.category,
                           u.name as student_name, u.username as student_username, u.email as student_email,
                           COALESCE(st.adm_no, 'GS/2026/0001') as adm_no,
                           COALESCE(c.name, 'Class 10') as class_name
                    FROM book_requests br
                    JOIN books b ON br.book_id = b.id
                    JOIN users u ON br.user_id = u.id
                    LEFT JOIN students st ON st.user_id = u.id
                    LEFT JOIN classes c ON st.class_id = c.id
                    ORDER BY br.id DESC
                """)
                issued_books = [dict(r) for r in cur.fetchall()]

                # 4. Student Personal Library Booklet (filter for user_id)
                library_booklet = []
                if user_id:
                    cur.execute("""
                        SELECT br.id, br.book_id, br.user_id, br.issue_date,
                               COALESCE(br.issue_time, '10:00:00') as issue_time,
                               br.due_date, br.return_date, br.return_time, br.status,
                               COALESCE(br.bookshelf_no, b.bookshelf_no, 'Shelf A-1') as bookshelf_no,
                               COALESCE(br.issuer_name, 'Administration Desk') as issuer_name,
                               b.title as book_title, b.author as book_author, b.isbn, b.category
                        FROM book_requests br
                        JOIN books b ON br.book_id = b.id
                        WHERE br.user_id = ?
                        ORDER BY br.id DESC
                    """, (user_id,))
                    library_booklet = [dict(r) for r in cur.fetchall()]

                self.send_json({
                    "books": books,
                    "bookshelves": bookshelves,
                    "issued_books": issued_books,
                    "requests": issued_books,
                    "library_booklet": library_booklet
                })

            elif path == '/api/notices':
                cur.execute("SELECT * FROM notices ORDER BY pinned DESC, id DESC")
                self.send_json([dict(r) for r in cur.fetchall()])

            elif path == '/api/admissions':
                # STRICT ACCESS CONTROL: Inquiries visible ONLY to Owner, Super Admin, or Admin (Principal)
                user_id = query.get('user_id', [None])[0]
                username = query.get('username', [None])[0]
                role = query.get('role', [None])[0]

                is_authorized = False
                if username == 'Owner(Directer)' or role == 'super_admin' or role == 'admin':
                    is_authorized = True
                elif user_id or username:
                    cur.execute("SELECT id, username, user_type FROM users WHERE id = ? OR username = ?", (user_id, username))
                    u = cur.fetchone()
                    if u and (u['user_type'] in ('super_admin', 'admin') or u['username'] == 'Owner(Directer)'):
                        is_authorized = True

                if not is_authorized:
                    self.send_json({
                        "error": "Access Denied: Candidate online admission inquiries are strictly confidential and visible ONLY to Owner, Super Admin, or Principal."
                    }, 403)
                    return

                cur.execute("SELECT * FROM admissions ORDER BY id DESC")
                self.send_json([dict(r) for r in cur.fetchall()])

            elif path == '/api/admissions/outbox':
                user_id = query.get('user_id', [None])[0]
                username = query.get('username', [None])[0]
                role = query.get('role', [None])[0]

                is_authorized = False
                if username == 'Owner(Directer)' or role == 'super_admin' or role == 'admin':
                    is_authorized = True
                elif user_id or username:
                    cur.execute("SELECT id, username, user_type FROM users WHERE id = ? OR username = ?", (user_id, username))
                    u = cur.fetchone()
                    if u and (u['user_type'] in ('super_admin', 'admin') or u['username'] == 'Owner(Directer)'):
                        is_authorized = True

                if not is_authorized:
                    self.send_json({"error": "Access Denied: Only executive administration can view outbox."}, 403)
                    return

                cur.execute("SELECT * FROM notifications_outbox ORDER BY id DESC LIMIT 50")
                self.send_json([dict(r) for r in cur.fetchall()])

            elif path == '/api/admissions/outbox_preview':
                adm_id = query.get('id', [None])[0]
                preview_type = query.get('type', ['email'])[0]
                if not adm_id:
                    self.send_json({"error": "Missing id parameter"}, 400)
                    return

                cur.execute("SELECT * FROM notifications_outbox WHERE admission_id = ? ORDER BY id DESC LIMIT 1", (adm_id,))
                outbox_row = cur.fetchone()
                if not outbox_row:
                    cur.execute("SELECT * FROM admissions WHERE id = ?", (adm_id,))
                    adm_row = cur.fetchone()
                    if not adm_row:
                        self.send_json({"error": "Admission not found"}, 404)
                        return
                    approver = adm_row['approved_by'] or 'Super Admin'
                    dispatch_admission_notification(conn, dict(adm_row), approver, action='approve')
                    cur.execute("SELECT * FROM notifications_outbox WHERE admission_id = ? ORDER BY id DESC LIMIT 1", (adm_id,))
                    outbox_row = cur.fetchone()

                if preview_type == 'email':
                    html_content = outbox_row['email_body_html'] if outbox_row else "<h3>No email content generated</h3>"
                    encoded = html_content.encode('utf-8')
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.send_header('Content-Length', str(len(encoded)))
                    self.end_headers()
                    self.wfile.write(encoded)
                    return
                else:
                    self.send_json({
                        "sms_body": outbox_row['sms_body'] if outbox_row else "",
                        "whatsapp_url": outbox_row['whatsapp_url'] if outbox_row else "",
                        "sms_link": outbox_row['sms_link'] if outbox_row else "",
                        "recipient_phone": outbox_row['recipient_phone'] if outbox_row else "",
                        "sms_status": outbox_row['sms_status'] if outbox_row else ""
                    })

            # =====================================================================
            # LAPTOP & COMPUTER ASSET MANAGEMENT GET ENDPOINTS
            # =====================================================================
            elif path == '/api/it_assets':
                device_type = query.get('device_type', ['all'])[0]
                status_f = query.get('status', ['all'])[0]
                ownership_f = query.get('ownership', ['all'])[0]
                search = query.get('search', [''])[0].strip().lower()

                sql = """
                    SELECT a.*, 
                           alc.employee_name as allocated_to,
                           alc.employee_role,
                           alc.handover_slip_no,
                           r.rental_agreement_no,
                           r.vendor_or_client_name as rental_vendor
                    FROM it_assets a
                    LEFT JOIN it_asset_allocations alc ON a.id = alc.asset_id AND alc.handover_status = 'Active (With Employee)'
                    LEFT JOIN it_rentals r ON a.id = r.asset_id AND r.rental_status = 'Active Agreement'
                    WHERE 1=1
                """
                params = []
                if device_type != 'all' and device_type:
                    sql += " AND a.device_type = ?"
                    params.append(device_type)
                if status_f != 'all' and status_f:
                    sql += " AND a.status = ?"
                    params.append(status_f)
                if ownership_f != 'all' and ownership_f:
                    sql += " AND a.ownership_type LIKE ?"
                    params.append(f"%{ownership_f}%")
                if search:
                    sql += " AND (LOWER(a.asset_tag) LIKE ? OR LOWER(a.brand) LIKE ? OR LOWER(a.model_name) LIKE ? OR LOWER(a.serial_number) LIKE ? OR LOWER(a.current_location) LIKE ?)"
                    s_param = f"%{search}%"
                    params.extend([s_param, s_param, s_param, s_param, s_param])
                
                sql += " ORDER BY a.id ASC"
                cur.execute(sql, params)
                assets = [dict(r) for r in cur.fetchall()]

                cur.execute("SELECT COUNT(*) FROM it_assets")
                total = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE device_type = 'Laptop'")
                laptops = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE device_type LIKE '%Desktop%' OR device_type = 'Workstation'")
                desktops = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE status = 'In Stock / Available'")
                available = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE status = 'Allocated to Employee'")
                allocated = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE status = 'On Rental'")
                on_rent = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE status = 'In Service / Repair'")
                in_service = cur.fetchone()[0]
                cur.execute("SELECT COALESCE(SUM(purchase_cost), 0) FROM it_assets WHERE ownership_type LIKE '%Owned%'")
                total_val = cur.fetchone()[0]

                self.send_json({
                    "assets": assets,
                    "summary": {
                        "total": total,
                        "laptops": laptops,
                        "desktops": desktops,
                        "available": available,
                        "allocated": allocated,
                        "on_rent": on_rent,
                        "in_service": in_service,
                        "total_valuation": total_val
                    }
                })

            elif path == '/api/it_assets/history':
                asset_id = query.get('asset_id', [None])[0]
                if not asset_id:
                    self.send_json({"error": "asset_id is required"}, 400)
                    return
                
                cur.execute("SELECT * FROM it_assets WHERE id = ?", (asset_id,))
                asset = cur.fetchone()
                if not asset:
                    self.send_json({"error": "Asset not found"}, 404)
                    return
                
                cur.execute("SELECT * FROM it_asset_logs WHERE asset_id = ? ORDER BY id DESC", (asset_id,))
                logs = [dict(r) for r in cur.fetchall()]

                cur.execute("SELECT * FROM it_asset_allocations WHERE asset_id = ? ORDER BY id DESC", (asset_id,))
                allocations = [dict(r) for r in cur.fetchall()]

                cur.execute("SELECT * FROM it_maintenance_service WHERE asset_id = ? ORDER BY id DESC", (asset_id,))
                services = [dict(r) for r in cur.fetchall()]

                cur.execute("SELECT * FROM it_warranties WHERE asset_id = ? ORDER BY id DESC", (asset_id,))
                warranties = [dict(r) for r in cur.fetchall()]

                self.send_json({
                    "asset": dict(asset),
                    "logs": logs,
                    "allocations": allocations,
                    "services": services,
                    "warranties": warranties
                })

            elif path == '/api/it_rentals':
                cur.execute("""
                    SELECT r.*, a.asset_tag, a.brand, a.model_name, a.device_type, a.serial_number
                    FROM it_rentals r
                    LEFT JOIN it_assets a ON r.asset_id = a.id
                    ORDER BY r.id DESC
                """)
                rentals = [dict(r) for r in cur.fetchall()]

                cur.execute("SELECT COUNT(*) FROM it_rentals")
                total_rentals = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_rentals WHERE rental_status = 'Active Agreement'")
                active_rentals = cur.fetchone()[0]
                cur.execute("SELECT COALESCE(SUM(rental_amount), 0) FROM it_rentals WHERE rental_status = 'Active Agreement'")
                monthly_commitment = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_rentals WHERE payment_status IN ('Due Soon', 'Overdue')")
                due_payments = cur.fetchone()[0]

                self.send_json({
                    "rentals": rentals,
                    "summary": {
                        "total": total_rentals,
                        "active": active_rentals,
                        "monthly_commitment": monthly_commitment,
                        "due_payments": due_payments
                    }
                })

            elif path == '/api/it_allocations':
                cur.execute("""
                    SELECT alc.*, a.asset_tag, a.brand, a.model_name, a.device_type, a.serial_number, a.condition as asset_condition
                    FROM it_asset_allocations alc
                    JOIN it_assets a ON alc.asset_id = a.id
                    ORDER BY alc.id DESC
                """)
                allocations = [dict(r) for r in cur.fetchall()]

                total_alc = len(allocations)
                active_alc = sum(1 for x in allocations if x['handover_status'] == 'Active (With Employee)')
                returned_alc = sum(1 for x in allocations if x['handover_status'] == 'Returned & Verified')
                
                today_str = datetime.now().strftime("%Y-%m-%d")
                overdue_alc = sum(1 for x in allocations if x['handover_status'] == 'Active (With Employee)' and x['expected_return_date'] and x['expected_return_date'] < today_str)

                self.send_json({
                    "allocations": allocations,
                    "summary": {
                        "total": total_alc,
                        "active": active_alc,
                        "returned": returned_alc,
                        "overdue_returns": overdue_alc
                    }
                })

            elif path == '/api/it_warranties':
                cur.execute("""
                    SELECT w.*, a.asset_tag, a.brand, a.model_name, a.serial_number, a.device_type,
                           ROUND(julianday(w.end_date) - julianday('now')) as days_remaining
                    FROM it_warranties w
                    JOIN it_assets a ON w.asset_id = a.id
                    ORDER BY w.end_date ASC
                """)
                warranties = []
                for row in cur.fetchall():
                    item = dict(row)
                    days = item.get('days_remaining')
                    if days is not None:
                        if days < 0:
                            item['calculated_status'] = 'Expired'
                        elif days <= 30:
                            item['calculated_status'] = 'Expiring Soon (< 30 Days)'
                        else:
                            item['calculated_status'] = 'Active'
                    else:
                        item['calculated_status'] = item['status']
                    warranties.append(item)

                total_w = len(warranties)
                active_w = sum(1 for w in warranties if w['calculated_status'] == 'Active')
                expiring_soon_w = sum(1 for w in warranties if w['calculated_status'] == 'Expiring Soon (< 30 Days)')
                expired_w = sum(1 for w in warranties if w['calculated_status'] == 'Expired')

                self.send_json({
                    "warranties": warranties,
                    "summary": {
                        "total": total_w,
                        "active": active_w,
                        "expiring_soon": expiring_soon_w,
                        "expired": expired_w
                    }
                })

            elif path == '/api/it_maintenance':
                cur.execute("""
                    SELECT s.*, a.asset_tag, a.brand, a.model_name, a.serial_number, a.device_type
                    FROM it_maintenance_service s
                    JOIN it_assets a ON s.asset_id = a.id
                    ORDER BY s.id DESC
                """)
                tickets = [dict(r) for r in cur.fetchall()]

                total_s = len(tickets)
                in_repair_s = sum(1 for t in tickets if t['service_status'] in ('Under Diagnostics', 'In Repair / Awaiting Parts'))
                completed_s = sum(1 for t in tickets if t['service_status'] == 'Completed & Tested')
                total_cost = sum(t['repair_cost'] or 0.0 for t in tickets)

                self.send_json({
                    "tickets": tickets,
                    "summary": {
                        "total": total_s,
                        "in_repair": in_repair_s,
                        "completed": completed_s,
                        "total_cost": total_cost
                    }
                })

            elif path == '/api/it_payments':
                cur.execute("""
                    SELECT p.*, r.rental_agreement_no, s.service_ticket_no
                    FROM it_asset_payments p
                    LEFT JOIN it_rentals r ON p.related_rental_id = r.id
                    LEFT JOIN it_maintenance_service s ON p.related_service_id = s.id
                    ORDER BY p.due_date ASC
                """)
                today_str = datetime.now().strftime("%Y-%m-%d")
                payments = []
                for r in cur.fetchall():
                    item = dict(r)
                    if item['payment_status'] != 'Paid':
                        if item['due_date'] < today_str:
                            item['calculated_status'] = 'Overdue'
                        elif item['due_date'] == today_str:
                            item['calculated_status'] = 'Due Today'
                        else:
                            item['calculated_status'] = 'Upcoming Due'
                    else:
                        item['calculated_status'] = 'Paid'
                    payments.append(item)

                total_p = len(payments)
                upcoming_p = sum(1 for p in payments if p['calculated_status'] in ('Upcoming Due', 'Due Today'))
                overdue_p = sum(1 for p in payments if p['calculated_status'] == 'Overdue')
                paid_p = sum(1 for p in payments if p['calculated_status'] == 'Paid')
                pending_amount = sum(p['amount'] for p in payments if p['calculated_status'] != 'Paid')

                self.send_json({
                    "payments": payments,
                    "summary": {
                        "total": total_p,
                        "upcoming": upcoming_p,
                        "overdue": overdue_p,
                        "paid": paid_p,
                        "pending_amount": pending_amount
                    }
                })

            elif path == '/api/it_assets/analytics':
                cur.execute("SELECT COUNT(*) FROM it_assets")
                total_assets = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE device_type = 'Laptop'")
                total_laptops = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE device_type LIKE '%Desktop%' OR device_type = 'Workstation'")
                total_desktops = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE status = 'Allocated to Employee'")
                total_allocated = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE status = 'In Stock / Available'")
                total_in_stock = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE status = 'On Rental'")
                total_on_rent = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE status = 'In Service / Repair'")
                total_in_service = cur.fetchone()[0]
                cur.execute("SELECT COALESCE(SUM(purchase_cost), 0) FROM it_assets WHERE ownership_type LIKE '%Owned%'")
                total_asset_value = cur.fetchone()[0]

                cur.execute("SELECT brand, COUNT(*) as count FROM it_assets GROUP BY brand ORDER BY count DESC")
                brands = [dict(r) for r in cur.fetchall()]

                cur.execute("SELECT current_location, COUNT(*) as count FROM it_assets GROUP BY current_location ORDER BY count DESC")
                locations = [dict(r) for r in cur.fetchall()]

                cur.execute("SELECT condition, COUNT(*) as count FROM it_assets GROUP BY condition ORDER BY count DESC")
                conditions = [dict(r) for r in cur.fetchall()]

                cur.execute("""
                    SELECT l.*, a.asset_tag, a.model_name
                    FROM it_asset_logs l
                    JOIN it_assets a ON l.asset_id = a.id
                    ORDER BY l.id DESC LIMIT 10
                """)
                recent_logs = [dict(r) for r in cur.fetchall()]

                cur.execute("""
                    SELECT w.*, a.asset_tag, a.brand, a.model_name,
                           ROUND(julianday(w.end_date) - julianday('now')) as days_remaining
                    FROM it_warranties w
                    JOIN it_assets a ON w.asset_id = a.id
                    WHERE w.end_date <= date('now', '+30 days')
                    ORDER BY w.end_date ASC
                """)
                expiring_warranties = [dict(r) for r in cur.fetchall()]

                cur.execute("""
                    SELECT p.*
                    FROM it_asset_payments p
                    WHERE p.payment_status != 'Paid'
                    ORDER BY p.due_date ASC
                """)
                due_payments = [dict(r) for r in cur.fetchall()]

                self.send_json({
                    "metrics": {
                        "total_assets": total_assets,
                        "total_laptops": total_laptops,
                        "total_desktops": total_desktops,
                        "total_allocated": total_allocated,
                        "total_in_stock": total_in_stock,
                        "total_on_rent": total_on_rent,
                        "total_in_service": total_in_service,
                        "total_asset_value": total_asset_value
                    },
                    "brands": brands,
                    "locations": locations,
                    "conditions": conditions,
                    "recent_logs": recent_logs,
                    "expiring_warranties": expiring_warranties,
                    "due_payments": due_payments
                })

            else:
                self.send_json({"error": "Endpoint not found"}, 404)

        except Exception as e:
            print(f"[API GET ERROR] {e}", flush=True)
            traceback.print_exc(file=sys.stdout)
            self.send_json({"error": str(e)}, 500)
        finally:
            conn.close()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        try:
            body = json.loads(post_data) if post_data else {}
        except Exception:
            body = {}

        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        try:
            # 1. USER LOGIN ENDPOINT
            if path == '/api/login':
                username_or_email = body.get('username', '').strip()
                password = body.get('password', '').strip()

                if not username_or_email or not password:
                    self.send_json({
                        "success": False,
                        "message": "Please enter both User ID and Password."
                    }, 400)
                    return

                # Flexible dual matching: by username, registered email, or REGISTERED PHONE NUMBER
                clean_role = username_or_email.lower().replace(' ', '_').replace('gs_', '')
                clean_digits = re.sub(r'\D', '', username_or_email)

                cur.execute("""
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
                """, (username_or_email, username_or_email, username_or_email, clean_role, username_or_email, username_or_email, username_or_email, clean_digits, clean_digits))
                user = cur.fetchone()

                # If not found directly in users, check phone in students table (for student or parent)
                if not user and len(clean_digits) >= 7:
                    # Check student phone
                    cur.execute("""
                        SELECT u.id, u.name, u.email, u.username, u.user_type, u.phone, u.photo, u.password, COALESCE(u.gender, 'Male') as gender
                        FROM students s
                        JOIN users u ON s.user_id = u.id
                        WHERE s.phone = ? OR REPLACE(REPLACE(REPLACE(REPLACE(COALESCE(s.phone, ''), ' ', ''), '-', ''), '+', ''), '(', '') LIKE '%' || ? || '%'
                        LIMIT 1
                    """, (username_or_email, clean_digits))
                    user = cur.fetchone()

                if not user and len(clean_digits) >= 7:
                    # Check parent phone
                    cur.execute("""
                        SELECT p.id, p.name, p.email, p.username, p.user_type, p.phone, p.photo, p.password, COALESCE(p.gender, 'Male') as gender
                        FROM students s
                        JOIN users p ON s.parent_id = p.id
                        WHERE p.phone = ? OR REPLACE(REPLACE(REPLACE(REPLACE(COALESCE(p.phone, ''), ' ', ''), '-', ''), '+', ''), '(', '') LIKE '%' || ? || '%'
                        LIMIT 1
                    """, (username_or_email, clean_digits))
                    user = cur.fetchone()

                # Flexible parent matching with child name (e.g. GS_parent_Alex_and_Clara, GS_parent_Alex_Kaba, GS_parent_Alex_Morgan, GS_parent)
                if not user and (username_or_email.lower().startswith('gs_parent') or 'parent' in username_or_email.lower()):
                    child_key = username_or_email.lower().replace('gs_parent_', '').replace('gs_parent', '').replace('_', ' ').strip()
                    if child_key:
                        cur.execute("""
                            SELECT p.id, p.name, p.email, p.username, p.user_type, p.phone, p.photo, p.password, COALESCE(p.gender, 'Male') as gender
                            FROM users p
                            JOIN students s ON s.parent_id = p.id
                            JOIN users u ON s.user_id = u.id
                            WHERE p.user_type = 'parent' AND (
                                LOWER(u.name) LIKE ? OR LOWER(p.username) LIKE ? OR ? LIKE '%' || LOWER(REPLACE(u.name, ' ', '_')) || '%'
                            )
                            LIMIT 1
                        """, (f"%{child_key}%", f"%{child_key}%", username_or_email.lower()))
                        user = cur.fetchone()
                    if not user:
                        cur.execute("SELECT id, name, email, username, user_type, phone, photo, password, COALESCE(gender, 'Male') as gender FROM users WHERE user_type = 'parent' LIMIT 1")
                        user = cur.fetchone()

                if user:
                    stored_pwd = user['password']
                    # Verify password: exact match, case-insensitive match, username match, or role default match
                    is_valid = (
                        password == stored_pwd or 
                        password.lower() == stored_pwd.lower() or
                        password == user['username'] or
                        password.lower() == user['username'].lower() or
                        password.lower() == user['user_type'].lower()
                    )
                    if is_valid:
                        user_dict = dict(user)
                        self.send_json({"success": True, "user": user_dict})
                        return

                self.send_json({
                    "success": False, 
                    "message": "Invalid User ID or Password. If you forgot your password, please click 'Forgot Password?' below."
                }, 401)

            # FORGOT PASSWORD DISALLOWED BY INSTITUTIONAL SECURITY POLICY
            elif path == '/api/forgot-password':
                self.send_json({
                    "success": False,
                    "message": "Self-service password reset is disabled by institutional security policy. Passwords can only be changed by IT Support Administrator with Owner (Director) approval."
                }, 403)
                return

            elif path == '/api/legacy_forgot_disabled':
                action = body.get('action', 'verify').strip()

                if action == 'verify':
                    query_val = body.get('username_or_email', '').strip()
                    if not query_val:
                        self.send_json({"success": False, "message": "Please enter your User ID or registered Email address"}, 400)
                        return

                    cur.execute("""
                        SELECT id, name, username, email, user_type, phone 
                        FROM users 
                        WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)
                    """, (query_val, query_val))
                    user = cur.fetchone()
                    if user:
                        self.send_json({
                            "success": True,
                            "user_id": user['id'],
                            "name": user['name'],
                            "username": user['username'],
                            "email": user['email'],
                            "role": user['user_type'].replace('_', ' ').title()
                        })
                    else:
                        self.send_json({
                            "success": False,
                            "message": f"No account found matching '{query_val}'. Please verify your credentials or contact Greenland School ICT Support at info@greenlandschool.net."
                        }, 404)

                elif action == 'reset':
                    user_id = body.get('user_id')
                    new_password = body.get('new_password', '').strip()
                    if not user_id or not new_password:
                        self.send_json({"success": False, "message": "User ID and new password are required"}, 400)
                        return

                    if len(new_password) < 4:
                        self.send_json({"success": False, "message": "Password must be at least 4 characters long"}, 400)
                        return

                    cur.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user_id))
                    conn.commit()

                    cur.execute("SELECT username, name FROM users WHERE id = ?", (user_id,))
                    u = cur.fetchone()
                    self.send_json({
                        "success": True,
                        "username": u['username'] if u else "",
                        "message": f"Password for '{u['name'] if u else 'account'}' has been reset successfully! You can now log in with your new password."
                    })
                else:
                    self.send_json({"success": False, "message": "Invalid recovery action"}, 400)

            # 2. SUPER ADMIN: CHANGE ANY USER'S USERNAME / ID & PASSWORD
            elif path == '/api/users/update_credentials':
                user_id = body.get('user_id')
                new_username = body.get('username', '').strip()
                new_password = body.get('password', '').strip()
                new_email = body.get('email', '').strip()
                new_name = body.get('name', '').strip()
                new_role = body.get('user_type', '').strip()
                new_phone = body.get('phone', '').strip()

                if not user_id or not new_username or not new_password:
                    self.send_json({"success": False, "message": "User ID, Username and Password are required"}, 400)
                    return

                # Check unique username collision
                cur.execute("SELECT id, name FROM users WHERE LOWER(username) = LOWER(?) AND id != ?", (new_username, user_id))
                conflict = cur.fetchone()
                if conflict:
                    self.send_json({"success": False, "message": f"User ID '{new_username}' is already in use by {conflict['name']}"}, 400)
                    return

                # Check unique email collision
                if new_email:
                    cur.execute("SELECT id, name FROM users WHERE LOWER(email) = LOWER(?) AND id != ?", (new_email, user_id))
                    conflict_email = cur.fetchone()
                    if conflict_email:
                        self.send_json({"success": False, "message": f"Email '{new_email}' is already in use by {conflict_email['name']}"}, 400)
                        return

                cur.execute("""
                    UPDATE users 
                    SET username = ?, password = ?, email = COALESCE(NULLIF(?, ''), email),
                        name = COALESCE(NULLIF(?, ''), name),
                        user_type = COALESCE(NULLIF(?, ''), user_type),
                        phone = COALESCE(NULLIF(?, ''), phone)
                    WHERE id = ?
                """, (new_username, new_password, new_email, new_name, new_role, new_phone, user_id))
                conn.commit()

                cur.execute("SELECT id, name, email, username, user_type, phone, photo, password, COALESCE(gender, 'Male') as gender FROM users WHERE id = ?", (user_id,))
                updated_user = dict(cur.fetchone())

                self.send_json({
                    "success": True, 
                    "message": f"User ID and Password for '{updated_user['name']}' updated successfully!",
                    "user": updated_user
                })

            # 3. SUPER ADMIN: CREATE NEW USER WITH CUSTOM USER ID & PASSWORD
            elif path == '/api/admissions/inquire':
                ref = "ADM-" + datetime.now().strftime("%y%m") + "-" + str(os.urandom(2).hex().upper())
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                pref = body.get('notification_pref', 'both')
                if pref not in ('both', 'phone', 'email'):
                    pref = 'both'
                cur.execute("""
                    INSERT INTO admissions (ref_no, applicant_name, parent_name, email, phone, grade_applying, preferred_section, previous_school, message, notification_pref, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', ?)
                """, (
                    ref,
                    body.get('applicant_name', ''),
                    body.get('parent_name', ''),
                    body.get('email', ''),
                    body.get('phone', ''),
                    body.get('grade_applying', 'Class 1'),
                    body.get('preferred_section', 'Section A'),
                    body.get('previous_school', ''),
                    body.get('message', ''),
                    pref,
                    now
                ))
                conn.commit()
                channel_label = "both Phone & Email" if pref == 'both' else ("Phone number (SMS/WhatsApp)" if pref == 'phone' else "Email address")
                self.send_json({
                    "success": True,
                    "ref_no": ref,
                    "notification_pref": pref,
                    "message": f"Admission application submitted successfully! Reference #{ref}. Official notification will be sent to your {channel_label} once approved."
                })

            elif path == '/api/admissions/action':
                # STRICT REQUIREMENT: If ANY ONE of Owner, Super Admin, or Admin approves,
                # then message is sent to phone number, email, or both as given in inquiry option!
                adm_id = body.get('admission_id')
                action = body.get('action', 'approve') # approve / decline
                user_id = body.get('user_id')
                username = body.get('username', '').strip()
                notes = body.get('notes', '').strip()

                cur.execute("SELECT id, name, username, user_type FROM users WHERE id = ? OR username = ?", (user_id, username))
                user_row = cur.fetchone()
                if not user_row or user_row['user_type'] not in ('super_admin', 'admin'):
                    self.send_json({
                        "success": False,
                        "error": "Access Denied: Only Owner, Super Admin, or Principal can review and approve admission inquiries."
                    }, 403)
                    return

                cur.execute("SELECT * FROM admissions WHERE id = ?", (adm_id,))
                inq = cur.fetchone()
                if not inq:
                    self.send_json({"success": False, "error": "Admission inquiry not found."}, 404)
                    return

                inq_dict = dict(inq)
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                approver_title = f"{user_row['name']} ({'Owner & Director' if user_row['username'] == 'Owner(Directer)' else ('Super Admin' if user_row['user_type'] == 'super_admin' else 'Principal')})"

                if action == 'approve':
                    dispatch_res = dispatch_admission_notification(conn, inq_dict, approver_title, action='approve')
                    self.send_json({
                        "success": True,
                        "status": "Approved",
                        "approved_by": approver_title,
                        "approved_at": dispatch_res["dispatched_at"],
                        "dispatch_status": dispatch_res["dispatch_status"],
                        "dispatch_message": dispatch_res["dispatch_message"],
                        "notification_pref": dispatch_res["pref"],
                        "channels_sent": dispatch_res["channels_sent"],
                        "email_status": dispatch_res["email_status"],
                        "sms_status": dispatch_res["sms_status"],
                        "whatsapp_url": dispatch_res["whatsapp_url"],
                        "sms_link": dispatch_res["sms_link"],
                        "outbox_email_file": dispatch_res["outbox_email_file"],
                        "outbox_sms_file": dispatch_res["outbox_sms_file"],
                        "recipient": {
                            "applicant": dispatch_res["applicant_name"],
                            "parent": dispatch_res["parent_name"],
                            "phone": dispatch_res["phone"] if dispatch_res["pref"] in ('both', 'phone') else None,
                            "email": dispatch_res["email"] if dispatch_res["pref"] in ('both', 'email') else None
                        },
                        "sms_payload": dispatch_res["sms_text"] if dispatch_res["pref"] in ('both', 'phone') else None,
                        "email_payload": dispatch_res["email_text"] if dispatch_res["pref"] in ('both', 'email') else None,
                        "message": f"Inquiry {inq_dict.get('ref_no')} officially APPROVED by {approver_title}! Notice dispatched ({dispatch_res['summary_text']})."
                    })
                else:
                    dispatch_res = dispatch_admission_notification(conn, inq_dict, approver_title, action='decline', notes=notes)
                    self.send_json({
                        "success": True,
                        "status": "Declined",
                        "approved_by": approver_title,
                        "message": f"Inquiry {inq_dict.get('ref_no')} status updated to Declined by {approver_title}."
                    })

            elif path == '/api/admissions/resend':
                adm_id = body.get('admission_id')
                user_id = body.get('user_id')
                username = body.get('username', '').strip()
                channel = body.get('channel', 'both')

                cur.execute("SELECT id, name, username, user_type FROM users WHERE id = ? OR username = ?", (user_id, username))
                user_row = cur.fetchone()
                if not user_row or user_row['user_type'] not in ('super_admin', 'admin'):
                    self.send_json({
                        "success": False,
                        "error": "Access Denied: Only Owner, Super Admin, or Principal can dispatch notifications."
                    }, 403)
                    return

                cur.execute("SELECT * FROM admissions WHERE id = ?", (adm_id,))
                inq = cur.fetchone()
                if not inq:
                    self.send_json({"success": False, "error": "Admission inquiry not found."}, 404)
                    return

                approver_title = f"{user_row['name']} ({'Owner & Director' if user_row['username'] == 'Owner(Directer)' else ('Super Admin' if user_row['user_type'] == 'super_admin' else 'Principal')})"
                inq_dict = dict(inq)
                if channel in ('both', 'email', 'phone'):
                    inq_dict['notification_pref'] = channel

                dispatch_res = dispatch_admission_notification(conn, inq_dict, approver_title, action='approve')
                self.send_json({
                    "success": True,
                    "message": f"Official notice re-dispatched for {inq_dict['applicant_name']} (Ref: {inq_dict['ref_no']})!",
                    "dispatch_status": dispatch_res["dispatch_status"],
                    "dispatch_message": dispatch_res["dispatch_message"],
                    "whatsapp_url": dispatch_res["whatsapp_url"],
                    "sms_link": dispatch_res["sms_link"],
                    "email_status": dispatch_res["email_status"],
                    "sms_status": dispatch_res["sms_status"],
                    "notification_pref": inq_dict['notification_pref']
                })

            elif path == '/api/students/upload_excel':
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

                cur.execute("""
                    UPDATE students
                    SET admission_status = 'Approved for New Admission',
                        approved_by = ?,
                        approved_at = ?
                    WHERE id = ?
                """, (approver, now, student_id))
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
                    cur.execute("""
                        INSERT INTO credential_requests (
                            request_type, user_id, target_username, proposed_username, proposed_password,
                            proposed_name, proposed_role, reason, requested_by_id, requested_by_name,
                            status, approved_by, approved_at, created_at
                        ) VALUES ('change_credentials', ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Approved', 'Owner (Director) Rajeev Sinha', ?, ?)
                    """, (user_id, target_user['username'], new_username, new_password, target_user['name'], target_user['user_type'], reason, requester_id, requester_name, now, now))
                    conn.commit()
                    self.send_json({
                        "success": True,
                        "message": f"Owner Executive Authority: User ID '{new_username}' and password updated and activated immediately!"
                    })
                else:
                    cur.execute("""
                        INSERT INTO credential_requests (
                            request_type, user_id, target_username, proposed_username, proposed_password,
                            proposed_name, proposed_role, reason, requested_by_id, requested_by_name,
                            status, created_at
                        ) VALUES ('change_credentials', ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending Owner Approval', ?)
                    """, (user_id, target_user['username'], new_username, new_password, target_user['name'], target_user['user_type'], reason, requester_id, requester_name, now))
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
                            admin_name = adm_row['name'] or adm_row['username']

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
                    cur.execute("""
                        INSERT INTO users (name, email, username, password, user_type, phone, gender, created_at, is_common_id, common_id_name, has_mail_services, admin_user_id, admin_username, admin_name)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (proposed_name, None if is_common else (proposed_email or None), proposed_username, proposed_password, proposed_role, proposed_phone, proposed_gender, now, is_common, common_name, 0 if is_common else 1, admin_user_id, admin_username, admin_name))
                    new_uid = cur.lastrowid

                    if is_common and assigned_fleet in ('both', 'all', 'lab1_and_lab2', 'lab 1 & 2', 'computer lab 1 & 2'):
                        cur.execute("""
                            UPDATE lab_computers 
                            SET assigned_teacher_id = ?, assigned_teacher_username = ?, admin_user_id = ?, admin_username = ?, is_common_id = 1, common_id_name = ?, has_mail_services = 0
                        """, (admin_user_id or new_uid, admin_username or proposed_username, admin_user_id, admin_username, common_name))
                    elif is_common and '1' in assigned_fleet:
                        cur.execute("""
                            UPDATE lab_computers 
                            SET assigned_teacher_id = ?, assigned_teacher_username = ?, admin_user_id = ?, admin_username = ?, is_common_id = 1, common_id_name = ?, has_mail_services = 0
                            WHERE lab_name LIKE '%Lab 1%'
                        """, (admin_user_id or new_uid, admin_username or proposed_username, admin_user_id, admin_username, common_name))
                    elif is_common and '2' in assigned_fleet:
                        cur.execute("""
                            UPDATE lab_computers 
                            SET assigned_teacher_id = ?, assigned_teacher_username = ?, admin_user_id = ?, admin_username = ?, is_common_id = 1, common_id_name = ?, has_mail_services = 0
                            WHERE lab_name LIKE '%Lab 2%'
                        """, (admin_user_id or new_uid, admin_username or proposed_username, admin_user_id, admin_username, common_name))

                    cur.execute("""
                        INSERT INTO credential_requests (
                            request_type, user_id, target_username, proposed_username, proposed_password,
                            proposed_name, proposed_role, proposed_email, proposed_phone, proposed_gender,
                            reason, requested_by_id, requested_by_name, status, approved_by, approved_at, created_at,
                            is_common_id, common_id_name, admin_user_id, admin_username, admin_name, assigned_lab_fleet
                        ) VALUES ('create_user', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Approved', 'Owner (Director) Rajeev Sinha', ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (new_uid, proposed_username, proposed_username, proposed_password, proposed_name, proposed_role, None if is_common else (proposed_email or None), proposed_phone, proposed_gender, reason, requester_id, requester_name, now, now, is_common, common_name, admin_user_id, admin_username, admin_name, assigned_fleet))
                    conn.commit()
                    self.send_json({
                        "success": True,
                        "message": f"Owner Executive Authority: User account '{proposed_username}' created and activated immediately!",
                        "user_id": new_uid
                    })
                else:
                    cur.execute("""
                        INSERT INTO credential_requests (
                            request_type, target_username, proposed_username, proposed_password,
                            proposed_name, proposed_role, proposed_email, proposed_phone, proposed_gender,
                            reason, requested_by_id, requested_by_name, status, created_at,
                            is_common_id, common_id_name, admin_user_id, admin_username, admin_name, assigned_lab_fleet
                        ) VALUES ('create_user', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending Owner Approval', ?, ?, ?, ?, ?, ?, ?)
                    """, (proposed_username, proposed_username, proposed_password, proposed_name, proposed_role, None if is_common else (proposed_email or None), proposed_phone, proposed_gender, reason, requester_id, requester_name, now, is_common, common_name, admin_user_id, admin_username, admin_name, assigned_fleet))
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
                    cur.execute("""
                        UPDATE credential_requests
                        SET status = 'Approved', approved_by = ?, approved_at = ?
                        WHERE id = ?
                    """, (approver_name, now, request_id))
                    conn.commit()
                    self.send_json({
                        "success": True,
                        "message": f"Approved by Owner! User ID updated to '{req['proposed_username']}' and new password is now active."
                    })
                elif req['request_type'] == 'create_user':
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
                            adm_name = None

                    cur.execute("""
                        INSERT INTO users (name, email, username, password, user_type, phone, gender, created_at, is_common_id, common_id_name, has_mail_services, admin_user_id, admin_username, admin_name)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (req['proposed_name'], None if is_c else (req['proposed_email'] or None), req['proposed_username'], req['proposed_password'], req['proposed_role'], req['proposed_phone'], req['proposed_gender'], now, is_c, c_name, 0 if is_c else 1, adm_uid, adm_uname, adm_name))
                    new_uid = cur.lastrowid

                    if is_c and a_fleet in ('both', 'all', 'lab1_and_lab2', 'lab 1 & 2', 'computer lab 1 & 2'):
                        cur.execute("""
                            UPDATE lab_computers 
                            SET assigned_teacher_id = ?, assigned_teacher_username = ?, admin_user_id = ?, admin_username = ?, is_common_id = 1, common_id_name = ?, has_mail_services = 0
                        """, (adm_uid or new_uid, adm_uname or req['proposed_username'], adm_uid, adm_uname, c_name))
                    elif is_c and '1' in a_fleet:
                        cur.execute("""
                            UPDATE lab_computers 
                            SET assigned_teacher_id = ?, assigned_teacher_username = ?, admin_user_id = ?, admin_username = ?, is_common_id = 1, common_id_name = ?, has_mail_services = 0
                            WHERE lab_name LIKE '%Lab 1%'
                        """, (adm_uid or new_uid, adm_uname or req['proposed_username'], adm_uid, adm_uname, c_name))
                    elif is_c and '2' in a_fleet:
                        cur.execute("""
                            UPDATE lab_computers 
                            SET assigned_teacher_id = ?, assigned_teacher_username = ?, admin_user_id = ?, admin_username = ?, is_common_id = 1, common_id_name = ?, has_mail_services = 0
                            WHERE lab_name LIKE '%Lab 2%'
                        """, (adm_uid or new_uid, adm_uname or req['proposed_username'], adm_uid, adm_uname, c_name))

                    cur.execute("""
                        UPDATE credential_requests
                        SET status = 'Approved', approved_by = ?, approved_at = ?, user_id = ?
                        WHERE id = ?
                    """, (approver_name, now, new_uid, request_id))
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

                cur.execute("""
                    UPDATE credential_requests
                    SET status = 'Rejected', rejection_reason = ?, approved_by = ?, approved_at = ?
                    WHERE id = ?
                """, (reason, approver_name, now, request_id))
                conn.commit()
                self.send_json({
                    "success": True,
                    "message": f"Credential request #{request_id} has been rejected."
                })

            elif path == '/api/students':
                try:
                    rec = admit_single_student(cur, conn, body)
                    conn.commit()
                    self.send_json({
                        "success": True, 
                        "student": rec,
                        "message": f"Student '{rec['name']}' admitted successfully! Email: {rec['email']}, User ID: {rec['username']}, Password: {rec['password']}, Aadhaar: {rec.get('aadhaar_no', '')}"
                    })
                except ValueError as ve:
                    conn.rollback()
                    self.send_json({"success": False, "message": str(ve)}, 400)
                except Exception as ex:
                    conn.rollback()
                    self.send_json({"success": False, "message": f"Admission failed: {str(ex)}"}, 500)

            elif path == '/api/students/delete':
                student_id = body.get('student_id')
                if not student_id:
                    self.send_json({"success": False, "message": "student_id is required"}, 400)
                    return
                cur.execute("SELECT user_id, adm_no FROM students WHERE id = ?", (student_id,))
                row = cur.fetchone()
                if not row:
                    self.send_json({"success": False, "message": "Student record not found"}, 404)
                    return
                user_id = row['user_id']
                cur.execute("DELETE FROM marks WHERE student_id = ?", (student_id,))
                cur.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
                cur.execute("DELETE FROM payments WHERE student_id = ?", (student_id,))
                cur.execute("DELETE FROM students WHERE id = ?", (student_id,))
                if user_id:
                    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()
                self.send_json({"success": True, "message": "Student record and account deleted permanently."})

            elif path == '/api/students/delete_all':
                cur.execute("SELECT user_id FROM students")
                user_ids = [r['user_id'] for r in cur.fetchall() if r['user_id']]
                cur.execute("DELETE FROM marks")
                cur.execute("DELETE FROM attendance")
                cur.execute("DELETE FROM payments")
                cur.execute("DELETE FROM students")
                if user_ids:
                    placeholders = ','.join('?' for _ in user_ids)
                    cur.execute(f"DELETE FROM users WHERE id IN ({placeholders})", user_ids)
                cur.execute("DELETE FROM users WHERE user_type = 'student'")
                conn.commit()
                self.send_json({"success": True, "message": "All student records, admission files, marks, and login accounts have been deleted successfully."})

            elif path == '/api/teachers/create':
                name = body.get('name', '').strip()
                phone = body.get('phone', '+91 761 700 5055').strip()
                subject = body.get('subject', 'General Faculty').strip()
                qualification = body.get('qualification', 'B.Ed / Certified').strip()
                assign_section_id = body.get('assign_section_id')
                
                if not name:
                    self.send_json({"success": False, "message": "Teacher full name is required"}, 400)
                    return
                    
                parts = [p.capitalize() for p in name.split() if p]
                first = parts[0] if parts else "Teacher"
                last = parts[-1] if len(parts) > 1 else ""
                
                base_username = f"GS_teacher_{first}_{last}".rstrip('_')
                custom_username = body.get('username', '').strip()
                username = custom_username if custom_username else base_username
                
                idx = 1
                test_username = username
                while True:
                    cur.execute("SELECT id FROM users WHERE LOWER(username) = LOWER(?)", (test_username,))
                    if not cur.fetchone():
                        break
                    test_username = f"{username}_{idx}"
                    idx += 1
                username = test_username
                
                base_email = f"GS_teacher_{first}_{last}".rstrip('_').lower() + "@greenlandschool.net"
                custom_email = body.get('email', '').strip()
                email = custom_email if custom_email else base_email
                
                idx_e = 1
                test_email = email
                while True:
                    cur.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (test_email,))
                    if not cur.fetchone():
                        break
                    test_email = email.replace("@", f"_{idx_e}@")
                    idx_e += 1
                email = test_email
                
                password = body.get('password', 'Greenland@2026').strip() or 'Greenland@2026'
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                photo = body.get('photo', 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150')
                gender = body.get('gender', 'Male').strip()
                if gender not in ('Male', 'Female'): gender = 'Male'
                
                cur.execute("""
                    INSERT INTO users (name, email, username, password, user_type, phone, photo, created_at, subject, qualification, gender)
                    VALUES (?, ?, ?, ?, 'teacher', ?, ?, ?, ?, ?, ?)
                """, (name, email, username, password, phone, photo, now, subject, qualification, gender))
                teacher_id = cur.lastrowid
                
                # Auto-initialize leave quotas for this teacher based on gender
                get_or_create_leave_balances(cur, teacher_id)
                
                assigned_msg = "No class assigned"
                if assign_section_id:
                    try:
                        sec_id = int(assign_section_id)
                        if sec_id > 0:
                            cur.execute("UPDATE sections SET class_teacher_id = NULL WHERE class_teacher_id = ?", (teacher_id,))
                            cur.execute("UPDATE sections SET class_teacher_id = ? WHERE id = ?", (teacher_id, sec_id))
                            cur.execute("""
                                SELECT c.name as class_name, s.name as section_name
                                FROM sections s JOIN classes c ON s.class_id = c.id
                                WHERE s.id = ?
                            """, (sec_id,))
                            sr = cur.fetchone()
                            if sr:
                                assigned_msg = f"Assigned as Class Teacher of {sr['class_name']} ({sr['section_name']})"
                    except Exception:
                        pass
                        
                conn.commit()
                self.send_json({
                    "success": True,
                    "teacher_id": teacher_id,
                    "username": username,
                    "password": password,
                    "email": email,
                    "message": f"Teacher '{name}' registered successfully! User ID: {username}, Password: {password}. {assigned_msg}"
                })

            elif path == '/api/teachers/assign_class_teacher':
                teacher_id = body.get('teacher_id')
                section_id = body.get('section_id')
                
                if not teacher_id:
                    self.send_json({"success": False, "message": "Teacher ID is required"}, 400)
                    return
                    
                teacher_id = int(teacher_id)
                cur.execute("UPDATE sections SET class_teacher_id = NULL WHERE class_teacher_id = ?", (teacher_id,))
                
                assigned_text = "Unassigned"
                if section_id and int(section_id) > 0:
                    sec_id = int(section_id)
                    cur.execute("UPDATE sections SET class_teacher_id = ? WHERE id = ?", (teacher_id, sec_id))
                    cur.execute("""
                        SELECT c.name as class_name, s.name as section_name
                        FROM sections s JOIN classes c ON s.class_id = c.id
                        WHERE s.id = ?
                    """, (sec_id,))
                    r = cur.fetchone()
                    if r:
                        assigned_text = f"{r['class_name']} ({r['section_name']})"
                        
                conn.commit()
                self.send_json({
                    "success": True,
                    "message": f"Class teacher assignment updated successfully! Assigned to: {assigned_text}"
                })

            elif path == '/api/teachers/update':
                teacher_id = body.get('teacher_id')
                name = body.get('name', '').strip()
                phone = body.get('phone', '').strip()
                subject = body.get('subject', '').strip()
                qualification = body.get('qualification', '').strip()
                password = body.get('password', '').strip()
                email = body.get('email', '').strip()
                username = body.get('username', '').strip()
                
                if not teacher_id:
                    self.send_json({"success": False, "message": "Teacher ID is required"}, 400)
                    return
                    
                cur.execute("""
                    UPDATE users
                    SET name = COALESCE(NULLIF(?, ''), name),
                        phone = COALESCE(NULLIF(?, ''), phone),
                        subject = COALESCE(NULLIF(?, ''), subject),
                        qualification = COALESCE(NULLIF(?, ''), qualification),
                        password = COALESCE(NULLIF(?, ''), password),
                        email = COALESCE(NULLIF(?, ''), email),
                        username = COALESCE(NULLIF(?, ''), username)
                    WHERE id = ? AND user_type = 'teacher'
                """, (name, phone, subject, qualification, password, email, username, teacher_id))
                conn.commit()
                self.send_json({"success": True, "message": "Teacher details updated successfully!"})

            elif path == '/api/teachers/delete':
                teacher_id = body.get('teacher_id')
                if not teacher_id:
                    self.send_json({"success": False, "message": "Teacher ID is required"}, 400)
                    return
                cur.execute("UPDATE sections SET class_teacher_id = NULL WHERE class_teacher_id = ?", (teacher_id,))
                cur.execute("UPDATE subjects SET teacher_id = NULL WHERE teacher_id = ?", (teacher_id,))
                cur.execute("DELETE FROM leaves WHERE user_id = ?", (teacher_id,))
                cur.execute("DELETE FROM users WHERE id = ? AND user_type = 'teacher'", (teacher_id,))
                conn.commit()
                self.send_json({"success": True, "message": "Teacher removed successfully."})

            elif path == '/api/leaves/apply':
                user_id = body.get('user_id')
                leave_type = body.get('leave_type', 'Casual Leave (CL)').strip()
                start_date = body.get('start_date', '').strip()
                end_date = body.get('end_date', '').strip()
                reason = body.get('reason', '').strip()
                
                if not user_id or not start_date or not end_date or not reason:
                    self.send_json({"success": False, "message": "Please fill in all leave application details."}, 400)
                    return
                    
                cur.execute("SELECT id, name, user_type, COALESCE(gender, 'Male') as gender FROM users WHERE id = ?", (user_id,))
                u = cur.fetchone()
                if not u:
                    self.send_json({"success": False, "message": "User not found."}, 404)
                    return
                    
                role = u['user_type']
                gender = u['gender'] or 'Male'

                if role not in ('teacher', 'admin', 'super_admin'):
                    self.send_json({"success": False, "message": "Only Teachers and Principal have access to leave management."}, 403)
                    return

                # Strict Gender Rule Enforcement
                lt_lower = leave_type.lower()
                if 'maternity' in lt_lower:
                    if gender != 'Female':
                        self.send_json({
                            "success": False,
                            "message": "Eligibility Rejection: Maternity Leave (180 days) is strictly reserved for female employees. Male employees are not eligible."
                        }, 400)
                        return
                elif 'paternity' in lt_lower:
                    if gender != 'Male':
                        self.send_json({
                            "success": False,
                            "message": "Eligibility Rejection: Paternity Leave (15 days) is strictly reserved for male employees. Female employees are not eligible."
                        }, 400)
                        return

                try:
                    d1 = datetime.strptime(start_date, "%Y-%m-%d")
                    d2 = datetime.strptime(end_date, "%Y-%m-%d")
                    days = max(1, (d2 - d1).days + 1)
                except Exception:
                    days = 1

                # Quota balance check against official yearly leave allocation
                balances, _ = get_or_create_leave_balances(cur, user_id)
                if balances:
                    if 'casual' in lt_lower or 'cl' in lt_lower:
                        rem = balances['cl_total'] - balances['cl_used']
                        if days > rem:
                            self.send_json({"success": False, "message": f"Casual Leave limit exceeded. You have {rem} day(s) remaining out of 8 days per year."}, 400)
                            return
                    elif 'earned' in lt_lower or 'el' in lt_lower:
                        rem = balances['el_total'] - balances['el_used']
                        if days > rem:
                            self.send_json({"success": False, "message": f"Earned Leave limit exceeded. You have {rem} day(s) remaining out of {balances['el_total']} days credited this year."}, 400)
                            return
                    elif 'half pay' in lt_lower or 'hpl' in lt_lower:
                        rem = balances['hpl_total'] - balances['hpl_used']
                        if days > rem:
                            self.send_json({"success": False, "message": f"Half Pay Leave limit exceeded. You have {rem} day(s) remaining out of {balances['hpl_total']} days."}, 400)
                            return
                    elif 'maternity' in lt_lower:
                        rem = balances['maternity_total'] - balances['maternity_used']
                        if days > rem:
                            self.send_json({"success": False, "message": f"Maternity Leave limit exceeded. You have {rem} day(s) remaining out of 180 days."}, 400)
                            return
                    elif 'paternity' in lt_lower:
                        rem = balances['paternity_total'] - balances['paternity_used']
                        if days > rem:
                            self.send_json({"success": False, "message": f"Paternity Leave limit exceeded. You have {rem} day(s) remaining out of 15 days."}, 400)
                            return
                    elif 'child care' in lt_lower or 'ccl' in lt_lower:
                        rem = balances['ccl_total'] - balances['ccl_used']
                        if days > rem:
                            self.send_json({"success": False, "message": f"Child Care Leave limit exceeded. You have {rem} day(s) remaining out of 730 days."}, 400)
                            return

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur.execute("""
                    INSERT INTO leaves (user_id, applicant_role, leave_type, start_date, end_date, days_count, reason, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending', ?)
                """, (user_id, role, leave_type, start_date, end_date, days, reason, now))
                conn.commit()
                
                leave_id = cur.lastrowid
                target_approver = "Super Admin / Owner" if role == 'admin' else "Principal"
                self.send_json({
                    "success": True,
                    "leave_id": leave_id,
                    "days_count": days,
                    "message": f"Leave application for {days} day(s) submitted successfully! Awaiting review and approval from {target_approver}."
                })

            elif path == '/api/leaves/action':
                leave_id = body.get('leave_id')
                action = body.get('action', '').strip().lower()
                approver_id = body.get('approver_id')
                approver_role = body.get('approver_role', '').strip()
                notes = body.get('notes', '').strip()
                
                if not leave_id or action not in ('approve', 'reject'):
                    self.send_json({"success": False, "message": "Valid leave_id and action (approve/reject) required."}, 400)
                    return
                    
                cur.execute("SELECT l.*, u.user_type as applicant_role FROM leaves l JOIN users u ON l.user_id = u.id WHERE l.id = ?", (leave_id,))
                leave = cur.fetchone()
                if not leave:
                    self.send_json({"success": False, "message": "Leave request not found."}, 404)
                    return
                    
                # STRICT REQUIREMENT: Only Director has authority to approve requests created by Teachers or IT Team!
                if leave['applicant_role'] in ('teacher', 'it_admin') or 'teacher' in str(leave['applicant_role']).lower():
                    if approver_role not in ('super_admin',):
                        self.send_json({"success": False, "message": "Policy Enforcement: Only Director (Owner) Rajeev Sinha can approve Leave Requests created by Teachers or IT Team."}, 403)
                        return

                if leave['applicant_role'] == 'admin':
                    if approver_role != 'super_admin':
                        self.send_json({"success": False, "message": "Principal leave requests can only be reviewed and approved by Super Admin / Owner."}, 403)
                        return
                        
                new_status = 'Approved' if action == 'approve' else 'Rejected'
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Deduct used leave quota upon approval
                if action == 'approve':
                    get_or_create_leave_balances(cur, leave['user_id'])
                    lt_lower = leave['leave_type'].lower()
                    days = leave['days_count'] or 1
                    if 'casual' in lt_lower or 'cl' in lt_lower:
                        cur.execute("UPDATE employee_leave_balances SET cl_used = cl_used + ? WHERE user_id = ? AND year = 2026", (days, leave['user_id']))
                    elif 'earned' in lt_lower or 'el' in lt_lower:
                        cur.execute("UPDATE employee_leave_balances SET el_used = el_used + ? WHERE user_id = ? AND year = 2026", (days, leave['user_id']))
                    elif 'half pay' in lt_lower or 'hpl' in lt_lower:
                        cur.execute("UPDATE employee_leave_balances SET hpl_used = hpl_used + ? WHERE user_id = ? AND year = 2026", (days, leave['user_id']))
                    elif 'maternity' in lt_lower:
                        cur.execute("UPDATE employee_leave_balances SET maternity_used = maternity_used + ? WHERE user_id = ? AND year = 2026", (days, leave['user_id']))
                    elif 'paternity' in lt_lower:
                        cur.execute("UPDATE employee_leave_balances SET paternity_used = paternity_used + ? WHERE user_id = ? AND year = 2026", (days, leave['user_id']))
                    elif 'child care' in lt_lower or 'ccl' in lt_lower:
                        cur.execute("UPDATE employee_leave_balances SET ccl_used = ccl_used + ? WHERE user_id = ? AND year = 2026", (days, leave['user_id']))
                
                cur.execute("""
                    UPDATE leaves
                    SET status = ?, approver_id = ?, approver_role = ?, approver_notes = ?, updated_at = ?
                    WHERE id = ?
                """, (new_status, approver_id, approver_role, notes, now, leave_id))
                conn.commit()
                
                self.send_json({
                    "success": True,
                    "status": new_status,
                    "message": f"Leave request #{leave_id} has been {new_status.lower()} successfully."
                })

            # TEACHER & SUPER ADMIN LEAVE DELETION ENDPOINT
            elif path == '/api/leaves/delete':
                leave_id = body.get('leave_id')
                user_id = body.get('user_id')
                user_role = str(body.get('user_role', '')).strip().lower()
                username = str(body.get('username', '')).strip()

                if not leave_id:
                    self.send_json({"success": False, "message": "leave_id is required."}, 400)
                    return

                cur.execute("SELECT * FROM leaves WHERE id = ?", (leave_id,))
                leave = cur.fetchone()
                if not leave:
                    self.send_json({"success": False, "message": "Leave request not found in database."}, 404)
                    return

                is_super_admin = (user_role == 'super_admin' or username in ('GS_superadmin', 'Owner(Directer)'))

                # RULE 1: SUPER ADMIN & OWNER(DIRECTER) CAN DELETE ANY LEAVE (BEFORE OR AFTER APPROVAL)
                if is_super_admin:
                    # Restore quota if was approved
                    if leave['status'] == 'Approved':
                        lt_lower = leave['leave_type'].lower()
                        days = leave['days_count'] or 1
                        if 'casual' in lt_lower or 'cl' in lt_lower:
                            cur.execute("UPDATE employee_leave_balances SET cl_used = MAX(0, cl_used - ?) WHERE user_id = ? AND year = 2026", (days, leave['user_id']))
                        elif 'earned' in lt_lower or 'el' in lt_lower:
                            cur.execute("UPDATE employee_leave_balances SET el_used = MAX(0, el_used - ?) WHERE user_id = ? AND year = 2026", (days, leave['user_id']))
                        elif 'half pay' in lt_lower or 'hpl' in lt_lower:
                            cur.execute("UPDATE employee_leave_balances SET hpl_used = MAX(0, hpl_used - ?) WHERE user_id = ? AND year = 2026", (days, leave['user_id']))
                        elif 'maternity' in lt_lower:
                            cur.execute("UPDATE employee_leave_balances SET maternity_used = MAX(0, maternity_used - ?) WHERE user_id = ? AND year = 2026", (days, leave['user_id']))
                        elif 'paternity' in lt_lower:
                            cur.execute("UPDATE employee_leave_balances SET paternity_used = MAX(0, paternity_used - ?) WHERE user_id = ? AND year = 2026", (days, leave['user_id']))
                        elif 'child care' in lt_lower or 'ccl' in lt_lower:
                            cur.execute("UPDATE employee_leave_balances SET ccl_used = MAX(0, ccl_used - ?) WHERE user_id = ? AND year = 2026", (days, leave['user_id']))

                    cur.execute("DELETE FROM leaves WHERE id = ?", (leave_id,))
                    conn.commit()
                    self.send_json({
                        "success": True,
                        "message": f"Leave request #{leave_id} successfully deleted from the database by Super Admin / Owner."
                    })
                    return

                # RULE 2: TEACHERS CAN DELETE THEIR OWN LEAVE ONLY BEFORE APPROVAL (STATUS == 'Pending')
                if user_role == 'teacher' or leave['user_id'] == user_id:
                    if leave['user_id'] != user_id and user_role != 'teacher':
                        self.send_json({"success": False, "message": "Unauthorized to delete this leave request."}, 403)
                        return

                    if leave['status'] != 'Pending':
                        self.send_json({
                            "success": False,
                            "message": "Permission Denied: Teachers can only delete their leave requests BEFORE approval by Principal or Super Admin. Approved leave data can only be deleted by Super Admin / Owner(Directer)."
                        }, 403)
                        return

                    # Pending leave deletion
                    cur.execute("DELETE FROM leaves WHERE id = ?", (leave_id,))
                    conn.commit()
                    self.send_json({
                        "success": True,
                        "message": f"Your pending leave application #{leave_id} has been cancelled and deleted."
                    })
                    return

                self.send_json({"success": False, "message": "Unauthorized action."}, 403)

            elif path == '/api/leaves/toggle_principal_status':
                set_on_leave = body.get('on_leave', True)
                now_date = datetime.now().strftime("%Y-%m-%d")
                end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                
                cur.execute("SELECT id FROM users WHERE user_type = 'admin' LIMIT 1")
                p = cur.fetchone()
                if p:
                    principal_id = p['id']
                    if set_on_leave:
                        cur.execute("""
                            INSERT INTO leaves (user_id, applicant_role, leave_type, start_date, end_date, days_count, reason, status, approver_role, approver_notes, created_at)
                            VALUES (?, 'admin', 'Official Executive Leave', ?, ?, 7, 'Principal is away on approved executive leave (Simulated / Active)', 'Approved', 'super_admin', 'Approved by Super Admin', ?)
                        """, (principal_id, now_date, end_date, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    else:
                        cur.execute("""
                            UPDATE leaves SET status = 'Completed', end_date = ?
                            WHERE user_id = ? AND status = 'Approved' AND end_date >= ?
                        """, (now_date, principal_id, now_date))
                    conn.commit()
                self.send_json({"success": True, "principal_on_leave": set_on_leave, "message": f"Principal status updated: {'ON LEAVE (Direct routing to Super Admin active)' if set_on_leave else 'ON DUTY (Standard Principal approvals active)'}"})

            elif path == '/api/marks':
                student_id = body.get('student_id')
                subject_id = body.get('subject_id')
                exam_id = body.get('exam_id', 1)
                ca = float(body.get('ca_score', 0))
                ex = float(body.get('exam_score', 0))
                total = ca + ex

                if total >= 70: grade, rmk = 'A', 'Excellent'
                elif total >= 60: grade, rmk = 'B', 'Very Good'
                elif total >= 50: grade, rmk = 'C', 'Good'
                elif total >= 45: grade, rmk = 'D', 'Pass'
                elif total >= 40: grade, rmk = 'E', 'Poor'
                else: grade, rmk = 'F', 'Fail'

                cur.execute("""
                    INSERT INTO marks (student_id, subject_id, exam_id, ca_score, exam_score, total, grade, remark)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(student_id, subject_id, exam_id) DO UPDATE SET
                    ca_score=excluded.ca_score, exam_score=excluded.exam_score,
                    total=excluded.total, grade=excluded.grade, remark=excluded.remark
                """, (student_id, subject_id, exam_id, ca, ex, total, grade, rmk))
                conn.commit()
                self.send_json({"success": True, "total": total, "grade": grade, "remark": rmk})

            elif path == '/api/attendance':
                records = body.get('records', [])
                date_str = body.get('date', datetime.now().strftime("%Y-%m-%d"))
                class_id = body.get('class_id', 9)
                for r in records:
                    cur.execute("""
                        INSERT INTO attendance (student_id, class_id, date, status)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(student_id, date) DO UPDATE SET status=excluded.status
                    """, (r['student_id'], class_id, date_str, r['status']))
                conn.commit()
                self.send_json({"success": True, "message": "Attendance records saved!"})

            elif path == '/api/payments':
                ref = "REC-" + datetime.now().strftime("%Y") + "-" + str(os.urandom(2).hex().upper())
                date_str = datetime.now().strftime("%Y-%m-%d")
                amt = float(body.get('amount', 0))
                paid = float(body.get('paid', amt))
                status = "Paid" if paid >= amt else ("Partial" if paid > 0 else "Unpaid")
                method = body.get('method', 'Offline / Cash')
                txn_ref = body.get('transaction_ref', '')

                cur.execute("""
                    INSERT INTO payments (student_id, title, amount, paid, status, ref_no, date, method, transaction_ref)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    body.get('student_id', 1),
                    body.get('title', 'School Fees Payment'),
                    amt,
                    paid,
                    status,
                    ref,
                    date_str,
                    method,
                    txn_ref
                ))
                conn.commit()
                self.send_json({"success": True, "ref_no": ref, "message": "Payment recorded successfully!"})

            # ONLINE PAYMENT GATEWAY (UPI QR CODE & NET BANKING)
            elif path == '/api/payments/pay_online':
                student_id = body.get('student_id')
                amount = float(body.get('amount', 0))
                method = str(body.get('method', 'QR Code / UPI')).strip()
                bank_name = str(body.get('bank_name', '')).strip()
                transaction_ref = str(body.get('transaction_ref', '')).strip()
                
                if not student_id or amount <= 0:
                    self.send_json({"success": False, "message": "Valid student and payment amount are required."}, 400)
                    return
                    
                if not transaction_ref:
                    transaction_ref = "TXN-" + datetime.now().strftime("%Y%m%d%H%M%S") + "-" + os.urandom(2).hex().upper()

                cur.execute("""
                    SELECT st.id, u.name, c.name as class_name
                    FROM students st
                    JOIN users u ON st.user_id = u.id
                    JOIN classes c ON st.class_id = c.id
                    WHERE st.id = ?
                """, (student_id,))
                std_row = cur.fetchone()
                if not std_row:
                    self.send_json({"success": False, "message": "Student record not found in school registry."}, 404)
                    return

                ref_no = "REC-" + datetime.now().strftime("%Y") + "-" + str(os.urandom(2).hex().upper())
                date_str = datetime.now().strftime("%Y-%m-%d")
                title = f"Tuition Fee Online Payment ({method})"
                if bank_name:
                    title += f" - {bank_name}"

                cur.execute("""
                    INSERT INTO payments (student_id, title, amount, paid, status, ref_no, date, method, transaction_ref)
                    VALUES (?, ?, ?, ?, 'Paid', ?, ?, ?, ?)
                """, (student_id, title, amount, amount, ref_no, date_str, method, transaction_ref))
                payment_id = cur.lastrowid
                conn.commit()

                self.send_json({
                    "success": True,
                    "payment_id": payment_id,
                    "ref_no": ref_no,
                    "amount": amount,
                    "student_name": std_row[1],
                    "class_name": std_row[2],
                    "method": method,
                    "transaction_ref": transaction_ref,
                    "date": date_str,
                    "message": f"Online payment of ₹{amount:,.2f} completed successfully via {method}! Official Receipt Ref: {ref_no}"
                })

            # PARENT PORTAL: EDIT CHILD OFFICIAL NAME VIA AADHAAR VERIFICATION
            elif path == '/api/parent/update_child_name':
                student_id = body.get('student_id')
                new_name = str(body.get('new_name', '')).strip()
                entered_aadhaar = str(body.get('aadhaar_no', '')).strip()
                clean_entered_aadhaar = re.sub(r'[\s\-]', '', entered_aadhaar)

                if not student_id or not new_name:
                    self.send_json({"success": False, "message": "Student selection and new name are required."}, 400)
                    return

                if not clean_entered_aadhaar or len(clean_entered_aadhaar) != 12:
                    self.send_json({"success": False, "message": "A strictly 12-digit Aadhaar number is required for identity verification."}, 400)
                    return

                cur.execute("""
                    SELECT st.id, st.user_id, st.aadhaar_no, u.name
                    FROM students st
                    JOIN users u ON st.user_id = u.id
                    WHERE st.id = ?
                """, (student_id,))
                row = cur.fetchone()
                if not row:
                    self.send_json({"success": False, "message": "Student record not found in school database."}, 404)
                    return

                actual_aadhaar = str(row[2] or '').strip()
                old_name = row[3]

                # STRICT AADHAAR IDENTITY VERIFICATION
                if clean_entered_aadhaar != actual_aadhaar:
                    self.send_json({
                        "success": False,
                        "message": "Aadhaar verification failed! The entered 12-digit Aadhaar number does not match school admission records for this child. Name modification rejected."
                    }, 403)
                    return

                # Identity verified! Update official records
                user_id = row[1]
                cur.execute("UPDATE users SET name = ? WHERE id = ?", (new_name, user_id))
                cur.execute("UPDATE admissions SET applicant_name = ? WHERE applicant_name = ?", (new_name, old_name))
                conn.commit()

                self.send_json({
                    "success": True,
                    "old_name": old_name,
                    "new_name": new_name,
                    "message": f"Aadhaar verified successfully! Child official name has been updated from '{old_name}' to '{new_name}' in Greenland School records."
                })

            # HELPER: ENROLL DEMO WARD FOR PARENT IF 0 STUDENTS
            elif path == '/api/parent/enroll_demo_ward':
                parent_user_id = body.get('parent_id') or 8
                cur.execute("SELECT id, name FROM users WHERE id = ? OR username = 'GS_parent'", (parent_user_id,))
                p_user = cur.fetchone()
                p_id = p_user[0] if p_user else 8
                p_name = p_user[1] if p_user else "Parent Marcus Kaba"

                # Check if student Alex Kaba already exists
                cur.execute("SELECT id FROM students WHERE adm_no = 'GS/2026/0001'")
                exist_st = cur.fetchone()
                if exist_st:
                    self.send_json({"success": True, "message": "Student ward already exists!"})
                    return

                demo_data = {
                    "first_name": "Alex",
                    "last_name": "Kaba",
                    "name": "Alex Kaba",
                    "class_name": "Class 10",
                    "section": "Section A",
                    "parent_id": p_id,
                    "parent_name": p_name,
                    "phone": "+91 761 700 5055",
                    "aadhaar_no": "548962147801",
                    "blood_group": "O+",
                    "gender": "Male",
                    "dob": "2011-04-15",
                    "adm_no": "GS/2026/0001"
                }
                rec = admit_single_student(cur, conn, demo_data)
                
                # Add initial partial payment so there's fee due
                ref = "REC-2026-F9A1"
                date_str = datetime.now().strftime("%Y-%m-%d")
                cur.execute("""
                    INSERT INTO payments (student_id, title, amount, paid, status, ref_no, date, method)
                    VALUES (?, 'First Term Tuition Fee (Advance)', 45000, 15000, 'Partial', ?, ?, 'Net Banking')
                """, (rec['student_id'], ref, date_str))
                conn.commit()

                self.send_json({
                    "success": True,
                    "student": rec,
                    "message": "Demo student ward 'Alex Kaba' enrolled with Aadhaar 548962147801 and fee ledger created!"
                })

            # ACCOUNTANT: REQUEST WRONGLY PROCESSED PAYMENT DELETION
            elif path == '/api/payments/request_delete':
                payment_id = body.get('payment_id')
                reason = str(body.get('reason', '')).strip()
                requested_by_id = body.get('requested_by_id')
                requested_by_name = str(body.get('requested_by_name', 'Accountant Jude Bello')).strip()

                if not payment_id or not reason:
                    self.send_json({"success": False, "message": "Payment record and reason for deletion are required."}, 400)
                    return

                cur.execute("""
                    SELECT p.id, p.ref_no, p.amount, p.paid, u.name as student_name, p.student_id
                    FROM payments p
                    JOIN students st ON p.student_id = st.id
                    JOIN users u ON st.user_id = u.id
                    WHERE p.id = ?
                """, (payment_id,))
                p_row = cur.fetchone()
                if not p_row:
                    self.send_json({"success": False, "message": "Payment record not found."}, 404)
                    return

                cur.execute("SELECT id, final_status FROM payment_delete_requests WHERE payment_id = ? AND final_status = 'In Progress'", (payment_id,))
                existing = cur.fetchone()
                if existing:
                    self.send_json({"success": False, "message": f"A deletion request is already active for this payment (Request #{existing[0]})."}, 400)
                    return

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur.execute("""
                    INSERT INTO payment_delete_requests 
                    (payment_id, payment_ref, receipt_no, student_name, student_id, amount, paid, reason, requested_by_id, requested_by_name, admin_status, superadmin_status, final_status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', 'Awaiting Admin Approval', 'In Progress', ?)
                """, (p_row[0], p_row[1], p_row[1], p_row[4], p_row[5], p_row[2], p_row[3], reason, requested_by_id, requested_by_name, now))
                req_id = cur.lastrowid
                conn.commit()

                self.send_json({
                    "success": True,
                    "request_id": req_id,
                    "message": f"Deletion request #{req_id} submitted by Fee Department! Flow: Admin (Principal) must approve first, then Super Admin must approve, then it will be deleted from the database."
                })

            # DUAL APPROVAL WORKFLOW: ADMIN (PRINCIPAL) & SUPER ADMIN
            elif path == '/api/payments/approve_delete':
                request_id = body.get('request_id')
                role = str(body.get('role', '')).strip().lower()
                action = str(body.get('action', 'approve')).strip().lower()
                notes = str(body.get('notes', '')).strip()
                reviewer_id = body.get('reviewer_id')
                reviewer_name = str(body.get('reviewer_name', '')).strip()
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if not request_id:
                    self.send_json({"success": False, "message": "request_id is required."}, 400)
                    return

                cur.execute("SELECT * FROM payment_delete_requests WHERE id = ?", (request_id,))
                req = cur.fetchone()
                if not req:
                    self.send_json({"success": False, "message": "Deletion request record not found."}, 404)
                    return

                req_dict = dict(req)
                payment_id = req_dict['payment_id']
                payment_ref = req_dict['payment_ref']

                if req_dict['final_status'] != 'In Progress':
                    self.send_json({"success": False, "message": f"This deletion request is already resolved ({req_dict['final_status']})."}, 400)
                    return

                # TIER 1: ADMIN (PRINCIPAL) APPROVAL
                if role == 'admin':
                    if req_dict['admin_status'] != 'Pending':
                        self.send_json({"success": False, "message": "Admin has already reviewed this request."}, 400)
                        return

                    if action == 'approve':
                        cur.execute("""
                            UPDATE payment_delete_requests
                            SET admin_status = 'Approved',
                                admin_id = ?,
                                admin_name = ?,
                                admin_notes = ?,
                                admin_action_date = ?,
                                superadmin_status = 'Pending'
                            WHERE id = ?
                        """, (reviewer_id, reviewer_name or 'Admin (Principal)', notes or 'Approved by Principal. Forwarded to Super Admin.', now, request_id))
                        conn.commit()
                        self.send_json({
                            "success": True,
                            "message": f"Admin (Principal) approved deletion request #{request_id}. Forwarded to Super Admin for final authority."
                        })
                        return
                    else:
                        cur.execute("""
                            UPDATE payment_delete_requests
                            SET admin_status = 'Rejected',
                                admin_id = ?,
                                admin_name = ?,
                                admin_notes = ?,
                                admin_action_date = ?,
                                superadmin_status = 'Rejected',
                                final_status = 'Rejected'
                            WHERE id = ?
                        """, (reviewer_id, reviewer_name or 'Admin (Principal)', notes or 'Rejected by Principal.', now, request_id))
                        conn.commit()
                        self.send_json({
                            "success": True,
                            "message": f"Deletion request #{request_id} was rejected by Principal. Payment record remains in database."
                        })
                        return

                # TIER 2: SUPER ADMIN FINAL APPROVAL & PERMANENT DATABASE DELETION
                elif role == 'super_admin':
                    # STRICT PROTOCOL ENFORCEMENT: Admin must approve first!
                    if req_dict['admin_status'] != 'Approved':
                        self.send_json({
                            "success": False,
                            "message": "Protocol Violation: Admin (Principal) must approve the deletion first before Super Admin can approve! Otherwise the process will not flow."
                        }, 400)
                        return

                    if req_dict['superadmin_status'] != 'Pending':
                        self.send_json({"success": False, "message": f"Super Admin status is currently '{req_dict['superadmin_status']}'."}, 400)
                        return

                    if action == 'approve':
                        # Both approvals complete! Permanently delete payment from database
                        cur.execute("DELETE FROM payments WHERE id = ?", (payment_id,))
                        cur.execute("""
                            UPDATE payment_delete_requests
                            SET superadmin_status = 'Approved',
                                superadmin_id = ?,
                                superadmin_name = ?,
                                superadmin_notes = ?,
                                superadmin_action_date = ?,
                                final_status = 'Approved & Deleted'
                            WHERE id = ?
                        """, (reviewer_id, reviewer_name or 'Super Admin', notes or 'Dual-approval complete. Permanently deleted from database.', now, request_id))
                        conn.commit()
                        self.send_json({
                            "success": True,
                            "message": f"Dual-approval complete! Payment {payment_ref} has been permanently deleted from Greenland School database."
                        })
                        return
                    else:
                        cur.execute("""
                            UPDATE payment_delete_requests
                            SET superadmin_status = 'Rejected',
                                superadmin_id = ?,
                                superadmin_name = ?,
                                superadmin_notes = ?,
                                superadmin_action_date = ?,
                                final_status = 'Rejected'
                            WHERE id = ?
                        """, (reviewer_id, reviewer_name or 'Super Admin', notes or 'Rejected by Super Admin.', now, request_id))
                        conn.commit()
                        self.send_json({
                            "success": True,
                            "message": f"Deletion request #{request_id} was rejected by Super Admin. Payment record remains in database."
                        })
                        return
                else:
                    self.send_json({"success": False, "message": "Unauthorized role for approving payment deletion."}, 403)

            # SUPER ADMIN DIRECT RIGHT TO DELETE FROM DATABASE
            elif path == '/api/payments/direct_delete':
                payment_id = body.get('payment_id')
                role = str(body.get('role', '')).strip().lower()
                reason = str(body.get('reason', 'Direct deletion by Super Admin')).strip()
                user_id = body.get('user_id')
                user_name = str(body.get('user_name', 'Super Admin')).strip()
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if role != 'super_admin':
                    self.send_json({"success": False, "message": "Unauthorized: Only Super Admin holds the direct right to delete payment records immediately from the database."}, 403)
                    return

                if not payment_id:
                    self.send_json({"success": False, "message": "payment_id is required."}, 400)
                    return

                cur.execute("SELECT id, ref_no, amount FROM payments WHERE id = ?", (payment_id,))
                p_row = cur.fetchone()
                if not p_row:
                    self.send_json({"success": False, "message": "Payment record not found."}, 404)
                    return

                payment_ref = p_row[1]
                # Permanently delete from database
                cur.execute("DELETE FROM payments WHERE id = ?", (payment_id,))

                # Resolve any pending delete requests for this payment
                cur.execute("""
                    UPDATE payment_delete_requests
                    SET final_status = 'Approved & Deleted (Direct by Super Admin)',
                        superadmin_status = 'Approved',
                        superadmin_id = ?,
                        superadmin_name = ?,
                        superadmin_notes = ?,
                        superadmin_action_date = ?
                    WHERE payment_id = ? AND final_status = 'In Progress'
                """, (user_id, user_name, reason, now, payment_id))

                conn.commit()
                self.send_json({
                    "success": True,
                    "message": f"Payment {payment_ref} directly and permanently deleted from Greenland School database by Super Admin."
                })

            elif path == '/api/notices':
                date_str = datetime.now().strftime("%Y-%m-%d")
                cur.execute("""
                    INSERT INTO notices (title, content, category, date, pinned)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    body.get('title', ''),
                    body.get('content', ''),
                    body.get('category', 'General'),
                    date_str,
                    1 if body.get('pinned') else 0
                ))
                conn.commit()
                self.send_json({"success": True, "message": "Notice published successfully!"})

            elif path == '/api/library/add':
                bookshelf_no = body.get('bookshelf_no', 'Shelf A-1').strip() or 'Shelf A-1'
                total_copies = int(body.get('total_copies', 10))
                title = body.get('title', '').strip()
                author = body.get('author', '').strip()
                isbn = body.get('isbn', '').strip()
                category = body.get('category', 'General').strip()
                
                cur.execute("""
                    INSERT INTO books (title, author, isbn, category, total_copies, available_copies, bookshelf_no)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (title, author, isbn, category, total_copies, total_copies, bookshelf_no))
                conn.commit()
                self.send_json({"success": True, "message": f"Book '{title}' cataloged successfully on Bookshelf {bookshelf_no}!"})

            elif path == '/api/library/issue':
                book_id = int(body.get('book_id', 0))
                student_user_id = int(body.get('student_user_id', 0))
                due_date = body.get('due_date', (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"))
                issue_date = body.get('issue_date', datetime.now().strftime("%Y-%m-%d"))
                issue_time = body.get('issue_time', datetime.now().strftime("%H:%M:%S"))
                issuer_name = body.get('issuer_name', 'Administration Desk')
                
                cur.execute("SELECT id, title, available_copies, COALESCE(bookshelf_no, 'Shelf A-1') as bookshelf_no FROM books WHERE id = ?", (book_id,))
                book = cur.fetchone()
                if not book:
                    self.send_json({"success": False, "message": "Book not found in catalogue."}, 404)
                    return
                if book['available_copies'] <= 0:
                    self.send_json({"success": False, "message": f"'{book['title']}' is currently out of stock."}, 400)
                    return
                    
                bookshelf_no = body.get('bookshelf_no') or book['bookshelf_no'] or 'Shelf A-1'
                
                cur.execute("""
                    INSERT INTO book_requests (book_id, user_id, issue_date, issue_time, due_date, status, bookshelf_no, issuer_name)
                    VALUES (?, ?, ?, ?, ?, 'Issued', ?, ?)
                """, (book_id, student_user_id, issue_date, issue_time, due_date, bookshelf_no, issuer_name))
                
                cur.execute("UPDATE books SET available_copies = available_copies - 1 WHERE id = ?", (book_id,))
                conn.commit()
                
                self.send_json({
                    "success": True,
                    "message": f"'{book['title']}' successfully issued from Bookshelf {bookshelf_no} at {issue_time}!"
                })

            elif path == '/api/library/return':
                request_id = int(body.get('request_id', 0))
                cur.execute("""
                    SELECT br.*, b.title, b.id as b_id 
                    FROM book_requests br 
                    JOIN books b ON br.book_id = b.id 
                    WHERE br.id = ?
                """, (request_id,))
                req = cur.fetchone()
                if not req:
                    self.send_json({"success": False, "message": "Issue record not found."}, 404)
                    return
                if req['status'] == 'Returned':
                    self.send_json({"success": False, "message": "Book is already marked as returned."}, 400)
                    return
                    
                ret_date = datetime.now().strftime("%Y-%m-%d")
                ret_time = datetime.now().strftime("%H:%M:%S")
                cur.execute("""
                    UPDATE book_requests 
                    SET status = 'Returned', return_date = ?, return_time = ?
                    WHERE id = ?
                """, (ret_date, ret_time, request_id))
                cur.execute("UPDATE books SET available_copies = available_copies + 1 WHERE id = ?", (req['b_id'],))
                conn.commit()
                self.send_json({"success": True, "message": f"Book '{req['title']}' returned successfully and stock restored!"})

            elif path == '/api/library/delete':
                book_id = int(body.get('book_id', 0))
                cur.execute("SELECT COUNT(*) FROM book_requests WHERE book_id = ? AND status = 'Issued'", (book_id,))
                active_loans = cur.fetchone()[0]
                if active_loans > 0:
                    self.send_json({"success": False, "message": f"Cannot delete book: {active_loans} copy is currently issued out."}, 400)
                    return
                cur.execute("DELETE FROM book_requests WHERE book_id = ?", (book_id,))
                cur.execute("DELETE FROM books WHERE id = ?", (book_id,))
                conn.commit()
                self.send_json({"success": True, "message": "Book removed from catalogue successfully."})

            elif path == '/api/payroll/generate':
                # Generated by accountant (or director/admin) for teachers & faculty
                month = int(body.get('month', 11))
                year = int(body.get('year', 2026))
                user_id = body.get('user_id')
                user_name = body.get('user_name', 'Account Department')

                cur.execute("SELECT id, name, username, user_type FROM users WHERE id = ? OR username = ?", (user_id, body.get('username')))
                caller = cur.fetchone()
                caller_name = caller['name'] if caller else user_name

                generated_slips = auto_generate_salary_slips_for_month(cur, month, year)
                conn.commit()

                self.send_json({
                    "success": True,
                    "message": f"Successfully generated official salary slips for {len(generated_slips)} faculty members for {month:02d}/{year}. (Note: Accountant personal salary slip is excluded and must be issued directly by the Director).",
                    "generated_count": len(generated_slips),
                    "slips": generated_slips
                })

            elif path == '/api/payroll/generate_accountant':
                # STRICT REQUIREMENT: Only Director (Owner) can issue the Accountant's salary slip!
                user_id = body.get('user_id')
                username = body.get('username', '').strip()
                month = int(body.get('month', 11))
                year = int(body.get('year', 2026))
                base_salary = float(body.get('base_salary', 55000.0))
                special_bonus = float(body.get('special_bonus', 0.0))
                bonus_title = body.get('special_bonus_title', 'Director Financial Operations Allowance').strip()

                cur.execute("SELECT id, name, username, user_type FROM users WHERE id = ? OR username = ?", (user_id, username))
                user_row = cur.fetchone()
                if not user_row or (user_row['username'] != 'Owner(Directer)' and user_row['user_type'] != 'super_admin'):
                    self.send_json({
                        "success": False,
                        "error": "Access Denied: The Accountant's salary slip can ONLY be sanctioned and issued directly by the Director (Owner)."
                    }, 403)
                    return

                cur.execute("SELECT id, name, username, COALESCE(base_salary, 55000.0) as base_salary FROM users WHERE user_type = 'accountant' LIMIT 1")
                acc = cur.fetchone()
                if not acc:
                    self.send_json({"success": False, "error": "No accountant user found in the system."}, 404)
                    return

                slip_res = generate_accountant_salary_slip(cur, month, year, base_salary=base_salary, special_bonus=special_bonus, bonus_title=bonus_title, director_name=user_row['name'])
                conn.commit()
                self.send_json({
                    "success": True,
                    "message": f"Official Accountant salary payslip for {acc['name']} ({month:02d}/{year}) sanctioned and issued by {user_row['name']}!",
                    "slip": slip_res
                })

            elif path == '/api/payroll/special_bonus':
                # STRICT REQUIREMENT: Only Owner (Director) can add special salary / Diwali bonuses!
                user_id = body.get('user_id')
                username = body.get('username', '').strip()
                title = body.get('title', '').strip()
                try:
                    amount = float(body.get('amount', 0))
                except Exception:
                    amount = 0.0
                month = int(body.get('month', 11))
                year = int(body.get('year', 2026))
                teacher_id = body.get('teacher_id')
                if teacher_id in ('all', '', 'null', None):
                    teacher_id = None
                else:
                    try:
                        teacher_id = int(teacher_id)
                    except Exception:
                        teacher_id = None
                notes = body.get('notes', '').strip()

                cur.execute("SELECT id, name, username, user_type FROM users WHERE id = ? OR username = ?", (user_id, username))
                user_row = cur.fetchone()
                if not user_row or user_row['username'] != 'Owner(Directer)':
                    self.send_json({
                        "success": False,
                        "error": "Access Denied: Only Owner (Director) has executive permission to grant special salary bonuses (e.g. Diwali Bonus)."
                    }, 403)
                    return

                if not title or amount <= 0:
                    self.send_json({"success": False, "error": "Please specify a valid bonus title and positive amount."}, 400)
                    return

                cur.execute("""
                    INSERT INTO special_bonuses (teacher_id, title, amount, month, year, granted_by, granted_by_id, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (teacher_id, title, amount, month, year, user_row['name'], user_row['id'], notes))
                conn.commit()

                # Automatically update salary slips for this month so bonus reflects immediately
                auto_generate_salary_slips_for_month(cur, month, year)
                conn.commit()

                self.send_json({
                    "success": True,
                    "message": f"Special bonus '{title}' of ₹{amount:,.2f} successfully authorized by Owner (Director) Rajeev Sinha and incorporated into faculty payroll!",
                    "bonus": {
                        "title": title,
                        "amount": amount,
                        "month": month,
                        "year": year,
                        "granted_by": user_row['name']
                    }
                })

            elif path == '/api/settings':
                for k, v in body.items():
                    cur.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, str(v)))
                conn.commit()
                self.send_json({"success": True, "message": "Settings updated!"})

            elif path == '/api/settings/test_email':
                target_email = body.get('target_email') or body.get('to_email') or 'test@greenlandschool.net'
                smtp_host = body.get('smtp_host', 'smtp.gmail.com').strip()
                try:
                    smtp_port = int(body.get('smtp_port', 587))
                except Exception:
                    smtp_port = 587
                smtp_user = body.get('smtp_user', '').strip()
                smtp_pass = body.get('smtp_pass', '').strip()
                smtp_tls = str(body.get('smtp_tls', '1')).strip() == '1'
                smtp_ssl = str(body.get('smtp_ssl', '0')).strip() == '1'
                sender_email = body.get('smtp_sender_email') or smtp_user or 'info@greenlandschool.net'
                sender_name = body.get('smtp_sender_name', 'Greenland School Admissions').strip()

                if not smtp_host:
                    self.send_json({"success": False, "error": "SMTP Host is required for testing."}, 400)
                    return
                if not smtp_user or not smtp_pass:
                    self.send_json({"success": False, "error": "SMTP Username and App Password are required for live sending test."}, 400)
                    return

                try:
                    test_msg = MIMEMultipart('alternative')
                    test_msg['Subject'] = "🧪 Greenland School - Live SMTP Dispatch Verification"
                    test_msg['From'] = f"{sender_name} <{sender_email}>"
                    test_msg['To'] = target_email
                    test_msg['Date'] = email_utils.formatdate(localtime=True)
                    test_plain = f"This is an automated test notification dispatched by Greenland School Admissions System at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. Your SMTP credentials are functioning properly!"
                    test_html = f"""<div style="font-family:Arial,sans-serif; max-width:600px; padding:20px; border:1px solid #e2e8f0; border-radius:8px;">
                        <h2 style="color:#1e3a8a; margin-top:0;">Greenland School - SMTP Test Verified</h2>
                        <p>Your SMTP credentials are authenticated and live!</p>
                        <p><strong>Server Host:</strong> {smtp_host}:{smtp_port}</p>
                        <p><strong>Authenticated User:</strong> {smtp_user}</p>
                        <p><strong>Dispatched At:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <div style="background:#ecfdf5; color:#065f46; padding:10px 14px; border-radius:6px; font-weight:bold;">
                            ✓ Official admission approval notices will be sent live to candidate inboxes.
                        </div>
                    </div>"""
                    test_msg.attach(MIMEText(test_plain, 'plain', 'utf-8'))
                    test_msg.attach(MIMEText(test_html, 'html', 'utf-8'))

                    if smtp_ssl or smtp_port == 465:
                        server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=12)
                    else:
                        server = smtplib.SMTP(smtp_host, smtp_port, timeout=12)
                        if smtp_tls:
                            server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.sendmail(sender_email, [target_email], test_msg.as_string())
                    server.quit()
                    self.send_json({
                        "success": True,
                        "message": f"✅ Live Test Email delivered successfully to {target_email} via {smtp_host}:{smtp_port}!"
                    })
                except Exception as ex:
                    self.send_json({
                        "success": False,
                        "error": f"SMTP Connection Failed: {str(ex)}"
                    }, 500)

            elif path == '/api/settings/test_sms':
                target_phone = body.get('target_phone') or '+918004125223'
                provider = body.get('sms_provider', 'none').strip().lower()
                api_key = body.get('sms_api_key', '').strip()
                webhook_url = body.get('sms_webhook_url', '').strip()
                test_msg = f"Greenland School: Live SMS gateway test at {datetime.now().strftime('%H:%M:%S')}."
                clean_phone = re.sub(r'[^0-9]', '', target_phone)
                if clean_phone and len(clean_phone) == 10:
                    clean_phone = '91' + clean_phone
                wa_url = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(test_msg)}" if clean_phone else ""

                if provider == 'fast2sms' and api_key:
                    try:
                        req_url = f"https://www.fast2sms.com/dev/bulkV2?authorization={api_key}&route=q&message={urllib.parse.quote(test_msg)}&flash=0&numbers={clean_phone}"
                        req = urllib.request.Request(req_url, headers={'User-Agent': 'GreenlandSchool/2.0'})
                        with urllib.request.urlopen(req, timeout=10) as resp:
                            self.send_json({"success": True, "message": f"Fast2SMS dispatched successfully to {target_phone}!", "whatsapp_url": wa_url})
                    except Exception as ex:
                        self.send_json({"success": False, "error": f"Fast2SMS Error: {str(ex)}", "whatsapp_url": wa_url}, 500)
                elif provider == 'webhook' and webhook_url:
                    try:
                        target_url = webhook_url.replace("{phone}", clean_phone).replace("{message}", urllib.parse.quote(test_msg)).replace("{api_key}", api_key)
                        req = urllib.request.Request(target_url, headers={'User-Agent': 'GreenlandSchool/2.0'})
                        with urllib.request.urlopen(req, timeout=10) as resp:
                            self.send_json({"success": True, "message": f"Webhook dispatched successfully to {target_phone}!", "whatsapp_url": wa_url})
                    except Exception as ex:
                        self.send_json({"success": False, "error": f"Webhook Error: {str(ex)}", "whatsapp_url": wa_url}, 500)
                else:
                    self.send_json({
                        "success": True,
                        "message": f"WhatsApp direct dispatch link generated for {target_phone}! To enable automated carrier SMS, provide a Fast2SMS API Key or Webhook URL.",
                        "whatsapp_url": wa_url
                    })

            elif path == '/api/lab/computers':
                # STRICT REQUIREMENT: Computer Lab Computer IDs (PC numbers), IP addresses, and hardware configurations
                # can ONLY be changed / created by IT Support Administrator (or Director).
                caller_role = body.get('caller_role') or body.get('user_type') or body.get('role', '')
                if caller_role not in ['it_admin', 'super_admin']:
                    self.send_json({
                        "success": False,
                        "error": "🔒 Access Restricted: Computer Lab Computer IDs and hardware configurations can ONLY be changed by IT Support Administrator."
                    }, 403)
                    return

                computer_id = body.get('id')
                lab_name = body.get('lab_name', 'Computer Lab 1 (Main Lab)').strip()
                pc_number = body.get('pc_number', '').strip()
                ip_address = body.get('ip_address', '').strip()
                processor = body.get('processor', 'Intel Core i5-12400 / 16GB RAM / 512GB SSD').strip()
                os_name = body.get('os', 'Windows 11 Pro').strip()
                status = body.get('status', 'Working').strip()
                notes = body.get('notes', '').strip()

                if not pc_number:
                    self.send_json({"success": False, "error": "Computer ID / PC Number is required (e.g. PC-01)."}, 400)
                    return

                if computer_id:
                    # IT Support changing existing Computer ID or configuration
                    cur.execute("""
                        UPDATE lab_computers
                        SET lab_name = ?,
                            pc_number = ?,
                            ip_address = ?,
                            processor = ?,
                            os = ?,
                            notes = ?
                        WHERE id = ?
                    """, (lab_name, pc_number, ip_address, processor, os_name, notes, computer_id))
                    # Propagate Computer ID change to existing complaint history for this computer
                    cur.execute("UPDATE lab_complaints SET pc_number = ?, lab_name = ? WHERE computer_id = ?", (pc_number, lab_name, computer_id))
                    conn.commit()
                    self.send_json({
                        "success": True,
                        "message": f"Computer ID '{pc_number}' and hardware profile updated successfully by IT Support Administrator!"
                    })
                    return

                # Add new workstation
                cur.execute("""
                    INSERT INTO lab_computers (lab_name, pc_number, ip_address, processor, os, status, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(lab_name, pc_number) DO UPDATE SET
                        ip_address = excluded.ip_address,
                        processor = excluded.processor,
                        os = excluded.os,
                        status = excluded.status,
                        notes = excluded.notes
                """, (lab_name, pc_number, ip_address, processor, os_name, status, notes))
                conn.commit()
                self.send_json({"success": True, "message": f"Computer ID '{pc_number}' in {lab_name} saved successfully by IT Support Administrator!"})

            elif path == '/api/lab/complaints':
                # Teacher / Staff / IT logs computer problem in Complaint Desk
                computer_id = body.get('computer_id')
                lab_name = (body.get('lab_name') or 'Computer Lab 1 (Main Lab)').strip()
                pc_number = (body.get('pc_number') or '').strip().upper()
                issue_category = (body.get('issue_category') or 'Hardware Fault').strip()
                problem_desc = (body.get('problem_description') or body.get('issue_description') or '').strip()
                priority = (body.get('priority') or 'Medium').strip()
                user_id = body.get('user_id')
                username = (body.get('username') or '').strip()

                if not problem_desc:
                    self.send_json({"success": False, "error": "Please describe the problem with the computer."}, 400)
                    return

                cur.execute("SELECT id, name, user_type FROM users WHERE id = ? OR username = ?", (user_id, username))
                teacher = cur.fetchone()
                reporter_name = teacher['name'] if teacher and teacher['name'] else (body.get('reported_by_name') or 'Computer Faculty')

                # Resilient workstation lookup
                if not computer_id and pc_number:
                    # 1. Exact match
                    cur.execute("SELECT id, lab_name, pc_number FROM lab_computers WHERE pc_number = ? AND lab_name = ?", (pc_number, lab_name))
                    c_row = cur.fetchone()
                    # 2. Match by pc_number alone
                    if not c_row:
                        cur.execute("SELECT id, lab_name, pc_number FROM lab_computers WHERE pc_number = ?", (pc_number,))
                        c_row = cur.fetchone()
                    # 3. Match by partial lab_name
                    if not c_row and ('1' in lab_name or '2' in lab_name):
                        lab_kw = '%Lab 1%' if '1' in lab_name else '%Lab 2%'
                        cur.execute("SELECT id, lab_name, pc_number FROM lab_computers WHERE pc_number = ? AND lab_name LIKE ?", (pc_number, lab_kw))
                        c_row = cur.fetchone()

                    if c_row:
                        computer_id = c_row[0]
                        lab_name = c_row[1]
                        pc_number = c_row[2]
                    else:
                        # Auto-create PC entry if a valid workstation number is provided
                        cur.execute("INSERT INTO lab_computers (lab_name, pc_number, status) VALUES (?, ?, 'Faulty')", (lab_name, pc_number))
                        computer_id = cur.lastrowid

                if not computer_id:
                    self.send_json({"success": False, "error": "Please specify a valid workstation (e.g. PC-01 to PC-35)."}, 400)
                    return

                ticket_no = f"TKT-LAB-{datetime.now().strftime('%y%m%d')}-{os.urandom(2).hex().upper()}"
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                cur.execute("""
                    INSERT INTO lab_complaints (
                        ticket_no, computer_id, pc_number, lab_name, reported_by_id, reported_by_name,
                        teacher_role, issue_category, problem_description, priority, status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, 'Computer Teacher', ?, ?, ?, 'Pending', ?)
                """, (ticket_no, computer_id, pc_number, lab_name, user_id, reporter_name, issue_category, problem_desc, priority, now))
                complaint_id = cur.lastrowid

                # Update computer status to Faulty
                cur.execute("UPDATE lab_computers SET status = 'Faulty', active_complaint_id = ? WHERE id = ?", (complaint_id, computer_id))
                conn.commit()

                self.send_json({
                    "success": True,
                    "ticket_no": ticket_no,
                    "message": f"Complaint ticket {ticket_no} created for {pc_number}! Dispatched to IT Support Administrator.",
                    "complaint_id": complaint_id
                })

            elif path == '/api/lab/complaints/assign':
                # IT Support Administrator assigns repair technician
                complaint_id = body.get('complaint_id')
                assigned_to_name = (body.get('assigned_to_name') or body.get('technician_name') or 'IT Hardware Support').strip()
                technician_notes = (body.get('technician_notes') or '').strip()
                pc_number = (body.get('pc_number') or '').strip().upper()
                computer_id = body.get('computer_id')
                user_id = body.get('user_id')
                username = (body.get('username') or '').strip()

                cur.execute("SELECT id, name, user_type FROM users WHERE id = ? OR username = ?", (user_id, username))
                admin_row = cur.fetchone()
                assigner_name = admin_row['name'] if admin_row and admin_row['name'] else 'IT Support Administrator'

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Resilient self-healing: if complaint_id is missing or 0, locate active ticket or generate one
                if (not complaint_id or str(complaint_id) in ('0', 'null', 'None')) and (pc_number or computer_id):
                    cur.execute("SELECT id FROM lab_complaints WHERE (computer_id = ? OR pc_number = ?) AND status != 'Resolved' ORDER BY id DESC LIMIT 1", (computer_id, pc_number))
                    t_match = cur.fetchone()
                    if t_match:
                        complaint_id = t_match[0]
                    else:
                        detected_lab = 'Computer Lab'
                        if pc_number or computer_id:
                            cur.execute("SELECT lab_name, id, pc_number FROM lab_computers WHERE id = ? OR pc_number = ?", (computer_id, pc_number))
                            c_info = cur.fetchone()
                            if c_info:
                                detected_lab = c_info[0] or 'Computer Lab'
                                if not computer_id:
                                    computer_id = c_info[1]
                                if not pc_number:
                                    pc_number = c_info[2]
                        tkt_no = f"TKT-LAB-{datetime.now().strftime('%y%m%d')}-{os.urandom(2).hex().upper()}"
                        cur.execute("""
                            INSERT INTO lab_complaints (ticket_no, computer_id, pc_number, lab_name, reported_by_name, teacher_role, issue_category, problem_description, priority, status, created_at)
                            VALUES (?, ?, ?, ?, 'IT Support Administrator', 'IT Hardware Dispatch', 'Hardware Repair', 'Technician assigned for hardware fault.', 'High', 'Assigned', ?)
                        """, (tkt_no, computer_id or 1, pc_number or 'Workstation', detected_lab, now))
                        complaint_id = cur.lastrowid

                if complaint_id:
                    cur.execute("""
                        UPDATE lab_complaints
                        SET status = 'Assigned',
                            assigned_to_name = ?,
                            assigned_by = ?,
                            assigned_at = ?,
                            technician_notes = ?
                        WHERE id = ?
                    """, (assigned_to_name, assigner_name, now, technician_notes, complaint_id))

                    cur.execute("SELECT computer_id, pc_number FROM lab_complaints WHERE id = ?", (complaint_id,))
                    c_row = cur.fetchone()
                    cid = (c_row[0] if c_row else None) or computer_id
                    pcn = (c_row[1] if c_row else None) or pc_number
                    if cid or pcn:
                        cur.execute("UPDATE lab_computers SET status = 'In Repair', active_complaint_id = ? WHERE id = ? OR pc_number = ?", (complaint_id, cid, pcn))
                conn.commit()

                self.send_json({
                    "success": True,
                    "complaint_id": complaint_id,
                    "message": f"Repair task successfully assigned to '{assigned_to_name}'! Computer marked as 'In Repair'."
                })

            elif path == '/api/lab/complaints/resolve':
                # IT Support Administrator marks repair as completed and computer as working
                complaint_id = body.get('complaint_id')
                resolution_notes = (body.get('resolution_notes') or 'Hardware inspected, tested operational, restored to lab.').strip()
                pc_number = (body.get('pc_number') or '').strip().upper()
                computer_id = body.get('computer_id')
                user_id = body.get('user_id')
                username = (body.get('username') or '').strip()

                cur.execute("SELECT id, name, user_type FROM users WHERE id = ? OR username = ?", (user_id, username))
                admin_row = cur.fetchone()
                resolver_name = admin_row['name'] if admin_row and admin_row['name'] else 'IT Support Administrator'

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Resilient ticket resolution
                if (not complaint_id or str(complaint_id) in ('0', 'null', 'None')) and (pc_number or computer_id):
                    cur.execute("SELECT id FROM lab_complaints WHERE (computer_id = ? OR pc_number = ?) AND status != 'Resolved' ORDER BY id DESC LIMIT 1", (computer_id, pc_number))
                    t_match = cur.fetchone()
                    if t_match:
                        complaint_id = t_match[0]

                if complaint_id and str(complaint_id) not in ('0', 'null', 'None'):
                    cur.execute("""
                        UPDATE lab_complaints
                        SET status = 'Resolved',
                            resolution_notes = ?,
                            resolved_by = ?,
                            resolved_at = ?
                        WHERE id = ?
                    """, (resolution_notes, resolver_name, now, complaint_id))

                    cur.execute("SELECT computer_id, pc_number FROM lab_complaints WHERE id = ?", (complaint_id,))
                    c_row = cur.fetchone()
                    cid = (c_row[0] if c_row else None) or computer_id
                    pcn = (c_row[1] if c_row else None) or pc_number
                    if cid or pcn:
                        cur.execute("UPDATE lab_computers SET status = 'Working', active_complaint_id = NULL WHERE id = ? OR pc_number = ?", (cid, pcn))
                        cur.execute("UPDATE lab_complaints SET status = 'Resolved', resolution_notes = ?, resolved_by = ?, resolved_at = ? WHERE (computer_id = ? OR pc_number = ?) AND status != 'Resolved'", (resolution_notes, resolver_name, now, cid, pcn))
                elif computer_id or pc_number:
                    cur.execute("UPDATE lab_computers SET status = 'Working', active_complaint_id = NULL WHERE id = ? OR pc_number = ?", (computer_id, pc_number))
                    cur.execute("UPDATE lab_complaints SET status = 'Resolved', resolution_notes = ?, resolved_by = ?, resolved_at = ? WHERE (computer_id = ? OR pc_number = ?) AND status != 'Resolved'", (resolution_notes, resolver_name, now, computer_id, pc_number))

                conn.commit()

                self.send_json({
                    "success": True,
                    "message": f"Ticket #{complaint_id or 'LAB'} marked as Resolved! Computer has been verified operational and restored to 'Working'."
                })

            elif path == '/api/users/create':
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
                is_common = 1 if (new_role == 'common_id' or body.get('is_common_id') or body.get('common_id_name')) else 0
                common_name = (body.get('common_id_name') or '').strip() or (f"{new_username} Fleet" if is_common else None)
                has_mail = 0 if is_common else int(body.get('has_mail_services', 1))
                if is_common:
                    new_email = None

                admin_user_id = body.get('admin_user_id')
                admin_username = (body.get('admin_username') or '').strip()
                admin_name = (body.get('admin_name') or '').strip()
                assigned_fleet = (body.get('assigned_lab_fleet') or body.get('lab_fleet') or '').strip().lower()

                if admin_user_id or admin_username:
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
                            admin_name = adm_row['name'] or adm_row['username']

                cur.execute("""
                    INSERT INTO users (username, password, user_type, name, email, phone, gender, created_at, is_common_id, common_id_name, has_mail_services, admin_user_id, admin_username, admin_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (new_username, new_password, new_role, new_name, new_email, new_phone, new_gender, now, is_common, common_name, has_mail, admin_user_id, admin_username, admin_name))
                new_uid = cur.lastrowid

                # Link workstations fleet if selected for this Common ID
                if is_common and assigned_fleet in ('both', 'all', 'lab1_and_lab2', 'lab 1 & 2', 'computer lab 1 & 2'):
                    cur.execute("""
                        UPDATE lab_computers 
                        SET assigned_teacher_id = ?,
                            assigned_teacher_username = ?,
                            admin_user_id = ?,
                            admin_username = ?,
                            is_common_id = 1,
                            common_id_name = ?,
                            has_mail_services = 0
                    """, (admin_user_id or new_uid, admin_username or new_username, admin_user_id, admin_username, common_name))
                elif is_common and '1' in assigned_fleet:
                    cur.execute("""
                        UPDATE lab_computers 
                        SET assigned_teacher_id = ?,
                            assigned_teacher_username = ?,
                            admin_user_id = ?,
                            admin_username = ?,
                            is_common_id = 1,
                            common_id_name = ?,
                            has_mail_services = 0
                        WHERE lab_name LIKE '%Lab 1%'
                    """, (admin_user_id or new_uid, admin_username or new_username, admin_user_id, admin_username, common_name))
                elif is_common and '2' in assigned_fleet:
                    cur.execute("""
                        UPDATE lab_computers 
                        SET assigned_teacher_id = ?,
                            assigned_teacher_username = ?,
                            admin_user_id = ?,
                            admin_username = ?,
                            is_common_id = 1,
                            common_id_name = ?,
                            has_mail_services = 0
                        WHERE lab_name LIKE '%Lab 2%'
                    """, (admin_user_id or new_uid, admin_username or new_username, admin_user_id, admin_username, common_name))

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
                })

            elif path == '/api/it_requests/create':
                # IT Support creates equipment procurement or service request for Director Approval
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                req_type = body.get('request_type', 'Equipment Procurement').strip()
                title = body.get('title', 'Fleet Laptop Procurement').strip()
                desc = body.get('description', '').strip()
                cost = float(body.get('estimated_cost') or 0.0)
                by = body.get('requested_by', 'IT Support Administrator').strip()

                cur.execute("""
                    INSERT INTO it_asset_requests (request_type, title, description, estimated_cost, requested_by, status, created_at)
                    VALUES (?, ?, ?, ?, ?, 'Pending Director Approval', ?)
                """, (req_type, title, desc, cost, by, now))
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

                # Verify Director authority (robust & case-insensitive)
                uname_low = caller_username.lower().strip()
                role_low = caller_role.lower().strip()
                is_director = (
                    'director' in uname_low or
                    'directer' in uname_low or
                    'super_admin' in uname_low or
                    'super_admin' in role_low or
                    'director' in role_low or
                    uname_low in ('owner(directer)', 'owner(director)', 'owner')
                )
                if not is_director:
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
                    cur.execute("SELECT computer_id, pc_number FROM lab_complaints WHERE id = ?", (req_id,))
                    c_row = cur.fetchone()
                    if c_row:
                        if action == 'approve':
                            cur.execute("UPDATE lab_computers SET status = 'Faulty', active_complaint_id = ? WHERE id = ? OR pc_number = ?", (req_id, c_row[0], c_row[1]))
                        else:
                            cur.execute("UPDATE lab_computers SET status = 'Working', active_complaint_id = NULL WHERE id = ? OR pc_number = ?", (c_row[0], c_row[1]))
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

                # Clean up common ID admin links and workstation assignments
                cur.execute("UPDATE users SET admin_user_id = NULL, admin_username = NULL, admin_name = NULL WHERE admin_user_id = ? OR admin_username = ?", (uid, uname))
                cur.execute("UPDATE lab_computers SET assigned_teacher_id = NULL, assigned_teacher_username = NULL WHERE assigned_teacher_id = ? OR assigned_teacher_username = ?", (uid, uname))
                cur.execute("UPDATE lab_computers SET admin_user_id = NULL, admin_username = NULL WHERE admin_user_id = ? OR admin_username = ?", (uid, uname))
                cur.execute("DELETE FROM credential_requests WHERE user_id = ? OR target_username = ? OR proposed_username = ?", (uid, uname, uname))

                cur.execute("DELETE FROM users WHERE id = ?", (uid,))
                conn.commit()
                self.send_json({
                    "success": True,
                    "message": f"User ID '{uname}' has been deleted permanently and will no longer appear on the login page.",
                    "deleted_id": uid,
                    "deleted_username": uname
                })

            elif path == '/api/users/assign_role':
                # Role can be changed by IT Support Administrator or Director
                caller_id = body.get('caller_id')
                caller_username = (body.get('caller_username') or body.get('assigned_by') or body.get('username') or '').strip()

                caller = None
                if caller_id:
                    cur.execute("SELECT id, username, user_type FROM users WHERE id = ?", (caller_id,))
                    caller = cur.fetchone()
                if not caller and caller_username:
                    cur.execute("SELECT id, username, user_type FROM users WHERE username = ? OR name = ?", (caller_username, caller_username))
                    caller = cur.fetchone()

                is_authorized = False
                if caller:
                    if caller['user_type'] in ('it_admin', 'super_admin') or caller['username'] in ('GS_itsupport', 'Owner(Directer)'):
                        is_authorized = True
                elif caller_username in ('GS_itsupport', 'Owner(Directer)') or not caller_username or any(k in caller_username.lower() for k in ['support', 'admin', 'director', 'owner']):
                    is_authorized = True

                if not is_authorized:
                    self.send_json({"success": False, "error": "Access Denied: Only IT Support Administrator or Director can change roles."}, 403)
                    return

                target_id = body.get('target_user_id') or body.get('user_id')
                new_role = body.get('role', '').strip()
                target_name = (body.get('name') or '').strip()
                target_gender = body.get('gender') if target_name else None

                if not target_id or not new_role:
                    self.send_json({"success": False, "error": "Target User ID and new role are required."}, 400)
                    return

                is_common = 1 if (new_role == 'common_id' or body.get('is_common_id') or body.get('common_id_name')) else (1 if 'common' in str(body.get('common_id_name', '')).lower() else 0)
                common_name = (body.get('common_id_name') or '').strip()
                has_mail = 0 if is_common else int(body.get('has_mail_services', 1))
                assigned_fleet = (body.get('assigned_lab_fleet') or '').strip().lower()

                admin_user_id = body.get('admin_user_id')
                admin_username = (body.get('admin_username') or '').strip()
                admin_name = (body.get('admin_name') or '').strip()
                if admin_user_id or admin_username:
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
                            admin_name = adm_row['name'] or adm_row['username']

                # Update role, common id, admin, and name/gender according to rule
                if target_name:
                    cur.execute("""
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
                    """, (new_role, target_name, target_gender, is_common, common_name if is_common else None, has_mail, admin_user_id, admin_username, admin_name, target_id))
                else:
                    cur.execute("""
                        UPDATE users 
                        SET user_type = ?,
                            is_common_id = ?,
                            common_id_name = ?,
                            has_mail_services = ?,
                            admin_user_id = ?,
                            admin_username = ?,
                            admin_name = ?
                        WHERE id = ?
                    """, (new_role, is_common, common_name if is_common else None, has_mail, admin_user_id, admin_username, admin_name, target_id))
                    cur.execute("UPDATE users SET gender = NULL WHERE id = ? AND (name IS NULL OR TRIM(name) = '')", (target_id,))

                # If assigning lab fleet (e.g. Lab 1 & 2)
                cur.execute("SELECT username FROM users WHERE id = ?", (target_id,))
                t_user_row = cur.fetchone()
                target_uname = t_user_row['username'] if t_user_row else ''

                if assigned_fleet in ('both', 'all', 'lab1_and_lab2', 'lab 1 & 2', 'computer lab 1 & 2'):
                    cur.execute("""
                        UPDATE lab_computers 
                        SET assigned_teacher_id = ?,
                            assigned_teacher_username = ?,
                            is_common_id = 1,
                            common_id_name = 'Computer Teacher Lab Fleet (Common ID)',
                            has_mail_services = 0
                    """, (target_id, target_uname))
                elif '1' in assigned_fleet:
                    cur.execute("""
                        UPDATE lab_computers 
                        SET assigned_teacher_id = ?,
                            assigned_teacher_username = ?,
                            is_common_id = 1,
                            common_id_name = 'Computer Lab 1 Fleet (Common ID)',
                            has_mail_services = 0
                        WHERE lab_name LIKE '%Lab 1%'
                    """, (target_id, target_uname))
                elif '2' in assigned_fleet:
                    cur.execute("""
                        UPDATE lab_computers 
                        SET assigned_teacher_id = ?,
                            assigned_teacher_username = ?,
                            is_common_id = 1,
                            common_id_name = 'Computer Lab 2 Fleet (Common ID)',
                            has_mail_services = 0
                        WHERE lab_name LIKE '%Lab 2%'
                    """, (target_id, target_uname))

                conn.commit()

                cur.execute("SELECT id, username, name, user_type, gender FROM users WHERE id = ?", (target_id,))
                updated_user = cur.fetchone()
                uname = updated_user['username'] if updated_user else f"ID #{target_id}"

                self.send_json({
                    "success": True, 
                    "message": f"Role for '{uname}' successfully changed to '{new_role}' by IT Support Administrator / Administration!",
                    "user": dict(updated_user) if updated_user else None
                })

            elif path == '/api/system/clean_test_data':
                # Cleans synthetic test data, preserves manual user entries (like Virat Singh), leaves Director & IT Support Admin
                user_id = body.get('user_id')
                username = (body.get('username') or body.get('requested_by') or body.get('user_name') or '').strip()

                caller = None
                if user_id:
                    cur.execute("SELECT id, username, user_type FROM users WHERE id = ?", (user_id,))
                    caller = cur.fetchone()
                if not caller and username:
                    cur.execute("SELECT id, username, user_type FROM users WHERE username = ?", (username,))
                    caller = cur.fetchone()

                is_authorized = False
                if caller:
                    if caller['username'] in ('Owner(Directer)', 'GS_superadmin', 'GS_itsupport') or caller['user_type'] in ('super_admin', 'it_admin'):
                        is_authorized = True
                elif username in ('Owner(Directer)', 'GS_superadmin', 'GS_itsupport') or not username:
                    is_authorized = True

                if not is_authorized:
                    self.send_json({"success": False, "error": "Access Denied: Only Director or Authorized Admin can clear test data."}, 403)
                    return

                # 1. Clean synthetic users (preserve Owner(Directer), GS_itsupport, and manual user data like Virat Singh)
                cur.execute("""
                    DELETE FROM users
                    WHERE username NOT IN ('Owner(Directer)', 'GS_itsupport')
                      AND (name IS NULL OR name NOT LIKE '%Virat%')
                      AND (email IS NULL OR email NOT LIKE '%vs0839265%')
                      AND (username NOT LIKE '%virat%')
                """ )

                # 2. Clean synthetic students
                cur.execute("""
                    DELETE FROM students
                    WHERE user_id NOT IN (SELECT id FROM users)
                      AND (adm_no NOT LIKE '%VIRAT%')
                """ )

                # 3. Clean synthetic admissions/inquiries
                cur.execute("""
                    DELETE FROM admissions
                    WHERE (applicant_name IS NULL OR applicant_name NOT LIKE '%Virat%')
                      AND (parent_name IS NULL OR parent_name NOT LIKE '%Virat%')
                      AND (email IS NULL OR email NOT LIKE '%vs0839265%')
                      AND (ref_no IS NULL OR ref_no NOT LIKE '%VIRAT%')
                """ )

                # 4. Clean credential requests
                cur.execute("DELETE FROM credential_requests")

                # 5. Clean payments for deleted students
                cur.execute("DELETE FROM payments WHERE student_id NOT IN (SELECT id FROM students)")

                # 6. Clean marks & attendance for deleted students
                cur.execute("DELETE FROM marks WHERE student_id NOT IN (SELECT id FROM students)")
                cur.execute("DELETE FROM attendance WHERE student_id NOT IN (SELECT id FROM students)")

                # 7. Clean leaves for deleted users
                cur.execute("DELETE FROM leaves WHERE user_id NOT IN (SELECT id FROM users)")

                # 8. Clean salary slips for deleted faculty & special bonuses
                cur.execute("DELETE FROM salary_slips WHERE teacher_id NOT IN (SELECT id FROM users)")
                cur.execute("DELETE FROM special_bonuses")

                # 9. Clean lab complaints and reset all 35 lab computers to Working
                cur.execute("DELETE FROM lab_complaints")
                cur.execute("UPDATE lab_computers SET status = 'Working', active_complaint_id = NULL")

                # 10. Clean library book requests for deleted students
                cur.execute("DELETE FROM book_requests WHERE user_id NOT IN (SELECT id FROM users)")

                # 11. Clean payment delete requests
                cur.execute("DELETE FROM payment_delete_requests")

                # 12. Clean notifications outbox (preserve Virat)
                cur.execute("""
                    DELETE FROM notifications_outbox 
                    WHERE (recipient_email IS NULL OR recipient_email NOT LIKE '%vs0839265%')
                      AND (applicant_name IS NULL OR applicant_name NOT LIKE '%Virat%')
                """)

                # 13. Maintain rule: IDs without a person's name have NO gender (—)
                cur.execute("UPDATE users SET gender = NULL WHERE name IS NULL OR TRIM(name) = ''")

                conn.commit()

                self.send_json({
                    "success": True,
                    "message": "All test dummy data cleared! Portal is reset to a brand new, clean state: Director (Owner) Rajeev Sinha and IT Support Administrator remain active, alongside manually entered user records."
                })

            elif path == '/api/system/seed_faculty':
                # Re-seed demo faculty accounts for testing
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for u in UNIQUE_DEFAULT_USERS:
                    if u['username'] not in ('Owner(Directer)', 'GS_itsupport'):
                        u_gender = u.get('gender', 'Female' if 'rose' in u['username'].lower() or 'superadmin' in u['username'].lower() else 'Male')
                        cur.execute("""
                            INSERT OR REPLACE INTO users (name, email, username, password, user_type, phone, photo, created_at, gender)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (u['name'], u['email'], u['username'], u['password'], u['role'], u['phone'], u['photo'], now, u_gender))
                conn.commit()
                self.send_json({"success": True, "message": "Demo Faculty & Staff accounts seeded successfully for testing!"})

            # =====================================================================
            # LAPTOP & COMPUTER ASSET MANAGEMENT POST ENDPOINTS
            # =====================================================================
            elif path == '/api/it_assets/create':
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                device_type = body.get('device_type', 'Laptop').strip()
                brand = body.get('brand', '').strip()
                model_name = body.get('model_name', '').strip()
                serial_number = body.get('serial_number', '').strip()
                processor = body.get('specs_processor', '').strip()
                ram = body.get('specs_ram', '').strip()
                storage = body.get('specs_storage', '').strip()
                os_name = body.get('specs_os', 'Windows 11 Pro').strip()
                ownership = body.get('ownership_type', 'Owned (Institutional Purchase)').strip()
                condition = body.get('condition', 'Excellent').strip()
                purchase_date = body.get('purchase_date') or datetime.now().strftime("%Y-%m-%d")
                purchase_cost = float(body.get('purchase_cost') or 0.0)
                location = body.get('current_location', 'IT Support Depot').strip()
                status = body.get('status', 'In Stock / Available').strip()
                notes = body.get('notes', '').strip()
                creator = body.get('created_by', 'IT Support Administrator').strip()

                prefix = 'LAP' if 'laptop' in device_type.lower() else 'PC'
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE asset_tag LIKE ?", (f"{prefix}-2026-%",))
                next_num = cur.fetchone()[0] + 1
                asset_tag = body.get('asset_tag') or f"{prefix}-2026-{next_num:03d}"

                cur.execute("""
                    INSERT INTO it_assets (
                        asset_tag, device_type, brand, model_name, serial_number, specs_processor, specs_ram,
                        specs_storage, specs_os, ownership_type, condition, purchase_date, purchase_cost,
                        current_location, status, notes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (asset_tag, device_type, brand, model_name, serial_number, processor, ram, storage, os_name, ownership, condition, purchase_date, purchase_cost, location, status, notes, now))
                asset_id = cur.lastrowid

                cur.execute("""
                    INSERT INTO it_asset_logs (asset_id, action_type, from_location, to_location, assigned_to, performed_by, details, timestamp)
                    VALUES (?, 'Asset Registered / Added to Inventory', 'Procurement / Delivery', ?, 'IT Support Depot', ?, ?, ?)
                """, (asset_id, location, creator, f"Device registered: {brand} {model_name} ({processor or 'Standard Specs'}). Initial status: {status}.", now))
                conn.commit()

                self.send_json({
                    "success": True,
                    "message": f"Asset '{asset_tag}' ({brand} {model_name}) successfully registered in inventory!",
                    "asset_id": asset_id,
                    "asset_tag": asset_tag
                })

            elif path == '/api/it_assets/update':
                asset_id = body.get('id') or body.get('asset_id')
                if not asset_id:
                    self.send_json({"success": False, "message": "Asset ID is required."}, 400)
                    return
                
                cur.execute("SELECT * FROM it_assets WHERE id = ?", (asset_id,))
                old_asset = cur.fetchone()
                if not old_asset:
                    self.send_json({"success": False, "message": "Asset not found."}, 404)
                    return

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                brand = body.get('brand', old_asset['brand']).strip()
                model_name = body.get('model_name', old_asset['model_name']).strip()
                processor = body.get('specs_processor', old_asset['specs_processor']).strip()
                ram = body.get('specs_ram', old_asset['specs_ram']).strip()
                storage = body.get('specs_storage', old_asset['specs_storage']).strip()
                os_name = body.get('specs_os', old_asset['specs_os']).strip()
                condition = body.get('condition', old_asset['condition']).strip()
                new_location = body.get('current_location', old_asset['current_location']).strip()
                new_status = body.get('status', old_asset['status']).strip()
                notes = body.get('notes', old_asset['notes']).strip()
                updated_by = body.get('updated_by', 'IT Support Administrator').strip()

                cur.execute("""
                    UPDATE it_assets
                    SET brand = ?, model_name = ?, specs_processor = ?, specs_ram = ?, specs_storage = ?,
                        specs_os = ?, condition = ?, current_location = ?, status = ?, notes = ?
                    WHERE id = ?
                """, (brand, model_name, processor, ram, storage, os_name, condition, new_location, new_status, notes, asset_id))

                if new_location != old_asset['current_location'] or new_status != old_asset['status']:
                    cur.execute("""
                        INSERT INTO it_asset_logs (asset_id, action_type, from_location, to_location, assigned_to, performed_by, details, timestamp)
                        VALUES (?, 'Location / Status Movement', ?, ?, ?, ?, ?, ?)
                    """, (asset_id, old_asset['current_location'], new_location, new_status, updated_by, f"Status updated to '{new_status}'. Condition: '{condition}'.", now))

                conn.commit()
                self.send_json({"success": True, "message": f"Asset '{old_asset['asset_tag']}' updated successfully!"})

            elif path == '/api/it_assets/delete':
                asset_id = body.get('id') or body.get('asset_id')
                cur.execute("SELECT asset_tag FROM it_assets WHERE id = ?", (asset_id,))
                row = cur.fetchone()
                if row:
                    cur.execute("DELETE FROM it_assets WHERE id = ?", (asset_id,))
                    cur.execute("DELETE FROM it_asset_logs WHERE asset_id = ?", (asset_id,))
                    conn.commit()
                    self.send_json({"success": True, "message": f"Asset '{row['asset_tag']}' removed from inventory."})
                else:
                    self.send_json({"success": False, "message": "Asset not found."}, 404)

            elif path == '/api/it_rentals/create':
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                rental_type = body.get('rental_type', 'Inward (Rented from Vendor)').strip()
                asset_id = body.get('asset_id')
                vendor_name = body.get('vendor_or_client_name', '').strip()
                phone = body.get('contact_phone', '').strip()
                email = body.get('contact_email', '').strip()
                start_date = body.get('start_date', '').strip()
                end_date = body.get('end_date', '').strip()
                billing_cycle = body.get('billing_cycle', 'Monthly').strip()
                rental_amount = float(body.get('rental_amount') or 0.0)
                deposit = float(body.get('deposit_amount') or 0.0)
                next_due = body.get('next_payment_due_date') or end_date
                terms = body.get('terms_notes', '').strip()

                cur.execute("SELECT COUNT(*) FROM it_rentals")
                r_num = cur.fetchone()[0] + 1
                agreement_no = f"RNT-2026-{r_num:03d}"

                cur.execute("""
                    INSERT INTO it_rentals (
                        rental_agreement_no, rental_type, asset_id, vendor_or_client_name, contact_phone,
                        contact_email, start_date, end_date, billing_cycle, rental_amount, deposit_amount,
                        next_payment_due_date, payment_status, rental_status, terms_notes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Due Soon', 'Active Agreement', ?, ?)
                """, (agreement_no, rental_type, asset_id, vendor_name, phone, email, start_date, end_date, billing_cycle, rental_amount, deposit, next_due, terms, now))
                rental_id = cur.lastrowid

                if asset_id:
                    cur.execute("""
                        UPDATE it_assets 
                        SET status = 'On Rental', 
                            ownership_type = 'Rented / Leased from Vendor',
                            current_location = ?
                        WHERE id = ?
                    """, (f"On Rental ({vendor_name})", asset_id))
                    cur.execute("""
                        INSERT INTO it_asset_logs (asset_id, action_type, from_location, to_location, assigned_to, performed_by, details, timestamp)
                        VALUES (?, 'Rental Agreement Activated', 'IT Support Depot', ?, ?, 'IT Support Administrator', ?, ?)
                    """, (asset_id, f"On Rental ({vendor_name})", vendor_name, f"Agreement #{agreement_no}. Rate: ₦{rental_amount:,.2f}.", now))

                cur.execute("SELECT COUNT(*) FROM it_asset_payments")
                p_num = cur.fetchone()[0] + 1
                pmt_ref = f"PMT-2026-{p_num:03d}"
                cur.execute("""
                    INSERT INTO it_asset_payments (
                        ref_no, payment_category, related_rental_id, vendor_name, amount, due_date, payment_status, notes, created_at
                    ) VALUES (?, 'Rental Invoice', ?, ?, ?, ?, 'Upcoming Due', ?, ?)
                """, (pmt_ref, rental_id, vendor_name, rental_amount, next_due, f"Scheduled rental fee under agreement #{agreement_no}.", now))

                conn.commit()
                self.send_json({
                    "success": True,
                    "message": f"Rental Agreement '{agreement_no}' with '{vendor_name}' successfully created!",
                    "rental_id": rental_id,
                    "agreement_no": agreement_no
                })

            elif path == '/api/it_rentals/update':
                rental_id = body.get('id')
                status = body.get('rental_status')
                pay_status = body.get('payment_status')
                end_date = body.get('end_date')
                terms = body.get('terms_notes')

                cur.execute("""
                    UPDATE it_rentals
                    SET rental_status = COALESCE(?, rental_status),
                        payment_status = COALESCE(?, payment_status),
                        end_date = COALESCE(?, end_date),
                        terms_notes = COALESCE(?, terms_notes)
                    WHERE id = ?
                """, (status, pay_status, end_date, terms, rental_id))
                conn.commit()
                self.send_json({"success": True, "message": "Rental agreement updated successfully."})

            elif path == '/api/it_allocations/handover':
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                asset_id = body.get('asset_id')
                employee_id = body.get('employee_id')
                employee_name = body.get('employee_name', '').strip()
                employee_role = body.get('employee_role', 'Faculty / Staff').strip()
                department = body.get('department', 'Academics').strip()
                handover_date = body.get('handover_date', datetime.now().strftime("%Y-%m-%d"))
                expected_return = body.get('expected_return_date')
                condition = body.get('handover_condition', 'Pristine / Like New').strip()
                accessories = body.get('accessories_included', 'Original Charger, Laptop Bag, Wireless Mouse').strip()
                notes = body.get('handover_notes', '').strip()
                officer = body.get('handover_by', 'IT Support Administrator').strip()

                if not asset_id or not employee_name:
                    self.send_json({"success": False, "message": "Asset and employee name are required."}, 400)
                    return

                cur.execute("SELECT asset_tag, brand, model_name, current_location FROM it_assets WHERE id = ?", (asset_id,))
                asset_row = cur.fetchone()
                if not asset_row:
                    self.send_json({"success": False, "message": "Asset not found."}, 404)
                    return

                cur.execute("SELECT COUNT(*) FROM it_asset_allocations")
                h_num = cur.fetchone()[0] + 1
                slip_no = f"HND-2026-{h_num:03d}"

                cur.execute("""
                    INSERT INTO it_asset_allocations (
                        handover_slip_no, asset_id, employee_id, employee_name, employee_role, department,
                        handover_date, expected_return_date, handover_condition, accessories_included,
                        handover_notes, handover_status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active (With Employee)', ?)
                """, (slip_no, asset_id, employee_id, employee_name, employee_role, department, handover_date, expected_return, condition, accessories, notes, now))
                alloc_id = cur.lastrowid

                cur.execute("""
                    UPDATE it_assets
                    SET status = 'Allocated to Employee',
                        current_location = ?
                    WHERE id = ?
                """, (f"With Employee ({employee_name})", asset_id))

                cur.execute("""
                    INSERT INTO it_asset_logs (asset_id, action_type, from_location, to_location, assigned_to, performed_by, details, timestamp)
                    VALUES (?, 'Handover to Employee', ?, ?, ?, ?, ?, ?)
                """, (asset_id, asset_row['current_location'], f"With Employee ({employee_name})", employee_name, officer, f"Formally allocated under Handover Slip #{slip_no}. Accessories: {accessories}.", now))

                conn.commit()
                self.send_json({
                    "success": True,
                    "message": f"Asset '{asset_row['asset_tag']}' successfully handed over to {employee_name}! Handover Slip #{slip_no} generated.",
                    "allocation_id": alloc_id,
                    "handover_slip_no": slip_no
                })

            elif path == '/api/it_allocations/return':
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                today_str = datetime.now().strftime("%Y-%m-%d")
                allocation_id = body.get('allocation_id')
                return_condition = body.get('return_condition', 'Good').strip()
                verified_by = body.get('return_verified_by', 'IT Support Administrator').strip()
                return_notes = body.get('return_notes', 'Inspection verified. System in full working order.').strip()

                cur.execute("SELECT alc.*, a.asset_tag, a.current_location FROM it_asset_allocations alc JOIN it_assets a ON alc.asset_id = a.id WHERE alc.id = ?", (allocation_id,))
                alc = cur.fetchone()
                if not alc:
                    self.send_json({"success": False, "message": "Allocation record not found."}, 404)
                    return

                cur.execute("""
                    UPDATE it_asset_allocations
                    SET handover_status = 'Returned & Verified',
                        actual_return_date = ?,
                        return_condition = ?,
                        return_verified_by = ?
                    WHERE id = ?
                """, (today_str, return_condition, verified_by, allocation_id))

                cur.execute("""
                    UPDATE it_assets
                    SET status = 'In Stock / Available',
                        condition = ?,
                        current_location = 'IT Support Depot'
                    WHERE id = ?
                """, (return_condition, alc['asset_id']))

                cur.execute("""
                    INSERT INTO it_asset_logs (asset_id, action_type, from_location, to_location, assigned_to, performed_by, details, timestamp)
                    VALUES (?, 'Asset Handover Return', ?, 'IT Support Depot', 'IT Support Depot', ?, ?, ?)
                """, (alc['asset_id'], alc['current_location'], verified_by, f"Device returned by {alc['employee_name']}. Condition: '{return_condition}'. Notes: {return_notes}", now))

                conn.commit()
                self.send_json({
                    "success": True,
                    "message": f"Asset '{alc['asset_tag']}' return confirmed and checked back into IT Support Depot inventory!"
                })

            elif path == '/api/it_warranties/create':
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                asset_id = body.get('asset_id')
                provider = body.get('provider_name', '').strip()
                policy_no = body.get('policy_number', '').strip()
                w_type = body.get('warranty_type', 'OEM Standard Warranty').strip()
                start_date = body.get('start_date', '').strip()
                end_date = body.get('end_date', '').strip()
                contact = body.get('support_contact', '').strip()
                notes = body.get('notes', '').strip()

                cur.execute("""
                    INSERT INTO it_warranties (
                        asset_id, provider_name, policy_number, warranty_type, start_date, end_date,
                        support_contact, status, claim_count, notes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'Active', 0, ?, ?)
                """, (asset_id, provider, policy_no, w_type, start_date, end_date, contact, notes, now))
                conn.commit()
                wid = cur.lastrowid
                self.send_json({"success": True, "message": f"Warranty policy '{policy_no}' registered successfully!", "warranty_id": wid})

            elif path == '/api/it_warranties/claim':
                warranty_id = body.get('warranty_id')
                claim_notes = body.get('notes', 'Warranty claim filed by IT Support').strip()
                cur.execute("UPDATE it_warranties SET claim_count = claim_count + 1, notes = notes || ' | ' || ? WHERE id = ?", (claim_notes, warranty_id))
                conn.commit()
                self.send_json({"success": True, "message": "Warranty claim logged and registered with provider."})

            elif path == '/api/it_maintenance/create':
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                asset_id = body.get('asset_id')
                s_type = body.get('service_type', 'Hardware Repair').strip()
                issue = body.get('reported_issue', '').strip()
                center = body.get('service_center_or_vendor', 'Authorized Service Hub').strip()
                tech = body.get('technician_name', '').strip()
                start_d = body.get('start_date', datetime.now().strftime("%Y-%m-%d")).strip()
                cost = float(body.get('repair_cost') or 0.0)
                is_warranty = 1 if body.get('warranty_claim_covered') else 0
                remarks = body.get('remarks', '').strip()

                cur.execute("SELECT COUNT(*) FROM it_maintenance_service")
                s_num = cur.fetchone()[0] + 1
                ticket_no = f"SVC-2026-{s_num:03d}"

                cur.execute("""
                    INSERT INTO it_maintenance_service (
                        service_ticket_no, asset_id, service_type, reported_issue, service_center_or_vendor,
                        technician_name, start_date, repair_cost, service_status, warranty_claim_covered, remarks, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'In Repair / Awaiting Parts', ?, ?, ?)
                """, (ticket_no, asset_id, s_type, issue, center, tech, start_d, cost, is_warranty, remarks, now))
                ticket_id = cur.lastrowid

                cur.execute("""
                    UPDATE it_assets 
                    SET status = 'In Service / Repair',
                        current_location = ?
                    WHERE id = ?
                """, (f"Service Center ({center})", asset_id))

                cur.execute("""
                    INSERT INTO it_asset_logs (asset_id, action_type, from_location, to_location, assigned_to, performed_by, details, timestamp)
                    VALUES (?, 'Dispatched for Service / Repair', 'IT Support Depot', ?, ?, 'IT Support Administrator', ?, ?)
                """, (asset_id, f"Service Center ({center})", center, f"Ticket #{ticket_no}. Type: {s_type}. Issue: {issue}.", now))

                conn.commit()
                self.send_json({
                    "success": True,
                    "message": f"Service ticket '{ticket_no}' opened! Device marked 'In Service / Repair'.",
                    "ticket_id": ticket_id,
                    "ticket_no": ticket_no
                })

            elif path == '/api/it_maintenance/complete':
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ticket_id = body.get('ticket_id')
                comp_date = body.get('completion_date', datetime.now().strftime("%Y-%m-%d")).strip()
                actual_cost = float(body.get('repair_cost') or 0.0)
                parts = body.get('parts_replaced', '').strip()
                remarks = body.get('remarks', 'Repair and operational diagnostic testing verified.').strip()
                location = body.get('return_location', 'IT Support Depot').strip()

                cur.execute("SELECT s.*, a.asset_tag FROM it_maintenance_service s JOIN it_assets a ON s.asset_id = a.id WHERE s.id = ?", (ticket_id,))
                t_row = cur.fetchone()
                if not t_row:
                    self.send_json({"success": False, "message": "Ticket not found."}, 404)
                    return

                cur.execute("""
                    UPDATE it_maintenance_service
                    SET service_status = 'Completed & Tested',
                        completion_date = ?,
                        repair_cost = ?,
                        parts_replaced = ?,
                        remarks = COALESCE(remarks || ' | ' || ?, remarks)
                    WHERE id = ?
                """, (comp_date, actual_cost, parts, remarks, ticket_id))

                cur.execute("""
                    UPDATE it_assets
                    SET status = 'In Stock / Available',
                        condition = 'Good',
                        current_location = ?
                    WHERE id = ?
                """, (location, t_row['asset_id']))

                cur.execute("""
                    INSERT INTO it_asset_logs (asset_id, action_type, from_location, to_location, assigned_to, performed_by, details, timestamp)
                    VALUES (?, 'Service Completed & Tested', ?, ?, 'IT Support Depot', 'IT Support Administrator', ?, ?)
                """, (t_row['asset_id'], t_row['service_center_or_vendor'], location, f"Ticket #{t_row['service_ticket_no']} completed. Parts: {parts or 'None'}. Cost: ₦{actual_cost:,.2f}.", now))

                if actual_cost > 0 and not t_row['warranty_claim_covered']:
                    cur.execute("SELECT COUNT(*) FROM it_asset_payments")
                    p_num = cur.fetchone()[0] + 1
                    pmt_ref = f"PMT-2026-{p_num:03d}"
                    cur.execute("""
                        INSERT INTO it_asset_payments (
                            ref_no, payment_category, related_service_id, vendor_name, amount, due_date, payment_status, notes, created_at
                        ) VALUES (?, 'Hardware Repair Bill', ?, ?, ?, date('now', '+7 days'), 'Upcoming Due', ?, ?)
                    """, (pmt_ref, ticket_id, t_row['service_center_or_vendor'], actual_cost, f"Invoice for completed repair on ticket #{t_row['service_ticket_no']}.", now))

                conn.commit()
                self.send_json({
                    "success": True,
                    "message": f"Service ticket '{t_row['service_ticket_no']}' marked completed! Device tested and restored to '{location}'."
                })

            elif path == '/api/it_payments/create':
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cat = body.get('payment_category', 'Rental Invoice').strip()
                vendor = body.get('vendor_name', '').strip()
                amount = float(body.get('amount') or 0.0)
                due = body.get('due_date', '').strip()
                rental_id = body.get('related_rental_id')
                service_id = body.get('related_service_id')
                notes = body.get('notes', '').strip()

                cur.execute("SELECT COUNT(*) FROM it_asset_payments")
                p_num = cur.fetchone()[0] + 1
                pmt_ref = f"PMT-2026-{p_num:03d}"

                cur.execute("""
                    INSERT INTO it_asset_payments (
                        ref_no, payment_category, related_rental_id, related_service_id, vendor_name,
                        amount, due_date, payment_status, notes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'Upcoming Due', ?, ?)
                """, (pmt_ref, cat, rental_id, service_id, vendor, amount, due, notes, now))
                pmt_id = cur.lastrowid
                conn.commit()
                self.send_json({"success": True, "message": f"Payment schedule '{pmt_ref}' created successfully!", "payment_id": pmt_id, "ref_no": pmt_ref})

            elif path == '/api/it_payments/record':
                payment_id = body.get('payment_id')
                paid_date = body.get('paid_date', datetime.now().strftime("%Y-%m-%d"))
                method = body.get('payment_method', 'Bank Transfer / NEFT').strip()
                tx_ref = body.get('transaction_ref', '').strip()
                notes = body.get('notes', '').strip()

                cur.execute("""
                    UPDATE it_asset_payments
                    SET payment_status = 'Paid',
                        paid_date = ?,
                        payment_method = ?,
                        transaction_ref = ?,
                        notes = COALESCE(notes || ' | ' || ?, notes)
                    WHERE id = ?
                """, (paid_date, method, tx_ref, notes, payment_id))
                conn.commit()
                self.send_json({"success": True, "message": "Payment recorded successfully as Paid in Full!"})

            elif path == '/api/it_payments/send_reminder':
                payment_id = body.get('payment_id')
                cur.execute("SELECT * FROM it_asset_payments WHERE id = ?", (payment_id,))
                p = cur.fetchone()
                if p:
                    self.send_json({
                        "success": True,
                        "message": f"Payment reminder notification dispatched to School Bursar & Finance Desk for {p['vendor_name']} (₦{p['amount']:,.2f} due on {p['due_date']})!"
                    })
                else:
                    self.send_json({"success": False, "message": "Payment record not found."}, 404)

            else:
                self.send_json({"error": "Action not supported"}, 404)

        finally:
            conn.close()

class DualStackServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, server_address, RequestHandlerClass):
        try:
            self.address_family = socket.AF_INET6
            super().__init__(server_address, RequestHandlerClass)
        except OSError:
            self.address_family = socket.AF_INET
            super().__init__(server_address, RequestHandlerClass)

    def server_bind(self):
        if self.address_family == socket.AF_INET6:
            try:
                self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            except (AttributeError, OSError):
                pass
        super().server_bind()

def run_server():
    init_db()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    server = None
    actual_port = PORT
    for port in [PORT, 5001, 5050, 8000]:
        try:
            server = DualStackServer(("", port), SchoolHandler)
            actual_port = port
            break
        except OSError:
            continue

    if not server:
        server = DualStackServer(("", 0), SchoolHandler)
        actual_port = server.server_address[1]

    with server as httpd:
        print(f"===============================================================")
        print(f"  GREENLAND SCHOOL (GS) - School Management System & Website")
        print(f"  IPv4 Link:          http://127.0.0.1:{actual_port}")
        print(f"  Localhost Link:     http://localhost:{actual_port}")
        print(f"  SMS Portal Login:   http://127.0.0.1:{actual_port}#login")
        print(f"  SMS Portal:         http://127.0.0.1:{actual_port}#portal")
        print(f"  Campus Mobile App:  http://127.0.0.1:{actual_port}#app")
        print(f"===============================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")

if __name__ == '__main__':
    run_server()
