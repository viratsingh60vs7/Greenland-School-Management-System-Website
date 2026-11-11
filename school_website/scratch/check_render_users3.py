with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("function renderUsersTab")
print(text[pos+5000:pos+8000])
