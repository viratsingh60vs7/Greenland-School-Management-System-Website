with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("IT & Owner Credential Desk")
print(text[pos-200:pos+500])
