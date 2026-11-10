import sqlite3
conn = sqlite3.connect('school_website/school.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM students")
print("Students count:", cur.fetchone()[0])

cur.execute("SELECT COUNT(*) FROM books")
print("Books count:", cur.fetchone()[0])

cur.execute("SELECT COUNT(*) FROM classes")
print("Classes count:", cur.fetchone()[0])

cur.execute("SELECT COUNT(*) FROM sections")
print("Sections count:", cur.fetchone()[0])
