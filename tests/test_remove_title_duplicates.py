import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pandas as pd
import numpy as np

from utilities import *
from clean import *
from pandas import testing as tm

'''
The test function only uses test dfs that have columns that are being changed in 
`remove_title_duplicates` plus one that isn't changed. This needs to be revised if
and when making changes to `remove_title_duplicates`.

The following items are tested:
    - Merging of the columns
        - sources (joined by '; ')
        - bib_srcs (joined by '; ')
        - n_cited: sum the citations, except between duplicate sources where the maximum vakue is used
        - fos (joined by '; ')
        - anzsrc_2020 (joined by '; ')
        - kws (joined by '; '): 
            - kws_author, kws_index (Scopus)
            - kws_lens, mesh (Lens)
            - mesh (Dimensions)
        - link:
            - 'https://dx.doi.org/' + 'doi' (Scopus)
            - ext_url (Lens)
            - ext_url (Dimensions)
        - links (joined by '; '):
            - link (Scopus)
            - source_urls (Lens)
            - link (Dimensions)
    - Other operations
        - year replaced by pub_date, pub_date replace by year
        - authors format is normalised
        - authors-affiliations format is normalised
    - Values in all other columns are unchanged
'''


# Test case with changes to pub_date and year
#   1. pub_date given, year nan: year is pub_date year
#   2. year given, pub_date nan: pub:date is 1/1/year
#   3. neither year nor pub_date are given: both remain nan
def test_pub_date_year():

    input_df = pd.DataFrame({
        'authors': ['auth0'],
        'title': ['title0'],
        'abstract': ['abs0'],
        'year': [np.nan],
        'pub_date': [pd.NaT],
        'bib_src': ['lens']
    })

    expected_output_df = pd.DataFrame({
        'authors': ['auth0'],
        'title': ['title0'],
        'abstract': ['abs0'],
        'year': [0],
        'pub_date': [pd.NaT]
    })
    
    remove_cols = ['bib_src', 'bib_srcs']   # drop bib_src since it will be picked at random

    # 1. Neither year nor pub_date are given: both remain nan
    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    tm.assert_frame_equal(output_df.reset_index(drop = True), expected_output_df.reset_index(drop = True))

    # 2. Year given, pub_date nan: pub:date is 1/1/year
    input_df['year'] = 2023
    input_df['pub_date'] = pd.NaT
    expected_output_df['year'] = 2023
    expected_output_df['pub_date'] = pd.to_datetime('2023-01-01')

    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    tm.assert_frame_equal(output_df.reset_index(drop = True), expected_output_df.reset_index(drop = True))

    # 3. pub_date given, year nan: year is pub_date year
    input_df['year'] = np.nan
    input_df['pub_date'] = '2019-12-06'
    expected_output_df['year'] = 2019
    expected_output_df['pub_date'] = pd.to_datetime('2019-12-06')

    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    tm.assert_frame_equal(output_df.reset_index(drop = True), expected_output_df.reset_index(drop = True))


# Test case for merging the source columns
#   1. All sources are NAN or empty strings
#   2. All sources are the same except for whitespaces and letter cases
#   3. Some sources are different, with some NANs
def test_merge_source_cols():

    input_df = pd.DataFrame({
        'authors': ['auth0', 'auth0', 'auth0'],
        'title': ['title0', 'title0', 'title0'],
        'abstract': ['abs0', 'abs0', 'abs0'],
        'source': ['Scientific reports', ' scientific  reports', 'Scientific Reports'],
        'bib_src': ['lens', 'dims', 'lens']
    })

    expected_output_df = pd.DataFrame({
        'authors': ['auth0'],
        'title': ['title0'],
        'abstract': ['abs0'],
        'source': ['Scientific Reports'],
        'sources': ['Scientific Reports']
    })

    remove_cols = ['year', 'pub_date', 'bib_src', 'bib_srcs']   # drop bib_src since it will be picked at random

    # 1. All sources are NAN or empty strings
    input_df['source'] = ['', '', '']
    expected_output_df['source'] = ''
    expected_output_df['sources'] = ''

    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    tm.assert_frame_equal(output_df.reset_index(drop = True), expected_output_df.reset_index(drop = True))

    # 2. All sources are the same except for whitespaces and letter cases
    input_df['source'] = ['Scientific reports', ' scientific  reports', 'Scientific Reports']
    expected_output_df['source'] = 'Scientific Reports'
    expected_output_df['sources'] = 'Scientific Reports'

    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    tm.assert_frame_equal(output_df.reset_index(drop = True), expected_output_df.reset_index(drop = True))

    # 3. Some sources are different, with some NANs
    input_df['source'] = ['physics   today', ' scientific  reports', 'Journal of Mathematics']
    expected_output_df['sources'] = ['Physics Today; Scientific Reports; Journal of Mathematics']

    remove_cols += ['source']   # source is picked at random this scenario
    expected_output_df.drop(columns = 'source', inplace = True)

    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    tm.assert_frame_equal(output_df.reset_index(drop = True), expected_output_df.reset_index(drop = True))

# Test case for merging bib_srcs
#   1. Same bib_src
#   2. Different bib_src
def test_merge_bib_src_cols():

    input_df = pd.DataFrame({
        'authors': ['auth0', 'auth0', 'auth0'],
        'title': ['title0', 'title0', 'title0'],
        'abstract': ['abs0', 'abs0', 'abs0'],
        'bib_src': ['scopus', 'scopus', 'scopus']
    })

    expected_output_df = pd.DataFrame({
        'authors': ['auth0'],
        'title': ['title0'],
        'abstract': ['abs0'],
        'bib_srcs': ['scopus']
    })
    
    remove_cols = ['bib_src', 'year', 'pub_date']   # drop bib_src since it will be picked at random

    # 1. Same bib_src
    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    tm.assert_frame_equal(output_df.reset_index(drop = True), expected_output_df.reset_index(drop = True))

    # 2. Different bib_src
    input_df['bib_src'] = ['dims', 'scopus', 'lens']
    expected_output_df['bib_srcs'] = 'dims; scopus; lens'
    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    tm.assert_frame_equal(output_df.reset_index(drop = True), expected_output_df.reset_index(drop = True))


# Test case for merging n_cited
#   1. All sources are different: sum all n_cited
#   2. Some sources are the same: don't sum n_cited for identical sources, instead pick the max value
def test_merge_n_cited_cols():

    input_df = pd.DataFrame({
        'authors': ['auth0', 'auth0', 'auth0'],
        'title': ['title0', 'title0', 'title0'],
        'abstract': ['abs0', 'abs0', 'abs0'],
        'bib_src': ['dims', 'lens', 'scopus'],
        'source': ['pub1', 'pub2', 'pub3'],
        'n_cited': [4, 7, 12]
    })

    expected_output_df = pd.DataFrame({
        'authors': ['auth0'],
        'title': ['title0'],
        'abstract': ['abs0'],
        'n_cited': [23]
    })
    
    remove_cols = ['source', 'sources', 'bib_src', 'bib_srcs', 'year', 'pub_date']   # drop bib_src since it will be picked at random

    # 1. All sources are different: sum all n_cited
    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    tm.assert_frame_equal(output_df.reset_index(drop = True), expected_output_df.reset_index(drop = True))

    # 2. Some sources are the same: don't sum n_cited for identical sources, instead pick the max value
    input_df['source'] = ['pub1', 'pub2', 'pub1']
    expected_output_df['n_cited'] = 19
    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    tm.assert_frame_equal(output_df.reset_index(drop = True), expected_output_df.reset_index(drop = True))


# Test case for merging fos and anzsrc
def test_merge_fos_anzsrc_cols():

    input_df = pd.DataFrame({
        'authors': ['auth0', 'auth0', 'auth0'],
        'title': ['title0', 'title0', 'title0'],
        'abstract': ['abs0', 'abs0', 'abs0'],
        'bib_src': ['lens', 'lens', 'lens'],
        'fos': ['f2; f1; f3', 'f2; f4', ''],
        'anzsrc_2020': ['a1; ; a6', 'a2; a1; a5; a6', '']
    })

    expected_output_df = pd.DataFrame({
        'authors': ['auth0'],
        'title': ['title0'],
        'abstract': ['abs0'],
        'fos': ['f1; f2; f3; f4'],
        'anzsrc_2020': ['a1; a2; a5; a6']
    })
    
    remove_cols = ['bib_src', 'bib_srcs', 'year', 'pub_date']

    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    tm.assert_frame_equal(output_df.reset_index(drop = True), expected_output_df.reset_index(drop = True))


# Test case for merging keywords
def test_merge_kws_cols():

    input_df = pd.DataFrame({
        'authors': ['auth0', 'auth0', 'auth0'],
        'title': ['title0', 'title0', 'title0'],
        'abstract': ['abs0', 'abs0', 'abs0'],
        'bib_src': ['lens', 'scopus', 'dims'],
        'kws': ['k2; k1; k3', 'k2; k4', 'k9; ; k8']
    })

    expected_output_df = pd.DataFrame({
        'authors': ['auth0'],
        'title': ['title0'],
        'abstract': ['abs0'],
        'kws': ['k1; k2; k3; k4; k8; k9']
    })
    
    remove_cols = ['bib_src', 'bib_srcs', 'year', 'pub_date']   # drop bib_src since it will be picked at random

    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    tm.assert_frame_equal(output_df.reset_index(drop = True), expected_output_df.reset_index(drop = True))


# Test case for merging links
def test_merge_links_cols():

    input_df = pd.DataFrame({
        'authors': ['auth0', 'auth0', 'auth0'],
        'title': ['title0', 'title0', 'title0'],
        'abstract': ['abs0', 'abs0', 'abs0'],
        'bib_src': ['lens', 'scopus', 'dims'],
        'links': ['https://example.com https://trivia.com ', '   ', ' https://trivia.com https://any.com  ']
    })

    expected_output_df = pd.DataFrame({
        'authors': ['auth0'],
        'title': ['title0'],
        'abstract': ['abs0'],
        'links': ['https://any.com https://example.com https://trivia.com']
    })
    
    remove_cols = ['bib_src', 'bib_srcs', 'year', 'pub_date']   # drop bib_src since it will be picked at random

    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    tm.assert_frame_equal(output_df.reset_index(drop = True), expected_output_df.reset_index(drop = True))


# Test case for picking an authors string, authors-affiliations string, and links string
#   1. If there is a scopus entry, pick that authors/authors-affils/links string
#   2. If there are multiple scopus entries, pick the authors/authors-affils/links string from those at random
#   3. If there are no scopus entries, pick the authors/authors-affils/links string at random
def test_merge_authors_cols():

    input_df = pd.DataFrame({
        'authors': ['auth1', 'auth2', 'auth3'],
        'title': ['title0', 'title0', 'title0'],
        'abstract': ['abs0', 'abs0', 'abs0'],
        'bib_src': ['dims', 'lens', 'scopus'],
        'auth_affils': ['af1', 'af2', 'af3'],
        'link': ['https://example.com', '   ', 'https://trivia.com']

    })

    expected_output_df = pd.DataFrame({
        'authors': ['auth3'],
        'title': ['title0'],
        'abstract': ['abs0'],
        'bib_src': ['scopus'],
        'auth_affils': ['af3'],
        'link': ['https://trivia.com']
    })
    
    remove_cols = ['bib_srcs', 'year', 'pub_date']

    # 1. If there is a scopus entry, pick that author
    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    tm.assert_frame_equal(output_df.reset_index(drop = True), expected_output_df.reset_index(drop = True))

    # 2. If there are multiple scopus entries, pick the author from those at random
    input_df['bib_src'] = ['scopus', 'lens', 'scopus']
    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    assert (output_df['authors'].iloc[0] == 'auth1') | (output_df['authors'].iloc[0] == 'auth3')

    # 3. If there are no scopus entries, pick the author at random
    input_df['bib_src'] = ['dims', 'lens', 'dims']
    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    assert (output_df['authors'].iloc[0] == 'auth1') | (output_df['authors'].iloc[0] == 'auth2') | (output_df['authors'].iloc[0] == 'auth3')


# Test case for the complex scenario (abstract => bib_src => year => source => pub_date => random pick)
def test_complex_case():

    input_df = pd.DataFrame({
        'authors': ['auth0', 'auth0', 'auth0'],
        'title': ['title0', 'title0', 'title0'],
        'abstract': ['abs0', 'abs0', 'abs0'],
        'bib_src': ['dims', 'lens', 'scopus'],
        'source': ['s1', 's2', 's3'],
        'year': [2019, 2020, 2021],
        'pub_date': ['2019-04-01', '2020-11-23', '2021-02-13']
    })

    expected_output_df = pd.DataFrame({
        'authors': ['auth0'],
        'title': ['title0'],
        'abstract': ['abs0'],
        'bib_src': ['scopus'],
        'source': ['S3'],
        'year': 2021,
        'pub_date': pd.to_datetime('2021-02-13')
    })
    
    remove_cols = ['sources', 'bib_srcs']

    # 1. Single scopus source: picks that publication
    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    tm.assert_frame_equal(output_df.reset_index(drop = True), expected_output_df.reset_index(drop = True))

    # 2. Like 1, but no abstracts (keeps all pubs), no sources, no years, no pub_dates
    input_df['abstract'] = ['', '', '']
    input_df['source'] = ['', '', '']
    input_df['year'] = [np.nan, np.nan, np.nan]
    input_df['pub_date'] = [pd.NaT, pd.NaT, pd.NaT]
    expected_output_df['abstract'] = ['']
    expected_output_df['source'] = ['']
    expected_output_df['year'] = [0]
    expected_output_df['pub_date'] = [pd.NaT]

    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    tm.assert_frame_equal(output_df.reset_index(drop = True), expected_output_df.reset_index(drop = True))

    # 3. No abstracts, double scopus, single max year, no sources, one max pub_date: picks scopus with max year
    input_df['bib_src'] = ['scopus', 'lens', 'scopus']
    input_df['abstract'] = ['', '', '']
    input_df['source'] = ['', '', '']
    input_df['year'] = [2016, 2023, 2019]
    input_df['pub_date'] = [pd.NaT, pd.to_datetime('2023-04-08'), pd.to_datetime('2019-10-10')]
    expected_output_df['abstract'] = ['']
    expected_output_df['source'] = ['']
    expected_output_df['year'] = [2019]
    expected_output_df['pub_date'] = [pd.to_datetime('2019-10-10')]

    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    tm.assert_frame_equal(output_df.reset_index(drop = True), expected_output_df.reset_index(drop = True))

    # 4. No abstracts, double scopus, double max year, no sources, one max pub_date: picks scopus with max pub_date
    input_df['bib_src'] = ['scopus', 'lens', 'scopus']
    input_df['abstract'] = ['', '', '']
    input_df['source'] = ['', '', '']
    input_df['year'] = [2019, 2023, 2019]
    input_df['pub_date'] = [pd.to_datetime('2019-10-12'), pd.to_datetime('2023-04-08'), pd.to_datetime('2019-10-10')]
    expected_output_df['abstract'] = ['']
    expected_output_df['source'] = ['']
    expected_output_df['year'] = [2019]
    expected_output_df['pub_date'] = [pd.to_datetime('2019-10-12')]

    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    tm.assert_frame_equal(output_df.reset_index(drop = True), expected_output_df.reset_index(drop = True))

    # 5. No abstracts, double scopus, double max year, one source: picks scopus with that source
    input_df['bib_src'] = ['scopus', 'lens', 'scopus']
    input_df['abstract'] = ['', '', '']
    input_df['source'] = ['', '', 'S2']
    input_df['year'] = [2019, 2023, 2019]
    input_df['pub_date'] = [pd.to_datetime('2019-10-12'), pd.to_datetime('2023-04-08'), pd.to_datetime('2019-10-10')]
    expected_output_df['abstract'] = ['']
    expected_output_df['source'] = ['S2']
    expected_output_df['year'] = [2019]
    expected_output_df['pub_date'] = [pd.to_datetime('2019-10-10')]

    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    tm.assert_frame_equal(output_df.reset_index(drop = True), expected_output_df.reset_index(drop = True))

    # 6. One abstract (not scopus), double scopus, double max year, one source: picks lens with the abstract
    input_df['bib_src'] = ['scopus', 'lens', 'scopus']
    input_df['abstract'] = ['', 'abs1', '']
    input_df['source'] = ['', '', 'S2']
    input_df['year'] = [2019, 2023, 2019]
    input_df['pub_date'] = [pd.to_datetime('2019-10-12'), pd.to_datetime('2023-04-08'), pd.to_datetime('2019-10-10')]
    expected_output_df['bib_src'] = ['lens']
    expected_output_df['abstract'] = ['abs1']
    expected_output_df['source'] = ['']
    expected_output_df['year'] = [2023]
    expected_output_df['pub_date'] = [pd.to_datetime('2023-04-08')]

    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    tm.assert_frame_equal(output_df.reset_index(drop = True), expected_output_df.reset_index(drop = True))

    # 7. Like 4, but no scopus (4: no abstracts, double max year, no sources, one max pub_date): picks dims with max pub_date
    input_df['bib_src'] = ['dims', 'dims', 'lens']
    input_df['abstract'] = ['', '', '']
    input_df['source'] = ['', '', '']
    input_df['year'] = [2019, 2017, 2019]
    input_df['pub_date'] = [pd.to_datetime('2019-10-12'), pd.to_datetime('2017-04-08'), pd.to_datetime('2019-10-10')]
    expected_output_df['bib_src'] = ['dims']
    expected_output_df['abstract'] = ['']
    expected_output_df['source'] = ['']
    expected_output_df['year'] = [2019]
    expected_output_df['pub_date'] = [pd.to_datetime('2019-10-12')]

    output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
    tm.assert_frame_equal(output_df.reset_index(drop = True), expected_output_df.reset_index(drop = True))

    # 8. All other scenarios lead to random picks

    for i in range(10):
        # 8.1 No abstract, no scopus, duplicate max year, no source, two max pub_date: picks randomly from max pub_date records
        input_df['id'] = [0, 1, 2]
        input_df['bib_src'] = ['lens', 'dims', 'dims']
        input_df['abstract'] = ['', '', '']
        input_df['source'] = ['', '', '']
        input_df['year'] = [2019, 2017, 2019]
        input_df['pub_date'] = [pd.to_datetime('2019-06-12'), pd.NaT, pd.to_datetime('2019-06-12')]

        output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
        assert output_df['id'].iloc[0] in [0, 2]

        # 8.2 No abstract, no scopus, duplicate max year, two sources, two max pub_date: picks randomly from records with a source
        input_df['id'] = [0, 1, 2]
        input_df['bib_src'] = ['lens', 'dims', 'dims']
        input_df['abstract'] = ['', '', '']
        input_df['source'] = ['', 'S1', 'S2']
        input_df['year'] = [2019, 2017, 2019]
        input_df['pub_date'] = [pd.to_datetime('2019-06-12'), pd.NaT, pd.to_datetime('2019-06-12')]

        output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
        assert output_df['id'].iloc[0] in [1, 2]

        # 8.3 No abstract, no scopus, duplicate max year, no sources, no max pub_date: picks randomly from records with max year
        input_df['id'] = [0, 1, 2]
        input_df['bib_src'] = ['lens', 'dims', 'dims']
        input_df['abstract'] = ['', '', '']
        input_df['source'] = ['', '', '']
        input_df['year'] = [2023, 2023, 2019]
        input_df['pub_date'] = [pd.NaT, pd.NaT, pd.NaT]

        output_df = remove_title_duplicates(input_df).drop(columns = remove_cols)
        assert output_df['id'].iloc[0] in [0, 1]


test_merge_source_cols()
test_pub_date_year()
test_merge_bib_src_cols()
test_merge_n_cited_cols()
test_merge_fos_anzsrc_cols()
test_merge_kws_cols()
test_merge_authors_cols()
test_complex_case()


dup_1_0_row = [
    {
        'authors': "Kobayashi, T.; Hasui, K.",
        'title': "Efficient immunization strategies to prevent financial contagion",
        'abstract': "Many immunization strategies have been proposed to prevent infectious viruses from spreading through a network. In this work, we study efficient immunization strategies to prevent a default contagion that might occur in a financial network. An essential difference from the previous studies on immunization strategy is that we take into account the possibility of serious side effects. Uniform immunization refers to a situation in which banks are 'vaccinated' with a common low-risk asset. The riskiness of immunized banks will decrease significantly, but the level of systemic risk may increase due to the de-diversification effect. To overcome this side effect, we propose another immunization strategy, called counteractive immunization, which prevents pairs of banks from failing simultaneously. We find that counteractive immunization can efficiently reduce systemic risk without altering the riskiness of individual banks. 2014, Nature Publishing Group. All rights reserved.",
        'year': 2014.0,
        'pub_date': None,
        'n_cited': 18.0,
        'source': "Scientific Reports",
        'kws': "computer simulation; economic model; economic recession; financial management; human; humans; models, economic; risk management; risk sharing, financial",
        'fos': None,
        'anzsrc_2020': None,
        'auth_affils': "Kobayashi, T. (Graduate School of Economics, Kobe University, 2-1 Rokkodai, Nada, Kobe, 657-8501, Japan); Hasui, K. (Graduate School of Economics, Kobe University, 2-1 Rokkodai, Nada, Kobe, 657-8501, Japan)",
        'link': "https://dx.doi.org/10.1038/srep03834",
        'links': "https://dx.doi.org/10.1038/srep03834",
        'bib_src': "scopus",
        'scopus_id': "2-s2.0-84901042803",
        'lens_id': None,
        'dim_id': None
    }
]

dup_1_1_row = [
    {
        'authors': "Kobayashi, T.; Hasui, K.",
        'title': "Efficient immunization strategies to prevent financial contagion",
        'abstract': "Many immunization strategies have been proposed to prevent infectious viruses from spreading through a network. In this work, we study efficient immunization strategies to prevent a default contagion that might occur in a financial network. An essential difference from the previous studies on immunization strategy is that we take into account the possibility of serious side effects. Uniform immunization refers to a situation in which banks are vaccinated with a common low-risk asset. The riskiness of immunized banks will decrease significantly, but the level of systemic risk may increase due to the de-diversification effect. To overcome this side effect, we propose another immunization strategy, called counteractive immunization, which prevents pairs of banks from failing simultaneously. We find that counteractive immunization can efficiently reduce systemic risk without altering the riskiness of individual banks.",
        'year': 2014.0,
        'pub_date': '2014-01-23',
        'n_cited': 20.0,
        'source': "Scientific reports ",
        'kws': "computer simulation; economic recession; financial management; humans; models, economic; risk sharing, financial",
        'fos': "business; systemic risk; asset (economics); financial contagion; immunization (finance); financial management; monetary economics",
        'anzsrc_2020': None,
        'auth_affils': None,
        'link': "http://dx.doi.org/10.1038/srep03834",
        'links': "https://www.ncbi.nlm.nih.gov/pubmed/24452277 https://www.nature.com/srep/2014/140123/srep03834/fig_tab/srep03834_F3.html http://ui.adsabs.harvard.edu/abs/2014NatSR...4E3834K/abstract https://ci.nii.ac.jp/naid/120005600764 https://www.nature.com/articles/srep03834.pdf https://europepmc.org/article/MED/24452277 https://jglobal.jst.go.jp/en/detail?JGLOBAL_ID=201902219536149881 https://www.nature.com/articles/srep03834 https://core.ac.uk/download/41098249.pdf",
        'bib_src': "lens",
        'scopus_id': None,
        'lens_id': "003-657-516-425-014",
        'dim_id': None
    }
]

dup_1_2_row = [
    {
        'authors': "Kobayashi, T.; Hasui, K.",
        'title': "Efficient immunization strategies to prevent financial contagion",
        'abstract': "Many immunization strategies have been proposed to prevent infectious viruses from spreading through a network. In this work, we study efficient immunization strategies to prevent a default contagion that might occur in a financial network. An essential difference from the previous studies on immunization strategy is that we take into account the possibility of serious side effects. Uniform immunization refers to a situation in which banks are vaccinated with a common low-risk asset. The riskiness of immunized banks will decrease significantly, but the level of systemic risk may increase due to the de-diversification effect. To overcome this side effect, we propose another immunization strategy, called counteractive immunization, which prevents pairs of banks from failing simultaneously. We find that counteractive immunization can efficiently reduce systemic risk without altering the riskiness of individual banks.",
        'year': 2014.0,
        'pub_date': '2014-01-23',
        'n_cited': 22.0,
        'source': "scientific Reports",
        'kws': "computer simulation; economic recession; financial management; humans; models, economic; risk sharing, financial",
        'fos': "35 Commerce, Management, Tourism and Services; 3502 Banking, Finance and Investment; 38 Economics; 3801 Applied Economics",
        'anzsrc_2020': None,
        'auth_affils': "Kobayashi, T. (Graduate School of Economics, Kobe University, 2-1 Rokkodai, 657-8501, Nada, Kobe, Japan); Hasui, K. (Graduate School of Economics, Kobe University, 2-1 Rokkodai, 657-8501, Nada, Kobe, Japan)",
        'link': "https://www.nature.com/articles/srep03834.pdf",
        'links': "https://www.nature.com/articles/srep03834.pdf",
        'bib_src': "dims",
        'scopus_id': None,
        'lens_id': None,
        'dim_id': "pub.1041874688"
    }
]

dup_2_0_row = [
    {
        'authors': "Laskin, D.M.",
        'title': "Should prophylactic antibiotics be used for patients having removal of erupted teeth",
        'abstract': "Generally, antibiotics should not be required before the removal of erupted carious or periodontally involved teeth unless a significant risk of postoperative infection is present. The decision to use prophylactic antibiotics in noninfected cases should also be based on whether patients have any significant medical risk factors that could adversely affect their humoral and cellular defense mechanisms, and whether any systemic risks are associated with the bacteremia that accompanies tooth extraction. This article discusses the various indications for using prophylactic antibiotics in patients having erupted teeth extracted based on a consideration of these factors. 2011 Elsevier Inc.",
        'year': 2011.0,
        'pub_date': None,
        'n_cited': 6.0,
        'source': "Oral and Maxillofacial Surgery Clinics of North America",
        'kws': "antibiotic prophylaxis; bacteremia; dental caries; erupted tooth; focal infection, dental; human; humans; immunocompromised host; immunocompromised patient; infection; periodontal disease; periodontal diseases; postextraction infection; prophylactic antibiotics; prosthesis-related infections; review; risk factor; risk factors; surgical infection; surgical wound infection; tooth extraction; tooth infection; tooth removal",
        'fos': None,
        'anzsrc_2020': None,
        'auth_affils': "Laskin, D.M. (Department of Oral and Maxillofacial Surgery VCU, School of Dentistry, VCU Medical Center, 521 North 11th St., PO Box 980566, Richmond, VA 23298-0566, United States)",
        'link': "https://dx.doi.org/10.1016/j.coms.2011.07.006",
        'links': "https://dx.doi.org/10.1016/j.coms.2011.07.006",
        'bib_src': "scopus",
        'scopus_id': "2-s2.0-80053579003",
        'lens_id': None,
        'dim_id': None
    }
]

dup_2_1_row = [
    {
        'authors': "Laskin, D.M.",
        'title': "Should prophylactic antibiotics be used for patients having removal of erupted teeth",
        'abstract': "Generally, antibiotics should not be required before the removal of erupted carious or periodontally involved teeth unless a significant risk of postoperative infection is present. The decision to use prophylactic antibiotics in noninfected cases should also be based on whether patients have any significant medical risk factors that could adversely affect their humoral and cellular defense mechanisms, and whether any systemic risks are associated with the bacteremia that accompanies tooth extraction. This article discusses the various indications for using prophylactic antibiotics in patients having erupted teeth extracted based on a consideration of these factors.",
        'year': 2011.0,
        'pub_date': "2011-11",
        'n_cited': 7.0,
        'source': "Oral and maxillofacial surgery clinics of North  America   ",
        'kws': "antibiotic prophylaxis; bacteremia; dental caries; focal infection, dental; humans; immunocompromised host; periodontal diseases; prosthesis-related infections; risk factors; surgical wound infection; tooth extraction",
        'fos': "32 Biomedical and Clinical Sciences; 3203 Dentistry",
        'anzsrc_2020': None,
        'auth_affils': "Laskin, D.M. (Department of Oral and Maxillofacial Surgery VCU School of Dentistry and VCU Medical Center, 521 North 11th Street, PO Box 980566, Richmond, VA 23298-0566, USA)",
        'link': None,
        'links': None,
        'bib_src': "dims",
        'scopus_id': None,
        'lens_id': None,
        'dim_id': "pub.1032068830"
    }
]

dup_3_1_df = [
    {
        'authors': "Celebi, A.R.C.; Kadayifcilar, S.; Eldem, B.",
        'title': "Hyperbaric oxygen therapy in branch retinal artery occlusion in a 15-year-old boy with methylenetetrahydrofolate reductase mutation",
        'abstract': "Purpose. To report the efficacy of hyperbaric oxygen (HBO) therapy in a case of branch retinal artery occlusion (BRAO) in a 15-year-old boy. Methods. We report a 15-year-old boy with sudden loss of vision due to BRAO. Examination included laboratory evaluation for systemic risk factors. Follow-up exams included visual acuity, fundus examination, fundus fluorescein angiography, and visual field testing. HBO therapy was employed for treatment. Medical history was positive for isolated glucocorticoid deficiency. Laboratory evaluation disclosed hyperhomocysteinemia and methylenetetrahydrofolate reductase (MTHFR) mutation. The visual acuity 0.05 at presentation improved to 0.8 after 20 days of HBO therapy. There was no change on visual fields. Conclusion. In this pediatric case, HBO therapy was useful in the treatment of BRAO.",
        'year': 2015.0,
        'pub_date': "2015-02-05",
        'n_cited': 2.0,
        'source': "Case Reports in Ophthalmological Medicine",
        'kws': None,
        'fos': "32 Biomedical and Clinical Sciences; 3212 Ophthalmology and Optometry",
        'anzsrc_2020': None,
        'auth_affils': "Celebi, A.R.C. (Department of Ophthalmology, Acibadem University School of Medicine, 34303 Istanbul, Turkey); Kadayifcilar, S. (Department of Ophthalmology, Hacettepe University School of Medicine, Ankara, Turkey); Eldem, B. (Department of Ophthalmology, Hacettepe University School of Medicine, Ankara, Turkey)",
        'link': "http://downloads.hindawi.com/journals/criopm/2015/640247.pdf",
        'links': "http://downloads.hindawi.com/journals/criopm/2015/640247.pdf",
        'bib_src': "dims",
        'scopus_id': None,
        'lens_id': None,
        'dim_id': "pub.1007905354"
    }
]