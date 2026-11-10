with open('school_website/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

pos = html.find("onclick=\"fillLoginUsername('GS_teacher')\"")
print(html[pos:pos+2500])
