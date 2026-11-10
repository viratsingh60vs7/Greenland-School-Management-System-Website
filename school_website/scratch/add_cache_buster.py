with open('school_website/index.html', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('<script src="js/app.js"></script>', '<script src="js/app.js?v=20261109_common_id"></script>')
with open('school_website/index.html', 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(c)
print('Cache buster added to app.js script tag in index.html')
