import pandas as pd
import numpy as np
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


def add_biblio_source(biblio_df: pd.DataFrame,
                      biblio_source: BiblioType) -> pd.DataFrame:
    
    if biblio_source == BiblioType.SCOPUS:
        biblio_df['bib_src'] = 'scopus'
    elif biblio_source == BiblioType.LENS:
        biblio_df['bib_src'] = 'lens'
    elif biblio_source == BiblioType.DIMS:
        biblio_df['bib_src'] = 'dims'
    else:
        biblio_df['bib_src'] = 'biblio'

    return biblio_df


def format_auth_affils_scopus(x: Union[str, float]) -> Union[str, float]:
        
    auth_affils =[]

    if isinstance(x, str):
        if x != '':
            auth_affils = [re.split(r'\.\s*,|.\s+,\s*', name.strip(), maxsplit = 1) for name in x.split(';')]
            auth_affils = [[parts[0] + '.' if len(parts) > 1 else parts[0], parts[1].strip()] if len(parts) > 1 else 
                        [parts[0].strip()] for parts in auth_affils]
        else:
            return 'Anonymous ()'
    else:
        return np.nan

    auth_affil_str_lst = []

    for auth_affil in auth_affils:
        
        # If author_affil has just one, assume that the affiliation is missing
        if len(auth_affil) == 1:
            auth_affil_str = '{} ()'.format(auth_affil[0].strip())
        else:
            auth_affil_str = '{} ({})'.format(auth_affil[0].strip(), auth_affil[1].strip())
        
        auth_affil_str_lst.append(auth_affil_str)

    return '; '.join(auth_affil_str_lst)


def format_auth_affils_dims(x: Union[str, float]) -> Union[str, float]:
    
    # The auth_affil strings are split at ';' except if the ';' is inside of parentheses. In that case, it
    # separates multiple affiliations.
    if isinstance(x, str):
        auth_affils = [part.strip().split('(', maxsplit = 1) for part in re.split(r';(?![^()]*\))', x.strip())]
    else:
        return np.nan

    auth_affil_str_lst = []

    for auth_affil in auth_affils:

        # Extract the affiliation, if present
        if len(auth_affil) == 2:
            affiliation = auth_affil[1][:-1] if auth_affil[1].endswith(')') else auth_affil[1]

        else:
            affiliation = ''

        # Extract the author information, if present
        if auth_affil[0]:
            author_parts = auth_affil[0].split(',', maxsplit=1)
            surname = author_parts[0].strip()
            name_parts = [part.strip() for part in author_parts[1].split()]

            # Format the author name using the first letter of each name part
            initials = [part[0] + '.' if not part.endswith('.') else part for part in name_parts]
            name = ''.join(initials)
        else:
            # No author information
            surname = ''
            name = ''

        # Construct the final string
        auth_affil_str = np.nan

        if surname:
            auth_affil_str = f'{surname}, {name} ({affiliation})'
        elif affiliation:
            auth_affil_str = f'Anonymous ({affiliation})'

        auth_affil_str_lst.append(auth_affil_str)

    if len(auth_affil_str_lst) == 0 or all(x is np.nan for x in auth_affil_str_lst):
        return np.nan
    else:
        return '; '.join(auth_affil_str_lst)


def normalise_biblio_entities(biblio_df: pd.DataFrame,
                              biblio_source: BiblioType) -> pd.DataFrame:

    # Create the clickable link and the list of all links
    if biblio_source == BiblioType.SCOPUS:
        if 'doi' in biblio_df.columns:
            biblio_df['link'] = 'https://dx.doi.org/' + biblio_df['doi']
            biblio_df['links'] = biblio_df['link']
        else:
            biblio_df['link'] = np.nan
            biblio_df['links'] = np.nan
    elif biblio_source == BiblioType.LENS:
        if 'ext_url' in biblio_df.columns:
            biblio_df['link'] = biblio_df['ext_url']
            biblio_df['links'] = biblio_df['source_urls']
        else:
            biblio_df['link'] = np.nan
            biblio_df['links'] = np.nan
    elif biblio_source == BiblioType.DIMS:
        if 'ext_url' in biblio_df.columns:
            biblio_df['link'] = biblio_df['ext_url']
            biblio_df['links'] = biblio_df['ext_url']
        else:
            biblio_df['link'] = np.nan
            biblio_df['links'] = np.nan

    # Create the unified keywords list kws
    if biblio_source == BiblioType.SCOPUS:
        biblio_df['kws'] = biblio_df.apply(
            lambda row: '; '.join(sorted(set(
                [kw.strip() for kw in row[['kws_author', 'kws_index']].str.cat(sep = ';', na_rep = '').lower().split(';') if kw.strip()]
            ))), axis=1)
            
    elif biblio_source == BiblioType.LENS:
        biblio_df['kws'] = biblio_df.apply(
            lambda row: '; '.join(sorted(set(
                [kw.strip() for kw in row[['kws_lens', 'mesh']].str.cat(sep = ';', na_rep = '').lower().split(';') if kw.strip()]
            ))), axis=1)
    elif biblio_source == BiblioType.DIMS:
        if 'mesh' in biblio_df.columns:
            # biblio_df['kws'] = biblio_df['kws'].apply(lambda x: '; '.join(sorted(x.split('; '))))
            biblio_df['kws'] = biblio_df['mesh'].apply(lambda x: '; '.join(sorted(x.lower().split('; '))) 
                                                       if pd.notna(x) and ';' in x else x.lower() if pd.notna(x) else np.nan)
        else:
            biblio_df['kws'] = np.nan

    # Format the author affiliations
    if biblio_source == BiblioType.SCOPUS:
        biblio_df['auth_affils'] = biblio_df['auth_affils'].apply(format_auth_affils_scopus)
    if biblio_source == BiblioType.DIMS:
        biblio_df['auth_affils'] = biblio_df['auth_affils'].apply(format_auth_affils_dims)

    return biblio_df


def remove_title_duplicates(biblio_df: pd.DataFrame):
    """
        Removing duplicate publications by title

        Deciding which publication to retain:
        - If one or several duplicate publications have an abstract, remove from consideration those that don't have 
          an abstract. Otherwise, don't remove any.
        - If one or several of the remaining publications are from Scopus, retain the one with the latest publish_year. 
          In case the publish_years are the same, select the one that has an abstract. If they all have an abstract, 
          select one at random.
        - For publications that don't have a pub_date, set it to 1 Jan of year.
        - Keep the publication with the latest pub_date. If there are multiple publications with the same pub_date,
          select one at random.
    """

    # Create a copy of the input DataFrame
    biblio_df_copy = biblio_df.copy()

    logger.info(f"There are {biblio_df_copy.shape[0]} publications in the dataframe before removing duplciate titles")

    # Convert the years to int (Lens has the year as a float, so I force missing values there to zero)
    biblio_df_copy['year'] = biblio_df_copy['year'].fillna(0).astype(int)

    # Replace the missing pub_date with 1/1/1700
    biblio_df_copy['pub_date_dummy'] = biblio_df_copy['pub_date'].fillna(pd.to_datetime('01-01-1700', format = '%d-%m-%Y'))

    # Replace NaT values with original datetimes
    # mask = biblio_df_copy['pub_date_dummy'].isna()
    # biblio_df_copy.loc[mask, 'pub_date_dummy'] = pd.to_datetime(biblio_df_copy.loc[mask, 'pub_date_dummy'])

    # Remove entries where no date information is provided
    biblio_df_copy = biblio_df_copy.loc[
        ((biblio_df_copy['bib_src'] == 'scopus') & (biblio_df_copy['year'] != 0)) |
        ((biblio_df_copy['bib_src'] != 'scopus') & ((biblio_df_copy['year'] != 0) | (biblio_df_copy['pub_date_dummy'] != pd.to_datetime('01-01-1700', format = '%d-%m-%Y'))))
    ]

    if not biblio_df_copy.empty:
        # Create a pub_date of 01/01/year for all missing pub_dates
        biblio_df_copy['pub_date_dummy'] = biblio_df_copy['pub_date']
        biblio_df_copy['pub_date_dummy'].fillna(pd.to_datetime('01-01-' + biblio_df_copy.loc[biblio_df_copy['year'] != 0, 'year'].astype(int).astype(str), format = '%d-%m-%Y'), inplace=True)

        # Convert all 'pub_date_dummy' values to datetime
        biblio_df_copy['pub_date_dummy'] = pd.to_datetime(biblio_df_copy['pub_date_dummy'], errors = 'coerce')

        # Extract missing years from pub_date
        if (biblio_df_copy['year'] == 0).any():
            biblio_df_copy.loc[biblio_df_copy['year'] == 0, 'year'] = \
                biblio_df_copy.loc[biblio_df_copy['year'] == 0, 'pub_date_dummy'].dt.year

    # Create new columns for merged values
    biblio_df_copy['bib_srcs'] = np.nan

    if 'source' in biblio_df_copy:
        biblio_df_copy['sources'] = np.nan

    # Group the rows by the titles and loop over the groups
    for _, group in biblio_df_copy.groupby('title'):

        if len(group) > 1:
            # Identify the duplicates within this group
            duplicates = group.duplicated(subset = 'title', keep = False)

            # Sum the values in n_cited
            if 'n_cited' in group.columns:
                sum_n_cited = group['n_cited'].sum()
                group['n_cited'] = sum_n_cited
                biblio_df_copy.update(group[['n_cited']])
            
            # Merge the values in the fos column
            if 'fos' in group.columns:
                unique_fos = group['fos'].dropna().str.split(';').explode().str.strip().unique()
                group['fos'] = '; '.join(unique_fos)
                biblio_df_copy.update(group[['fos']])

            # Merge the values in the anzsrc_2020 column
            if 'anzsrc_2020' in group.columns:
                unique_anzsrc = group['anzsrc_2020'].dropna().str.split(';').explode().str.strip().unique()
                group['anzsrc_2020'] = '; '.join(unique_anzsrc)
                biblio_df_copy.update(group[['anzsrc_2020']])

            # Merge the values in the keywords (kws) column
            if 'kws' in group.columns:
                unique_kws = group['kws'].str.lower().dropna().str.split(';').explode().str.strip().unique()
                group['kws'] = '; '.join(unique_kws)
                biblio_df_copy.update(group[['kws']])

            # Create a new column 'bib_srcs' that has all the bib_src strings of the duplicate titles
            unique_bib_src = group['bib_src'].dropna().str.split(',').explode().str.strip().unique()
            group['bib_srcs'] = ', '.join(unique_bib_src)
            biblio_df_copy.update(group[['bib_srcs']])

            # Create a new column 'sources' that has all the source titles
            if 'source' in group.columns:
                unique_src = group['source'].str.lower().dropna().str.split(';').explode().str.strip().unique()
                group['sources'] = '; '.join(unique_src)
                biblio_df_copy.loc[group.index, 'sources'] = group['source']

            # Create a new column 'links' that has all the URLs separate with a space
            if 'links' in group.columns:
                unique_links = group['links'].dropna().str.split(' ').explode().str.strip().unique()
                group['links'] = ' '.join(unique_links)
                biblio_df_copy.update(group[['links']])

            # Pick an author affiliation string
            if 'author_affils' in group.columns:
                has_scopus = group['bib_src'].str.contains('scopus', case = False, na = False)
                filtered_group = group['author_affils'].dropna()

                if has_scopus.any():
                    filtered_group = filtered_group.loc[has_scopus]
                
                if not filtered_group.empty:
                    selected_row = filtered_group.sample(n = 1)
                    group['author_affils'] = selected_row.iloc[0]

            # If at least one publication in the group has an abstract,
            # remove any publication in the group that doesn't have an abstract
            # and then reset the group with the removed publications
            if group['abstract'].notna().any():
                items_to_drop = group[duplicates & group['abstract'].isna()]    # drops all items except the item_to_keep
                group = group.drop(items_to_drop.index)
                biblio_df_copy = biblio_df_copy.drop(items_to_drop.index)

            # Check if any publication in the group has bib_src = 'scopus'
            if 'scopus' in group['bib_src'].values:

                # Identify the duplicates within this group
                duplicates = group.duplicated(subset = 'title', keep = False)
                scopus_mask = (group['bib_src'] == 'scopus')

                scopus = group[scopus_mask]

                if scopus.shape[0] > 0:
                    latest_scopus = scopus.loc[[scopus['year'].idxmax()]]

                    if latest_scopus['abstract'].isna().any():
                        scopus_with_abstract = scopus.dropna(subset = ['abstract'], how = 'any')

                        if scopus_with_abstract.shape[0] > 0:
                            item_to_keep = scopus_with_abstract.sample()
                        else:
                            item_to_keep = scopus.sample()
                    else:
                        item_to_keep = latest_scopus

                    biblio_df_copy = biblio_df_copy.loc[biblio_df_copy['bib_src'] == 'scopus']
                    group = group.loc[group['bib_src'] == 'scopus']

                    items_to_drop = scopus.drop(item_to_keep.index) # drops all items except the item_to_keep
                    group = group.drop(items_to_drop.index)
                    biblio_df_copy = biblio_df_copy.drop(items_to_drop.index)

            # If there are several publications left, select the one with the latest
            # pub_date. If they are all the same, select one randomly.
            if len(group) > 1:

                # If there are multiple records with the same largest pub_date, first check whether 
                # there is one that has a source. If there are multiple, then pick one at random
                if 'source' in group.columns and group['source'].notna().any():
                    idxmax_group = group.loc[(group['pub_date_dummy'] == group['pub_date_dummy'].max()) & (group['source'].notna())]
                else:
                    idxmax_group = group.loc[group['pub_date_dummy'] == group['pub_date_dummy'].max()]

                idxmax_values = idxmax_group.index.values
                random_idx = np.random.choice(idxmax_values)

                # Drop all rows except for the one with the largest pub_date
                indices_to_drop = group.index.difference([random_idx])
                group = group.drop(indices_to_drop)
                biblio_df_copy = biblio_df_copy.drop(indices_to_drop)

        else:
            # Copy single values to new columns
            biblio_df_copy['bib_srcs'] = biblio_df_copy['bib_src']

    # Remove the dummy column
    biblio_df_copy = biblio_df_copy.drop(['pub_date_dummy'], axis = 1)

    # Change n_cited to int
    if 'n_cited' in biblio_df_copy.columns:
        biblio_df_copy['n_cited'] = biblio_df_copy['n_cited'].astype(int)

    print("Publications that were removed")
    print(biblio_df[~biblio_df.index.isin(biblio_df_copy.index)][['title', 'year']])

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
    biblio_df['title'] = biblio_df['title'].str.replace(r'\s+', ' ', regex = True).str.strip()

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
    biblio_df['abstract'] = biblio_df['abstract'].str.replace(r'\s+', ' ', regex = True).str.strip()


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

    biblio_df = remove_title_duplicates(biblio_df)





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
