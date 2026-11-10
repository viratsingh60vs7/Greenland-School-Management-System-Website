import sqlite3
from datetime import datetime

conn = sqlite3.connect('school_website/school.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
today = datetime.now().strftime("%Y-%m-%d")

# 1. Ensure Teacher Chike exists
cur.execute("SELECT id FROM users WHERE username = 'GS_teacher'")
t = cur.fetchone()
if not t:
    cur.execute("""
        INSERT INTO users (name, email, username, password, user_type, phone, photo, created_at, gender)
        VALUES ('Teacher Chike', 'teacher.chike@greenlandschool.net', 'GS_teacher', 'Greenland@2026', 'teacher', '9876543210', 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150', ?, 'Male')
    """, (now,))
    teacher_id = cur.lastrowid
else:
    teacher_id = t['id']
    cur.execute("UPDATE users SET phone = '9876543210' WHERE id = ?", (teacher_id,))

# 2. Ensure Parent Marcus Kaba exists
cur.execute("SELECT id FROM users WHERE username = 'GS_parent_Alex_and_Clara'")
p = cur.fetchone()
if not p:
    cur.execute("""
        INSERT INTO users (name, email, username, password, user_type, phone, photo, created_at, gender)
        VALUES ('Marcus Kaba (Parent)', 'parent.kaba@greenlandschool.net', 'GS_parent_Alex_and_Clara', 'Greenland@2026', 'parent', '9812345678', 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150', ?, 'Male')
    """, (now,))
    parent_id = cur.lastrowid
else:
    parent_id = p['id']
    cur.execute("UPDATE users SET phone = '9812345678' WHERE id = ?", (parent_id,))

# 3. Ensure Student Virat Singh exists in students table
virat_student_id = None
cur.execute("SELECT id FROM users WHERE name LIKE '%Virat%'")
v = cur.fetchone()
if v:
    virat_uid = v['id']
    cur.execute("SELECT id FROM students WHERE user_id = ?", (virat_uid,))
    s = cur.fetchone()
    if not s:
        cur.execute("""
            INSERT INTO students (user_id, class_id, section_id, adm_no, blood_group, parent_id, dob, gender, address, admission_status, approved_by, approved_at)
            VALUES (?, 1, 1, 'GS-2026-001', 'O+', ?, '2008-05-15', 'Male', 'Greenland Campus Residences, Suite 4B', 'Approved for New Admission', 'Director Rajeev Sinha', ?)
        """, (virat_uid, parent_id, now))
        virat_student_id = cur.lastrowid
    else:
        virat_student_id = s['id']
        cur.execute("UPDATE students SET parent_id = ? WHERE user_id = ?", (parent_id, virat_uid))

# 4. Ensure a second student Clara Kaba linked to the same parent for multi-child testing
cur.execute("SELECT id FROM users WHERE username = 'GS_student_Clara'")
c = cur.fetchone()
if not c:
    cur.execute("""
        INSERT INTO users (name, email, username, password, user_type, phone, photo, created_at, gender)
        VALUES ('Clara Kaba', 'clara.kaba@greenlandschool.net', 'GS_student_Clara', 'Greenland@2026', 'student', '9812345679', 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150', ?, 'Female')
    """, (now,))
    clara_uid = cur.lastrowid
    cur.execute("""
        INSERT INTO students (user_id, class_id, section_id, adm_no, blood_group, parent_id, dob, gender, address, admission_status, approved_by, approved_at)
        VALUES (?, 2, 4, 'GS-2026-002', 'A+', ?, '2010-09-22', 'Female', 'Greenland Campus Residences, Suite 4B', 'Approved for New Admission', 'Director Rajeev Sinha', ?)
    """, (clara_uid, parent_id, now))
    clara_student_id = cur.lastrowid
else:
    clara_uid = c['id']
    cur.execute("SELECT id FROM students WHERE user_id = ?", (clara_uid,))
    cs = cur.fetchone()
    clara_student_id = cs['id'] if cs else None

# 5. Ensure issued book for Virat Singh in e-library
if v:
    cur.execute("SELECT id FROM book_requests WHERE user_id = ?", (v['id'],))
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO book_requests (book_id, user_id, status, issue_date, due_date, issue_time, bookshelf_no, issuer_name)
            VALUES (1, ?, 'Issued', ?, '2026-11-20', '10:30:00', 'Shelf A-3', 'Librarian Rose Davies')
        """, (v['id'], today))

# 6. Ensure fees record exists
if virat_student_id:
    cur.execute("SELECT COUNT(*) FROM payments WHERE student_id = ?", (virat_student_id,))
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO payments (student_id, title, amount, paid, status, ref_no, date, method, transaction_ref)
            VALUES (?, 'Term 1 Tuition & Academic Lab Fee', 35000.0, 35000.0, 'Paid', 'REC-2026-001', ?, 'Online / UPI', 'UPI-HDFC-991823')
        """, (virat_student_id, today))

if clara_student_id:
    cur.execute("SELECT COUNT(*) FROM payments WHERE student_id = ?", (clara_student_id,))
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO payments (student_id, title, amount, paid, status, ref_no, date, method, transaction_ref)
            VALUES (?, 'Term 1 Tuition & Computer Fee', 28000.0, 28000.0, 'Paid', 'REC-2026-002', ?, 'Online Bank Transfer', 'NEFT-SBI-443322')
        """, (clara_student_id, today))

conn.commit()
print("✓ Seeded/Verified student, parent, and teacher app accounts in database!")
