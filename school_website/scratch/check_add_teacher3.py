with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("function submitAddTeacher")
print(text[pos+800:pos+1500])
