with open('school_website/server.py', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("path == '/api/leaves/action'")
print("Leaves action:")
print(text[pos:pos+1000])

pos2 = text.find("path == '/api/lab/complaints/resolve'")
print("\nLab resolve:")
print(text[pos2:pos2+1000])
