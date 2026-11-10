import sys

with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    code = f.read()

in_single_quote = False
in_double_quote = False
in_backtick = False
in_line_comment = False
in_block_comment = False
stack = []
line = 1
col = 0

i = 0
n = len(code)
errors = []
while i < n:
    c = code[i]
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
        if c == '*' and i + 1 < n and code[i+1] == '/':
            in_block_comment = False
            i += 2
            col += 1
            continue
        i += 1
        continue

    # Escape in string
    if (in_single_quote or in_double_quote or in_backtick) and c == '\\':
        i += 2
        col += 1
        continue

    if in_single_quote:
        if c == "'":
            in_single_quote = False
        i += 1
        continue
    if in_double_quote:
        if c == '"':
            in_double_quote = False
        i += 1
        continue
    if in_backtick:
        if c == '`':
            in_backtick = False
        i += 1
        continue

    # Check start of comment
    if c == '/' and i + 1 < n:
        if code[i+1] == '/':
            in_line_comment = True
            i += 2
            col += 1
            continue
        elif code[i+1] == '*':
            in_block_comment = True
            i += 2
            col += 1
            continue

    if c == "'":
        in_single_quote = True
        i += 1
        continue
    if c == '"':
        in_double_quote = True
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
            errors.append(f'Extra closing {c} at line {line}:{col}')
        else:
            top, tl, tc = stack.pop()
            matches = {')':'(', '}':'{', ']':'['}
            if matches[c] != top:
                errors.append(f'Mismatched {c} at line {line}:{col}, expected matching for {top} from line {tl}:{tc}')
                break
    i += 1

if stack:
    top, tl, tc = stack[-1]
    errors.append(f'Unclosed {top} from line {tl}:{tc}. Total unclosed: {len(stack)}')

print('Syntax check result: Errors found =', len(errors))
for err in errors[:10]:
    print('  ', err)
