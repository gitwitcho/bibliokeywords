import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from transform import *

def test_format_auth_affils_dims():
    
    # Test case with single author and affiliation
    input_str = 'Shriver, Erin Simon M. P. (Department of Ophthalmology, Stanford University School of Medicine, 300 Pasteur Dr. , Room A-157, 94305, Stanford, California, USA)'
    expected_output_str = 'Shriver, E.S.M.P. (Department of Ophthalmology, Stanford University School of Medicine, 300 Pasteur Dr. , Room A-157, 94305, Stanford, California, USA)'
    output_str = format_auth_affils_dims(input_str)
    assert output_str == expected_output_str

    # Test case with single author and no affiliation
    input_str = 'Shriver, Erin Simon M. P.'
    expected_output_str = 'Shriver, E.S.M.P. ()'
    output_str = format_auth_affils_dims(input_str)
    assert output_str == expected_output_str
    
    # Test case with multiple authors and multiple affiliations
    input_str = 'Miño de Kaspar, Herminia (Department of Ophthalmology, Stanford University School of Medicine, 300 Pasteur Dr. , Room A-157, 94305, Stanford, California, USA; Department of Ophthalmology, Ludwig-Maximilians-Universität, Mathildenstrasse 8, 80336, Munich, Germany); Schweizer, Pia‐Johanna (Institute for Advanced Sustainability Studies (IASS), Potsdam, Germany)'
    expected_output_str = 'Miño de Kaspar, H. (Department of Ophthalmology, Stanford University School of Medicine, 300 Pasteur Dr. , Room A-157, 94305, Stanford, California, USA; Department of Ophthalmology, Ludwig-Maximilians-Universität, Mathildenstrasse 8, 80336, Munich, Germany); Schweizer, P. (Institute for Advanced Sustainability Studies (IASS), Potsdam, Germany)'
    output_str = format_auth_affils_dims(input_str)
    assert output_str == expected_output_str

    # Test case with missing author information
    input_str = '(Higher Institute of Technological Studies in Communications in Tunis, Tunisia)'
    expected_output_str = 'Anonymous (Higher Institute of Technological Studies in Communications in Tunis, Tunisia)'
    output_str = format_auth_affils_dims(input_str)
    assert output_str == expected_output_str

    # Test case with empty input string
    input_str = ''
    expected_output_str = np.nan
    output_str = format_auth_affils_dims(input_str)
    assert pd.isna(output_str) and pd.isna(expected_output_str)

    # Test case with nan input string
    input_str = np.nan
    expected_output_str = np.nan
    output_str = format_auth_affils_dims(input_str)
    assert pd.isna(output_str) and pd.isna(expected_output_str)
