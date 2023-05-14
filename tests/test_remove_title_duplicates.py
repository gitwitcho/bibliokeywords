import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pandas as pd
import numpy as np
from datetime import datetime
from transform import remove_title_duplicates


# def compare_dataframes(df1, df2):
#     """
#     Compares two DataFrames element by element.

#     Returns True if the DataFrames are equal, False otherwise.
#     """
#     # Check if the shape and column names are the same
#     if df1.shape != df2.shape or set(df1.columns) != set(df2.columns):
#         return False

#     # Check if each element in the DataFrames is equal
#     for column in df1.columns:
#         if not np.array_equal(df1[column], df2[column]):
#             return False

#     # If all elements are equal, the DataFrames are equal
#     return True


def test_remove_title_duplicates():

    # Test case 1: No duplicates, returns the original DataFrame with the added column 'bib_srcs'
    df = pd.DataFrame({'title': ['Publication A1', 'Publication B1'], 
                       'year': [2021, 2022],
                       'bib_src': ['scopus', 'pubmed'],
                       'abstract': ['Abstract A', 'Abstract B'],
                       'pub_date': [datetime(2021, 1, 1), datetime(2022, 1, 1)]})
    expected_df = pd.DataFrame({'title': ['Publication A1', 'Publication B1'], 
                       'year': [2021, 2022],
                       'bib_src': ['scopus', 'pubmed'],
                       'abstract': ['Abstract A', 'Abstract B'],
                       'pub_date': [datetime(2021, 1, 1), datetime(2022, 1, 1)],
                       'bib_srcs': ['scopus', 'pubmed']})
    output_df, _ = remove_title_duplicates(df)
    expected_df.reset_index(drop = True, inplace = True)
    output_df.reset_index(drop = True, inplace = True)
    assert output_df.equals(expected_df)

    # Test case 2: Two duplicates, one without abstract. Should keep the one with abstract.
    df = pd.DataFrame({'title': ['Publication A2', 'Publication A2'],
                       'year': [2021, 2022],
                       'bib_src': ['scopus', 'pubmed'],
                       'abstract': [np.nan, 'Abstract A2'],
                       'pub_date': [datetime(2021, 1, 1), datetime(2022, 10, 4)]})
    expected_df = pd.DataFrame({'title': ['Publication A2'], 
                                'year': [2022], 
                                'bib_src': ['pubmed'],
                                'abstract': ['Abstract A2'], 
                                'pub_date': [datetime(2022, 10, 4)],
                                'bib_srcs':['scopus, pubmed']})
    output_df, _ = remove_title_duplicates(df)
    expected_df.reset_index(drop = True, inplace = True)
    output_df.reset_index(drop = True, inplace = True)
    assert output_df.equals(expected_df)
    
    # Test case 3: Two duplicates with abstract, one from Scopus. Should retain the one from Scopus.
    df = pd.DataFrame({'title': ['Publication A3', 'Publication A3'],
                       'year': [2023, 2021],
                       'bib_src': ['pubmed', 'scopus'],
                       'abstract': ['Abstract A3', 'Abstract A3'],
                       'pub_date': [datetime(2023, 1, 1), datetime(2021, 1, 1)]})
    expected_df = pd.DataFrame({'title': ['Publication A3'],
                                'year': [2021],
                                'bib_src': ['scopus'],
                                'abstract': ['Abstract A3'],
                                'pub_date': [datetime(2021, 1, 1)],
                                'bib_srcs':['pubmed, scopus']})
    output_df, _ = remove_title_duplicates(df)
    expected_df.reset_index(drop = True, inplace = True)
    output_df.reset_index(drop = True, inplace = True)
    assert output_df.equals(expected_df)
    
    # Test case 4: Two duplicates from Scopus, should keep the one with latest year
    df = pd.DataFrame({'title': ['Publication A4', 'Publication A4'],
                       'year': [2021, 2022],
                       'bib_src': ['scopus', 'scopus'],
                       'abstract': ['Abstract A4', 'Abstract A4'],
                       'pub_date': [datetime(2021, 1, 1), datetime(2022, 1, 1)]})
    expected_df = pd.DataFrame({'title': ['Publication A4'],
                                'year': [2022],
                                'bib_src': ['scopus'],
                                'abstract': ['Abstract A4'],
                                'pub_date': [datetime(2022, 1, 1)],
                                'bib_srcs':['scopus']})
    output_df, _ = remove_title_duplicates(df)
    expected_df.reset_index(drop = True, inplace = True)
    output_df.reset_index(drop = True, inplace = True)
    assert output_df.equals(expected_df)
    
    # Test case 5: Two duplicates, none from Scopus, one missing pub_date. Should infer the pub_date from the year and insert it into biblio_df. Should keep the one with the most recent pub_date.
    df = pd.DataFrame({'title': ['Publication A5', 'Publication A5'],
                       'year': [2021, 2022],
                       'bib_src': ['dims', 'lens'],
                       'abstract': ['Abstract A5', 'Abstract A5'],
                       'pub_date': [datetime(2021, 1, 1), pd.NaT]})
    expected_df = pd.DataFrame({'title': ['Publication A5'],
                                'year': [2022],
                                'bib_src': ['lens'],
                                'abstract': ['Abstract A5'],
                                'pub_date': [pd.NaT],
                                'bib_srcs':['dims, lens']})
    output_df, _ = remove_title_duplicates(df)
    expected_df.reset_index(drop = True, inplace = True)
    output_df.reset_index(drop = True, inplace = True)
    assert output_df.equals(expected_df)
    
    
    # Test case 6: Two duplicates, none from Scopus, one missing year. Should infer the year from the pub_date and insert it into biblio_df. Should keep the one with the latest pub_date
    df = pd.DataFrame({'title': ['Publication A6', 'Publication A6'],
                       'year': [2016, np.nan],
                       'bib_src': ['lens', 'dims'],
                       'abstract': ['Abstract A6', 'Abstract A6'],
                       'pub_date': [datetime(2016, 1, 1), datetime(2019, 12, 1)]})
    expected_df = pd.DataFrame({'title': ['Publication A6'],
                                'year': [2019],
                                'bib_src': ['dims'],
                                'abstract': ['Abstract A6'],
                                'pub_date': [datetime(2019, 12, 1)],
                                'bib_srcs':['lens, dims']})
    output_df, _ = remove_title_duplicates(df)
    expected_df.reset_index(drop = True, inplace = True)
    output_df.reset_index(drop = True, inplace = True)
    assert output_df.equals(expected_df)
    
    
    # Test case 7: Two duplicates, none from Scopus, both abstracts are missing. Should pick the one with the latest date
    df = pd.DataFrame({'title': ['Publication A7', 'Publication A7'],
                       'year': [2016, np.nan],
                       'bib_src': ['lens', 'dims'],
                       'abstract': [np.nan, np.nan],
                       'pub_date': [datetime(2016, 1, 1), datetime(2019, 12, 1)]})
    expected_df = pd.DataFrame({'title': ['Publication A7'],
                                'year': [2019],
                                'bib_src': ['dims'],
                                'abstract': [np.nan],
                                'pub_date': [datetime(2019, 12, 1)],
                                'bib_srcs':['lens, dims']})
    output_df, _ = remove_title_duplicates(df)
    expected_df.reset_index(drop = True, inplace = True)
    output_df.reset_index(drop = True, inplace = True)
    assert output_df.equals(expected_df)

    # Test case 8: Two duplicates, none from Scopus, one has both the year and the pub_date missing. Should pick the other one.
    df = pd.DataFrame({'title': ['Publication A8', 'Publication A8'],
                       'year': [2016, np.nan],
                       'bib_src': ['lens', 'dims'],
                       'abstract': ['Abstract A8', np.nan],
                       'pub_date': [datetime(2016, 12, 1), np.nan]})
    expected_df = pd.DataFrame({'title': ['Publication A8'],
                                'year': [2016],
                                'bib_src': ['lens'],
                                'abstract': ['Abstract A8'],
                                'pub_date': [datetime(2016, 12, 1)],
                                'bib_srcs':['lens']})
    output_df, _ = remove_title_duplicates(df)
    expected_df.reset_index(drop = True, inplace = True)
    output_df.reset_index(drop = True, inplace = True)
    assert output_df.equals(expected_df)

    # Test case 9: Two duplicates, one from Scopus, for both the years and the pub_date are missing. Should pick none.
    df = pd.DataFrame({'title': ['Publication A9', 'Publication A9'],
                       'year': [np.nan, np.nan],
                       'bib_src': ['lens', 'dims'],
                       'abstract': ['Abstract A9', np.nan],
                       'pub_date': [np.nan, np.nan]})
    expected_df = pd.DataFrame({'title': [],
                                'year': [],
                                'bib_src': [],
                                'abstract': [],
                                'pub_date': [],
                                'bib_srcs':[]})
    output_df, _ = remove_title_duplicates(df)
    expected_df.reset_index(drop = True, inplace = True)
    output_df.reset_index(drop = True, inplace = True)
    assert output_df.empty
    
    # Test case 10: Two exact duplicates. It just keeps the first one.
    df = pd.DataFrame({'title': ['Publication A10', 'Publication A10'],
                       'year': [2021, 2021],
                       'bib_src': ['scopus', 'scopus'],
                       'abstract': ['Abstract A10', 'Abstract A10'],
                       'pub_date': [datetime(2021, 1, 1), datetime(2021, 1, 1)]})
    expected_df = pd.DataFrame({'title': ['Publication A10'],
                                'year': [2021],
                                'bib_src': ['scopus'],
                                'abstract': ['Abstract A10'],
                                'pub_date': [datetime(2021, 1, 1)],
                                'bib_srcs':['scopus']})
    output_df, _ = remove_title_duplicates(df)
    expected_df.reset_index(drop = True, inplace = True)
    output_df.reset_index(drop = True, inplace = True)
    assert output_df.equals(expected_df)
    
    # Test case 11: Two duplicates with identical pub_date, none is Scopus. Picks one at random.
    df = pd.DataFrame({'title': ['Publication A11', 'Publication A11'],
                       'year': [2021, 2021],
                       'bib_src': ['lens', 'dims'],
                       'abstract': ['Abstract A11', 'Abstract B11'],
                       'pub_date': [datetime(2021, 1, 1), datetime(2021, 1, 1)]})
    assert True

    # Test case 12: Two duplicates with identical pub_date, none is Scopus. Picks the one that has a source.
    df = pd.DataFrame({'title': ['Publication A12', 'Publication A12'],
                       'year': [2021, 2021],
                       'bib_src': ['lens', 'dims'],
                       'abstract': ['Abstract A12', 'Abstract B12'],
                       'pub_date': [datetime(2021, 1, 1), datetime(2021, 1, 1)],
                       'source': [np.nan, 'Journal of Philosophy']})
    expected_df = pd.DataFrame({'title': ['Publication A12'],
                                'year': [2021],
                                'bib_src': ['dims'],
                                'abstract': ['Abstract B12'],
                                'pub_date': [datetime(2021, 1, 1)],
                                'source': ['Journal of Philosophy'],
                                'bib_srcs':['lens, dims'],
                                'sources': ['Journal of Philosophy']})
    output_df, _ = remove_title_duplicates(df)
    expected_df.reset_index(drop = True, inplace = True)
    output_df.reset_index(drop = True, inplace = True)
    assert output_df.equals(expected_df)

    # Test case 13: Two duplicates. Tests the creating of new columns and the merging.
    df = pd.DataFrame({'title': ['P13', 'P13', 'P13'],
                       'year': [2021, 2021, 2021],
                       'bib_src': ['scopus', 'lens', 'scopus'],
                       'abstract': ['AA13', 'AB13', 'AC13'],
                       'pub_date': [datetime(2021, 1, 1), datetime(2021, 1, 1), datetime(2021, 1, 1)],
                       'n_cited': [5, 12, np.nan],
                       'fos': ['A;B;C', 'B;C;D;E;F', 'A;C;F;G;H;I'],
                       'anzsrc_2020': ['A;B;C', 'D;E;F', 'A;C;F;G;H;I'],
                       'kws': ['A;B;C', np.nan, 'G'],
                       'links': ['A B C', 'B C D E F', 'A C F G H I'],
                       'author_affils': ['AFF1', np.nan, 'AFF1']})
    expected_df = pd.DataFrame({'title': ['P13'],
                                'year': [2021],
                                'bib_src': ['scopus'],
                                'abstract': ['AA13'],
                                'pub_date': [datetime(2021, 1, 1)],
                                'n_cited': [17],
                                'fos': ['A; B; C; D; E; F; G; H; I'],
                                'anzsrc_2020': ['A; B; C; D; E; F; G; H; I'],
                                'kws': ['a; b; c; g'],
                                'links': ['A B C D E F G H I'],
                                'author_affils': ['AFF1'],
                                'bib_srcs':['scopus, lens']})
    output_df, _ = remove_title_duplicates(df)
    expected_df.reset_index(drop = True, inplace = True)
    output_df.reset_index(drop = True, inplace = True)
    assert output_df.equals(expected_df)

# test_remove_title_duplicates()