import urllib.request, urllib.error, json, time, subprocess, sys, os

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
proc = subprocess.Popen([sys.executable, 'run_website.py'], cwd=root_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
time.sleep(2.5)

try:
    data = json.dumps({"requested_by": "Owner(Directer)", "username": "Owner(Directer)"}).encode('utf-8')
    req = urllib.request.Request('http://localhost:5000/api/system/clean_test_data', data=data, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req) as resp:
            print("RESP:", resp.status, resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print("HTTP ERROR:", e.code, e.read().decode('utf-8'))
    except Exception as e:
        print("OTHER ERROR:", e)
finally:
    proc.terminate()
    stdout, stderr = proc.communicate()
    print("SERVER STDOUT:\n", stdout)
    print("SERVER STDERR:\n", stderr)
