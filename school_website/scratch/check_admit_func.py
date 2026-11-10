# Check lines around admit_single_student in server.py
with open('school_website/server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("admit_single_student start around line 200")
for i in range(215, 245):
    print(lines[i], end='')
