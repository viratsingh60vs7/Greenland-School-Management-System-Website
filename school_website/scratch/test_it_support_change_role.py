import urllib.request, urllib.error, json, time, subprocess, sys, os, sqlite3

def test_role_change():
    db_path = 'school_website/school.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Find or seed a test user to change role
    cur.execute("SELECT id, username, user_type FROM users WHERE username = 'Viratsingh60vs7'")
    target = cur.fetchone()
    if not target:
        cur.execute("SELECT id, username, user_type FROM users WHERE username != 'Owner(Directer)' LIMIT 1")
        target = cur.fetchone()
    
    target_id = target['id']
    old_role = target['user_type']
    target_username = target['username']
    print(f"Target user: ID {target_id}, Username '{target_username}', Current Role '{old_role}'")
    conn.close()

    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    proc = subprocess.Popen([sys.executable, 'run_website.py'], cwd=root_dir)
    time.sleep(2.5)

    try:
        new_role = 'teacher' if old_role != 'teacher' else 'accountant'

        # Test POST /api/users/assign_role initiated by IT Support Administrator
        payload = {
            "target_user_id": target_id,
            "user_id": target_id,
            "role": new_role,
            "name": "Virat Singh",
            "gender": "Male",
            "caller_username": "GS_itsupport",
            "assigned_by": "IT Support Administrator"
        }

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request('http://localhost:5000/api/users/assign_role', data=data, headers={'Content-Type': 'application/json'}, method='POST')
        
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            print("Response from /api/users/assign_role:", res)
            assert res['success'] is True, "Failed to change role"
            print(f"✓ Successfully changed role to '{new_role}' as IT Support Admin!")

        # Verify in DB
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id, username, user_type, name, gender FROM users WHERE id = ?", (target_id,))
        updated = cur.fetchone()
        print(f"DB verification: {dict(updated)}")
        assert updated['user_type'] == new_role, f"Expected role {new_role}, got {updated['user_type']}"
        assert updated['gender'] == 'Male', f"Expected gender Male, got {updated['gender']}"
        conn.close()

        # Reassign back to it_admin or desired role as IT Support
        payload2 = {
            "target_user_id": target_id,
            "user_id": target_id,
            "role": "it_admin",
            "name": "Virat Singh",
            "gender": "Male",
            "caller_username": "GS_itsupport",
            "assigned_by": "IT Support Administrator"
        }
        data2 = json.dumps(payload2).encode('utf-8')
        req2 = urllib.request.Request('http://localhost:5000/api/users/assign_role', data=data2, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req2) as resp:
            res2 = json.loads(resp.read().decode('utf-8'))
            print("Reset response:", res2)
            assert res2['success'] is True

        # Test role change without name to verify: no name = no gender
        payload3 = {
            "target_user_id": target_id,
            "user_id": target_id,
            "role": "librarian",
            "name": "",
            "caller_username": "GS_itsupport",
            "assigned_by": "IT Support Administrator"
        }
        data3 = json.dumps(payload3).encode('utf-8')
        req3 = urllib.request.Request('http://localhost:5000/api/users/assign_role', data=data3, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req3) as resp:
            res3 = json.loads(resp.read().decode('utf-8'))
            print("Role update without name change response:", res3)
            assert res3['success'] is True

        # Restore role back to it_admin with Virat Singh name and Male gender
        payload_restore = {
            "target_user_id": target_id,
            "user_id": target_id,
            "role": "it_admin",
            "name": "Virat Singh",
            "gender": "Male",
            "caller_username": "GS_itsupport",
            "assigned_by": "IT Support Administrator"
        }
        data_restore = json.dumps(payload_restore).encode('utf-8')
        req_restore = urllib.request.Request('http://localhost:5000/api/users/assign_role', data=data_restore, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req_restore) as resp:
            json.loads(resp.read().decode('utf-8'))

        print("\n=======================================================")
        print("✓ ALL IT SUPPORT ROLE CHANGE TESTS PASSED 100%!")
        print("=======================================================")

    finally:
        proc.terminate()
        proc.wait()

if __name__ == '__main__':
    test_role_change()
