with open('school_website/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos1 = text.find('class="nav-actions"')
print(text[pos1:pos1+300])

pos2 = text.find('class="role-switcher-banner')
print("\nRole switcher banner:")
print(text[pos2:pos2+600])
