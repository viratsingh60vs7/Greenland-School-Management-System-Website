with open('school_website/server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for idx, line in enumerate(lines):
    # Check if this line is the duplicate assignment right before conn.commit() or self.send_json
    if idx + 1 == 5787 and 'alloc_id = cur.lastrowid' in line:
        print(f"Removing line {idx+1}: {line.strip()}")
        continue
    if idx + 1 == 5903 and 'ticket_id = cur.lastrowid' in line:
        print(f"Removing line {idx+1}: {line.strip()}")
        continue
    new_lines.append(line)

with open('school_website/server.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Removed duplicate rowid overwrites!")
