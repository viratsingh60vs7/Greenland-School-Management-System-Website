import sqlite3
conn = sqlite3.connect('school_website/school.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("""
    SELECT s.id as student_id, s.adm_no, s.user_id, s.parent_id,
           u.name as student_name, u.phone as student_phone, u.username as student_username,
           p.name as parent_name, p.phone as parent_phone, p.username as parent_username
    FROM students s
    LEFT JOIN users u ON s.user_id = u.id
    LEFT JOIN users p ON s.parent_id = p.id
    LIMIT 5
""")
for r in cur.fetchall():
    print(dict(r))
