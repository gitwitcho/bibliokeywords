import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import numpy as np
import pandas as pd
from typing import Union
from clean import format_auth_affils_scopus

def test_format_auth_affils_scopus():

    # Note: in Scopus, multiple affiliations are separated with a comma so that
    # they are combined into a single affiliation.

    # Test case 1: Valid input with multiple authors
    input_str = 'Smith, J., Harvard University, Boston, USA; Brown, M., NYU Stern'
    expected_output = 'Smith, J. (Harvard University, Boston, USA); Brown, M. (NYU Stern)'
    output_str = format_auth_affils_scopus(input_str)
    assert output_str == expected_output

    # Test case 2: Valid input with single author and affiliation
    input_str = 'Jones, S., UCLA'
    expected_output = 'Jones, S. (UCLA)'
    output_str = format_auth_affils_scopus(input_str)
    assert output_str == expected_output

    # Test case 3: Input with missing affiliation for one author
    # This is a case where the output isn't well-constructed. Unfortunately, in the
    # case where only the author or the affiliation is provided, it is not possible
    # in general to determine whether it is a name or an affiliation.
    # is not easily possible to determine whether 
    input_str = 'Smith, J., Harvard University; Brown, M.'
    expected_output = 'Smith, J. (Harvard University); Brown, M. ()'
    output_str = format_auth_affils_scopus(input_str)
    assert output_str == expected_output

    # Test case 4: Input with missing author and affiliation
    input_str = ''
    expected_output = 'Anonymous ()'
    output_str = format_auth_affils_scopus(input_str)
    assert output_str == expected_output

    # Test case 5: Input is NaN
    input_str = np.nan
    expected_output = np.nan
    output_str = format_auth_affils_scopus(input_str)
    assert pd.isna(output_str) == pd.isna(expected_output)

    # Test case 6: Input with leading/trailing whitespaces
    input_str = '   Smith, J., Harvard University; Brown, M., NYU Stern   '
    expected_output = 'Smith, J. (Harvard University); Brown, M. (NYU Stern)'
    output_str = format_auth_affils_scopus(input_str)
    assert output_str == expected_output

    # Test case 7: Input with extra whitespaces in author and affiliation
    input_str = 'Smith, J. ,  Harvard University ;  Brown, M. , NYU Stern'
    expected_output = 'Smith, J. (Harvard University); Brown, M. (NYU Stern)'
    output_str = format_auth_affils_scopus(input_str)
    assert output_str == expected_output
