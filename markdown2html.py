#!/usr/bin/python3
"""
Converts markdown to HTML.

Usage: ./markdown2html.py <MD input file> <HTML output file>
"""
from sys import argv, stderr, exit
from hashlib import md5
from typing import List


def decorated_line(line: str, inside_header: bool = False) -> str:
    """
    Returns a new string like line,
    but with its mardown decorations ("**...**", "__...__")
    as their corresponding HTML tags (<b>...</b>, <em></em>)
    and these markdown decorations: "[[...]]", "((...))"
    as the MD5 of the content and the content without 'c's (case-sensitive)

    'inside_header' indicates if the line is part of a header,
    so that <em>'s can instead be <b>'s.
    """

    syntax_tree_stack: List[List[str, str]] = [["", ""]]
    """
    A list of lists of the opening bracket type and the contents inside it.
    0th item is where the final result should end up in, and it has no opening bracket.

    Good for finding missmatching bracket errors.
    """

    # concatenate every character in the line to the string in the top
    # (in-most) level of the 'syntax_tree_stack_', if the character is normal.

    # ...But if it's an opening bracket, create a new level of the stack with the opening
    # bracket (to remember it when we find its closing bracket, so that we can validate
    # where each bracket opens, and where they close, and if there are missmatched brackets)
    # and "", which will be the new top (in-most) string

    # ...And if it's a closing bracket, check if it closes the top level string.
    # If it doesn't, or if there is nothing in the 'syntax_tree_stack', raise a SyntaxError.
    # If it does, pop the list of the bracket and string enclosed by the brackets off the
    # 'syntax_tree_stack', modify the text according to this function's docstring,
    # and concatenate the decorated content into the previous level of 'syntax_tree_stack'.
    # If there is no lower (outer) level in the 'syntax_tree_stack', there is an unmatched closing bracket,
    # and we need to raise SyntaxError.

    line_index: int = 0

    def raise_too_many_closing_decoration_error(decoration: str):
        raise SyntaxError(f'\n\tIn index {line_index}:\n\tToo many "{decoration}"!\n\tsyntax_tree_stack={syntax_tree_stack}')

    while line_index < len(line):

        # print(line[line_index])

        if line.startswith("((", line_index):
            syntax_tree_stack.append(["((", ""])

            line_index += 2

        elif line.startswith("))", line_index):

            if not syntax_tree_stack or syntax_tree_stack[-1][0] != "((":
                raise_too_many_closing_decoration_error("))")

            c_less_line_segment: str = syntax_tree_stack.pop()[1].replace("C", "").replace("c", "")

            if not syntax_tree_stack:
                raise_too_many_closing_decoration_error("))")

            syntax_tree_stack[-1][1] += c_less_line_segment

            line_index += 2

        elif line.startswith("[[", line_index):
            syntax_tree_stack.append(["[[", ""])

            line_index += 2

        elif line.startswith("]]", line_index):
            if not syntax_tree_stack or syntax_tree_stack[-1][0] != "[[":
                raise_too_many_closing_decoration_error("]]")

            md5_line_segment: str = md5(syntax_tree_stack.pop()[1].encode()).hexdigest()

            if not syntax_tree_stack:
                raise_too_many_closing_decoration_error("]]")

            syntax_tree_stack[-1][1] += md5_line_segment

            line_index += 2

        elif line.startswith("**", line_index):
            if not syntax_tree_stack or syntax_tree_stack[-1][0] != "**":
                syntax_tree_stack.append(["**", ""])
            else:
                bold_line_segment: str = f"<b>{syntax_tree_stack.pop()[1]}</b>"

                if not syntax_tree_stack:
                    raise_too_many_closing_decoration_error("**")
                syntax_tree_stack[-1][1] += bold_line_segment

            line_index += 2
        
        elif line.startswith("__", line_index):
            if not syntax_tree_stack or syntax_tree_stack[-1][0] != "__":
                syntax_tree_stack.append(["__", ""])
            else:
                TAG_NAME = "em"  # if not inside_header else "b"

                bold_line_segment: str = f"<{TAG_NAME}>{syntax_tree_stack.pop()[1]}</{TAG_NAME}>"

                if not syntax_tree_stack:
                    raise_too_many_closing_decoration_error("__")
                syntax_tree_stack[-1][1] += bold_line_segment

            line_index += 2

        else:
            syntax_tree_stack[-1][1] += line[line_index]

            line_index += 1

    if len(syntax_tree_stack) > 1:
        raise SyntaxError("Opened decorations weren't closed!")
    elif len(syntax_tree_stack) < 1:
        raise SyntaxError("Too many closing decorations!")

    assert syntax_tree_stack[0][0] == ""

    return syntax_tree_stack[0][1]


if __name__ == "__main__":
    assert argv

    if len(argv) < 3:
        print(f"Usage: {argv[0]} README.md README.html", file=stderr)
        exit(1)

    MD_INPUT_FILE_NAME = argv[1]
    HTML_OUTPUT_FILE_NAME = argv[2]

    try:
        MD_INPUT_FILE = open(MD_INPUT_FILE_NAME)
    except FileNotFoundError:
        print(f"Missing {MD_INPUT_FILE_NAME}", file=stderr)
        exit(1)

    HTML_OUTPUT_FILE = open(HTML_OUTPUT_FILE_NAME, "w")

    previous_line_type: str = ""

    for line in MD_INPUT_FILE:

        # Close opened tags, if any
        if previous_line_type == "p" and not line[:-1]:
            HTML_OUTPUT_FILE.write("</p>")
        elif previous_line_type == "ul" and not line.startswith("- "):
            HTML_OUTPUT_FILE.write("</ul>")
        elif previous_line_type == "ol" and not line.startswith("* "):
            HTML_OUTPUT_FILE.write("</ol>")

        if line.startswith("#"):

            for hashtag_amount in range(1, 6 + 1):
                HEADING_LINE_START = "#" * hashtag_amount + " "

                if line.startswith(HEADING_LINE_START):

                    REST_OF_LINE = line[hashtag_amount + 1:].strip()
                    DECORATED_LINE = decorated_line(REST_OF_LINE, inside_header=True)
                    #        ("__...__" used inside of a MD heading ^ should output bold in HTML)
                    HTML_OUTPUT_FILE.write(f"<h{hashtag_amount}>{DECORATED_LINE}</h{hashtag_amount}>")

                    previous_line_type = "h"
                    break
            else:
                if previous_line_type == "p":
                    HTML_OUTPUT_FILE.write("<br>")
                else:
                    HTML_OUTPUT_FILE.write("<p>")

                DECORATED_LINE = decorated_line(REST_OF_LINE)
                HTML_OUTPUT_FILE.write(DECORATED_LINE)
                previous_line_type = "p"

        elif line.startswith("- ") or line.startswith("* "):

            for list_line_start, list_tag in {"- ": "ul", "* ": "ol"}.items():
                if line.startswith(list_line_start):

                    if previous_line_type != list_tag:
                        HTML_OUTPUT_FILE.write(f"<{list_tag}>")
                    
                    REST_OF_LINE = line[len(list_line_start):]
                    DECORATED_REST_OF_LINE = decorated_line(REST_OF_LINE)

                    HTML_OUTPUT_FILE.write(f"<li>{DECORATED_REST_OF_LINE.strip()}</li>")
                    previous_line_type = list_tag
                    break
        elif line.strip():
            if previous_line_type == "p":
                HTML_OUTPUT_FILE.write("<br>")
            else:
                HTML_OUTPUT_FILE.write("<p>")

            DECORATED_LINE = decorated_line(line)
            HTML_OUTPUT_FILE.write(DECORATED_LINE)
            previous_line_type = "p"
        else:
            previous_line_type = ""

    # Close opened tags, if any
    if previous_line_type == "p":
        HTML_OUTPUT_FILE.write("</p>\n")
    elif previous_line_type == "ul":
        HTML_OUTPUT_FILE.write("</ul>\n")
    elif previous_line_type == "ol":
        HTML_OUTPUT_FILE.write("</ol>\n")

    exit(0)
