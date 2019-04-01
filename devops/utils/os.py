import re


def replace_in_multiline_string(pattern: str, substitute: str, text: str):
    return re.sub(pattern, substitute, text, flags=re.DOTALL)


def replace_in_file(filepath: str, pattern: str, substitute: str) -> None:
    with open(filepath) as f:
        contents = f.read()
    contents = replace_in_multiline_string(pattern, substitute, contents)
    with open(filepath, 'w') as f:
        f.write(contents)
