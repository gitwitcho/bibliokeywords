import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pandas as pd
import numpy as np
from transform import format_auth_lens


def test_format_auth_lens():
    # Test case 1: Single author, no modification
    output_str = format_auth_lens('John Doe')
    assert output_str == 'Doe, J.'

    # Test case 2: Multiple authors, last name modification
    output_str = format_auth_lens('Jane Smith; J. Doe')
    assert output_str == 'Smith, J.; Doe, J.'

    # Test case 3: Multiple authors, last name and first name modification
    output_str = format_auth_lens('Sanjay P. Bhat; M. Uday Kumar; Shariq Mohammed')
    assert output_str == 'Bhat, S.P.; Kumar, M.U.; Mohammed, S.'

    # Test case 4: No authors
    output_str =  format_auth_lens('')
    assert pd.isna(output_str)

    # Test case 5: Single author with a name ending in '.'
    output_str = format_auth_lens(np.nan)
    assert pd.isna(output_str)
