import sqlite3

conn = sqlite3.connect('school_website/school.db')
cur = conn.cursor()
cur.execute("UPDATE users SET username = 'GS_teacher', is_common_id = 1, common_id_name = 'Computer Teacher Lab Fleet (Lab 1 & 2 Common ID)', has_mail_services = 0 WHERE id = 93")
conn.commit()
conn.close()
print("Updated user 93 to GS_teacher with Common ID")

# Also update server.py
with open('school_website/server.py', 'r', encoding='utf-8') as f:
    code = f.read()

code_norm = code.replace('\r\n', '\n')
old_t = "cur.execute(\"SELECT id FROM users WHERE username = 'GS_teacher'\")"
new_t = "cur.execute(\"SELECT id FROM users WHERE username IN ('GS_teacher', 'GS_Computer_Teacher') OR email = 'teacher.chike@greenlandschool.net'\")"
if old_t in code_norm:
    code_norm = code_norm.replace(old_t, new_t)
    with open('school_website/server.py', 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(code_norm)
    print("Updated server.py computer teacher lookup")
