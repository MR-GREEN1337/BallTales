def sanitize_code(code: str) -> str:
    """
    Sanitize Python code by fixing common issues with indentation and structure.

    This function performs several important cleanup steps:
    1. Removes leading/trailing whitespace
    2. Ensures consistent indentation
    3. Fixes import statements placement
    4. Ensures proper block structure

    Args:
        code (str): The Python code to sanitize

    Returns:
        str: The sanitized Python code ready for execution
    """
    # First, split the code into lines and remove empty lines
    lines = [line.rstrip() for line in code.split("\n") if line.strip()]

    # Find the base indentation level (minimum non-zero indentation)
    indentation_levels = []
    for line in lines:
        leading_spaces = len(line) - len(line.lstrip())
        if leading_spaces > 0:
            indentation_levels.append(leading_spaces)

    base_indent = min(indentation_levels) if indentation_levels else 0

    # Remove the base indentation from all lines
    normalized_lines = []
    for line in lines:
        if line.strip():
            # Remove exactly base_indent spaces from the start, if they exist
            if line.startswith(" " * base_indent):
                line = line[base_indent:]
            normalized_lines.append(line)

    # Ensure imports are at the top
    import_lines = []
    other_lines = []

    for line in normalized_lines:
        if line.startswith("import ") or line.startswith("from "):
            import_lines.append(line)
        else:
            other_lines.append(line)

    # Combine the lines with proper structure
    final_lines = import_lines + [""] + other_lines if import_lines else other_lines

    # Join lines and ensure no double newlines
    code = "\n".join(final_lines)

    # Add proper indentation for try-except blocks
    code = fix_try_except_blocks(code)

    return code


def fix_try_except_blocks(code: str) -> str:
    """
    Ensure proper indentation in try-except blocks.

    Args:
        code (str): Python code to fix

    Returns:
        str: Code with properly indented try-except blocks
    """
    lines = code.split("\n")
    final_lines = []
    indent_level = 0

    for line in lines:
        stripped = line.strip()

        # Handle try and except keywords
        if stripped.startswith("try:"):
            final_lines.append(line)
            indent_level += 1
            continue

        if stripped.startswith("except"):
            indent_level -= 1
            final_lines.append(line)
            indent_level += 1
            continue

        # Add proper indentation for block contents
        if indent_level > 0 and stripped:
            final_lines.append("    " * indent_level + stripped)
        else:
            final_lines.append(line)

        # Reset indent level after block ends
        if stripped.endswith(":"):
            indent_level += 1
        elif not stripped and indent_level > 0:
            indent_level = 0

    return "\n".join(final_lines)
