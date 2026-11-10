import urllib.request, urllib.error, json, time, subprocess, sys, os

def test():
    # Start server in thread or process
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    proc = subprocess.Popen([sys.executable, 'run_website.py'], cwd=root_dir)
    time.sleep(2.5)

    try:
        # Test GET /api/users
        req = urllib.request.Request('http://localhost:5000/api/users')
        with urllib.request.urlopen(req) as resp:
            users = json.loads(resp.read().decode('utf-8'))
            print(f"Initial GET /api/users returned {len(users)} users:")
            for u in users:
                print(f"  - {u['id']}: {u['username']} ({u['name']}) [{u['user_type']}]")

        # Test POST /api/system/clean_test_data
        data = json.dumps({"requested_by": "Owner(Directer)", "username": "Owner(Directer)"}).encode('utf-8')
        req = urllib.request.Request('http://localhost:5000/api/system/clean_test_data', data=data, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req) as resp:
            clean_res = json.loads(resp.read().decode('utf-8'))
            print("\nPOST /api/system/clean_test_data result:", clean_res)
            assert clean_res['success'] is True

        # Test GET /api/users after clean
        req = urllib.request.Request('http://localhost:5000/api/users')
        with urllib.request.urlopen(req) as resp:
            users_after = json.loads(resp.read().decode('utf-8'))
            print(f"\nAfter clean GET /api/users returned {len(users_after)} users:")
            for u in users_after:
                print(f"  - {u['id']}: {u['username']} ({u['name']}) [{u['user_type']}]")
            assert len(users_after) <= 3, f"Expected 3 or fewer users, got {len(users_after)}"

        # Test GET /api/students after clean
        req = urllib.request.Request('http://localhost:5000/api/students')
        with urllib.request.urlopen(req) as resp:
            students = json.loads(resp.read().decode('utf-8'))
            print(f"\nAfter clean GET /api/students returned {len(students)} students.")
            assert len(students) == 0, f"Expected 0 students, got {len(students)}"

        # Test POST /api/system/seed_faculty
        req = urllib.request.Request('http://localhost:5000/api/system/seed_faculty', data=b'{}', headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req) as resp:
            seed_res = json.loads(resp.read().decode('utf-8'))
            print("\nPOST /api/system/seed_faculty result:", seed_res)
            assert seed_res['success'] is True

        # Test GET /api/users after seed
        req = urllib.request.Request('http://localhost:5000/api/users')
        with urllib.request.urlopen(req) as resp:
            users_seeded = json.loads(resp.read().decode('utf-8'))
            print(f"\nAfter seed GET /api/users returned {len(users_seeded)} users.")
            assert len(users_seeded) > 3, "Expected faculty users to be re-seeded"

        # Now clean again to ensure repeatable idempotence
        data = json.dumps({"requested_by": "Owner(Directer)", "username": "Owner(Directer)"}).encode('utf-8')
        req = urllib.request.Request('http://localhost:5000/api/system/clean_test_data', data=data, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req) as resp:
            clean_res2 = json.loads(resp.read().decode('utf-8'))
            print("\nSecond POST /api/system/clean_test_data result:", clean_res2)
            assert clean_res2['success'] is True

        # Verify clean again
        req = urllib.request.Request('http://localhost:5000/api/users')
        with urllib.request.urlopen(req) as resp:
            users_final = json.loads(resp.read().decode('utf-8'))
            print(f"\nFinal GET /api/users returned {len(users_final)} users:")
            for u in users_final:
                print(f"  - {u['id']}: {u['username']} ({u['name']}) [{u['user_type']}]")
            assert len(users_final) <= 3

        print("\n==============================================")
        print("✓ ALL HTTP ENDPOINT CLEAN TESTS PASSED 100%!")
        print("==============================================")

    finally:
        proc.terminate()
        proc.wait()

if __name__ == '__main__':
    test()
