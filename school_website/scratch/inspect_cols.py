import sqlite3
conn = sqlite3.connect('school_website/school.db')
cur = conn.cursor()

print("Books table columns:")
cur.execute("PRAGMA table_info(books)")
for c in cur.fetchall():
    print(c)

print("\nSubjects table columns:")
cur.execute("PRAGMA table_info(subjects)")
for c in cur.fetchall():
    print(c)

print("\nit_asset_requests table exists?")
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='it_asset_requests'")
print(cur.fetchall())
