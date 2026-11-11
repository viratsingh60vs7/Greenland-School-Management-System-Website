with open('school_website/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('id="portal-login-view"')
end_pos = text.find('</section>', pos)
print("Portal login view section ends at:", end_pos)
print(text[end_pos-100:end_pos+300])
