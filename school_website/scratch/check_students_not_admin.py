import sqlite3

conn = sqlite3.connect('school_website/school.db')
cur = conn.cursor()
cur.execute("""
    SELECT u.id, u.username, u.admin_user_id, u.admin_username, a.user_type as admin_role
    FROM users u
    LEFT JOIN users a ON u.admin_user_id = a.id
    WHERE u.is_common_id = 1
""")
print("Common IDs and their admins:")
for row in cur.fetchall():
    print(" ", row)

# Clean any common ID admin that is a student or parent
cur.execute("""
    UPDATE users 
    SET admin_user_id = NULL, admin_username = NULL, admin_name = NULL 
    WHERE admin_user_id IN (SELECT id FROM users WHERE user_type IN ('student', 'parent', 'common_id'))
""")
conn.commit()
conn.close()
