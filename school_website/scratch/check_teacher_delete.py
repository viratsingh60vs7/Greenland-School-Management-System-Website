with open('school_website/server.py', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("DELETE FROM users WHERE id = ? AND user_type = 'teacher'")
print(text[pos-400:pos+300])
