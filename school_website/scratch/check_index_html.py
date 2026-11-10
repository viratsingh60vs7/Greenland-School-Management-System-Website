with open('school_website/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Check sidebar nav
pos_sidebar = content.find('<li data-tab="library">')
print("Found library in sidebar:", pos_sidebar != -1)

# 2. Check staff directory in login
pos_login = content.find("onclick=\"fillLoginUsername('GS_librarian')\"")
print("Found GS_librarian in login:", pos_login != -1)

# 3. Check modal-create-user
pos_create = content.find('id="modal-create-user"')
print("Found modal-create-user:", pos_create != -1)

# 4. Check end of modals before <script src="js/app.js">
pos_script = content.find('<script src="js/app.js"></script>')
print("Found script tag:", pos_script != -1)
