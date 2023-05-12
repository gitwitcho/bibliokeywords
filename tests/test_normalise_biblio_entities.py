import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pandas as pd
import numpy as np

from transform import normalise_biblio_entities, BiblioType


def test_normalise_biblio_entities():

    # Test Scopus normalisation: doi to link, links, kws, author affiliations
    df = pd.DataFrame({
        'doi': ['10.1016/j.jfin.2020.08.011', '10.1016/j.jbankfin.2019.103444', np.nan],
        'kws_author': ['Finance; Banking', np.nan, 'Finance; Economics;  '],
        'kws_index': ['Finance', 'Banking', 'Finance; Economics'],
        'auth_affils': ['Smith, J.A., Harvard University; Brown, M.', 
                        'Jones, S., UCLA; Davis, R., UC Berkeley, USA; Universität Berlin, Germany', 
                        np.nan],
        'mesh': [np.nan, 'Banking; Finance', 'Finance']
    })
    expected_df = pd.DataFrame({
        'doi': ['10.1016/j.jfin.2020.08.011', '10.1016/j.jbankfin.2019.103444', np.nan],
        'kws_author': ['finance; banking', np.nan, 'finance; economics;  '],
        'kws_index': ['finance', 'banking', 'finance; economics'],
        'auth_affils': ['Smith, J.A. (Harvard University); Brown, M. ()', 
                        'Jones, S. (UCLA); Davis, R. (UC Berkeley, USA); Universität Berlin, Germany ()', 
                        np.nan],
        'mesh': [np.nan, 'banking; finance', 'finance'],
        'link': ['https://dx.doi.org/10.1016/j.jfin.2020.08.011', 'https://dx.doi.org/10.1016/j.jbankfin.2019.103444', np.nan],
        'links': ['https://dx.doi.org/10.1016/j.jfin.2020.08.011', 'https://dx.doi.org/10.1016/j.jbankfin.2019.103444', np.nan],
        'kws': ['banking; finance', 'banking', 'economics; finance']
    })
    output_df = normalise_biblio_entities(df, BiblioType.SCOPUS)
    assert 'link' in output_df.columns
    assert 'links' in output_df.columns
    assert 'kws' in output_df.columns

    for col in output_df.columns:   # use this for pin-pointing problem column
        assert output_df[col].equals(expected_df[col])

    assert output_df.equals(expected_df)

    # Test Lens normalisation: doi to link, links, kws, author affiliations
    df = pd.DataFrame({
        'ext_url': ['https://dx.doi.org/10.1016/j.jfin.2020.08.011', 'https://dx.doi.org/10.1016/j.jbankfin.2019.103444', np.nan],
        'source_urls': ['https://dx.doi.org/10.1016/j.jfin.2020.08.011 https://dx.doi.org/10.1016/j.jbankfin.2019.103444', np.nan, np.nan],
        'kws_lens': ['Finance; Banking', np.nan, 'Finance; Economics;  '],
        'mesh': [np.nan, 'Banking; Finance', 'Finance']
    })
    expected_df = pd.DataFrame({
        'ext_url': ['https://dx.doi.org/10.1016/j.jfin.2020.08.011', 'https://dx.doi.org/10.1016/j.jbankfin.2019.103444', np.nan],
        'source_urls': ['https://dx.doi.org/10.1016/j.jfin.2020.08.011 https://dx.doi.org/10.1016/j.jbankfin.2019.103444', np.nan, np.nan],
        'kws_lens': ['finance; banking', np.nan, 'finance; economics;  '],
        'mesh': [np.nan, 'banking; finance', 'finance'],
        'link': ['https://dx.doi.org/10.1016/j.jfin.2020.08.011', 'https://dx.doi.org/10.1016/j.jbankfin.2019.103444', np.nan],
        'links': ['https://dx.doi.org/10.1016/j.jfin.2020.08.011 https://dx.doi.org/10.1016/j.jbankfin.2019.103444', np.nan, np.nan],
        'kws': ['banking; finance', 'banking; finance', 'economics; finance']
    })
    output_df = normalise_biblio_entities(df, BiblioType.LENS)
    assert 'link' in output_df.columns
    assert 'links' in output_df.columns
    assert 'kws' in output_df.columns

    # for col in output_df.columns:   # use this for pin-pointing problem column
    #     assert output_df[col].equals(expected_df[col])

    assert output_df.equals(expected_df)
    
    # Test Dimensions normalisation: doi to link, links, kws, author affiliations
    df = pd.DataFrame({
        'ext_url': ['https://dx.doi.org/10.1016/j.jfin.2020.08.011', 'https://dx.doi.org/10.1016/j.jbankfin.2019.103444', np.nan],
        'mesh': [np.nan, 'Medicine; Economics; Finance', 'Engineering'],
        'auth_affils': ['Smith, John Albert (Harvard University, USA; UB, Barcelona, Spain); Brown, Mary', 
                        'Jones, Shaun (UCLA); Davis, Rodney (UC Berkeley, USA); Universität Berlin, Germany', 
                        np.nan]
    })
    expected_df = pd.DataFrame({
        'ext_url': ['https://dx.doi.org/10.1016/j.jfin.2020.08.011', 'https://dx.doi.org/10.1016/j.jbankfin.2019.103444', np.nan],
        'mesh': [np.nan, 'medicine; economics; finance', 'engineering'],
        'auth_affils': ['Smith, J.A. (Harvard University, USA; UB, Barcelona, Spain); Brown, M. ()', 
                        'Jones, S. (UCLA); Davis, R. (UC Berkeley, USA); Universität Berlin, G. ()', 
                        np.nan],
        'link': ['https://dx.doi.org/10.1016/j.jfin.2020.08.011', 'https://dx.doi.org/10.1016/j.jbankfin.2019.103444', np.nan],
        'links': ['https://dx.doi.org/10.1016/j.jfin.2020.08.011', 'https://dx.doi.org/10.1016/j.jbankfin.2019.103444', np.nan],
        'kws': [np.nan, 'economics; finance; medicine', 'engineering']
   })
    output_df = normalise_biblio_entities(df, BiblioType.DIMS)
    assert 'link' in output_df.columns
    assert 'links' in output_df.columns
    assert 'kws' in output_df.columns

    for col in output_df.columns:   # use this for pin-pointing problem column
        assert output_df[col].equals(expected_df[col])

    assert output_df.equals(expected_df)

# test_normalise_biblio_entities()