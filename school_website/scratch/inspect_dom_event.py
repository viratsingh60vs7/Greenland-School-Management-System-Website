with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("DOMContentLoaded', () => {")
print(text[pos:pos+400])
