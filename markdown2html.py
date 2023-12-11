#!/usr/bin/python3
"""Script that converts Markdown to HTML."""

-------------------------------------------------------------------------------------------------------

def file_exist(argv):
    """Verify if the necessary files exist and if the correct number of arguments are provided.
    
    Args:
        argv (list of str): Command line arguments where argv[1] is the source Markdown file
                            and argv[2] is the destination HTML file.
    """
