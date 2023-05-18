import pandas as pd
import numpy as np
import re

from typing import List, Optional, Union, Dict, Any

from config import *
from utilities import *

"""

[Module description]

"""


def modify_cols_biblio_df(biblio_df_: pd.DataFrame,
                                     reshape_base: Optional[Reshape] = None,
                                     reshape_filter: Optional[Union[Dict,List]] = None,
                                     keep_bib_src: bool = True
                                     ) -> pd.DataFrame:
    """
    Rename and retain columns in the bibliographic dataset `biblio_df` based on `reshape_base` with its
    preset criteria or on `reshape_filter`, where you define what column to retain and how to rename them.
    
    The reshape_base parameter allows you to specify preset criteria for renaming and retaining the columns 
    in the bibliographic `DataFrame`. The available values for `reshape_base` are defined in the 
    `config.py` file. For each bibliographic database that can be processed (e.g.Scopus, Lens, 
    Dimensions), there are three levels of detail that can be retained: *All*, *Full*, and *Compact*.

    - The "All" level retains all the columns of the raw dataset from the respective bibliographic database:
      `Reshape.SCOPUS_ALL`, `Reshape.LENS_ALL`, `Reshape.DIMS_ALL`.
    - The "Full" level removes certain columns from `biblio_df` that might not be needed for the analysis:
      `Reshape.SCOPUS_FULL`, `Reshape.LENS_FULL`, `Reshape.DIMS_FULL`.
    - The "Compact" level is similar to "Full" and further reduces the number of columns in `biblio_df`:
      `Reshape.SCOPUS_COMPACT`, `Reshape.LENS_COMPACT`, `Reshape.DIMS_COMPACT`.
    
    Alternatively, you can use the `reshape_filter` parameter to specify a list of column names in `biblio_df` 
    that you want to retain. This allows you to manually select the specific columns you need for further analysis.

    By using either `reshape_base` or `reshape_filter`, you can customize the column selection and reshaping process 
    of the bibliographic `DataFrame` based on your requirements.

    Args:
        biblio_df: 
            The input bibliographic `DataFrame`.
        reshape_base:
            If provided, only the columns specified in the `reshape_base` criteria will be retained and renamed 
            according to the predefined reshape structures (e.g. `reshape_struc_dims_compact`) defined in `config.py`.
        reshape_filter:
            A list or dictionary of column names for retaining specific columns. If a `reshape_base`is provided, 
            the `reshape_filter` only retains columns that are present once `reshape_base` has been applied.
            - If `reshape_filter` is a list, only the columns present in the list will be retained.
            - If `reshape_filter` is a dictionary, the keys represent the columns to be retained,
              and the values represent the new column names.
        keep_bib_src:
            Flag indicating whether to retain the 'bib_src' column in the output `DataFrame`. Otherwise
            it will be removed when applying `rehshape_base`and `reshape_column`(unless you provide it in the list).
            The values in `bib_src` are used in some of the other functions. 
    Returns:
        The modified bibliographic `DataFrame`.

    Raises:
        ValueError:
            - If any of the columns specified in `reshape_base` are not found in the `biblio_df`.
            - If any of the columns specified in `reshape_filter` are not found in the `biblio_df`.
    """

    biblio_df = biblio_df_.copy()

    if reshape_base:
        if not all(col in biblio_df.columns for col in reshape_strucs[reshape_base.value].keys()):
            raise ValueError(f"One or more columns not found in biblio_df: {reshape_strucs[reshape_base.value]}")
        
        reshape_columns = list(reshape_strucs[reshape_base.value].keys())

        if ('bib_src' in biblio_df.columns) and ('bib_src' not in reshape_columns):
            reshape_columns.append('bib_src')

        biblio_df = biblio_df[reshape_columns].rename(columns = reshape_strucs[reshape_base.value])

    if reshape_filter:

        if isinstance(reshape_filter, List):
            if not all(col in biblio_df.columns for col in reshape_filter):
                raise ValueError(f"One or more columns not found in biblio_df: {reshape_filter}")
            
            if ('bib_src' in biblio_df.columns) and ('bib_src' not in reshape_filter):
                reshape_filter.append('bib_src')

            biblio_df = biblio_df[reshape_filter]

        elif isinstance(reshape_filter, Dict):

            if not all(col in biblio_df.columns for col in reshape_filter.keys()):
                raise ValueError(f"One or more columns not found in biblio_df: {reshape_filter}")
            
            reshape_columns = list(reshape_filter.keys())

            if 'bib_src' not in reshape_columns:
                reshape_columns.append('bib_src')

            biblio_df = biblio_df[reshape_columns].rename(columns = reshape_filter)

    return biblio_df


def add_search_label(biblio_df_: pd.DataFrame,
                     search_label: str) -> pd.DataFrame:
    '''
    Add a column `search_label` to `biblio_df`.
     
    In some cases, especially when merging bibliographic datasets from different sources, it is helpful to
    know where the searches come from or what particular search terms were used. The `search_label`
    of merged datasets are merged into a list.

    Args:
        biblio_df: 
            The input bibliographic `DataFrame`.
        search_label:
            The search label that will be added to the column 'search_label.
    
    Returns:
        The bibliographic dataset `biblio_df` with the new column `search_label`.
    '''

    biblio_df = biblio_df_.copy()

    biblio_df['search_label'] = search_label
    
    return biblio_df


def add_biblio_source(biblio_df_: pd.DataFrame,
                      biblio_source: BiblioSource = BiblioSource.UNDEFINED
                      ) -> pd.DataFrame:
    """
    Adds a bibliography source column to `biblio_df` based on the specified `BiblioSource`.

    Use this function in case the `bib_src` has not been set correctly or the bibliographic
    dataset wasn't read with `read_biblio_csv_files_to_df`.

    Args:
        biblio_df: 
            The bibliographic dataset to add the bibliography source column to.
        biblio_source: 
            The bibliography source: `SCOPUS`, `LENS`, `DIMS`, `BIBLIO`. See `config.py` for 
            an updated list.

    Returns:
        pd.DataFrame: The modified DataFrame with the bibliography source column added.
    """

    biblio_df = biblio_df_.copy()

    if biblio_source == BiblioSource.SCOPUS:
        biblio_df['bib_src'] = 'scopus'
    elif biblio_source == BiblioSource.LENS:
        biblio_df['bib_src'] = 'lens'
    elif biblio_source == BiblioSource.DIMS:
        biblio_df['bib_src'] = 'dims'
    elif biblio_source == BiblioSource.BIBLIO:
        biblio_df['bib_src'] = 'biblio'

    return biblio_df


def format_auth_scopus(authors: Union[str, float]) -> Union[str, float]:
    """
    Reformats the author names string of a Scopus publication in a CSV export.

    The normalised format is

    - For a single author: `Surname, Initials` (e.g. Smith, J.A.)
    - For multipe authors: `Surname1, Initials1; Surname 2, Initials2 (e.g. Martínez, X.; Müller, H.W.)

    Example of a Scopus author names string: `Alexandre M., Silva T.C., Michalak K., Rodrigues F.A.`

    Args:
        authors: 
            The author names as a string in Scopus format. Handles NaN via `float`.

    Returns:
        The formatted author names as a string or NaN if missing.
    """

    if isinstance(authors, str) and authors != '':
        authors_lst = authors.split(',')

        authors_str_lst = []

        for author in authors_lst:
            if author.strip():
                # Split author name into parts (surname and initials)
                author_parts = author.strip().split()
                surname = author_parts[0].strip()

                if len(author_parts) > 1:
                    initials = [name.strip()[0] + '.' if not name.endswith('.') else name.strip() for name in author_parts[1:]]
                    initials = ''.join(initials)
                else:
                    initials = 'NA.'

                # Create normalised author string
                author_str = '{}, {}'.format(surname, initials)
                authors_str_lst.append(author_str)

        normalised_str = '; '.join(authors_str_lst)

        return normalised_str
    else:
        return np.nan


def format_auth_lens(authors: Union[str, float]) -> Union[str, float]:
    """
    Reformats the author names string of a Lens publication in a CSV export.

    The normalised format is

    - For a single author: `Surname, Initials` (e.g. Smith, J.A.)
    - For multipe authors: `Surname1, Initials1; Surname 2, Initials2 (e.g. Martínez, X.; Müller, H.W.)

    Example of a Lens author names string: `Elena L. Mishchenko; A. M. Mishchenko; Vladimir A. Ivanisenko`

    Args:
        authors: 
            The author names as a string in Lens format. Handles NaN via `float`.

    Returns:
        The formatted author names as a string or NaN if missing.
    """

    if isinstance(authors, str) and authors != '':
        authors_lst = authors.split(';')

        authors_str_lst = []

        for author in authors_lst:
            try:
                if author.strip():
                    # Split author name into parts (surname and initials)
                    author_parts = author.strip().split()
                    surname = author_parts[-1]

                    if len(author_parts) > 1:
                        initials = [name[0] + '.' if not name.endswith('.') else name for name in author_parts[:-1]]
                        initials = ''.join(initials)
                    else:
                        initials = 'NA.'

                    # Create normalised author string
                    author_str = '{}, {}'.format(surname.strip(), initials.strip())
                    authors_str_lst.append(author_str)
            except:
                raise ValueError(f"Failed with author name '{author}'")

        normalised_str = '; '.join(authors_str_lst)

        return normalised_str
    else:
        return np.nan


def format_auth_dims(authors: Union[str, float]) -> Union[str, float]:
    """
    Reformats the author names string of a Dimensions publication in a CSV export.

    The normalised format is

    - For a single author: `Surname, Initials` (e.g. Smith, J.A.)
    - For multipe authors: `Surname1, Initials1; Surname 2, Initials2 (e.g. Martínez, X.; Müller, H.W.)

    Example of a Dimensions author names string: `Bai, Xiao; Sun, Huaping; Lu, Shibao; Taghizadeh-Hesary, Farhad`

    Args:
        authors: 
            The author names as a string in Dimensions format. Handles NaN via `float`.

    Returns:
        The formatted author names as a string or NaN if missing.
    """

    if isinstance(authors, str) and authors != '':
        authors_lst = authors.split(';')

        authors_str_lst = []

        for author in authors_lst:
            if author.strip():
                # Split author name into parts (surname and initials)
                author = author.replace(',', '')
                author_parts = author.strip().split()
                surname = author_parts[0].strip()

                if len(author_parts) > 1:
                    initials = [name.strip()[0] + '.' if not name.endswith('.') else name.strip() for name in author_parts[1:]]
                    initials = ''.join(initials)
                else:
                    initials = 'NA.'

                # Create normalised author string
                author_str = '{}, {}'.format(surname, initials)
                authors_str_lst.append(author_str)

        normalised_str = '; '.join(authors_str_lst)

        return normalised_str
    else:
        return np.nan


def format_auth_affils_scopus(auth_affils_str: Union[str, float]) -> Union[str, float]:
    """
    Reformats the authors-affilitions string of a Scopus publication in a CSV export.

    The normalised format is

    - For a single author-affiliation: `Surname, Initials (Affiliation(s))` (e.g. Jin, X. (Luxembourg School of Finance, University of Luxembourg, Luxembourg))
    - For multipe authors-affiliations: `Surname1, Initials1 (Affiliation(s)1); Surname 2, Initials2 (Affiliation(s)2)

    Example of a Scopus authors-affiliations names string: `Blundell-Wignall, A., Enterprise Affairs, OECD, France; Roulet, C., Enterprise Affairs, OECD, France`

    !!! note
        Since Lens does not provide affiliation information, there is no corresponding function `format_auth_affils_lens`.

    Args:
        auth_affils_str: 
            The authors-affiliations as a string in Scopus format. Handles NaN via `float`.

    Returns:
        The formatted authors-affiliations string or NaN if missing.
    """
 
    auth_affils =[]

    if isinstance(auth_affils_str, str):  # prevents a Pylance error in x.split()
        if auth_affils_str != '':
            # Split auth_affils_str into individual author-affiliation pairs
            auth_affils = [re.split(r'\.\s*,|.\s+,\s*', name.strip(), maxsplit = 1) for name in auth_affils_str.split(';')]

            # Format each author-affiliation pair
            auth_affils = [[parts[0] + '.' if len(parts) > 1 else parts[0], parts[1].strip()] if len(parts) > 1 else 
                        [parts[0].strip()] for parts in auth_affils]
        else:
            # If auth_affils_str is an empty string, return a default anonymous author-affiliation
            return 'Anonymous ()'
    else:
        return np.nan

    auth_affil_str_lst = []

    for auth_affil in auth_affils:
        
        # Create the formatted author-affiliation string in the normalised format
        # If author_affil has just one element (author or affiliation), assume that the affiliation rather than the author name is missing
        if len(auth_affil) == 1:
            auth_affil_str = '{} ()'.format(auth_affil[0].strip())
        else:
            auth_affil_str = '{} ({})'.format(auth_affil[0].strip(), auth_affil[1].strip())
        
        auth_affil_str_lst.append(auth_affil_str)

    normalised_str = '; '.join(auth_affil_str_lst)

    return normalised_str


def format_auth_affils_dims(auth_affils_str: Union[str, float]) -> Union[str, float]:
    """
    Reformats the authors-affilitions string of a Dimensions publication in a CSV export.

    The normalised format is

    - For a single author-affiliation: `Surname, Initials (Affiliation(s))` (e.g. Jin, X. (Luxembourg School of Finance, University of Luxembourg, Luxembourg))
    - For multipe authors-affiliations: `Surname1, Initials1 (Affiliation(s)1); Surname 2, Initials2 (Affiliation(s)2)

    Example of a Scopus authors-affiliations names string: `Schweizer, Pia‐Johanna (Institute for Advanced Sustainability Studies (IASS), Potsdam, Germany); Goble, Robert (Clark University, Worcester, MA, USA)`

    !!! note
        Since Lens does not provide affiliation information, there is no corresponding function `format_auth_affils_lens`.

    Args:
        auth_affils_str: 
            The authors-affiliations as a string in Dimensions format. Handles NaN via `float`.

    Returns:
        The formatted authors-affiliations string or NaN if missing.
    """

    # The auth_affil strings are split at ';' except if the ';' is inside of parentheses. In that case, it
    # separates multiple affiliations and is therefore ignored.
    if isinstance(auth_affils_str, str):  # prevents a Pylance error in x.split()
        auth_affils = [part.strip().split('(', maxsplit = 1) for part in re.split(r';(?![^()]*\))', auth_affils_str.strip())]
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

        # Construct the normalised author-affiliation string
        auth_affil_str = np.nan

        if surname:
            auth_affil_str = f'{surname}, {name} ({affiliation})'
        elif affiliation:
            auth_affil_str = f'Anonymous ({affiliation})'

        auth_affil_str_lst.append(auth_affil_str)

    if not auth_affil_str_lst:
        return np.nan
    else:
        normalised_str = '; '.join(auth_affil_str_lst)
        return normalised_str


def get_biblio_source_string(biblio_source: BiblioSource) -> Union[str, float]:
    """
    Retrieves the string representation of a bibliography source.

    Args:
        biblio_source: The source of the bibliography (e.g. `BiblioSource.SCOPUS`).

    Returns:
        The string representation of the bibliography source (e.g. `scopus`) or NaN if not recognized.
    """

    biblio_source_str = np.nan

    if biblio_source == BiblioSource.SCOPUS:
        biblio_source_str = 'scopus'
    elif biblio_source == BiblioSource.LENS:
        biblio_source_str = 'lens'
    elif biblio_source == BiblioSource.DIMS:
        biblio_source_str = 'dims'
    elif biblio_source == BiblioSource.BIBLIO:
        biblio_source_str = 'biblio'
    else:
        raise ValueError(f"The value passed for biblio_source is invalid.")
    
    return biblio_source_str


def normalise_biblio_entities(biblio_df_: pd.DataFrame,
                              biblio_source: BiblioSource = BiblioSource.UNDEFINED
                              ) -> pd.DataFrame:
    """
    Converts certain values in the bibliographic dataset `biblio_df` to a normalised 
    format so that datasets from different bibliographic databases can be merged.

    The exact values that are normalised depend on the source (Scopus, Lens,...) of 
    the dataset provided by 'biblio_source`. If `biblio_source` is not provided, the
    function will try to obtain it from `bib_src`. This only works if there is just 
    one bibliographic source provided in `bib_src` and it is the same for are all
    publications in `biblio_df`.

    Args:
        biblio_df: 
            The bibliographic dataset.
        biblio_source: 
            The bibliographic database that is the source of the bibliographic dataset.

    Returns:
        The bibliographic dataset with normalised bibliographic entities.
    """

    biblio_df = biblio_df_.copy()

    if biblio_source == BiblioSource.UNDEFINED:

        # Check if the bib_src column exists and has consistent values
        if 'bib_src' in biblio_df.columns:

            # Determine the bibliography source based on the first record
            if (biblio_df['bib_src'].isin(['scopus', 'lens', 'dims', 'biblio'])).all():
                if biblio_df.loc[0, 'bib_src'] == 'scopus':
                    biblio_source = BiblioSource.SCOPUS
                elif biblio_df.loc[0, 'bib_src'] == 'lens':
                    biblio_source = BiblioSource.LENS
                elif biblio_df.loc[0, 'bib_src'] == 'dims':
                    biblio_source = BiblioSource.DIMS
                elif biblio_df.loc[0, 'bib_src'] == 'biblio':
                    biblio_source = BiblioSource.BIBLIO
            else:
                raise ValueError(f"The bib_src needs to be the same for all records in biblio_df")
        else:
            raise ValueError(f"You either need to pass a biblio_source to the function or add a bib_src column")

    # Create the clickable link and the list of all links
    if biblio_source == BiblioSource.SCOPUS:
        if 'doi' in biblio_df.columns:
            biblio_df['link'] = 'https://dx.doi.org/' + biblio_df['doi']
            biblio_df['links'] = biblio_df['link']
        else:
            biblio_df['link'] = np.nan
            biblio_df['links'] = np.nan
    elif biblio_source == BiblioSource.LENS:
        biblio_df['link'] = np.nan
        biblio_df['links'] = np.nan

        if 'ext_url' in biblio_df.columns:
            biblio_df['link'] = biblio_df['ext_url']
        if 'source_urls' in biblio_df.columns:
            biblio_df['links'] = biblio_df['source_urls']
            
    elif biblio_source == BiblioSource.DIMS:
        if 'ext_url' in biblio_df.columns:
            biblio_df['link'] = biblio_df['ext_url']
            biblio_df['links'] = biblio_df['ext_url']
        else:
            biblio_df['link'] = np.nan
            biblio_df['links'] = np.nan

    # Create the unified keywords lists in column 'kws'
    if biblio_source == BiblioSource.SCOPUS:
        biblio_df['kws'] = biblio_df.apply(
            lambda row: '; '.join(sorted(set(
                [kw.strip() for kw in row[['kws_author', 'kws_index']].str.cat(sep = ';', na_rep = '').lower().split(';') if kw.strip()]
            ))), axis=1)
            
    elif biblio_source == BiblioSource.LENS:
        biblio_df['kws'] = biblio_df.apply(
            lambda row: '; '.join(sorted(set(
                [kw.strip() for kw in row[['kws_lens', 'mesh']].str.cat(sep = ';', na_rep = '').lower().split(';') if kw.strip()]
            ))), axis=1)
    elif biblio_source == BiblioSource.DIMS:
        if 'mesh' in biblio_df.columns:
            # biblio_df['kws'] = biblio_df['kws'].apply(lambda x: '; '.join(sorted(x.split('; '))))
            biblio_df['kws'] = biblio_df['mesh'].apply(lambda x: '; '.join(sorted(x.lower().split('; '))) 
                                                       if pd.notna(x) and ';' in x else x.lower() if pd.notna(x) else np.nan)
        else:
            biblio_df['kws'] = np.nan

    # Normalise the authors format
    if 'authors' in biblio_df.columns:
        if biblio_source == BiblioSource.SCOPUS:
            biblio_df['authors'] = biblio_df['authors'].apply(format_auth_scopus)
        elif biblio_source == BiblioSource.LENS:
            biblio_df['authors'] = biblio_df['authors'].apply(format_auth_lens)
        elif biblio_source == BiblioSource.DIMS:
            biblio_df['authors'] = biblio_df['authors'].apply(format_auth_dims)

    # Normalise the author-affiliations format
    if 'auth_affils' in biblio_df.columns:
        if biblio_source == BiblioSource.SCOPUS:
            biblio_df['auth_affils'] = biblio_df['auth_affils'].apply(format_auth_affils_scopus)
        elif biblio_source == BiblioSource.DIMS:
            biblio_df['auth_affils'] = biblio_df['auth_affils'].apply(format_auth_affils_dims)

    # Convert some other entities to lower case
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


def remove_title_duplicates(biblio_df_: pd.DataFrame) -> pd.DataFrame:
    """
    Removes duplicate publications by title from `biblio_df`.

    The function takes a bibliographic dataset `biblio_df` as input and performs several 
    operations to remove duplicate titles. It returns the modified `DataFrame` after removing 
    duplicates.

    The major processing steps are:

    - Group all duplicate titles
    - For each group
        - Merge keywords, links, bib_src, and other columns
        - Ignore the publications with missing abstracts (unless they are all missing)
        - If there are Scopus publications, use their title, abstract, and year
        - Pick the publication with the latest publish date/year. If there are several,
          then pick one at random.

    The function merges:
    
    - bib_src (the bibliographic sources)
    - source (the publication sources, e.g. journals, conference proceedings,...)
    - n_cited (number of citations)
    - fos (fields of study; only Lens)
    - anzsrc_2020 (Australian and New Zealand Standard Research Classification)
    - kws (keywords)
    - links (URLs to access the publication)

    Args:
        biblio_df: The bibliographic dataset.

    Returns:
        The modified `DataFrame` after removing duplicates.

    Assumptions:
        The titles have previously been cleaned using the function `clean_biblio_df`. If not, there is a chance that duplicate titles are being missed because of differences in lower/upper case, special characters, etc.
    """

    biblio_df = biblio_df_.copy()

    logger.info(f"Number of publications before removing duplicate titles: {biblio_df.shape[0]}")

    # Convert the years to int (Lens has the year as a float, so I force missing values there to zero)
    biblio_df['year'] = biblio_df['year'].fillna(0).astype(int)

    # Create column pub_date if it doesn't exist (in Scopus for instance)
    if 'pub_date' not in biblio_df.columns:
        biblio_df['pub_date'] = np.nan

    # Replace the missing pub_date with 1/1/1700
    biblio_df['pub_date_dummy'] = biblio_df['pub_date'].fillna(pd.to_datetime('01-01-1700', format = '%d-%m-%Y'))

    # Remove entries where no date information is provided
    # biblio_df = biblio_df.loc[
    #     ((biblio_df['bib_src'] == 'scopus') & (biblio_df['year'] != 0)) |
    #     ((biblio_df['bib_src'] != 'scopus') & ((biblio_df['year'] != 0) | (biblio_df['pub_date_dummy'] != pd.to_datetime('01-01-1700', format = '%d-%m-%Y'))))
    # ]

    if not biblio_df.empty:

        # Create a pub_date of 01/01/year for all missing pub_dates
        biblio_df['pub_date_dummy'] = biblio_df['pub_date']
        biblio_df['pub_date_dummy'].fillna(pd.to_datetime('01-01-' + biblio_df.loc[biblio_df['year'] != 0, 'year'].astype(int).astype(str), format = '%d-%m-%Y'), inplace=True)

        # Convert all 'pub_date_dummy' values to datetime
        biblio_df['pub_date_dummy'] = pd.to_datetime(biblio_df['pub_date_dummy'], errors = 'coerce')

        # Extract missing years from pub_date
        if (biblio_df['year'] == 0).any():
            biblio_df.loc[biblio_df['year'] == 0, 'year'] = \
                biblio_df.loc[biblio_df['year'] == 0, 'pub_date_dummy'].dt.year

    # Create new columns for merged values
    biblio_df['bib_srcs'] = biblio_df['bib_src']

    if 'source' in biblio_df:
        biblio_df['sources'] = np.nan
    
    # Dataframe for duplicate titles
    dup_df = pd.DataFrame()

    # Storing the updated values (e.g. when merging) in a dictionary and then updating
    # biblio_df in one go outside the loop makes the code run much faster
    update_dict = {}

    # Storing the indices of rows to drop. This is much faster than using the drop()
    # function of the dataframe inside the loop. The rows are then dropped from the
    # dataframe biblio_df outside the loop.
    drop_rows = []

    # Group the rows by the titles and loop over the groups
    for idx, (_, group) in enumerate(biblio_df.groupby('title')):

        # Create a new column 'sources' that has all the source titles
        if 'source' in group.columns:
            unique_src = group['source'].dropna().str.split(';').explode().str.strip().unique()
            group['sources'] = '; '.join(unique_src)
            # biblio_df.loc[group.index, 'sources'] = group['sources']

            for row_idx, value in group['sources'].items():     # NEW PERFORMANCE CODE
                update_dict[(row_idx, 'sources')] = value


        if(idx % 100 == 0):
            print(f'Duplicate group: #{idx} ', end = '\r')   # '\r' to overwrite the previous string; ' ' to append to the right

        if len(group) > 1:
            dup_df = pd.concat([dup_df, group])

            # Identify the duplicates by index within this group
            duplicates = group.duplicated(subset = 'title', keep = False)

            # Sum the values in n_cited
            if 'n_cited' in group.columns:
                sum_n_cited = group['n_cited'].sum()
                group['n_cited'] = sum_n_cited
                # biblio_df.update(group[['n_cited']])
                for row_idx, value in group['n_cited'].items():     # NEW PERFORMANCE CODE
                    update_dict[(row_idx, 'n_cited')] = value
            
            # Merge the values in the fos column
            if 'fos' in group.columns:
                unique_fos = group['fos'].dropna().str.split(';').explode().str.strip().unique()
                group['fos'] = '; '.join(unique_fos)
                # biblio_df.update(group[['fos']])
                for row_idx, value in group['fos'].items():     # NEW PERFORMANCE CODE
                    update_dict[(row_idx, 'fos')] = value

            # Merge the values in the anzsrc_2020 column
            if 'anzsrc_2020' in group.columns:
                unique_anzsrc = group['anzsrc_2020'].dropna().str.split(';').explode().str.strip().unique()
                group['anzsrc_2020'] = '; '.join(unique_anzsrc)
                # biblio_df.update(group[['anzsrc_2020']])
                for row_idx, value in group['anzsrc_2020'].items():     # NEW PERFORMANCE CODE
                    update_dict[(row_idx, 'anzsrc_2020')] = value

            # Merge the values in the keywords (kws) column
            if 'kws' in group.columns:
                unique_kws = group['kws'].str.lower().dropna().str.split(';').explode().str.strip().unique()
                group['kws'] = '; '.join(unique_kws)
                # biblio_df.update(group[['kws']])
                for row_idx, value in group['kws'].items():     # NEW PERFORMANCE CODE
                    update_dict[(row_idx, 'kws')] = value

            # Create a new column 'links' that has all the URLs separate with a space
            if 'links' in group.columns:
                unique_links = group['links'].dropna().str.split(' ').explode().str.strip().unique()
                group['links'] = ' '.join(unique_links)
                # biblio_df.update(group[['links']])
                for row_idx, value in group['links'].items():     # NEW PERFORMANCE CODE
                    update_dict[(row_idx, 'links')] = value

            # Create a new column 'bib_srcs' that has all the bib_src strings of the duplicate titles
            unique_bib_src = group['bib_src'].dropna().str.split(',').explode().str.strip().unique()
            group['bib_srcs'] = ', '.join(unique_bib_src)
            # biblio_df.update(group[['bib_srcs']])
            for row_idx, value in group['bib_srcs'].items():     # NEW PERFORMANCE CODE
                update_dict[(row_idx, 'bib_srcs')] = value

            # Pick an author affiliation string
            if 'author_affils' in group.columns:
                has_scopus = group['bib_src'].str.contains('scopus', case = False, na = False)
                filtered_group = group['author_affils'].dropna()

                if has_scopus.any():
                    filtered_group = filtered_group.loc[has_scopus]
                
                if not filtered_group.empty:
                    selected_row = filtered_group.sample(n = 1)
                    group['author_affils'] = selected_row.iloc[0]
                    # FIXME: I think the biblio_df update is missing here

            # If at least one publication in the group has an abstract,
            # remove any publication in the group that doesn't have an abstract
            # and then reset the group with the removed publications
            if group['abstract'].notna().any():
                items_to_drop = group[duplicates & group['abstract'].isna()]    # drops all items except the item_to_keep
                group = group.drop(items_to_drop.index)
                # biblio_df = biblio_df.drop(items_to_drop.index)
                drop_rows.append(items_to_drop.index.to_list())

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

                    # biblio_df = biblio_df.loc[biblio_df['bib_src'] == 'scopus']
                    group = group.loc[group['bib_src'] == 'scopus']

                    items_to_drop = scopus.drop(item_to_keep.index) # drops all items except the item_to_keep
                    group = group.drop(items_to_drop.index)
                    # biblio_df = biblio_df.drop(items_to_drop.index)
                    drop_rows.append(items_to_drop.index.to_list())

            # If there are several publications left, select the one with the latest
            # pub_date. If they are all the same, select one randomly.
            if len(group) > 1:

                # If there are multiple records with the same largest pub_date, first check whether 
                # there is one that has a source. If there are multiple, then pick one at random
                if 'source' in group.columns and group['source'].notna().any():
                    idxmax_group = group[group['source'].notna()]
                else:
                    idxmax_group = group.loc[group['pub_date_dummy'] == group['pub_date_dummy'].max()]

                idxmax_values = idxmax_group.index.values
                random_idx = np.random.choice(idxmax_values)

                # Drop all rows except for the one with the largest pub_date
                indices_to_drop = group.index.difference([random_idx])
                group = group.drop(indices_to_drop)
                # biblio_df = biblio_df.drop(indices_to_drop)
                drop_rows.append(indices_to_drop.to_list())


        else:
            # Copy single values to new columns
            biblio_df['bib_srcs'] = biblio_df['bib_src']

    # Update biblio_df with the value updates (e.g. merges) made during the duplicate scanning above
    for (row, column), value in update_dict.items():
        biblio_df.at[row, column] = value

    # Remove rows that were dropped during the duplicate scanning above
    drop_rows = [item for sublist in drop_rows for item in sublist]
    biblio_df = biblio_df.drop(drop_rows)


    # Remove the dummy column
    biblio_df = biblio_df.drop(['pub_date_dummy'], axis = 1)

    # Change n_cited to int
    if 'n_cited' in biblio_df.columns:
        biblio_df['n_cited'] = biblio_df['n_cited'].fillna(0)
        biblio_df['n_cited'] = biblio_df['n_cited'].astype(int)

    logger.info(f"Number of publications after removing duplicate titles: {biblio_df.shape[0]}")

    return biblio_df


def clean_biblio_df(biblio_df_: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the bibliographic dataset `biblio_df` by processing the publication titles
    and abstracts to remove noise and standardise formatting.

    The function removes publications with empty titles, NaN titles, and titles containing 
    specific keywords such as 'conference', 'workshop', 'proceedings'. It converts titles to 
    lowercase, removes HTML tags, non-alphabetic characters (except specific punctuation and 
    Greek letters), excess whitespace, and common terms from the beginning of titles.

    For abstracts, the function replaces NaN values with empty strings, removes HTML tags, 
    non-alphabetic characters (except specific punctuation and Greek letters), excess whitespace, 
    and common terms used in abstracts of publications in some disciplines such as 'background', 
    'objectives', 'results' etc. It also removes duplicate publications using the function 
    `remove_title_duplicates` and generates standard publication IDs.

    Args:
        biblio_df: 
            Input DataFrame containing bibliographic information.

    Returns:
        Cleaned bibligraphic dataset with standardized publication titles, abstracts, and new publication IDs.

    Raises:
        None.

    """

    biblio_df = biblio_df_.copy()

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
    """

    biblio_df = remove_title_duplicates(biblio_df)
    

    # Convert year to integer and replace nan with zeros (in Lens, year is a float)
    if 'year' in biblio_df.columns and biblio_df['year'].dtype == float:
        biblio_df['year'] = pd.to_numeric(biblio_df['year'], errors = 'coerce')
        biblio_df['year'] = biblio_df['year'].fillna(0)
        biblio_df['year'] = biblio_df['year'].astype(int)


    '''
        Generate the new publication IDs
    '''
    
    # Sort the dataset before creating the ids
    biblio_df = biblio_df.sort_values(by = ['year', 'title'], ascending = [False, True], na_position='last')

    # Generate the record IDs
    global counter
    counter = 0

    def generate_id(row):
        global counter
        author = ''

        if (row['authors'] != "") and isinstance(row['authors'], str):
            if "no author name" in row['authors'].lower():
                author = 'Anonymous'
            else:
                author = row['authors'].split()[0].strip().strip(',')
        else:
            author = 'Anonymous'

        id = str(counter).zfill(6) + '_' + author + '_' + str(row['year'])
        counter += 1

        return id
    
    # Make sure the index is properly set (starts at 0, then at unit increments)
    biblio_df.reset_index(drop = True, inplace = True)

    # Generate the unique identifiers for the publications
    biblio_df['id'] = biblio_df.apply(generate_id, axis = 1)
    
    return biblio_df



