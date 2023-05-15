import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# import pandas as pd
# import numpy as np
import re

from add_col_search_term_matches import extract_search_terms

def test_extract_search_terms():

    search_terms_str = '"systemic risk" OR asset* AND NOT (TITLE-ABS:(asset AND (*systemic* OR "risk *assessment"))) OR ISSN:(123456)'
    # search_terms_str = 'TITLE-ABS (asset)'


    search_terms = extract_search_terms(search_terms_str = search_terms_str)

test_extract_search_terms()