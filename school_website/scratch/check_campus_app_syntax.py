with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_code = "".join(lines[10601:])

# Let's check for any basic unclosed brackets in new_code
stack = []
line = 10602
col = 0
errors = []

in_single = False
in_double = False
in_backtick = False
in_line_comment = False
in_block_comment = False

i = 0
n = len(new_code)

while i < n:
    c = new_code[i]
    col += 1
    if c == '\n':
        line += 1
        col = 0
        in_line_comment = False
        i += 1
        continue
    
    if in_line_comment:
        i += 1
        continue
    
    if in_block_comment:
        if c == '*' and i + 1 < n and new_code[i+1] == '/':
            in_block_comment = False
            i += 2
            col += 1
            continue
        i += 1
        continue
        
    if in_single:
        if c == '\\':
            i += 2; col += 1; continue
        if c == "'":
            in_single = False
        i += 1
        continue

    if in_double:
        if c == '\\':
            i += 2; col += 1; continue
        if c == '"':
            in_double = False
        i += 1
        continue

    if in_backtick:
        if c == '\\':
            i += 2; col += 1; continue
        if c == '`':
            in_backtick = False
        i += 1
        continue

    if c == '/' and i + 1 < n:
        if new_code[i+1] == '/':
            in_line_comment = True
            i += 2
            col += 1
            continue
        elif new_code[i+1] == '*':
            in_block_comment = True
            i += 2
            col += 1
            continue

    if c == "'":
        in_single = True
        i += 1
        continue
    if c == '"':
        in_double = True
        i += 1
        continue
    if c == '`':
        in_backtick = True
        i += 1
        continue

    if c in '{[(':
        stack.append((c, line, col))
    elif c in '}])':
        if not stack:
            errors.append(f'Unexpected {c} at {line}:{col}')
        else:
            top, tl, tc = stack.pop()
            expected = '{' if c == '}' else ('[' if c == ']' else '(')
            if top != expected:
                errors.append(f'Mismatched {c} at {line}:{col}, top was {top} from {tl}:{tc}')
                break
    i += 1

if stack:
    errors.append(f'Unclosed count: {len(stack)}, first: {stack[0]}')

print('Campus App code check errors:', len(errors))
for e in errors[:5]:
    print(' ', e)
