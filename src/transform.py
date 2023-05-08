import pandas as pd

from typing import List, Optional, Union, Dict
from config import *
from utilities import *


def reshape_cols_biblio_df(biblio_df: pd.DataFrame,
                      reshape_base: Optional[Reshape] = None,
                      reshape_filter: Optional[Union[Dict,List]] = None,
                      project: Optional[str] = None,
                      output_file: Optional[str] = None,
                      output_dir: Optional[str] = None
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


    if output_file and output_dir and project:
        logger.info(f"Writing biblio_df to file {output_file}")
        output_path = Path(root_dir, data_root_dir, project, output_dir, output_file)
        
        if Path(output_file).suffix == '.csv':
            biblio_df.to_csv(output_path, index = False)
        elif Path(output_file).suffix == '.xlsx':
            biblio_df.to_excel(output_path, index = False)
    elif not all([project, output_dir, output_file]) and any([project, output_dir, output_file]):
        raise ValueError("You need to provide all three values for project, output_file, and output_dir if you want to write the output to a file")

    return biblio_df


def add_search_label(biblio_df: pd.DataFrame,
                     search_label: str) -> pd.DataFrame:
    biblio_df['search_label'] = search_label
    return biblio_df


def clean_biblio_df(biblio_df: pd.DataFrame,
                    biblio_type: BiblioType,
                    project: Optional[str] = None,
                    output_file: Optional[str] = None,
                    output_dir: Optional[str] = None
                    ) -> pd.DataFrame:
    
    logger.info(f'Number of publications in the input biblio_df: {len(biblio_df)}')

    # Do the shared cleaning tasks
    # TODO:
    #  - Clean titles and abstracts
    #  - Create a new column with titles and abstracts that have been stripped of all non-alphanumeric characters, for easier comparison

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
