with open('school_website/server.py', 'r', encoding='utf-8') as f:
    c = f.read()

target1 = 'cur.execute("DELETE FROM book_requests WHERE student_id NOT IN (SELECT id FROM students)")'
replacement1 = 'cur.execute("DELETE FROM book_requests WHERE user_id NOT IN (SELECT id FROM users)")'

target2 = 'cur.execute("DELETE FROM notifications_outbox WHERE recipient NOT LIKE \'%vs0839265%\' AND recipient NOT LIKE \'%Virat%\'")'
replacement2 = '''cur.execute("""
                    DELETE FROM notifications_outbox 
                    WHERE (recipient_email IS NULL OR recipient_email NOT LIKE '%vs0839265%')
                      AND (applicant_name IS NULL OR applicant_name NOT LIKE '%Virat%')
                """)'''

assert target1 in c, 'target1 not found'
c = c.replace(target1, replacement1, 1)

assert target2 in c, 'target2 not found'
c = c.replace(target2, replacement2, 1)

with open('school_website/server.py', 'w', encoding='utf-8') as f:
    f.write(c)

print("Successfully replaced SQL delete statements in server.py!")
