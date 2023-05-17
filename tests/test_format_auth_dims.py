import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pandas as pd
import numpy as np
from clean import format_auth_dims


def test_format_auth_dims():
    # Test case 1: Single author, no modification
    output_str = format_auth_dims('Doe, John')
    assert output_str == 'Doe, J.'

    # Test case 2: Multiple authors, last name modification
    output_str = format_auth_dims('Smith, Jane; Doe, J.')
    assert output_str == 'Smith, J.; Doe, J.'

    # Test case 3: Multiple authors, last name and first name modification
    output_str = format_auth_dims('Bhat, Sanjay P.; Kumar, M. Uday; Mohammed, Shariq')
    assert output_str == 'Bhat, S.P.; Kumar, M.U.; Mohammed, S.'

    # Test case 4: No authors
    output_str =  format_auth_dims('')
    assert pd.isna(output_str)

    # Test case 5: Single author with a name ending in '.'
    output_str = format_auth_dims(np.nan)
    assert pd.isna(output_str)

test_format_auth_dims()