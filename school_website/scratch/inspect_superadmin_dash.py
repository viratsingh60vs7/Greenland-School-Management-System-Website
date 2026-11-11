with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('async function renderSuperAdminDashboard()')
if pos == -1:
    pos = text.find('function renderSuperAdminDashboard()')
print(text[pos:pos+1200])
