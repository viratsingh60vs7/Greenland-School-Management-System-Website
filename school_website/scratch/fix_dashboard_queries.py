import sqlite3

conn = sqlite3.connect('school_website/school.db')
cur = conn.cursor()

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
conn.commit()
print("✓ Created it_asset_requests table in school.db!")

# Now fix queries in server.py
with open('school_website/server.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix student_dashboard query
old_s_query = """                cur.execute(\"\"\"
                    SELECT br.*, b.title as book_title, b.author, b.cover, b.bookshelf
                    FROM book_requests br
                    JOIN books b ON br.book_id = b.id
                    WHERE br.user_id = ? AND br.status IN ('Issued', 'Approved', 'Pending')
                    ORDER BY br.id DESC
                \"\"\", (u['id'],))"""

new_s_query = """                cur.execute(\"\"\"
                    SELECT br.*, b.title as book_title, b.author, COALESCE(br.bookshelf_no, b.bookshelf_no) as bookshelf_no
                    FROM book_requests br
                    JOIN books b ON br.book_id = b.id
                    WHERE br.user_id = ? AND br.status IN ('Issued', 'Approved', 'Pending')
                    ORDER BY br.id DESC
                \"\"\", (u['id'],))"""

assert old_s_query in code, "old_s_query not found in server.py"
code = code.replace(old_s_query, new_s_query, 1)

# Fix student timetable query
old_s_tt = """                c_id = s_row['class_id'] if s_row else 1
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
                \"\"\", (c_id,))"""

new_s_tt = """                c_id = s_row['class_id'] if s_row else 1
                sec_id = s_row['section_id'] if s_row else 1
                cur.execute(\"\"\"
                    SELECT sub.name as subject_name, sub.code, u.name as teacher_name
                    FROM subjects sub
                    LEFT JOIN users u ON sub.teacher_id = u.id
                    LIMIT 6
                \"\"\")"""

assert old_s_tt in code, "old_s_tt not found in server.py"
code = code.replace(old_s_tt, new_s_tt, 1)

# Fix parent_dashboard query
old_p_query = """                    cur.execute(\"\"\"
                        SELECT br.*, b.title as book_title, b.author, b.bookshelf
                        FROM book_requests br
                        JOIN books b ON br.book_id = b.id
                        WHERE br.user_id = ? AND br.status IN ('Issued', 'Approved', 'Pending')
                    \"\"\", (c_uid,))"""

new_p_query = """                    cur.execute(\"\"\"
                        SELECT br.*, b.title as book_title, b.author, COALESCE(br.bookshelf_no, b.bookshelf_no) as bookshelf_no
                        FROM book_requests br
                        JOIN books b ON br.book_id = b.id
                        WHERE br.user_id = ? AND br.status IN ('Issued', 'Approved', 'Pending')
                    \"\"\", (c_uid,))"""

assert old_p_query in code, "old_p_query not found in server.py"
code = code.replace(old_p_query, new_p_query, 1)

# Fix teacher_dashboard query
old_t_classes = """                cur.execute(\"\"\"
                    SELECT sub.id as subject_id, sub.name as subject_name, c.name as class_name, sec.name as section_name
                    FROM subjects sub
                    LEFT JOIN classes c ON sub.class_id = c.id
                    LEFT JOIN sections sec ON sub.class_id = sec.class_id
                    WHERE sub.teacher_id = ?
                    LIMIT 4
                \"\"\", (t['id'],))"""

new_t_classes = """                cur.execute(\"\"\"
                    SELECT sub.id as subject_id, sub.name as subject_name, sub.code
                    FROM subjects sub
                    WHERE sub.teacher_id = ?
                    LIMIT 4
                \"\"\", (t['id'],))"""

assert old_t_classes in code, "old_t_classes not found in server.py"
code = code.replace(old_t_classes, new_t_classes, 1)

with open('school_website/server.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ Fixed all dashboard queries in server.py!")
