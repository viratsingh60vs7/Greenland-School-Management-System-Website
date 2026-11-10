with open('school_website/server.py', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("path == '/api/login'")
print(text[pos:pos+1500])
