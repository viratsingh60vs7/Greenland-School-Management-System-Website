with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Check simple bracket balancing (ignoring comments/strings approximately)
# Or write a small tokenizer
stack = []
in_str = False
str_char = ''
in_line_comment = False
in_block_comment = False
in_template = False

errors = []
for line_no, line in enumerate(text.splitlines(), start=1):
    i = 0
    while i < len(line):
        ch = line[i]
        # check comments
        if not in_str and not in_template:
            if not in_block_comment and line[i:i+2] == '//':
                break
            if not in_block_comment and line[i:i+2] == '/*':
                in_block_comment = True
                i += 2
                continue
            if in_block_comment and line[i:i+2] == '*/':
                in_block_comment = False
                i += 2
                continue
        if in_block_comment:
            i += 1
            continue

        # strings
        if not in_str and not in_template:
            if ch in ('"', "'"):
                in_str = True
                str_char = ch
                i += 1
                continue
            if ch == '`':
                in_template = True
                i += 1
                continue
        elif in_str:
            if ch == '\\':
                i += 2
                continue
            if ch == str_char:
                in_str = False
            i += 1
            continue
        elif in_template:
            if ch == '\\':
                i += 2
                continue
            if ch == '`':
                in_template = False
                i += 1
                continue
            if line[i:i+2] == '${':
                stack.append(('${', line_no))
                i += 2
                continue

        # braces/brackets
        if ch in ('{', '(', '['):
            stack.append((ch, line_no))
        elif ch in ('}', ')', ']'):
            if not stack:
                errors.append(f"Unexpected '{ch}' at line {line_no}")
            else:
                top, top_line = stack.pop()
                expected = {'{': '}', '(': ')', '[': ']', '${': '}'}.get(top)
                if expected != ch:
                    errors.append(f"Mismatched '{top}' from line {top_line} with '{ch}' at line {line_no}")
        i += 1

print(f"Brackets validation done. Errors count: {len(errors)}")
if errors:
    for e in errors[:10]:
        print(e)
if stack:
    print(f"Unclosed items in stack: {len(stack)}")
    for s in stack[-5:]:
        print(s)
