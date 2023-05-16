import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pandas as pd
import numpy as np
from co_terms import create_co_term_graph

def test_create_co_term_df():

    # Test case 1
    se = pd.Series([
        'risk; assets; statistical',
        'banks; systemic; financial',
        'spread; bank; risks',
        'asset management; systemic risks'
    ])

    create_co_term_graph(term_se = se,
                      singularise = True,
                      synonymise = True,
                      stem = True,
                      min_count = 2)
    
test_create_co_term_df()
