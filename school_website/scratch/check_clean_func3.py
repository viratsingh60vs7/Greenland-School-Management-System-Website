with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find("function confirmCleanTestData")
print(text[pos+1000:pos+1600])
