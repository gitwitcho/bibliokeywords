import pandas as pd
import re

from typing import List, Optional, Union, Dict
from config import *
from utilities import *


def reshape_cols_biblio_df(biblio_df: pd.DataFrame,
                      reshape_base: Optional[Reshape] = None,
                      reshape_filter: Optional[Union[Dict,List]] = None
                      ) -> pd.DataFrame:
    
    root_dir = get_root_dir()

    if reshape_base:
        if not all(col in biblio_df.columns for col in reshape_strucs[reshape_base.value].keys()):
            raise ValueError(f"One or more columns not found in biblio_df: {reshape_strucs[reshape_base.value]}")
        biblio_df = biblio_df[list(reshape_strucs[reshape_base.value].keys())].rename(columns = reshape_strucs[reshape_base.value])

    if reshape_filter:
        if isinstance(reshape_filter, List):
            if not all(col in biblio_df.columns for col in reshape_filter):
                raise ValueError(f"One or more columns not found in biblio_df: {reshape_filter}")
            biblio_df = biblio_df[reshape_filter]
        elif isinstance(reshape_filter, Dict):
            if not all(col in biblio_df.columns for col in reshape_filter.keys()):
                raise ValueError(f"One or more columns not found in biblio_df: {reshape_filter}")
            biblio_df = biblio_df[list(reshape_filter.keys())].rename(columns = reshape_filter)


    # if output_file and output_dir and project:
    #     logger.info(f"Writing biblio_df to file {output_file}")
    #     output_path = Path(root_dir, data_root_dir, project, output_dir, output_file)
        
    #     if Path(output_file).suffix == '.csv':
    #         biblio_df.to_csv(output_path, index = False)
    #     elif Path(output_file).suffix == '.xlsx':
    #         biblio_df.to_excel(output_path, index = False)
    # elif not all([project, output_dir, output_file]) and any([project, output_dir, output_file]):
    #     raise ValueError("You need to provide all three values for project, output_file, and output_dir if you want to write the output to a file")

    return biblio_df


def add_search_label(biblio_df: pd.DataFrame,
                     search_label: str) -> pd.DataFrame:
    biblio_df['search_label'] = search_label
    return biblio_df


def remove_title_duplicates(biblio_df: pd.DataFrame):

    # Create a copy of the input DataFrame
    biblio_df_copy = biblio_df.copy()

    # Group the rows by the titles and loop over the groups
    for _, group in biblio_df_copy.groupby('title'):

        # Identify the duplicates within this group
        duplicates = group.duplicated(subset = 'title', keep = False)

        # Apply the rules to decide which item to keep within this group
        # Here's an example of a rule: keep the item with the longest abstract
        item_to_keep = group.sort_values('abstract', ascending=False).iloc[0]
        
        # Drop the other items from the copy of the DataFrame
        items_to_drop = group[duplicates].drop(item_to_keep.name)
        biblio_df_copy = biblio_df_copy.drop(items_to_drop.index)

    # Return the deduplicated DataFrame
    return biblio_df_copy


def clean_biblio_df(biblio_df: pd.DataFrame,
                    biblio_type: BiblioType
                    ) -> pd.DataFrame:
    
    logger.info(f'Number of publications in the input biblio_df: {len(biblio_df)}')


    """
        Cleaning the publication titles
    """

    # Remove publications with empty titles
    count_titles_empty = len(biblio_df[biblio_df['title'] == ''])
    biblio_df = biblio_df[biblio_df['title'] != '']
    print(f'Removed {count_titles_empty} titles that were empty strings')

    # Remove all titles that are NaN
    count_titles_nan = biblio_df['title'].isna().sum()
    biblio_df = biblio_df.dropna(subset = ['title'])
    print(f'Removed {count_titles_nan} titles that were NaN')

    # Remove all titles that contain 'conference', 'workshop', or 'proceedings'
    count_procs = len(biblio_df[biblio_df['title'].str.contains('proceedings|conference|workshop', case = False)])
    biblio_df = biblio_df[~biblio_df['title'].str.contains('proceedings|conference|workshop', case = False)]
    print(f'Removed {count_procs} records where the title contained "conference", "workshop", or "proceeding"')

    # Convert the titles to lower case except for the first word
    def title_to_lc(s):
        words = s.split()
        words = [words[0]] + [w.lower() if w[0].isupper() and len(w) > 1 and w[1].isalpha() and not w[1].isupper() else w for w in words[1:]]
        return ' '.join(words)

    biblio_df['title'] = biblio_df['title'].apply(title_to_lc)

    # Remove text between '<' and '>' characters
    biblio_df['title'] = biblio_df['title'].str.replace(r'<.*?>', '', regex = True)

    # Remove all non-alphabetic characters except for '-', ',', ':', ')', '(', '$', '%',  whitespace and Greek letters
    biblio_df['title'] = biblio_df['title'].apply(lambda x: re.sub(r'[^a-zA-Z0-9α-ωΑ-Ω\s,:’()$%\'\"\-]+', ' ', x))

    # Replace any special whitespace character with a normal whitespace
    biblio_df['title'] = biblio_df['title'].str.replace(r'\u2002|\u2003|\u2005|\u2009|\u200a|\u202f|\xa0', ' ', regex = True)

    # Replace all newline and tab characters with a white space
    biblio_df['title'] = biblio_df['title'].str.replace(r'\n|\t', ' ', regex = True)

    # Remove the word 'abstract' at the start of any title
    biblio_df['title'] = biblio_df['title'].str.replace(r'^(?i)abstract\s*', '', regex = True)

    # Remove words from the beginning of the title that are combinations of at least one number and zero or more special charcters
    biblio_df['title'] = biblio_df['title'].apply(lambda x: re.sub(r'^[\W\d]+(?=\s)', '', x))

    # Remove any words starting with '.' or '-' and any single letter except 'a' from the beginning of the title and abstract
    biblio_df['title'] = biblio_df['title'].str.replace(r'^[-.]+\s*\w+\s*|[-.]+(?!\w)|(\s|^)[^Aa\s+](\s+|$)', '', regex = True)

    # Remove excess whitespace
    biblio_df['title'] = biblio_df['title'].str.replace('\s+', ' ', regex = True).str.strip()

    # Remove any remaining empty titles
    count_titles = biblio_df.shape[0]
    biblio_df = biblio_df[biblio_df['title'].str.strip().astype(bool)]
    print(f'Removed additional {count_titles - biblio_df.shape[0]} titles that were empty strings')


    """
        Cleaning the publication abstracts
    """

    # Replace all abstracts that are NaN with empty strings
    count_abs_nan = biblio_df['abstract'].isna().sum()
    biblio_df['abstract'] = biblio_df['abstract'].fillna('')
    print(f'Replaced {count_abs_nan} abtracts that were NaN with an empty string')

    # Remove text between '<' and '>' characters
    biblio_df['abstract'] = biblio_df['abstract'].str.replace(r'<.*?>', '', regex = True)

    # Remove all non-alphabetic characters except for '.', '-', ',', ':', ')', '(', '$', '%',  whitespace and Greek letters
    biblio_df['abstract'] = biblio_df['abstract'].apply(lambda x: re.sub(r'[^a-zA-Z0-9α-ωΑ-Ω\s.,:’()$%\'\"\-]+', ' ', x))

    # Replace any special whitespace character with a normal whitespace
    biblio_df['abstract'] = biblio_df['abstract'].str.replace(r'\u2002|\u2003|\u2005|\u2009|\u200a|\u202f|\xa0', ' ', regex = True)

    # Replace all newline and tab characters with a white space
    biblio_df['abstract'] = biblio_df['abstract'].str.replace(r'\n|\t', ' ', regex = True)

    # Remove the word 'abstract' and 'objective' at the start of any abstract
    biblio_df['abstract'] = biblio_df['abstract'].str.replace(r'^(?i)abstract\s*', '', regex = True)
    biblio_df['abstract'] = biblio_df['abstract'].str.replace(r'^(?i)objective(s)?\s*', '', regex = True)

    # Remove the following common terms from the abstract independently of the case
    remove_strings = ['background', 'objective', 'results', 'conclusions', 'introduction']
    pattern = "|".join(remove_strings)
    biblio_df['abstract'] = biblio_df['abstract'].apply(lambda x: re.sub(pattern, '', x, flags = re.IGNORECASE))

    # Remove any words starting with '.' or '-' and any single letter except 'a' from the beginning of the title and abstract
    biblio_df['abstract'] = biblio_df['abstract'].str.replace(r'^[-.]+\s*\w+\s*|(\s|^)[^Aa\s+](\s+|$)', '', regex = True)

    # Remove excess whitespace
    biblio_df['abstract'] = biblio_df['abstract'].str.replace('\s+', ' ', regex = True).str.strip()


    """
        Removing duplicate publications

        Deciding which publication to retain:
        - If one or several duplicate publications have an abstract, remove from consideration those that don't have 
          an abstract.
        - If one or several of the publications are from Scopus, retain the one with the latest publish_year. In case
          the publish_years are the same, select the one that has an abstract. If they all have an abstract, select one
          at random.
        - For publications that don't have a publish_date, set it to 1 Jan of publish_year.
        - Keep the publication with the latest publish_date. If there are multiple publications with the same publish_date,
          select one at random.
    """







    """
        Cleaning Scopus/Lens/Dimensions-specific elements
    """

    # Do the biblio_type specific cleaning tasks
    if biblio_type == BiblioType.SCOPUS:
        pass
    elif biblio_type == BiblioType.LENS:

        # Convert year to integer and replace nan with zeros
        biblio_df['year'] = pd.to_numeric(biblio_df['year'], errors = 'coerce')
        biblio_df['year'] = biblio_df['year'].fillna(0)
        biblio_df['year'] = biblio_df['year'].astype(int)

    elif biblio_type == BiblioType.DIMS:
        pass
    elif biblio_type == BiblioType.BIBLIO:
        pass
    else:
        raise ValueError("The biblio_type provided is not implemented")
    
    return biblio_df


def filter_biblio_df(biblio_df: pd.DataFrame, 
                     query_str: str
                     ) -> pd.DataFrame:
    """
    Filter biblio_df using a query string.

    Parameters:

    biblio_df (pd.DataFrame): 
        The DataFrame to filter.
    query_str (str): 
        The query string to use for filtering.

    Raises:
        ValueError: If the query string is not valid, or if any of the column names
        referred to in the query string do not exist in the DataFrame.

    Returns:

    pd.DataFrame: 
        The filtered DataFrame.
    """

    # Check that the query string is valid and that any column names it refers to exist
    try:
        filtered_df = biblio_df.query(query_str)
    except (SyntaxError, ValueError) as e:
        raise ValueError("Invalid query string") from e

    for col in filtered_df.columns:
        if col not in biblio_df.columns:
            raise ValueError(f"Column '{col}' does not exist in DataFrame")

    # Return the filtered DataFrame
    return filtered_df
