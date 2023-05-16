import pandas as pd
import re

from typing import List, Union
from config import *
from co_terms import *


def extract_search_terms(search_terms_str: str) -> List[str]:

    search_terms = [term.strip() for term in re.split(r'\b(?:OR|AND)\b', search_terms_str) if term.strip()]
    search_terms = [re.sub(r'[a-zA-Z-]+\s*:?\(', '', term) for term in search_terms]
    search_terms = [re.sub(r'[\*\"\(\)]|not|NOT', '', term).strip() for term in search_terms if term.strip()]
    search_terms = list(set(search_terms))

    return search_terms


def expand_with_synonyms(terms: List[str]):
    '''
        FIXME: This currently adds keywords that got nothing to do with the topic.
        One possible way around this is to only add a synonym if it is somewhere 
        in a relevant corpus. This might be the keywords or the nouns in the title
        or abstracts. The synonyms that were tested should be added to a dictionary 
        for faster checking and only synonyms that weren't checked yet would be 
        tested aginst the corpus. Also: limit the synonyms that are included to nouns.
    '''

    expanded_terms = []

    for term in terms:
        synonyms = Word(term).synsets

        # Create a list of the synonyms, include the term, and add to expanded_terms
        term_and_synonyms = list(set([term] + [syn.lemma_names()[0] for syn in synonyms]))      # type: ignore - Pylance: "cached_property" is not iterable
        expanded_terms += term_and_synonyms

    return expanded_terms


def add_search_term_matches_as_col(biblio_df: pd.DataFrame,
                                 cols: List,
                                 search_terms: Union[str, List[str]],
                                 full_matches: List[str],
                                 singularise: bool = False,
                                 expand_synonyms: bool = False,
                                 stem: bool = False
                                 ) -> pd.DataFrame:
    '''
    
        Make sure to remove any strings that are not search terms and that are
        not in the removal lists in config.py
    '''
    
    if any(string not in biblio_df.columns for string in cols):
        raise ValueError(f"Some columns in {cols} are not in biblio_df")
    
    # If a search string from Scopus, Lens, or Dimensions is provided, extract the search terms
    if isinstance(search_terms, str):
        search_terms = extract_search_terms(search_terms_str = search_terms)

    # Replace '-' with whitespace in search_terms
    search_terms = [search_term.replace('-', ' ') for search_term in search_terms]

    # Remove the full_search_terms from the search terms list so that later the titles and 
    # abstracts only match the complete words from the full_search_terms list
    filter_set = set(full_matches)
    target_set = set(search_terms)
    search_terms = list(target_set - filter_set)

    # Singularise the terms
    if singularise:
        search_terms = singularize_terms(search_terms)

    # Expand the search_terms with synonyms
    if expand_synonyms:
        search_terms = expand_with_synonyms(search_terms)

    # Stem the terms in term_df
    if stem:
        search_terms = stem_terms(search_terms)

    search_terms = sorted(search_terms)


    # Create a list with the strings in search_terms and full_search_terms that 
    # are in the text (title, abstract,...) in the row and col of a dataframe
    def filter_strings_by_sentence(row:pd.Series, col, strings: List[str]):

        row_num = pd.RangeIndex(len(row)).get_loc(row.name)

        if(row_num % 100 == 0): # print row index
            print(f'{row_num}', end = '\r')

        # 'title' or 'abstract'
        value = row[col]
        
        if not pd.isna(value):
            sentence = value.lower()
            sentence = sentence.replace('-', ' ')

            matches = [string for string in full_matches if re.search(r'(?i)\b' + string +r'\b', sentence)]
            matches += [string for string in search_terms if re.search(r'(?i)\b' + string, sentence)]
        else:
            matches = []
        
        return matches


    biblio_df['search_terms'] = [[]] * len(biblio_df)  # Create an empty 'search_terms' column

    for col in cols:

        logger.info(f'Extracting search terms from {col}...')

        biblio_df['search_terms'] += biblio_df.apply(lambda row: filter_strings_by_sentence(row, col, search_terms), axis = 1)
        biblio_df['search_terms'] = biblio_df['search_terms'].apply(lambda lst: sorted(set(lst)))


    return biblio_df


    # # TODO Add the keyword matches so that we don't remove publications (see below) that have no title and abstract match but that have a keyword match
    # # if logger.getEffectiveLevel() == logging.INFO: print(f'\nExtracting search terms from keywords...')
    # # biblio_df['search_kws'] = biblio_df.apply(lambda row: filter_strings_by_sentence(row, 'kws'), axis = 1)

    # # Number of publications before applying the search term filter to titles and abstracts. You can apply a 
    # # subset of the original search terms if you want to remove pulications that only contain search terms not
    # # in the subset. Sometimes this is useful when some of the search terms turn out to be adding many 
    # # publications that are not relevant.
    # n_pubs = len(biblio_df)

    # # Replace the stemmed search terms in columns 'search_title' and 'search_abstract' with the original search terms
    # mapping = dict(zip(search_terms, search_terms))   # create a dictionary that maps values in A to their corresponding values in B

    # def replace_values(lst):    # replace values in a list using the mapping dictionary
    #     return [mapping.get(x, x) for x in lst]

    # biblio_df[['search_title', 'search_abs']] = biblio_df[['search_title', 'search_abs']].applymap(replace_values)

    # # FIXME This is a little dodgy since it might remove publciations that were matched by the Scopus or Lens search engine but that for some reason aren't matched here
    # # Remove publications where search_title and search_abs are empty lists. This happens when you remove search terms from the 
    # # biblio_search_term string, for instance terms that turn out to generate a lot of irrelevant publications.
    # print(f"Removing {len(biblio_df[~biblio_df[['search_title', 'search_abs']].apply(lambda x: any(x.apply(bool)), axis=1)])} \
    #     publications where search_title and search_abs are empty...")
    # biblio_df = biblio_df[biblio_df[['search_title', 'search_abs']].apply(lambda x: any(x.apply(bool)), axis=1)]

    # n_pubs_filtered = len(biblio_df)

    # logger.info(f'Retained {n_pubs_filtered} of {n_pubs} publications.')