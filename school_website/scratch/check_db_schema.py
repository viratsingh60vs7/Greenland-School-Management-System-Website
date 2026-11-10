import sqlite3
import os

db_path = os.path.join('school_website', 'school.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. users table
cur.execute('PRAGMA table_info(users)')
u_cols = [c[1] for c in cur.fetchall()]
if 'admin_user_id' not in u_cols: cur.execute('ALTER TABLE users ADD COLUMN admin_user_id INTEGER')
if 'admin_username' not in u_cols: cur.execute('ALTER TABLE users ADD COLUMN admin_username TEXT')
if 'admin_name' not in u_cols: cur.execute('ALTER TABLE users ADD COLUMN admin_name TEXT')

# 2. lab_computers table
cur.execute('PRAGMA table_info(lab_computers)')
c_cols = [c[1] for c in cur.fetchall()]
if 'admin_user_id' not in c_cols: cur.execute('ALTER TABLE lab_computers ADD COLUMN admin_user_id INTEGER')
if 'admin_username' not in c_cols: cur.execute('ALTER TABLE lab_computers ADD COLUMN admin_username TEXT')

# 3. credential_requests table
cur.execute('PRAGMA table_info(credential_requests)')
cr_cols = [c[1] for c in cur.fetchall()]
if 'is_common_id' not in cr_cols: cur.execute('ALTER TABLE credential_requests ADD COLUMN is_common_id INTEGER DEFAULT 0')
if 'common_id_name' not in cr_cols: cur.execute('ALTER TABLE credential_requests ADD COLUMN common_id_name TEXT')
if 'admin_user_id' not in cr_cols: cur.execute('ALTER TABLE credential_requests ADD COLUMN admin_user_id INTEGER')
if 'admin_username' not in cr_cols: cur.execute('ALTER TABLE credential_requests ADD COLUMN admin_username TEXT')
if 'admin_name' not in cr_cols: cur.execute('ALTER TABLE credential_requests ADD COLUMN admin_name TEXT')
if 'assigned_lab_fleet' not in cr_cols: cur.execute('ALTER TABLE credential_requests ADD COLUMN assigned_lab_fleet TEXT')

cur.execute("SELECT id, username, is_common_id, common_id_name FROM users WHERE username = 'GS_teacher'")
t = cur.fetchone()
print('GS_teacher:', t)

conn.commit()
conn.close()
print('Database schema verification complete for school_website/school.db!')
