import pandas as pd
import cmd

from typing import List, Dict
from clean import *


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
        # kws_col_df = kws_df.apply(lambda x: x.str.split(',')).explode(col).reset_index(drop = True)
        kws_col_df = kws_df.fillna('').apply(lambda x: x.str.split(';')).explode(col).reset_index(drop=True)
        kws_col_df = kws_col_df[kws_col_df[col] != '']
        kws_col_df[col] = kws_col_df[col].str.replace('-', ' ')


        # Create a count table for the keywords
        # kw_count_df = pd.DataFrame(kws_col_df[col].value_counts()).reset_index(drop = True)
        kw_count_df = kws_col_df[col].value_counts().reset_index()
        kw_count_df.columns = ['kw', 'count']
        kw_count_df = kw_count_df.sort_values(by = ['count', 'kw'], ascending = [False, True]).reset_index(drop = True)
        # kw_count_df.drop(['index'], axis = 1, inplace = True)

        kws_count_df_dict[col] = kw_count_df

        if assoc_filter:
            if not '{}' in assoc_filter:
                raise ValueError(f"The assoc_filter needs to include place holders '{{}}' for the keyword column")
            
            kw_assoc_count_df = kw_count_df.copy()
            kw_assoc_count_df = filter_biblio_df(kw_count_df,
                                                 assoc_filter.format('kw'))
            kws_count_df_dict[col + '_assoc'] = kw_count_df

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

