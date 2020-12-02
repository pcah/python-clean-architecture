import re


def replace_in_multiline_string(pattern: str, substitute: str, text: str) -> str:
    return re.sub(pattern, substitute, text, flags=re.DOTALL)


def replace_in_file(filepath: str, pattern: str, substitute: str) -> bool:
    with open(filepath) as f:
        contents = f.read()
    new_contents = replace_in_multiline_string(pattern, substitute, contents)
    if new_contents != contents:
        with open(filepath, "w") as f:
            f.write(new_contents)
        return True
    return False
