with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('ROLE_ALLOWED_TABS = {')
end = text.find('};', pos)
print(repr(text[pos:end+2]))
