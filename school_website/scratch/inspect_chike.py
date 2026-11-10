import sqlite3
conn = sqlite3.connect('school_website/school.db')
cur = conn.cursor()
cur.execute("SELECT id, username, email, name FROM users WHERE email LIKE '%chike%' OR username = 'GS_teacher'")
print(cur.fetchall())
conn.close()
