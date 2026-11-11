import re

def find_in_file(path, terms):
    print(f"=== {path} ===")
    with open(path, 'r', encoding='utf-8') as f:
        for i, l in enumerate(f):
            if any(t in l.lower() for t in terms):
                print(f"{i+1}: {l.strip()[:100]}")

find_in_file('school_website/index.html', ['edit-credentials', 'forgot-password', 'change password', 'modal-edit'])
find_in_file('school_website/js/app.js', ['editcredentials', 'openforgotpassword', 'submitchangepassword', 'submiteditcredentials'])
find_in_file('school_website/server.py', ['/api/users/edit_credentials', '/api/users/change_password', '/api/auth/reset_password'])
