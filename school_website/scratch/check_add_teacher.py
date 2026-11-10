with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("function submitAddTeacher")
if pos != -1:
    print(text[pos:pos+700])
else:
    print("submitAddTeacher not found")
