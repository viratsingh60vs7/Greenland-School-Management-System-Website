with open('school_website/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

pos1 = html.find('<!-- Staff Usernames Directory')
pos2 = html.find('<form id="portal-login-form"', pos1)

print("Block in index.html:")
print(html[pos1:pos2])
