import pandas as pd
import numpy as np
import re
import logging
import webcolors

from typing import List, Optional, Union, Dict, Tuple, Any
from IPython.core.display import HTML
from openpyxl import Workbook
from openpyxl.styles import Font, colors, Alignment
from openpyxl.cell.text import InlineFont
from openpyxl.cell.rich_text import TextBlock, CellRichText

from config import *
from utilities import *

def reshape_cols_biblio_df(biblio_df: pd.DataFrame,
                      reshape_base: Optional[Reshape] = None,
                      reshape_filter: Optional[Union[Dict,List]] = None,
                      keep_bib_src: bool = True,
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


def format_auth_scopus(authors: Union[str, float]) -> Union[str, float]:

    if isinstance(authors, str) and authors != '':
        authors_lst = authors.split(',')

        authors_str_lst = []

        for author in authors_lst:
            # author = author.replace(',', '')
            author_parts = author.strip().split()
            surname = author_parts[0].strip()
            initials = [name.strip()[0] + '.' if not name.endswith('.') else name.strip() for name in author_parts[1:]]
            initials = ''.join(initials)
            author_str = '{}, {}'.format(surname, initials)
            authors_str_lst.append(author_str)

        return '; '.join(authors_str_lst)
    else:
        return np.nan


def format_auth_lens(authors: Union[str, float]) -> Union[str, float]:

    if isinstance(authors, str) and authors != '':
        authors_lst = authors.split(';')

        authors_str_lst = []

        for author in authors_lst:
            author_parts = author.strip().split()
            surname = author_parts[-1]
            initials = [name[0] + '.' if not name.endswith('.') else name for name in author_parts[:-1]]
            initials = ''.join(initials)
            author_str = '{}, {}'.format(surname.strip(), initials.strip())
            authors_str_lst.append(author_str)

        return '; '.join(authors_str_lst)
    else:
        return np.nan


def format_auth_dims(authors: Union[str, float]) -> Union[str, float]:

    if isinstance(authors, str) and authors != '':
        authors_lst = authors.split(';')

        authors_str_lst = []

        for author in authors_lst:
            author = author.replace(',', '')
            author_parts = author.strip().split()
            surname = author_parts[0].strip()
            initials = [name.strip()[0] + '.' if not name.endswith('.') else name.strip() for name in author_parts[1:]]
            initials = ''.join(initials)
            author_str = '{}, {}'.format(surname, initials)
            authors_str_lst.append(author_str)

        return '; '.join(authors_str_lst)
    else:
        return np.nan


def format_auth_affils_scopus(x: Union[str, float]) -> Union[str, float]:
        
    auth_affils =[]

    if isinstance(x, str):  # prevents a Pylance error in x.split()
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
    if isinstance(x, str):  # prevents a Pylance error in x.split()
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


def get_biblio_source_string(biblio_source: BiblioType) -> Union[str, float]:
    biblio_source_str = np.nan

    if biblio_source == BiblioType.SCOPUS:
        biblio_source_str = 'scopus'
    elif biblio_source == BiblioType.LENS:
        biblio_source_str = 'lens'
    elif biblio_source == BiblioType.DIMS:
        biblio_source_str = 'dims'
    elif biblio_source == BiblioType.BIBLIO:
        biblio_source_str = 'biblio'
    
    return biblio_source_str


def normalise_biblio_entities(biblio_df: pd.DataFrame,
                              biblio_source: BiblioType = BiblioType.UNDEFINED
                              ) -> pd.DataFrame:

    if biblio_source == BiblioType.UNDEFINED:
        if 'bib_src' in biblio_df.columns:
            if (biblio_df['bib_src'].isin(['scopus', 'lens', 'dims', 'biblio'])).all():
                if biblio_df.loc[0, 'bib_src'] == 'scopus':
                    biblio_source = BiblioType.SCOPUS
                elif biblio_df.loc[0, 'bib_src'] == 'lens':
                    biblio_source = BiblioType.LENS
                elif biblio_df.loc[0, 'bib_src'] == 'dims':
                    biblio_source = BiblioType.DIMS
                elif biblio_df.loc[0, 'bib_src'] == 'biblio':
                    biblio_source = BiblioType.BIBLIO
            else:
                raise ValueError(f"The bib_src needs to be the same for all records in biblio_df")
        else:
            raise ValueError(f"You either need to pass a biblio_source to the function or add a bib_src column")

    # Create the clickable link and the list of all links
    if biblio_source == BiblioType.SCOPUS:
        if 'doi' in biblio_df.columns:
            biblio_df['link'] = 'https://dx.doi.org/' + biblio_df['doi']
            biblio_df['links'] = biblio_df['link']
        else:
            biblio_df['link'] = np.nan
            biblio_df['links'] = np.nan
    elif biblio_source == BiblioType.LENS:
        biblio_df['link'] = np.nan
        biblio_df['links'] = np.nan

        if 'ext_url' in biblio_df.columns:
            biblio_df['link'] = biblio_df['ext_url']
        if 'source_urls' in biblio_df.columns:
            biblio_df['links'] = biblio_df['source_urls']
            
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

    # Format the authors
    if 'authors' in biblio_df.columns:
        if biblio_source == BiblioType.SCOPUS:
            biblio_df['authors'] = biblio_df['authors'].apply(format_auth_scopus)
        elif biblio_source == BiblioType.LENS:
            biblio_df['authors'] = biblio_df['authors'].apply(format_auth_lens)
        elif biblio_source == BiblioType.DIMS:
            biblio_df['authors'] = biblio_df['authors'].apply(format_auth_dims)

    # Format the author affiliations
    if 'auth_affils' in biblio_df.columns:
        if biblio_source == BiblioType.SCOPUS:
            biblio_df['auth_affils'] = biblio_df['auth_affils'].apply(format_auth_affils_scopus)
        elif biblio_source == BiblioType.DIMS:
            biblio_df['auth_affils'] = biblio_df['auth_affils'].apply(format_auth_affils_dims)

    # Lower casing some other fields
    if 'fos' in biblio_df.columns:
        biblio_df['fos'] = biblio_df['fos'].apply(lambda x: x.lower() if pd.notnull(x) else x) # biblio_df['fos'].str.lower()
    if 'kws_lens' in biblio_df.columns:
        biblio_df['kws_lens'] = biblio_df['kws_lens'].apply(lambda x: x.lower() if pd.notnull(x) else x) # biblio_df['kws_lens'].str.lower()
    if 'mesh' in biblio_df.columns:
        biblio_df['mesh'] = biblio_df['mesh'].apply(lambda x: x.lower() if pd.notnull(x) else x) # biblio_df['mesh'].fillna('').str.lower()
    if 'kws_author' in biblio_df.columns:
        biblio_df['kws_author'] = biblio_df['kws_author'].apply(lambda x: x.lower() if pd.notnull(x) else x) # biblio_df['kws_author'].fillna('').str.lower()
    if 'kws_index' in biblio_df.columns:
        biblio_df['kws_index'] = biblio_df['kws_index'].apply(lambda x: x.lower() if pd.notnull(x) else x) # biblio_df['kws_index'].fillna('').str.lower()


    return biblio_df


def remove_title_duplicates(biblio_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
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

    logger.info(f"Number of publications before removing duplicate titles: {biblio_df_copy.shape[0]}")

    # Convert the years to int (Lens has the year as a float, so I force missing values there to zero)
    biblio_df_copy['year'] = biblio_df_copy['year'].fillna(0).astype(int)

    # Create column pub_date if it doesn't exist (in Scopus for instance)
    if 'pub_date' not in biblio_df_copy.columns:
        biblio_df_copy['pub_date'] = np.nan

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
    biblio_df_copy['bib_srcs'] = biblio_df_copy['bib_src']

    if 'source' in biblio_df_copy:
        biblio_df_copy['sources'] = np.nan
    
    # Dataframe for duplicate titles
    dup_df = pd.DataFrame()

    # Group the rows by the titles and loop over the groups
    # for _, group in biblio_df_copy.groupby('title'):
    for idx, (_, group) in enumerate(biblio_df_copy.groupby('title')):

        # Create a new column 'sources' that has all the source titles
        if 'source' in group.columns:
            unique_src = group['source'].dropna().str.split(';').explode().str.strip().unique()
            group['sources'] = '; '.join(unique_src)
            biblio_df_copy.loc[group.index, 'sources'] = group['source']

        if(idx % 1 == 0):
            print(f'Group: {idx} ', end = '\r')

        if len(group) > 1:
            dup_df = pd.concat([dup_df, group])

            # Identify the duplicates by index within this group
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

            # Create a new column 'links' that has all the URLs separate with a space
            if 'links' in group.columns:
                unique_links = group['links'].dropna().str.split(' ').explode().str.strip().unique()
                group['links'] = ' '.join(unique_links)
                biblio_df_copy.update(group[['links']])

            # Create a new column 'bib_srcs' that has all the bib_src strings of the duplicate titles
            unique_bib_src = group['bib_src'].dropna().str.split(',').explode().str.strip().unique()
            group['bib_srcs'] = ', '.join(unique_bib_src)
            biblio_df_copy.update(group[['bib_srcs']])

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
                    # group = group.dropna(subset = ['source'])
                    # idxmax_group = group.loc[group['pub_date_dummy'] == group['pub_date_dummy'].max()]
                    idxmax_group = group[group['source'].notna()]
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
        biblio_df_copy['n_cited'] = biblio_df_copy['n_cited'].fillna(0)
        biblio_df_copy['n_cited'] = biblio_df_copy['n_cited'].astype(int)

    logger.info(f"Number of publications after removing duplicate titles: {biblio_df_copy.shape[0]}")

    return biblio_df_copy, dup_df

counter = 0

def clean_biblio_df(biblio_df: pd.DataFrame) -> pd.DataFrame:
    global counter

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
    def title_to_lc(s: str) -> str:
        clean_s = re.sub(r'[^A-Za-z]', ' ', s)
        if clean_s.isupper():
            final_s = clean_s.capitalize()
        else:
            words = s.split()
            words = [words[0]] + [w.lower() if w[0].isupper() and len(w) > 1 and w[1].isalpha() and not w[1].isupper() else w for w in words[1:]]
            final_s = ' '.join(words)
        return final_s

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
    biblio_df['title'] = biblio_df['title'].str.replace(r'(?i)^abstract\s*', '', regex = True)

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
    biblio_df['abstract'] = biblio_df['abstract'].str.replace(r'(?i)^abstract\s*', '', regex = True)
    biblio_df['abstract'] = biblio_df['abstract'].str.replace(r'(?i)^objective(s)?\s*', '', regex = True)

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

    biblio_df, _ = remove_title_duplicates(biblio_df)
    

    '''
        Generate the new publication IDs
    '''
    
    # Sort the dataset before creating the ids
    biblio_df = biblio_df.sort_values(by = ['year', 'title'], ascending = [False, True], na_position='last')

    # Generate the record IDs
    counter = 0

    def generate_id(row):
        global counter
        author = ''

        if (row['authors'] != "") and isinstance(row['authors'], str):
            if "no author name" in row['authors'].lower():
                author = 'Anonymous'
            else:
                author = row['authors'].split()[0].strip()
        else:
            author = 'Anonymous'

        id = str(counter).zfill(6) + '_' + author + '_' + str(row['year'])
        counter += 1

        return id

    biblio_df['id'] = biblio_df.apply(generate_id, axis = 1)


    """
        Cleaning Scopus/Lens/Dimensions-specific elements
    """

    # # Do the biblio_type specific cleaning tasks
    # if biblio_type == BiblioType.SCOPUS:
    #     pass
    # elif biblio_type == BiblioType.LENS:

    # Convert year to integer and replace nan with zeros
    if biblio_df['year'].dtype == float:
        biblio_df['year'] = pd.to_numeric(biblio_df['year'], errors = 'coerce')
        biblio_df['year'] = biblio_df['year'].fillna(0)
        biblio_df['year'] = biblio_df['year'].astype(int)

    # elif biblio_type == BiblioType.DIMS:
    #     pass
    # elif biblio_type == BiblioType.BIBLIO:
    #     pass
    # else:
    #     raise ValueError("The biblio_type provided is not implemented")
    
    return biblio_df


def generate_pandas_query_string(query_str: str) -> str:
    split_at = r"()|&~"
    pad = r"|&~"
    split_at_escaped = re.escape(split_at)

    if re.search(r'\[[^\]]*~[^\]]*\]', query_str):
        raise ValueError(f"The not operator '~' is not allowed inside square brackets '[...]'")
    
    if re.search(r'in\*\s*~', query_str):
        raise ValueError(f"Applying the not operator '~' on the columns is not allowed")
    
    pattern = fr"(?=[{split_at_escaped}])|(?<=[{split_at_escaped}])"
    query_parts = re.split(pattern, query_str)
    query_parts = [item.strip() for item in query_parts if item.strip()]

    modified_query_parts = []

    for query_part in query_parts:

        if 'in*' in query_part:
            in_parts = query_part.split('in*')
            search_str = in_parts[0].strip()
            col_str = in_parts[1].strip()                

            match_and = re.match(r"^\[\[.*\]\]$", search_str)
            match_or = re.match(r"^\[.*\]$", search_str)
            match = match_and if match_and else (match_or if match_or else False)
            match_col = re.match(r"^\[.*\]$", col_str)

            if match_col:   # multiple columns to search in
                matched_col_lst = [string.strip() for string in match_col.group().replace('[', '').replace(']', '').split(',')]
            else:
                matched_col_lst = [col_str]

            if match:   # multiple search strings
                matched_string = match.group().strip().replace('[', '').replace(']', '')

                # if ... multiple columns in which to search

                # else ...
                search_str_lst = [string.strip() for string in matched_string.split(',')]
                first_col_str = True
                subst_query = ""

                for col_str in matched_col_lst:
                    subst_query += f"{' | ' if not first_col_str else ''}({col_str}.str.contains(r'"
                    first_search_str = True

                    for search_str in search_str_lst:
                        if re.match(r"^['\"].*['\"]$", search_str):   # single search string, full word match enforced
                            search_str = search_str.strip().replace("'", "").replace('"', "")
                            if match_and:
                                subst_query += f"{'^' if not first_search_str else ''}(?=.*\\b{search_str}\\b)"
                            else:
                                subst_query += f"{'|' if not first_search_str else ''}\\b{search_str}\\b"
                            first_search_str = False
                        else:   # single search string, partial word match allowed
                            search_str = search_str.strip()
                            if match_and:
                                subst_query += f"{'^' if not first_search_str else ''}(?=.*{search_str})"
                            else:
                                subst_query += f"{'|' if not first_search_str else ''}{search_str}"
                            first_search_str = False

                    subst_query += f"', case = False, regex = True))"
                    first_col_str = False

                modified_query_parts.append(subst_query)
            else:
                first_col_str = True
                subst_query = ""

                for col_str in matched_col_lst:
                    # subst_query += f"{' | ' if not first_col_str else ''}({col_str}.str.contains(r'^"
                    subst_query += f"{' | ' if not first_col_str else '('}"

                    if re.match(r"^['\"].*['\"]$", search_str):   # single search string, full word match enforced
                        search_str = search_str.strip().replace("'", "").replace('"', "")
                        subst_query += f"{col_str}.str.contains(r'\\b{search_str}\\b', case = False, regex = True)"
                    else:   # single search string, partial word match allowed
                        subst_query += f"{col_str}.str.contains('{search_str}', case = False, regex = True)"
                    
                    first_col_str = False

                subst_query += f")"
                modified_query_parts.append(subst_query)
        else:
            modified_query_parts.append(query_part)

    modified_query_parts = [s if s not in pad else f" {s} " for s in modified_query_parts]

    return ''.join(modified_query_parts)

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

    # Build pandas query string
    filter_pandas_query = generate_pandas_query_string(query_str = query_str)

    # Check that the query string is valid
    try:
        filtered_df = biblio_df.query(filter_pandas_query)
    except (SyntaxError, ValueError) as e:
        raise ValueError("Invalid query string") from e

    # Return the filtered DataFrame
    return filtered_df


def highlight_selected_text(text: str, 
                            strings: Union[List[str], str], 
                            colour: str, 
                            partial: bool = True, 
                            i_row: Optional[int] = None
                            ) -> str:
    text = str(text)

    if isinstance(strings, str):
        strings = [strings]
    
    if i_row and (i_row % 100 == 0) and (logger.get_level() == logging.INFO): # print row index
        print(f'{i_row}', end = '\r')

    if len(strings) == 0:
        return text
    
    if (len(strings) == 1) and (strings[0] == ""):
        return text

    for k in strings:
        if partial: # highlight partial and full matches
            # pattern = r"\b\w*{}+\w*\b".format(k)
            pattern = r"(?<!>)\b\w*{}+\w*\b(?!<)".format(k)
            text = re.sub(pattern, lambda match: f'<span style="color: {colour}; font-weight: bold">{match.group()}</span>', text, flags = re.IGNORECASE)
        else:   # highlight full matches only
            # pattern = r"(?i)\b"+k+r"[\w-]*"
            pattern = r"(?i)(?<!>)\b"+k+r"[\w-]*\b(?!<)"
            text = re.sub(pattern, lambda match: f'<span style="color: {colour}; font-weight: bold">{match.group()}</span>', text)

    return text


def colour_name_to_hex(colour_name):
    # See the colour names here: https://www.w3.org/TR/SVG11/types.html#ColorKeywords

    try:
        # Get RGB value for the color name
        rgb = webcolors.name_to_rgb(colour_name)

        # Convert RGB to hex code
        hex_code = webcolors.rgb_to_hex(rgb)

        return hex_code
    except:
        raise ValueError(f"The colour {colour_name} does not exist")


def get_excel_column(number):
    column = ""
    while number > 0:
        number, remainder = divmod(number - 1, 26)
        column = chr(65 + remainder) + column
    return column


def excel_highlights_builder(biblio_highlights_df: pd.DataFrame,
                             excel_params: Optional[Any]) -> Workbook:

    # FIXME: This needs the lxml package installed for Workbook.save to work. Add that to the requirements.txt

    excel_sheet_name = 'Highlights' # default name for the new Excel sheet with the highlights
    excel_zoom = 100    # default zoom of the sheet
    excel_freeze_panes = None   # default freeze for horizontal panes
    excel_cols = None
    excel_highlighted_cols = None

    default_width = 15
    default_wrap = False

    # Unpack the parameters
    if isinstance(excel_params, Dict):
        excel_cols = excel_params.get('cols', None)
        excel_sheet_name = excel_params.get('sheet_name', None)
        excel_zoom = excel_params.get('zoom', excel_zoom)
        excel_freeze_panes = excel_params.get('freeze_panes', excel_freeze_panes)
        excel_highlighted_cols = excel_params.get('highlighted_cols', None)
    elif excel_params != None:
        raise ValueError(f"The function argument excel_params has to be a dictionary")
    
    formatted_cols = []
    remaining_cols = []

    # Get the columns to be added first (the remaining columns are added as-is to the Excel sheet)
    if isinstance(excel_cols, List):
        formatted_cols = [d['col'] for d in excel_cols if d['col'] in biblio_highlights_df.columns]
        remaining_cols = [col for col in biblio_highlights_df.columns if col not in formatted_cols]
    elif excel_cols == None:  # if no columns have been provided in excel_params, use all columns from biblio_highlights_df
        remaining_cols = biblio_highlights_df.columns
    else:
        raise ValueError(f"The item 'excel_cols' in the dictionary has to be a list")

    # Reorder the columns in biblio_highlights_df
    reorder_cols = formatted_cols + remaining_cols
    biblio_highlights_df = biblio_highlights_df[reorder_cols]

    # Create a new workbook
    wb = Workbook()

    # Create a new sheet
    ws = wb.create_sheet(excel_sheet_name)

    # Remove the default sheet
    if wb["Sheet"]:
        wb.remove(wb["Sheet"])

    # Make a copy of titles_highlights_df
    tak_excel_df = biblio_highlights_df.copy()

    # Excel column headers
    for j, col in enumerate(formatted_cols):
        # header = str(tak_excel_df.columns[j])
        header = col

        if excel_cols is not None:
            header = next((col_info.get('heading', col) for col_info in excel_cols if col_info['col'] == col), col)

        ws.cell(row = 1, column = j + 1, value = header).font = Font(bold = True)

    cursor = len(formatted_cols)

    for j, col in enumerate(remaining_cols):
        header = col

        if excel_cols is not None:
            header = next((col_info.get('heading', col) for col_info in excel_cols if col_info['col'] == col), col)

        ws.cell(row = 1, column = j + cursor + 1, value = header).font = Font(bold = True)

    # Apply findall() to split a string at '<span.../span>'
    def split_string_at_span(string):
        lst = re.findall(r"(.*?)(<span.*?/span>|$)", string)
        lst = [elem for tup in lst for elem in tup]
        lst = [x for x in lst if x.strip()]
        return lst

    def replace_span_with_textblock(lst: List[str]) -> List[str]:
        is_prev_kw = False  # need to add a space between two consecutive keywords
        rich_text_lst = []

        for string in lst:
            if string.startswith('<span'):
                colour_name = re.findall(r'color: (\w+)', string)[0] if re.findall(r'color: (\w+)', string) else None
                colour_hex = '00' + colour_name_to_hex(colour_name = colour_name)[1:]
                # span_string = '<span style="color: {}; font-weight: bold">'.format(colour_name)
                text = (' ' if is_prev_kw else '') + string.split('>')[1].split('<')[0]
                text_block = TextBlock(InlineFont(b = True, color = colour_hex), text)  # type: ignore (the Pylance issue is caused by the TextBlock constructor typing)
                rich_text_lst.append(text_block)
                is_prev_kw = True
            else:
                rich_text_lst.append(string)
                is_prev_kw = False

        return rich_text_lst

    if excel_highlighted_cols is not None:
        excel_highlighted_cols = [col for col in excel_highlighted_cols if col in biblio_highlights_df.columns]

        for col in excel_highlighted_cols:
            # Create a list of each cell content by splitting at '<span...>some text</span>' using findall()
            tak_excel_df[col] = tak_excel_df[col].apply(split_string_at_span)

            # Replace all '<span...>some text</span>' with the results of calling TextBlock(bold_red, 'some text')
            tak_excel_df[col] = tak_excel_df[col].apply(replace_span_with_textblock)

    numeric_cols = biblio_highlights_df.select_dtypes(include = "number").columns.tolist()

    # Loop through rows and columns of the dataframe
    for i in range(len(tak_excel_df)):
        for col in tak_excel_df.columns:
            j = tak_excel_df.columns.get_loc(col)

            if col in excel_highlighted_cols:
                rs = CellRichText(tak_excel_df.iloc[i, j])  # type: ignore - not sure how to avoid the Pylance typing warning
            elif col in numeric_cols:
                # rs = str(tak_excel_df.iloc[i, j])
                rs = tak_excel_df.iloc[i, j]
            else:
                rs = str(tak_excel_df.iloc[i, j])

            ws.cell(row = i + 2, column = j + 1, value = rs)

    for idx, col in enumerate(formatted_cols):
        col_letter = get_excel_column(idx + 1)
        width = default_width
        wrap = default_wrap

        if excel_cols is not None:
            width = next((col_info.get('width', default_width) for col_info in excel_cols if col_info['col'] == col), default_width)
            wrap = next((col_info.get('wrap', default_wrap) for col_info in excel_cols if col_info['col'] == col), default_wrap)

        ws.column_dimensions[col_letter].width = width

        for cell in ws[col_letter]:
            cell.alignment = Alignment(wrap_text = wrap)

    ws.sheet_view.zoomScale = excel_zoom

    if excel_freeze_panes:
        ws.freeze_panes = excel_freeze_panes

    return wb


def highlight_biblio_df(biblio_df: pd.DataFrame,
                        highlight_params: List[Dict[str, Union[List[str], str]]],
                        html_cols: Optional[List] = None,
                        xlsx_cols: Optional[List] = None,
                        excel_params: Optional[Any] = None
                        ) -> Tuple[Optional[HTML], Optional[Workbook]]:
    biblio_highlights_df = biblio_df.copy()

    highlighted_cols = []

    for param in highlight_params:
        if not all([key in param for key in ['strings', 'targets']]):
            raise ValueError(f"The key 'strings' or 'targets' is missing in the parameter dictionary")
        
        if 'colour' not in param:
            colour = 'red'
        else:
            colour = param.get('colour')

        if isinstance(param['strings'], list):
            strings = param.get('strings', [])
        else:
            strings = str(param.get('strings'))

        if isinstance(param['targets'], list):
            targets = param.get('targets', [])
        else:
            targets = [param.get('targets')]

        # Highlight the strings provided in param
        for target in targets:
            if target in biblio_highlights_df.columns:
                highlighted_cols.append(target)
                print(f'Highlighting strings in {colour} in the {target}...')
                biblio_highlights_df[target] = biblio_highlights_df \
                    .apply(lambda x: highlight_selected_text(
                            text = x[target], 
                            strings = strings, 
                            colour = str(colour), 
                            i_row = biblio_highlights_df.index.get_loc(x.name)), axis = 1)

    html_out = None
    xlsx_out = None

    if html_cols != None:
        if html_cols == []:
            html_out = HTML(biblio_highlights_df.to_html(escape = False))
        else:
             html_out = HTML(biblio_highlights_df[html_cols].to_html(escape = False))

    if excel_params != None:
        excel_params['highlighted_cols'] = list(set(highlighted_cols))

    if xlsx_cols != None:
        if xlsx_cols == []:
            xlsx_cols = list(biblio_highlights_df.columns)
        
        xlsx_out = excel_highlights_builder(biblio_highlights_df = biblio_highlights_df[xlsx_cols],
                                            excel_params = excel_params)
    else:
        xlsx_out = excel_highlights_builder(biblio_highlights_df = biblio_highlights_df,
                                            excel_params = excel_params)

    return html_out, xlsx_out


