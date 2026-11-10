import os
import sys
import threading
import time
import webbrowser

# Add school_website directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
school_website_dir = os.path.join(current_dir, "school_website")
sys.path.insert(0, school_website_dir)

from server import run_server, PORT

def open_browser():
    time.sleep(1.2)
    url = f"http://127.0.0.1:{PORT}#login"
    print(f"Opening browser at: {url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Browser launch notice: {e}")

if __name__ == '__main__':
    threading.Thread(target=open_browser, daemon=True).start()
    run_server()
