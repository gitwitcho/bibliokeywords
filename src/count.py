import pandas as pd
import cmd

from typing import List, Dict
from IPython.core.display import HTML
from tqdm import tqdm
from textblob import Word

from clean import *
from filter import *
from language import singularise_terms, stem_terms


def stack_keyword_count_dfs(keywords_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Stacks the keyword-count DataFrames horizontally into a single DataFrame. This is 
    mainly useful for writing the various keyword-count DataFrames into a single 
    Excel spreadsheet for inspection and further use.

    Args:
        keywords_dict: A dictionary where keys are identifiers and values are DataFrames 
                       with keyword-count information.

    Returns:
        pd.DataFrame: The horizontally stacked DataFrame.

    Note:
        The DataFrames in `keywords_dict` are allowed to have different number of rows.
    """

    # Get the maximum number of rows across all the DataFrames
    max_rows = max(df.shape[0] for df in keywords_dict.values())
    
    # stacked_df = pd.DataFrame(index = range(max_rows))

    # # Set unique column names across the DataFrames
    # for key, df in keywords_dict.items():
    #     new_column_names = {df.columns[0]: key, df.columns[1]: key + '_count'}
    #     df.rename(columns = new_column_names, inplace = True)

    # # Store the keyword DataFrames in a list
    # kws_df_list = list(keywords_dict.values())

    # Create a list of keyword DataFrames with unique column names
    updated_dfs = []

    for key, df in keywords_dict.items():
        updated_df = df.copy()  # Create a copy to avoid modifying the original DataFrame
        updated_df.columns = [key, key + '_count']
        updated_df.reset_index(drop = True, inplace = True)
        updated_dfs.append(updated_df)

    # Concatenate the keyword dataframes horizontally
    # stacked_df = pd.concat([df.reindex(range(max_rows)) for df in kws_df_list], axis = 1)
    stacked_df = pd.concat(updated_dfs, axis=1)

    return stacked_df


def generate_keyword_stats(biblio_df_: pd.DataFrame,
                           cols: List,
                           assoc_filter: Optional[str],
                           singularise: bool = False,
                           stem: bool = False
                           ) -> Dict:
    
    if any(string not in biblio_df_.columns for string in cols):
        raise ValueError(f"Some columns in {cols} are not in biblio_df")
    
    kws_df = biblio_df_[cols].copy()
    kws_count_df_dict = {}
    kws_assoc_count_df_dict = {}
    
    for col in cols:

        # Create a single keyword list by exploding the table
        kws_col_df= kws_df.fillna('').apply(lambda x: x.str.split(';'))  
        
        # Singularise keywords
        if singularise:
            tqdm.pandas(desc = f"Singularising the keywords in '{col}'")   # lots of cool paramiters you can pass here. 
            kws_col_df[col] = kws_col_df[col].progress_apply(singularise_terms)
            # kws_col_df[col] = kws_col_df[col].apply(singularise_terms)

        # Stem keywords
        if stem:
            tqdm.pandas(desc = f"Stemming the keywords in '{col}'")   # lots of cool paramiters you can pass here. 
            kws_col_df[col] = kws_col_df[col].progress_apply(stem_terms)
            # kws_col_df[col] = kws_col_df[col].apply(stem_terms)
        
        kws_col_df[col] = kws_col_df[col].apply(lambda x: list(set(x)))
        kws_col_df = kws_col_df.explode(col).reset_index(drop=True)

        kws_col_df = kws_col_df.apply(lambda x: x.str.strip())

        kws_col_df = kws_col_df[kws_col_df[col].str.strip() != '']
        kws_col_df[col] = kws_col_df[col].str.replace('-', ' ')


        # Create a count table for the keywords
        kw_count_df = kws_col_df[col].value_counts().reset_index()
        kw_count_df.columns = ['kw', 'count']
        kw_count_df = kw_count_df.sort_values(by = ['count', 'kw'], ascending = [False, True]).reset_index(drop = True)

        kws_count_df_dict[col] = kw_count_df

        if assoc_filter:
            if not '{}' in assoc_filter:
                raise ValueError(f"The assoc_filter needs to include place holders '{{}}' for the keyword column")
            
            kw_assoc_count_df = filter_biblio_df(biblio_df_= kw_count_df,
                                                 query_str = assoc_filter.format('kw'))
            kws_count_df_dict[col + '_assoc'] = kw_assoc_count_df

    return kws_count_df_dict


def write_keyword_count_to_console(keywords_dict: Dict[str, pd.DataFrame],
                                   max_n_rows: int = 0,
                                   display_width: int = 120
                                   ) -> None:
    """
    Write keyword-count pairs to the console in a multi-column format.

    Args:
        keywords_dict: A dictionary where keys are keyword collection names and values
                       are DataFrames with keywords and keyword counts.
        max_n_rows: The maximum number of rows to display. Keywords that don't fit into the 
                    rows x columns matrix are cut off. If max_n_rows = 0, then no cutoff is applied.
        display_width: The width of the console display.

    Returns:
        None
    """

    cli = cmd.Cmd()

    for col, kw_count_df in keywords_dict.items():
 
        # Create the list of keyword-count pairs
        kw_count_str_list = kw_count_df.apply(lambda row: str(row['kw']) + ' (' + str(row['count']) + ')', axis=1).tolist()
        total_n_keywords = len(kw_count_str_list)

        # Adjust the list to the available display width and the given maximum number of rows
        cumulative_str_lengths = [sum(len(string) for string in kw_count_str_list[:i+1]) for i in range(len(kw_count_str_list))]

        # If max_n_rows > 0, then remove the excess keywords. If 0, then keep all the keywords
        if max_n_rows > 0:
            max_characters = max_n_rows * display_width
            cutoff_idx = max((i for i, num in enumerate(cumulative_str_lengths) if num < max_characters), default = 0)
            kw_count_str_list = kw_count_str_list[:cutoff_idx]

        # Print the result
        print(f"\nKeywords for column '{col}'")
        print(f"Displaying {len(kw_count_str_list)} keywords of a total of {total_n_keywords}")
        print("-------------------------------------------")
        cli.columnize(kw_count_str_list, displaywidth = display_width)  # neat function to print a list of values to a compact column
        print("-------------------------------------------")

    return


def create_keyword_count_html(keywords_dict: Dict,
                              n_cols: int,
                              max_n_rows: int) -> HTML:
    
    kws_html_str = ''

    for col, kw_count_df in keywords_dict:

        kw_count_str_list = kw_count_df.apply(lambda row: str(row['kw']) + ' (' + str(row['count']) + ')', axis=1).tolist()

        # Calculate the number of rows in the table
        n_rows = len(kw_count_str_list) // n_cols + (len(kw_count_str_list) % n_cols > 0)
        num_rows_all = n_rows

        # Row cutoff
        if n_rows > max_n_rows:
            n_rows = max_n_rows

        # Create an HTML string to display the list of strings in a table
        kws_html_str = "<h3>Keywords for column '{col}'"
        kws_html_str += f"Total number of '{col}' keywords: {len(kw_count_str_list)}"
        kws_html_str += f"Displaying {n_rows} rows of a total of {max_n_rows}"
        kws_html_str += '<table style="width:100%;">'
        for j in range(n_cols):
            kws_html_str += '<td style="vertical-align:top;">'
            for i in range(n_rows):
                idx = j * n_rows + i
                if idx < len(kw_count_str_list) and kw_count_str_list[idx]:
                    kws_html_str += f'{kw_count_str_list}<br>'
            kws_html_str += '</td>'
        kws_html_str += '</table>'
        kws_html_str += '<br><br>'
        
    return HTML(kws_html_str)


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
        search_terms = singularise_terms(search_terms)

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