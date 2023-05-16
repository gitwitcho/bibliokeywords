import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Import your module or package
import utilities

from utilities import *

# Get functions with docstrings from the module
functions_with_docstrings = get_functions_with_docstrings(utilities)

# Print the overview
for name, docstring in functions_with_docstrings:
    print(f"Function: {name}")
    print(f"Docstring:\n{docstring}\n")