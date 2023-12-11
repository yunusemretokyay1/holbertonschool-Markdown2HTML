#!/usr/bin/python3
"""Write a script markdown2html.py that takes an argument 2 strings:"""
import sys

def convert_heading(line):
    if line.startswith("#"):
        heading_level = min(line.count("#"), 6)
        heading_text = line.strip("# ").strip()
        html_heading = f"<h{heading_level}>{heading_text}</h{heading_level}>"
        return html_heading
    else:
        return line
def convert_unordered_list(line):
    if line.startswith("- ") and not line.startswith("# "):
        list_item = line.strip("- ").strip()
        html_list_item = f"<li>{list_item}</li>"
        return html_list_item
    else:
        return line


def markdown_file(name, output):
    try:
        with open(name, 'r') as file:
            markdown_lines = file.readlines()

        converted_lines = []
        for line in markdown_lines:
            converted_line = convert_heading(line)
            converted_line = convert_unordered_list(converted_line)
            converted_lines.append(converted_line)

        with open(output, 'w') as file:
            for line in converted_lines:
                file.write(line)

    except FileNotFoundError:
        sys.stderr.write(f"Missing {name}\n")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.stderr.write("Usage: ./markdown2html.py README.md README.html\n")
        sys.exit(1)

    markdown_file(sys.argv[1], sys.argv[2])
