import sqlite3

# 1. Update school.db so any email = '' is set to NULL
conn = sqlite3.connect('school_website/school.db')
cur = conn.cursor()
cur.execute("UPDATE users SET email = NULL WHERE email = '' OR email IS NULL OR (is_common_id = 1 AND (email LIKE '%nomail%' OR email = ''))")
conn.commit()
conn.close()
print("Updated database: set empty emails to NULL")

# 2. Update server.py
with open('school_website/server.py', 'r', encoding='utf-8') as f:
    code = f.read()

code_norm = code.replace('\r\n', '\n')

code_norm = code_norm.replace("'' if is_common else proposed_email", "None if is_common else (proposed_email or None)")
code_norm = code_norm.replace("'' if is_c else req['proposed_email']", "None if is_c else (req['proposed_email'] or None)")
code_norm = code_norm.replace("if is_common:\n                    new_email = ''", "if is_common:\n                    new_email = None")

with open('school_website/server.py', 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(code_norm)
print("Updated server.py to use None for common ID email")
