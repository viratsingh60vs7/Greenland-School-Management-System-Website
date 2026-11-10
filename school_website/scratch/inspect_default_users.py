with open('school_website/server.py', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("UNIQUE_DEFAULT_USERS = [")
print(text[pos:pos+1500])
