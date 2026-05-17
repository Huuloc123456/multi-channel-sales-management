import os
import tokenize
import io

def strip_comments_and_docstrings(source_code):
    io_obj = io.StringIO(source_code)
    try:
        tokens = list(tokenize.generate_tokens(io_obj.readline))
    except tokenize.TokenError:
        return source_code

    docstring_lines = set()
    for i, tok in enumerate(tokens):
        if tok.type == tokenize.STRING:
            is_doc = False
            prev_tok = tokens[i - 1] if i > 0 else None
            next_tok = tokens[i + 1] if i + 1 < len(tokens) else None
            
            # Simple check if string token is acting as a docstring statement
            if (not prev_tok or prev_tok.type in (tokenize.INDENT, tokenize.NEWLINE, tokenize.NL)) and \
               (not next_tok or next_tok.type in (tokenize.NEWLINE, tokenize.NL, tokenize.ENDMARKER)):
                is_doc = True
                
            if is_doc:
                for line in range(tok.start[0], tok.end[0] + 1):
                    docstring_lines.add(line)

    lines = source_code.splitlines(keepends=True)
    new_lines = []
    
    comment_positions = {}
    for tok in tokens:
        if tok.type == tokenize.COMMENT:
            comment_positions[tok.start[0]] = tok.start[1]

    for idx, line in enumerate(lines, 1):
        if idx in docstring_lines:
            continue
        
        if idx in comment_positions:
            col = comment_positions[idx]
            line = line[:col].rstrip()
            if not line:
                continue
            if not line.endswith('\n') and lines[idx-1].endswith('\n'):
                line += '\n'
                
        # Keep at most one consecutive blank line
        if line.strip() == "":
            if new_lines and new_lines[-1].strip() == "":
                continue
            
        new_lines.append(line)
        
    # Remove leading/trailing blank lines
    res = "".join(new_lines)
    while res.startswith('\n'):
        res = res[1:]
    while res.endswith('\n\n'):
        res = res[:-1]
    return res

def clean_project(directory):
    for root, dirs, files in os.walk(directory):
        # Skip __pycache__ and git folders
        if '__pycache__' in root or '.git' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                print(f"Cleaning comments from: {path}")
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                cleaned = strip_comments_and_docstrings(content)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(cleaned)

if __name__ == "__main__":
    target_dir = r"D:\HUIT\python\source\DOAN\omnichannel-sales-management-2"
    clean_project(target_dir)
    print("Done!")
