with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('ROLE_ALLOWED_TABS = {')
print(repr(text[pos:pos+400]))
